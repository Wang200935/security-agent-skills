# SPI + nRF24 Hardware Diagnostic Procedure

When all nRF24 `radio.begin()` calls return FAIL on a shared SPI bus, follow this procedure to isolate software vs hardware causes.

## Quick Decision Tree

```
All radios FAIL?
├─ Flash diagnostic sketch (below)
├─ Check serial output:
│  ├─ CSN/CE toggle OK? → GPIO is fine, problem is on SPI/nRF24 side
│  ├─ Raw CONFIG = 0xFF → MISO not connected or nRF24 has no power
│  ├─ Raw CONFIG = 0x00 → MISO pulled LOW (short, broken wire, GND disconnected)
│  ├─ Raw CONFIG = 0x08/0x0C → nRF24 alive, check SPI.begin() ordering
│  └─ GPIO toggle BAD → ESP32 pin damaged or wrong board
├─ If CONFIG = 0x00/0xFF (hardware):
│  ├─ Check 3.3V with multimeter
│  ├─ Check all GND connections
│  ├─ Check MISO wire continuity (GPIO 19)
│  ├─ Check SCK wire (GPIO 18) and MOSI wire (GPIO 23)
│  ├─ Add 10µF cap across each nRF24 VCC-GND
│  └─ Test ONE radio at a time (isolate bad module)
└─ If CONFIG = 0x08/0x0C (software):
   ├─ Ensure SPI.begin(18,19,23) called AFTER all CSN set HIGH
   ├─ Ensure CSN pins are GPIO 13/17/4 (not strapping pins)
   └─ Check RF24 library version compatibility
```

## Diagnostic Sketch (PlatformIO)

### platformio.ini

```ini
[env:esp32dev]
platform = espressif32@6.7.0
board = esp32dev
framework = arduino
upload_speed = 460800
upload_port = /dev/cu.usbserial-210
monitor_port = /dev/cu.usbserial-210
monitor_speed = 115200
lib_deps =
    nrf24/RF24@^1.4.0
```

### src/main.cpp

```cpp
#include <Arduino.h>
#include <SPI.h>
#include <RF24.h>

// Pin definitions — adjust to match your project
#define CE_A   5
#define CSN_A  17
#define CE_B   16
#define CSN_B  4
#define CE_C   15
#define CSN_C  13  // Changed from GPIO 2 to avoid strapping pin issue

RF24 radioA(CE_A, CSN_A);
RF24 radioB(CE_B, CSN_B);
RF24 radioC(CE_C, CSN_C);

// Raw SPI register read — bypasses RF24 library to test hardware directly
uint8_t rawSpiRead(int csn, uint8_t reg) {
    SPI.beginTransaction(SPISettings(8000000, MSBFIRST, SPI_MODE0));
    digitalWrite(csn, LOW);
    delayMicroseconds(10);
    SPI.transfer(reg & 0x1F);  // R_REGISTER command
    uint8_t val = SPI.transfer(0xFF);  // dummy clock, read response
    digitalWrite(csn, HIGH);
    SPI.endTransaction();
    return val;
}

void testRadio(const char* name, RF24 &radio, int ce, int csn) {
    Serial.printf("\n--- %s (CE=%d, CSN=%d) ---\n", name, ce, csn);

    // Test 1: CSN pin toggle (GPIO working?)
    pinMode(csn, OUTPUT);
    digitalWrite(csn, HIGH); delay(1);
    int csnHi = digitalRead(csn);
    digitalWrite(csn, LOW); delay(1);
    int csnLo = digitalRead(csn);
    digitalWrite(csn, HIGH);
    Serial.printf("  CSN: H=%d L=%d %s\n", csnHi, csnLo, (csnHi && !csnLo) ? "OK" : "BAD");

    // Test 2: CE pin toggle
    pinMode(ce, OUTPUT);
    digitalWrite(ce, LOW); delay(1);
    int ceLo = digitalRead(ce);
    digitalWrite(ce, HIGH); delay(1);
    int ceHi = digitalRead(ce);
    digitalWrite(ce, LOW);
    Serial.printf("  CE: L=%d H=%d %s\n", ceLo, ceHi, (!ceLo && ceHi) ? "OK" : "BAD");

    // Test 3: Raw SPI read CONFIG register (0x00)
    // 0xFF = no MISO/no power, 0x00 = MISO short to GND, 0x08/0x0C = alive
    uint8_t cfg = rawSpiRead(csn, 0x00);
    Serial.printf("  Raw CONFIG=0x%02X (0xFF=no MISO, 0x08/0x0C=alive)\n", cfg);

    // Test 4: RF24 library begin()
    bool ok = radio.begin();
    Serial.printf("  begin(): %s\n", ok ? "OK" : "FAIL");
    if (ok) radio.powerDown();

    digitalWrite(csn, HIGH);
}

void setup() {
    Serial.begin(115200);
    delay(1500);
    Serial.println("\n=== SPI + nRF24 Diagnostic ===\n");

    SPI.begin(18, 19, 23);  // VSPI: SCK=18, MISO=19, MOSI=23
    delay(100);

    // Deselect all slaves
    pinMode(CSN_A, OUTPUT); digitalWrite(CSN_A, HIGH);
    pinMode(CSN_B, OUTPUT); digitalWrite(CSN_B, HIGH);
    pinMode(CSN_C, OUTPUT); digitalWrite(CSN_C, HIGH);
    pinMode(CE_A, OUTPUT); digitalWrite(CE_A, LOW);
    pinMode(CE_B, OUTPUT); digitalWrite(CE_B, LOW);
    pinMode(CE_C, OUTPUT); digitalWrite(CE_C, LOW);
    delay(10);

    testRadio("RadioA", radioA, CE_A, CSN_A);
    delay(50);
    testRadio("RadioB", radioB, CE_B, CSN_B);
    delay(50);
    testRadio("RadioC", radioC, CE_C, CSN_C);

    Serial.println("\n=== Done ===");
    Serial.println("0xFF = no MISO wire or no 3.3V power to nRF24");
    Serial.println("0x00 = MISO partial / bad contact / GND not connected");
    Serial.println("0x08/0x0C = nRF24 alive, check SPI.begin() ordering in firmware");
}

void loop() {}
```

## Reading Serial Output (Non-TTY)

Use pyserial from Hermes terminal — `pio device monitor` will crash with `termios.error`:

```bash
python3 -c "
import serial, time

ser = serial.Serial('/dev/cu.usbserial-210', 115200, timeout=1)
time.sleep(0.3)

# Soft-reset via DTR/RTS
ser.dtr = True; ser.rts = True
time.sleep(0.1)
ser.dtr = False; ser.rts = False
time.sleep(0.5)

buf = b''
start = time.time()
while time.time() - start < 10:
    data = ser.read(4096)
    if data: buf += data
    else: time.sleep(0.05)

ser.close()
print(buf.decode('utf-8', errors='replace'))
" 2>&1
```

## Session Log (2026-07-24)

- **Project**: RF-Clown v2 firmware at `~/Documents/2.4ghz_jammer_research/rfclown_fw/`
- **Symptom**: All 3 radios (A, B, C) returned `radio.begin() = FAIL` after firmware烧录
- **GPIO toggle**: All CSN/CE pins toggled correctly (HIGH/LOW both read back fine)
- **Raw CONFIG**: 0x00 for all three radios → MISO pulled LOW
- **Root cause**: Hardware — MISO line not properly connected or nRF24 modules not powered. The firmware init order (SPI.begin before/after CSN-HIGH) was also corrected but the underlying issue was hardware wiring.
- **Fix applied**: CSN_C changed from GPIO 2 → 13 (strapping pin), `SPI.begin(18,19,23)` added after CSN-HIGH. Hardware wiring needs user-side fix (check MISO, 3.3V, GND connections, add 10µF caps).
- **Diagnostic sketch**: `~/Documents/2.4ghz_jammer_research/spi_diag/` (standalone PlatformIO project)

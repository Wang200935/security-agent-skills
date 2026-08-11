# SoftNRF Bit-Bang SPI Driver for nRF24L01+ on ESP32

## Context
When nRF24 modules are connected via breadboard with high-resistance contacts (Dupont wires, loose headers), hardware SPI's nanosecond edge rates cause ringing and bit corruption. Bit-banging with microsecond delays provides clean edges that pass through high-R connections.

## Proven Results
- Hardware SPI at 50kHz: Radio C **dead** (MISO stuck 0x00)
- Bit-bang at 2kHz (500µs delay): Radio C **alive**, 0/20 errors
- Bit-bang at 20kHz (50µs delay): Radio C **0/20 errors** but marginal
- Bit-bang at 40kHz (25µs delay): Radio C **occasional errors**
- Bit-bang at 100kHz (10µs delay): Radio C **frequent errors**
- **Final stable: 150µs delay (~6.6 kHz)** for high-R branch; 10µs for healthy branches

## Architecture

```cpp
class SoftNRF {
public:
  SoftNRF(uint8_t cePin, uint8_t csnPin, uint16_t delayUs);
  
  static void busInit();           // Call ONCE at boot
  void beginPins();                // CE low, CSN high
  bool isPresent();                // STATUS sanity check
  void configureTx();              // Power-up, TX, no CRC/ACK, 2Mbps, PA max
  void setChannel(uint8_t ch);     // Fast path (no verification)
  void setChannelChecked(uint8_t); // Verified write (for init)
  void carrierOn();                // CONT_WAVE + PLL_LOCK, CE HIGH
  void carrierOff();               // CE LOW, clear carrier bits
  void powerDown();                // Full power down
  
  // ShockBurst mode for WiFi-like interference
  void startShockBurst();          // Continuous max-length packets
  void repairShockBurstConfig();   // CE-low re-write of all critical regs
  
  uint8_t readReg(uint8_t reg);    // Verification helper

private:
  uint8_t transfer(uint8_t out);
  void writeReg(uint8_t reg, uint8_t val);
  bool writeRegChecked(uint8_t reg, uint8_t val);  // Write + read-back verify (4 retries)
  
  uint8_t _ce, _csn;
  uint16_t _d;  // per-bit delay in microseconds
};
```

## Critical Implementation Details

### Bus Initialization (call once)
```cpp
void SoftNRF::busInit() {
  pinMode(18, OUTPUT); digitalWrite(18, LOW);  // SCK
  pinMode(23, OUTPUT); digitalWrite(23, LOW);  // MOSI
  pinMode(19, INPUT);                          // MISO
}
```

### Bit-Bang Transfer (MSB first, mode 0)
```cpp
uint8_t SoftNRF::transfer(uint8_t out) {
  uint8_t in = 0;
  for (int i = 0; i < 8; i++) {
    digitalWrite(23, (out & 0x80) ? HIGH : LOW);  // MOSI
    out <<= 1;
    delayMicroseconds(_d);
    digitalWrite(18, HIGH);        // SCK rising
    delayMicroseconds(_d);
    in = (in << 1) | digitalRead(19);  // MISO
    digitalWrite(18, LOW);         // SCK falling
    delayMicroseconds(_d);
  }
  return in;
}
```

### Verified Write with Retry
```cpp
bool SoftNRF::writeRegChecked(uint8_t reg, uint8_t val) {
  for (int attempt = 0; attempt < 4; attempt++) {
    writeReg(reg, val);
    if (readReg(reg) == val) return true;
  }
  return false;
}
```

### ShockBurst Configuration
```cpp
void SoftNRF::startShockBurst() {
  writeRegChecked(EN_AA, 0x00);        // Auto-ack off
  writeRegChecked(SETUP_RETR, 0x00);   // No retries
  writeRegChecked(RF_SETUP, 0x0F);     // 2Mbps, PA max, LNA
  writeReg(STATUS, 0x70);              // Clear IRQ (not verifiable)
  writeRegChecked(CONFIG, 0x02);       // PWR_UP=1, PRIM_RX=0, CRC off
  delay(2);                            // Tpd2stby ≥ 1.5ms
  
  // TX address + payload width
  writeRegChecked(TX_ADDR, 0xE7);
  writeRegChecked(RX_ADDR_P0, 0xE7);
  writeRegChecked(RX_PW_P0, 32);
  
  // Fill TX FIFO with 32 bytes of 0xAA
  digitalWrite(_csn, LOW);
  delayMicroseconds(_d * 2);
  transfer(0xA0);  // W_TX_PAYLOAD
  for (int i = 0; i < 32; i++) transfer(0xAA);
  digitalWrite(_csn, HIGH);
  delayMicroseconds(_d * 2);
  
  // Dynamic payload + re-use TX payload
  writeRegChecked(FEATURE, 0x01);   // EN_DYN_ACK
  writeRegChecked(DYNPD, 0x01);     // DPL on pipe 0
  
  digitalWrite(_ce, HIGH);          // Continuous TX
}
```

### Repair Pass (for FIFO-load corruption)
Long FIFO-load transaction (33 bytes) on high-R CSN line causes glitches that corrupt previously-written registers. Repair pass rewrites all critical config with CE low:

```cpp
void SoftNRF::repairShockBurstConfig() {
  digitalWrite(_ce, LOW);
  writeRegChecked(CONFIG, 0x02);
  delay(2);
  writeRegChecked(EN_AA, 0x00);
  writeRegChecked(SETUP_RETR, 0x00);
  writeRegChecked(RF_SETUP, SNRF_RF_SETUP_BASE);
  writeRegChecked(RX_PW_P0, 32);
  writeRegChecked(FEATURE, 0x01);
  writeRegChecked(DYNPD, 0x01);
  digitalWrite(_ce, HIGH);
}
```

## Usage in RF-Clown (3-radio setup)

```cpp
// Radio A: healthy, 10µs delay
SoftNRF RadioA(5, 17, 10);
// Radio B: healthy, 10µs delay  
SoftNRF RadioB(16, 4, 10);
// Radio C: high-R branch, 150µs delay
SoftNRF RadioC(14, 13, 150);

void setup() {
  SoftNRF::busInit();
  RadioA.beginPins(); RadioB.beginPins(); RadioC.beginPins();
  
  // ... init all ...
  
  // Start ShockBurst with repair loop
  RadioA.startShockBurst();
  RadioB.startShockBurst();
  RadioC.startShockBurst();
  
  // Verify + repair up to 3 passes
  for (int pass = 0; pass < 3; pass++) {
    bool allGood = true;
    for (auto* r : {&RadioA, &RadioB, &RadioC}) {
      if (r->readReg(0x06) != 0x0F || r->readReg(0x1D) != 0x01) {
        r->repairShockBurstConfig();
        allGood = false;
      }
    }
    if (allGood) break;
    delay(10);
  }
}
```

## Periodic Health Check (every 5s in main loop)

```cpp
if (millis() - lastReport >= 5000) {
  for (auto* r : {&RadioA, &RadioB, &RadioC}) {
    uint8_t rf = r->readReg(0x06);
    uint8_t feat = r->readReg(0x1D);
    if (rf != 0x0F || feat != 0x01) {
      r->repairShockBurstConfig();
      // Restore channel for static modes
      r->setChannelChecked(storedChannel);
    }
  }
}
```

## Key Registers Reference

| Register | Addr | Purpose | ShockBurst Value |
|----------|------|---------|------------------|
| CONFIG | 0x00 | Power, CRC, TX/RX | 0x02 |
| EN_AA | 0x01 | Auto-ack enable | 0x00 |
| EN_RXADDR | 0x02 | RX pipes | 0x01 |
| SETUP_RETR | 0x04 | Retry delay/count | 0x00 |
| RF_CH | 0x05 | Channel (0-125) | varies |
| RF_SETUP | 0x06 | Data rate, PA, LNA | 0x0F (2Mbps, PA max, LNA on) |
| STATUS | 0x07 | FIFO status, IRQ | read-only |
| TX_ADDR | 0x10 | TX address | 0xE7... |
| RX_ADDR_P0 | 0x0A | RX pipe 0 address | 0xE7... |
| RX_PW_P0 | 0x11 | RX payload width | 32 |
| DYNPD | 0x1C | Dynamic payload | 0x01 |
| FEATURE | 0x1D | EN_DYN_ACK, etc. | 0x01 |

## nRF24 Channel → Frequency Mapping
**nRF24 channel N = 2400 + N MHz**

| Protocol | Freq Range | nRF24 Channels |
|----------|------------|----------------|
| WiFi ch 1 | 2412 MHz | **12** |
| WiFi ch 6 | 2437 MHz | **37** |
| WiFi ch 11 | 2462 MHz | **62** |
| BLE adv 37 | 2402 MHz | **2** |
| BLE adv 38 | 2426 MHz | **26** |
| BLE adv 39 | 2480 MHz | **80** |
| BT Classic | 2402-2480 MHz | **2-80** |

## Why ShockBurst Beats Pure CW for WiFi
- **Pure CW (CONT_WAVE)**: Single tone at center frequency. Some WiFi CCA only triggers on energy detect + preamble detect.
- **ShockBurst**: Continuous 32-byte packets at 2Mbps with valid preamble/SFD. Triggers **both** energy detect AND preamble detect in WiFi PHY, forcing CSMA/CA deferral more reliably.

## Debugging Tips
1. **STATUS register 0x00 or 0xFF** = SPI not communicating (check wiring, power, CSN)
2. **RF_SETUP reads 0x62 instead of 0x0F** = write corruption during long transaction (use repair pass)
3. **FEATURE reads 0x00** = EN_DYN_ACK not set (ShockBurst won't re-transmit payload)
4. **Radio works on boot but drifts** = add periodic health check every 5s
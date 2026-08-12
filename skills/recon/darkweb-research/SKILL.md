---
name: darkweb-research
description: 暗網自主研究環境 - 透過 Tor SOCKS5 探測/索引/搜尋 .onion 站。已在本機建立硬化 torrc + darksearch.py
  SQLite 索引 (1385 站、924 存活) + Keepass 加密 DB + exiftool 證據隔離。**資安研究專用** - references/security-onion-map.md
  記錄已鑑定高價值資安站 (snapWONDERS 隱寫/法醫 API+MCP server, NetForge CVE feed, Surveillance Archive
  法醫工具書, Tor core dev homepage, archive.today onion mirror, lanodan cyber blog 等)。Use
  when 需要上暗網找資訊/做 OSINT/做資安研究/索引 onion 站/驗證 Tor 連線安全。
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags:
    - osint
    - recon
    - information-gathering
    - darkweb
    - research
    related_skills: []
    origin: import
---

# 暗網研究環境 (本機 macOS)

**狀態**: 2026-07-19 已建好並實測運作。
**核心位置**: `~/Documents/darkweb-research/`
- tools/ - 所有腳本
- scans/idx.db - SQLite 索引
- keepass/research.kdbx - AES-256 Keepass DB
- evidence/ - sanitize 隔離區
- logs/, onions/, README.md

## Tor 環境
- daemon: `brew services start tor` (已 launchd 啟動)
- SOCKS5: `127.0.0.1:9050` (socks5h, Tor 端 DNS 解 .onion)
- Control: `127.0.0.1:9051` (cookie auth)
- torrc: `/Users/wang/homebrew/etc/tor/torrc`
- 硬化: StrictNodes=1, ExcludeNodes 擋五眼+TW+CN/RU/IR/KP/SA/SY, ExitNodes 限定 {nl},{de},{ch},{se},{ro},{is},{fi},{no},{fr},{be},{at}
  - **⚠ 語法陷阱**: torrc 不接受 `ExitNodes {nl,de,ch}` (單一大括號逗號串)。必須每國各一 `{}` 再以逗號串連: `ExitNodes {nl},{de},{ch}`。錯誤寫法會被靜默丟棄 → Tor fallback 到「任意 exit」,安全回退!改完一律 `brew services restart tor` + 重跑 `check.torproject.org/api/ip` 對照 exit 國家。詳見 `references/pitfalls-and-sources.md`。
- IsolateDestAddr: 每站獨立 circuit

## 驗證 IP 隱蔽 (每次 session 開始/中/尾都驗)
```bash
# 真實 IP (對照)
curl -s --max-time 10 https://api.ipify.org
# Tor 出口 IP (應不同, 非 TW)
curl -s --max-time 30 --socks5-hostname 127.0.0.1:9050 https://api.ipify.org
# Tor 官方認證 - 必須看到 "IsTor":true
curl -s --max-time 30 --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

## 工具
### onion_probe.py - 探一批 .onion 活存/title
```bash
cd ~/Documents/darkweb-research/tools
python3 onion_probe.py /tmp/urls.txt -o /tmp/out.json --timeout 45 --workers 4
# workers 保守 4 (避免 Tor overload; 382 站 * 2-10s/站 約 20 分鐘)
```

### darksearch.py - 索引 + 本地關鍵字搜尋
```bash
# 建索引
python3 darksearch.py index /tmp/urls.txt --workers 4 --timeout 45
# 搜尋 (--db 要在 search 之前)
python3 darksearch.py --db ~/Documents/darkweb-research/scans/idx.db search "wiki" --limit 10
python3 darksearch.py --db ~/Documents/darkweb-research/scans/idx.db search "leak" --limit 10
python3 darksearch.py --db ~/Documents/darkweb-research/scans/idx.db search "SecureDrop" --limit 10
```
- 文件 schema: urls(url PRIMARY KEY, title, http_code, size, elapsed, probed_at, category, error)
- index 時 prefix heuristic 過濾 (drug/dark/cann/card/hack 等 BAD_PREFIXES 排除)

### init_keepass.py - Keepass 加密 DB (一次性)
- 路徑: `~/Documents/darkweb-research/keepass/research.kdbx`
- AES-256, key 32-byte 隨機存 macOS Keychain
- 取出 key: `security find-generic-password -w -s darkweb-research-kp-key`
- Groups: Onion URLs / Credentials / Notes / Investigation Logs

### sanitize.py - 證據隔離 + 去 metadata
```bash
python3 sanitize.py <file>     # 單檔
python3 sanitize.py -d <dir>   # bulk
python3 sanitize.py --list     # 列已隔離
```
- 改名: `YYYYMMDD-HHMMSS-<sha8>.<ext>`
- exiftool -all= 清所有 metadata
- mtime 重設防原檔時間指紋
- sidecar `.meta.json` 記 sha256 + 取得時間

### Sherlock - username 跨平台 OSINT
```bash
~/.hermes/hermes-agent/venv/bin/sherlock <username>
```

## URL 入口來源 (優先順序)
1. **SecureDrop API** *(最高效,先抓)* `https://securedrop.org/api/v1/directory/` — 23 個合法媒體 SecureDrop .onion, JSON 直出, 不需 JS, 不被 Cloudflare 擋. START HERE for legitimate news/whistleblowing research.
2. **Ahmia 全索引**: `https://ahmia.fi/onions` — 8259 URL 單頁 660KB dump (透 Tor 取). 注意: `?page=N` 是裝飾, 永遠回同一頁.
3. **Ahmia onion mirror** (v3): `http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/` — ⚠ SPA only, `curl`/`urllib` 只拿 4727B 空 shell. 不要花工具呼叫試 `/search?q=` (驗證空). 用 darksearch.py 在本地 grep 全 dump.
4. ~~Wikipedia "List of Tor hidden services"~~ 取不出 URL (大部分 inline 文字), 跳過.

詳細 source 評比與實測數字見 `references/pitfalls-and-sources.md`.

## 已驗證的合法研究站 (活著 SecureDrop 等)
- Guardian, Bloomberg, Spiegel, Forbidden Stories, CBC, ProPublica, NRK, Dagbladet (各 Welcome | SecureDrop 頁)
- TorBox 匿名郵件: `http://torbox36ijlcevujx7mjb4oiusvwgvmue7jfn2cvutwa6kl6to3uyd.onion/`
- Hidden Wiki 多個 mirror (站目錄)
- Haystak 暗網搜尋引擎

## 第一次抓 8259 URLs(已實測索引)
- 在 `/tmp/ahmia-urls.txt` (每行一個 URL)
- 過濾非法 prefix (排除 drug/dark/cann 等) → 約 382 站進行實測
- 結果: 271/386 = 70% HTTP 2xx 存活

## 行為守則 (重要, 避免法律/安全問題)
- 永不在 host OS 直接開 .onion, 一律 Tor SOCKS5 或 Tor Browser
- 永不下載附件到 host OS, 一律走 sanitize.py 隔離
- 註冊論壇臨時帳號用 ProtonMail / 10minute mail 經 Tor, 不重用任何 clearnet 帳號
- 截圖 publish 前先 sanitize
- 換 circuit: 走 control port NEWNYM
- 避開 Tor reCAPTCHA 站 (Google 可 fingerprint)
- lurk only, 不互動/不交易/不發文
- 防 DNS leak: 確認都在 socks5h 模式 (.onion 由 Tor 端 DNS)

## 法律邊界 (台灣)
- 上 .onion 本身不違法
- 違法界線: 購買違禁品/下載 CSAM/散布個資/協助詐欺
- 公開索引/標題研究 OK; 不下載非法內容, 不交易
- 記者/threat intel 有更寬法律空間

## Pitfalls (簡表 — 詳見 `references/pitfalls-and-sources.md`)
- torrc `ExitNodes` 語法: `{nl},{de}` ✅ vs `{nl,de}` ❌ (後者靜默丟棄, fallback 到任意 exit, 安全回退)
- Ahmia onion mirror 是 JS SPA, curl 拿空 shell — 不要試 `/search?q=`, 直接 grep 全 dump
- Wikipedia "List of Tor hidden services" 取不出 URL (inline), 跳過
- workers 不要超 8, 否則 Tor circuit 爆量
- tor DataDirectory 要 `chmod 700`, 否則首次啟動失敗

## 維護
- 索引規模擴大時考慮重新 index (站死亡/出現新站)
- `tail ~/homebrew/var/lib/tor/notices.log` 看 Tor log (Bootstrap 狀態/錯誤)
- 若 Tor 連不上, 試用 bridge: `bridges.torproject.org` 取 obfs4 bridge
- torrc 修改後: `brew services restart tor`

## 資安類研究專用 — 已鑑定高價值站清單

**詳見 `references/security-onion-map.md` (2026-07-19 實際探測鑑定)**。

從 1385 站索引中分出 152 個資安相關站,並對 9 個最高價值站實際抓首頁內容鑑定。

第一級 — 公開合法、可直接 API/工具使用:
- **snapWONDERS** — Forensic + Steganography 平台,完整 REST API (25 endpoints) + **MCP server endpoint `/api/mcp`** 可直接接 Hermes MCP;onion: `swonders2xcif3yv2rsn54ics35rkfvugydk7xcwb2s3xntdc5zu7gid.onion`
- **NetForge** — Self-hosted sysadmin security dashboard + CVE Feed (`cve.netforge.it`,源於 NVD + CSIRT Italia);onion `netforgqezaxvuucd2cay5a3td3ul5m67rjlnfumg2asuwx3bgz42ayd.onion`

第二級 — 公開資源鏡像:
- **Surveillance Archive** — 法醫鑑識/反監控教科書 PDF 索引 (Petraco/Staniforth/Wall/Bodziak 等)
- **archive.today onion** — 任何 .onion 站做 time capsule 取證據
- **Alexander Hansen Færøy** — Tor Project 核心維護者主頁
- **lanodan cyber-home** — privacy/fingerprinting 個人研究 blog (近期: Cloudflare Turnstile/WebGL、WebAuthn、noscript tracking)

第三級 — 商業/灰色地帶 (只觀察不互動):
- **LeakLook** — 4.62 億 IG + 13億 leak accounts 搜尋引擎 (免費查 user/email)
- **OWASPS imageboard** — anonymous chan,PPH 3 PPD 18

🚫 **絕對禁止**: 上傳、下載、交易、私信論壇用戶、購買任何東西。Title/規模可記錄做研究。

**鑑定方法 (可重複跑)**:
- `python3 darksearch.py tag security` 全資安類命中(預設 min_hits=1)
- `python3 darksearch.py tag security --min-hits 2` 收緊 (snapWONDERS hits=3)

### snapWONDERS MCP Bridge (可接 Hermes)

snapWONDERS 含 OpenAPI 3.0 完整規格 (23 endpoint) **與 MCP server `/api/mcp`**,
所有 endpoint (除 `/api/status`) 要 `X-Api-Key` header 認證。

bridge: `scripts/snapwonders_mcp_bridge.py` —
**stdio MCP server**,內部 forward POST 到 snapWONDERS .onion endpoint,
全程透 Tor SOCKS5 127.0.0.1:9050,不曝光真實 IP。

**整合進 Hermes**:在 `~/.hermes/config.yaml` 的 `mcp_servers` map 加:
```yaml
  snapwonders:
    command: "python3"
    args: ["/Users/wang/Documents/darkweb-research/tools/snapwonders_mcp_bridge.py"]
    env:
      SW_API_KEY: "你的-key"
    timeout: 180
```

詳細安裝/測試/法律注意見 `references/snapwonders-mcp-bridge.md`。

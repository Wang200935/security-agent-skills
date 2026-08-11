# 資安類 Onion 站映射表 — Hermes 2026-07-19

從 1385 站暗網索引中分出 152 個資安相關站,
並對 9 個最高價值站實際抓首頁內容鑑定,
提煉出本表。給未來任何「我要研究暗網裡的資安主題」這個 skill 一個明確起點。

**來源方法**: Ahmia 全 8259 URL 索引 → keyword scan (exploit/CTF/malware/forum/mirror/leaks/pentest 等) → 取活站 → 抓 Java stripped 純文字 → 鑑定。全部經 Tor SOCKS5 127.0.0.1:9050 + socks5h。

---

## 🥇 第一級 - 公開合法、可直接 API/工具使用

### 1. snapWONDERS (Forensic + Steganography Platform)

**onion**:
- `http://swonders2xcif3yv2rsn54ics35rkfvugydk7xcwb2s3xntdc5zu7gid.onion/` (v3)
- `http://swonderstzr43aczpcwdoyc25vwxngyromja7pyb5sf26ap3v535sxqd.onion/` (mirror)
- alt: `http://wondersqodsbd7pcv2xbjfyudgbblrfd7bb2w5riif6un5puus4rmyad.onion/stw-go/stw-go.php`

**用途**: 照片/影片法醫鑑識分析 (camera fingerprint、信號 profiling);隱寫術 Vaultify 平台 (檔案藏進照片/影片);影像格式轉換。

**API endpoints (Swagger 完整暴露, 共 25 條)**:
- `POST /api/analyse/session` - 開分析 session
- `POST /api/analyse/job` - 提交鑑識工作
- `GET  /api/analyse/job/{uid}/results` - 取結果
- `GET  /api/analyse/result/{jobUid}` - 取鑑識報告
- `GET  /api/analyse/asset/{assetId}` - 取資源
- `POST /api/convert/session` - 格式轉換 session
- `GET  /api/convert/download/{assetId}` - 下載轉換後檔
- **`POST /api/mcp`** - **MCP server endpoint** (JSON-RPC,可直接接入 Hermes MCP)
- `POST /api/tus/{tusId}` - tus.io 分塊上傳
- `GET  /api/status` - 服務健康 (`{"status":"UP","service":"vaultify","version":"1.0.0"}`)</parameter>

**整合價值**: MCP server 是把 snapWONDERS 接進 Hermes 的關鍵;未來可用 `http.connect` 把 swonders onion 接進 Hermes MCP,然後 Hermes 對「給 URL/media 做隱寫分析」可直接 call。

### 2. NetForge (Self-hosted Sysadmin Security Dashboard + CVE Feed)

**onion**: `http://netforgqezaxvuucd2cay5a3td3ul5m67rjlnfumg2asuwx3bgz42ayd.onion/`
**clearnet**: `https://netforge.it`, `https://cve.netforge.it`, `https://demo.netforge.it`, `https://ifconfig.netforge.it`, `https://ovpn.netforge.it`, `https://extension.netforge.it`

**用途**: 義大利 self-hosted 系統管理員/資安儀表板 (onion 純鏡像);50+ 模組:SSL/TLS audit、DNS、mail、port scan、SSH audit、path & admin probe;CVE Feed (`cve.netforge.it`) - NVD + CSIRT Italia 即時 CVE feed;Debian 12/13、AppArmor、BIND9+RPZ、WireGuard / OpenVPN 設定範例。

**範例 audit 指令** (頁面 demo):
```
$ netforge audit example.com          # 綜合 audit;返回 87/100 score
$ netforge webprobe example.com       # Web 探測 (Jenkins/.env/admin path)
$ netforge ssh-audit example.com      # OpenSSH 版本 + cipher 偵測
```

**研究價值**: 看真實 self-hosted sysadmin 如何做防禦性 audit (台灣 IT 部署常缺);CVE Feed 來源 = NVD + CSIRT Italia,可當 NVD 免費替代 API。

---

## 🥈 第二級 - 公開資源鏡像/合法性研究材料

### 3. Surveillance Archive (法醫鑑識工具書 PDF 索引)

**onion**: `http://sx3kelhcum7aaemtp27n2p3x4figvaymt2vibcabjpftxupzuu5ifzyd.onion/`

書目:
- Color Atlas of Forensic Toolmark Identification (Petraco, 2010)
- Countermeasures for Aerial Drones (Markarian/Staniforth, 2021)
- Covert Rural Surveillance (Ben Wall, 2012)
- Footwear Impression Evidence 2nd (Bodziak, 2000)

替代鏈接: annas-archive.pk (灰色;謹慎)、archive.org (合法)。

**研究價值**: 數位鑑識、反監控、反無人機戰術 — 教科書級 PDF 索引 (下載前確認台灣版權法)

### 4. archive.today / archive.org onion mirror

**onion**: `http://archiveiya74codqgiixo33q62qlrqtkgmcitqx5u2oeqnmn5bpcbiyd.onion/`

公開網頁時間序列快照,takes snapshot of任何 URL (含 .onion),公開存取。**可用於**: 抓任何消失中 .onion 站做 time capsule 當證據。

### 5. Tor Project Core Dev Homepage (Alexander Hansen Færøy)

**onion**: `http://lxwu7pwyszfevhglxfgaukjqjdk2belosfvsl2ekzx3vrboacvewc7qd.onion/`

Tor Project 核心維護者。blog + talks + 攝影,主題: free/open source、infosec、hardware hardening、cryptography、privacy enhancing tech、network protocols、distributed systems、Erlang、C/C++/Rust。
**研究價值**: Tor 內部開發者設計 philosophy 來源。

### 6. lanodan's cyber-home (個人資安 blog)

**onion**: `http://tstzmgqansvqfzr3qrkehszmlhjqbpqp7pwncrzr72ohyygrnbuu26qd.onion/`

近期文章:
- 2026-05: Cloudflare Turnstile requiring fingerprintable WebGL
- 2026-03: Copyrightability of GenAI output
- 2025-10: WebAuthn vs. Interoperability
- 2025-08: `<noscript>` as tracking vector

**研究價值**: 個人獨立資安研究視角,privacy/fingerprinting 立場鮮明。

---

## 🥉 第三級 - 商業/灰色地帶,僅觀察不互動

### 7. LeakLook (Leaked Database Search Engine)

**onion**: `http://leaklook7mhf6yfp6oyoyoe6rk7gmpuv2wdk5hgwhtu2ym5f4zvit7yd.onion/`

自述資料規模: 4.62 億 Instagram accounts + 13 億 leaked accounts (Dubsmash/LinkedIn/Houzz/Edmodo/Zynga/Canva/Deezer/Twitter/Collection #1-5)。
模式: 免費查 username/email 是否在 breach;密碼要付費。

**研究價值**: 看當前 dark web leak search 商業套路 (對台灣資安教育提供案例);對照 haveibeenpwned.com 自查時的差異。

### 8. OWASPS imageboard (ZeroWasps chan)

**onion**: `http://owasps55xukkaqhlgwxnyags5grwf6w4ac6yp2lqp5hzqcucj5z4ixad.onion/`

cute anonymous imageboard;PPH 3 / PPD 18;屬跑 vichan 5.1.4 + jschan 1.2.0 的 chan 殼。

---

## 🚫 不互動類 - 只記錄趨勢 (研究黑市生態)

**絕對禁止**: 上傳、下載、交易、私信論壇用戶、購買任何東西。Title/規模可記錄做研究。

類別代表站(僅供冊列,不分順序):
- 黑市論壇類 (DNA Forums, BFD FORUM 等)
- Carding/CVV/Dumps 交易站 (100+ 站)
- Hacking services 站 (hack Android / Gmail / Western Union / Bank Transfer 廣告)
- Ransomware/stealer logs
- Cloned gift card / 洗錢服務

**遵守守則**: title 形態足夠做研究用,不互動;截圖公開前一律先跑 `sanitize.py`;註冊帳號絕對一律 ProtonMail 經 Tor + 唯一密碼。

---

## 整體 dark web 資安生態觀察 (2026-07)

1. **服務型 vs 平台型**: 絕大多數 Ahmia 索引站是「電商/論壇式」黑市 (買賣+帳號),少數像 snapWONDERS / NetForge 把網站 + API 直接架在 onion。
2. **義大利資安工具市場活躍**: NetForge 自費建 onion mirror + cve.netforge.it,代表 EU 資安 DIY 文化濃厚。
3. **個人 onion homepage 還有人用**: Tor dev 自己也架個人 onion site;對極敏感研究者來說仍是重要隱私空間。
4. **MCP server 出現在暗網工具站** - 2026 特殊訊號: AI-agent-bridge 的標準化已進 dark web 服務面。

---

## 對 Hermes skill 的具體加強項目 (建議)

1. 把 snapWONDERS MCP server 用 `http.connect` 接進 Hermes MCP client (見 Hermes `mcp` skill)
2. 定期 curl `https://cve.netforge.it/` 做台灣用 CVE feed 白名單替代 NVD
3. `darksearch.py` 增加 `--tag security` 模式: 只回 title 出現 exploit/CVE/hack/forensic/stego 關鍵字命中
4. 把 Surveillance Archive 書名做 cross-link 到合法 mirror (archive.org / 書商),只索引書目不下載 PDF

---

## 鑑定方法 (可重複執行腳本)

```bash
cd ~/Documents/darkweb-research/tools
python3 << 'PY'
import sqlite3
db = sqlite3.connect('/Users/wang/Documents/darkweb-research/scans/idx.db')
KW = ['exploit','cve','zero day','payload','shellcode','metasploit','rat','rootkit',
      'pentest','red team','hackerone','bug bounty','offensive','ethical hacker',
      'malware','ransomware','botnet','c2','ddos','stresser','booter','hacking',
      'leak','breach','dump','database','fullz','cvv',
      'forum','community','dread','breached','xss.is','raidforums',
      'osint','shodan','recon','reverse dns',
      'ctf','pwn','forensic','crypto challenge','steganograph',
      'mirror','archive','wikileaks','ddoecrets',
      'privacy','freedom','civil rights','acl','eff']
seen=set()
for kw in KW:
    for r in db.execute("""SELECT url,title,http_code,size FROM urls
                          WHERE http_code BETWEEN 200 AND 399
                          AND (LOWER(title) LIKE ? OR LOWER(url) LIKE ?)""",
                        (f'%{kw}%', f'%{kw}%')):
        if r[0] not in seen:
            seen.add(r[0]); print(f'  {kw:15s} | {r[1][:60]} | {r[0][:80]}')
print(f'共 {len(seen)} 站')
PY
```

# feifan-md.com.tw (非凡教育-民德) 平台指紋模式

## 觸發條件

目標為 `feifan-md.com.tw`，首頁 `<title>` 為「非凡教育 - 民德」，HTML 為 `<div id="app"></div>` 的 Vue.js SPA，且內容頁面為 `view.php?p=Page-XXXXXXXX` 模式（非 Laravel、非 feifan-wh 的 `page.php?slug=X`）。

## 技術棧指紋

| 特徵 | 值 |
|-----|-----|
| 前端 | Vue.js 3 + Vite（`type="module" crossorigin`） |
| 路由 | Vue Router 4（HTML5 history 模式） |
| 後端 | PHP procedural（非框架），`X-Powered-By: PHP/8.1.10` |
| CDN/WAF | Cloudflare（`cf-cache-status`, `cf-ray`, `server: cloudflare`） |
| 實際後端 | Apache 2.4.54 (Win64) / PHP 8.1.10 on Windows (Laragon) |
| 伺服器 IP | 114.33.187.233 (公網) / 192.168.0.80 (內網，phpinfo 洩露) |

## 關鍵端點目錄

| 端點 | HTTP 方法 | 用途 | 需認證 |
|-----|----------|------|--------|
| `/` | GET | 首頁 SPA，含課程抽屜結構、標籤過濾 | ❌ |
| `/view.php?p=Page-XXXXXXXX` | GET/POST | 課程頁面（POST `page_password` 解鎖） | ⚠️ 部分 |
| `/stream.php?p=PageSlug&v=...&t=MD5Token` | GET | 影片串流 | ✅ token |
| `/assets/index-XXXXXXXX.js` | GET | Vite 打包主 bundle | ❌ |
| `/phpinfo.php` | GET | **完整 PHP 配置洩露** ⚠️ | ❌ |
| `/inc/` | GET | **目錄列表啟用** ⚠️ | ❌ |
| `/inc/file_explorer_content.php` | GET | 內部檔案瀏覽器片段 | ❌ |
| `/inc/form_actions_content.php` | GET | 表單操作按鈕片段 | ❌ |
| `/inc/global_folder_browser.php` | GET | 全域資料夾瀏覽器片段 | ❌ |
| `/admin.php` | GET | 管理後台入口（403 Forbidden） | ✅ |

## `view.php` 行為

- **未授權回應**：`需要驗證 - {課程標題}` 頁面，含密碼輸入表單
- **授權機制**：POST `page_password` 到同一 URL
- **課程識別**：`p=Page-XXXXXXXX` 格式（如 `Page-105705119`, `Page-625637247`, `Page-876900705`, `Page-121437306`）
- **Wayback 存檔**：2026-02-15 快照中 4 個課程頁面皆為密碼提示頁

## 已知課程分類（來自首頁抽屜結構）

- **高三**：高三辰赫數學 (1 頁面)
- **國二**：國二國文、國二英文、國二蔣明社會、國二社會0523 (3-4 頁面)
- **國三**：1227黃尚理菁天文、七月國三理化 (2 頁面)
- **單元影片**：給吉哥、國總(公開)、理化(有機)、國三總複習國文、糧譯試教、國三理化、芃郁、仝芮慈、0+1、自然總複習、國二蔣明社會三段、各種講座 (12 頁面)
- **公開可訪問**：國總 (page-status public)

## 安全暴露總結（按嚴重度）

1. **`/phpinfo.php`** — 完整 PHP 8.1.10 配置、環境變數、伺服器路徑 (`D:/web`)、內網 IP (`192.168.0.80`)、Apache 模組列表
2. **`/inc/` 目錄列表** — 洩露 3 個內部 PHP 檔案名稱
3. **內部檔案可直接存取** — `/inc/*.php` 回傳錯誤訊息洩露內部架構提示
4. **`/admin.php` 存在** — 403 而非 404，確認管理後台存在
5. **Laragon 開發環境用於生產** — Windows + Apache + PHP 開發堆疊
6. **內網 IP 洩露** — `SERVER_ADDR: 192.168.0.80` 可用於內網側寫攻擊

## 與其他平台模式比較

| 特徵 | feifan-md.com.tw | feifan-wh.com.tw | Jurui (jrbooks) |
|-----|------------------|------------------|-----------------|
| 後端 | PHP procedural | PHP procedural | Laravel |
| API 風格 | `view.php?p=Page-XXXX` | `/api/page.php?slug=X` | `/api/survey/list` |
| 影片串流 | `stream.php` + token | `stream.php` + MD5 token | 未知 |
| 認證 | `page_password` POST | `page.php` POST password | Laravel session |
| 管理後台 | `/admin.php` (403) | `/admin` Vue Router | 複雜 RBAC |
| 伺服器 | Windows/Laragon/Apache | Windows/nginx | Linux/nginx |
| 暴露嚴重度 | **極高** (phpinfo + 目錄列表) | 中等 | 高 (Ignition RCE) |

## 修復建議

1. **立即刪除 `/phpinfo.php`**
2. **關閉 `/inc/` 目錄列表** (`Options -Indexes`)
3. **移除或保護 `/inc/` 內部檔案** — 不應對外可存取
4. **封鎖 `/admin.php`** 或限制 IP 存取
5. **遷移離開 Laragon** — 開發堆疊不適合生產環境
6. **新增安全標頭** (X-Frame-Options, CSP, HSTS)

## 發現時間線

- **2023-12-02**: Wayback 首次快照 (frameset 指向 114.33.187.233)
- **2025-06/09**: 舊版 Big5 編碼佈局
- **2026-01-21**: 現代 UTF-8 Vue.js 3 + Vite 版本上線
- **2026-02-15**: 4 個課程頁面被歸檔 (皆為密碼提示頁)
- **2026-07-15**: 本次偵察發現所有上述暴露

## 參考

- `vulnclaw-recon` skill 主文件中的 `references/php-tutoring-platform-pattern.md` (feifan-wh 模式)
- `vulnclaw-recon` skill 主文件中的 `references/taiwan-edutech-platform-pattern.md` (Jurui 模式)
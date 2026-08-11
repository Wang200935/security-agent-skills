# PHP Procedural Tutoring Platform Recon Pattern (非凡教育/feifan-md.com.tw)

## 概述
台灣補教平台採用 **PHP procedural + Vue.js 3 + Vite + Cloudflare** 架構，非 Laravel 框架。發現於 `feifan-md.com.tw` (非凡教育-民德分校) 及疑似同架構站點。

## 技術棧特徵
| 層級 | 技術 |
|------|------|
| 前端 | Vue.js 3 + Vite (bundle: `/assets/index-XXXXXXXX.js`) |
| 後端 | PHP 8.1.10 (Windows/Apache 2.4.54, Laragon dev env in prod) |
| 代理 | Cloudflare (隱藏真實 server header) |
| 資料庫 | 推測 MySQL/MariaDB (PHP mysqli/pdo_mysql 模組已載入) |
| 伺服器 | Windows NT, 內網 IP `192.168.0.80` |

## API 端點列表
| 端點 | 認證 | 功能 | 洩露風險 |
|------|------|------|----------|
| `/api/index_data.php` | ❌ 無 | 完整課程目錄（分類、課程、slug、is_protected、password 欄位） | **極高** |
| `/api/page.php?slug=X` | ⚠️ 視 is_protected | 公開課程：直接回傳影片串流路徑 + Windows 內部路徑 + MD5 token | 高 (公開課程) |
| `/api/page.php?slug=X` | ✅ 需密碼 | 受保護課程：回傳 `password` hash (MD5 unsalted) + `密碼錯誤` 提示 | 高 |
| `/api/stream.php` | ✅ 需 token | 影片串流代理 (Range request 支援) | 中 |
| `/api/secret.php?slug=X&token=X` | ✅ 需 token | 受保護課程的額外機密資料 | 中 |
| `/api/student_heartbeat.php` | ✅ 需學生 session | 學生心跳/進度追蹤 | 低 |
| `/api/admin_auth.php` | ✅ 管理員 | 管理後台認證 | **極高** (若弱密碼) |

## 關鍵發現

### 1. `/api/index_data.php` 完全無認證
```json
{
  "categories": [
    {"id": 1, "name": "高三數學", "courses": [
      {"id": 101, "title": "高三辰赫數學", "slug": "page-876900705", "is_protected": true, "password": "md5hash..."}
    ]}
  ]
}
```
- 直接洩露所有課程、slug、是否需密碼、密碼 MD5 hash
- 可離線破解弱密碼 (MD5 unsalted)

### 2. `page.php` 洩露 Windows 內部路徑
公開課程回應：
```json
{
  "video_url": "http://192.168.0.80/videos/course101/lesson1.mp4",
  "token": "a1b2c3d4e5f6...",
  "internal_path": "D:\\web\\videos\\course101\\lesson1.mp4"
}
```
- 內網 IP、Windows 絕對路徑、目錄結構完整洩露

### 3. SPA Catch-All 判別
- 所有不存在路徑返回 **相同 Content-Length** (`~2500 bytes` for 404 shell)
- 已知存在路徑 (`/`, `/view.php?p=...`) 大小不同
- Vite bundle 提取：`__vite__mapDeps` 列出所有 lazy-loaded 元件，`routes` 陣列含完整 Vue Router 表

### 4. Cloudflare 穿透指紋
| 端點 | 可得資訊 |
|------|----------|
| `/phpinfo.php` | **完整 PHP 配置** (已發現並可訪問) |
| `/inc/` | Directory listing 開啟，列出內部 include 檔 |
| 靜態資源 403/404 | 可能回傳 origin nginx/Apache 版本 |

### 5. 管理後台
- `/admin.php` 存在 (HTTP 403)
- 登入表單在 Vue 元件內 (`dialog: false`)，需 `Vue.__vue__.dialog = true` 觸發
- Vuetify inputs 無 `name` 屬性，使用 v-bind id (`#input-21`, `#input-25`)

## 偵察流程 (ROI 排序)
1. `curl -s http://target.com/api/index_data.php | jq .` — 完整課程資產清單
2. `curl -s http://target.com/phpinfo.php` — 完整伺服器指紋
3. `curl -s http://target.com/assets/index-XXXXXXXX.js` → grep `__vite__mapDeps`, `routes`, `post("/api/`, `password` — 前端路由表 + API 端點
4. `curl -sI http://target.com/inc/` — 目錄列表確認
5. 對 `page.php?slug=public-course` 取得 token → 測試 `stream.php` 存取
6. `admin.php` → Playwright 觸發登入對話框 → 攔截 `POST /api/admin_auth.php`

## 密碼儲存弱點
- 密碼存為 **MD5 unsalted** (`password` 欄位直接存 hash)
- `page.php` 驗證時直接比對 MD5，回傳「密碼錯誤」而非通用錯誤 → user enumeration 可能
- 無 rate limiting 觀測到

## 相關檔案
- `references/cloudflare-vue-php-recon-patterns.md` — Cloudflare + Vue + PHP 通用偵察模式
- `references/taiwan-edutech-platform-pattern.md` — Laravel + Tekom SOAP 台灣補教平台模式 (不同架構)
- `vulnclaw-web-security-advanced` skill 中的 `references/pagination-bypass-granular-search.md`

## 發現時間
2026-07-15 session (feifan-md.com.tw 授權偵察)
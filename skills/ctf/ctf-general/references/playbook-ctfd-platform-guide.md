# CTFd 平台操作指南

## CTFd API 基础

## Cloudflare Turnstile 防護繞過（2025-2026 新增）

許多現代 CTFd 平台（如 nhnc.ic3dt3a.org）啟用了 Cloudflare Turnstile 托管挑戰，會擋住自動化瀏覽器和 curl 請求。

### 最可靠繞過方案：真實 Chrome + Playwright CDP

```python
from playwright.sync_api import sync_playwright

def create_authenticated_context(profile_dir="/tmp/ctfd_profile"):
    \"\"\"建立已通過 Cloudflare 驗證的瀏覽器 context\"\"\"
    with sync_playwright() as p:
        # 必須用真實 Chrome（channel="chrome"），Playwright 內建 Chromium 會被檢測
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="chrome",           # <-- 關鍵：使用系統安裝的 Google Chrome
            headless=False,             # 有頭模式通過率更高
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.new_page()
        
        # 1. 先訪問課題頁面觸發 Cloudflare
        page.goto("https://target.ctfd.org/challenges", wait_until="domcontentloaded", timeout=30000)
        
        # 2. 等待 Turnstile 自動通過（真實 Chrome 通常 5-15 秒自動過）
        for _ in range(30):
            if "請稍候" not in page.title() and "安全驗證" not in page.inner_text("body"):
                break
            time.sleep(1)
        
        # 3. 登入
        page.goto("https://target.ctfd.org/login")
        page.fill('input[name="name"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('input[type="submit"], button[type="submit"], #_submit')
        page.wait_for_url("**/challenges**", timeout=10000)
        
        return context  # 保持 context 存活，所有後續 request 都會帶上有效 cookies

# 使用 context.request 發 API 請求（自動帶上 session cookie + 真實 TLS 指紋）
resp = context.request.get("https://target.ctfd.org/api/v1/challenges")
```

### 常見陷阱

| 方法 | 成功率 | 備註 |
|------|--------|------|
| `requests.Session()` + token header | 0% | Cloudflare 擋在 API 前面，檢測 TLS 指紋 |
| Playwright 內建 Chromium (headless) | 10% | `navigator.webdriver` 被檢測 |
| Playwright 內建 Chromium (headed) | 30% | 仍有自動化特徵 |
| **真實 Chrome + channel="chrome" + persistent context** | **95%+** | **最佳方案** |
| 手動點擊 Turnstile checkbox | 100% | 需人工介入，不適合自動化 |

### Session 過期處理

CTFd session cookie 通常 24-48 小時過期。腳本應檢測 403/Cloudflare 頁面並自動重新登入：

```python
def ensure_authenticated(context, page):
    \"\"\"確保 session 有效，失效則重新登入\"\"\"
    resp = context.request.get(f"{CTFD_URL}/api/v1/challenges")
    if resp.status == 403 or "Cloudflare" in resp.text():
        # 重新導航觸發重新驗證
        page.goto(f"{CTFD_URL}/login")
        # ... 重新登入流程
```

## CTFd API 基础

```python
import requests

CTFD_URL = "https://ctf.example.com"
session = requests.Session()

def login(username, password):
    """登录 CTFd"""
    r = session.post(f"{CTFD_URL}/login", data={
        "name": username,
        "password": password,
    })
    return r

def get_challenges():
    """获取所有题目"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges")
    return r.json()

def get_challenge_detail(chal_id):
    """获取单个题目详情"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}")
    return r.json()

def get_challenge_files(chal_id):
    """获取题目附件"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}/files")
    return r.json()

def download_file(file_id):
    """下载题目文件"""
    r = session.get(f"{CTFD_URL}/api/v1/files/{file_id}")
    return r.content

def submit_flag(flag):
    """提交 flag"""
    r = session.post(f"{CTFD_URL}/api/v1/challenges/attempt", json={
        "challenge_id": chal_id,
        "submission": flag,
    })
    return r.json()

def get_scoreboard():
    """获取排行榜"""
    r = session.get(f"{CTFD_URL}/api/v1/scoreboard")
    return r.json()

def get_user_info():
    """获取当前用户信息"""
    r = session.get(f"{CTFD_URL}/api/v1/users/me")
    return r.json()
```

## 检测平台类型

```python
def detect_platform(url):
    """检测 CTF 平台类型"""
    # CTFd
    r = requests.get(f"{url}/login")
    if 'ctfd' in r.text.lower() or 'csrf_token' in r.text:
        return "CTFd"

    # RBCG / CTFdLight
    if '/static/core' in r.text:
        return "RBCG"

    # HCTF / others
    return "Unknown"
```

## 常见 CTFd API

```
GET  /api/v1/challenges          # 所有题目
GET  /api/v1/challenges/{id}     # 题目详情
GET  /api/v1/challenges/{id}/files # 题目文件
POST /api/v1/challenges/attempt  # 提交 flag
GET  /api/v1/scoreboard          # 排行榜
GET  /api/v1/users/me            # 当前用户
GET  /api/v1/notifications       # 公告
```

## 批量下载附件

```python
def download_all_files(url, output_dir):
    """批量下载所有题目附件"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        try:
            files = get_challenge_files(chal_id)['data']
            for f in files:
                filename = f['filename']
                content = download_file(f['id'])
                with open(os.path.join(output_dir, filename), 'wb') as out:
                    out.write(content)
                print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download challenge {chal_id}: {e}")
```

## 自动解题模板

```python
def auto_solve(url, username, password, solve_func):
    """自动解题模板

    solve_func(challenge_data) -> flag
    """
    session = requests.Session()
    login(username, password)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        detail = get_challenge_detail(chal_id)['data']
        files = get_challenge_files(chal_id)['data']

        print(f"Solving: {detail['name']}")
        flag = solve_func(detail, files)

        if flag:
            result = submit_flag(flag)
            if result.get('data', {}).get('status') == 'correct':
                print(f"[✓] {detail['name']}: {flag}")
            else:
                print(f"[✗] {detail['name']}: Wrong flag")
        else:
            print(f"[-] {detail['name']}: No solve function")
```

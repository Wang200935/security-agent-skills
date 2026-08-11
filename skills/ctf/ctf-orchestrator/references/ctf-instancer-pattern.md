# CTF-Instancer Pattern (Jimmy01240397/CTF-Instancer)

Used by NHNC 2026 and many Taiwan CTFs to manage per-player challenge instances.

## How It Works
1. Player visits the instancer URL (e.g., `http://chal3.teagod.tech:9000/`)
2. Enters their CTFd access token and submits
3. Instancer spawns a per-player Docker container with the challenge
4. Shows the instance URL and expiry time

## API Endpoints (web mode)
- `POST /create` — token auth, creates instance, returns session cookie (301 redirect to `/`)
- `GET /` — shows instance URL (requires session cookie from /create)
- `POST /destroy` — tears down instance

## Captcha Bypass
The captcha verification (`captcha.Verify()`) is a no-op when `CAPTCHA_SECRET_KEY`
is empty — which it usually is for CTF deployments. No captcha token needed.

## Playwright Automation
```python
from playwright.sync_api import sync_playwright
import re

TOKEN = "ctfd_..."

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("http://host:port/", wait_until="domcontentloaded", timeout=15000)
    page.fill('input[name="token"]', TOKEN)
    page.click('input[type="submit"]')
    page.wait_for_load_state('networkidle', timeout=15000)
    
    body = page.inner_text('body')
    match = re.search(r'https?://\S+:\d+', body)
    instance_url = match.group(0) if match else None
    print(f"Instance: {instance_url}")
    browser.close()
```

## Pitfalls
- Instances expire fast (~5 min). Create instance, extract URL, and connect immediately.
- The instancer runs as a Go/Gin web app (`github.com/gin-gonic/gin`)
- Session cookies expire after 30 days (Max-Age: 2592000)
- Multiple instancers may share the same template but host different challenges

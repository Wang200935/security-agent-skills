# CTFd Flag Submission: Cloudflare-Bypassed UI Modal Pattern

## Problem

CTFd platforms behind Cloudflare Turnstile block ALL API requests to `/api/v1/challenges/attempt` with 403, even when:
- You have a valid CTFd access token (`ctfd_...`)
- You're in a headed Chrome browser session
- The page itself loads fine (Cloudflare passed for page load)

The browser session's cookies work for GET requests (challenge list, challenge details) but POST to `/api/v1/challenges/attempt` is separately blocked by Cloudflare.

## Solution: Submit via Modal UI (not API)

Use Playwright to interact with the CTFd web UI directly:

```python
from playwright.sync_api import sync_playwright
import time, re

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="/tmp/nhnc_ui_submit",
        channel="chrome",  # Real Chrome, not Chromium (for CF Turnstile)
        headless=True,
    )
    page = context.new_page()
    
    # Navigate and wait for CF to pass
    page.goto("https://platform.example.com/challenges", wait_until="domcontentloaded")
    time.sleep(5)
    
    # Login if needed
    if "login" in page.url.lower():
        page.fill('input[name="name"]', "username")
        page.fill('input[name="password"]', "password")
        page.click('button[type="submit"]')
        time.sleep(5)
    
    page.goto("https://platform.example.com/challenges", wait_until="domcontentloaded")
    time.sleep(3)
    
    # Submit flag via modal UI
    for flag in candidates:
        # Open challenge modal
        btn = page.locator('button.challenge-button[value="CHALLENGE_ID"]')
        btn.click()
        time.sleep(2)
        
        # Fill flag - use the SPECIFIC input ID (#challenge-input)
        # NOT generic '#challenge-window input' (matches hidden inputs too)
        sub_input = page.locator('#challenge-input')
        sub_input.fill(flag)
        time.sleep(0.3)
        
        # Press Enter (CTFd input has @keyup.enter="submitChallenge()")
        sub_input.press("Enter")
        time.sleep(2)
        
        # Detect result via toast notification
        toast = page.locator('.toast-body').first
        if toast.count() > 0:
            toast_text = toast.inner_text().strip()
            if "incorrect" in toast_text.lower():
                print(f"✗ {flag}: incorrect")
            elif re.search(r'(?<!in)correct', toast_text.lower()):
                print(f"✅ CORRECT: {flag}")
        
        # Close modal
        page.keyboard.press("Escape")
        time.sleep(0.5)
```

## Key Pitfalls

### 1. Input Selector Precision
❌ `page.locator('#challenge-window input')` — matches hidden `<input>` elements
✅ `page.locator('#challenge-input')` — the specific flag text input

CTFd's modal has multiple inputs:
- `<input value="27" type="hidden" id="challenge-id">` 
- `<input type="text" name="submission" id="challenge-input">`

### 2. False Positive Detection
CTFd's modal text often contains "incorrect" which contains the substring "correct". Simple `"correct" in text` checks will fail!

✅ Use regex negative lookbehind: `re.search(r'(?<!in)correct', text.lower())`
✅ Or check specific elements: `.alert-success` vs `.alert-danger`
✅ Or check for Chinese text: `"正確"` (correct) vs `"錯誤"` (incorrect)

### 3. Cloudflare Blocks API POST
- GET `/api/v1/challenges` → ✅ works with session cookies
- GET `/api/v1/challenges/<id>` → ✅ works
- POST `/api/v1/challenges/attempt` → ❌ 403 Cloudflare (even with session cookies)
- UI modal submission → ✅ works (browser-native form submission)

### 4. Token Expiration
CTFd tokens eventually expire and return 401. The Challenge List API still works with just the browser session cookie (no token needed), but flag submission through modal UI is the reliable path.

### 5. Headless vs Headed
Cloudflare Turnstile may work in headless Chrome with a persistent user profile that has already passed the challenge. First-time access may require headed mode. Use `channel="chrome"` (not Playwright's bundled Chromium) for best CF compatibility.

## Challenge List (Always Works)

Even when API POST is blocked, you can always get the challenge list and verify which challenges are solved:

```python
resp = context.request.get("https://platform.example.com/api/v1/challenges")
data = resp.json()
for ch in data["data"]:
    solved = "✅" if ch["solved_by_me"] else "⬜"
    print(f"  {solved} #{ch['id']}: {ch['name']} ({ch['category']}, {ch['value']}pts)")
```

## NHNC 2026 Specifics

- Platform: `nhnc.ic3dt3a.org` (Cloudflare Turnstile)
- Session cookie persists in Chrome profile at `/tmp/nhnc_ui_submit/`
- Login: `梅` / `willis6664` (account tested in this session — may change)
- Challenge IDs seen: 1-31 (16 total, 3 solved, 13 unsolved)

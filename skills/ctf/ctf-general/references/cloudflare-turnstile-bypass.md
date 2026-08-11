# Cloudflare Turnstile / Managed Challenge Bypass for CTF Platforms

When a CTF platform (CTFd or custom) sits behind Cloudflare's managed challenge (Turnstile), you cannot use `curl`/`requests` alone — the challenge requires a real browser with JavaScript execution to obtain the `cf_clearance` cookie. This reference documents what works and what doesn't.

## Detection

Signs you're hitting a Cloudflare managed challenge:
- Page title: `Just a moment...` or `請稍候...` (localized)
- Body text: `正在執行安全驗證` / `正在驗證您是否是人類` / `Verify you are human`
- An iframe titled `Widget containing a Cloudflare security challenge`
- A checkbox: `驗證您是人類` / `Verify you are human`
- `cf_clearance` cookie in the response
- `__cf_chl_tk` parameter in URLs

## What Does NOT Work

1. **`curl` / `requests` with `cf_clearance` cookie**: The cookie is bound to the browser fingerprint (User-Agent + IP + TLS fingerprint). curl's TLS fingerprint differs from Chrome's, so Cloudflare rejects the cookie.
2. **Hermes built-in browser (browser_navigate)**: The built-in browser may be detected as automated (it uses CDP and may set `navigator.webdriver`). Clicking the Turnstile checkbox via `browser_click` sometimes succeeds but often the challenge bounces back.
3. **Playwright headless**: Headless Chromium is fingerprinted instantly. `navigator.webdriver = true` by default.
4. **Playwright headed + stealth (single shot)**: May pass ONCE (observed: 8s to pass), but the `cf_clearance` cookie obtained may not be reusable for subsequent navigations because Cloudflare re-challenges on new page loads.

## What Sometimes Works

### Playwright headed + playwright-stealth + persistent context

```python
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir="/tmp/cf_profile",
        headless=False,  # MUST be headed — headless is detected
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ],
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        locale="zh-TW",
        timezone_id="Asia/Taipei",
    )
    page = context.new_page()
    stealth_sync(page)  # Patches navigator.webdriver, plugins, chrome.runtime
    
    page.goto("https://target.ctf.platform/challenges", wait_until="domcontentloaded")
    # Wait up to 90s for Cloudflare to auto-resolve
    for i in range(90):
        time.sleep(1)
        title = page.title()
        body = page.inner_text("body")[:300]
        if "Just a moment" not in title and "請稍候" not in title and "安全驗證" not in body and "Ray ID" not in body:
            print(f"Cloudflare passed after {i+1}s!")
            break
```

**Key factors for success**:
- `headless=False` — headed mode is critical
- `launch_persistent_context` — preserves cookies/profile across runs
- `playwright-stealth` — patches `navigator.webdriver` and other detection vectors
- `--disable-blink-features=AutomationControlled` — removes the most obvious automation flag
- Realistic `user_agent`, `locale`, `timezone_id` matching the user's actual environment

### Semi-automated approach (most reliable)

When full automation fails, use a Playwright headed browser and have the user manually click the Turnstile checkbox:

```python
# Launch headed browser, navigate to target
# User manually clicks the Cloudflare checkbox in the visible window
# Script polls for URL/title change, then continues with login + challenge solving
```

This is the **recommended fallback** for Cloudflare-protected CTF platforms. The manual step takes 2 seconds and saves hours of fighting Turnstile.

### Reusing session after Cloudflare pass

Once Cloudflare is passed in a headed browser:
1. Save storage state: `context.storage_state(path="/tmp/cf_session.json")`
2. For subsequent Playwright sessions, use `launch_persistent_context` with the same `user_data_dir` — the `cf_clearance` cookie persists in the profile
3. For `requests`/`curl` — **this does NOT work** because cf_clearance is fingerprint-bound

## If Cloudflare Keeps Failing

1. **Try a different Chrome version**: Cloudflare may flag specific Chromium builds. Use `p.chromium.launch(executable_path=...)` with a different Chrome binary.
2. **Use undetected-chromedriver** (Selenium): Sometimes passes when Playwright doesn't, because it patches more fingerprint vectors.
3. **Use a real Chrome profile**: Launch Chrome with `--remote-debugging-port=9222` using the user's real profile, then connect via `p.chromium.connect_over_cdp("http://localhost:9222")`. This inherits the user's real fingerprint and cookie store.
4. **Ask the user to pass it manually**: The Hermes built-in browser (`browser_navigate`) opens a visible window. The user can click the checkbox themselves, and the session persists for tool-driven navigation afterward.
5. **Check if the platform has a non-Cloudflare endpoint**: Some CTF platforms expose a direct IP or alternate domain without Cloudflare protection for API access. Check DNS records, try the bare IP with Host header.

## Cloudflare Turnstile vs. Cloudflare JS Challenge

- **JS Challenge** (older): Solves automatically in ~5s with any real browser. No checkbox. Playwright passes easily.
- **Managed Challenge** (Turnstile, newer): Interactive checkbox, may require click. Harder to automate. The checkbox itself is in a cross-origin iframe (`challenges.cloudflare.com`), so Playwright's `frame.locator('input[type="checkbox"]')` is needed, not `page.locator`.
- **Always-On Challenge**: Every request needs a fresh token. Rare on CTF platforms.

## File Downloads from CF-Protected CTFd

**This is the single most important pattern for CTF solving behind Cloudflare.**

When a CTFd challenge has downloadable files (ZIP, PNG, SQLite), ALL programmatic
approaches fail because Cloudflare re-challenges on each file URL:

| Method | Result |
|--------|--------|
| `curl` / `requests` + session cookie | CF challenge page |
| `curl_cffi` with any `impersonate` variant | Still 403 |
| `context.request.get(file_url)` | CF per URL |
| `page.goto(file_url)` from authenticated page | CF per URL |
| `page.evaluate(fetch(...))` | CORS blocks |
| `page.on("response")` interceptor | CF blocks before response |

**The ONLY working approach**: Click the file download link in the
challenge modal UI, letting the browser's native download mechanism
reuse the existing CF clearance:

```python
# 1. Navigate to challenges page, pass CF
page.goto("https://target-ctf.com/challenges")

# 2. Click challenge button to open modal
page.locator('button.challenge-button[value="<challenge_id>"]').click()
time.sleep(2)

# 3. Click file download link — triggers browser-native download
page.on("download", lambda d: d.save_as(f"/tmp/{d.suggested_filename}"))
page.locator('#challenge-window a[href*="/files/"]').click()
```

This works because the browser's native download pipeline (triggered
by a real user click) sends the user's existing cookies and TLS
fingerprint, satisfying Cloudflare.

## Flag Submission via UI (API Blocked by CF)

When CTFd's `/api/v1/challenges/attempt` endpoint is also behind
Cloudflare, `context.request.post()` returns 403 even from an
authenticated browser context. **Use the challenge modal UI instead**:

```python
# Open challenge modal, fill submission input, click submit
page.locator(f'button.challenge-button[value="{cid}"]').click()
page.locator('#challenge-window input[name="submission"]').fill(flag)
page.locator('#challenge-window button:has-text("提交")').click()
# Check result in modal or toast notification
```

If Playwright fails with `ModuleNotFoundError: No module named 'greenlet._greenlet'`, the C extension is missing/broken. Fix:

```bash
/Users/wang/.hermes/hermes-agent/venv/bin/pip install --force-reinstall --no-cache-dir greenlet
```

This is a venv-specific issue (the system pip may install a different arch binary). Always use the venv's own pip, not the system pip.

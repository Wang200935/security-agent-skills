# Cloudflare-Turnstile File Download Workarounds

When a CTF platform is behind Cloudflare Turnstile, **all curl-based and
non-browser HTTP calls will fail** — including `web_extract`, `web_search`'s
backend fetchers, `curl`, `wget`, `python requests`, and `curl_cffi` (even
with `impersonate='chrome124'` and multiple impersonation variants tested
against NHNC 2026). The platform's file-download URLs each require their OWN
Cloudflare clearance — navigating from an authenticated page to a file URL
still hits a fresh CF challenge.

### The One Reliable Pattern

Use **real Google Chrome with CDP** (not Playwright's bundled Chromium):

```python
# Launch real Chrome (not Playwright's Chromium)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9335 \
  --user-data-dir=/tmp/cf_clean_profile \
  "https://target-ctf.com/challenges" &

# Connect via Playwright CDP
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9335")
    context = browser.contexts[0]
    page = context.pages[0]
    
    # Real Chrome auto-passes Cloudflare Turnstile in ~7-15s
    # Wait for it, then use context.request for API/file calls:
    resp = context.request.get("https://target-ctf.com/api/v1/challenges",
        headers={"Authorization": f"Token {CTFD_TOKEN}"})
```

Or with `channel="chrome"` (Playwright launches real Chrome internally):
```python
context = p.chromium.launch_persistent_context(
    user_data_dir="/tmp/cf_profile",
    channel="chrome",  # <-- the key: real Chrome, not Chromium
    headless=True,
)
```

### What Does NOT Work

| Approach | Result |
|----------|--------|
| `curl`/`requests` + cookie | CF challenge page |
| `curl_cffi` with `impersonate='chrome124'` (or any variant) | Still 403 |
| `web_extract` tool | CF challenge page |
| Playwright `context.request.get()` from expired profile | CF challenge page |
| `page.goto(file_url)` — even from authenticated page | Fresh CF per URL |
| `page.evaluate(fetch(...))` | CORS blocks cross-origin |
| `page.on("response")` interceptor + `page.goto()` | CF blocks before response |

### Instancer Patterns

**CTF Instancer (Jimmy01240397/CTF-Instancer)** — many NHNC/Taiwan challenges
use this. Flow: POST `/create` with CTFd token → gets session cookie →
GET `/` shows instance URL and expiry (~5 min). Captcha is a no-op when
`CAPTCHA_SECRET_KEY` is empty (nearly always).

**Whale120 Instancer** (whale-tw.com) — different system. Shows POW stats
(e.g. "pow 395K @ 152,198/s"). Requires solving POW before instance creation.
Also displays "Make sure you already local solved the challenge, then start
an instancer to get flag" — meaning you must solve from source code FIRST
before the instancer gives you the running instance with the real flag.

### User Frustration Signals — STOP Patterns

When solving CTF challenges behind Cloudflare:
- **Do NOT repeatedly ask the user to click the checkbox.** One request is
  fine; repeating it after they've declined/ignored is infuriating.
  ("不要一直讓我重複點擊人類驗證")
- **Do NOT kill the user's Chrome process.** ("不要一直關我的chrome")
  Use a separate profile (`--user-data-dir`) and `channel="chrome"` with
  Playwright persistent context instead.
- If you've spent >10 tool calls fighting Cloudflare, **switch to
  challenges that don't need file downloads** (web services with direct
  URLs, nc challenges, OSINT). Report the CF blocker honestly and move on.

Many NHNC / Taiwan CTF challenges deploy behind the CTF-Instancer system
(github.com/Jimmy01240397/CTF-Instancer). The flow is:

```bash
# 1. POST /create with your CTFd access token to create an instance
curl -sk -X POST "http://<host>:<port>/create" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=ctfd_<64-char-hex>" -c jar.txt

# 2. GET / with the session cookie to see the instance URL
curl -sk -b jar.txt "http://<host>:<port>/"
# Response includes: "Your instance can be accessed here: http://..."
```

The instancer sets a session cookie on POST /create (301 redirect to /),
then shows the actual challenge instance URL and expiry time on GET /.
Instances typically expire after ~5 minutes.

In Playwright:
```python
page.goto("http://host:port/", wait_until='domcontentloaded')
page.fill('input[name="token"]', TOKEN)
page.click('input[type="submit"]')
page.wait_for_load_state('networkidle')
body = page.inner_text('body')
# Extract instance URL with regex: r'https?://\S+:\d+'
```

The instancer's captcha is a no-op when `CAPTCHA_SECRET_KEY` is empty
(which it usually is for CTF deployments). No captcha token needed.

**Pitfall**: Instances expire fast (~5 min). Create the instance, immediately extract
the URL, and connect to it within the same script run. Do not create an
instance and then spend minutes analyzing the instancer page.

**Post-CTF shutdown**: After the CTF event ends, instancers may return 404 (\"404 page not found\") or silently timeout. This does NOT mean the approach is wrong — the infrastructure was simply torn down. When `/create` stops working on a previously-working instancer URL and the CTF end date has passed, **stop trying to create instances** and focus on file-only challenges or challenges with persistent endpoints. Do not burn 10+ tool calls retrying dead instancers.

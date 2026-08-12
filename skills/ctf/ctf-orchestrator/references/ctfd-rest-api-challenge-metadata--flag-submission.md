# CTFd REST API (Challenge Metadata + Flag Submission)

When the user provides a CTFd access token (`ctfd_<64-char-hex>`), the CTFd REST API can list challenges, get challenge details, and submit flags — even without a browser session. This complements the nc/websocket-based challenge interactions already documented above.

**Base URL**: usually `https://<platform-host>` (e.g. `pre-exam.ais3.org`).

**Auth header**: `Authorization: Token ctfd_<token>` with `-L` flag to follow redirects (CTFd API endpoints redirect to login without auth; the header satisfies auth after redirect).

### List all challenges
```bash
curl -sk -L -H "Authorization: Token ctfd_<token>" \
  "https://<host>/api/v1/challenges"
```
Returns JSON array with `id`, `name`, `value`, `category`, `solves`, `solved_by_me`, `tags`.

### Get challenge details
```bash
curl -sk -L -H "Authorization: Token ctfd_<token>" \
  "https://<host>/api/v1/challenges/<id>"
```
Returns description, files list, hints, connection_info.

### Submit a flag
```bash
curl -sk -L -X POST \
  -H "Authorization: Token ctfd_<token>" \
  -H "Content-Type: application/json" \
  -d '{"challenge_id": <id>, "submission": "FLAG{...}"}' \
  "https://<host>/api/v1/challenges/attempt"
```
Returns `{"success": true, "data": {"status": "correct"}}` or `"incorrect"`.

**Token expiration pitfall**: CTFd tokens can expire mid-session. The `/api/v1/challenges` (list) endpoint often keeps working while `/api/v1/challenges/attempt` (submit) returns `401 {"message": "Your access token is invalid"}`. This is NOT a Cloudflare issue — the token itself has expired. To detect: if the list endpoint returns 200 with challenge data but attempt returns 401, the token is expired, not blocked. Get a fresh token from the challenge page (F12 → Network → look for `Authorization: Token ctfd_...` headers in XHR requests).

**Modal UI false positive pitfall**: When submitting flags via Playwright modal UI (because API is CF-blocked), checking `"correct" in modal_text.lower()` can return **false positives for ALL candidates**. If a challenge was previously solved, the modal may show "Already Solved" or "Correct!" text from a cached state. Before declaring victory, verify: (a) the challenge's `solved_by_me` in the API list was `false` before submission, (b) the toast/popup after submission says "correct" (not just the static modal text), (c) re-query `/api/v1/challenges` afterward and check `solved_by_me` changed to `true`.

**Important limitation**: When the CTFd platform is behind Cloudflare Turnstile (NHNC 2026, etc.), the REST API is ALSO behind Cloudflare. `curl`/`requests` with `Authorization: Token` header will receive a CF challenge page (403), not JSON. **The token only works when sent through a browser context that has already passed Cloudflare.** Use Playwright's `context.request.get()` with the `Authorization` header AFTER navigating to the platform and obtaining `cf_clearance` — the browser's TLS fingerprint + cookies satisfy Cloudflare and the API will respond. See `references/cloudflare-turnstile-bypass.md` for the full pattern.

**Cloudflare blocks API POST but UI modal works**: Even with a valid browser session and CF clearance, POST to `/api/v1/challenges/attempt` may still be blocked (403) while GET endpoints work. In this case, submit flags through the **CTFd modal UI** instead: Playwright can click challenge buttons, fill `#challenge-input` (the specific flag text input — NOT generic `#challenge-window input` which matches hidden inputs), and press Enter. See `references/ctfd-cloudflare-ui-flag-submission.md` for the full pattern including false-positive avoidance.

**Modal UI false positive pitfall**: When checking modal text for success, `"correct" in text` matches BOTH "correct" AND "incorrect". Use `re.search(r'(?<!in)correct', text.lower())` or check specific toast elements (`.alert-success` vs `.alert-danger`). Also: if a challenge was previously solved, the modal may show cached "Correct!" text for ANY input — verify by checking `solved_by_me` in the challenge list API before and after submission.

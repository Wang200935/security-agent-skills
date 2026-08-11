# CTF-Instancer Platform Patterns

## Overview

`github.com/Jimmy01240397/CTF-Instancer` is a popular CTF challenge instance manager written in Go (Gin framework). It's used by many Taiwanese CTFs including No Hack No CTF (NHNC), AIS3, and HITCON qualifiers.

## API

Two modes: `web` (session-cookie based) and `api` (token-header based).

### Web mode

```
GET  /            → index page with instancer form or instance info
POST /create      → create instance (form: token=<ctfd_token>)
POST /destroy     → destroy instance
```

### API mode

```
GET  /            → instance status (requires token auth)
GET  /flag        → get flag (requires token auth)
POST /create      → create instance (JSON: {"userid": <id>})
POST /destroy     → destroy instance
```

## Flow

1. POST `/create` with CTFd token → sets session cookie → 301 redirect to `/`
2. GET `/` with session cookie → returns HTML page showing instance access point (URL, nc command, or proxy host)
3. Each instance type uses a different `Mode`: `Forward` (raw port), `Proxy` (subdomain), or `Command` (nc/ssh template)

## Captcha

The captcha is optional — if `CAPTCHA_SECRET_KEY` is empty, the verification function returns `true` immediately. Most deployments skip captcha.

## Implementation Notes

- Session stores the user's CTFd nickname in `session["name"]`
- Instance is created via `instance.Up(name)` and destroyed via `instance.Down(name)`
- Challenge instances typically expire after 5 minutes
- The instancer page auto-refreshes to show expiration countdown

## Flag Retrieval

In API mode, `GET /flag?userid=<id>` returns the flag directly. In web mode, the flag must be obtained by connecting to the challenge instance and exploiting the challenge itself.

## Pitfalls

- Session cookies expire after 30 days by default (`Max-Age: 2592000`)
- Challenge instances expire much faster (typically 3-5 minutes)
- `expect_navigation` / `networkidle` often hangs on instancer pages due to polling — use `domcontentloaded` + `wait_for_timeout` instead
- The instancer is often served on a non-443 port behind a reverse proxy; `page.goto()` may need explicit port in URL

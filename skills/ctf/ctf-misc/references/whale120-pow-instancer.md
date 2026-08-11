# Whale120 CTF Instancer (POW + Local-Solve Pattern)

## Overview

Whale120's custom instancer (`nhnc-whale.whale-tw.com`) requires **two stages** to get a flag:

1. **Local solve**: Download the challenge source (dist.zip), reverse/solve it locally to develop an exploit
2. **Instance + flag**: Start an instance on the platform, connect, and run your exploit to retrieve the real flag

The platform displays: "Make sure you already local solved the challenge, then start an instancer to get flag."

## POW (Proof of Work)

Before an instance can be started, a **hashcash-style POW** must be solved. The UI shows:
```
pow 395K @ 152,198/s
```
This is a JavaScript-based SHA-256 POW running in the browser.

### POW Flow
1. Page loads → starts computing POW in background (Web Worker)
2. POW counter increases until difficulty threshold is met
3. Button changes from "POW 395K" to "START" when POW complete
4. Click START → instance spawns

### Automation
```python
# Wait for POW to complete (UI changes from "POW ..." to "START")
page.wait_for_selector("button.start:not(:disabled)", timeout=120000)
# Then click to start instance
page.click("button.start")
# Wait for instance info to appear
page.wait_for_selector("#instances a[href]", timeout=30000)
```

## Challenge Types on Whale120 Platform

All are web challenges on separate ports:
- **Web:[port]** — direct access via port
- **Review:[port]** — secondary review endpoint (e.g., admin bot view)
- Instance duration: 5 minutes

## Flag Submission

After exploiting the instance and getting the flag:
```
POST https://nhnc.ic3dt3a.org/api/v1/challenges/attempt
Authorization: Token ctfd_<token>
Content-Type: application/json
{"challenge_id": <id>, "submission": "NHNC{...}"}
```

## Pitfalls
- The POW can take 30-120 seconds to complete
- Instances expire in 5 minutes; have your exploit ready before starting
- The dist.zip files are behind Cloudflare; download them through an authenticated browser session, not curl
- All three challenges (Talking to the Sun, WhCMS, XDD) share the same instancer page

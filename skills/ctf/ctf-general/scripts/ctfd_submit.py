#!/usr/bin/env python3
"""
Submit a CTFd challenge flag via Playwright UI (bypasses the 403 from
the REST /api/v1/challenges/attempt endpoint that regular user sessions hit).

Usage:
    python3 ctfd_submit.py \\
        --base http://target:8000 \\
        --state /tmp/ctf_session/state.json \\
        --challenge "04. Weak Password Bruteforce" \\
        --flag "flag{...}"

Requires:
    playwright install chromium
    state.json from a prior `ctx.storage_state(path=...)` after logging in.
"""
import argparse, json, sys, time
from playwright.sync_api import sync_playwright


def submit(base: str, state_path: str, challenge_text: str, flag: str) -> dict:
    state = json.load(open(state_path))
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(state["cookies"])
        page = ctx.new_page()

        attempt_responses = []

        def on_resp(resp):
            if "/api/v1/challenges/attempt" in resp.url:
                attempt_responses.append((resp.status, resp.text()))

        page.on("response", on_resp)

        page.goto(f"{base}/challenges", wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)

        # Click challenge card by visible text
        sel = f'button.challenge-button:has-text("{challenge_text}")'
        page.locator(sel).first.scroll_into_view_if_needed()
        page.locator(sel).first.click()
        page.wait_for_timeout(2000)  # Alpine.js render time

        # Fill submission input
        page.fill('input[name="submission"]', flag)

        # Click submit button (try several selectors)
        for bs in [
            'button:has-text("Submit")',
            'input[type="submit"]:visible',
            '.btn-success:has-text("Submit")',
            '#submit-flag',
        ]:
            if page.locator(bs).count() > 0:
                page.click(bs)
                break
        else:
            # Fallback: press Enter
            page.press('input[name="submission"]', "Enter")
        page.wait_for_timeout(2500)

        # Verify via API
        solved = page.evaluate(
            """async () => {
                const r = await fetch('/api/v1/challenges', {credentials:'include'});
                const d = await r.json();
                return d.data.filter(c => c.solved_by_me)
                             .map(c => ({id: c.id, name: c.name}));
            }"""
        )

        browser.close()
        return {
            "attempt_responses": attempt_responses,
            "solved_count": len(solved),
            "solved": solved,
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="CTFd base URL, e.g. http://target:8000")
    ap.add_argument("--state", required=True, help="path to storage_state.json from Playwright login")
    ap.add_argument("--challenge", required=True, help="challenge card text, e.g. '04. Weak Password Bruteforce'")
    ap.add_argument("--flag", required=True, help="the flag string, e.g. flag{...}")
    args = ap.parse_args()

    result = submit(args.base, args.state, args.challenge, args.flag)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["attempt_responses"]:
        print("WARNING: no /api/v1/challenges/attempt responses captured", file=sys.stderr)
        sys.exit(1)
    last = result["attempt_responses"][-1]
    if '"correct"' not in last[1] and '"already_solved"' not in last[1]:
        print(f"WARNING: last attempt was {last[0]} and not correct: {last[1]}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

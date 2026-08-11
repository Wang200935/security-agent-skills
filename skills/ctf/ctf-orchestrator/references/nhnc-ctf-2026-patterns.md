# NHNC CTF 2026 Platform Patterns

## Platform

- URL: `https://nhnc.ic3dt3a.org`
- Type: CTFd behind Cloudflare Turnstile
- Flag format: `NHNC{...}`
- Account tested: 梅 / willis6664
- Chrome profile: `/tmp/nhnc_ui_submit/`

## Challenge Categories (Author-Based)

NHNC uses **author usernames as CTFd categories**, not standard categories:

| Author | Challenges | Notes |
|--------|-----------|-------|
| fishbaby1011 | Final Boarding (#26), LemonShelf (#28) | OSINT/forensics |
| UmmIt Kin | Kira-Notes (#27) | OSINT/forensics, AI-resistant |
| whale120 | Talking to the Sun (#14), WhCMS (#15), XDD (#16), TEARoam (#24), WhC2 (#31), Guessy CTF (#13) | 450-500pts, source at `github.com/William957-web/My-CTF-Challenges` |
| hsuan0223x | newbie-crypto (#4), Confused Component (#11) | Crypto + Web |
| Auron | 67 login system (#9) | Pwn, Arch Linux glibc 2.38 |
| LemonTea | Login_page (#7), Tea-agent (#1) | Web |
| 夜有夢 | Who is Whois？(#30) | OSINT |
| viivie | cucumber farm (#17) | - |
| legendyang | watch tv (#10) | - |
| solarfish | #include (#21) | - |

## Full Challenge Catalog (16 total, 3 solved)

| ID | Name | Author | Value | Solved |
|----|------|--------|-------|--------|
| 3 | Welcome | - | 10pts | ✅ |
| 4 | newbie-crypto | hsuan0223x | 100pts | ✅ |
| 26 | Final Boarding | fishbaby1011 | 100pts | ✅ |
| 27 | Kira-Notes | UmmIt Kin | 343pts | ⬜ |
| 28 | LemonShelf | fishbaby1011 | 397pts | ⬜ |
| 14 | Talking to the Sun | whale120 | 450pts | ⬜ |
| 11 | Confused Component | hsuan0223x | 455pts | ⬜ |
| 9 | 67 login system | Auron | 458pts | ⬜ |
| 30 | Who is Whois？ | 夜有夢 | 481pts | ⬜ |
| 7 | Login_page | LemonTea | 495pts | ⬜ |
| 21 | #include | solarfish | 497pts | ⬜ |
| 1 | Tea-agent | LemonTea | 498pts | ⬜ |
| 10 | watch tv | legendyang | 500pts | ⬜ |
| 13 | Guessy CTF | whale120 | 500pts | ⬜ |
| 15 | WhCMS v0.1 | whale120 | 500pts | ⬜ |
| 24 | TEARoam | whale120 | 500pts | ⬜ |

## Flag Submission (Cloudflare-Blocked API)

Cloudflare blocks POST to `/api/v1/challenges/attempt`. Modal UI submission works instead. See `ctfd-cloudflare-ui-flag-submission.md`.

## Per-Challenge Analysis Notes

### Final Boarding (#26) — ✅ SOLVED
- EXIF: DateTimeOriginal=2026-05-05 14:49 JST, GPSImgDirection=134° (SE)
- Camera: Pixel 8
- Airport clues: NRT, HND, CTS, ITM (in binary string table)
- Flight: NRT→TPE ~14:30 JST (EVA Air BR197 / China Airlines CI101)
- Flag format: `NHNC{YYYYMMDD_FLIGHT}`

### Kira-Notes (#27) — ⬜ UNSOLVED
- File-only: `places.sqlite` (Firefox history)
- Firefox history with manipulated timestamps (year 1657), visit_type=9 (custom)
- Proton Drive: `drive.proton.me/urls/00MNVW0SHG#do4wWWpAQ0Lw`
- Retro Archive: `151.158.224.74:31337` (static Astro, all /dl/ 404)
- GitHub: `UmmItKin/Kira-Notes` (45 commits, no flag in source)
- Email clue: `kira-notes.countdown368@slmails.com`, PGP: `0xDEADBEEF1337`
- Flag candidates FAILED: `do4wWWpAQ0Lw`, `nothing`, `UmmIt_Kin`, `UmmItKin`, `K1r4_N0t3s_1337`, `countdown368`, `deadbeef`, `nothing_1337`, `kira_notes`, `osint-framework`, `forensics`, `misc`, `nothing_here`, `kira_notes_countdown368`, `osint-framework_kira`
- Description says: "Please don't use AI to solve this question"
- 70 solves → solvable by humans

### Confused Component (#11) — ⬜
- Web: path confusion between "previewer" and "loader"
- Instancer: `chal3.teagod.tech:9000` (CTF-Instancer, needs fresh token)
- `?name=auth` parameter accepted
- All paths except `/` return 404 without instance

### 67 login system (#9) — ⬜
- ELF x86-64, PIE, stripped, glibc 2.38, stack canary
- Menu: register/show/login/update/delete/exit (6 options + hidden option 0)
- `scanf("%d")` input, non-numeric → exit(1)
- 4 user slots, login reads 6-byte password
- `/flag.txt` NOT in binary strings
- Cannot run on ARM64 Mac (Docker permission denied for glibc 2.38 binary)
- Capstone disassembly completed: jump table at 0x209c, main at 0x1641

### WhCMS v0.1 (#15) — ⬜
- whale120 challenge, 500pts
- File: dist.zip (91MB, Go binary + readflag.c + docker-compose)
- whale120 repo: `William957-web/My-CTF-Challenges` (NHNC 2025 only, 2026 not yet)
- whale120 instancer at whale-tw.com (PoW required + local-solve-first)

# Security Agent Skills — Project Instructions

## Skill Loading

This project contains 79 security skills organized into 9 domains under `skills/`.

### Load Order
1. Always load `skills/security-orchestrator/SKILL.md` first — it routes to specialized skills
2. The orchestrator analyzes user intent and loads the right skill(s)
3. Multiple skills can load in parallel for speed

### Skill Categories
- `skills/recon/` — OSINT, reconnaissance, dark web research
- `skills/web-pentest/` — Web app testing, API security, WAF bypass
- `skills/network-pentest/` — Network scanning, AD attacks, lateral movement
- `skills/exploit-dev/` — Zero-day hunting, fuzzing, kernel exploitation, crypto
- `skills/reverse-engineering/` — Binary analysis, firmware, Ghidra/IDA/radare2
- `skills/ctf/` — CTF challenges across all categories
- `skills/post-exploitation/` — Privilege escalation, persistence, reporting
- `skills/cloud-security/` — AI/MCP security, code audit, modern attack surfaces
- `skills/hardware-iot/` — UART/JTAG/SPI, firmware, SDR, Flipper Zero, ESP32

### Rules Library
Shared knowledge in `rules/` is loaded across skills:
- `payloads.md` — Attack payloads (XSS, SSRF, SQLi, etc.)
- `techniques.md` — Proven attack techniques
- `waf-bypass-protocol.md` — WAF bypass ladder
- `hunting.md` — Hunting rules with harm checks
- `mistakes.md` — Common mistakes to avoid

## Authorized Use Only
These skills are for authorized security testing only. The user is responsible for obtaining proper authorization before testing any system.

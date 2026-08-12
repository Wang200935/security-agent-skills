# Security Agent Skills — Project Instructions

## Skill Loading

This project contains 79 security skills organized into 9 domains under `skills/`.

### Load Order
1. Load `skills/security-orchestrator/SKILL.md` only for cross-domain routing
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
Shared knowledge in `rules/security-rules.md` is loaded across skills for attack payloads, techniques, WAF bypass patterns, hunting rules, and common mistakes.

## Authorized Use Only
These skills are for authorized security testing only. The user is responsible for obtaining proper authorization before testing any system.

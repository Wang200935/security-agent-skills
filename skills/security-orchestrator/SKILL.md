---
name: security-orchestrator
description: "Master router for all security operations — 79 skills across 9 domains: recon/OSINT, web pentest, network pentest, exploit development, reverse engineering, CTF, post-exploitation, cloud security, and hardware/IoT hacking. Load this first for any security task to get intelligent routing to the right specialized skill."
version: 2.0.0
category: security
tags: [security, pentest, red-team, ctf, osint, exploit, reverse-engineering, zero-day, hardware, cloud-security]
---

# Security Orchestrator — Master Router v2.0

## When to Load

Load this skill when the user asks about ANY security-related task. It routes to the right specialized skill based on intent analysis.

## Skill Inventory (79 skills across 9 domains)

### 1. Recon & OSINT (12 skills)

| Skill | Purpose |
|:------|:--------|
| `osint` | Complete OSINT framework — SOCMINT, DNS/domain recon, email/phone intelligence, geolocation, dark web |
| `aliens-eye` | AI-OSINT username scanner — 840+ platforms with ML-based matching |
| `email-osint` | Email-first OSINT — 7-track parallel workflow |
| `spiderfoot-osint` | SpiderFoot 4.0 OSINT automation |
| `parallel-intel` | Parallel intelligence gathering — web_search + web_extract batch |
| `vulnclaw-osint-recon` | OSINT collection — four-dimension model (server→website→domain→people) |
| `vulnclaw-recon` | Passive + active reconnaissance flow |
| `darkweb-research-env` | Dark web research environment via Tor SOCKS5 |
| `vulnclaw-vuln-discovery` | Vulnerability scanning flow |
| `chatgpt-web-relay` | Relay prompts to ChatGPT web UI for research |
| `local-network-recon` | Local network device discovery and identification |
| `network-device-recon` | Network device port scanning and service identification |

### 2. Web Pentest (14 skills)

| Skill | Purpose |
|:------|:--------|
| `web-app-pentest` | Full OWASP 2025 web app pentesting — SQLi, XSS, SSRF, SSTI, etc. |
| `api-security-testing` | API security — REST, GraphQL, WebSocket, gRPC |
| `client-side-auth-bypass` | Reverse and bypass client-side JS authentication |
| `vulnclaw-web-pentest` | Web pentest full flow — stack fingerprinting, dir enum, auth testing |
| `vulnclaw-web-security-advanced` | Advanced web security — injection families, protocol, auth, file, modern attack surfaces |
| `vulnclaw-waf-bypass` | WAF bypass techniques library |
| `vulnclaw-ctf-web` | CTF web attack knowledge — PHP weak comparison, command injection, SSTI, deserialization |
| `ctf-pwn-web-methodology` | CTF pwn/web solving methodology |
| `full-stack-vulnerability-research` | Framework vulnerability research — frontend/backend frameworks, DB engines, GraphQL, API Gateway |
| `sql-server-exploitation` | SQL injection on MSSQL — xp_cmdshell, information_schema, lateral |
| `vulnclaw-client-reverse` | Client-side reverse engineering — signature recovery, encrypted restoration, request chain tracing |
| `vulnclaw-android-pentest` | Android app pentest — APK analysis, hook, automated testing, runtime driver, signature recovery |
| `playwright-browser` | Playwright browser automation for security testing and OSINT |
| `devops/playwright-cli` | Playwright CLI workflow for browser automation |

### 3. Network Pentest (6 skills)

| Skill | Purpose |
|:------|:--------|
| `network-pentest` | Port scanning, service enumeration, network exploitation |
| `pentest` | Advanced pentest — AD attacks, cloud pentesting, container escape, privilege escalation, C2, EDR evasion |
| `pentest-tool-installation` | Install/troubleshoot pentesting tools |
| `vulnclaw-pentest-flow` | Full pentest flow orchestration — recon to report generation |
| `vulnclaw-pentest-tools` | Pentest tool reference — encoding/decoding, reverse shells, credentials, privilege, tunnels |
| `vulnclaw-rapid-checklist` | Quick pentest checklist + payload families |

### 4. Exploit Development (10 skills)

| Skill | Purpose |
|:------|:--------|
| `exploit-development` | Vulnerability to working exploit — ROP, heap, format strings, shellcode |
| `zero-day-hunting` | Zero-day methodology — AFL++, libFuzzer, syzkaller, crash triage, CVE submission |
| `kernel-exploitation` | Linux kernel exploitation — SLUB/SLAB, use-after-free, race conditions, SMEP/SMAP bypass |
| `vulnclaw-exploitation` | PoC construction and exploitation of discovered vulnerabilities |
| `vulnclaw-crypto-toolkit` | Encode/decode + crypto toolkit — base64/URL/Hex, MD5/SHA, AES/DES, RSA |
| `vulnclaw-ctf-crypto` | CTF crypto attacks — RSA (small exp, common modulus, Wiener, Coppersmith), AES padding, ECC |
| `cryptography` | Deep cryptography knowledge base |
| `ctf-cryptography` | CTF crypto challenge solving |
| `ctf-encoding-realignment` | Custom alphabet/unusual encoding realignment |
| `ctf-pwn-binary-exploitation` | Binary exploitation — stack/heap overflow, ROP, format string |

### 5. Reverse Engineering (3 skills)

| Skill | Purpose |
|:------|:--------|
| `reverse-engineering` | Complete RE — Ghidra, IDA, radare2, angr, firmware extraction, binary analysis |
| `ctf-reverse-engineering` | CTF reverse engineering challenges — binaries, obfuscation, anti-debug |
| `ctf-forensics` | CTF forensics — file type identification, steganography, memory/disk forensics |

### 6. CTF (12 skills)

| Skill | Purpose |
|:------|:--------|
| `ctf-playbook` | CTF playbook — web, crypto, pwn, reverse, forensics, misc |
| `ctf-general` | Orchestrate CTF challenge solving across all categories |
| `ctf-misc` | CTF misc — Python/Bash jail escapes, encoding chains, QR/audio/image steganography |
| `ctf-technique-atlas` | Deep technique atlas — map challenge clues to techniques |
| `ctf-training-loop` | Systematic CTF training workflow |
| `ctf-web-exploitation` | CTF web exploitation — HTTP behavior triage, injection, auth bypass |
| `ctf-writeup-artifact-discipline` | CTF write-ups with authentic evidence, screenshots |
| `natural-ctf-writeup-screenshots` | Natural-looking CTF screenshots |
| `ctf-kernel-exploitation` | CTF kernel pwn — syscalls, drivers, ioctl, kernel ROP |
| `vulnclaw-ctf-misc` | CTF misc knowledge — jail escapes, encoding, steganography |

### 7. Post-Exploitation (6 skills)

| Skill | Purpose |
|:------|:--------|
| `vulnclaw-post-exploitation` | Post-exploitation — internal info gathering, lateral movement |
| `vulnclaw-intranet-pentest-advanced` | Intranet pentest advanced — lateral movement, credential theft, persistence, tunnels, AD, ADCS, Exchange/SharePoint |
| `overclock-combat-pentest` | Overclock combat mode — 10-year deep pentest knowledge, cloud-native escape, framework exploitation, protocol malformation |
| `professional-pentest-mastery` | Full pentest system — recon to zero-day hunting, PayloadsAllTheThings + HackTricks integrated |
| `strix-pentest` | Open-source AI multi-agent pentesting tool |
| `vulnclaw-reporting` | Structured pentest report + PoC generation |

### 8. Cloud & AI Security (7 skills)

| Skill | Purpose |
|:------|:--------|
| `vulnclaw-ai-mcp-security` | AI & MCP security — prompt injection, tool abuse, MCP trust boundaries, agent privilege escalation |
| `ai-mcp-security` | AI/MCP security assessment — prompt injection, data leakage, model risk |
| `modern-attack-surfaces` | Modern attack surfaces — LLM jailbreaking, MCP abuse, agent trust, supply chain |
| `security-and-hardening` | Hardens code against vulnerabilities — input validation, auth, crypto, secrets |
| `claude-code-security-review` | Security-focused code review for Claude Code |
| `security-audit` | Security audit of codebases — web apps, APIs, services |
| `hackingtool` | 21-category, 173-tool offensive security toolkit |

### 9. Hardware & IoT (12 skills)

| Skill | Purpose |
|:------|:--------|
| `hardware-iot-hacking` | Hardware & IoT hacking — UART/JTAG/SPI/I2C, firmware, SDR/RFID/NFC/BLE/Zigbee |
| `bt-classic-segmented-sweep` | Bluetooth Classic (BR/EDR) segmented sweep technique |
| `esp32-wifi-killer-v12` | ESP32 targeted WiFi deauth + nRF24 2.4GHz jammer v12 |
| `nrf24-bitbang-driver` | Bit-bang SPI driver for nRF24L01+ on ESP32 |
| `rfclown-multi-protocol-jammer` | OLED-menu multi-protocol 2.4GHz jammer based on RF-Clown |
| `esp32-dualband-wifi-jammer` | ESP32 dual-band (2.4GHz + 5GHz) WiFi jammer |
| `esp32-serial-diagnostics` | ESP32 serial diagnostics in non-TTY environments |
| `flipper-zero-back` | Complete 3-layer backup of Flipper Zero |
| `flipper-zero-firmware-modification` | Flash/replace/reflash Flipper Zero firmware |
| `rf-clown-master` | RF-Clown v2 complete port — 3×nRF24 source analysis, firmware porting |
| `smart-card-reader-driver-debugging` | Debug/configure smart card readers for synchronous memory cards |
| `smart-card-usb-direct` | Bypass PC/SC/CCID middleware, communicate directly with smart card reader |

## Routing Logic

```
User intent → route to skill:

"scan this target" / "find vulnerabilities" → recon + web-app-pentest
"exploit this bug" / "write PoC" → exploit-development
"reverse this binary" / "decompile" → reverse-engineering
"CTF challenge" / "capture the flag" → ctf (ctf-general routes further)
"enumerate network" / "port scan" → network-pentest
"OSINT on person/domain" / "find information" → recon (osint)
"bypass WAF" → web-pentest (vulnclaw-waf-bypass)
"privilege escalation" / "lateral movement" → post-exploitation
"audit this code" / "security review" → cloud-security (security-audit)
"hack IoT device" / "firmware reverse" → hardware-iot
"AI security" / "MCP vulnerability" → cloud-security (ai-mcp-security)
"fuzz this target" / "find crashes" → exploit-dev (zero-day-hunting)
"crack this hash" / "break encryption" → exploit-dev (cryptography)
"pentest report" → post-exploitation (vulnclaw-reporting)
"jailbreak" / "escape sandbox" → ctf (ctf-misc)
```

## Parallel Execution

For maximum speed, load multiple skills in parallel:
- **Full pentest**: recon + web-app-pentest + network-pentest + post-exploitation
- **Bug bounty**: recon + web-app-pentest + exploit-dev + vulnclaw-waf-bypass
- **CTF solve**: ctf-general → (routes to ctf-web/ctf-crypto/ctf-misc/ctf-reverse as needed)
- **Internal pentest**: network-pentest + post-exploitation + vulnclaw-intranet-pentest-advanced
- **Hardware assessment**: hardware-iot-hacking + reverse-engineering

## Installation

```bash
# Clone and install for your agent
git clone https://github.com/wang/security-agent-skills.git
cd security-agent-skills
./install.sh --agent claude-code  # or codex, cursor, gemini, hermes, openclaw, copilot, windsurf

# Install for all detected agents
./install.sh --all

# List available skills
./install.sh --list
```

## Philosophy

These skills were built from real security engagements — not theoretical exercises. They contain battle-tested methodologies, complete payload libraries, and working exploit patterns. The knowledge base integrates 479+ GitHub repositories, 214+ markdown reference files, and extensive field experience.

Every skill follows the same structure:
```
skill-name/
├── SKILL.md          # Instructions and metadata
├── references/       # Deep knowledge files (payloads, methodologies, tool references)
├── scripts/          # Helper scripts (automation, setup, testing)
└── templates/         # Report templates, config templates
```

## Companion Rules

Load `rules/` files for shared knowledge that applies across skills:
- `payloads.md` — 2600+ lines of XSS/SSRF/SQLi/IDOR/OAuth/SSTI/deser payloads
- `techniques.md` — Proven attack techniques from real engagements
- `waf-bypass-protocol.md` — WAF bypass iteration ladder
- `hunting.md` — 31 hunting rules with harm checks and mutation matrices
- `mistakes.md` — Top 10 most common mistakes to avoid

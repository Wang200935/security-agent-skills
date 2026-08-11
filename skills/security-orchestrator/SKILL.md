---
name: security-orchestrator
description: "Master router for all security operations — 79 skills across 9 domains: recon/OSINT, web pentest, network pentest, exploit development, reverse engineering, CTF, post-exploitation, cloud security, and hardware/IoT hacking. Load this first for any security task to get intelligent routing to the right specialized skill."
version: 2.0.0
category: security
tags: [security, advanced-pentest, red-team, ctf, osint-framework, exploit, reverse-engineering, zero-day, hardware, cloud-security]
---

# Security Orchestrator — Master Router v2.0

## When to Load

Load this skill when the user asks about ANY security-related task. It routes to the right specialized skill based on intent analysis.

## Skill Inventory (79 skills across 9 domains)

### 1. Recon & OSINT (12 skills)

| Skill | Purpose |
|:------|:--------|
| `osint-framework` | Complete OSINT framework — SOCMINT, DNS/domain recon, email/phone intelligence, geolocation, dark web |
| `username-scanner` | AI-OSINT username scanner — 840+ platforms with ML-based matching |
| `email-osint-investigation` | Email-first OSINT — 7-track parallel workflow |
| `spiderfoot-automation` | SpiderFoot 4.0 OSINT automation |
| `parallel-intel-gathering` | Parallel intelligence gathering — web_search + web_extract batch |
| `osint-recon-model` | OSINT collection — four-dimension model (server→website→domain→people) |
| `reconnaissance-ops` | Passive + active reconnaissance flow |
| `darkweb-research` | Dark web research environment via Tor SOCKS5 |
| `vulnerability-discovery` | Vulnerability scanning flow |
| `chatgpt-web-relay` | Relay prompts to ChatGPT web UI for research |
| `local-network-recon` | Local network device discovery and identification |
| `network-device-recon` | Network device port scanning and service identification |

### 2. Web Pentest (14 skills)

| Skill | Purpose |
|:------|:--------|
| `web-app-pentest` | Full OWASP 2025 web app penetration testing — SQLi, XSS, SSRF, SSTI, etc. |
| `api-security-testing` | API security — REST, GraphQL, WebSocket, gRPC |
| `client-auth-bypass` | Reverse and bypass client-side JS authentication |
| `web-app-assessment` | Web advanced-pentest full flow — stack fingerprinting, dir enum, auth testing |
| `web-security-advanced` | Advanced web security — injection families, protocol, auth, file, modern attack surfaces |
| `waf-bypass-techniques` | WAF bypass techniques library |
| `ctf-web-attacks` | CTF web attack knowledge — PHP weak comparison, command injection, SSTI, deserialization |
| `ctf-web-pwn-methodology` | CTF pwn/web solving methodology |
| `framework-vulnerability-research` | Framework vulnerability research — frontend/backend frameworks, DB engines, GraphQL, API Gateway |
| `sql-server-exploitation` | SQL injection on MSSQL — xp_cmdshell, information_schema, lateral |
| `client-reverse-engineering` | Client-side reverse engineering — signature recovery, encrypted restoration, request chain tracing |
| `android-pentest` | Android app pentest — APK analysis, hook, automated testing, runtime driver, signature recovery |
| `browser-automation-security` | Playwright browser automation for security testing and OSINT |
| `devops/playwright-cli` | Playwright CLI workflow for browser automation |

### 3. Network Pentest (6 skills)

| Skill | Purpose |
|:------|:--------|
| `network-pentest` | Port scanning, service enumeration, network exploitation |
| `advanced-pentest` | Advanced advanced-pentest — AD attacks, cloud penetration testing, container escape, privilege escalation, C2, EDR evasion |
| `pentest-tool-setup` | Install/troubleshoot penetration testing tools |
| `pentest-workflow` | Full advanced-pentest flow orchestration — recon to report generation |
| `pentest-tool-reference` | Pentest tool reference — encoding/decoding, reverse shells, credentials, privilege, tunnels |
| `pentest-quick-checklist` | Quick advanced-pentest checklist + payload families |

### 4. Exploit Development (10 skills)

| Skill | Purpose |
|:------|:--------|
| `exploit-development` | Vulnerability to working exploit — ROP, heap, format strings, shellcode |
| `zero-day-hunting` | Zero-day methodology — AFL++, libFuzzer, syzkaller, crash triage, CVE submission |
| `kernel-exploitation` | Linux kernel exploitation — SLUB/SLAB, use-after-free, race conditions, SMEP/SMAP bypass |
| `exploit-poc-builder` | PoC construction and exploitation of discovered vulnerabilities |
| `crypto-toolkit` | Encode/decode + crypto toolkit — base64/URL/Hex, MD5/SHA, AES/DES, RSA |
| `crypto-ctf-attacks` | CTF crypto attacks — RSA (small exp, common modulus, Wiener, Coppersmith), AES padding, ECC |
| `cryptography-fundamentals` | Deep cryptography-fundamentals knowledge base |
| `crypto-attack-patterns` | CTF crypto challenge solving |
| `encoding-realignment` | Custom alphabet/unusual encoding realignment |
| `binary-exploitation` | Binary exploitation — stack/heap overflow, ROP, format string |

### 5. Reverse Engineering (3 skills)

| Skill | Purpose |
|:------|:--------|
| `reverse-engineering` | Complete RE — Ghidra, IDA, radare2, angr, firmware extraction, binary analysis |
| `ctf-reverse-engineering` | CTF reverse engineering challenges — binaries, obfuscation, anti-debug |
| `digital-forensics` | CTF forensics — file type identification, steganography, memory/disk forensics |

### 6. CTF (12 skills)

| Skill | Purpose |
|:------|:--------|
| `ctf-playbook` | CTF playbook — web, crypto, pwn, reverse, forensics, misc |
| `ctf-orchestrator` | Orchestrate CTF challenge solving across all categories |
| `ctf-misc-toolkit` | CTF misc — Python/Bash jail escapes, encoding chains, QR/audio/image steganography |
| `ctf-technique-atlas` | Deep technique atlas — map challenge clues to techniques |
| `ctf-training-loop` | Systematic CTF training workflow |
| `ctf-web-exploitation` | CTF web exploitation — HTTP behavior triage, injection, auth bypass |
| `ctf-writeup-discipline` | CTF write-ups with authentic evidence, screenshots |
| `ctf-writeup-screenshots` | Natural-looking CTF screenshots |
| `ctf-kernel-exploitation` | CTF kernel pwn — syscalls, drivers, ioctl, kernel ROP |
| `ctf-jail-escape` | CTF misc knowledge — jail escapes, encoding, steganography |

### 7. Post-Exploitation (6 skills)

| Skill | Purpose |
|:------|:--------|
| `post-exploitation-ops` | Post-exploitation — internal info gathering, lateral movement |
| `intranet-pentest-advanced` | Intranet pentest — lateral movement, credential theft, persistence, tunnels, AD, ADCS, Exchange/SharePoint |
| `advanced-attack-chains` | Overclock combat mode — 10-year deep advanced-pentest knowledge, cloud-native escape, framework exploitation, protocol malformation |
| `professional-pentest-guide` | Full advanced-pentest system — recon to zero-day hunting, PayloadsAllTheThings + HackTricks integrated |
| `autonomous-pentest-scanner` | Open-source AI multi-agent penetration testing tool |
| `pentest-report-generator` | Structured advanced-pentest report + PoC generation |

### 8. Cloud & AI Security (7 skills)

| Skill | Purpose |
|:------|:--------|
| `ai-ml-security-assessment` | AI & MCP security — prompt injection, tool abuse, MCP trust boundaries, agent privilege escalation |
| `ai-mcp-security` | AI/MCP security assessment — prompt injection, data leakage, model risk |
| `modern-attack-surfaces` | Modern attack surfaces — LLM jailbreaking, MCP abuse, agent trust, supply chain |
| `security-and-hardening` | Hardens code against vulnerabilities — input validation, auth, crypto, secrets |
| `security-code-review` | Security-focused code review for Claude Code |
| `security-audit` | Security audit of codebases — web apps, APIs, services |
| `offensive-toolkit` | 21-category, 173-tool offensive security toolkit |

### 9. Hardware & IoT (12 skills)

| Skill | Purpose |
|:------|:--------|
| `hardware-iot-hacking` | Hardware & IoT hacking — UART/JTAG/SPI/I2C, firmware, SDR/RFID/NFC/BLE/Zigbee |
| `bluetooth-jammer-sweep` | Bluetooth Classic (BR/EDR) segmented sweep technique |
| `wifi-deauth-jammer` | ESP32 targeted WiFi deauth + nRF24 2.4GHz jammer v12 |
| `nrf24-bitbang-spi` | Bit-bang SPI driver for nRF24L01+ on ESP32 |
| `rf-multi-protocol-jammer` | OLED-menu multi-protocol 2.4GHz jammer based on RF-Clown |
| `wifi-dualband-jammer` | ESP32 dual-band (2.4GHz + 5GHz) WiFi jammer |
| `esp32-serial-diag` | ESP32 serial diagnostics in non-TTY environments |
| `flipper-zero-backup` | Complete 3-layer backup of Flipper Zero |
| `flipper-zero-firmware` | Flash/replace/reflash Flipper Zero firmware |
| `rf-jammer-firmware-port` | RF-Clown v2 complete port — 3×nRF24 source analysis, firmware porting |
| `smart-card-driver-debug` | Debug/configure smart card readers for synchronous memory cards |
| `smart-card-usb-direct` | Bypass PC/SC/CCID middleware, communicate directly with smart card reader |

## Routing Logic

```
User intent → route to skill:

"scan this target" / "find vulnerabilities" → recon + web-app-pentest
"exploit this bug" / "write PoC" → exploit-development
"reverse this binary" / "decompile" → reverse-engineering
"CTF challenge" / "capture the flag" → ctf (ctf-orchestrator routes further)
"enumerate network" / "port scan" → network-pentest
"OSINT on person/domain" / "find information" → recon (osint-framework)
"bypass WAF" → web-advanced-pentest (waf-bypass-techniques)
"privilege escalation" / "lateral movement" → post-exploitation
"audit this code" / "security review" → cloud-security (security-audit)
"hack IoT device" / "firmware reverse" → hardware-iot
"AI security" / "MCP vulnerability" → cloud-security (ai-mcp-security)
"fuzz this target" / "find crashes" → exploit-dev (zero-day-hunting)
"crack this hash" / "break encryption" → exploit-dev (cryptography-fundamentals)
"advanced-pentest report" → post-exploitation (pentest-report-generator)
"jailbreak" / "escape sandbox" → ctf (ctf-misc-toolkit)
```

## Parallel Execution

For maximum speed, load multiple skills in parallel:
- **Full advanced-pentest**: recon + web-app-pentest + network-pentest + post-exploitation
- **Bug bounty**: recon + web-app-pentest + exploit-dev + waf-bypass-techniques
- **CTF solve**: ctf-orchestrator → (routes to ctf-web/ctf-crypto/ctf-misc-toolkit/ctf-reverse as needed)
- **Internal advanced-pentest**: network-pentest + post-exploitation + intranet-pentest-advanced
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

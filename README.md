<p align="center">
  <img src="security-agent-skills.png" alt="security-agent-skills" width="100%">
</p>

<h1 align="center">security-agent-skills</h1>

<h3 align="center">Cybersecurity Skills Router · 資安技能路由包</h3>

<p align="center"><em>79 skills · 9 domains · 8 agent platforms — installable as Agent Skills</em></p>

<p align="center">
  <a href="https://github.com/Wang200935/security-agent-skills/releases"><img src="https://img.shields.io/badge/release-v2.0.0-blue" alt="release"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/stargazers"><img src="https://img.shields.io/github/stars/Wang200935/security-agent-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/forks"><img src="https://img.shields.io/github/forks/Wang200935/security-agent-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/Wang200935/security-agent-skills/issues"><img src="https://img.shields.io/github/issues/Wang200935/security-agent-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-orange" alt="contributing"></a>
</p>

<p align="center">
  <a href="#about">About</a> ·
  <a href="#getting-started">Getting Started</a> ·
  <a href="#skill-categories">Categories</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#compatibility">Compatibility</a> ·
  <a href="#contributing">Contributing</a>
</p>

<p align="center">
  🌐
  <a href="README_zh.md">繁體中文</a> ·
  <a href="README_zh_CN.md">简体中文</a> ·
  <a href="README_ja.md">日本語</a>
</p>

---

## About

When an AI agent (Claude Code, Codex, Cursor, Gemini CLI, Windsurf, GitHub Copilot, OpenClaw, or Hermes Agent) encounters a security task — an APK to reverse, a web app to advanced-pentest, a CTF challenge to solve, or a binary to analyze — this pack routes it to the right methodology, payloads, and commands instead of guessing.

```
User task → security-orchestrator (master router · intent analysis)
         → specialized skill activated (methodology + payloads + commands)
         → execution + evidence collection
         → reporting
```

**Why this exists:**

- AI agents don't know whether to use nmap, sqlmap, Burp Suite, or Ghidra for a given task
- Web, network, binary, CTF, and hardware tasks each need different playbooks
- The same mistakes get repeated because experience isn't reused
- Payloads, tool references, and methodologies are scattered across bookmarks and notes

Primary router: [`skills/security-orchestrator/SKILL.md`](skills/security-orchestrator/SKILL.md)

### Current Status

| Metric | Value |
|:-------|------:|
| Total skills | 79 |
| Domains | 9 |
| Master router | 1 (security-orchestrator) |
| Supported agents | 8 |
| Reference files | 214+ |
| Integrated repos | 479+ |
| Skill format | SKILL.md (Agent Skills open standard) |

---

## Getting Started

### Prerequisites

- A supported AI coding agent (Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Copilot, OpenClaw, or Hermes)
- `bash` for the install script
- Some skills reference tools like nmap, sqlmap, Ghidra, IDA, Frida, etc.

### Installation

```bash
git clone https://github.com/Wang200935/security-agent-skills.git
cd security-agent-skills

# Install for your agent
./install.sh --agent claude-code

# Or install for all detected agents
./install.sh --all

# List available skills
./install.sh --list
```

| Agent | Flag |
|:------|:-----|
| Claude Code | `--agent claude-code` |
| Codex / OpenAI | `--agent codex` |
| Cursor IDE | `--agent cursor` |
| Gemini CLI | `--agent gemini-cli` |
| Windsurf | `--agent windsurf` |
| GitHub Copilot | `--agent github-copilot` |
| OpenClaw | `--agent openclaw` |
| Hermes Agent | `--agent hermes-agent` |

---

## Skill Categories

<!-- BEGIN INVENTORY -->

### 🔍 Recon & OSINT (12 skills)
`osint-framework` · `username-scanner` · `email-osint-investigation` · `spiderfoot-automation` · `parallel-intel-gathering` · `osint-recon-model` · `reconnaissance-ops` · `darkweb-research` · `vulnerability-discovery` · `chatgpt-web-relay` · `local-network-recon` · `network-device-recon`

### 🌐 Web Pentest (13 skills)
`web-app-pentest` · `api-security-testing` · `client-auth-bypass` · `web-app-assessment` · `web-security-advanced` · `waf-bypass-techniques` · `ctf-web-attacks` · `ctf-web-pwn-methodology` · `framework-vulnerability-research` · `sql-server-exploitation` · `client-reverse-engineering` · `android-pentest` · `browser-automation-security`

### 🖥️ Network Pentest (6 skills)
`network-pentest` · `advanced-pentest` · `pentest-tool-setup` · `pentest-workflow` · `pentest-tool-reference` · `pentest-quick-checklist`

### 💥 Exploit Development (10 skills)
`exploit-development` · `zero-day-hunting` · `kernel-exploitation` · `exploit-poc-builder` · `crypto-toolkit` · `crypto-ctf-attacks` · `cryptography-fundamentals` · `crypto-attack-patterns` · `encoding-realignment` · `binary-exploitation`

### 🔧 Reverse Engineering (3 skills)
`reverse-engineering` · `ctf-reverse-engineering` · `digital-forensics`

### 🚩 CTF (10 skills)
`ctf-playbook` · `ctf-orchestrator` · `ctf-misc-toolkit` · `ctf-technique-atlas` · `ctf-training-loop` · `ctf-web-exploitation` · `ctf-writeup-discipline` · `ctf-writeup-screenshots` · `ctf-kernel-exploitation` · `ctf-jail-escape`

### 🎯 Post-Exploitation (6 skills)
`post-exploitation-ops` · `intranet-pentest-advanced` · `advanced-attack-chains` · `professional-pentest-guide` · `autonomous-pentest-scanner` · `pentest-report-generator`

### ☁️ Cloud & AI Security (6 skills)
`ai-ml-security-assessment` · `ai-mcp-security` · `modern-attack-surfaces` · `security-and-hardening` · `security-audit` · `offensive-toolkit`

### 🔌 Hardware & IoT (12 skills)
`hardware-iot-hacking` · `bluetooth-jammer-sweep` · `wifi-deauth-jammer` · `nrf24-bitbang-spi` · `rf-multi-protocol-jammer` · `wifi-dualband-jammer` · `esp32-serial-diag` · `flipper-zero-backup` · `flipper-zero-firmware` · `rf-jammer-firmware-port` · `smart-card-driver-debug` · `smart-card-usb-direct`

**Total: 79 skills** (+ 1 orchestrator)
<!-- END INVENTORY -->

---

## Usage

### The Orchestrator

`security-orchestrator` is an optional cross-domain router. It is **not** a
mandatory first-load skill — for single-domain tasks, let native skill
discovery handle routing. Use the orchestrator only when a task spans multiple
security domains and needs coordination.

1. Analyzes intent across domains
2. Routes to the right specialized skill(s)
3. Can trigger parallel skill loading for speed

### Routing Logic

```
"scan this target"         → recon + web-app-pentest
"exploit this bug"         → exploit-development
"reverse this binary"      → reverse-engineering
"CTF challenge"            → ctf (ctf-orchestrator routes further)
"enumerate network"        → network-pentest
"OSINT on person/domain"   → recon (osint-framework)
"bypass WAF"              → web-advanced-pentest (waf-bypass-techniques)
"privilege escalation"     → post-exploitation
"audit this code"          → cloud-security (security-audit)
"hack IoT device"          → hardware-iot
"AI security / MCP"        → cloud-security (ai-mcp-security)
"fuzz this target"         → exploit-dev (zero-day-hunting)
"crack this hash"          → exploit-dev (cryptography-fundamentals)
"advanced-pentest report"           → post-exploitation (pentest-report-generator)
```

### Parallel Execution

For maximum speed, load multiple skills in parallel:
- **Full advanced-pentest**: recon + web-app-pentest + network-pentest + post-exploitation
- **Bug bounty**: recon + web-app-pentest + exploit-dev + waf-bypass-techniques
- **CTF solve**: ctf-orchestrator → routes to ctf-web / ctf-crypto / ctf-misc-toolkit / ctf-reverse as needed
- **Internal advanced-pentest**: network-pentest + post-exploitation + intranet-pentest-advanced
- **Hardware assessment**: hardware-iot-hacking + reverse-engineering

### Selective Install

```bash
# Install only specific domains
./install.sh --agent claude-code --domains web-advanced-pentest,exploit-dev

# Install only CTF skills
./install.sh --agent claude-code --domains ctf

# Install only the orchestrator
./install.sh --agent claude-code --skills security-orchestrator
```

### Skill Structure

Every skill follows the [Agent Skills open standard](https://agentskills.io):

```
skills/
├── security-orchestrator/          # Master router
│   └── SKILL.md
├── recon/
│   ├── osint-framework/
│   │   ├── SKILL.md                # Instructions + YAML frontmatter
│   │   ├── references/             # Deep knowledge files
│   │   └── scripts/                # Helper automation
│   └── ...
└── ...
```

### Rules Library

Shared knowledge in `rules/` loaded across skills:

| File | Contents |
|:-----|:---------|
| `rules/security-rules.md` | Payloads (XSS/SSRF/SQLi/SSTI), WAF bypass ladder, hunting rules, top 10 mistakes |

### Provider Configs

Pre-configured instruction files in `providers/` for each agent:

```
providers/
├── claude-code/CLAUDE.md
├── codex/AGENTS.md
├── cursor/.cursorrules
├── gemini/GEMINI.md
├── hermes/AGENTS.md
└── openclaw/AGENTS.md
```

---

## Compatibility

| Agent | Install location |
|:------|:-----------------|
| Claude Code | `.claude/skills/` or `~/.claude/skills/` |
| Codex | `.codex/skills/` or `AGENTS.md` |
| Cursor | `.cursor/skills/` or `.cursorrules` |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/skills/` |
| GitHub Copilot | `.github/copilot-instructions.md` |
| OpenClaw | `.agents/skills/` |
| Hermes Agent | `~/.hermes/skills/` |

---

## Contributing

PRs welcome. New skills must include:
1. `SKILL.md` with required YAML frontmatter (`name`, `description`)
2. At least one `references/` file with real knowledge (not AI-generated)
3. Trigger conditions in `description` field
4. Tested in at least one agent before submitting

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

[MIT](LICENSE) — Use for authorized security testing only. Follow responsible disclosure.

---

> 🌐 繁體中文 · [简体中文](README_zh_CN.md) · [日本語](README_ja.md)

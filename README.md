# Security Agent Skills

**79 security skills across 9 domains — installable into Claude Code, Codex, Cursor, Gemini CLI, Windsurf, GitHub Copilot, OpenClaw, and Hermes Agent.**

Built from real security engagements. Not theoretical. Not AI-generated filler. Battle-tested methodologies, complete payload libraries, and working exploit patterns integrating 479+ GitHub repositories and 214+ reference files.

## What's Inside

| Domain | Skills | Highlights |
|:-------|------:|:-----------|
| 🔍 Recon & OSINT | 12 | Multi-platform username scanning, email-first OSINT, dark web research, SpiderFoot automation |
| 🌐 Web Pentest | 14 | OWASP 2025 complete, API security (REST/GraphQL/gRPC), WAF bypass, client-side auth bypass |
| 🖥️ Network Pentest | 6 | AD attacks, cloud pentesting, container escape, C2 frameworks, EDR evasion |
| 💥 Exploit Development | 10 | Zero-day hunting (AFL++/syzkaller), kernel exploitation, ROP/heap/format string, crypto attacks |
| 🔧 Reverse Engineering | 3 | Ghidra/IDA/radare2/angr, firmware extraction, binary analysis |
| 🚩 CTF | 12 | Full CTF playbook, technique atlas, writeup discipline, training loop |
| 🎯 Post-Exploitation | 6 | Lateral movement, credential theft, persistence, AD/ADCS attacks, tunneling |
| ☁️ Cloud & AI Security | 7 | MCP/AI security, prompt injection, agent privilege escalation, code audit |
| 🔌 Hardware & IoT | 12 | UART/JTAG/SPI, firmware, SDR/RFID/NFC, Flipper Zero, ESP32, smart cards |

## Quick Install

```bash
git clone https://github.com/wang/security-agent-skills.git
cd security-agent-skills
./install.sh --agent claude-code
```

### Supported Agents

```bash
./install.sh --agent claude-code   # → .claude/skills/ or ~/.claude/skills/
./install.sh --agent codex         # → .codex/skills/ or AGENTS.md
./install.sh --agent cursor        # → .cursor/skills/ or .cursorrules
./install.sh --agent gemini        # → .gemini/skills/
./install.sh --agent windsurf      # → .windsurf/skills/
./install.sh --agent copilot       # → .github/copilot-instructions.md
./install.sh --agent openclaw      # → .agents/skills/
./install.sh --agent hermes        # → ~/.hermes/skills/
./install.sh --all                 # → Install for every detected agent
./install.sh --list                # → List all available skills
```

## Skill Structure

Every skill follows the Agent Skills open standard:

```
skills/
├── security-orchestrator/          # Master router — load first, routes to specialized skills
│   └── SKILL.md
├── recon/
│   ├── osint/
│   │   ├── SKILL.md                # Instructions + YAML frontmatter (name, description)
│   │   ├── references/             # Deep knowledge files
│   │   └── scripts/                # Helper automation
│   ├── aliens-eye/
│   └── ...
├── web-pentest/
│   ├── web-app-pentest/
│   ├── api-security-testing/
│   └── ...
└── ...
```

### SKILL.md Format

```yaml
---
name: skill-name
description: "What this skill does and when to load it"
version: 1.0.0
tags: [relevant, tags]
---

# Skill Title

Instructions the agent follows when the skill is activated...
```

The `name` and `description` fields are required. The agent uses `description` to decide when to activate the skill — make it specific about trigger conditions.

## The Orchestrator

`security-orchestrator` is the master router. When a user asks about any security task, it:
1. Analyzes intent
2. Routes to the right specialized skill(s)
3. Can trigger parallel skill loading for speed

Load it first in your agent's system prompt or instructions file for intelligent routing.

## Rules Library

Shared knowledge files that apply across skills:

| File | Contents |
|:-----|:---------|
| `rules/payloads.md` | 2600+ lines: XSS, SSRF, SQLi, IDOR, OAuth, SSTI, deserialization payloads |
| `rules/techniques.md` | Proven attack techniques from real paid engagements |
| `rules/waf-bypass-protocol.md` | WAF bypass iteration ladder (Akamai/Cloudflare/Imperva) |
| `rules/hunting.md` | 31 hunting rules with harm checks and mutation matrices |
| `rules/mistakes.md` | Top 10 most common mistakes to avoid |

## Provider Configs

Pre-configured instruction files for each agent are in `providers/`:

```
providers/
├── claude-code/CLAUDE.md          # Claude Code project instructions
├── codex/AGENTS.md                # Codex / OpenAI agents
├── cursor/.cursorrules            # Cursor IDE rules
├── gemini/GEMINI.md               # Gemini CLI
├── openclaw/AGENTS.md             # OpenClaw
└── hermes/AGENTS.md               # Hermes Agent
```

Copy the relevant file to your project root during installation, or let `install.sh` do it automatically.

## Selective Install

Install only specific domains:

```bash
# Install only web pentest and exploit dev
./install.sh --agent claude-code --domains web-pentest,exploit-dev

# Install only CTF skills
./install.sh --agent claude-code --domains ctf

# Install only the orchestrator
./install.sh --agent claude-code --skills security-orchestrator
```

## Compatibility

This follows the [Agent Skills open standard](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) — portable directories with `SKILL.md` files and YAML frontmatter. Works with any agent that supports the `SKILL.md` format:

- Claude Code (`.claude/skills/`)
- Codex CLI (`.codex/skills/`)
- Cursor (`.cursor/skills/`)
- Gemini CLI (`.gemini/skills/`)
- Windsurf (`.windsurf/skills/`)
- OpenClaw (`.agents/skills/`)
- Hermes Agent (`~/.hermes/skills/`)
- GitHub Copilot (`.github/copilot-instructions.md`)
- Any agent reading `AGENTS.md` with skill paths

## License

MIT — Use for authorized security testing only. Follow responsible disclosure.

## Contributing

PRs welcome. New skills must include:
1. `SKILL.md` with required frontmatter
2. At least one `references/` file with real knowledge (not AI-generated)
3. Trigger conditions in `description` field
4. Test the skill in at least one agent before submitting

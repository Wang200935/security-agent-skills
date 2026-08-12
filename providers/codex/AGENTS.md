# Codex / OpenAI Agents — Security Skills

## Skill Discovery

Skills are in `skills/` organized by domain. Load `skills/security-orchestrator/SKILL.md` for automatic routing.

## Installation

```bash
./install.sh --agent codex
```

This copies skills to `.codex/skills/` or adds skill paths to `AGENTS.md`.

## Skill Paths

```
skills/security-orchestrator/SKILL.md
skills/recon/*/SKILL.md
skills/web-pentest/*/SKILL.md
skills/network-pentest/*/SKILL.md
skills/exploit-dev/*/SKILL.md
skills/reverse-engineering/*/SKILL.md
skills/ctf/*/SKILL.md
skills/post-exploitation/*/SKILL.md
skills/cloud-security/*/SKILL.md
skills/hardware-iot/*/SKILL.md
```

## Rules

Shared knowledge in `rules/security-rules.md` covers attack payloads, proven techniques, WAF bypass patterns, and hunting rules.

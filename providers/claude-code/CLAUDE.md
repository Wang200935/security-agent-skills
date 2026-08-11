# Claude Code — Security Skills

## Skill Discovery

Skills are in `skills/` organized by domain. Load `skills/security-orchestrator/SKILL.md` for automatic routing.

## Manual Skill Loading

For Claude Code, skills are auto-discovered from `.claude/skills/` (project) or `~/.claude/skills/` (global). When installed:

```
.claude/skills/
├── security-orchestrator/SKILL.md
├── recon/
│   ├── osint/SKILL.md
│   └── ...
├── web-pentest/
│   └── ...
└── ...
```

Claude Code reads `name` and `description` from YAML frontmatter to decide when to activate skills.

## Recommended Workflow

1. User asks a security question
2. `security-orchestrator` activates and routes to the right skill
3. Specialized skill activates and provides methodology/payloads/commands
4. For broad tasks, multiple skills activate in parallel

## Example Prompts

- "Run an OSINT investigation on domain example.com"
- "Test this web app for OWASP Top 10 vulnerabilities"
- "Help me solve this CTF crypto challenge"
- "Audit this code for security issues"
- "Reverse engineer this binary firmware"

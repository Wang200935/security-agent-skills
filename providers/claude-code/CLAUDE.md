# Claude Code — Security Skills

## Skill Discovery

Skills are in `skills/` organized by domain. Load `skills/security-orchestrator/SKILL.md` only when you need cross-domain routing.

## Manual Skill Loading

Claude Code reads the repo-local skill tree after installation. Skills are flattened by installer into the agent's skills root.

## Recommended Workflow

1. User asks a security question
2. Optional: `security-orchestrator` activates and routes to the right skill
3. Specialized skill activates and provides methodology/payloads/commands
4. For broad tasks, multiple skills activate in parallel

## Example Prompts

- "Run an OSINT investigation on domain example.com"
- "Test this web app for OWASP Top 10 vulnerabilities"
- "Help me solve this CTF crypto challenge"
- "Audit this code for security issues"
- "Reverse engineer this binary firmware"

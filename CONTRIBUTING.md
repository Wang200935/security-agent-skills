# Security Agent Skills — Contributing

## Adding New Skills

1. Create a directory under the appropriate category in `skills/`
2. Write a `SKILL.md` with required YAML frontmatter (`name`, `description`)
3. Add `references/` with real knowledge — port from actual tools, repos, or field experience
4. Add `scripts/` if the skill benefits from automation
5. Test in at least one agent (Claude Code, Codex, etc.)

### SKILL.md Template

```yaml
---
name: your-skill-name
description: "Specific trigger conditions and what the skill does. The agent reads this to decide activation."
version: 1.0.0
tags: [relevant, tags]
---

# Skill Title

## When to Load
Trigger conditions...

## Methodology
Steps...

## References
- `references/your-ref.md` — What it contains
```

### Quality Standards

- No AI-generated filler — every reference file must contain actionable knowledge
- Payloads must be tested, not theoretical
- Commands must work on the stated platform
- Include pitfalls and error recovery sections

## Adding Provider Configs

To support a new agent:
1. Create a directory under `providers/` with the agent name
2. Add the instruction file format that agent expects (`.cursorrules`, `AGENTS.md`, etc.)
3. Update `install.sh` to handle the new agent
4. Update `README.md` supported agents list

## Rule Files

Shared knowledge in `rules/` is loaded by multiple skills. When adding:
- Keep it cross-domain (not specific to one skill)
- Include real examples from engagements
- Mark vendor-specific behavior clearly

## Pull Request Checklist

- [ ] `SKILL.md` has required `name` and `description` fields
- [ ] At least one `references/` file with real knowledge
- [ ] Trigger conditions in `description` field
- [ ] Tested in at least one agent
- [ ] No hardcoded credentials or tokens
- [ ] No obfuscated or encoded payloads
- [ ] `./install.sh --list` shows the new skill

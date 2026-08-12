# Gemini CLI Security Skills

## Overview
79 security skills for Gemini CLI, organized into 9 domains.

## Installation
```bash
./install.sh --agent gemini
```

Skills are installed to `.gemini/skills/`.

## Load Order
1. `security-orchestrator` is optional; use it only when a task spans multiple domains
2. Route to specialized skills based on intent
3. Parallel loading is available for broad tasks

## Skill Paths
```
.gemini/skills/security-orchestrator/SKILL.md
.gemini/skills/osint-framework/SKILL.md
.gemini/skills/web-app-pentest/SKILL.md
...
```

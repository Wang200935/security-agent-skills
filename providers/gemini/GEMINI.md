# Gemini CLI Security Skills

## Overview
79 security skills for Gemini CLI, organized into 9 domains.

## Installation
```bash
./install.sh --agent gemini
```

Skills are installed to `.gemini/skills/`.

## Load Order
1. Load `security-orchestrator` first for routing
2. Orchestrator routes to specialized skills based on intent
3. Parallel loading for broad tasks

## Skill Paths
```
.gemini/skills/security-orchestrator/SKILL.md
.gemini/skills/recon/*/SKILL.md
.gemini/skills/web-pentest/*/SKILL.md
...
```

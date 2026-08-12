# OpenClaw Security Skills

## Installation
```bash
./install.sh --agent openclaw
```

Skills are installed to `.agents/skills/`.

## Structure
```
.agents/skills/
├── security-orchestrator/SKILL.md
├── osint-framework/SKILL.md
├── web-app-pentest/SKILL.md
├── ...
```

## Load Order
1. `security-orchestrator` is optional; load it only for cross-domain routing
2. Route to specialized skills based on intent
3. Parallel loading is available for broad tasks

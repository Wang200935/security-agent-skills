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
├── recon/
├── web-pentest/
├── ...
└── hardware-iot/
```

## Load Order
1. Load `security-orchestrator` for routing
2. Route to specialized skills based on intent
3. Parallel loading for broad tasks

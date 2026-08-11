# Hermes Agent Security Skills

## Installation
```bash
./install.sh --agent hermes
```

Skills are installed to `~/.hermes/skills/` (or current profile's skills directory).

## Categories
Same 9 domains as other agents. The `security-orchestrator` skill serves as the master router.

## Usage
```bash
# Load the orchestrator in Hermes
skill_view(name='security-orchestrator')

# The orchestrator routes to specialized skills
# e.g., "pentest this web app" → loads web-app-pentest + api-security-testing
```

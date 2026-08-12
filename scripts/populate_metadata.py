#!/usr/bin/env python3
"""
Populate tags and related_skills for all SKILL.md files.
Tags: derived from domain + skill name tokens + description keywords.
Related: computed from cross-references in RELATED_MAP.
"""

import os, yaml, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

DOMAIN_TAGS = {
    "recon": ["osint", "recon", "information-gathering"],
    "web-pentest": ["web", "pentest", "owasp"],
    "network-pentest": ["network", "pentest", "infrastructure"],
    "exploit-dev": ["exploit", "vulnerability", "payload"],
    "reverse-engineering": ["reversing", "binary-analysis", "disassembly"],
    "ctf": ["ctf", "competition", "challenge"],
    "post-exploitation": ["post-exploitation", "lateral-movement", "persistence"],
    "cloud-security": ["cloud", "aws", "azure", "gcp", "kubernetes"],
    "hardware-iot": ["hardware", "iot", "embedded", "firmware"],
    "orchestrator": ["router", "orchestration", "meta"],
}

# Manually curated cross-references
RELATED_MAP = {
    "web-app-pentest": ["web-app-assessment", "api-security-testing", "waf-bypass-techniques", "ctf-web-attacks"],
    "web-app-assessment": ["web-app-pentest", "web-security-advanced", "vulnerability-discovery"],
    "network-pentest": ["advanced-pentest", "pentest-workflow", "pentest-tool-setup"],
    "advanced-pentest": ["network-pentest", "intranet-pentest-advanced", "post-exploitation-ops"],
    "api-security-testing": ["web-app-pentest", "web-security-advanced", "web-app-assessment"],
    "ctf-playbook": ["ctf-orchestrator", "ctf-technique-atlas", "ctf-training-loop"],
    "ctf-orchestrator": ["ctf-playbook", "ctf-technique-atlas", "security-orchestrator"],
    "exploit-development": ["binary-exploitation", "exploit-poc-builder", "zero-day-hunting"],
    "binary-exploitation": ["exploit-development", "kernel-exploitation", "ctf-kernel-exploitation"],
    "kernel-exploitation": ["binary-exploitation", "ctf-kernel-exploitation", "exploit-development"],
    "reverse-engineering": ["ctf-reverse-engineering", "client-reverse-engineering", "digital-forensics"],
    "ctf-reverse-engineering": ["reverse-engineering", "digital-forensics", "ctf-technique-atlas"],
    "osint-framework": ["osint-recon-model", "spiderfoot-automation", "username-scanner"],
    "osint-recon-model": ["osint-framework", "reconnaissance-ops", "parallel-intel-gathering"],
    "wifi-deauth-jammer": ["wifi-dualband-jammer", "rf-multi-protocol-jammer", "bluetooth-jammer-sweep"],
    "wifi-dualband-jammer": ["wifi-deauth-jammer", "rf-multi-protocol-jammer", "rf-jammer-firmware-port"],
    "flipper-zero-backup": ["flipper-zero-firmware", "hardware-iot-hacking"],
    "flipper-zero-firmware": ["flipper-zero-backup", "hardware-iot-hacking"],
    "intranet-pentest-advanced": ["advanced-pentest", "post-exploitation-ops", "pentest-report-generator"],
    "security-orchestrator": ["ctf-orchestrator", "advanced-pentest", "osint-framework"],
    "autonomous-pentest-scanner": ["intranet-pentest-advanced", "advanced-pentest", "exploit-development"],
    "sql-server-exploitation": ["web-app-pentest", "exploit-development", "api-security-testing"],
    "client-auth-bypass": ["client-reverse-engineering", "web-app-pentest", "browser-automation-security"],
    "client-reverse-engineering": ["reverse-engineering", "client-auth-bypass", "browser-automation-security"],
    "cloud-security": ["security-audit", "security-and-hardening", "security-code-review"],
    "security-audit": ["security-and-hardening", "security-code-review", "ai-mcp-security"],
}


def parse_frontmatter(path):
    with open(path, 'r', errors='replace') as f:
        content = f.read()
    if not content.startswith('---'):
        return {}, content
    lines = content.split('\n')
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return {}, content
    fm_text = '\n'.join(lines[1:end])
    body = '\n'.join(lines[end+1:])
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return {}, content
    return fm, body


def get_tags(skill_id, domain, description):
    tags = list(DOMAIN_TAGS.get(domain, []))
    # Add tokens from skill_id
    for token in re.split(r'[-_]', skill_id):
        token = token.lower().strip()
        if len(token) > 2 and token not in tags:
            tags.append(token)
    # Cap at 8 tags
    return tags[:8]


def get_related(skill_id, valid_ids):
    related = RELATED_MAP.get(skill_id, [])
    return [r for r in related if r in valid_ids and r != skill_id]


def main():
    # Build set of valid skill IDs
    valid_ids = set()
    for root, dirs, files in os.walk(SKILLS):
        for f in files:
            if f == 'SKILL.md':
                valid_ids.add(os.path.basename(root))
    
    updated = 0
    for root, dirs, files in os.walk(SKILLS):
        for f in files:
            if f != 'SKILL.md':
                continue
            path = Path(os.path.join(root, f))
            skill_id = path.parent.name
            domain = os.path.basename(os.path.dirname(root))
            
            fm, body = parse_frontmatter(path)
            if not fm:
                continue
            
            changed = False
            metadata = fm.get('metadata', {})
            if not isinstance(metadata, dict):
                metadata = {}
            hermes = metadata.get('hermes', {})
            if not isinstance(hermes, dict):
                hermes = {}
            
            # Populate tags
            current_tags = fm.get('tags', [])
            if isinstance(current_tags, str):
                current_tags = [current_tags]
            if not current_tags:
                new_tags = get_tags(skill_id, domain, fm.get('description', ''))
                fm['tags'] = new_tags
                changed = True
            
            # Populate related_skills
            current_related = fm.get('related_skills', [])
            if isinstance(current_related, str):
                current_related = [current_related]
            if not current_related:
                related = get_related(skill_id, valid_ids)
                fm['related_skills'] = related
                changed = True

            # Keep legacy metadata.hermes mirror for compatibility, but only if needed
            metadata = fm.get('metadata', {})
            if not isinstance(metadata, dict):
                metadata = {}
            hermes = metadata.get('hermes', {})
            if not isinstance(hermes, dict):
                hermes = {}
            hermes['tags'] = fm.get('tags', [])
            hermes['related_skills'] = fm.get('related_skills', [])
            hermes['origin'] = hermes.get('origin', 'import')
            metadata['hermes'] = hermes
            fm['metadata'] = metadata
    
    print(f"\nUpdated: {updated}")


if __name__ == "__main__":
    main()

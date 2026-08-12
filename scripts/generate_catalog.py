#!/usr/bin/env python3
"""Generate catalog.yaml from the skills/ tree — single source of truth."""

import os, re, sys, yaml
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_PATH = REPO_ROOT / "catalog.yaml"

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
    try:
        fm = yaml.safe_load(fm_text) or {}
    except Exception:
        fm = {}
    return fm, content

def scan_skills():
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f != 'SKILL.md':
                continue
            path = Path(root)
            skill_name = path.name
            
            # Detect domain: parent dir relative to skills/
            rel = path.relative_to(SKILLS_DIR)
            parts = rel.parts
            if len(parts) == 1:
                domain = 'orchestrator'
            elif len(parts) == 2:
                domain = parts[0]
            else:
                domain = parts[0] if len(parts) > 1 else 'orchestrator'
            
            skill_path = path / 'SKILL.md'
            fm, content = parse_frontmatter(skill_path)
            
            ref_dir = path / 'references'
            ref_count = len(list(ref_dir.glob('*.md'))) if ref_dir.is_dir() else 0
            
            script_dir = path / 'scripts'
            script_count = len([s for s in script_dir.iterdir() if s.suffix in ('.sh', '.py', '.js')]) if script_dir.is_dir() else 0
            
            size = skill_path.stat().st_size
            
            skills.append({
                'id': fm.get('name', skill_name),
                'path': f"skills/{rel}/SKILL.md",
                'domain': domain,
                'description': str(fm.get('description', ''))[:200],
                'version': str(fm.get('version', '')),
                'tags': fm.get('tags', []),
                'related_skills': fm.get('related_skills', []),
                'skill_md_bytes': size,
                'reference_count': ref_count,
                'script_count': script_count,
            })
    
    # Normalize tag/related fields to lists for downstream consumers
    for s in skills:
        if isinstance(s['tags'], str):
            s['tags'] = [s['tags']]
        elif not isinstance(s['tags'], list):
            s['tags'] = []
        if isinstance(s['related_skills'], str):
            s['related_skills'] = [s['related_skills']]
        elif not isinstance(s['related_skills'], list):
            s['related_skills'] = []
    
    skills.sort(key=lambda s: (s['domain'], s['id']))
    return skills

def main():
    skills = scan_skills()
    domains = sorted(set(s['domain'] for s in skills))
    counts = Counter(s['domain'] for s in skills)
    
    catalog = {
        'schema_version': 1,
        'total_skills': len(skills),
        'domains': domains,
        'domain_counts': dict(sorted(counts.items())),
        'skills': skills,
    }
    
    with open(CATALOG_PATH, 'w') as f:
        yaml.dump(catalog, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"catalog.yaml: {len(skills)} skills, {len(domains)} domains")
    for d, c in sorted(counts.items()):
        print(f"  {d}: {c}")

if __name__ == '__main__':
    main()

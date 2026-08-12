#!/usr/bin/env python3
"""
Normalize SKILL.md frontmatter to a consistent schema:

Required fields:
  - name: string (matches directory name)
  - description: string

Optional fields (consistent placement):
  - version: string
  - license: string (default MIT)
  - category: string (domain name)
  - metadata: dict (platform-specific: hermes, cursor, etc.)
    metadata.hermes.tags: list
    metadata.hermes.related_skills: list
    metadata.hermes.origin: string
  - platforms: list (default [linux, macos, windows])

This script migrates flat fields (tags, related_skills, origin)
into nested metadata.hermes.* and fills in missing version/license.
"""

import os, sys, yaml, re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

def parse_frontmatter(path):
    with open(path, 'r', errors='replace') as f:
        content = f.read()
    if not content.startswith('---'):
        return {}, content, content
    lines = content.split('\n')
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return {}, content, content
    fm_text = '\n'.join(lines[1:end])
    body = '\n'.join(lines[end+1:])
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        return {}, content, content
    return fm, body, content


def normalize_skill(skill_path):
    fm, body, original = parse_frontmatter(skill_path)
    if not fm:
        return False, "no frontmatter"
    
    changed = False
    skill_name = skill_path.parent.name
    
    # Fix name if it doesn't match directory
    if fm.get('name') != skill_name:
        fm['name'] = skill_name
        changed = True
    
    # Ensure description exists
    if 'description' not in fm:
        return False, "no description"
    
    # Ensure version
    if 'version' not in fm or not fm['version']:
        fm['version'] = '1.0.0'
        changed = True
    
    # Ensure license
    if 'license' not in fm or not fm['license']:
        fm['license'] = 'MIT'
        changed = True
    
    # Migrate flat fields into metadata.hermes
    flat_to_nested = ['tags', 'related_skills', 'origin']
    
    if 'metadata' not in fm:
        fm['metadata'] = {}
    
    metadata = fm['metadata']
    if not isinstance(metadata, dict):
        metadata = {}
        fm['metadata'] = {}
    
    hermes = metadata.get('hermes', {})
    if not isinstance(hermes, dict):
        hermes = {}
        metadata['hermes'] = hermes
    
    for field in flat_to_nested:
        if field in fm:
            # Move from flat to nested (if not already there)
            if field not in hermes:
                hermes[field] = fm[field]
                changed = True
            del fm[field]
    
    if hermes:
        if 'tags' not in hermes:
            hermes['tags'] = []
            changed = True
        if 'related_skills' not in hermes:
            hermes['related_skills'] = []
            changed = True
        if 'origin' not in hermes:
            hermes['origin'] = 'import'
            changed = True
        metadata['hermes'] = hermes
    
    if not metadata:
        del fm['metadata']
    
    if not changed:
        return False, "already normalized"
    
    # Rebuild file
    new_fm = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    new_content = '---\n' + new_fm + '---\n' + body
    
    if new_content != original:
        with open(skill_path, 'w') as f:
            f.write(new_content)
        return True, "normalized"
    
    return False, "no change after rebuild"


def main():
    fixed = 0
    skipped = 0
    errors = 0
    
    for root, dirs, files in os.walk(SKILLS):
        for f in files:
            if f != 'SKILL.md':
                continue
            path = os.path.join(root, f)
            skill_name = os.path.basename(root)
            
            ok, msg = normalize_skill(Path(path))
            
            if ok:
                print(f"  normalized: {skill_name}")
                fixed += 1
            elif msg == "no frontmatter":
                print(f"  ERROR: {skill_name} has no frontmatter")
                errors += 1
            elif msg == "no description":
                print(f"  ERROR: {skill_name} has no description")
                errors += 1
            else:
                skipped += 1
    
    print(f"\nNormalized: {fixed}, Skipped (already ok): {skipped}, Errors: {errors}")


if __name__ == "__main__":
    main()

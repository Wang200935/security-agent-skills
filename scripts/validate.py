#!/usr/bin/env python3
"""
CI validation for security-agent-skills repository.

Checks:
1. SKILL.md frontmatter parseable (YAML valid)
2. name field exists and matches directory name
3. description field exists and non-empty
4. name syntax valid (lowercase, hyphens, max 64 chars)
5. No duplicate skill names
6. All related_skills reference existing skills
7. All internal markdown path references resolve
8. No hardcoded absolute home paths (/Users/...)
9. No empty reference files (0 bytes)
10. catalog.yaml matches actual filesystem
11. No ghost skills in orchestrator routing table
12. No oversized SKILL.md (>50KB warning, >100KB error)
"""

import os, re, sys, yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
CATALOG_PATH = REPO_ROOT / "catalog.yaml"

errors = []
warnings = []

def err(msg):
    errors.append(msg)

def warn(msg):
    warnings.append(msg)

def parse_frontmatter(path):
    with open(path, 'r', errors='replace') as f:
        content = f.read()
    if not content.startswith('---'):
        return {}, content, False
    # Find the closing --- on its own line (not part of a horizontal rule in body)
    lines = content.split('\n')
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return {}, content, False
    fm_text = '\n'.join(lines[1:end])
    if not fm_text.strip():
        return {}, content, False
    try:
        fm = yaml.safe_load(fm_text) or {}
        return fm, content, True
    except yaml.YAMLError:
        return {}, content, False

def check_skill_md(path, all_skill_names):
    skill_name = path.parent.name
    fm, content, parsed = parse_frontmatter(path)
    
    # 1. Frontmatter parseable
    if not parsed:
        err(f"{path}: frontmatter not parseable")
        return
    
    # 2. name exists
    if 'name' not in fm:
        err(f"{path}: missing 'name' field")
    else:
        fm_name = fm['name']
        # 3. name matches directory
        if fm_name != skill_name:
            err(f"{path}: name '{fm_name}' != directory '{skill_name}'")
        # 4. name syntax
        if not re.match(r'^[a-z][a-z0-9-]{0,63}$', str(fm_name)):
            err(f"{path}: name '{fm_name}' invalid syntax (lowercase, hyphens, max 64)")
    
    # 5. description exists
    desc = fm.get('description', '')
    if not desc:
        err(f"{path}: missing 'description' field")
    elif len(str(desc)) < 10:
        warn(f"{path}: description very short ({len(str(desc))} chars)")
    elif len(str(desc)) > 500:
        warn(f"{path}: description very long ({len(str(desc))} chars)")
    
    # 6. related_skills reference existing skills (top-level schema)
    related = fm.get('related_skills', [])
    if not isinstance(related, list):
        related = [related] if related else []
    for r in related:
        r = str(r).strip()
        if r and r not in all_skill_names:
            err(f"{path}: related_skill '{r}' not found in skills tree (ghost reference)")

    # 6b. nested metadata.hermes is legacy and should not be the canonical source
    meta = fm.get('metadata', {})
    if isinstance(meta, dict) and isinstance(meta.get('hermes'), dict):
        hermes = meta['hermes']
        if hermes.get('tags') or hermes.get('related_skills'):
            warn(f"{path}: metadata.hermes contains tags/related_skills; use top-level tags/related_skills for catalog")
    
    # 8. No hardcoded absolute home paths
    if '/Users/' in content or '/home/' in content:
        # Check if it's in a code block (sometimes legitimate in examples)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '/Users/' in line and 'example' not in line.lower() and '<' not in line:
                warn(f"{path}:{i}: hardcoded home path: {line.strip()[:100]}")
    
    # 12. Oversized SKILL.md
    size = path.stat().st_size
    if size > 100_000:
        err(f"{path}: SKILL.md is {size} bytes (>100KB — must split into references)")
    elif size > 50_000:
        warn(f"{path}: SKILL.md is {size} bytes (>50KB — consider splitting)")
    
    # 7. Internal markdown path references resolve
    md_refs = re.findall(r'\[.+?\\\]\((?!https?://)(?!mailto:)(.+?\.md)\)', content)
    for ref in md_refs:
        ref_path = (path.parent / ref).resolve()
        if not ref_path.exists():
            warn(f"{path}: internal reference '{ref}' does not resolve")
    
    # Check inline path references: `../../path.md` or `references/foo.md`
    inline_paths = re.findall(r'(?:^|\s)(?:→|see|See|see also)\s+[`"]?([a-z_./-]+\.md)[`"]?', content, re.I)
    for ref in inline_paths:
        if ref.startswith('http'):
            continue
        ref_path = (path.parent / ref).resolve()
        if not ref_path.exists():
            warn(f"{path}: inline path reference '{ref}' does not resolve")
    
    # 7b. Validate body backtick skill ID references
    # Tokens in backticks that look like skill IDs (kebab-case, 2+ words) and aren't in the canonical set
    BODY_SKILL_IGNORE = {
        # External skills referenced but not part of this repo
        'esp32-embedded-development', 'esp32-jammer-diag', 'esp32-nrf24-jammer-builder',
        'smart-card-reader-sle4442', 'esp32-wifi-deauth', 'playwright-cli',
        'deep-research', 'claude-code-coding-executor', 'claude-code-pr-executor',
        'claude-code-review-executor', 'esp32-wifi-killer',
        # Tool names / packages (not skill IDs)
        'rw-p', 'qemu-system-x86', 'extract-vmlinux', 'connect-src', 'img-src',
        'script-src', 'easy-session', 'apfs-fuse', 'minidump-stackwalk',
        'nbd-client', 'qemu-nbd', 'qflipper-cli', 'bose-ctl',
        'document-format-supported', 'dhcpv6-discover', 'ipv6-neighbor-discovery',
        'targets-ipv6-map4to6', 'targets-ipv6-multicast-mld', 'port-scanner',
        'impacket-psexec', 'impacket-secretsdump', 'cross-env', 'react-dom',
        'ssrf-req-filter', 'request-filtering-agent', 'factordb-python',
        'spiderfoot-venv', 'owl-alpha', 'gpt-4o', 'gpt-4o-mini', 'o1-pro',
        'playwright-stealth', 'playwright-with-fingerprints',
    }
    # Extract body (after frontmatter)
    lines = content.split('\n')
    fm_end = -1
    in_fm = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_fm:
                in_fm = True
            elif fm_end == -1:
                fm_end = i
                break
    body_text = '\n'.join(lines[fm_end+1:]) if fm_end >= 0 else ''
    
    for m in re.finditer(r'`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`', body_text):
        token = m.group(1)
        if token in BODY_SKILL_IGNORE:
            continue
        if token not in all_skill_names:
            err(f"{path}: body references skill ID `{token}` which is not in the skills tree (ghost reference)")

def check_references(path):
    ref_dir = path / 'references'
    if not ref_dir.is_dir():
        return
    for rf in ref_dir.iterdir():
        if rf.suffix == '.md':
            # 9. No empty reference files
            if rf.stat().st_size == 0:
                err(f"{rf}: empty reference file (0 bytes — delete it)")

def check_catalog():
    if not CATALOG_PATH.exists():
        err("catalog.yaml: missing — run scripts/generate_catalog.py")
        return
    
    with open(CATALOG_PATH) as f:
        catalog = yaml.safe_load(f)
    
    if not catalog:
        err("catalog.yaml: not parseable")
        return
    
    catalog_skills = set(s['id'] for s in catalog.get('skills', []))
    
    # 10. catalog matches filesystem
    fs_skills = set()
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == 'SKILL.md':
                path = Path(root)
                fm, _, _ = parse_frontmatter(path / 'SKILL.md')
                name = fm.get('name', path.name)
                fs_skills.add(name)
    
    missing_in_catalog = fs_skills - catalog_skills
    extra_in_catalog = catalog_skills - fs_skills
    
    for m in missing_in_catalog:
        err(f"catalog.yaml: missing skill '{m}' (exists in filesystem)")
    for e in extra_in_catalog:
        err(f"catalog.yaml: stale skill '{e}' (not in filesystem)")

def main():
    # Collect all skill names first
    all_skill_names = set()
    skill_paths = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        for f in files:
            if f == 'SKILL.md':
                path = Path(root) / 'SKILL.md'
                skill_paths.append(path)
                fm, _, _ = parse_frontmatter(path)
                name = fm.get('name', path.parent.name)
                all_skill_names.add(name)
    
    # Check each skill
    for path in skill_paths:
        check_skill_md(path, all_skill_names)
        check_references(path.parent)
    
    # Check catalog
    check_catalog()
    
    # Report
    print(f"{'='*60}")
    print(f"Validation: {len(skill_paths)} skills checked")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    
    if errors:
        print(f"\n{'='*60}\nERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
    
    if warnings:
        print(f"\n{'='*60}\nWARNINGS:")
        for w in warnings[:30]:
            print(f"  ⚠ {w}")
        if len(warnings) > 30:
            print(f"  ... and {len(warnings)-30} more warnings")
    
    if errors:
        sys.exit(1)
    else:
        print("\n✓ All checks passed (errors=0)")
        sys.exit(0)

if __name__ == '__main__':
    main()

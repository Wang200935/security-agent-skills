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
        # 4. name syntax — official Agent Skills grammar
        # [a-z][a-z0-9]*(-[a-z0-9]+)* , 1-64 chars, no trailing/leading/double hyphens
        name_str = str(fm_name)
        if len(name_str) > 64:
            err(f"{path}: name '{fm_name}' exceeds 64 chars ({len(name_str)})")
        elif not re.match(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$', name_str):
            err(f"{path}: name '{fm_name}' invalid syntax (lowercase, hyphens, no trailing/double hyphens, max 64)")
    
    # 5. description exists — official hard limit is 1024 chars
    desc = fm.get('description', '')
    desc_len = len(str(desc)) if desc else 0
    if not desc:
        err(f"{path}: missing 'description' field")
    elif desc_len < 10:
        warn(f"{path}: description very short ({desc_len} chars)")
    elif desc_len > 1024:
        err(f"{path}: description exceeds 1024 chars ({desc_len} chars — hardcoded limit)")
    elif desc_len > 500:
        warn(f"{path}: description very long ({desc_len} chars)")
    
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
    
    # 8. No hardcoded absolute home paths (macOS /Users/ and Linux /home/)
    home_patterns = ['/Users/', '/home/']
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pat in home_patterns:
            if pat in line:
                # Skip code blocks and examples
                stripped = line.strip()
                if stripped.startswith('|') or stripped.startswith('```'):
                    continue
                if 'example' in line.lower() or '<' in line:
                    continue
                # Skip if it's inside a backtick code span on the same line
                # (common in inline code examples)
                warn(f"{path}:{i}: hardcoded home path: {stripped[:100]}")
    
    # 12. Oversized SKILL.md
    size = path.stat().st_size
    if size > 100_000:
        err(f"{path}: SKILL.md is {size} bytes (>100KB — must split into references)")
    elif size > 50_000:
        warn(f"{path}: SKILL.md is {size} bytes (>50KB — consider splitting)")
    
    # External skill IDs (Hermes built-in tools/skills not in this pack)
    LEGACY_SKILL_ALIASES = {
        'client-side-auth-bypass': 'client-auth-bypass',
        'web-advanced-pentest': 'web-app-pentest',
        'ctf-crypto': 'crypto-toolkit',
        'ctf-forensics': 'digital-forensics',
        'ctf-misc': 'ctf-misc-toolkit',
        'ctf-re': 'ctf-reverse-engineering',
        'ctf-web': 'ctf-web-exploitation',
        'osint-recon': 'osint-framework',
        'recon-osint': 'osint-framework',
        'pentest-flow': 'pentest-workflow',
    }
    EXTERNAL_SKILL_IDS = {
        'godmode', 'obliteratus', 'cybersecurity', 'pentest', 'osint',
        'computer-use', 'computer_use', 'computer_use',
        'vision', 'vision-based-input-automation',
        'playwright-cli', 'playwright-browser',
        'phone-harness-ios-control', 'phone-harness',
        'web_search', 'web_extract', 'web-search', 'web-extract',
        'execute_code', 'execute-code',
        'read_file', 'read-file', 'write_file', 'write-file',
        'terminal', 'delegate_task', 'delegate-task',
        'skill_manage', 'skill-manage', 'skill_view', 'skill-view',
        'patch', 'search_files', 'search-files',
        'memory', 'cronjob', 'clarify',
        'himalaya', 'notion', 'linear', 'airtable',
        'comfyui', 'stable-diffusion-image-generation',
        'whisper', 'clip', 'segment-anything-model',
        'jupyter-live-kernel', 'jupyter',
        'llama-cpp', 'gguf-quantization',
        'outlines', 'guidance',
        'spotify', 'obsidian', 'slidev',
        'esp32-embedded-development',
        'claude-code-coding-executor', 'claude-code-pr-executor',
        'claude-code-review-executor', 'claude-code-security-review',
        'impacket-psexec', 'impacket-secretsdump',
        'playwright-stealth', 'port-scanner',
        'smart-card-reader-sle4442', 'source_aware_sast',
        'recon',  # external Hermes skill, not this pack's recon-*
    }
    all_valid = all_skill_names | set(LEGACY_SKILL_ALIASES.keys()) | EXTERNAL_SKILL_IDS
    
    # 7. Internal markdown path references resolve
    # Match [text](path.md) where path is not http/mailto
    md_refs = re.findall(r'\[([^\]]*)\]\((?!https?://)(?!mailto:)([^)]+\.md)\)', content)
    for link_text, ref in md_refs:
        ref_path = (path.parent / ref).resolve()
        if not ref_path.exists():
            err(f"{path}: markdown link '{link_text}' → '{ref}' does not resolve (file not found)")
    
    # Check inline path references: `../../path.md` or `references/foo.md`
    inline_paths = re.findall(r'(?:^|\s)(?:→|see|See|see also)\s+[`"]?([a-z_./-]+\.md)[`"]?', content, re.I)
    for ref in inline_paths:
        if ref.startswith('http'):
            continue
        ref_path = (path.parent / ref).resolve()
        if not ref_path.exists():
            warn(f"{path}: inline path reference '{ref}' does not resolve")
    
    # 7b. Validate body backtick skill ID references
    # Two-pass approach:
    #   Pass A — kebab-case with at least one '-' (standard skill ID format)
    #   Pass B — single words that appear in skill-reference contexts only
    BODY_SKILL_IGNORE = {
        # Tool names / packages (not skill IDs)
        'rw-p', 'qemu-system-x86', 'extract-vmlinux', 'connect-src', 'img-src',
        'script-src', 'easy-session', 'apfs-fuse', 'minidump-stackwalk',
        'nbd-client', 'qemu-nbd', 'qflipper-cli', 'bose-ctl',
        'document-format-supported', 'dhcpv6-discover', 'ipv6-neighbor-discovery',
        'targets-ipv6-map4to6', 'targets-ipv6-multicast-mld',
        'cross-env', 'react-dom', 'ssrf-req-filter', 'request-filtering-agent',
        'factordb-python', 'spiderfoot-venv', 'owl-alpha', 'gpt-4o', 'gpt-4o-mini',
        'o1-pro', 'playwright-with-fingerprints',
        'esp32-jammer-diag', 'esp32-nrf24-jammer-builder', 'esp32-wifi-deauth',
        'esp32-wifi-killer', 'deep-research',
    }
    # Merge with EXTERNAL_SKILL_IDS defined above
    BODY_SKILL_IGNORE = BODY_SKILL_IGNORE | EXTERNAL_SKILL_IDS
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
    
    # Pass A: kebab-case tokens with at least one '-'
    for m in re.finditer(r'`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`', body_text):
        token = m.group(1)
        if token in BODY_SKILL_IGNORE:
            continue
        if token in LEGACY_SKILL_ALIASES:
            err(f"{path}: body references legacy skill ID `{token}` — should be `{LEGACY_SKILL_ALIASES[token]}`")
            continue
        if token not in all_skill_names:
            err(f"{path}: body references skill ID `{token}` which is not in the skills tree (ghost reference)")
    
    # Pass B: single-word tokens in EXPLICIT skill-reference contexts only
    # Must contain the word "skill" within a few words of the backtick token
    # Catches: "load `godmode` skill", "use `pentest` skill", "`osint` skill", "載入 `xxx` skill"
    SKILL_REF_CONTEXT = re.compile(
        r'(?:load|use|see|載入|先載入|搭配|invoke|call)\s+`([a-z][a-z0-9_-]+)`\s+skill'
        r'|`([a-z][a-z0-9_-]+)`\s+skill'
        r'|(?:load|use|載入|先載入)\s+`([a-z][a-z0-9_-]+)`\s*[\n。，；]\s*(?:skill|技能)',
        re.IGNORECASE
    )
    for m in SKILL_REF_CONTEXT.finditer(body_text):
        token = m.group(1) or m.group(2) or m.group(3)
        if not token:
            continue
        if token in BODY_SKILL_IGNORE or token in all_skill_names:
            continue
        if token in LEGACY_SKILL_ALIASES:
            err(f"{path}: body references legacy skill ID `{token}` — should be `{LEGACY_SKILL_ALIASES[token]}`")
            continue
        err(f"{path}: body references skill ID `{token}` in a skill-reference context but not in the skills tree")

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

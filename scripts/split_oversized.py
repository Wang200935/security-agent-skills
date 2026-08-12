#!/usr/bin/env python3
"""
Split oversized SKILL.md files into progressive disclosure format.

For each SKILL.md > target_size:
1. Parse frontmatter (preserve as-is)
2. Keep the overview section (first H2 or until "## Detailed" / "## Attack" etc.)
3. Move remaining sections to reference files
4. Replace moved content with brief pointers: "See references/<file>.md"

Usage: python3 scripts/split_oversized.py [--dry-run]
"""

import os, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
TARGET_SIZE = 50_000  # bytes

def split_skill(skill_path, dry_run=False):
    with open(skill_path, 'r', errors='replace') as f:
        content = f.read()
    
    size = len(content.encode('utf-8'))
    if size <= TARGET_SIZE:
        return False, f"under limit ({size//1024}KB)"
    
    skill_dir = skill_path.parent
    skill_name = skill_dir.name
    
    # Parse frontmatter
    if not content.startswith('---'):
        return False, "no frontmatter"
    
    lines = content.split('\n')
    fm_end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            fm_end = i
            break
    if fm_end is None:
        return False, "no closing ---"
    
    frontmatter = '\n'.join(lines[:fm_end+1])
    body_lines = lines[fm_end+1:]
    body = '\n'.join(body_lines)
    
    # Find all H2 sections
    sections = re.split(r'^(## .+)$', body, flags=re.MULTILINE)
    # sections: [text_before_first_h2, h2_title, h2_content, h2_title, h2_content, ...]
    
    # Keep frontmatter + first 2 sections (overview + first detail)
    # Move rest to references
    kept_sections = []
    moved_sections = []
    
    # First element is text before any H2 (usually intro paragraph)
    intro = sections[0].strip()
    if intro:
        kept_sections.append(intro)
    
    # Pair up (title, content)
    pairs = []
    i = 1
    while i < len(sections):
        title = sections[i].strip() if i < len(sections) else ""
        content_block = sections[i+1].strip() if i+1 < len(sections) else ""
        pairs.append((title, content_block))
        i += 2
    
    # Strategy: keep first 3 H2 sections inline, move rest to references
    KEEP = 3
    for idx, (title, block) in enumerate(pairs):
        if idx < KEEP:
            kept_sections.append(f"{title}\n{block}")
        else:
            moved_sections.append((title, block))
    
    if not moved_sections:
        return False, "no sections to move"
    
    # Build new SKILL.md
    new_content = frontmatter + '\n'
    for s in kept_sections:
        new_content += f"\n{s}\n"
    
    # Add see-also pointer
    ref_names = []
    for title, block in moved_sections:
        # Generate safe filename from H2 title
        safe = re.sub(r'[^\w\-]', '', title.lower().replace('## ', '').replace(' ', '-'))
        safe = safe.strip('-')
        if not safe:
            safe = f"section-{len(ref_names)}"
        ref_names.append(safe)
    
    new_content += f"\n## See Also\n\n"
    for name in ref_names:
        filepath = f"references/{name}.md"
        header_name = name.replace('-', ' ').title()
        new_content += f"- `{filepath}` — {header_name}\n"
    
    # Write reference files
    if not dry_run:
        refs_dir = skill_dir / "references"
        refs_dir.mkdir(exist_ok=True)
        
        for (title, block), name in zip(moved_sections, ref_names):
            ref_path = refs_dir / f"{name}.md"
            ref_content = f"# {title.replace('## ', '')}\n\n{block}\n"
            ref_path.write_text(ref_content)
        
        # Write trimmed SKILL.md
        skill_path.write_text(new_content)
    
    moved_kb = sum(len(b.encode('utf-8')) for _, b in moved_sections) // 1024
    new_size = len(new_content.encode('utf-8'))
    
    return True, f"split {len(moved_sections)} sections to references ({moved_kb}KB moved, SKILL.md now {new_size//1024}KB)"


def main():
    dry_run = "--dry-run" in sys.argv
    
    for root, dirs, files in os.walk(SKILLS):
        for f in files:
            if f != 'SKILL.md':
                continue
            path = Path(os.path.join(root, f))
            ok, msg = split_skill(path, dry_run)
            skill = path.parent.name
            if ok:
                prefix = "[DRY RUN] " if dry_run else ""
                print(f"  {prefix}{skill}: {msg}")
            elif "under limit" not in msg:
                print(f"  SKIP {skill}: {msg}")
    
    if dry_run:
        print("\n(dry run — no files written)")


if __name__ == "__main__":
    main()

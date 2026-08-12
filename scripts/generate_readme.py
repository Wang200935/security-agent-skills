#!/usr/bin/env python3
"""
Generate the skill inventory section for README files from catalog.yaml.
Updates the inventory block between <!-- BEGIN INVENTORY --> and <!-- END INVENTORY --> markers.
"""

import yaml, sys, os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CATALOG = REPO / "catalog.yaml"

# Domain display config: (emoji, display_name)
DOMAIN_CONFIG = {
    "recon":               ("🔍", "Recon & OSINT"),
    "web-pentest":         ("🌐", "Web Pentest"),
    "network-pentest":     ("🖥️", "Network Pentest"),
    "exploit-dev":         ("💥", "Exploit Development"),
    "reverse-engineering": ("🔧", "Reverse Engineering"),
    "ctf":                 ("🚩", "CTF"),
    "post-exploitation":   ("🎯", "Post-Exploitation"),
    "cloud-security":      ("☁️", "Cloud & AI Security"),
    "hardware-iot":        ("🔌", "Hardware & IoT"),
    "orchestrator":        ("🧭", "Orchestrator"),
}

# Language config: (readme_file, header_text, total_text)
LANG_CONFIG = {
    "en": ("README.md", "## Skill Categories", "skills"),
    "zh": ("README_zh.md", "## 技能分類", "個技能"),
    "zh_CN": ("README_zh_CN.md", "## 技能分类", "个技能"),
    "ja": ("README_ja.md", "## スキルカテゴリ", "スキル"),
}

def generate_inventory(lang="en"):
    with open(CATALOG) as f:
        catalog = yaml.safe_load(f)
    
    skills = catalog["skills"]
    domain_counts = catalog["domain_counts"]
    
    # Group skills by domain
    by_domain = {}
    for s in skills:
        d = s["domain"]
        if d not in by_domain:
            by_domain[d] = []
        by_domain[d].append(s["id"])
    
    lines = ["<!-- BEGIN INVENTORY -->"]
    
    for domain_key in ["recon", "web-pentest", "network-pentest", "exploit-dev",
                       "reverse-engineering", "ctf", "post-exploitation",
                       "cloud-security", "hardware-iot", "orchestrator"]:
        if domain_key not in by_domain:
            continue
        emoji, display = DOMAIN_CONFIG.get(domain_key, ("", domain_key))
        count = domain_counts.get(domain_key, len(by_domain[domain_key]))
        skill_list = " · ".join(f"`{s}`" for s in by_domain[domain_key])
        lines.append(f"### {emoji} {display} ({count} {LANG_CONFIG[lang][1]})")
        lines.append(skill_list)
        lines.append("")
    
    total = catalog["total_skills"]
    lines.append(f"**Total: {total} skills** (+ 1 orchestrator)")
    lines.append("<!-- END INVENTORY -->")
    
    return "\n".join(lines)


def update_readme(lang="en"):
    readme_file, header, unit = LANG_CONFIG[lang]
    readme_path = REPO / readme_file
    
    if not readme_path.exists():
        print(f"  skip {readme_file} (not found)")
        return False
    
    content = readme_path.read_text()
    inventory = generate_inventory(lang)
    
    # Replace between markers, or after header if no markers
    if "<!-- BEGIN INVENTORY -->" in content:
        parts = content.split("<!-- BEGIN INVENTORY -->")
        before = parts[0]
        after = parts[1].split("<!-- END INVENTORY -->", 1)[-1] if len(parts) > 1 else ""
        new_content = before + inventory + after
    else:
        # Insert after header
        if header in content:
            idx = content.index(header)
            # Find next ## or end
            after_header = content[idx:]
            next_section = after_header.find("\n## ", 1)
            if next_section == -1:
                next_section = len(after_header)
            before = content[:idx]
            after = after_header[next_section:]
            new_content = before + inventory + "\n" + after
        else:
            # Append at end
            new_content = content + "\n" + inventory + "\n"
    
    readme_path.write_text(new_content)
    print(f"  updated {readme_file}")
    return True


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    if lang == "all":
        for l in LANG_CONFIG:
            update_readme(l)
    else:
        update_readme(lang)

#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$SCRIPT_DIR}"
SOURCE_SKILLS_DIR="$REPO_ROOT/skills"

# Validate a skill name matches Agent Skills name grammar:
# lowercase alphanumeric + hyphens, no leading/trailing hyphen, no consecutive --
validate_skill_name() {
  local name="$1"
  [[ -z "$name" ]] && return 1
  # No path components, no .., no /
  [[ "$name" == */* ]] && return 1
  [[ "$name" == ".." ]] && return 1
  # Must match [a-z][a-z0-9-]*[a-z0-9] with no trailing/leading/double hyphens
  [[ "$name" =~ ^[a-z][a-z0-9-]*[a-z0-9]$ ]] || return 1
  [[ "$name" == *"--"* ]] && return 1
  [[ "$name" == -* ]] && return 1
  [[ "$name" == *- ]] && return 1
  return 0
}

canonical_path() {
  python3 - "$1" <<'PY'
import os, sys
print(os.path.realpath(sys.argv[1]))
PY
}

MODE="symlink"           # symlink | copy
CLAUDE_SCOPE="project"   # project | global
FORCE=0
DRY_RUN=0
NON_INTERACTIVE=0
SHOW_LIST=0
INSTALL_ALL=0
FILTER_DOMAIN=""
FILTER_SKILL=""

REQUESTED_AGENTS=()

AGENT_KEYS=(
  "claude-code"
  "codex"
  "cursor"
  "gemini-cli"
  "windsurf"
  "github-copilot"
  "openclaw"
  "hermes-agent"
)

agent_label() {
  case "$1" in
    claude-code) echo "Claude Code" ;;
    codex) echo "Codex" ;;
    cursor) echo "Cursor" ;;
    gemini-cli) echo "Gemini CLI" ;;
    windsurf) echo "Windsurf" ;;
    github-copilot) echo "GitHub Copilot" ;;
    openclaw) echo "OpenClaw" ;;
    hermes-agent) echo "Hermes Agent" ;;
    *) echo "$1" ;;
  esac
}

normalize_agent() {
  case "${1,,}" in
    claude|claude-code) echo "claude-code" ;;
    codex) echo "codex" ;;
    cursor) echo "cursor" ;;
    gemini|gemini-cli) echo "gemini-cli" ;;
    windsurf) echo "windsurf" ;;
    copilot|github-copilot) echo "github-copilot" ;;
    openclaw) echo "openclaw" ;;
    hermes|hermes-agent) echo "hermes-agent" ;;
    *) return 1 ;;
  esac
}

skills_root_for_claude() {
  if [[ "$CLAUDE_SCOPE" == "global" ]]; then
    printf '%s\n' "$HOME/.claude/skills"
  else
    printf '%s\n' "$REPO_ROOT/.claude/skills"
  fi
}

skills_root_for_agent() {
  case "$1" in
    claude-code) skills_root_for_claude ;;
    codex) printf '%s\n' "$REPO_ROOT/.agents/skills" ;;
    cursor) printf '%s\n' "$REPO_ROOT/.cursor/skills" ;;
    gemini-cli) printf '%s\n' "$REPO_ROOT/.gemini/skills" ;;
    windsurf) printf '%s\n' "$REPO_ROOT/.windsurf/skills" ;;
    openclaw) printf '%s\n' "$REPO_ROOT/.agents/skills" ;;
    hermes-agent) printf '%s\n' "$HOME/.hermes/skills" ;;
    github-copilot) printf '%s\n' "$REPO_ROOT/.github/copilot-instructions.md" ;;
    *) return 1 ;;
  esac
}

is_interactive() {
  [[ -t 0 && -t 1 && $NON_INTERACTIVE -eq 0 ]]
}

# Check if a path has existing real content (not just empty dir)
has_existing_content() {
  local path="$1"
  if [[ -L "$path" ]]; then
    return 0
  fi
  if [[ -f "$path" ]]; then
    return 0
  fi
  if [[ -d "$path" ]]; then
    local count
    count=$(find "$path" -maxdepth 1 -mindepth 1 2>/dev/null | wc -l | tr -d ' ')
    [[ "$count" -gt 0 ]]
    return $?
  fi
  return 1
}

# Is a skill managed by us? Check if this specific skill is listed in the manifest.
# Usage: is_managed_by_us <skill_name_or_path> <dest_root>
# If first arg is a skill name, grep for it in the manifest.
# If first arg == dest_root, just check manifest existence (for root-level checks).
is_managed_by_us() {
  local arg="$1"
  local dest_root="${2:-$arg}"
  local manifest="${dest_root}/.security-agent-skills-manifest"
  [[ -f "$manifest" ]] || return 1
  # If arg is the same as dest_root, we're checking the root itself
  if [[ "$arg" == "$dest_root" ]]; then
    return 0
  fi
  # Extract skill name: if arg is a path, basename it; otherwise use as-is
  local skill_name
  skill_name="$(basename "$arg")"
  # Check if this specific skill is listed in the manifest
  grep -Fxq "$skill_name" "$manifest"
}

# Timestamped backup
backup_path() {
  local path="$1"
  if [[ ! -e "$path" && ! -L "$path" ]]; then
    return 0
  fi
  local backup
  backup="${path}.backup-$(date +%Y%m%d-%H%M%S)"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would backup $path -> $backup"
  else
    mv "$path" "$backup"
    echo "[backup] $path -> $backup"
  fi
}

confirm_overwrite() {
  local path="$1"
  local label="$2"

  if [[ ! -e "$path" && ! -L "$path" ]]; then
    return 0
  fi

  if [[ $FORCE -eq 1 ]]; then
    return 0
  fi

  if [[ $NON_INTERACTIVE -eq 1 ]]; then
    echo "[skip] $label — existing data at $path (use --force to overwrite)"
    return 1
  fi

  local reply
  read -r -p "Overwrite $label at $path? [y/N] " reply
  [[ "${reply,,}" == "y" || "${reply,,}" == "yes" ]]
}

# Append skill to manifest with dedup (e4 fix)
manifest_add() {
  local dest_root="$1"
  local skill_name="$2"
  local manifest="${dest_root}/.security-agent-skills-manifest"

  # Dedup: skip if already in manifest
  if [[ -f "$manifest" ]] && grep -Fxq "$skill_name" "$manifest"; then
    return 0
  fi
  echo "$skill_name" >> "$manifest"
}

# Install a single skill directory into dest root, additively.
# Returns: 0=installed/updated, 1=error, 2=skipped
# Usage: install_single_skill <source_skill_dir> <dest_root> <skill_name>
install_single_skill() {
  local src="$1"
  local dest_root="$2"
  local skill_name="$3"
  local dest="$dest_root/$skill_name"

  if [[ ! -d "$src" ]]; then
    echo "[error] Source skill not found: $src" >&2
    return 1
  fi

  # If dest exists and is managed by us, replace OK
  # If dest exists and is NOT managed by us:
  #   --force: backup + replace
  #   else: skip with warning
  if has_existing_content "$dest"; then
    if is_managed_by_us "$skill_name" "$dest_root"; then
      # Our own previous install — safe to replace
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "[dry-run] Would update managed skill: $skill_name"
      else
        rm -rf "$dest"
      fi
    elif [[ $FORCE -eq 1 ]]; then
      backup_path "$dest"
      if [[ $DRY_RUN -eq 0 ]]; then
        rm -rf "$dest"
      fi
    elif [[ $NON_INTERACTIVE -eq 1 ]]; then
      echo "[skip] $skill_name — existing non-managed data at $dest (use --force)"
      return 2
    else
      local reply
      read -r -p "Skill '$skill_name' already exists at $dest (not ours). Overwrite? [y/N] " reply
      if [[ "${reply,,}" != "y" && "${reply,,}" != "yes" ]]; then
        echo "[skip] $skill_name"
        return 2
      fi
      backup_path "$dest"
      if [[ $DRY_RUN -eq 0 ]]; then
        rm -rf "$dest"
      fi
    fi
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would install skill: $skill_name -> $dest ($MODE)"
    return 0
  fi

  mkdir -p "$dest_root"

  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$src" "$dest"
  else
    if command -v rsync >/dev/null 2>&1; then
      rsync -a "$src/" "$dest/"
    else
      cp -R "$src" "$dest"
    fi
  fi

  # Write manifest marker with dedup (e4 fix)
  manifest_add "$dest_root" "$skill_name"
  return 0
}

# Enumerate all skill directories — handles both skills/<category>/<skill>/ and skills/<skill>/
# Echoes absolute paths, one per line.
# Respects FILTER_DOMAIN and FILTER_SKILL if set.
enumerate_skills() {
  shopt -s nullglob
  # First: top-level skills (skills/<skill>/SKILL.md)
  for skill_dir in "$SOURCE_SKILLS_DIR"/*/; do
    [[ -d "$skill_dir" ]] || continue
    if [[ -f "$skill_dir/SKILL.md" ]]; then
      _emit_if_filtered "$skill_dir" ""
    fi
  done
  # Second: nested skills (skills/<category>/<skill>/SKILL.md)
  for category_dir in "$SOURCE_SKILLS_DIR"/*/; do
    [[ -d "$category_dir" ]] || continue
    # Skip if category_dir itself is a skill (already handled above)
    [[ -f "$category_dir/SKILL.md" ]] && continue
    local category_name
    category_name="$(basename "$category_dir")"
    # Domain filter: skip entire category if it doesn't match
    if [[ -n "$FILTER_DOMAIN" && "$category_name" != "$FILTER_DOMAIN" ]]; then
      continue
    fi
    for skill_dir in "$category_dir"*/; do
      [[ -d "$skill_dir" ]] || continue
      _emit_if_filtered "$skill_dir" "$category_name"
    done
  done
  shopt -u nullglob
}

# Helper: echo skill_dir if it passes the skill + domain filters
_emit_if_filtered() {
  local skill_dir="$1"
  local category_name="$2"
  local skill_name
  skill_name="$(basename "$skill_dir")"

  # Skill filter: exact match
  if [[ -n "$FILTER_SKILL" ]]; then
    if [[ "$skill_name" != "$FILTER_SKILL" ]]; then
      return
    fi
  fi

  # Domain filter: must match the category directory name.
  # For top-level skills (category_name=""), only include if:
  #   - no domain filter is set (show everything), OR
  #   - the skill's own directory name matches FILTER_DOMAIN (e.g. --domain security-orchestrator)
  if [[ -n "$FILTER_DOMAIN" ]]; then
    if [[ "$category_name" != "$FILTER_DOMAIN" && "$skill_name" != "$FILTER_DOMAIN" ]]; then
      return
    fi
  fi

  echo "${skill_dir}"
}

# Install all skills additively into dest root
install_skills_additive() {
  local dest_root="$1"
  local label="$2"

  if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
    echo "[error] Skills source directory not found: $SOURCE_SKILLS_DIR" >&2
    exit 1
  fi

  # Check if dest_root itself exists with non-managed content
  if has_existing_content "$dest_root" && ! is_managed_by_us "$dest_root" "$dest_root"; then
    if [[ $FORCE -eq 1 ]]; then
      echo "[warn] $label: destination has existing non-managed content. --force will backup conflicts per-skill, not nuke the root."
    elif [[ $NON_INTERACTIVE -eq 1 ]]; then
      echo "[warn] $label: destination $dest_root has existing content. Installing additively (existing skills will be skipped unless --force)."
    fi
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would install skills additively to: $dest_root ($MODE)"
  fi

  mkdir -p "$dest_root" 2>/dev/null || true

  local installed=0
  local skipped=0
  local total=0

  while IFS= read -r skill_dir; do
    local skill_name
    skill_name="$(basename "$skill_dir")"
    total=$((total + 1))
    set +e
    install_single_skill "$skill_dir" "$dest_root" "$skill_name"
    local rc=$?
    set -e
    if [[ $rc -eq 0 ]]; then
      installed=$((installed + 1))
    elif [[ $rc -eq 2 ]]; then
      skipped=$((skipped + 1))
    else
      echo "[error] Failed to install $skill_name (rc=$rc)" >&2
      skipped=$((skipped + 1))
    fi
  done < <(enumerate_skills)

  if [[ $DRY_RUN -eq 0 ]]; then
    echo "[ok] $label: $installed installed, $skipped skipped, $total total"
  fi
}

# Gemini-specific: flatten to single level (no category nesting)
install_skills_gemini() {
  local dest_root="$1"
  local label="$2"

  if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
    echo "[error] Skills source directory not found: $SOURCE_SKILLS_DIR" >&2
    exit 1
  fi

  # Gemini discovers skills at <root>/<skill-name>/SKILL.md — one level deep.
  # Our source tree has skills/<category>/<skill-name>/SKILL.md — two levels.
  # So we must flatten: install each skill directly under dest_root/<skill-name>/.

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would install Gemini-flattened skills to: $dest_root"
  fi

  mkdir -p "$dest_root" 2>/dev/null || true

  local installed=0
  local skipped=0
  local total=0

  while IFS= read -r skill_dir; do
    local skill_name
    skill_name="$(basename "$skill_dir")"
    total=$((total + 1))

    local dest="$dest_root/$skill_name"

    if has_existing_content "$dest"; then
      if is_managed_by_us "$skill_name" "$dest_root"; then
        if [[ $DRY_RUN -eq 0 ]]; then rm -rf "$dest"; fi
      elif [[ $FORCE -eq 1 ]]; then
        backup_path "$dest"
        if [[ $DRY_RUN -eq 0 ]]; then rm -rf "$dest"; fi
      elif [[ $NON_INTERACTIVE -eq 1 ]]; then
        echo "[skip] $skill_name (Gemini) — existing at $dest"
        skipped=$((skipped + 1))
        continue
      else
        local reply
        read -r -p "Skill '$skill_name' exists at $dest (Gemini). Overwrite? [y/N] " reply
        if [[ "${reply,,}" != "y" && "${reply,,}" != "yes" ]]; then
          echo "[skip] $skill_name (Gemini)"
          skipped=$((skipped + 1))
          continue
        fi
        backup_path "$dest"
        if [[ $DRY_RUN -eq 0 ]]; then rm -rf "$dest"; fi
      fi
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
      echo "[dry-run] Would install (flattened): $skill_name -> $dest"
    else
      if [[ "$MODE" == "symlink" ]]; then
        ln -s "$skill_dir" "$dest"
      else
        if command -v rsync >/dev/null 2>&1; then
          rsync -a "$skill_dir/" "$dest/"
        else
          cp -R "$skill_dir" "$dest"
        fi
      fi
      # Append to manifest for uninstall tracking (with dedup)
      manifest_add "$dest_root" "$skill_name"
    fi
    installed=$((installed + 1))
  done < <(enumerate_skills)

  if [[ $DRY_RUN -eq 0 ]]; then
    echo "[ok] $label (Gemini flattened): $installed installed, $skipped skipped, $total total"
  fi
}

install_copilot_instructions() {
  local dest="$1"
  local label="GitHub Copilot instructions"

  if [[ -f "$dest" ]]; then
    if [[ $FORCE -eq 1 ]]; then
      backup_path "$dest"
    elif [[ $NON_INTERACTIVE -eq 1 ]]; then
      echo "[skip] $label — existing file at $dest (use --force)"
      return 0
    else
      local reply
      read -r -p "Overwrite $label at $dest? [y/N] " reply
      if [[ "${reply,,}" != "y" && "${reply,,}" != "yes" ]]; then
        echo "[skip] $label"
        return 0
      fi
      backup_path "$dest"
    fi
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] Would write: $dest"
    return 0
  fi

  mkdir -p "$(dirname "$dest")"
  cat > "$dest" <<'EOF'
# Security Agent Skills for GitHub Copilot

This repository contains a curated security skill library under:

- `./skills/recon/`
- `./skills/web-pentest/`
- `./skills/network-pentest/`
- `./skills/exploit-dev/`
- `./skills/reverse-engineering/`
- `./skills/ctf/`
- `./skills/post-exploitation/`
- `./skills/cloud-security/`
- `./skills/hardware-iot/`

When working on a security-related task in this repo:
1. Find the most relevant skill category.
2. Open the matching `SKILL.md` before editing or suggesting changes.
3. Follow any linked references, scripts, or validation steps in that skill.
4. Prefer the repo-local skill documentation over generic heuristics.

For native Copilot Agent Skills, skills are also installed to `.agents/skills/`.
EOF
  echo "[ok] $label -> wrote $dest"
}

install_agent() {
  local agent="$1"
  local label
  label="$(agent_label "$agent")"
  local target
  target="$(skills_root_for_agent "$agent")"

  case "$agent" in
    github-copilot)
      install_copilot_instructions "$target"
      # Also install native skills to .agents/skills
      local agents_target="$REPO_ROOT/.agents/skills"
      install_skills_additive "$agents_target" "$label (native skills)"
      ;;
    gemini-cli)
      # Gemini requires flattened single-level layout for discovery
      install_skills_gemini "$target" "$label"
      ;;
    claude-code|codex|cursor|windsurf|openclaw|hermes-agent)
      install_skills_additive "$target" "$label"
      ;;
    *)
      echo "[error] Unknown agent: $agent" >&2
      exit 1
      ;;
  esac
}

list_skills() {
  if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
    echo "[error] Skills source directory not found: $SOURCE_SKILLS_DIR" >&2
    exit 1
  fi

  local total=0
  echo "Available skills in $SOURCE_SKILLS_DIR"
  echo

  # Group by category for readability
  declare -A cat_skills
  declare -a cat_order

  shopt -s nullglob
  # Top-level skills (no category)
  local top_level=()
  for skill_dir in "$SOURCE_SKILLS_DIR"/*/; do
    [[ -d "$skill_dir" ]] || continue
    if [[ -f "$skill_dir/SKILL.md" ]]; then
      top_level+=("$(basename "$skill_dir")")
      total=$((total + 1))
    fi
  done
  # Nested skills
  for category_dir in "$SOURCE_SKILLS_DIR"/*/; do
    [[ -d "$category_dir" ]] || continue
    [[ -f "$category_dir/SKILL.md" ]] && continue  # skip top-level skills
    local category
    category="$(basename "$category_dir")"
    cat_order+=("$category")
    local -a slist=()
    for skill_dir in "$category_dir"*/; do
      [[ -d "$skill_dir" ]] || continue
      slist+=("$(basename "$skill_dir")")
      total=$((total + 1))
    done
    cat_skills["$category"]="${slist[*]}"
  done
  shopt -u nullglob

  # Print top-level skills first
  if [[ ${#top_level[@]} -gt 0 ]]; then
    printf '%s\n' "[standalone]"
    for name in "${top_level[@]}"; do
      printf '  - %s\n' "$name"
    done
    printf '  (%d skills)\n\n' "${#top_level[@]}"
  fi

  # Print categorized skills
  for category in "${cat_order[@]}"; do
    printf '%s\n' "[$category]"
    local count=0
    for name in ${cat_skills[$category]}; do
      printf '  - %s\n' "$name"
      count=$((count + 1))
    done
    printf '  (%d skills)\n\n' "$count"
  done

  echo "Total: $total skills"
}

uninstall_agent() {
  local agent="$1"
  local label
  label="$(agent_label "$agent")"
  local target
  target="$(skills_root_for_agent "$agent")"

  # GitHub Copilot has two install targets: instruction file + .agents/skills/
  if [[ "$agent" == "github-copilot" ]]; then
    local removed=0
    # Remove instruction file
    if [[ -f "$target" ]]; then
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "[dry-run] Would remove: $target"
      else
        backup_path "$target"
      fi
      removed=$((removed + 1))
    fi
    # Remove native skills from .agents/skills/
    local agents_target="$REPO_ROOT/.agents/skills"
    local agents_manifest="${agents_target}/.security-agent-skills-manifest"
    if [[ -f "$agents_manifest" ]]; then
      local removed=0
      local skipped_invalid=0
      while IFS= read -r skill_name; do
        # e1 fix: validate manifest entry
        if ! validate_skill_name "$skill_name"; then
          echo "[warn] Skipping invalid manifest entry: '$skill_name'" >&2
          skipped_invalid=$((skipped_invalid + 1))
          continue
        fi
        local skill_path="$agents_target/$skill_name"
        # e1 fix: canonical path containment
        local canonical_target
        canonical_target="$(canonical_path "$agents_target")"
        local canonical_skill_path
        canonical_skill_path="$(canonical_path "$skill_path")"
        if [[ "$canonical_skill_path" != "$canonical_target"/* ]]; then
          echo "[warn] Skipping '$skill_name': resolves outside target" >&2
          skipped_invalid=$((skipped_invalid + 1))
          continue
        fi
        if [[ -e "$skill_path" || -L "$skill_path" ]]; then
          if [[ $DRY_RUN -eq 1 ]]; then
            echo "[dry-run] Would remove: $skill_path"
          else
            rm -f "$skill_path"
            rm -rf "$skill_path"
          fi
          removed=$((removed + 1))
        fi
      done < "$agents_manifest"
      if [[ $DRY_RUN -eq 0 ]]; then
        rm -f "$agents_manifest"
      fi
    elif [[ $FORCE -eq 1 ]] && [[ -d "$agents_target" ]]; then
      backup_path "$agents_target"
      removed=$((removed + 1))
    fi
    echo "[ok] $label: $removed items removed"
    return 0
  fi

  if [[ ! -d "$target" ]]; then
    echo "[skip] $label — nothing installed at $target"
    return 0
  fi

  local manifest="${target}/.security-agent-skills-manifest"

  if [[ ! -f "$manifest" ]]; then
    echo "[skip] $label — $target is not managed by security-agent-skills (no manifest). Use --force to remove anyway."
    if [[ $FORCE -eq 1 ]]; then
      backup_path "$target"
      echo "[ok] Removed $label (forced)"
    fi
    return 0
  fi

  # Read manifest and remove only our skills
  local removed=0
  local skipped_invalid=0
  while IFS= read -r skill_name; do
    # e1 fix: validate manifest entry against Agent Skills name grammar
    if ! validate_skill_name "$skill_name"; then
      echo "[warn] Skipping invalid manifest entry: '$skill_name' (not a valid skill ID)" >&2
      skipped_invalid=$((skipped_invalid + 1))
      continue
    fi
    # e1 fix: resolve canonical path and assert it's a child of target
    local skill_path="$target/$skill_name"
    local canonical_target
    canonical_target="$(canonical_path "$target")"
    local canonical_skill_path
    canonical_skill_path="$(canonical_path "$skill_path")"
    # Containment check: resolved path must start with target
    if [[ "$canonical_skill_path" != "$canonical_target"/* ]]; then
      echo "[warn] Skipping '$skill_name': resolves outside target directory" >&2
      skipped_invalid=$((skipped_invalid + 1))
      continue
    fi
    if [[ -e "$skill_path" || -L "$skill_path" ]]; then
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "[dry-run] Would remove: $skill_path"
      else
        rm -f "$skill_path"
        rm -rf "$skill_path"
      fi
      removed=$((removed + 1))
    fi
  done < "$manifest"

  # Remove manifest itself
  if [[ $DRY_RUN -eq 0 ]]; then
    rm -f "$manifest"
  fi

  echo "[ok] $label: $removed skills removed from $target"
}

usage() {
  cat <<EOF
Usage:
  $0                     # interactive menu
  $0 --list              # list available skills
  $0 --agent NAME        # install one agent (repeatable)
  $0 --all               # install every supported agent
  $0 --uninstall NAME    # remove skills installed by this tool

Options:
  --agent NAME           Agent to install (repeatable)
                         claude-code | codex | cursor | gemini-cli | windsurf | github-copilot | openclaw | hermes-agent
  --domain DOMAIN        Only install skills from the given domain (e.g. ctf, web-pentest)
  --skill SKILL_ID       Only install a single skill by its ID
  --all                  Install to every supported agent (fixed list above)
  --list                 Show available skills by category
  --copy                 Copy the skills directory instead of symlinking
  --symlink              Symlink the skills directory (default)
  --global               Install Claude Code skills to ~/.claude/skills
  --force                Overwrite existing non-managed skills (backs up first)
  --dry-run              Show what would happen without making changes
  --uninstall NAME       Remove skills installed by this tool for the given agent
  -h, --help             Show this help

Safety:
  This installer is ADDITIVE. It never deletes an agent's entire skills directory.
  Each skill is installed individually. Existing skills not managed by this tool
  are left alone unless --force is given (a .backup-<timestamp> is created first).

  A manifest file (.security-agent-skills-manifest) tracks which skills this
  tool installed, enabling clean --uninstall. The manifest stores one skill ID
  per line — a skill is only treated as "managed" if its ID appears in the manifest.

  Gemini CLI: skills are flattened to a single-level directory for proper
  discovery (Gemini only discovers skills one level deep).

  GitHub Copilot: writes copilot-instructions.md AND installs native Agent
  Skills to .agents/skills/.
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agent)
        [[ $# -ge 2 ]] || { echo "[error] --agent requires a value" >&2; exit 1; }
        REQUESTED_AGENTS+=("$(normalize_agent "$2")")
        shift 2
        ;;
      --all)
        INSTALL_ALL=1
        shift
        ;;
      --list)
        SHOW_LIST=1
        shift
        ;;
      --domain)
        [[ $# -ge 2 ]] || { echo "[error] --domain requires a value" >&2; exit 1; }
        FILTER_DOMAIN="$2"
        shift 2
        ;;
      --skill)
        [[ $# -ge 2 ]] || { echo "[error] --skill requires a value" >&2; exit 1; }
        FILTER_SKILL="$2"
        shift 2
        ;;
      --copy)
        MODE="copy"
        shift
        ;;
      --symlink)
        MODE="symlink"
        shift
        ;;
      --global)
        CLAUDE_SCOPE="global"
        shift
        ;;
      --force)
        FORCE=1
        shift
        ;;
      --dry-run)
        DRY_RUN=1
        shift
        ;;
      --non-interactive)
        NON_INTERACTIVE=1
        shift
        ;;
      --uninstall)
        [[ $# -ge 2 ]] || { echo "[error] --uninstall requires a value" >&2; exit 1; }
        UNINSTALL_AGENT="$(normalize_agent "$2")"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "[error] Unknown argument: $1" >&2
        usage >&2
        exit 1
        ;;
    esac
  done
}

interactive_menu() {
  while true; do
    echo "Install for which agent?"
    echo "  1) Claude Code"
    echo "  2) Codex"
    echo "  3) Cursor"
    echo "  4) Gemini CLI"
    echo "  5) Windsurf"
    echo "  6) GitHub Copilot"
    echo "  7) OpenClaw"
    echo "  8) Hermes Agent"
    echo "  9) All"
    echo "  u) Uninstall"
    echo "  0) Exit"
    printf 'Select an option: '
    local choice
    read -r choice
    case "$choice" in
      1) install_agent "claude-code" ;;
      2) install_agent "codex" ;;
      3) install_agent "cursor" ;;
      4) install_agent "gemini-cli" ;;
      5) install_agent "windsurf" ;;
      6) install_agent "github-copilot" ;;
      7) install_agent "openclaw" ;;
      8) install_agent "hermes-agent" ;;
      9) for agent in "${AGENT_KEYS[@]}"; do install_agent "$agent"; done ;;
      u)
        printf 'Agent to uninstall: '
        local agent_name
        read -r agent_name
        local normalized
        normalized="$(normalize_agent "$agent_name" 2>/dev/null || true)"
        if [[ -z "$normalized" ]]; then
          echo "Unknown agent: $agent_name"
        else
          uninstall_agent "$normalized"
        fi
        ;;
      0) exit 0 ;;
      *) echo "Invalid choice: $choice" ;;
    esac
    echo
  done
}

main() {
  parse_args "$@"

  if [[ $SHOW_LIST -eq 1 ]]; then
    list_skills
    exit 0
  fi

  if [[ ${UNINSTALL_AGENT+x} ]]; then
    uninstall_agent "$UNINSTALL_AGENT"
    exit 0
  fi

  if [[ $INSTALL_ALL -eq 1 ]]; then
    for agent in "${AGENT_KEYS[@]}"; do
      install_agent "$agent"
    done
    exit 0
  fi

  if [[ ${#REQUESTED_AGENTS[@]} -gt 0 ]]; then
    for agent in "${REQUESTED_AGENTS[@]}"; do
      install_agent "$agent"
    done
    exit 0
  fi

  if is_interactive; then
    interactive_menu
  else
    usage >&2
    exit 1
  fi
}

main "$@"

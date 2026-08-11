#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$SCRIPT_DIR}"
SOURCE_SKILLS_DIR="$REPO_ROOT/skills"

MODE="symlink"           # symlink | copy
CLAUDE_SCOPE="project"   # project | global
FORCE=0
NON_INTERACTIVE=0
SHOW_LIST=0
INSTALL_ALL=0

# Parsed agent requests. Values are normalized agent keys.
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
    codex) printf '%s\n' "$REPO_ROOT/.codex/skills" ;;
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

warn_existing() {
  local path="$1"
  local label="$2"
  if [[ -e "$path" || -L "$path" ]]; then
    if [[ -L "$path" ]]; then
      local current
      current="$(readlink "$path" || true)"
      echo "[warn] $label already exists as symlink: $path -> $current"
    else
      echo "[warn] $label already exists: $path"
    fi
  fi
}

confirm_overwrite() {
  local path="$1"
  local label="$2"
  if [[ ! -e "$path" && ! -L "$path" ]]; then
    return 0
  fi

  warn_existing "$path" "$label"

  if [[ $FORCE -eq 1 || $NON_INTERACTIVE -eq 1 ]]; then
    return 0
  fi

  local reply
  read -r -p "Overwrite $label at $path? [y/N] " reply
  [[ "${reply,,}" == "y" || "${reply,,}" == "yes" ]]
}

remove_path() {
  local path="$1"
  if [[ -L "$path" || -f "$path" ]]; then
    rm -f "$path"
  elif [[ -d "$path" ]]; then
    rm -rf "$path"
  fi
}

install_skills_tree() {
  local dest="$1"
  local label="$2"

  if [[ ! -d "$SOURCE_SKILLS_DIR" ]]; then
    echo "[error] Skills source directory not found: $SOURCE_SKILLS_DIR" >&2
    exit 1
  fi

  if ! confirm_overwrite "$dest" "$label"; then
    echo "[skip] $label"
    return 0
  fi

  mkdir -p "$(dirname "$dest")"

  if [[ "$MODE" == "symlink" ]]; then
    remove_path "$dest"
    ln -s "$SOURCE_SKILLS_DIR" "$dest"
    echo "[ok] $label -> symlinked $dest -> $SOURCE_SKILLS_DIR"
  else
    mkdir -p "$dest"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete "$SOURCE_SKILLS_DIR/" "$dest/"
    else
      rm -rf "$dest"
      mkdir -p "$(dirname "$dest")"
      cp -R "$SOURCE_SKILLS_DIR" "$dest"
    fi
    echo "[ok] $label -> copied to $dest"
  fi
}

install_copilot_instructions() {
  local dest="$1"
  local label="GitHub Copilot instructions"

  if ! confirm_overwrite "$dest" "$label"; then
    echo "[skip] $label"
    return 0
  fi

  mkdir -p "$(dirname "$dest")"
  cat > "$dest" <<EOF
# Security Agent Skills for GitHub Copilot

This repository contains a curated security skill library under:

- \\`./skills/recon/\\`
- \\`./skills/web-pentest/\\`
- \\`./skills/network-pentest/\\`
- \\`./skills/exploit-dev/\\`
- \\`./skills/reverse-engineering/\\`
- \\`./skills/ctf/\\`
- \\`./skills/post-exploitation/\\`
- \\`./skills/cloud-security/\\`
- \\`./skills/hardware-iot/\\`

When working on a security-related task in this repo:
1. Find the most relevant skill category.
2. Open the matching \\`SKILL.md\\` before editing or suggesting changes.
3. Follow any linked references, scripts, or validation steps in that skill.
4. Prefer the repo-local skill documentation over generic heuristics.

Skills root: \\`$REPO_ROOT/skills\\`
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
      ;;
    claude-code)
      install_skills_tree "$target" "$label"
      ;;
    codex|cursor|gemini-cli|windsurf|openclaw|hermes-agent)
      install_skills_tree "$target" "$label"
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

  shopt -s nullglob
  for category_dir in "$SOURCE_SKILLS_DIR"/*/; do
    [[ -d "$category_dir" ]] || continue
    local category
    category="$(basename "$category_dir")"
    local -a skills=("$category_dir"*/)
    local count=0
    printf '%s\n' "[$category]"
    for skill_dir in "${skills[@]}"; do
      [[ -d "$skill_dir" ]] || continue
      local skill_name
      skill_name="$(basename "$skill_dir")"
      printf '  - %s\n' "$skill_name"
      count=$((count + 1))
      total=$((total + 1))
    done
    printf '  (%d skills)\n\n' "$count"
  done
  shopt -u nullglob

  echo "Total: $total skills"
}

usage() {
  cat <<EOF
Usage:
  $0                     # interactive menu
  $0 --list              # list available skills
  $0 --agent NAME        # install one agent non-interactively
  $0 --all               # install every supported agent

Options:
  --agent NAME           Agent to install (repeatable)
                         claude-code | codex | cursor | gemini-cli | windsurf | github-copilot | openclaw | hermes-agent
  --all                  Install every supported agent
  --list                 Show available skills by category
  --copy                 Copy the skills directory instead of symlinking it
  --symlink              Symlink the skills directory (default)
  --global               Install Claude Code skills to ~/.claude/skills instead of repo-local .claude/skills
  --force                Overwrite existing installs without prompting
  -h, --help             Show this help
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

  if [[ $INSTALL_ALL -eq 1 ]]; then
    NON_INTERACTIVE=1
    for agent in "${AGENT_KEYS[@]}"; do
      install_agent "$agent"
    done
    exit 0
  fi

  if [[ ${#REQUESTED_AGENTS[@]} -gt 0 ]]; then
    NON_INTERACTIVE=1
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

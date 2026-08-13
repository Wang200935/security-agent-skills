#!/usr/bin/env bash
# build.sh — Generate platform-specific dist/ output from skills/ source tree.
# Run from repo root: ./build.sh [all|gemini|copilot|cursor|claude-code|codex|hermes|windsurf|openclaw]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
SKILLS_SRC="$REPO_ROOT/skills"
DIST="$REPO_ROOT/dist"

TARGET="${1:-all}"

# Collect all skill directories (2-level: skills/<category>/<skill>/)
SKILL_DIRS=()
for cat_dir in "$SKILLS_SRC"/*/; do
    [ -d "$cat_dir" ] || continue
    if [ -f "$cat_dir/SKILL.md" ]; then
        # Top-level skill (e.g. security-orchestrator)
        SKILL_DIRS+=("$cat_dir")
    fi
    for skill_dir in "$cat_dir"*/; do
        [ -d "$skill_dir" ] || continue
        if [ -f "$skill_dir/SKILL.md" ]; then
            SKILL_DIRS+=("$skill_dir")
        fi
    done
done

DIST_DIR="$DIST"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

build_flattened() {
    local dest="$1"
    local ext="$2"  # "" for dir format, ".mdc" or ".md" for flat file
    mkdir -p "$dest"
    
    for skill_dir in "${SKILL_DIRS[@]}"; do
        local name
        name="$(basename "$skill_dir")"
        if [ -n "$ext" ]; then
            # Flat file format (cursor, windsurf)
            cp "$skill_dir/SKILL.md" "$dest/${name}${ext}"
        else
            # Directory format (gemini, copilot, claude, codex)
            mkdir -p "$dest/$name"
            cp "$skill_dir/SKILL.md" "$dest/$name/"
            [ -d "$skill_dir/references" ] && cp -r "$skill_dir/references" "$dest/$name/"
            [ -d "$skill_dir/scripts" ] && cp -r "$skill_dir/scripts" "$dest/$name/"
        fi
    done
    echo "Built $(find "$dest" -name 'SKILL.md' -o -name '*.mdc' -o -name '*.md' | wc -l | tr -d ' ') items"
}

build_gemini() {
    echo -n "  gemini: "
    build_flattened "$DIST_DIR/gemini/.gemini/skills" ""
}

build_copilot() {
    echo -n "  copilot: "
    build_flattened "$DIST_DIR/copilot/.agents/skills" ""
}

build_cursor() {
    echo -n "  cursor: "
    build_flattened "$DIST_DIR/cursor/.cursor/rules" ".mdc"
}

build_claude() {
    echo -n "  claude-code: "
    build_flattened "$DIST_DIR/claude-code/.claude/skills" ""
}

build_codex() {
    echo -n "  codex: "
    mkdir -p "$DIST_DIR/codex"
    [ -f "$REPO_ROOT/AGENTS.md" ] && cp "$REPO_ROOT/AGENTS.md" "$DIST_DIR/codex/"
    build_flattened "$DIST_DIR/codex/.agents/skills" ""
}

build_hermes() {
    echo -n "  hermes: "
    # Hermes preserves category hierarchy
    local out="$DIST_DIR/hermes/.hermes/skills"
    mkdir -p "$out"
    cp -r "$SKILLS_SRC"/* "$out/"
    echo "$(find "$out" -name 'SKILL.md' | wc -l | tr -d ' ') skills"
}

build_windsurf() {
    echo -n "  windsurf: "
    build_flattened "$DIST_DIR/windsurf/.windsurf/rules" ".md"
}

build_openclaw() {
    echo -n "  openclaw: "
    local out="$DIST_DIR/openclaw/.openclaw/skills"
    mkdir -p "$out"
    cp -r "$SKILLS_SRC"/* "$out/"
    echo "$(find "$out" -name 'SKILL.md' | wc -l | tr -d ' ') skills"
}

echo "Building dist/ from ${#SKILL_DIRS[@]} skills..."
echo ""

case "$TARGET" in
    all)
        build_gemini
        build_copilot
        build_cursor
        build_claude
        build_codex
        build_hermes
        build_windsurf
        build_openclaw
        ;;
    gemini)    build_gemini ;;
    copilot)   build_copilot ;;
    cursor)    build_cursor ;;
    claude|claude-code) build_claude ;;
    codex)     build_codex ;;
    hermes)    build_hermes ;;
    windsurf)  build_windsurf ;;
    openclaw)  build_openclaw ;;
    *) echo "Unknown target: $TARGET"; exit 1 ;;
esac

echo ""
echo "Build complete. Output in dist/"

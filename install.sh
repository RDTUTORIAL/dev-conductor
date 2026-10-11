#!/usr/bin/env sh
# Install the dev-conductor skill for Claude Code and/or Codex-style agents.
#
#   ./install.sh                 # user-wide, both agents (~/.claude/skills, ~/.agents/skills)
#   ./install.sh --claude        # Claude Code only
#   ./install.sh --codex         # Codex / agents that read ~/.agents/skills only
#   ./install.sh --project DIR   # into DIR/.claude/skills and DIR/.agents/skills instead
#   ./install.sh --agents-md     # with --project: also copy templates/AGENTS.md if DIR has none
#   ./install.sh --link          # symlink instead of copy (for developing the skill)
#   ./install.sh --force         # replace an existing install (old one goes to ../skill-backups)
#   ./install.sh --with-companions [PACKS]  # also install companion skills (core,frontend,backend,stacks or all)
#   ./install.sh --yes           # with --with-companions: skip the confirmation prompt
set -eu

NAME="dev-conductor"
SRC_ROOT=$(cd "$(dirname "$0")" && pwd)
SRC="$SRC_ROOT/skills/$NAME"
CLAUDE=1 CODEX=1 PROJECT="" LINK=0 FORCE=0 AGENTS_MD=0 COMPANIONS="" YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --claude) CODEX=0 ;;
    --codex) CLAUDE=0 ;;
    --project) PROJECT=${2:?--project needs a directory}; shift ;;
    --agents-md) AGENTS_MD=1 ;;
    --link) LINK=1 ;;
    --force) FORCE=1 ;;
    --yes|-y) YES=1 ;;
    --with-companions)
      COMPANIONS=core
      case "${2:-}" in -*|"") ;; *) COMPANIONS=$2; shift ;; esac ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -f "$SRC/SKILL.md" ] || { echo "cannot find $SRC/SKILL.md" >&2; exit 1; }

if [ -n "$PROJECT" ]; then
  BASE=$(cd "$PROJECT" && pwd)
  CLAUDE_DIR="$BASE/.claude/skills"
  CODEX_DIR="$BASE/.agents/skills"
else
  CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
  CODEX_DIR="$HOME/.agents/skills"
fi

install_to() {
  dest="$1/$NAME"
  mkdir -p "$1"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$FORCE" -ne 1 ]; then
      echo "skip: $dest exists (use --force to replace)"
      return
    fi
    # Back up outside the skills folder, or the agent would load the backup as a second skill.
    backup_dir="$(dirname "$1")/skill-backups"
    mkdir -p "$backup_dir"
    backup="$backup_dir/$NAME.$(date +%Y%m%d%H%M%S)"
    mv "$dest" "$backup"
    echo "moved old install to $backup"
  fi
  if [ "$LINK" -eq 1 ]; then
    ln -s "$SRC" "$dest"
  else
    cp -R "$SRC" "$dest"
    find "$dest" -name '__pycache__' -type d -prune -exec rm -r {} + 2>/dev/null || true
  fi
  echo "installed: $dest"
}

[ "$CLAUDE" -eq 1 ] && install_to "$CLAUDE_DIR"
[ "$CODEX" -eq 1 ] && install_to "$CODEX_DIR"

if [ "$AGENTS_MD" -eq 1 ]; then
  if [ -z "$PROJECT" ]; then
    echo "--agents-md needs --project DIR" >&2
  elif [ -e "$BASE/AGENTS.md" ]; then
    echo "skip: $BASE/AGENTS.md exists; merge templates/AGENTS.md by hand"
  else
    cp "$SRC_ROOT/templates/AGENTS.md" "$BASE/AGENTS.md"
    echo "copied AGENTS.md template; fill in section 2 (repo facts)"
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  python3 -I "$SRC/scripts/validate.py" >/dev/null && echo "self-check: ok"
else
  echo "note: python3 not found; the skill still works, but its helper scripts will be skipped"
fi
if [ -n "$COMPANIONS" ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "--with-companions needs python3; see README for installing companions by hand" >&2
    exit 1
  fi
  agent=both
  [ "$CLAUDE" -eq 0 ] && agent=codex
  [ "$CODEX" -eq 0 ] && agent=claude
  if [ "$COMPANIONS" = "all" ]; then set -- --all; else set -- --packs "$COMPANIONS"; fi
  [ -n "$PROJECT" ] && set -- "$@" --project "$BASE" --repo "$BASE"
  [ "$YES" -eq 1 ] && set -- "$@" --yes
  python3 "$SRC_ROOT/install_companions.py" "$@" --agent "$agent"
fi
echo "Restart your agent session so it picks up the skill."

#!/usr/bin/env bash
#
# agent-tools — global installer for opencode
#
# Symlinks this repo's agents/, commands/, skills/, and AGENTS.md into your
# opencode global config (~/.config/opencode/), making them available in every
# project. Works on macOS, Linux, and WSL.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/erikhoward/agent-tools/main/install.sh | bash
#   ./install.sh [options]
#
# Options:
#   --source <path>    Use an existing repo checkout instead of cloning
#   --clone-dir <path> Where to clone (default: ~/.local/share/agent-tools)
#   --force            Overwrite existing files/symlinks in the target
#   --update           git pull the clone, then re-link (picks up new files)
#   --uninstall        Remove the symlinks created by this tool
#   --dry-run          Show what would happen without making changes
#   -h, --help         Show this help

set -u

REPO_URL="https://github.com/erikhoward/agent-tools.git"
CLONE_DIR="${HOME}/.local/share/agent-tools"
SOURCE_DIR=""
FORCE=0
UNINSTALL=0
UPDATE=0
DRY_RUN=0

CNT_LINKED=0
CNT_SKIPPED=0
CNT_WARNED=0

die() { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
}

# --- args ---
while [ $# -gt 0 ]; do
  case "$1" in
    --source)    SOURCE_DIR="${2:-}"; shift 2 ;;
    --clone-dir) CLONE_DIR="${2:-}"; shift 2 ;;
    --force)     FORCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --update)    UPDATE=1; shift ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

# --- config target (XDG-aware) ---
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
OC_DIR="${XDG_CONFIG_HOME}/opencode"

# --- portable absolute path (handles files and dirs) ---
abs_path() {
  local p="$1"
  if [ -d "$p" ]; then
    ( cd -P "$p" && pwd -P )
  else
    ( cd -P "$(dirname "$p")" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$(basename "$p")" )
  fi
}

is_repo() {
  [ -d "$1/agents" ] && [ -d "$1/skills" ] && [ -d "$1/commands" ] && [ -f "$1/AGENTS.md" ]
}

# --- dry-run-aware primitives ---
do_mkdir() { if [ "$DRY_RUN" -eq 1 ]; then printf '  mkdir -p %s\n' "$1"; else mkdir -p "$1" || die "mkdir failed: $1"; fi; }
do_rm()    { if [ "$DRY_RUN" -eq 1 ]; then printf '  rm -f %s\n' "$1"; else rm -f "$1"; fi; }
do_ln()    { if [ "$DRY_RUN" -eq 1 ]; then printf '  link: %s -> %s\n' "$2" "$1"; else ln -s "$1" "$2" || die "symlink failed: $2"; fi; }
do_git()   { if [ "$DRY_RUN" -eq 1 ]; then printf '  git %s\n' "$*"; else git "$@" || die "git $1 failed"; fi; }

resolve_source() {
  if [ -n "$SOURCE_DIR" ]; then
    SOURCE_DIR="$(abs_path "$SOURCE_DIR")" || die "--source not found: $SOURCE_DIR"
    is_repo "$SOURCE_DIR" || die "--source is not an agent-tools checkout: $SOURCE_DIR"
    printf 'Source (provided): %s\n' "$SOURCE_DIR"; return
  fi
  if is_repo "$PWD"; then
    SOURCE_DIR="$(abs_path "$PWD")"
    printf 'Source (current dir): %s\n' "$SOURCE_DIR"; return
  fi
  SOURCE_DIR="$CLONE_DIR"
  if [ "$UNINSTALL" -eq 1 ] || [ "$UPDATE" -eq 1 ]; then
    [ -d "$SOURCE_DIR/.git" ] || die "clone not found at $SOURCE_DIR. Pass --source <path> to target your checkout."
  elif [ ! -d "$SOURCE_DIR/.git" ]; then
    printf 'Cloning %s -> %s\n' "$REPO_URL" "$SOURCE_DIR"
    do_git clone --depth 1 "$REPO_URL" "$SOURCE_DIR"
  fi
  is_repo "$SOURCE_DIR" || die "not a valid agent-tools checkout: $SOURCE_DIR"
  printf 'Source (cloned): %s\n' "$SOURCE_DIR"
}

# install_link <source_abs> <dest_abs>
install_link() {
  local src="$1" dst="$2"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then
      CNT_SKIPPED=$((CNT_SKIPPED + 1)); printf '  ok    (linked): %s\n' "${dst#${OC_DIR}/}"; return 0
    fi
    if [ "$FORCE" -eq 1 ]; then do_rm "$dst"
    else CNT_WARNED=$((CNT_WARNED + 1)); printf '  WARN  (symlink exists, --force to replace): %s\n' "${dst#${OC_DIR}/}" >&2; return 0; fi
  elif [ -e "$dst" ]; then
    if [ "$FORCE" -eq 1 ]; then do_rm "$dst"
    else CNT_WARNED=$((CNT_WARNED + 1)); printf '  WARN  (real file exists, --force to overwrite): %s\n' "${dst#${OC_DIR}/}" >&2; return 0; fi
  fi
  do_ln "$src" "$dst"
  CNT_LINKED=$((CNT_LINKED + 1))
}

# remove_link <dest_abs> <expected_source_abs>
remove_link() {
  local dst="$1" exp="$2"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$exp" ]; then
      do_rm "$dst"; CNT_LINKED=$((CNT_LINKED + 1))
    else
      printf '  skip  (points elsewhere): %s\n' "${dst#${OC_DIR}/}"
    fi
  elif [ -e "$dst" ]; then
    printf '  skip  (not a symlink, left alone): %s\n' "${dst#${OC_DIR}/}"
  fi
}

install_all() {
  do_mkdir "$OC_DIR/agents"
  do_mkdir "$OC_DIR/commands"
  do_mkdir "$OC_DIR/skills"

  local f name
  for f in "$SOURCE_DIR"/agents/*.md; do [ -e "$f" ] || continue
    name="$(basename "$f")"; install_link "$f" "$OC_DIR/agents/$name"; done
  for f in "$SOURCE_DIR"/commands/*.md; do [ -e "$f" ] || continue
    name="$(basename "$f")"; install_link "$f" "$OC_DIR/commands/$name"; done
  for f in "$SOURCE_DIR"/skills/*/; do [ -d "$f" ] || continue
    name="$(basename "$f")"; install_link "${f%/}" "$OC_DIR/skills/$name"; done

  install_link "$SOURCE_DIR/AGENTS.md" "$OC_DIR/AGENTS.md"
}

uninstall_all() {
  local f name
  for f in "$SOURCE_DIR"/agents/*.md; do [ -e "$f" ] || continue
    name="$(basename "$f")"; remove_link "$OC_DIR/agents/$name" "$f"; done
  for f in "$SOURCE_DIR"/commands/*.md; do [ -e "$f" ] || continue
    name="$(basename "$f")"; remove_link "$OC_DIR/commands/$name" "$f"; done
  for f in "$SOURCE_DIR"/skills/*/; do [ -d "$f" ] || continue
    name="$(basename "$f")"; remove_link "$OC_DIR/skills/$name" "${f%/}"; done
  remove_link "$OC_DIR/AGENTS.md" "$SOURCE_DIR/AGENTS.md"
}

summary() {
  printf '\n'
  printf '  linked:    %s\n' "$CNT_LINKED"
  printf '  skipped:   %s\n' "$CNT_SKIPPED"
  printf '  warnings:  %s\n' "$CNT_WARNED"
  printf '\nTarget:  %s\n' "$OC_DIR"
  printf 'Source:  %s\n' "$SOURCE_DIR"
}

# --- main ---
if [ "$UNINSTALL" -eq 1 ]; then
  resolve_source
  printf 'Uninstalling agent-tools symlinks from %s\n' "$OC_DIR"
  uninstall_all
  summary
  printf '\nRemoved agent-tools symlinks. The clone at %s is left in place.\n' "$SOURCE_DIR"
  exit 0
fi

resolve_source

if [ "$UPDATE" -eq 1 ]; then
  printf 'Updating clone...\n'
  do_git -C "$SOURCE_DIR" pull --ff-only
  FORCE=1
fi

printf 'Installing agent-tools into %s\n' "$OC_DIR"
install_all
summary

printf '\nNext steps:\n'
printf '  - Restart opencode for the new agents/commands/skills/AGENTS.md to load.\n'
printf '  - Update later:   ./install.sh --update   (or: cd %s && git pull)\n' "$SOURCE_DIR"
printf '  - Uninstall:      ./install.sh --uninstall\n'
if [ "$DRY_RUN" -eq 1 ]; then printf '\n(dry-run: no changes were made)\n'; fi

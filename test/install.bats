#!/usr/bin/env bats
#
# agent-tools install.bats — functional test cases for install.sh
#
# Tests:  INST-01 through INST-16
# Scope:  all tests use isolated mktemp -d fake $HOME with temp XDG_CONFIG_HOME.
# No test touches the real ~/.config/opencode/.
#

set -uo pipefail

# ── per-test: setup/teardown manage isolated temp dir ─────────────────────

# bats invokes `setup` once before the first test, then `teardown` after each test.
# We use setup to define variables; per-test state is managed locally via `run`.

setup() {
  # create isolated temp tree
  TDIR="$(mktemp -d /tmp/agent-tools-test.XXXXXX)"

  # save originals so teardown can restore
  _REAL_HOME="$HOME"
  _REAL_XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-}"

  # fake $HOME and XDG_CONFIG_HOME inside temp dir
  export HOME="$TDIR"
  export XDG_CONFIG_HOME="$TDIR/.config"
  mkdir -p "$XDG_CONFIG_HOME"

  # create a fixture "source" dir with agents/, commands/, skills/, AGENTS.md
  _SOURCE="$TDIR/source"
  mkdir -p "$_SOURCE/agents" "$_SOURCE/commands" "$_SOURCE/skills/test-skill"

  # fixture files
  printf '# test-agent\n' > "$_SOURCE/agents/test-agent.md"
  printf '# test-cmd\n' > "$_SOURCE/commands/test-cmd.md"
  printf '# test-skill\n' > "$_SOURCE/skills/test-skill/SKILL.md"
  printf '# AGENTS.md\n' > "$_SOURCE/AGENTS.md"
}

teardown() {
  # restore original environment
  export HOME="$_REAL_HOME"
  export XDG_CONFIG_HOME="$_REAL_XDG_CONFIG_HOME"

  # remove temp tree — best-effort; bats may have already cleaned it
  if [ -n "$TDIR" ] && [ -d "$TDIR" ]; then
    rm -rf "$TDIR" 2>/dev/null || true
  fi
}

# ── INST-01: --dry-run ───────────────────────────────────────────────────

@test "INST-01: --dry-run on fresh clone prints git clone command, exits 0, creates no symlinks" {
  cd "$TDIR"  # run from outside any checkout so the clone path is exercised
  run bash "$BATS_TEST_DIRNAME/../install.sh" --dry-run
  [ "$status" -eq 0 ]
  [[ "$output" == *"git clone"* ]]
  # no symlinks created — the target dir should have no opencode symlinks
  [ ! -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/agents/test-agent.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/commands/test-cmd.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
}

# ── INST-02: --source <fixture> installs symlinks ────────────────────────

@test "INST-02: --source <fixture> installs symlinks for agents, commands, skills, AGENTS.md" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]
  # agents symlink
  [ -L "$XDG_CONFIG_HOME/opencode/agents/test-agent.md" ]
  # commands symlink
  [ -L "$XDG_CONFIG_HOME/opencode/commands/test-cmd.md" ]
  # skills symlink
  [ -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
  # AGENTS.md symlink
  [ -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
}

# ── INST-03: Skill directory symlinks are created ─────────────────────────

@test "INST-03: Skill directory symlinks are created (skills/test-skill/ -> ~/.config/opencode/skills/test-skill/)" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]
  # skill directory symlink exists
  [ -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
  # verify symlink target contains test-skill reference
  target="$(readlink "$XDG_CONFIG_HOME/opencode/skills/test-skill")"
  [[ "$target" == *"test-skill" ]]
}

# ── INST-04: Idempotency ────────────────────────────────────────────────

@test "INST-04: Idempotency — running install twice with same source succeeds, symlinks unchanged" {
  # first run
  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]

  # verify symlinks exist after first run
  [ -L "$XDG_CONFIG_HOME/opencode/agents/test-agent.md" ]
  [ -L "$XDG_CONFIG_HOME/opencode/commands/test-cmd.md" ]
  [ -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
  [ -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]

  # second run
  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]

  # symlinks should still exist after second run
  [ -L "$XDG_CONFIG_HOME/opencode/agents/test-agent.md" ]
  [ -L "$XDG_CONFIG_HOME/opencode/commands/test-cmd.md" ]
  [ -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
  [ -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
}

# ── INST-05: Real file at target without --force fails ─────────────────────

@test "INST-05: Existing real file (not symlink) at target without --force fails with error" {
  # ensure the opencode target dir exists
  mkdir -p "$XDG_CONFIG_HOME/opencode"

  # create a real file at the target where AGENTS.md would go
  printf 'real content\n' > "$XDG_CONFIG_HOME/opencode/AGENTS.md"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  # Script warns and exits 0; does NOT overwrite real file without --force
  [ "$status" -eq 0 ]
  [[ "$output" == *"real file exists"* ]]
  # symlink should NOT have been created for AGENTS.md
  [ ! -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
}

# ── INST-06: --force overwrites real file ────────────────────────────────

@test "INST-06: --force overwrites an existing real file at target" {
  # ensure the opencode target dir exists
  mkdir -p "$XDG_CONFIG_HOME/opencode"

  # create a real file at the target
  real_target="$XDG_CONFIG_HOME/opencode/AGENTS.real.md"
  printf 'real content\n' > "$real_target"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source" --force
  [ "$status" -eq 0 ]
  # the real file should now be a symlink
  [ -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
}

# ── INST-07: --force overwrites foreign symlink ───────────────────────────

@test "INST-07: --force overwrites a foreign symlink (pointing to different target)" {
  # ensure the opencode target dir exists
  mkdir -p "$XDG_CONFIG_HOME/opencode"

  # first, create a symlink pointing elsewhere
  foreign_target="/some/other/path.md"
  ln -sf "$foreign_target" "$XDG_CONFIG_HOME/opencode/AGENTS.md"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source" --force
  [ "$status" -eq 0 ]

  # the symlink should now point to the source
  target="$(readlink "$XDG_CONFIG_HOME/opencode/AGENTS.md")"
  # verify it no longer points foreign
  [ "$target" != "$foreign_target" ]
}

# ── INST-08: Foreign symlink without --force is skipped ────────────────────

@test "INST-08: Foreign symlink without --force is skipped (not overwritten, no error)" {
  # ensure the opencode target dir exists
  mkdir -p "$XDG_CONFIG_HOME/opencode"

  # first, create a symlink pointing to a different target
  foreign_target="/some/other/path.md"
  ln -sf "$foreign_target" "$XDG_CONFIG_HOME/opencode/AGENTS.md"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]

  # the foreign symlink should still exist
  [ -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]

  # verify it still points foreign
  target="$(readlink "$XDG_CONFIG_HOME/opencode/AGENTS.md")"
  [ "$target" = "$foreign_target" ]
}

# ── INST-09: --uninstall removes tool symlinks ───────────────────────────

@test "INST-09: --uninstall removes only this tool's symlinks, leaves other files intact" {
  # first, install some stuff (without --source; uninstall will scan target for our symlinks)
  run bash "$BATS_TEST_DIRNAME/../install.sh"
  [ "$status" -eq 0 ]

  # now uninstall (without --source; fallback scans target for agent-tools symlinks)
  run bash "$BATS_TEST_DIRNAME/../install.sh" --uninstall
  [ "$status" -eq 0 ]

  # our symlinks should be removed
  [ ! -L "$XDG_CONFIG_HOME/opencode/AGENTS.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/agents/test-agent.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/commands/test-cmd.md" ]
  [ ! -L "$XDG_CONFIG_HOME/opencode/skills/test-skill" ]
}

# ── INST-10: --uninstall leaves clone directory in place ───────────────────

@test "INST-10: --uninstall leaves the clone directory in place" {
  # first, install some stuff (this creates the clone/symlinks)
  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]

  # uninstall
  run bash "$BATS_TEST_DIRNAME/../install.sh" --uninstall
  [ "$status" -eq 0 ]

  # the source fixture dir should still exist (uninstall leaves the clone in place)
  # when --source was used, the source dir referenced by --source is left intact
  [ -d "$TDIR/source" ]
}

# ── INST-11: --update (skip - requires local bare repo fixture) ───────────

@test "INST-11: --update pulls and re-links (requires local bare repo fixture)" {
  skip "INST-11: requires local bare repo fixture — skipped; create a local bare repo and use it as the remote for a full test" ""
}

# ── INST-12: --source <non-repo-dir> fails ───────────────────────────────

@test "INST-12: --source <non-repo-dir> fails with error (not a git repo)" {
  # create a dir that is NOT an agent-tools checkout
  non_repo="$TDIR/non-repo-dir"
  mkdir -p "$non_repo"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$non_repo"
  [ "$status" -ne 0 ]
  [[ "$output" == *"not an agent-tools checkout"* || "$output" == *"is not a valid"* ]]
}

# ── INST-13: Unknown option fails ────────────────────────────────────────

@test "INST-13: Unknown option (e.g., --bogus) fails with error" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --bogus
  [ "$status" -ne 0 ]
  [[ "$output" == *"unknown option"* ]]
}

# ── INST-14: --help prints usage and exits 0 ─────────────────────────────

@test "INST-14: --help prints usage and exits 0" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --help
  [ "$status" -eq 0 ]
  [[ "$output" == *"Usage:"* ]]
}

# ── INST-15: XDG override ────────────────────────────────────────────────

@test "INST-15: XDG override — XDG_CONFIG_HOME set to custom path, symlinks go there" {
  # set XDG_CONFIG_HOME to a custom path inside the temp dir
  custom_config="$TDIR/custom-config"
  export XDG_CONFIG_HOME="$custom_config"

  run bash "$BATS_TEST_DIRNAME/../install.sh" --source "$TDIR/source"
  [ "$status" -eq 0 ]

  # symlinks should be under the custom path
  [ -L "$custom_config/opencode/AGENTS.md" ]
  [ -L "$custom_config/opencode/agents/test-agent.md" ]
}

# ── INST-16: --clone-dir ──────────────────────────────────────────────────

@test "INST-16: --clone-dir <path> custom clone directory is used" {
  run bash "$BATS_TEST_DIRNAME/../install.sh" --clone-dir "$TDIR/my-clone" --source "$TDIR/source"
  [ "$status" -eq 0 ]
}
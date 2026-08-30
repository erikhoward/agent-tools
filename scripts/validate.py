#!/usr/bin/env python3
"""Validator for agent-tools repo configuration files.

Uses only Python 3 stdlib (re, pathlib, sys, argparse, json). No pip dependencies.
"""

import argparse
import json
import re
import sys
from pathlib import Path

Finding = dict[str, str | int]


def parse_frontmatter(fm_text: str) -> dict:
    """Parse YAML frontmatter using only re and string operations.

    Handles: flat key: value pairs, key: | block scalars, and one-level
    nested maps. List items (- value) are skipped. Does NOT use PyYAML.
    """
    result: dict = {}
    if not fm_text or not fm_text.startswith("---"):
        return result

    lines = fm_text.split("\n")

    # Find the second --- delimiter (skip index 0 which is the opening delimiter)
    second_dash_idx = None
    for i, line in enumerate(lines):
        if i == 0:
            continue  # skip the opening --- delimiter
        if line.strip() == "---":
            second_dash_idx = i
            break

    if second_dash_idx is None or second_dash_idx <= 1:
        return result

    # Frontmatter content is between the --- delimiters (indices 1 .. second_dash_idx-1)
    fm_lines = lines[1:second_dash_idx]

    i = 0
    in_block_scalar = False
    block_key: str | None = None
    block_value_lines: list[str] = []

    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()

        if stripped == "":
            i += 1
            continue

        # ----- Block scalar continuation / end -----
        if in_block_scalar:
            if len(line) > 0 and (line[0] == " " or line[0] == "\t"):
                block_value_lines.append(line.rstrip("\n"))
                i += 1
                continue
            else:
                # End of block scalar — put current line back for reprocessing
                result[block_key] = "\n".join(block_value_lines).strip()
                in_block_scalar = False
                block_key = None
                block_value_lines = []
                # continue without incrementing i — reprocess this line

        # ----- Pattern matching (only if not in block scalar) -----
        if not in_block_scalar:
            # ----- Block scalar trigger: key: | -----
            bs_match = re.match(r"^(\S+): \|\s*$", line)
            if bs_match:
                block_key = bs_match.group(1)
                in_block_scalar = True
                block_value_lines = []
                i += 1
                continue

            # ----- Flat key: value pair (must check before nested map) -----
            fk_match = re.match(r"^(\S+):\s*(.+)$", line)
            if fk_match:
                key = fk_match.group(1)
                value = fk_match.group(2).strip()
                result[key] = value
                i += 1
                continue

            # ----- Nested map: key: with indented sub-content -----
            nm_match = re.match(r"^(\S+):\s*$", line)
            if nm_match:
                key = nm_match.group(1)
                i += 1
                nested: dict = {}
                sub_lines: list[str] = []
                while i < len(fm_lines):
                    next_line = fm_lines[i]
                    if not next_line or not (next_line[0] == " " or next_line[0] == "\t"):
                        break
                    sub_lines.append(next_line.rstrip("\n"))
                    inner = next_line.strip()
                    if ":" in inner:
                        inner_key, _, inner_val = inner.partition(":")
                        inner_key = inner_key.strip()
                        inner_val = inner_val.strip()
                        if inner_val:
                            nested[inner_key] = inner_val
                    i += 1
                if nested:
                    result[key] = nested
                elif sub_lines:
                    result[key] = "\n".join(sub_lines).strip()
                # continue without incrementing i (already at non-indented line)
                continue


        # Unknown line — skip
        i += 1

    # Handle unclosed block scalar at end of frontmatter
    if in_block_scalar and block_key:
        result[block_key] = "\n".join(block_value_lines).strip()

    return result


def find_agent_mentions(content: str) -> list[tuple[str, int]]:
    """Find @agent-name mentions in prose, excluding false positives.

    Excludes: @{u} (git upstream), email-like patterns, @ followed by non-alphabetic.
    Returns list of (name, line_number) tuples.
    """
    mentions: list[tuple[str, int]] = []
    # Track whether we're inside a fenced code block ```
    in_code_block = False
    # Common non-agent @ patterns to denylist
    NON_AGENT_PATTERNS = {
        "latest", "me", "csv", "json", "example", "prod", "staging",
        "dev", "team", "file", "data", "owner", "user", "org", "all",
        "dataclass", "functools", "lru", "property", "staticmethod",
        "classmethod", "app", "router", "pytest", "unittest", "mock",
        "patch", "commitlint", "semantic-release", "babel", "types",
        "storybook", "angular", "vue", "see", "parametrize", "linter",
    }
    for line_num, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # Match @ followed by alphabetic char, then word chars or hyphens
        # Negative lookbehind prevents matching @{u}-style patterns
        # Also skip version patterns like v4, v5, v7
        for m in re.finditer(r"(?<![/\{])@([A-Za-z][A-Za-z0-9-]*)", line):
            name = m.group(1)
            # Skip version patterns like v4, v5, v7
            if re.match(r"^v\d+$", name):
                continue
            # Skip non-agent patterns
            if name in NON_AGENT_PATTERNS:
                continue
            # Exclude names containing . (email-like patterns like user@example)
            if "." in name:
                continue
            # Skip single-char names that are likely not agents
            if len(name) <= 1:
                continue
            mentions.append((name, line_num))
    return mentions


def find_skill_mentions(content: str) -> list[tuple[str, int]]:
    """Find `` `skill-name` `` mentions with skill-loading context.

    Matches patterns like: "the `go` skill", "load the `solid` skill".
    Returns list of (skill_name, line_number) tuples.
    """
    mentions: list[tuple[str, int]] = []
    # Match `` `name` `` followed by "skill", with optional "the " or "load " prefix
    for m in re.finditer(r"(?:load |the )?`([A-Za-z-]+)`\s+skill", content, re.IGNORECASE):
        skill_name = m.group(1)
        line_num = content[: m.start()].count("\n") + 1
        mentions.append((skill_name, line_num))
    return mentions


def find_relative_markdown_links(content: str) -> list[tuple[str, int]]:
    """Find relative markdown links [text](path) in content.

    Excludes http/https links and internal anchor links (#...).
    Returns list of (link_path, line_number) tuples.
    """
    links: list[tuple[str, int]] = []
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", content):
        link_path = m.group(2)
        # Skip absolute URLs
        if link_path.startswith("http://") or link_path.startswith("https://"):
            continue
        # Skip internal anchor links
        if link_path.startswith("#"):
            continue
        # Skip paths with spaces (not valid file paths — likely code syntax)
        if " " in link_path:
            continue
        # Skip paths with parentheses (likely code, not markdown links)
        if "(" in link_path or ")" in link_path:
            continue
        line_num = content[: m.start()].count("\n") + 1
        links.append((link_path, line_num))
    return links


def _find_key_line(content: str, key: str) -> int:
    """Return the 1-indexed line number where `key: ` first appears in content."""
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith(f"{key}:"):
            return i
    return 1


def _add_finding(findings: list[Finding], ftype: str, file_path: Path,
                 line: int, message: str) -> None:
    """Append a finding to the list."""
    findings.append({
        "type": ftype,
        "file": str(file_path),
        "line": line,
        "message": message,
    })


def validate_agents(repo: Path, findings: list[Finding]) -> None:
    """Validate agent schema in agents/*.md files."""
    agents_dir = repo / "agents"
    if not agents_dir.exists():
        return

    # Parse all agent frontmatter
    agent_files: dict[str, dict] = {}
    for md_file in agents_dir.glob("*.md"):
        try:
            content = md_file.read_text()
        except OSError:
            continue
        fm = parse_frontmatter(content)
        agent_files[md_file.name] = {
            "content": content,
            "fm": fm,
            "path": md_file,
        }

    valid_modes = {"primary", "subagent", "all"}
    valid_permissions = {"allow", "ask", "deny"}
    model_pattern = re.compile(r"^[a-z0-9_.-]+/[a-z0-9_.-]+$")

    for name, info in agent_files.items():
        fm = info["fm"]
        path = info["path"]
        content = info["content"]

        # --- Required: description (non-empty string) ---
        if "description" not in fm:
            _add_finding(findings, "E", path, _find_key_line(content, "description"),
                         "Missing required field `description`")
        elif not isinstance(fm["description"], str) or fm["description"].strip() == "":
            _add_finding(findings, "E", path, _find_key_line(content, "description"),
                         "`description` must be a non-empty string")

        # --- Required: mode (primary, subagent, or all) ---
        if "mode" not in fm:
            _add_finding(findings, "E", path, _find_key_line(content, "mode"),
                         "Missing required field `mode`")
        elif fm["mode"] not in valid_modes:
            _add_finding(findings, "E", path, _find_key_line(content, "mode"),
                         f"`mode` must be one of {valid_modes}, got `{fm['mode']}`")

        # --- Optional: model format check ---
        if "model" in fm:
            if not model_pattern.match(fm["model"]):
                _add_finding(findings, "W", path, _find_key_line(content, "model"),
                             f"`model` format invalid: `{fm['model']}` does not match "
                             r"`^[a-z0-9_.-]+/[a-z0-9_.-]+$`")

        # --- Optional: permission values ---
        if "permission" in fm:
            perm = fm["permission"]
            if isinstance(perm, dict):
                for p_key, p_val in perm.items():
                    if p_val not in valid_permissions:
                        _add_finding(findings, "W", path,
                                     _find_key_line(content, "permission"),
                                     f"permission value `{p_val}` not in {valid_permissions}")
            elif isinstance(perm, str):
                if perm not in valid_permissions:
                    _add_finding(findings, "W", path,
                                 _find_key_line(content, "permission"),
                                 f"permission value `{perm}` not in {valid_permissions}")


def validate_commands(repo: Path, findings: list[Finding]) -> None:
    """Validate command schema in commands/*.md files."""
    commands_dir = repo / "commands"
    if not commands_dir.exists():
        return

    valid_model_pattern = re.compile(r"^[a-z0-9_.-]+/[a-z0-9_.-]+$")

    for md_file in commands_dir.glob("*.md"):
        try:
            content = md_file.read_text()
        except OSError:
            continue

        fm = parse_frontmatter(content)

        # --- Required: description (non-empty) ---
        if "description" not in fm:
            _add_finding(findings, "E", md_file, _find_key_line(content, "description"),
                         "Missing required field `description`")
        elif not isinstance(fm["description"], str) or fm["description"].strip() == "":
            _add_finding(findings, "E", md_file, _find_key_line(content, "description"),
                         "`description` must be a non-empty string")

        # --- Required: agent must reference existing agent file ---
        if "agent" not in fm:
            _add_finding(findings, "E", md_file, _find_key_line(content, "agent"),
                         "Missing required field `agent`")
        else:
            agent_ref = fm["agent"]
            agent_file = repo / "agents" / f"{agent_ref}.md"
            if not agent_file.exists():
                _add_finding(findings, "E", md_file, _find_key_line(content, "agent"),
                             f"agent reference `{agent_ref}` does not resolve to an existing file")

        # --- Optional: model format check ---
        if "model" in fm:
            if not valid_model_pattern.match(fm["model"]):
                _add_finding(findings, "W", md_file, _find_key_line(content, "model"),
                             f"`model` format invalid: `{fm['model']}` does not match "
                             r"`^[a-z0-9_.-]+/[a-z0-9_.-]+$`")


def validate_skills(repo: Path, findings: list[Finding]) -> None:
    """Validate skill schema in skills/*/SKILL.md files."""
    skills_dir = repo / "skills"
    if not skills_dir.exists():
        return

    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text()
        except OSError:
            continue

        fm = parse_frontmatter(content)

        # --- Required: name must equal parent directory name ---
        dir_name = skill_dir.name
        if "name" not in fm:
            _add_finding(findings, "E", skill_md, _find_key_line(content, "name"),
                         "Missing required field `name`")
        elif fm["name"] != dir_name:
            _add_finding(findings, "E", skill_md, _find_key_line(content, "name"),
                         f"`name` ({fm['name']}) does not match parent directory name ({dir_name})")

        # --- Required: description (non-empty) ---
        if "description" not in fm:
            _add_finding(findings, "E", skill_md, _find_key_line(content, "description"),
                         "Missing required field `description`")
        elif not isinstance(fm["description"], str) or fm["description"].strip() == "":
            _add_finding(findings, "E", skill_md, _find_key_line(content, "description"),
                         "`description` must be a non-empty string")

        # --- Optional: license, compatibility, metadata (no format checks beyond existence) ---
        # Per spec: optional fields, no validation beyond presence


def cross_reference(repo: Path, findings: list[Finding]) -> None:
    """Cross-reference validation across all .md files."""
    all_md_content: list[tuple[str, Path]] = []

    # Collect all .md file contents for analysis
    for md_file in repo.rglob("*.md"):
        if ".opencode" in md_file.parts:
            continue
        try:
            content = md_file.read_text()
        except OSError:
            continue
        all_md_content.append((content, md_file))

    # -- 1. @agent-name mentions across all .md files --
    agent_allowlist = {"explore"}

    for content, md_file in all_md_content:
        for agent_name, line_num in find_agent_mentions(content):
            target_file = repo / "agents" / f"{agent_name}.md"
            if not target_file.exists() and agent_name not in agent_allowlist:
                _add_finding(
                    findings, "W", md_file, line_num,
                    f"@agent-reference `{agent_name}` has no corresponding agents/{agent_name}.md "
                    f"and is not in the external allowlist"
                )

    # -- 2. `` `skill-name` `` mentions in agent/command prose --
    for content, md_file in all_md_content:
        for skill_name, line_num in find_skill_mentions(content):
            skill_dir = repo / "skills" / skill_name
            if not skill_dir.exists():
                _add_finding(
                    findings, "W", md_file, line_num,
                    f"Skill `{skill_name}` mention without corresponding skills/{skill_name}/ directory"
                )

    # -- 3. Relative markdown links [text](path) in any .md file --
    for content, md_file in all_md_content:
        for link_path, line_num in find_relative_markdown_links(content):
            # Check that relative path (not http/https) target exists
            # Already excluded http/https from find_relative_markdown_links
            target = md_file.parent / link_path
            if not target.exists():
                # Avoid duplicate findings for the same link
                message = (
                    f"Relative markdown link `[text]({link_path})` target does not exist"
                )
                already_reported = any(
                    f["file"] == str(md_file) and f["message"] == message
                    for f in findings
                )
                if not already_reported:
                    _add_finding(findings, "W", md_file, line_num, message)


def roster_consistency(repo: Path, findings: list[Finding]) -> None:
    """Parse AGENTS.md and verify table consistency."""
    agents_md = repo / "AGENTS.md"
    commands_dir = repo / "commands"
    skills_dir = repo / "skills"
    if not agents_md.exists():
        return

    try:
        content = agents_md.read_text()
    except OSError:
        return

    # --- Parse Agents table ---
    agents_table_names: set[str] = set()
    in_agents_table = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### Agents"):
            in_agents_table = True
            continue
        if stripped.startswith("### ") and in_agents_table:
            in_agents_table = False
            continue
        if in_agents_table and stripped.startswith("|"):
            # Only extract from the first column (between first | and  |)
            first_col = stripped.split(" | ")[0]
            # Extract ALL names from table row first column | `name1`, `name2` |
            names = re.findall(r"`([^`]+)`", first_col)
            for name in names:
                name = name.lstrip("/@")  # strip leading / or @
                if name:
                    agents_table_names.add(name)

    # --- Parse Commands table ---
    commands_table_names: set[str] = set()
    # Reset
    in_commands_table = False
    # Re-read and find Commands section
    current_section = None
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### Commands"):
            current_section = "commands"
            in_commands_table = True
            continue
        if stripped.startswith("### ") and current_section == "commands":
            in_commands_table = False
            current_section = None
            continue
        if stripped.startswith("### ") and current_section is None:
            # Another section started
            current_section = None
            continue
        if current_section == "commands" and stripped.startswith("|"):
            # Only extract from the first column (between first | and  |)
            first_col = stripped.split(" | ")[0]
            # Extract ALL names from table row first column | `name1`, `name2` |
            names = re.findall(r"`([^`]+)`", first_col)
            for name in names:
                name = name.lstrip("/@")  # strip leading / or @
                if name:
                    commands_table_names.add(name)

    # --- Parse Skills table ---
    skills_table_names: set[str] = set()
    current_section = None
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### Skills"):
            current_section = "skills"
            continue
        if stripped.startswith("### ") and current_section == "skills":
            current_section = None
            continue
        if current_section == "skills" and stripped.startswith("|"):
            # Only extract from the first column (between first | and  |)
            first_col = stripped.split(" | ")[0]
            # Extract ALL names from table row first column | `name1`, `name2` |
            names = re.findall(r"`([^`]+)`", first_col)
            for name in names:
                name = name.lstrip("/@")  # strip leading / or @
                if name:
                    skills_table_names.add(name)

    # --- Validate: every agent name in table -> agents/<name>.md exists ---
    agents_dir = repo / "agents"
    for name in agents_table_names:
        agent_file = agents_dir / f"{name}.md"
        if not agent_file.exists():
            # Check if it's the @explore built-in
            if name != "explore":
                _add_finding(
                    findings, "E", agents_md, 1,
                    f"Agents table lists `{name}` but agents/{name}.md does not exist"
                )

    # --- Every agents/<name>.md -> appears in AGENTS.md table ---
    if agents_dir.exists():
        for md_file in agents_dir.glob("*.md"):
            name = md_file.stem  # filename without .md
            if name not in agents_table_names:
                _add_finding(
                    findings, "E", agents_md, 1,
                    f"agents/{name}.md exists but is not in the AGENTS.md Agents table"
                )

    # --- Same for Commands table ---
    for name in commands_table_names:
        cmd_file = repo / "commands" / f"{name}.md"
        if not cmd_file.exists():
            _add_finding(
                findings, "E", agents_md, 1,
                f"Commands table lists `{name}` but commands/{name}.md does not exist"
            )

    if commands_dir.exists():
        for md_file in commands_dir.glob("*.md"):
            name = md_file.stem
            if name not in commands_table_names:
                _add_finding(
                    findings, "E", agents_md, 1,
                    f"commands/{name}.md exists but is not in the AGENTS.md Commands table"
                )

    # --- Same for Skills table ---
    for name in skills_table_names:
        skill_dir = repo / "skills" / name
        if not skill_dir.exists():
            _add_finding(
                findings, "E", agents_md, 1,
                f"Skills table lists `{name}` but skills/{name}/ does not exist"
            )

    if skills_dir.exists():
        for sd in skills_dir.iterdir():
            if sd.is_dir() and (sd / "SKILL.md").exists():
                name = sd.name
                if name not in skills_table_names:
                    _add_finding(
                        findings, "E", agents_md, 1,
                        f"skills/{name}/SKILL.md exists but is not in the AGENTS.md Skills table"
                    )


def model_allowlist(repo: Path, findings: list[Finding]) -> None:
    """Check model: fields against scripts/models.txt allowlist if it exists."""
    models_txt = repo / "scripts" / "models.txt"
    if not models_txt.exists():
        return  # skip if no allowlist

    try:
        text = models_txt.read_text()
    except OSError:
        return

    allowlist: set[str] = set()
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        allowlist.add(line)

    if not allowlist:
        return

    # Check all .md files for model: fields
    for md_file in repo.rglob("*.md"):
        if ".opencode" in md_file.parts:
            continue
        try:
            content = md_file.read_text()
        except OSError:
            continue

        fm = parse_frontmatter(content)
        if "model" in fm:
            model_id = fm["model"]
            if model_id not in allowlist:
                _add_finding(
                    findings, "W", md_file, _find_key_line(content, "model"),
                    f"`model` `{model_id}` not in models.txt allowlist"
                )


def _format_text(findings: list[Finding], quiet: bool) -> str:
    """Format findings as text output."""
    if not findings:
        return "No findings.\n"

    errors = [f for f in findings if f["type"] == "E"]
    warnings = [f for f in findings if f["type"] == "W"]

    output_lines: list[str] = []
    for f in errors:
        output_lines.append(f"E  {f['file']}:{f['line']}  {f['message']}")
    for f in warnings:
        if not quiet:
            output_lines.append(f"W  {f['file']}:{f['line']}  {f['message']}")

    summary = f"Found {len(errors)} errors"
    if not quiet:
        summary += f", {len(warnings)} warnings"
    else:
        summary += f" ( {len(warnings)} warnings suppressed )"
    summary += ".\n"

    return "\n".join(output_lines) + summary


def _format_json(findings: list[Finding]) -> str:
    """Format findings as JSON output."""
    error_list = []
    for f in findings:
        if f["type"] == "E":
            error_list.append({
                "file": f["file"],
                "line": f["line"],
                "message": f["message"],
            })

    return json.dumps({
        "errors": error_list,
        "total_errors": len(error_list),
    }, indent=2) + "\n"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate agent-tools repo configuration files"
    )
    parser.add_argument(
        "--repo", default=".",
        help="Path to repo root (default: current directory)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress warning output (errors always shown)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output results as JSON instead of text",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    findings: list[Finding] = []

    # 1. Agent schema validation
    validate_agents(repo, findings)

    # 2. Command schema validation
    validate_commands(repo, findings)

    # 3. Skill schema validation
    validate_skills(repo, findings)

    # 4. Cross-reference validation
    cross_reference(repo, findings)

    # 5. Roster consistency
    roster_consistency(repo, findings)

    # 6. Model allowlist
    model_allowlist(repo, findings)

    # 7. Output
    if args.json:
        print(_format_json(findings))
    else:
        text = _format_text(findings, args.quiet)
        print(text)

    # Exit code: 1 if errors found, 0 otherwise
    error_count = sum(1 for f in findings if f["type"] == "E")
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
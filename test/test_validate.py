"""Unit tests for scripts/validate.py.

Regression suite for GitHub issue #15 (test-suite-first half; closes #10).
These tests pin CURRENT validator behavior only. A follow-up task
modernizes the validator schema; update these tests deliberately when
that behavior changes.

Stdlib unittest only. Every check that needs a repo tree builds it inside
a tempfile.TemporaryDirectory(); no test reads or writes real repo files.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Make scripts/validate.py importable no matter which CWD unittest runs from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate  # noqa: E402  (import after the sys.path setup above)

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_PY = REPO_ROOT / "scripts" / "validate.py"


class RepoTestCase(unittest.TestCase):
    """Base class for checks that need a fixture repo tree."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="validate-test-")
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)

    def write(self, relpath: str, content: str) -> Path:
        """Write content at relpath inside the fixture repo; return the path."""
        path = self.repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


class TestParseFrontmatter(unittest.TestCase):
    """parse_frontmatter: pure-function parsing behavior."""

    def test_flat_key_value_pairs(self):
        fm = validate.parse_frontmatter(
            "---\nname: agent\nmode: primary\n---\nbody\n"
        )
        self.assertEqual(fm, {"name": "agent", "mode": "primary"})

    def test_block_scalar_joins_multiline_value(self):
        fm = validate.parse_frontmatter(
            "---\ndescription: |\n  line one\n  line two\nname: agent\n---\n"
        )
        self.assertEqual(fm["name"], "agent")
        self.assertEqual(fm["description"], "line one\n  line two")

    def test_one_level_nested_map(self):
        fm = validate.parse_frontmatter("---\npermission:\n  edit: deny\n---\n")
        self.assertEqual(fm, {"permission": {"edit": "deny"}})

    def test_top_level_list_lines_are_skipped(self):
        fm = validate.parse_frontmatter("---\n- alpha\n- beta\n---\n")
        self.assertEqual(fm, {})

    def test_nested_map_drops_list_lines(self):
        fm = validate.parse_frontmatter(
            "---\npermission:\n  edit: deny\n  - stray item\n---\n"
        )
        self.assertEqual(fm, {"permission": {"edit": "deny"}})

    def test_text_without_delimiters_returns_empty_dict(self):
        fm = validate.parse_frontmatter("just prose, no frontmatter delimiters")
        self.assertEqual(fm, {})

    def test_unclosed_block_scalar_at_end_lands_in_result(self):
        fm = validate.parse_frontmatter(
            "---\nmode: primary\ndescription: |\n  only line\n---\n"
        )
        self.assertEqual(fm, {"mode": "primary", "description": "only line"})


class TestFindAgentMentions(unittest.TestCase):
    """find_agent_mentions: pure-function mention detection."""

    def test_finds_plain_mention(self):
        mentions = validate.find_agent_mentions("Ping @build for help.\n")
        self.assertEqual(mentions, [("build", 1)])

    def test_ignores_mentions_inside_code_fences(self):
        content = "outside @build\n```\n@build\n```\nafter @build\n"
        mentions = validate.find_agent_mentions(content)
        self.assertEqual(mentions, [("build", 1), ("build", 5)])

    def test_ignores_git_upstream_and_version_mentions(self):
        content = "push @{u} and tag @v4 or @v5\n"
        self.assertEqual(validate.find_agent_mentions(content), [])

    def test_ignores_denylisted_and_email_like_mentions(self):
        content = "run @linter; mail user@example.com\n"
        self.assertEqual(validate.find_agent_mentions(content), [])

    def test_ignores_single_char_names(self):
        self.assertEqual(validate.find_agent_mentions("see @x and @y\n"), [])


class TestFindRelativeMarkdownLinks(unittest.TestCase):
    """find_relative_markdown_links: pure-function link detection."""

    def test_finds_relative_link(self):
        content = "See [docs](docs/foo.md) now.\n"
        links = validate.find_relative_markdown_links(content)
        self.assertEqual(links, [("docs/foo.md", 1)])

    def test_skips_non_relative_links(self):
        content = (
            "[a](https://example.com) [b](http://example.com) [c](#top) "
            "[d](some path.md) [e](foo(1).md)\n"
        )
        self.assertEqual(validate.find_relative_markdown_links(content), [])


class TestValidateAgents(RepoTestCase):
    """validate_agents: agents/*.md schema checks."""

    def test_missing_description_is_error(self):
        agent = self.write("agents/bad.md", "---\nmode: primary\n---\n# bad\n")
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("required field `description`", findings[0]["message"])

    def test_empty_description_is_error(self):
        # A blank block scalar parses to an empty string description.
        agent = self.write(
            "agents/empty.md", "---\ndescription: |\n  \nmode: primary\n---\n# e\n"
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("non-empty string", findings[0]["message"])

    def test_mode_outside_allowed_set_is_error(self):
        agent = self.write(
            "agents/odd.md",
            "---\ndescription: does things\nmode: sometimes\n---\n# o\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("must be one of", findings[0]["message"])
        self.assertIn("sometimes", findings[0]["message"])

    def test_valid_agent_produces_no_findings(self):
        self.write(
            "agents/ok.md",
            "---\ndescription: runs builds\nmode: primary\n"
            "model: zai/glm-5.2\npermission:\n  edit: deny\n---\n# ok\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_model_without_slash_is_warning(self):
        agent = self.write(
            "agents/m.md",
            "---\ndescription: d\nmode: subagent\nmodel: glm-5.2\n---\n# m\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("format invalid", findings[0]["message"])

    def test_invalid_permission_string_is_warning(self):
        agent = self.write(
            "agents/p.md",
            "---\ndescription: d\nmode: subagent\npermission: maybe\n---\n# p\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("permission value", findings[0]["message"])

    def test_invalid_permission_map_value_is_warning(self):
        agent = self.write(
            "agents/p.md",
            "---\ndescription: d\nmode: subagent\n"
            "permission:\n  edit: perhaps\n---\n# p\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("perhaps", findings[0]["message"])


class TestValidateCommands(RepoTestCase):
    """validate_commands: commands/*.md schema checks."""

    def test_missing_agent_field_is_error(self):
        cmd = self.write(
            "commands/c.md", "---\ndescription: runs a thing\n---\n# c\n"
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(cmd))
        self.assertIn("required field `agent`", findings[0]["message"])

    def test_agent_reference_without_file_is_error(self):
        cmd = self.write(
            "commands/c.md",
            "---\ndescription: runs a thing\nagent: ghost\n---\n# c\n",
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(cmd))
        self.assertIn("does not resolve", findings[0]["message"])
        self.assertIn("ghost", findings[0]["message"])

    def test_valid_command_produces_no_findings(self):
        self.write("agents/worker.md", "# worker\n")
        self.write(
            "commands/run.md",
            "---\ndescription: does work\nagent: worker\n---\n# run\n",
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(findings, [])

    def test_invalid_model_format_is_warning(self):
        self.write("agents/worker.md", "# worker\n")
        cmd = self.write(
            "commands/run.md",
            "---\ndescription: does work\nagent: worker\n"
            "model: no-slash\n---\n# run\n",
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(cmd))
        self.assertIn("format invalid", findings[0]["message"])


class TestValidateSkills(RepoTestCase):
    """validate_skills: skills/*/SKILL.md schema checks."""

    def test_name_directory_mismatch_is_error(self):
        skill = self.write(
            "skills/go/SKILL.md",
            "---\nname: golang\ndescription: go conventions\n---\n# go\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("does not match", findings[0]["message"])

    def test_missing_description_is_error(self):
        skill = self.write("skills/py/SKILL.md", "---\nname: py\n---\n# py\n")
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("required field `description`", findings[0]["message"])

    def test_missing_name_is_error(self):
        skill = self.write(
            "skills/sh/SKILL.md",
            "---\ndescription: shell conventions\n---\n# sh\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("required field `name`", findings[0]["message"])

    def test_valid_skill_produces_no_findings(self):
        self.write(
            "skills/rust/SKILL.md",
            "---\nname: rust\ndescription: rust conventions\n---\n# rust\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(findings, [])


ROSTER_MD = """\
# Agents

### Agents

| Agent | Role |
|---|---|
| `alpha` | does alpha |

### Commands

| Command | Action |
|---|---|
| `/run` | runs |

### Skills

| Skill | Use for |
|---|---|
| `solid` | clean code |
"""


class TestRosterConsistency(RepoTestCase):
    """roster_consistency: AGENTS.md tables vs agents/commands/skills trees."""

    def write_roster(self, agents_md: str = ROSTER_MD) -> Path:
        """Write a consistent fixture repo: alpha agent, run command, solid skill."""
        self.write("agents/alpha.md", "# alpha\n")
        self.write("commands/run.md", "# run\n")
        self.write("skills/solid/SKILL.md", "# solid\n")
        return self.write("AGENTS.md", agents_md)

    def test_consistent_roster_produces_no_findings(self):
        self.write_roster()
        findings = []
        validate.roster_consistency(self.repo, findings)
        self.assertEqual(findings, [])

    def test_table_listing_agent_without_file_is_error(self):
        roster = ROSTER_MD.replace(
            "| `alpha` | does alpha |",
            "| `alpha` | does alpha |\n| `beta` | does beta |",
        )
        agents_md = self.write_roster(roster)
        findings = []
        validate.roster_consistency(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(agents_md))
        self.assertIn("beta", findings[0]["message"])

    def test_agent_file_missing_from_table_is_error(self):
        agents_md = self.write_roster()
        self.write("agents/ghost.md", "# ghost\n")
        findings = []
        validate.roster_consistency(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(agents_md))
        self.assertIn("ghost", findings[0]["message"])


class TestCrossReference(RepoTestCase):
    """cross_reference: mentions and links across all .md files."""

    def test_unresolved_agent_mention_is_warning(self):
        note = self.write("docs/note.md", "Ask @shamus for help.\n")
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(note))
        self.assertIn("shamus", findings[0]["message"])

    def test_allowlisted_explore_mention_produces_no_finding(self):
        self.write("docs/note.md", "Use @explore to read files.\n")
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(findings, [])

    def test_allowlisted_general_mention_produces_no_finding(self):
        self.write("docs/note.md", "Delegate the task to @general.\n")
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(findings, [])

    def test_unresolved_skill_mention_is_warning(self):
        note = self.write("docs/note.md", "Load the `go` skill first.\n")
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(note))
        self.assertIn("skills/go", findings[0]["message"])

    def test_duplicate_broken_link_reports_once(self):
        # Regression test for the dedup fix in 1986beb: the same broken
        # link twice in one file must yield exactly one warning.
        guide = self.write(
            "docs/guide.md",
            "See [guide](missing/guide.md) here.\n"
            "Again [guide](missing/guide.md).\n",
        )
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(guide))
        self.assertIn("missing/guide.md", findings[0]["message"])
        self.assertIn("does not exist", findings[0]["message"])

    def test_valid_relative_link_produces_no_finding(self):
        self.write("README.md", "readme\n")
        self.write("docs/guide.md", "Back to [home](../README.md).\n")
        findings = []
        validate.cross_reference(self.repo, findings)
        self.assertEqual(findings, [])


class TestModelAllowlist(RepoTestCase):
    """model_allowlist: model fields vs scripts/models.txt."""

    def test_model_not_in_allowlist_is_warning(self):
        self.write("scripts/models.txt", "zai/glm-5.2\nanthropic/claude-sonnet-4\n")
        worker = self.write("agents/worker.md", "---\nmodel: openai/gpt-9\n---\n# w\n")
        findings = []
        validate.model_allowlist(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(worker))
        self.assertIn("allowlist", findings[0]["message"])

    def test_model_in_allowlist_produces_no_finding(self):
        self.write("scripts/models.txt", "zai/glm-5.2\n")
        self.write("agents/worker.md", "---\nmodel: zai/glm-5.2\n---\n# w\n")
        findings = []
        validate.model_allowlist(self.repo, findings)
        self.assertEqual(findings, [])

    def test_missing_models_txt_skips_silently(self):
        self.write("agents/worker.md", "---\nmodel: anything/else\n---\n# w\n")
        findings = []
        validate.model_allowlist(self.repo, findings)
        self.assertEqual(findings, [])


class TestEndToEnd(RepoTestCase):
    """CLI behavior: run scripts/validate.py as a subprocess on fixture repos."""

    def run_validator(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(VALIDATE_PY), "--repo", str(self.repo), *args],
            capture_output=True,
            text=True,
        )

    def test_repo_with_error_exits_1(self):
        self.write("agents/bad.md", "---\nmode: primary\n---\n# bad\n")
        proc = self.run_validator()
        self.assertEqual(proc.returncode, 1)

    def test_clean_repo_exits_0_and_reports_no_findings(self):
        self.write(
            "agents/ok.md",
            "---\ndescription: runs builds\nmode: primary\n"
            "model: zai/glm-5.2\npermission:\n  edit: deny\n---\n# ok\n",
        )
        proc = self.run_validator()
        self.assertEqual(proc.returncode, 0)
        self.assertIn("No findings.", proc.stdout)

    def test_json_output_reports_errors(self):
        self.write("agents/bad.md", "---\nmode: primary\n---\n# bad\n")
        proc = self.run_validator("--json")
        data = json.loads(proc.stdout)
        self.assertEqual(data["total_errors"], 1)
        self.assertEqual(len(data["errors"]), 1)
        self.assertTrue(data["errors"][0]["file"].endswith("agents/bad.md"))
        self.assertIn("description", data["errors"][0]["message"])

    def test_quiet_suppresses_warning_lines_but_not_errors(self):
        # One error (missing description) plus one warning (bad model format).
        self.write(
            "agents/mixed.md",
            "---\nmode: primary\nmodel: badmodel\n---\n# mixed\n",
        )
        proc = self.run_validator("--quiet")
        self.assertEqual(proc.returncode, 1)
        lines = proc.stdout.splitlines()
        self.assertTrue(any(line.startswith("E  ") for line in lines))
        self.assertFalse(any(line.startswith("W  ") for line in lines))
        self.assertIn("suppressed", proc.stdout)
        # Contrast: without --quiet the warning line prints.
        proc = self.run_validator()
        self.assertTrue(any(line.startswith("W  ") for line in proc.stdout.splitlines()))


if __name__ == "__main__":
    unittest.main()

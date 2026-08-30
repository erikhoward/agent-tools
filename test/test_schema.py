"""Schema-modernization tests for scripts/validate.py (GitHub issue #15).

These tests pin the UPDATED opencode schema: two-level permission maps
with quoted wildcard keys, temperature/top_p/steps/hidden/color agent
fields, skill name/description limits, and the command subtask flag.
test_validate.py pins the pre-existing behavior and stays green unchanged.

Stdlib unittest only. Every check that needs a repo tree builds it inside
a tempfile.TemporaryDirectory(); no test reads or writes real repo files.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Make scripts/validate.py importable no matter which CWD unittest runs from.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate  # noqa: E402  (import after the sys.path setup above)


class RepoTestCase(unittest.TestCase):
    """Base class for checks that need a fixture repo tree."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="validate-schema-test-")
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name)

    def write(self, relpath: str, content: str) -> Path:
        """Write content at relpath inside the fixture repo; return the path."""
        path = self.repo / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


GRANULAR_PERMISSION = """\
permission:
  edit: deny
  bash:
    "*": ask
    "git diff": allow
    "git log*": allow
  webfetch: deny
"""


class TestParseFrontmatterSchema(unittest.TestCase):
    """parse_frontmatter: two-level nested maps with quoted keys."""

    def test_two_level_nested_map_with_quoted_keys(self):
        fm = validate.parse_frontmatter("---\n" + GRANULAR_PERMISSION + "---\n")
        self.assertEqual(fm, {
            "permission": {
                "edit": "deny",
                "bash": {"*": "ask", "git diff": "allow", "git log*": "allow"},
                "webfetch": "deny",
            }
        })

    def test_quoted_key_at_first_nested_level_is_stripped(self):
        fm = validate.parse_frontmatter('---\npermission:\n  "edit": deny\n---\n')
        self.assertEqual(fm, {"permission": {"edit": "deny"}})

    def test_three_level_nesting_does_not_crash(self):
        fm = validate.parse_frontmatter(
            "---\nouter:\n  mid:\n    leaf:\n      key: value\n---\n"
        )
        # No crash; the second level survives as a dict.
        self.assertIsInstance(fm.get("outer"), dict)
        self.assertIn("mid", fm["outer"])
        self.assertIsInstance(fm["outer"]["mid"], dict)


class TestValidateAgentsSchema(RepoTestCase):
    """validate_agents: modernized opencode agent schema fields."""

    def test_granular_permission_produces_no_findings(self):
        self.write(
            "agents/ok.md",
            "---\ndescription: d\nmode: subagent\n"
            + GRANULAR_PERMISSION + "---\n# ok\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_bad_granular_permission_value_is_warning_naming_key(self):
        agent = self.write(
            "agents/p.md",
            "---\ndescription: d\nmode: subagent\n"
            "permission:\n"
            "  bash:\n"
            '    "*": maybe\n'
            "---\n# p\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("bash", findings[0]["message"])
        self.assertIn("maybe", findings[0]["message"])

    def test_bad_flat_permission_value_is_warning_naming_key(self):
        agent = self.write(
            "agents/p.md",
            "---\ndescription: d\nmode: subagent\n"
            "permission:\n"
            "  edit: perhaps\n"
            "---\n# p\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("edit", findings[0]["message"])
        self.assertIn("perhaps", findings[0]["message"])

    def test_mixed_flat_and_granular_permission_produces_no_findings(self):
        self.write(
            "agents/ok.md",
            "---\ndescription: d\nmode: subagent\n"
            "permission:\n"
            "  edit: deny\n"
            "  bash:\n"
            '    "*": ask\n'
            "---\n# ok\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_permission_pattern_keys_produce_no_findings(self):
        # Keys are wildcard tool patterns, not a fixed list.
        self.write(
            "agents/ok.md",
            "---\ndescription: d\nmode: subagent\n"
            "permission:\n"
            "  skill:\n"
            '    "git-commit": allow\n'
            '  "mymcp_*": ask\n'
            "---\n# ok\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_temperature_valid_values_produce_no_findings(self):
        self.write(
            "agents/low.md",
            "---\ndescription: d\nmode: subagent\ntemperature: 0.1\n---\n# low\n",
        )
        self.write(
            "agents/zero.md",
            "---\ndescription: d\nmode: subagent\ntemperature: 0\n---\n# zero\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_temperature_invalid_values_are_warnings(self):
        high = self.write(
            "agents/high.md",
            "---\ndescription: d\nmode: subagent\ntemperature: 1.5\n---\n# high\n",
        )
        text = self.write(
            "agents/text.md",
            "---\ndescription: d\nmode: subagent\ntemperature: abc\n---\n# text\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 2)
        self.assertEqual({f["file"] for f in findings}, {str(high), str(text)})
        for f in findings:
            self.assertEqual(f["type"], "W")
            self.assertIn("temperature", f["message"])

    def test_top_p_valid_value_produces_no_findings(self):
        self.write(
            "agents/p.md", "---\ndescription: d\nmode: subagent\ntop_p: 0.9\n---\n# p\n"
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_top_p_invalid_value_is_warning(self):
        agent = self.write(
            "agents/p.md", "---\ndescription: d\nmode: subagent\ntop_p: 2\n---\n# p\n"
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("top_p", findings[0]["message"])
        self.assertIn("2", findings[0]["message"])

    def test_steps_valid_value_produces_no_findings(self):
        self.write(
            "agents/s.md", "---\ndescription: d\nmode: subagent\nsteps: 5\n---\n# s\n"
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_steps_invalid_values_are_warnings(self):
        zero = self.write(
            "agents/zero.md",
            "---\ndescription: d\nmode: subagent\nsteps: 0\n---\n# zero\n",
        )
        word = self.write(
            "agents/word.md",
            "---\ndescription: d\nmode: subagent\nsteps: many\n---\n# word\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 2)
        self.assertEqual({f["file"] for f in findings}, {str(zero), str(word)})
        for f in findings:
            self.assertEqual(f["type"], "W")
            self.assertIn("steps", f["message"])

    def test_hidden_true_with_subagent_mode_produces_no_findings(self):
        self.write(
            "agents/h.md",
            "---\ndescription: d\nmode: subagent\nhidden: true\n---\n# h\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_hidden_true_with_non_subagent_mode_is_warning(self):
        agent = self.write(
            "agents/h.md",
            "---\ndescription: d\nmode: primary\nhidden: true\n---\n# h\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("hidden", findings[0]["message"])
        self.assertIn("subagent", findings[0]["message"])

    def test_hidden_invalid_value_is_warning(self):
        agent = self.write(
            "agents/h.md",
            "---\ndescription: d\nmode: subagent\nhidden: yes\n---\n# h\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(agent))
        self.assertIn("hidden", findings[0]["message"])
        self.assertIn("yes", findings[0]["message"])

    def test_valid_colors_produce_no_findings(self):
        self.write(
            "agents/hex6.md",
            "---\ndescription: d\nmode: subagent\ncolor: #FF5733\n---\n# hex6\n",
        )
        self.write(
            "agents/named.md",
            "---\ndescription: d\nmode: subagent\ncolor: accent\n---\n# named\n",
        )
        self.write(
            "agents/hex3.md",
            "---\ndescription: d\nmode: subagent\ncolor: #0f9\n---\n# hex3\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(findings, [])

    def test_invalid_colors_are_warnings(self):
        named = self.write(
            "agents/named.md",
            "---\ndescription: d\nmode: subagent\ncolor: purple\n---\n# named\n",
        )
        short = self.write(
            "agents/short.md",
            "---\ndescription: d\nmode: subagent\ncolor: #12345\n---\n# short\n",
        )
        findings = []
        validate.validate_agents(self.repo, findings)
        self.assertEqual(len(findings), 2)
        self.assertEqual({f["file"] for f in findings}, {str(named), str(short)})
        for f in findings:
            self.assertEqual(f["type"], "W")
            self.assertIn("color", f["message"])


class TestValidateSkillsSchema(RepoTestCase):
    """validate_skills: name format/length and description length limits."""

    def test_valid_skill_name_produces_no_findings(self):
        self.write(
            "skills/git-release/SKILL.md",
            "---\nname: git-release\ndescription: git conventions\n---\n# git-release\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(findings, [])

    def test_invalid_skill_name_pattern_is_error(self):
        # Directory name equals the field, so only the pattern rule fires.
        skill = self.write(
            "skills/Git_Release/SKILL.md",
            "---\nname: Git_Release\ndescription: d\n---\n# Git_Release\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("name", findings[0]["message"])
        self.assertIn("Git_Release", findings[0]["message"])

    def test_trailing_hyphen_skill_name_is_error(self):
        skill = self.write(
            "skills/tools-/SKILL.md",
            "---\nname: tools-\ndescription: d\n---\n# tools-\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("name", findings[0]["message"])
        self.assertIn("tools-", findings[0]["message"])

    def test_overlong_skill_name_is_error(self):
        long_name = "a" * 65
        skill = self.write(
            f"skills/{long_name}/SKILL.md",
            f"---\nname: {long_name}\ndescription: d\n---\n# long\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("64", findings[0]["message"])

    def test_description_at_1024_chars_produces_no_findings(self):
        self.write(
            "skills/okname/SKILL.md",
            f"---\nname: okname\ndescription: {'x' * 1024}\n---\n# okname\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(findings, [])

    def test_description_over_1024_chars_is_error(self):
        skill = self.write(
            "skills/okname/SKILL.md",
            f"---\nname: okname\ndescription: {'x' * 1025}\n---\n# okname\n",
        )
        findings = []
        validate.validate_skills(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "E")
        self.assertEqual(findings[0]["file"], str(skill))
        self.assertIn("description", findings[0]["message"])
        self.assertIn("1024", findings[0]["message"])


class TestValidateCommandsSchema(RepoTestCase):
    """validate_commands: subtask flag."""

    def test_subtask_true_produces_no_findings(self):
        self.write("agents/worker.md", "# worker\n")
        self.write(
            "commands/run.md",
            "---\ndescription: does work\nagent: worker\nsubtask: true\n---\n# run\n",
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(findings, [])

    def test_subtask_invalid_value_is_warning(self):
        self.write("agents/worker.md", "# worker\n")
        cmd = self.write(
            "commands/run.md",
            "---\ndescription: does work\nagent: worker\nsubtask: yes\n---\n# run\n",
        )
        findings = []
        validate.validate_commands(self.repo, findings)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["type"], "W")
        self.assertEqual(findings[0]["file"], str(cmd))
        self.assertIn("subtask", findings[0]["message"])
        self.assertIn("yes", findings[0]["message"])


if __name__ == "__main__":
    unittest.main()

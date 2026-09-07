import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
RETIRED_PATHS = (
    "skills/solid",
    "agents/solution-architect.md",
    "agents/devops-engineer.md",
    "agents/test-engineer.md",
)


class AssetInventoryTests(unittest.TestCase):
    def test_expected_inventory(self):
        skills = list((REPO / "skills").glob("*/SKILL.md"))
        agents = list((REPO / "agents").glob("*.md"))
        commands = list((REPO / "commands").glob("*.md"))
        self.assertEqual(len(skills), 12)
        self.assertEqual(
            {path.stem for path in agents},
            {
                "principal-architect",
                "database-architect",
                "security-expert",
                "code-analyst",
                "performance-engineer",
                "ui-ux-designer",
            },
        )
        self.assertEqual(len(commands), 6)

    def test_retired_assets_are_absent(self):
        for relative_path in RETIRED_PATHS:
            with self.subTest(path=relative_path):
                self.assertFalse((REPO / relative_path).exists())

    def test_consultants_have_read_only_permissions(self):
        for path in (REPO / "agents").glob("*.md"):
            content = path.read_text()
            with self.subTest(agent=path.stem):
                self.assertRegex(content, r'(?m)^  "\*": deny$')
                for permission in ("read", "list", "glob", "grep"):
                    self.assertRegex(content, rf"(?m)^  {permission}: allow$")
                self.assertIsNone(re.search(r"(?m)^model:", content))


if __name__ == "__main__":
    unittest.main()

"""Keep the CI role's workflow available and tied to the public checks."""

import re
import unittest

from support.repo_root import ROOT
from support import containment


class TestCiWorkflow(unittest.TestCase):
    def read_workflow(self):
        return containment.read_text(
            ROOT / ".github/workflows/ci.yml", ROOT, encoding="utf-8"
        )

    def test_workflow_runs_public_checks_with_materialized_assets(self):
        workflow = self.read_workflow()
        # The reference checks and pixel tests need image bytes, not LFS pointers.
        self.assertRegex(workflow, r"uses: actions/checkout@v4\s+with:\s+lfs: true")
        self.assertRegex(
            workflow,
            r"uses: actions/setup-python@v5\s+with:\s+"
            r"python-version: \$\{\{ matrix\.python-version \}\}",
        )
        self.assertEqual(
            re.findall(r"^\s+- run: (.+)$", workflow, re.MULTILINE),
            ["make check", "make check-references"],
        )
        self.assertIn("  push:", workflow)
        self.assertIn("  pull_request:", workflow)
        self.assertIn("    timeout-minutes: 15", workflow)

    def test_workflow_checks_the_python_floor_and_development_version(self):
        workflow = self.read_workflow()
        matrix = re.search(
            r"^\s+python-version: \[([^\]]+)\]$", workflow, re.MULTILINE
        )
        self.assertIsNotNone(
            matrix, "workflow declares no Python version matrix"
        )
        self.assertEqual(
            ["3.10", "3.12"], re.findall(r"'([^']+)'", matrix.group(1))
        )


if __name__ == "__main__":
    unittest.main()

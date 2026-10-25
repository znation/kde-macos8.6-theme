"""Keep the CI role's workflow available and tied to the public checks."""

import re
import unittest

from support.repo_root import ROOT
from support import containment


class TestCiWorkflow(unittest.TestCase):
    def test_workflow_runs_public_checks_with_materialized_assets(self):
        workflow = containment.read_text(
            ROOT / ".github/workflows/ci.yml", ROOT, encoding="utf-8"
        )
        # The reference checks and pixel tests need image bytes, not LFS pointers.
        self.assertRegex(workflow, r"uses: actions/checkout@v4\s+with:\s+lfs: true")
        self.assertRegex(
            workflow,
            r"uses: actions/setup-python@v5\s+with:\s+python-version: '3\.12'",
        )
        self.assertEqual(
            re.findall(r"^\s+- run: (.+)$", workflow, re.MULTILINE),
            ["make check", "make check-references"],
        )
        self.assertIn("  push:", workflow)
        self.assertIn("  pull_request:", workflow)
        self.assertIn("    timeout-minutes: 15", workflow)


if __name__ == "__main__":
    unittest.main()

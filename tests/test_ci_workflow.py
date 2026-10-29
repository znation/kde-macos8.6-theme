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
        runs = re.findall(r"^\s+- run: (.+)$", workflow, re.MULTILINE)
        # Every one-line run step is a public check; a multiline run step
        # (the render-tool install) is pinned separately below.
        self.assertEqual(
            [run for run in runs if run != "|"],
            ["make check", "make check-references"],
        )
        self.assertIn("  push:", workflow)
        self.assertIn("  pull_request:", workflow)
        self.assertIn("    timeout-minutes: 30", workflow)

    def test_workflow_installs_and_verifies_the_plasma_render_tools(self):
        workflow = self.read_workflow()
        # The render gate (tests/test_render_surface.py::TestRender) silently
        # skips wherever its five Plasma tools are absent; the workflow must
        # install and, by name, verify all five, so a skipped render gate can
        # no longer ride a green job.
        for tool in (
            "dbus-run-session",
            "kwin_wayland",
            "plasmawindowed",
            "plasma-apply-colorscheme",
            "spectacle",
        ):
            self.assertIn(tool, workflow)
        # (?s) lets the pattern cross the shell line continuations.
        self.assertRegex(workflow, r"(?s)apt-get install.*kwin-wayland")
        self.assertRegex(workflow, r"(?s)apt-get install.*plasma-workspace")
        self.assertRegex(workflow, r"(?s)apt-get install.*spectacle")
        self.assertRegex(
            workflow,
            r"render tool missing after install: \$tool",
            "no step catches a tool that survives the install unpackaged",
        )

    def test_workflow_skips_package_install_when_render_tools_exist(self):
        workflow = self.read_workflow()
        self.assertRegex(
            workflow,
            r"if command -v dbus-run-session >/dev/null && \\\s*"
            r"command -v spectacle >/dev/null; then",
        )

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

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
        self.assertRegex(
            workflow,
            r"uses: actions/checkout@[0-9a-f]{40} # v4\s+with:\s+lfs: true",
        )
        self.assertRegex(
            workflow,
            r"uses: actions/setup-python@[0-9a-f]{40} # v5\s+with:\s+"
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
        # skips wherever its five Plasma tools are absent, and the four dialog
        # gates (TestCheckboxDialogRender, TestComboboxDialogRender,
        # TestMenuDialogRender and TestGtkDialogRender) skip wherever the dialog
        # client their dialog render opens is absent (kdialog for the three
        # kdialog modes, zenity for the GTK 4 mode). The workflow must install
        # and, by name, verify all seven tools,
        # so no gate quietly misses the render it byte-compares.
        for tool in (
            "dbus-run-session",
            "kwin_wayland",
            "plasmawindowed",
            "plasma-apply-colorscheme",
            "spectacle",
            "kdialog",
            "zenity",
        ):
            self.assertIn(tool, workflow)
        # (?s) lets the pattern cross the shell line continuations.
        self.assertRegex(workflow, r"(?s)apt-get install.*kwin-wayland")
        self.assertRegex(workflow, r"(?s)apt-get install.*plasma-workspace")
        self.assertRegex(workflow, r"(?s)apt-get install.*spectacle")
        # Ubuntu 26.04 publishes the screenshot package as `kde-spectacle`;
        # 24.04 publishes `spectacle`. The install must follow the name its
        # apt index actually provides, while verifying the unchanged
        # `spectacle` binary.
        self.assertRegex(
            workflow,
            r"(?s)apt-cache show spectacle .*?spectacle_package=kde-spectacle",
            "the install must select the renamed package when the index lacks spectacle",
        )
        self.assertRegex(workflow, r"(?s)apt-get install.*kdialog")
        self.assertRegex(workflow, r"(?s)apt-get install.*zenity")
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
            r"command -v kwin_wayland >/dev/null && \\\s*"
            r"command -v plasmawindowed >/dev/null && \\\s*"
            r"command -v plasma-apply-colorscheme >/dev/null && \\\s*"
            r"command -v spectacle >/dev/null && \\\s*"
            r"command -v kdialog >/dev/null && \\\s*"
            r"command -v zenity >/dev/null; then",
        )

    def test_every_use_pins_a_full_commit_sha(self):
        workflow = self.read_workflow()
        # A mutable version tag (`@v4`) is a retargeting vector: whoever
        # controls the action's repository can move the tag onto any commit
        # and run that code inside this workflow on every push and pull
        # request. Every `uses:` line must therefore name a full 40-hex
        # commit SHA, with the upstream version tag kept as a comment so the
        # pinned release stays legible to a reader.
        uses = re.findall(
            r"^\s*-\s*uses:\s*(\S+)\s+#\s*(\S+)\s*$", workflow, re.MULTILINE
        )
        self.assertTrue(uses, "workflow declares no third-party actions")
        for reference, tag in uses:
            name, _, pinned = reference.partition("@")
            self.assertTrue(name, f"uses line without an action name: {reference}")
            self.assertRegex(
                pinned,
                r"^[0-9a-f]{40}$",
                f"{name} is not pinned to a full 40-hex commit SHA",
            )
            self.assertRegex(
                tag,
                r"^v\d",
                f"{name} does not name its upstream version tag in a comment",
            )

    def test_workflow_runs_the_suite_on_the_headless_qt_platform(self):
        workflow = self.read_workflow()
        # The runner has no display; plasma-apply-colorscheme and
        # plasma-apply-desktoptheme abort when Qt's xcb plugin cannot connect.
        # The render session pins its own clients back to `wayland`.
        self.assertRegex(
            workflow,
            r"(?m)^\s+QT_QPA_PLATFORM: offscreen$",
            "the check job must select a headless Qt platform",
        )

    def test_workflow_pins_the_python_development_version(self):
        workflow = self.read_workflow()
        matrix = re.search(
            r"^\s+python-version: \[([^\]]+)\]$", workflow, re.MULTILINE
        )
        self.assertIsNotNone(
            matrix, "workflow declares no Python version matrix"
        )
        self.assertEqual(
            ["3.13"],
            re.findall(r"'([^']+)'", matrix.group(1)),
            "workflow must pin exactly Python 3.13, the development interpreter",
        )


if __name__ == "__main__":
    unittest.main()

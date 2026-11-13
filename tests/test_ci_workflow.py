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
        # skips wherever its six Plasma tools are absent, and the fifteen dialog
        # gates (TestCheckboxDialogRender, TestComboboxDialogRender,
        # TestLineInputDialogRender, TestMenuDialogRender,
        # TestRadioDialogRender,
        # TestCalendarDialogRender, TestCalendarLocaleDialogRender,
        # TestColorDialogRender,
        # TestIconDialogRender, TestProgressbarDialogRender,
        # TestSliderDialogRender, TestTextboxDialogRender,
        # TestGtkDialogRender, TestInactiveDialogRender and
        # TestFileDialogRender) skip wherever the
        # dialog client their dialog
        # render opens is absent (kdialog for the thirteen kdialog modes, zenity
        # for the GTK 4 mode). The workflow must
        # install and, by name, verify all eight tools,
        # so no gate quietly misses the render it byte-compares.
        for tool in (
            "dbus-run-session",
            "kwin_wayland",
            "plasmawindowed",
            "plasma-apply-colorscheme",
            "spectacle",
            "ksplashqml",
            "kdialog",
            "zenity",
        ):
            self.assertIn(tool, workflow)
        # (?s) lets the pattern cross the shell line continuations.
        self.assertRegex(workflow, r"(?s)apt-get install.*kwin-wayland")
        self.assertRegex(workflow, r"(?s)apt-get install.*plasma-workspace")
        # The applet render opens org.kde.plasma.calculator, which the runner
        # image does not preinstall; the package must arrive with the tools.
        self.assertRegex(
            workflow, r"(?s)apt-get install.*plasma-widgets-addons"
        )
        # The GPU-less runner needs Mesa's software EGL driver for KWin's
        # virtual backend.
        self.assertRegex(
            workflow, r"(?s)apt-get install.*libgl1-mesa-dri"
        )
        # Spectacle's OCR probe otherwise warns through three candidates and
        # leaves the optional path unavailable on the runner.
        self.assertRegex(
            workflow, r"(?s)apt-get install.*libtesseract5"
        )
        self.assertRegex(
            workflow, r"(?s)apt-get install.*tesseract-ocr-eng"
        )
        self.assertRegex(workflow, r"(?s)apt-get install.*spectacle")
        # Ubuntu 26.04 moved the Aurorae decoration engine out of kwin-common.
        self.assertRegex(
            workflow,
            r"(?s)apt-cache show kwin-style-aurorae .*?"
            r"aurorae_package=kwin-style-aurorae",
            "the install must select the split Aurorae engine package",
        )
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

    def test_workflow_provisions_and_verifies_imagemagick_convert(self):
        workflow = self.read_workflow()
        # tools/jpeg_convert.py resolves the literal `convert` executable with
        # shutil.which; the JPEG sampler tests have no skip, so the hosted
        # runner must provide it. The provisioning sits after the render-tool
        # block's closing check, so it runs whether or not the Plasma tools
        # were already present (the block's `else` only runs when they are
        # missing).
        anchor = "calculator applet missing after install"
        self.assertIn(anchor, workflow)
        tail = workflow.split(anchor, 1)[1]
        self.assertRegex(
            tail,
            r"(?s)if ! command -v convert >/dev/null; then.*?"
            r"apt-get install.*imagemagick",
            "the ImageMagick package must be installed when convert is absent",
        )
        self.assertRegex(
            tail,
            r"(?s)command -v convert >/dev/null\s*\\?\s*\|\|\s*\{[^}]*convert missing after install",
            "no step catches a convert that survives the install unpackaged",
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
            r"command -v ksplashqml >/dev/null && \\\s*"
            r"command -v kdialog >/dev/null && \\\s*"
            r"command -v zenity >/dev/null && \\\s*"
            r"has_calculator_applet; then",
        )

    def test_every_use_pins_a_full_commit_sha(self):
        self.assert_action_pins(self.read_workflow())

    def assert_action_pins(self, workflow):
        # A mutable version tag (`@v4`) is a retargeting vector: whoever
        # controls the action's repository can move the tag onto any commit
        # and run that code inside this workflow on every push and pull
        # request. Every `uses:` line must therefore name a full 40-hex
        # commit SHA, with the upstream version tag kept as a comment so the
        # pinned release stays legible to a reader.
        uses = re.findall(
            r"^[ \t]*(?:-[ \t]+)?uses:[ \t]*([^\n]*)$", workflow, re.MULTILINE
        )
        self.assertTrue(uses, "workflow declares no third-party actions")
        for declaration in uses:
            reference, comment, tag = declaration.partition("#")
            reference, tag = reference.strip(), tag.strip()
            self.assertTrue(
                comment and tag, "action must name its version tag in a comment"
            )
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
        check_job = re.search(
            r"(?ms)^  check:\n(?P<body>.*?)(?=^  [^\s].*:\s*$|\Z)",
            workflow,
        )
        self.assertIsNotNone(check_job, "workflow has no check job")
        job_body = check_job.group("body")
        job_env = re.search(
            r"(?ms)^    env:\n(?P<body>(?:^      .*\n|^\s*\n)*)",
            job_body,
        )
        self.assertIsNotNone(job_env, "check job has no job-level environment")
        env = job_env.group("body")
        # The runner has no display; plasma-apply-colorscheme and
        # plasma-apply-desktoptheme abort when Qt's xcb plugin cannot connect.
        # The render session pins its own clients back to `wayland`.
        self.assertRegex(
            env,
            r"(?m)^      QT_QPA_PLATFORM: offscreen$",
            "the check job must select a headless Qt platform",
        )
        # KWin's virtual backend still needs an EGL driver; the runner has no
        # GPU, and Mesa otherwise tries Zink and fails before the session
        # paints. LIBGL_ALWAYS_SOFTWARE=1 provides that software driver; a
        # pinned MESA_LOADER_DRIVER_OVERRIDE=llvmpipe (added with it in
        # a005ece42, so the override never carried its own evidence — the
        # hosted 18ded7fe run failed at the install step before any test)
        # breaks KWin's virtual session on a real-GPU host with a KMS
        # dumb-buffer permission denial. No driver name is pinned.
        self.assertRegex(env, r"(?m)^      LIBGL_ALWAYS_SOFTWARE: '1'$")
        self.assertNotRegex(
            env, r"(?m)^      MESA_LOADER_DRIVER_OVERRIDE:"
        )
        self.assertNotRegex(
            env, r"(?m)^      GALLIUM_DRIVER:"
        )

    def test_workflow_pins_the_runner_image(self):
        workflow = self.read_workflow()
        # The package names the install step selects are 26.04's; the
        # moving ubuntu-latest label must not decide the environment.
        self.assertRegex(workflow, r"(?m)^\s+runs-on: ubuntu-26\.04$")
        self.assertNotRegex(workflow, r"(?m)^\s+runs-on: ubuntu-latest$")

    def test_action_pin_check_covers_every_step(self):
        valid = "      - uses: actions/checkout@" + "a" * 40 + " # v4\n"
        for declaration in (
            "      - uses: example/action@v1\n",
            "      - uses: example/action@v1 # v1\n",
            "      - name: Another action\n        uses: example/action@v1 # v1\n",
            "      - uses: example/action@" + "b" * 40 + "\n",
        ):
            with self.subTest(declaration=declaration):
                with self.assertRaises(AssertionError):
                    self.assert_action_pins(valid + declaration)
        self.assert_action_pins(
            valid + "      - name: Pinned action\n        uses: example/action@"
            + "b" * 40 + " # v1\n"
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

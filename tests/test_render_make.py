"""Make's safe selector for the existing render surfaces."""

import shutil
import tempfile
import unittest
from pathlib import Path

from support import theme_install
from support.process_assertions import assert_failed, assert_succeeded


class TestRenderMake(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="render-make-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.python = self.root / "python"
        self.record = self.root / "argv"

    def env(self):
        self.python.write_text(
            "#!/bin/sh\n"
            'if [ "$1" = "-c" ]; then exit 0; fi\n'
            f'for arg do printf "%s\\n" "$arg" >> "{self.record}"; done\n'
        )
        self.python.chmod(0o755)
        env = theme_install.make_env("PYTHON", "RENDER_MODE", "RENDER_OUTPUT")
        env["PYTHON"] = str(self.python)
        return env

    def run_make(self, mode=None, output="capture path.png"):
        args = ["render", f"RENDER_OUTPUT={output}"]
        env = self.env()
        if mode is not None:
            env["RENDER_MODE"] = mode
        return theme_install.run_make(args, env=env)

    def test_default_and_explicit_modes_pass_literal_argv(self):
        modes = (
            (None, []),
            ("calculator", []),
            ("checkbox-dialog", ["--checkbox-dialog"]),
            ("combobox-dialog", ["--combobox-dialog"]),
            ("menu-dialog", ["--menu-dialog"]),
            ("calendar-dialog", ["--calendar-dialog"]),
            ("color-dialog", ["--color-dialog"]),
            ("progressbar-dialog", ["--progressbar-dialog"]),
            ("slider-dialog", ["--slider-dialog"]),
            ("textbox-dialog", ["--textbox-dialog"]),
            ("gtk-dialog", ["--gtk-dialog"]),
        )
        for mode, flags in modes:
            with self.subTest(mode=mode):
                self.record.unlink(missing_ok=True)
                result = self.run_make(mode)
                assert_succeeded(self, result)
                self.assertEqual(
                    ["tools/render_surface.py", *flags, "--", "capture path.png"],
                    self.record.read_text().splitlines(),
                )

    def test_trimmed_mode_and_dash_leading_path(self):
        result = self.run_make("  gtk-dialog  ", "-capture.png")
        assert_succeeded(self, result)
        self.assertEqual(
            ["tools/render_surface.py", "--gtk-dialog", "--", "-capture.png"],
            self.record.read_text().splitlines(),
        )

    def test_invalid_modes_fail_before_renderer_and_do_not_echo_value(self):
        injected_file = self.root / "sentinel"
        for mode in (
            "",
            "unknown",
            "gtk-dialog menu-dialog",
            "$(touch sentinel)",
            f"$(shell touch {injected_file})",
            "\x01",
        ):
            with self.subTest(mode=mode):
                self.record.unlink(missing_ok=True)
                result = self.run_make(mode)
                assert_failed(self, result)
                self.assertIn("RENDER_MODE", result.stderr)
                self.assertIn("calculator", result.stderr)
                if mode:
                    self.assertNotIn(mode, result.stderr)
                self.assertFalse(self.record.exists())
                self.assertFalse(injected_file.exists())

    def test_help_documents_mode_default(self):
        result = theme_install.run_make(["help"], env=self.env())
        assert_succeeded(self, result)
        self.assertIn("RENDER_MODE=name", result.stdout)
        self.assertIn("default calculator", result.stdout)


if __name__ == "__main__":
    unittest.main()

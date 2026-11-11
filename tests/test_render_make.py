"""Make's safe selector for the existing render surfaces."""

import shutil
import tempfile
import unittest
from pathlib import Path

from support import repo_root, theme_install
from support.process_assertions import assert_failed, assert_succeeded
from tools.render_dialogs import DIALOG_MODES


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
            ("lineedit-dialog", ["--lineedit-dialog"]),
            ("menu-dialog", ["--menu-dialog"]),
            ("radiolist-dialog", ["--radiolist-dialog"]),
            ("calendar-dialog", ["--calendar-dialog"]),
            ("color-dialog", ["--color-dialog"]),
            ("icon-dialog", ["--icon-dialog"]),
            ("progressbar-dialog", ["--progressbar-dialog"]),
            ("slider-dialog", ["--slider-dialog"]),
            ("textbox-dialog", ["--textbox-dialog"]),
            ("gtk-dialog", ["--gtk-dialog"]),
            ("inactive-dialog", ["--inactive-dialog"]),
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

    def test_makefile_mode_list_matches_dialog_modes_table(self):
        """The Makefile's RENDER_MODE_VALUES covers exactly the shared table's modes.

        The `render` recipe's refusal text and `make help`'s mode line derive
        from that Makefile variable, so a dialog mode added to the shared
        table without it (or a Makefile mode with no table entry) must fail
        here rather than reach the refusal as an undocumented value. The
        message's wording order is not the table's, so the modes are compared
        as a set; a duplicated mode would make the refusal suggest a value
        twice, so the list must also be duplicate-free.
        """
        makefile = repo_root.ROOT / "Makefile"
        declared = None
        for line in makefile.read_text().splitlines():
            if line.startswith("RENDER_MODE_VALUES :="):
                declared = line.split(":=", 1)[1].split()
                break
        self.assertIsNotNone(
            declared, "Makefile must declare RENDER_MODE_VALUES"
        )
        self.assertEqual(
            {"calculator", *[mode.flag[2:] for mode in DIALOG_MODES]},
            set(declared),
        )
        self.assertEqual(len(declared), len(set(declared)))

    def test_help_documents_mode_default(self):
        result = theme_install.run_make(["help"], env=self.env())
        assert_succeeded(self, result)
        self.assertIn("RENDER_MODE=name", result.stdout)
        self.assertIn("default calculator", result.stdout)


if __name__ == "__main__":
    unittest.main()

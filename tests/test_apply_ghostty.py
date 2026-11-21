"""The Ghostty selection CLI, `tools/apply_ghostty.py`, and its make targets.

Each test runs the tool in-process with `XDG_DATA_HOME`, `XDG_CONFIG_HOME`,
`HOME` and `PATH` pointed at a temp root. `PATH` holds a stub `ghostty` unless
a test needs it absent. The expected block is written out from the marker text
in the backlog entry.
"""

import os
import stat
import unittest

from support import theme_install
from support.cli_fixtures import run_main_with_env
from support.process_assertions import assert_succeeded
from support.tmp_dir import make_tmp_dir
from tools import apply_ghostty

THEME_REL = os.path.join(
    "ghostty", "themes", "org.macos8.desktop", "Platinum"
)
BEGIN = b"# >>> Platinum theme (managed by make apply-ghostty) >>>\n"
END = b"# <<< Platinum theme <<<\n"


class GhosttyCase(unittest.TestCase):
    def setUp(self):
        self.root = make_tmp_dir(self)
        self.data = self.root / "data"
        self.config = self.root / "config"
        self.home = self.root / "home"
        self.bin = self.root / "bin"
        self.empty_bin = self.root / "empty-bin"
        for path in (self.bin, self.empty_bin):
            path.mkdir()
        stub = self.bin / "ghostty"
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        self.theme = self.data / THEME_REL
        self.theme.parent.mkdir(parents=True)
        self.theme.write_bytes(b"background = #ffffff\n")
        self.target = self.config / "ghostty" / "config.ghostty"
        self.legacy = self.config / "ghostty" / "config"

    def env(self, path=None):
        return {
            "XDG_DATA_HOME": str(self.data),
            "XDG_CONFIG_HOME": str(self.config),
            "HOME": str(self.home),
            "PATH": str(self.bin if path is None else path),
        }

    def run_tool(self, *args, path=None):
        return run_main_with_env(
            apply_ghostty.main, "apply_ghostty", args, self.env(path)
        )

    def block(self):
        return BEGIN + b"theme = " + os.fsencode(self.theme) + b"\n" + END


class TestApply(GhosttyCase):
    def test_creates_the_file_with_only_the_block_when_absent(self):
        result = self.run_tool("--optional")
        assert_succeeded(self, result)
        self.assertEqual(self.target.read_bytes(), self.block())

    def test_block_names_the_absolute_installed_theme_path(self):
        assert_succeeded(self, self.run_tool("--optional"))
        expected = (
            b"theme = " + os.fsencode(self.data)
            + b"/ghostty/themes/org.macos8.desktop/Platinum\n"
        )
        self.assertIn(expected, self.target.read_bytes())

    def test_foreign_lines_before_and_after_the_block_survive(self):
        self.target.parent.mkdir(parents=True)
        before = b"font-size = 12\nbackground = #000000\n"
        after = b"cursor-style = bar\n"
        self.target.write_bytes(before + self.block() + after)
        assert_succeeded(self, self.run_tool("--optional"))
        self.assertEqual(self.target.read_bytes(), before + self.block() + after)

    def test_appends_after_foreign_lines_and_keeps_them_byte_for_byte(self):
        self.target.parent.mkdir(parents=True)
        original = b"font-size = 12\n"
        self.target.write_bytes(original)
        assert_succeeded(self, self.run_tool("--optional"))
        self.assertEqual(self.target.read_bytes(), original + self.block())

    def test_repeat_apply_is_byte_identical(self):
        assert_succeeded(self, self.run_tool("--optional"))
        first = self.target.read_bytes()
        assert_succeeded(self, self.run_tool("--optional"))
        self.assertEqual(self.target.read_bytes(), first)

    def test_legacy_config_file_is_never_written(self):
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_bytes(b"theme = Other\n")
        before = self.legacy.stat().st_mtime_ns
        assert_succeeded(self, self.run_tool("--optional"))
        self.assertEqual(self.legacy.read_bytes(), b"theme = Other\n")
        self.assertEqual(self.legacy.stat().st_mtime_ns, before)

    def test_missing_theme_file_is_refused_naming_make_install(self):
        self.theme.unlink()
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("make install", result.stderr)
        self.assertFalse(self.target.exists())

    def test_symlinked_target_is_refused_and_its_file_is_untouched(self):
        self.target.parent.mkdir(parents=True)
        elsewhere = self.root / "elsewhere"
        elsewhere.write_bytes(b"x = 1\n")
        self.target.symlink_to(elsewhere)
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("symbolic link", result.stderr)
        self.assertEqual(elsewhere.read_bytes(), b"x = 1\n")

    def test_unbalanced_markers_are_refused_and_the_file_is_untouched(self):
        self.target.parent.mkdir(parents=True)
        original = BEGIN + b"font-size = 12\n"
        self.target.write_bytes(original)
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unbalanced", result.stderr)
        self.assertEqual(self.target.read_bytes(), original)

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_uncreatable_config_directory_is_refused_with_exit_2(self):
        self.config.mkdir()
        self.config.chmod(0o555)
        self.addCleanup(self.config.chmod, 0o755)
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cannot create", result.stderr)
        self.assertFalse(self.target.parent.exists())

    def test_optional_without_ghostty_on_path_writes_nothing_and_exits_0(self):
        result = self.run_tool("--optional", path=self.empty_bin)
        assert_succeeded(self, result)
        self.assertIn("ghostty is not on PATH", result.stdout)
        self.assertFalse(self.target.exists())

    def test_without_optional_a_missing_ghostty_still_writes_the_block(self):
        assert_succeeded(self, self.run_tool(path=self.empty_bin))
        self.assertEqual(self.target.read_bytes(), self.block())


class TestRemove(GhosttyCase):
    def test_restores_the_original_bytes_of_a_preexisting_file(self):
        self.target.parent.mkdir(parents=True)
        original = b"background = #000000\nfont-size = 12\n"
        self.target.write_bytes(original)
        assert_succeeded(self, self.run_tool("--optional"))
        assert_succeeded(self, self.run_tool("--remove"))
        self.assertEqual(self.target.read_bytes(), original)

    def test_deletes_a_file_that_held_only_the_block(self):
        assert_succeeded(self, self.run_tool("--optional"))
        assert_succeeded(self, self.run_tool("--remove"))
        self.assertFalse(self.target.exists())

    def test_missing_file_is_a_no_op(self):
        assert_succeeded(self, self.run_tool("--remove"))
        self.assertFalse(self.target.exists())

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_undeletable_file_is_refused_with_exit_2(self):
        assert_succeeded(self, self.run_tool("--optional"))
        self.target.parent.chmod(0o555)
        self.addCleanup(self.target.parent.chmod, 0o755)
        result = self.run_tool("--remove")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cannot remove", result.stderr)
        self.assertEqual(self.target.read_bytes(), self.block())

    def test_leaves_the_legacy_config_file_alone(self):
        self.legacy.parent.mkdir(parents=True)
        self.legacy.write_bytes(b"theme = Other\n")
        assert_succeeded(self, self.run_tool("--optional"))
        assert_succeeded(self, self.run_tool("--remove"))
        self.assertEqual(self.legacy.read_bytes(), b"theme = Other\n")


class TestUnwritableConfigHome(GhosttyCase):
    """A config home that cannot be changed is refused with the documented exit 2."""

    def lock_config_home(self):
        self.config.mkdir(parents=True)
        self.config.chmod(stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(self.config.chmod, stat.S_IRWXU)

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_apply_refuses_a_config_home_it_cannot_create_a_directory_in(self):
        self.lock_config_home()
        result = self.run_tool()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(str(self.config / "ghostty"), result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    @unittest.skipIf(os.geteuid() == 0, "root ignores directory permissions")
    def test_remove_refuses_a_block_file_it_cannot_delete(self):
        ghostty = self.config / "ghostty"
        ghostty.mkdir(parents=True)
        self.target.write_bytes(self.block())
        ghostty.chmod(stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(ghostty.chmod, stat.S_IRWXU)
        result = self.run_tool("--remove")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(str(self.target), result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.target.read_bytes(), self.block())


class TestMakeTargets(unittest.TestCase):
    def test_apply_runs_the_ghostty_step_after_the_cursor_step(self):
        result = theme_install.run_make(
            ["-n", "apply"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_ghostty.py --optional", result.stdout)
        self.assertLess(
            result.stdout.index("tools/apply_cursor.py --optional"),
            result.stdout.index("tools/apply_ghostty.py --optional"),
        )

    def test_remove_ghostty_runs_the_tool_with_remove(self):
        result = theme_install.run_make(
            ["-n", "remove-ghostty"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_ghostty.py --remove", result.stdout)


if __name__ == "__main__":
    unittest.main()

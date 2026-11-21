"""Tests for Konsole profile refusals and command failures.

These pin refusals for a squatted ``konsole`` directory, unsafe or unresolved
profile names, symlinked destinations, and an unresolved config home, plus
failures reported by the Konsole commands.
"""

from __future__ import annotations

import stat
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.theme_install import write_file
from support.konsole_font_case import (
    FOREIGN_PROFILE,
    KonsoleError,
    StubKonsoleToolsTestCase,
)


class TestFallbackDirectoryRefusals(StubKonsoleToolsTestCase):
    """A regular file where the ``konsole`` data directory belongs is refused.

    The fallback path creates that directory before any write; a file
    squatting on it must stop the apply with the actionable diagnostic, and
    no selection is written.
    """

    def test_a_regular_file_at_the_konsole_data_directory_is_refused(self):
        write_file(self.profile_dir, "squatting file\n")
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn("it is not a directory", str(raised.exception))
        self.assertFalse(self.konsolerc.exists())


class TestRefusals(StubKonsoleToolsTestCase):
    def assert_refused(self, message_part, profile="Mine.profile"):
        """The helper raises, prints nothing, and writes nothing."""
        self.write_konsolerc(f"[Desktop Entry]\nDefaultProfile={profile}\n")
        before = self.read(self.konsolerc)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn(message_part, str(raised.exception))
        self.assertEqual(before, self.read(self.konsolerc))
        self.assertFalse(self.profile_dir.exists())

    def test_an_absolute_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="/etc/Own.profile")

    def test_a_traversal_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="../Own.profile")

    def test_a_separated_profile_name_is_refused(self):
        self.assert_refused("must be a plain file name", profile="sub/Own.profile")

    def test_a_backslash_separated_profile_name_is_refused(self):
        # A backslash is a separator on Windows and is legal inside a POSIX
        # file name, so the name is refused by spelling rather than left to
        # the filesystem: a "sub\Own.profile" must not be resolved at all.
        for name in ("sub\\Own.profile", "..\\Own.profile"):
            with self.subTest(name=name):
                self.assert_refused("must be a plain file name", profile=name)

    def test_the_dot_names_are_refused(self):
        for name in (".", ".."):
            with self.subTest(name=name):
                self.assert_refused("must be a plain file name", profile=name)

    def test_an_unresolvable_profile_name_is_refused(self):
        self.assert_refused(
            "does not exist in konsole/", profile="Gone.profile"
        )

    def test_a_symlinked_profile_is_refused(self):
        target = self.root / "real.profile"
        target.write_text("[Appearance]\nFont=Liberation Mono\n", encoding="utf-8")
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile_dir.mkdir(parents=True)
        self.profile = self.profile_dir / "Mine.profile"
        self.profile.symlink_to(target)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn("symbolic link", str(raised.exception))
        self.assertEqual(
            "[Appearance]\nFont=Liberation Mono\n", self.read(target)
        )

    def test_a_symlinked_copy_destination_is_refused(self):
        self.write_profile(self.system, "Mine.profile", FOREIGN_PROFILE)
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        target = self.root / "real.profile"
        target.write_text("[General]\nName=Real\n", encoding="utf-8")
        self.profile_dir.mkdir(parents=True)
        (self.profile_dir / "Mine.profile").symlink_to(target)
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font()
        self.assertIn("symbolic link", str(raised.exception))
        self.assertEqual("[General]\nName=Real\n", self.read(target))

    def test_an_unresolvable_config_home_is_refused(self):
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        with self.assertRaises(KonsoleError) as raised:
            self.apply_font(env=self.env_without_homes())
        self.assertIn("XDG_CONFIG_HOME", str(raised.exception))
        self.assertIn("HOME", str(raised.exception))


class TestCommandFailures(StubKonsoleToolsTestCase):
    def setUp(self):
        super().setUp()
        self.write_konsolerc("[Desktop Entry]\nDefaultProfile=Mine.profile\n")
        self.profile = self.write_profile(self.data, "Mine.profile", FOREIGN_PROFILE)

    def test_a_failing_read_exits_1_with_the_tail(self):
        self.fail_stub("kreadconfig6", 4)
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kreadconfig6 exited 4", stderr)
        self.assertIn("exploded", stderr)

    def test_a_failing_font_write_exits_1_and_writes_nothing(self):
        self.fail_stub("kwriteconfig6", 6)
        before = self.profile.read_bytes()
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 6", stderr)
        self.assertEqual(before, self.profile.read_bytes())

    def test_an_unrunnable_writer_exits_2_without_a_traceback(self):
        self.writer.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        self.writer.chmod(self.writer.stat().st_mode | stat.S_IXUSR)
        status, stderr = self.apply_font()
        self.assertEqual(2, status)
        self.assertIn("cannot run kwriteconfig6", stderr)
        self.assertIn("apply_theme: error:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_a_failing_fallback_write_stops_before_the_selection(self):
        # The fallback branch writes the profile before it selects it, so a
        # failed profile write must leave konsolerc without a selection.
        self.write_stub_body(
            "kwriteconfig6",
            'case "$*" in *--key\\ Name*) echo profile write failed >&2\n'
            "exit 7;; esac\nexit 0",
        )
        self.write_konsolerc("[General]\nColorScheme=BreezeLight\n")
        before = self.read(self.konsolerc)
        status, stderr = self.apply_font()
        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 7", stderr)
        self.assertEqual(before, self.read(self.konsolerc))

    def write_stub_body(self, name, body):
        self._write_stub(self.bin / name, f"#!/bin/sh\n{body}\n")


if __name__ == "__main__":
    unittest.main()

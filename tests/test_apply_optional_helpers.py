"""Direct tests for the optional-selection boundary in tools/apply_optional.

This also covers the Kvantum data-home note, which drives
``select_kvantum_theme`` through the stubs in ``support.apply_theme_stubs``.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.apply_theme_stubs import ApplyStubTestCase
from tools import apply_optional, apply_theme


class TestOptionalSelectionHelpers(unittest.TestCase):
    """Pin direct optional helper behavior against a narrowed PATH."""

    def test_run_optional_selections_notes_both_missing_tools_and_returns_0(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        empty_bin = root / "bin"
        empty_bin.mkdir()
        env = {"PATH": str(empty_bin)}
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=False):
            with contextlib.redirect_stderr(stderr):
                status = apply_optional.run_optional_selections(
                    root, dict(os.environ), 60.0
                )
        self.assertEqual(0, status)
        text = stderr.getvalue()
        self.assertIn("apply_theme: note:", text)
        self.assertIn("kvantummanager is not on PATH", text)
        self.assertIn("neither qdbus6 nor qdbus is on PATH", text)

    def test_run_best_effort_success_prints_nothing(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        stub_bin = root / "bin"
        stub_bin.mkdir()
        stub = stub_bin / "tool"
        stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        stderr = io.StringIO()
        with mock.patch.dict(os.environ, {"PATH": str(stub_bin)}, clear=False):
            with contextlib.redirect_stderr(stderr):
                apply_optional.run_best_effort(
                    root,
                    dict(os.environ),
                    ["tool"],
                    "tool.log",
                    60.0,
                    label="tool call",
                    consequence="nothing happens",
                )
        self.assertEqual("", stderr.getvalue())
        self.assertTrue((root / "tool.log").exists())

    def test_run_best_effort_start_error_names_the_command_and_consequence(self):
        root = Path(tempfile.mkdtemp(prefix="theme-apply-optional-test-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        stderr = io.StringIO()
        with mock.patch.object(
            apply_optional, "run_logged", side_effect=OSError("exec format error")
        ):
            with contextlib.redirect_stderr(stderr):
                apply_optional.run_best_effort(
                    root,
                    {},
                    ["broken-tool"],
                    "tool.log",
                    3.0,
                    label="optional selection",
                    consequence="the widgets use another style",
                )
        self.assertEqual(
            "apply_theme: note: optional selection could not be started: "
            "exec format error; the widgets use another style\n",
            stderr.getvalue(),
        )


class TestKvantumDataHomeNote(ApplyStubTestCase):
    """The apply-time note when Kvantum can only resolve our theme from the
    default data home.

    Kvantum joins its literal ``$HOME/.local/share/themes`` search path from
    ``$HOME``, so a selection written under another data home still succeeds
    while the engine silently keeps drawing its built-in default theme. These
    drive ``apply_optional.select_kvantum_theme`` directly through the
    stubbed ``kvantummanager`` machinery in
    ``support.apply_theme_stubs.ApplyStubTestCase``, one env shape per test, and
    assert the selection argv and status never change with the note.
    """

    def note(self, home, resolved):
        """Return the one-note full stderr line for *home* and *resolved*."""
        return (
            "apply_theme: note: the Kvantum engine reads its theme directory "
            f"only under the default data home {home}/.local/share, not the "
            f"resolved {resolved}; widgets draw Kvantum's built-in default "
            "theme until themes/org.macos8.desktop/Kvantum exists there"
        )

    def select(self):
        """Run the selection against the stubbed PATH, returning (status, stderr)."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = apply_optional.select_kvantum_theme(
                self.root, dict(os.environ), apply_theme.COMMAND_TIMEOUT
            )
        return status, stderr.getvalue()

    def test_a_non_default_absolute_data_home_prints_the_note(self):
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual([self.note(self.home, self.data)], stderr.splitlines())
        self.assertEqual(
            ["kvantummanager --set org.macos8.desktop"], self.recorded()
        )

    def theme_directory_at_default(self):
        """Create the theme directory the engine's default home resolves."""
        directory = (
            self.home / ".local" / "share" / "themes" / "org.macos8.desktop" / "Kvantum"
        )
        directory.mkdir(parents=True)
        return directory

    def test_a_theme_already_at_the_default_data_home_stays_silent(self):
        # The note exists for the selection the engine's literal search path
        # cannot reach; when the default home already holds the theme
        # directory (an earlier install under the default data home) the
        # engine can reach the selection and the warning would be false.
        self.theme_directory_at_default()
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)
        self.assertEqual(
            ["kvantummanager --set org.macos8.desktop"], self.recorded()
        )

    def test_a_wrongly_named_directory_at_the_default_home_still_warns(self):
        # Only the exact themes/org.macos8.desktop/Kvantum path silences the
        # note; a sibling-named theme cannot be what the engine resolves, so
        # the check must not stop at the themes directory or the theme name.
        for layout in (
            "themes/org.macos8.desktop/not-Kvantum",
            "themes/other.theme/Kvantum",
            "Kvantum/org.macos8.desktop",
        ):
            with self.subTest(layout=layout):
                (self.home / ".local" / "share" / layout).mkdir(parents=True)
                status, stderr = self.select()
                self.assertEqual(0, status, stderr)
                self.assertEqual(
                    [self.note(self.home, self.data)], stderr.splitlines()
                )

    def test_a_plain_file_at_the_theme_directory_path_still_warns(self):
        # The silencing check is for the theme *directory* the engine reads.
        # A regular file at that same path is not one, so the note still
        # names the gap; an existence test in place of the directory test
        # would wrongly silence it.
        kvantum = (
            self.home / ".local" / "share" / "themes" / "org.macos8.desktop" / "Kvantum"
        )
        kvantum.parent.mkdir(parents=True)
        kvantum.write_text("", encoding="utf-8")
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual([self.note(self.home, self.data)], stderr.splitlines())

    def test_the_default_data_home_below_home_stays_silent(self):
        with mock.patch.dict(
            os.environ, {"XDG_DATA_HOME": str(self.home / ".local" / "share")}
        ):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_unset_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("XDG_DATA_HOME", None)
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_empty_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": ""}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_relative_data_home_falls_back_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": "relative/data"}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_an_unset_home_leaves_no_default_to_name_and_stays_silent(self):
        # The resolved home comes from the absolute XDG_DATA_HOME alone, but
        # without a usable HOME there is no default to name, so the check
        # must skip instead of printing a half-substituted note.
        with mock.patch.dict(os.environ):
            os.environ.pop("HOME", None)
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_relative_home_leaves_no_default_to_name_and_stays_silent(self):
        with mock.patch.dict(os.environ, {"HOME": "relative/home"}):
            status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual("", stderr)

    def test_a_falling_back_home_with_no_data_home_stays_silent(self):
        # An empty/relative XDG_DATA_HOME with an unusable HOME resolves
        # neither side of the comparison.
        for data_home in ("", "relative/data"):
            with self.subTest(data_home=data_home), mock.patch.dict(
                os.environ, {"HOME": "relative/home", "XDG_DATA_HOME": data_home}
            ):
                status, stderr = self.select()
            self.assertEqual(0, status, stderr)
            self.assertEqual("", stderr)

    def test_a_missing_kvantummanager_prints_no_data_home_note(self):
        # The missing-engine remedy already names everything the operator has
        # to do; the data-home warning must not add a second note about a
        # selection that never ran.
        self.unstub("kvantummanager")
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertEqual(1, len(stderr.splitlines()), stderr)
        self.assertIn("kvantummanager is not on PATH", stderr)
        self.assertNotIn("default data home", stderr)

    def test_a_failing_selection_still_prints_the_data_home_note(self):
        self.stub("kvantummanager", "echo set failed >&2\nexit 5")
        status, stderr = self.select()
        self.assertEqual(0, status, stderr)
        self.assertIn(self.note(self.home, self.data), stderr.splitlines())
        self.assertIn("kvantummanager --set exited 5", stderr)
        self.assertIn("fall back", stderr)


if __name__ == "__main__":
    unittest.main()

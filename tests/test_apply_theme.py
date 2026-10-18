"""Tests for tools/apply_theme.py and the `make apply` target.

`apply_theme.main` runs the four re-selection commands against fake
executables on `PATH`, which record their argv and the
`DBUS_SESSION_BUS_ADDRESS` they saw, so the order, the ``--resetLayout``
omission, the session-bus default and the failure paths are pinned without a
running Plasma session. The Makefile tests drive the `apply` target through
`theme_install`, whose child processes run under the suite's timeout.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import repo_root  # noqa: F401  (puts the repository root on sys.path)
import theme_install
from cli_fixtures import call_main
from process_assertions import assert_failed, assert_succeeded
from tools import apply_theme


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of the external tools.

    `PATH` is narrowed to the stub directory, so a `qdbus6` installed on the
    host cannot be picked up and the fallback can be exercised. Each stub is a
    POSIX shell script that appends its own argv and the session bus address it
    inherited to two files in the test's temp dir.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="apply-theme-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.calls = self.root / "calls"
        self.env_log = self.root / "env"
        for name in apply_theme.REQUIRED_TOOLS:
            self.stub(name)
        self.stub("qdbus6")
        patch = mock.patch.dict(os.environ, {"PATH": str(self.bin)})
        patch.start()
        self.addCleanup(patch.stop)

    def stub(self, name, body="exit 0"):
        """Write an executable *name* that records its argv, then runs *body*."""
        path = self.bin / name
        path.write_text(
            "#!/bin/sh\n"
            'name=${0##*/}\n'
            f'printf \'%s %s\\n\' "$name" "$*" >> "{self.calls}"\n'
            f'printf \'%s DBUS=%s\\n\' "$name" "${{DBUS_SESSION_BUS_ADDRESS-}}"'
            f' >> "{self.env_log}"\n'
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def unstub(self, name):
        (self.bin / name).unlink()

    def recorded(self):
        if not self.calls.exists():
            return []
        return self.calls.read_text(encoding="utf-8").splitlines()

    def env_recorded(self):
        if not self.env_log.exists():
            return []
        return self.env_log.read_text(encoding="utf-8").splitlines()


class TestCommandOrder(StubTools):
    def test_runs_the_four_steps_in_order(self):
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            [
                "lookandfeeltool -a org.macos8.desktop",
                "plasma-apply-colorscheme MacOS8",
                "plasma-apply-desktoptheme org.macos8.desktop",
                "qdbus6 org.kde.KWin /KWin reconfigure",
            ],
            self.recorded(),
        )

    def test_never_passes_reset_layout(self):
        call_main(apply_theme.main)
        self.assertNotIn("--resetLayout", " ".join(self.recorded()))

    def test_falls_back_to_qdbus_when_qdbus6_is_missing(self):
        self.unstub("qdbus6")
        self.stub("qdbus")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            ["qdbus org.kde.KWin /KWin reconfigure"], self.recorded()[-1:]
        )


class TestFailurePaths(StubTools):
    def test_failing_required_command_exits_1_with_the_output_tail(self):
        self.stub(
            "plasma-apply-colorscheme",
            "echo colorscheme exploded >&2\nexit 4",
        )
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(1, status)
        self.assertIn("plasma-apply-colorscheme exited 4", stderr)
        self.assertIn("colorscheme exploded", stderr)

    def test_missing_qdbus_prints_a_note_and_exits_0(self):
        self.unstub("qdbus6")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)
        self.assertIn("qdbus", stderr)

    def test_failing_qdbus_prints_a_note_and_exits_0(self):
        self.stub("qdbus6", "echo reconfigure failed >&2\nexit 3")
        status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("note", stderr)


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_required_tool_and_exits_2(self):
        for missing in apply_theme.REQUIRED_TOOLS:
            with self.subTest(missing=missing):
                with tempfile.TemporaryDirectory() as directory:
                    for name in apply_theme.REQUIRED_TOOLS:
                        if name != missing:
                            tool = Path(directory) / name
                            tool.write_text("#!/bin/sh\n", encoding="utf-8")
                            tool.chmod(0o755)
                    with mock.patch.dict(os.environ, {"PATH": directory}):
                        status, stderr = call_main(apply_theme.main)
                self.assertEqual(2, status)
                self.assertTrue(stderr.rstrip().endswith(missing), stderr)


class TestSessionBus(StubTools):
    def test_defaults_the_address_from_an_absolute_runtime_dir(self):
        runtime = self.root / "rt"
        runtime.mkdir()
        (runtime / "bus").write_text("", encoding="utf-8")
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": str(runtime)}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn(
            f"qdbus6 DBUS=unix:path={runtime}/bus", self.env_recorded()
        )

    def test_keeps_an_existing_address(self):
        with mock.patch.dict(
            os.environ,
            {"DBUS_SESSION_BUS_ADDRESS": "unix:path=/existing"},
            clear=False,
        ):
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=unix:path=/existing", self.env_recorded())

    def test_does_not_default_from_a_relative_runtime_dir(self):
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": "relative"}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=", self.env_recorded())
        self.assertNotIn("unix:path=relative", self.env_recorded())

    def test_does_not_default_when_the_bus_socket_is_absent(self):
        runtime = self.root / "empty-runtime"
        runtime.mkdir()
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": str(runtime)}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_theme.main)
        self.assertEqual(0, status, stderr)
        self.assertIn("qdbus6 DBUS=", self.env_recorded())


class TestMakeApply(unittest.TestCase):
    def test_non_empty_destdir_is_refused(self):
        destdir = tempfile.mkdtemp(prefix="apply-destdir-")
        self.addCleanup(shutil.rmtree, destdir, ignore_errors=True)
        result = theme_install.run_make(
            ["apply", f"DESTDIR={destdir}"], env=theme_install.make_env()
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertNotIn("apply_theme.py", result.stdout + result.stderr)

    def test_dry_run_shows_install_before_the_script(self):
        result = theme_install.run_make(
            ["-n", "apply"], env=theme_install.make_env("XDG_DATA_HOME")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_theme.py", result.stdout)
        self.assertLess(
            result.stdout.index("--no-print-directory install"),
            result.stdout.index("tools/apply_theme.py"),
        )

    def test_help_lists_apply(self):
        result = theme_install.run_make(["help"], env=theme_install.make_env())
        assert_succeeded(self, result)
        self.assertTrue(
            any(
                line.startswith("  apply ")
                for line in result.stdout.splitlines()
            ),
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()

"""Tests for tools/apply_keymap.py and its `make apply` wiring.

The tool runs against stubs of the KConfig and session-bus commands on
`PATH`, so the read/merge/write/reload order, the preservation of the user's
other XKB options, the idempotent rewrite, and the best-effort reload policy
are pinned without touching the caller's `kxkbrc` or session.
"""

from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import theme_install
from support import process_runner
from support.cli_fixtures import assert_missing_tool_named, call_main
from support.process_assertions import assert_failed, assert_succeeded
from support.recorded_lines import recorded_lines
from tools import apply_keymap, diagnostics

MAKE = shutil.which("make")


class StubTools(unittest.TestCase):
    """Base for tests that run `main` against shell stubs of its tools.

    `PATH` is narrowed to the stub directory, so a host `kreadconfig6` or
    `dbus-send` cannot satisfy a test that removed it. Each stub appends its
    own argv to one file, so the order is the call order.
    """

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="apply-keymap-test-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.config = self.root / "config"
        self.config.mkdir()
        self.calls = self.root / "calls"
        self.env_log = self.root / "env"
        self.stub("kreadconfig6")
        self.stub("kwriteconfig6")
        self.stub("dbus-send")
        self.stub("busctl")
        patch = mock.patch.dict(
            os.environ,
            {
                "PATH": str(self.bin),
                "HOME": str(self.home),
                "XDG_CONFIG_HOME": str(self.config),
                "XDG_RUNTIME_DIR": "",
            },
            clear=False,
        )
        patch.start()
        self.addCleanup(patch.stop)

    def stub(self, name, body="exit 0"):
        """Write an executable *name* that records its argv, then runs *body*."""
        path = self.bin / name
        path.write_text(
            "#!/bin/sh\n"
            "name=${0##*/}\n"
            f'printf \'%s %s\\n\' "$name" "$*" >> "{self.calls}"\n'
            f'printf \'%s DBUS=%s\\n\' "$name" "${{DBUS_SESSION_BUS_ADDRESS-}}"'
            f' >> "{self.env_log}"\n'
            f"{body}\n",
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def broken_stub(self, name):
        """Make *name* executable but unable to start."""
        path = self.bin / name
        path.write_text("#!/nonexistent/interpreter\n", encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def unstub(self, name):
        """Remove the stub script named *name* from the stub bin."""
        (self.bin / name).unlink()

    def recorded(self):
        """Return the lines the stubs appended, in call order."""
        return recorded_lines(self.calls)

    def env_recorded(self):
        """Return the ``"<name> DBUS=<address>"`` lines the stubs appended."""
        return recorded_lines(self.env_log)


class TestMergeOption(unittest.TestCase):
    def test_an_empty_value_becomes_the_swap(self):
        self.assertEqual(apply_keymap.OPTION, apply_keymap.merge_option(""))

    def test_existing_options_are_kept_in_order(self):
        self.assertEqual(
            f"caps:escape,{apply_keymap.OPTION}",
            apply_keymap.merge_option("caps:escape"),
        )

    def test_removal_drops_only_exact_swap_tokens(self):
        self.assertEqual(
            "caps:escape,compose:ralt,ctrl:swap_lalt_lctl_extra",
            apply_keymap.remove_option(
                "caps:escape, ctrl:swap_lalt_lctl, compose:ralt,,"
                "ctrl:swap_lalt_lctl,ctrl:swap_lalt_lctl_extra"
            ),
        )

    def test_remove_discards_exact_swap_tokens_and_preserves_order(self):
        self.assertEqual(
            "caps:escape,compose:ralt,ctrl:swap_lalt_lctl_extra,caps:escape",
            apply_keymap.remove_option(
                " caps:escape, ,ctrl:swap_lalt_lctl,compose:ralt,"
                "ctrl:swap_lalt_lctl_extra,ctrl:swap_lalt_lctl,caps:escape "
            ),
        )

    def test_an_existing_swap_is_not_duplicated(self):
        existing = f"caps:escape,{apply_keymap.OPTION}"
        self.assertEqual(existing, apply_keymap.merge_option(existing))

    def test_blank_entries_and_surrounding_space_are_dropped(self):
        self.assertEqual(
            f"caps:escape,{apply_keymap.OPTION}",
            apply_keymap.merge_option(" , caps:escape ,, "),
        )


class TestCommandOrder(StubTools):
    def test_adds_the_swap_to_the_users_other_options_and_reloads(self):
        self.stub("kreadconfig6", "printf 'caps:escape\\n'")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertEqual(
            [
                "kreadconfig6 --file kxkbrc --group Layout --key Options",
                "kwriteconfig6 --file kxkbrc --group Layout --key Options "
                f"caps:escape,{apply_keymap.OPTION}",
                "kwriteconfig6 --file kxkbrc --group Layout --key "
                "ResetOldOptions --type bool true",
                "dbus-send --session --type=signal /Layouts "
                "org.kde.keyboard.reloadConfig",
            ],
            self.recorded(),
        )

    def test_a_stderr_warning_is_not_written_as_an_option(self):
        self.stub(
            "kreadconfig6",
            "printf 'warning: bad escape\\n' >&2; printf 'caps:escape\\n'",
        )

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        options_writes = [
            line
            for line in self.recorded()
            if line.startswith(
                "kwriteconfig6 --file kxkbrc --group Layout --key Options "
            )
        ]
        self.assertEqual(
            [f"kwriteconfig6 --file kxkbrc --group Layout --key Options "
             f"caps:escape,{apply_keymap.OPTION}"],
            options_writes,
        )

    def test_an_empty_configuration_writes_just_the_swap(self):
        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertIn(
            "kwriteconfig6 --file kxkbrc --group Layout --key Options "
            f"{apply_keymap.OPTION}",
            self.recorded(),
        )

    def test_a_repeat_run_keeps_one_copy(self):
        self.stub(
            "kreadconfig6",
            f"printf 'caps:escape,{apply_keymap.OPTION}\\n'",
        )

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        options_writes = [
            line
            for line in self.recorded()
            if line.startswith(
                "kwriteconfig6 --file kxkbrc --group Layout --key Options "
            )
        ]
        self.assertEqual(1, len(options_writes))
        self.assertEqual(1, options_writes[0].count(apply_keymap.OPTION))
        self.assertTrue(options_writes[0].endswith("caps:escape," + apply_keymap.OPTION))

    def test_remove_keeps_other_options_and_requests_reload(self):
        self.stub("kreadconfig6", "printf 'caps:escape,,ctrl:swap_lalt_lctl,compose:ralt,ctrl:swap_lalt_lctl\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            "kwriteconfig6 --file kxkbrc --group Layout --key Options caps:escape,compose:ralt",
            self.recorded()[1],
        )
        self.assertTrue(self.recorded()[2].endswith("ResetOldOptions --type bool true"))
        self.assertTrue(self.recorded()[-1].startswith("dbus-send"))

    def test_remove_sole_swap_writes_empty_value(self):
        self.stub("kreadconfig6", f"printf '{apply_keymap.OPTION}\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertEqual(
            "kwriteconfig6 --file kxkbrc --group Layout --key Options ",
            self.recorded()[1],
        )

    def test_remove_missing_swap_is_a_noop(self):
        self.stub("kreadconfig6", "printf 'caps:escape,,compose:ralt\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertEqual(1, len(self.recorded()))

    def test_remove_keymap_make_target_runs_only_removal(self):
        result = process_runner.run(
            [MAKE, "-n", "remove-keymap"],
            cwd=theme_install.repo_root.ROOT,
            env=theme_install.make_env(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("tools/apply_keymap.py --remove", result.stdout)
        self.assertNotIn("install", result.stdout)


class TestRemove(StubTools):
    def test_removes_swap_preserving_other_options_and_reloads(self):
        self.stub("kreadconfig6", f"printf 'caps:escape,{apply_keymap.OPTION},compose:ralt,{apply_keymap.OPTION}\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertEqual([
            "kreadconfig6 --file kxkbrc --group Layout --key Options",
            "kwriteconfig6 --file kxkbrc --group Layout --key Options caps:escape,compose:ralt",
            "kwriteconfig6 --file kxkbrc --group Layout --key ResetOldOptions --type bool true",
            "dbus-send --session --type=signal /Layouts org.kde.keyboard.reloadConfig",
        ], self.recorded())

    def test_removing_only_swap_writes_empty_options(self):
        self.stub("kreadconfig6", f"printf '{apply_keymap.OPTION}\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertTrue(self.recorded()[1].endswith("--key Options "))
        self.assertIn("ResetOldOptions --type bool true", self.recorded()[2])

    def test_absent_swap_is_noop(self):
        self.stub("kreadconfig6", "printf 'caps:escape\\n'")
        status, stderr = call_main(apply_keymap.main, "--remove")
        self.assertEqual(0, status, stderr)
        self.assertEqual(1, len(self.recorded()))

    def test_make_target_is_guarded_and_invokes_removal_flag(self):
        env = theme_install.make_env()
        env["PATH"] = os.defpath
        result = theme_install.run_make(["-n", "remove-keymap"], env=env)
        assert_succeeded(self, result)
        self.assertIn("tools/apply_keymap.py --remove", result.stdout)
        self.assertNotIn(" install", result.stdout)

    def test_make_refuses_destdir(self):
        env = theme_install.make_env()
        env["PATH"] = os.defpath
        result = theme_install.run_make(
            ["remove-keymap", "DESTDIR=/tmp/keymap-stage"],
            env=env,
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertNotIn("apply_keymap.py", result.stdout + result.stderr)


class TestMakeApplyKeymap(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="make-apply-keymap-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.calls = self.root / "calls"
        self.python = self.root / "python"
        self.python.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = -c ]; then exit 0; fi\n"
            f"printf '%s\\n' \"$*\" >> '{self.calls}'\n"
            "exit \"${FAKE_PYTHON_STATUS:-0}\"\n",
            encoding="utf-8",
        )
        self.python.chmod(0o755)

    def test_dry_run_is_standalone(self):
        result = theme_install.run_make(
            ["-n", "apply-keymap"], env=theme_install.make_env("PYTHON")
        )
        assert_succeeded(self, result)
        self.assertIn("tools/apply_keymap.py", result.stdout)
        self.assertNotIn("--remove", result.stdout)
        self.assertNotIn("install", result.stdout)

    def test_invokes_helper_once_without_mode_flag(self):
        env = theme_install.make_env("PYTHON")
        env["PYTHON"] = str(self.python)
        result = theme_install.run_make(["apply-keymap"], env=env)
        assert_succeeded(self, result)
        self.assertEqual(["tools/apply_keymap.py"], self.calls.read_text().splitlines())

    def test_refuses_destdir_before_helper(self):
        env = theme_install.make_env("PYTHON")
        env["PYTHON"] = str(self.python)
        result = theme_install.run_make(
            ["apply-keymap", "DESTDIR=/tmp/keymap-stage"], env=env
        )
        assert_failed(self, result)
        self.assertIn("DESTDIR", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_helper_failure_fails_target(self):
        env = theme_install.make_env("PYTHON")
        env["PYTHON"] = str(self.python)
        env["FAKE_PYTHON_STATUS"] = "7"
        result = theme_install.run_make(["apply-keymap"], env=env)
        assert_failed(self, result)
        self.assertEqual(["tools/apply_keymap.py"], self.calls.read_text().splitlines())

    def test_missing_interpreter_fails_before_helper(self):
        env = theme_install.make_env("PYTHON")
        env["PATH"] = os.defpath
        result = theme_install.run_make(
            ["apply-keymap", "PYTHON=missing-python-for-apply-keymap"], env=env
        )
        assert_failed(self, result)
        self.assertIn("PYTHON", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_old_interpreter_fails_before_helper(self):
        self.python.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = -c ]; then exit 3; fi\n"
            f"printf '%s\\n' \"$*\" >> '{self.calls}'\n",
            encoding="utf-8",
        )
        self.python.chmod(0o755)
        env = theme_install.make_env("PYTHON")
        env["PYTHON"] = str(self.python)
        result = theme_install.run_make(["apply-keymap"], env=env)
        assert_failed(self, result)
        self.assertIn("Python 3.10 or newer", result.stderr)
        self.assertFalse(self.calls.exists())


class TestReload(StubTools):
    def test_defaults_the_bus_address_from_the_runtime_directory(self):
        runtime = self.root / "rt"
        runtime.mkdir()
        (runtime / "bus").write_text("", encoding="utf-8")
        with mock.patch.dict(
            os.environ, {"XDG_RUNTIME_DIR": str(runtime)}, clear=False
        ):
            os.environ.pop("DBUS_SESSION_BUS_ADDRESS", None)
            status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertIn(
            f"dbus-send DBUS=unix:path={runtime}/bus", self.env_recorded()
        )

    def test_busctl_is_the_fallback_when_dbus_send_is_absent(self):
        self.unstub("dbus-send")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertEqual(
            "busctl --user emit /Layouts org.kde.keyboard reloadConfig",
            self.recorded()[-1],
        )

    def test_busctl_is_tried_when_dbus_send_fails(self):
        self.stub("dbus-send", "exit 3")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertTrue(
            any(line.startswith("busctl --user emit") for line in self.recorded())
        )
        self.assertNotIn("note", stderr)

    def test_no_emitter_is_a_note_and_still_succeeds(self):
        self.unstub("dbus-send")
        self.unstub("busctl")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertIn("next login", stderr)

    def test_a_failing_reload_is_a_note_and_still_succeeds(self):
        self.stub("dbus-send", "echo cannot reach the bus >&2\nexit 4")
        self.unstub("busctl")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(0, status, stderr)
        self.assertIn("dbus-send exited 4", stderr)
        self.assertIn("next login", stderr)


class TestFailurePaths(StubTools):
    def test_a_failing_read_exits_1_and_writes_nothing(self):
        self.stub("kreadconfig6", "echo unreadable >&2\nexit 3")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(1, status)
        self.assertIn("kreadconfig6 exited 3", stderr)
        self.assertFalse(
            any(line.startswith("kwriteconfig6") for line in self.recorded())
        )

    def test_a_failing_options_write_exits_1_and_skips_the_reload(self):
        self.stub("kwriteconfig6", "echo cannot write kxkbrc >&2\nexit 6")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(1, status)
        self.assertIn("kwriteconfig6 exited 6", stderr)
        self.assertFalse(
            any(line.startswith("dbus-send") for line in self.recorded())
        )

    def test_an_unrunnable_read_tool_exits_2_without_a_traceback(self):
        self.broken_stub("kreadconfig6")

        status, stderr = call_main(apply_keymap.main)

        self.assertEqual(2, status)
        self.assertIn("cannot run kreadconfig6", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_an_unusable_scratch_directory_exits_2_without_a_traceback(self):
        with mock.patch.object(
            diagnostics.tempfile, "mkdtemp", side_effect=OSError("no space left")
        ):
            status, stderr = call_main(apply_keymap.main)

        self.assertEqual(2, status)
        self.assertIn("cannot create a scratch directory", stderr)
        self.assertIn("no space left", stderr)
        self.assertNotIn("Traceback", stderr)


class TestMissingTool(unittest.TestCase):
    def test_names_the_first_missing_required_tool_and_exits_2(self):
        assert_missing_tool_named(self, apply_keymap.main, apply_keymap.REQUIRED_TOOLS)


if __name__ == "__main__":
    unittest.main()

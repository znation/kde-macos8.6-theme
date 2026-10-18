"""Tests for tools/local_hook.py and the local-hook Makefile targets.

Each test makes a throwaway ``git init`` repository and runs the tool with that
repository as its working directory, so the hook path and the repository root
come from real git plumbing. The CLI runs in-process (``run_tool``) so the
suite does not pay interpreter startup per call; ``test_script_entry_point``
spawns the script once so its direct-run wrapper stays covered. The hook body
is run directly against a fake ``make`` on ``PATH`` to pin that it re-applies
from the worktree root and swallows a failed apply. The Makefile tests drive
the new targets through `theme_install`.
"""

from __future__ import annotations

import contextlib
import os
import stat
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import theme_install
from support import tmp_dir
from support.cli_fixtures import run_main
from support.process_assertions import assert_failed, assert_succeeded
from tools import local_hook


def make_repo(case):
    """Create a fresh ``git init`` repository and return its root path."""
    repo = tmp_dir.make_tmp_dir(case)
    result = theme_install.run_captured(
        ["git", "init", "-q"], cwd=repo, env=dict(os.environ)
    )
    assert_succeeded(case, result)
    return repo


@contextlib.contextmanager
def _in_directory(path):
    """Run the block with *path* as the process working directory, then restore."""
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def run_tool(repo, *args):
    """Run the ``local_hook`` CLI with *repo* as its working directory.

    ``local_hook`` resolves its git hooks directory and work-tree root from
    the process working directory, so the call runs inside *repo*. Calling
    ``main`` in-process exercises the same argument parsing, output and exit
    status as ``python3 tools/local_hook.py`` without paying interpreter
    startup and module import per call; ``test_script_entry_point`` covers the
    script wrapper once.
    """
    with _in_directory(repo):
        return run_main(local_hook.main, "local_hook", args)


def hook_path(repo):
    """The default post-commit hook path of a repository made by `make_repo`."""
    return Path(repo) / ".git" / "hooks" / local_hook.HOOK_NAME


def write_fake_make(bindir, record, exit_status=0):
    """Write an executable ``make`` that records its cwd and argv, then exits."""
    bindir.mkdir(parents=True, exist_ok=True)
    make = bindir / "make"
    make.write_text(
        "#!/bin/sh\n"
        f'printf \'%s\\n\' "$PWD" > "{record}"\n'
        f'printf \'%s\\n\' "$*" >> "{record}"\n'
        f"exit {exit_status}\n",
        encoding="utf-8",
    )
    make.chmod(0o755)


class TestGitFailures(unittest.TestCase):
    """``_git`` turns a missing git, a timeout and a failed run into a report.

    Every git invocation goes through ``_git``; a failure must surface as a
    ``LocalHookError`` the caller prints with exit status 2 instead of a
    traceback. The command is patched, so the failure is produced without a
    real hung or absent git.
    """

    def _failure(self, **run):
        """Call ``_git`` with ``subprocess.run`` patched by *run*; return its message."""
        with mock.patch.object(local_hook.subprocess, "run", **run):
            with self.assertRaises(local_hook.LocalHookError) as caught:
                local_hook._git("rev-parse", "--git-path", "hooks")
        return str(caught.exception)

    def test_missing_git_is_reported(self):
        message = self._failure(side_effect=FileNotFoundError())
        self.assertEqual(message, "git not found on PATH")

    def test_timeout_names_the_command_and_duration(self):
        message = self._failure(
            side_effect=subprocess.TimeoutExpired(
                "git", local_hook.COMMAND_TIMEOUT
            )
        )
        self.assertEqual(
            message,
            "git rev-parse --git-path hooks timed out after "
            f"{local_hook.COMMAND_TIMEOUT:g}s",
        )

    def test_nonzero_exit_reports_gits_own_diagnostic(self):
        message = self._failure(
            return_value=mock.Mock(
                returncode=1, stderr="fatal: boom\n", stdout=""
            )
        )
        self.assertEqual(message, "fatal: boom")

    def test_nonzero_exit_falls_back_to_stdout(self):
        message = self._failure(
            return_value=mock.Mock(
                returncode=1, stderr="  \n", stdout="from stdout\n"
            )
        )
        self.assertEqual(message, "from stdout")

    def test_nonzero_exit_without_output_names_command_and_status(self):
        message = self._failure(
            return_value=mock.Mock(returncode=3, stderr="", stdout="")
        )
        self.assertEqual(message, "git rev-parse --git-path hooks exited 3")

    def test_success_returns_the_stripped_stdout(self):
        with mock.patch.object(
            local_hook.subprocess,
            "run",
            return_value=mock.Mock(
                returncode=0, stderr="", stdout=" /hooks \n"
            ),
        ):
            self.assertEqual(
                local_hook._git("rev-parse", "--git-path", "hooks"),
                "/hooks",
            )


class TestInstall(unittest.TestCase):
    def test_writes_an_executable_marked_hook(self):
        repo = make_repo(self)
        result = run_tool(repo, "install")
        assert_succeeded(self, result)
        hook = hook_path(repo)
        self.assertTrue(hook.is_file(), result.stdout + result.stderr)
        self.assertTrue(hook.stat().st_mode & stat.S_IXUSR, "hook is not executable")
        text = hook.read_text(encoding="utf-8")
        self.assertIn(local_hook.MARKER, text)
        self.assertIn("make apply", text)

    def test_reinstall_leaves_the_same_bytes(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        first = hook_path(repo).read_bytes()
        result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertEqual(first, hook_path(repo).read_bytes())

    def test_refuses_a_foreign_hook_and_leaves_it_alone(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
        hook.write_bytes(foreign)
        result = run_tool(repo, "install")
        assert_failed(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertEqual(foreign, hook.read_bytes())

    def test_refuses_a_dangling_symlinked_hook_without_writing_through(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        target = Path(repo) / "outside"
        hook.symlink_to(target)
        result = run_tool(repo, "install")
        assert_failed(self, result)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(str(hook), result.stderr)
        self.assertTrue(hook.is_symlink())
        self.assertFalse(target.exists(), "install wrote through the symlink")

    def test_refuses_an_unreadable_hook(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
        hook.write_bytes(foreign)
        hook.chmod(0o000)
        self.addCleanup(hook.chmod, 0o644)
        result = run_tool(repo, "install")
        assert_failed(self, result)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(str(hook), result.stderr)
        hook.chmod(0o644)
        self.assertEqual(foreign, hook.read_bytes())

    def test_refuses_a_directory_at_the_hook_path(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.mkdir()
        result = run_tool(repo, "install")
        assert_failed(self, result)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn(str(hook), result.stderr)
        self.assertIn("non-regular", result.stderr)
        self.assertTrue(hook.is_dir(), "install replaced the directory")

    def test_a_crash_mid_write_leaves_the_old_hook_intact(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        hook = hook_path(repo)
        complete = hook.read_bytes()

        def crashing_write_text(self, data, **kwargs):
            # Simulate a process death after a partial write: the file is left
            # truncated, then the write raises.
            self.write_bytes(data.encode()[: len(data) // 2])
            raise OSError("simulated crash mid-write")

        with mock.patch.object(local_hook, "hooks_dir", lambda: hook.parent), \
                mock.patch.object(local_hook, "top_level", lambda: Path(repo)), \
                mock.patch.object(Path, "write_text", crashing_write_text):
            status = local_hook.install()

        self.assertEqual(status, 2)
        self.assertEqual(hook.read_bytes(), complete, "old hook was truncated")
        leftovers = [
            entry.name
            for entry in hook.parent.iterdir()
            if entry.name.startswith(f".{local_hook.HOOK_NAME}-")
            and entry.name.endswith(".tmp")
        ]
        self.assertEqual([], leftovers, leftovers)

    def test_script_entry_point(self):
        # ``run_tool`` calls ``main`` in-process for speed; this spawns the
        # script once so its `if __name__ == "__main__": sys.exit(main())`
        # wrapper and direct-run imports stay covered.
        repo = make_repo(self)
        script = Path(theme_install.ROOT) / "tools" / "local_hook.py"
        result = theme_install.run_captured(
            [sys.executable, str(script), "install"],
            cwd=repo,
            env=dict(os.environ),
        )
        assert_succeeded(self, result)
        self.assertTrue(hook_path(repo).is_file(), result.stdout + result.stderr)


class TestUninstall(unittest.TestCase):
    def test_removes_a_hook_it_installed(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)
        self.assertFalse(hook_path(repo).exists())

    def test_refuses_a_foreign_hook_and_leaves_it_alone(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
        hook.write_bytes(foreign)
        result = run_tool(repo, "uninstall")
        assert_failed(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertEqual(foreign, hook.read_bytes())

    def test_refuses_a_symlinked_hook(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hook.parent.mkdir(parents=True, exist_ok=True)
        target = Path(repo) / "outside"
        target.write_text("keep me", encoding="utf-8")
        hook.symlink_to(target)
        result = run_tool(repo, "uninstall")
        assert_failed(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertTrue(hook.is_symlink())
        self.assertEqual("keep me", target.read_text(encoding="utf-8"))

    def test_a_missing_hook_is_not_an_error(self):
        repo = make_repo(self)
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)


class TestHookBody(unittest.TestCase):
    def _run_hook(self, repo, exit_status):
        bindir = Path(repo) / "fakebin"
        record = Path(repo) / "make-calls"
        write_fake_make(bindir, record, exit_status)
        env = dict(os.environ)
        env["PATH"] = str(bindir) + os.pathsep + env.get("PATH", "")
        result = theme_install.run_captured(
            [str(hook_path(repo))], cwd=repo, env=env
        )
        lines = (
            record.read_text(encoding="utf-8").splitlines()
            if record.exists()
            else []
        )
        return result, lines

    def test_runs_make_apply_from_the_worktree_root(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result, lines = self._run_hook(repo, exit_status=0)
        assert_succeeded(self, result)
        self.assertEqual([str(Path(repo).resolve()), "apply"], lines)

    def test_a_failed_apply_does_not_fail_the_hook(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result, lines = self._run_hook(repo, exit_status=3)
        assert_succeeded(self, result)
        self.assertEqual("apply", lines[-1])


class TestMakeTargets(unittest.TestCase):
    def test_dry_run_shows_the_python_invocations(self):
        for subcommand in ("install", "uninstall"):
            with self.subTest(subcommand=subcommand):
                result = theme_install.run_make(
                    ["-n", f"{subcommand}-local-hook"],
                    env=theme_install.make_env(),
                )
                assert_succeeded(self, result)
                self.assertIn(
                    f"tools/local_hook.py {subcommand}", result.stdout
                )

    def test_help_lists_both_targets(self):
        result = theme_install.run_make(
            ["help"], env=theme_install.make_env()
        )
        assert_succeeded(self, result)
        lines = result.stdout.splitlines()
        for target in ("install-local-hook", "uninstall-local-hook"):
            with self.subTest(target=target):
                self.assertTrue(
                    any(line.startswith(f"  {target} ") for line in lines),
                    result.stdout,
                )


if __name__ == "__main__":
    unittest.main()

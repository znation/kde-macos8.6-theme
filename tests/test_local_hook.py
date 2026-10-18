"""Tests for tools/local_hook.py and the local-hook Makefile targets.

Each test makes a throwaway ``git init`` repository and runs the tool as a
child process with that repository as its working directory, so the hook path
and the repository root come from real git plumbing. The hook body is run
directly against a fake ``make`` on ``PATH`` to pin that it re-applies from
the worktree root and swallows a failed apply. The Makefile tests drive the
new targets through `theme_install`.
"""

from __future__ import annotations

import os
import stat
import sys
import unittest
from pathlib import Path
from unittest import mock

import repo_root  # noqa: F401  (puts the repository root on sys.path)
import theme_install
import tmp_dir
from process_assertions import assert_failed, assert_succeeded
from tools import local_hook


def make_repo(case):
    """Create a fresh ``git init`` repository and return its root path."""
    repo = tmp_dir.make_tmp_dir(case)
    result = theme_install.run_captured(
        ["git", "init", "-q"], cwd=repo, env=dict(os.environ)
    )
    assert_succeeded(case, result)
    return repo


def run_tool(repo, *args):
    """Run ``tools/local_hook.py *args*`` with *repo* as the working directory."""
    script = Path(theme_install.ROOT) / "tools" / "local_hook.py"
    return theme_install.run_captured(
        [sys.executable, str(script), *args],
        cwd=repo,
        env=dict(os.environ),
    )


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

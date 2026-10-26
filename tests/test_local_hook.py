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
import shutil
import stat
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import theme_install
from support import tmp_dir
from support.atomic_write_failures import crashing_fdopen, swapping_mkstemp
from support.cli_fixtures import run_main
from support.close_tracking import failing_fdopen
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from support.unlink_failure import unlink_failing_for
from tools import atomic_write, local_hook, local_hook_git


def make_repo(case):
    """Create a fresh ``git init`` repository and return its root path."""
    repo = tmp_dir.make_tmp_dir(case)
    result = theme_install.run_captured(
        ["git", "init", "-q"], cwd=repo, env=dict(os.environ)
    )
    assert_succeeded(case, result)
    return repo


def make_non_utf8_repo(case):
    """Create a ``git init`` repository whose path holds a non-UTF-8 byte.

    Linux permits such a path and git prints it raw, so git's output is not
    decodable as strict UTF-8; this is the input that must not crash the tool.
    The returned path is a string with a surrogate escape for the byte.
    """
    base = os.fsencode(tmp_dir.make_tmp_dir(case))
    repo = os.fsdecode(base + b"/repo-\xff")
    os.mkdir(repo)
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


def make_repo_with_hook(case):
    """Create a repository and return its root with its default hook path.

    The hook's parent directory is created so a test can put its own file,
    symlink or directory at the hook path without repeating the setup.
    """
    repo = make_repo(case)
    hook = hook_path(repo)
    hook.parent.mkdir(parents=True, exist_ok=True)
    return repo, hook


def assert_refuses_a_foreign_hook(case, command):
    """Assert *command* refuses a hook this tool did not write and leaves it alone.

    ``install`` and ``uninstall`` share the refusal: each must exit with a
    failure, name the hook path on stderr, and leave the foreign bytes in
    place. Each of ``TestInstall`` and ``TestUninstall`` calls this once, so
    the sequence is stated here.
    """
    repo, hook = make_repo_with_hook(case)
    foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
    hook.write_bytes(foreign)
    result = run_tool(repo, command)
    assert_failed(case, result)
    case.assertIn(str(hook), result.stderr)
    case.assertEqual(foreign, hook.read_bytes())


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
        with mock.patch.object(local_hook_git.subprocess, "run", **run):
            with self.assertRaises(local_hook_git.LocalHookError) as caught:
                local_hook_git._git("rev-parse", "--git-path", "hooks")
        return str(caught.exception)

    def test_missing_git_is_reported(self):
        message = self._failure(side_effect=FileNotFoundError())
        self.assertEqual(message, "git not found on PATH")

    def test_unrunnable_git_is_reported(self):
        # A git that exists but cannot be executed (a permission error, a
        # directory on PATH) raises an OSError other than FileNotFoundError.
        # It must become a LocalHookError the caller prints with exit status
        # 2, not a traceback that names neither the tool nor the command.
        message = self._failure(
            side_effect=PermissionError(13, "Permission denied")
        )
        self.assertIn("cannot run git", message)
        self.assertIn("Permission denied", message)

    def test_timeout_names_the_command_and_duration(self):
        message = self._failure(
            side_effect=subprocess.TimeoutExpired(
                "git", local_hook_git.COMMAND_TIMEOUT
            )
        )
        self.assertEqual(
            message,
            "git rev-parse --git-path hooks timed out after "
            f"{local_hook_git.COMMAND_TIMEOUT:g}s",
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

    def test_non_utf8_output_is_decoded_instead_of_crashing(self):
        # A repository path may hold a byte that is not UTF-8, which git
        # prints raw; a strict decode raises an uncaught UnicodeDecodeError.
        # _git must decode it so the caller can use and report the path.
        bindir = tmp_dir.make_tmp_dir(self) / "bin"
        bindir.mkdir()
        fake = bindir / "git"
        fake.write_bytes(b"#!/bin/sh\nprintf '\\377\\376\\n'\n")
        fake.chmod(0o755)
        with mock.patch.dict(os.environ, {"PATH": str(bindir)}):
            self.assertEqual(
                local_hook_git._git("rev-parse", "--show-toplevel"),
                "\udcff\udcfe",
            )

    def test_success_returns_the_stripped_stdout(self):
        with mock.patch.object(
            local_hook_git.subprocess,
            "run",
            return_value=mock.Mock(
                returncode=0, stderr="", stdout=" /hooks \n"
            ),
        ):
            self.assertEqual(
                local_hook_git._git("rev-parse", "--git-path", "hooks"),
                "/hooks",
            )


class TestGitDiscovery(unittest.TestCase):
    """Pin the Git path discovery ``local_hook_git`` documents.

    One install test replaces ``hooks_dir`` and ``top_level`` with lambdas,
    and every other real-git case is a plain fresh checkout, so no existing
    test reaches a configured ``core.hooksPath``, a linked worktree or a
    relative Git path. Each of those selects where Git actually runs the
    hook; getting it wrong writes a hook Git never runs.
    """

    def _git(self, cwd, *args):
        result = theme_install.run_captured(
            ["git", *args], cwd=cwd, env=dict(os.environ)
        )
        assert_succeeded(self, result)
        return result.stdout.strip()

    def test_default_hooks_dir_is_the_resolved_dot_git_hook_dir(self):
        repo = make_repo(self)
        with _in_directory(repo):
            hooks = local_hook_git.hooks_dir()
        self.assertTrue(hooks.is_absolute())
        self.assertEqual((repo / ".git" / "hooks").resolve(), hooks)

    def test_a_subdirectory_still_names_the_repository_hooks_dir(self):
        repo = make_repo(self)
        sub = repo / "sub"
        sub.mkdir()
        # Git prints a path relative to the current directory here
        # (``../.git/hooks``); resolving it from the wrong base would point
        # outside the repository.
        with _in_directory(sub):
            hooks = local_hook_git.hooks_dir()
        self.assertTrue(hooks.is_absolute())
        self.assertEqual((repo / ".git" / "hooks").resolve(), hooks)

    def test_a_relative_core_hooks_path_is_honoured(self):
        repo = make_repo(self)
        self._git(repo, "config", "core.hooksPath", "team-hooks")
        sub = repo / "sub"
        sub.mkdir()
        with _in_directory(sub):
            hooks = local_hook_git.hooks_dir()
        self.assertTrue(hooks.is_absolute())
        self.assertEqual((repo / "team-hooks").resolve(), hooks)

    def test_an_absolute_core_hooks_path_is_used_as_given(self):
        repo = make_repo(self)
        shared = tmp_dir.make_tmp_dir(self) / "shared-hooks"
        shared.mkdir()
        self._git(repo, "config", "core.hooksPath", str(shared))
        with _in_directory(repo):
            hooks = local_hook_git.hooks_dir()
        self.assertEqual(shared.resolve(), hooks)

    def test_a_linked_worktree_uses_the_common_hooks_directory(self):
        repo = make_repo(self)
        self._git(
            repo,
            "-c",
            "user.email=local-hook@example.invalid",
            "-c",
            "user.name=Local Hook",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "base",
        )
        linked = repo.with_name(repo.name + "-linked")
        self.addCleanup(shutil.rmtree, linked, ignore_errors=True)
        self._git(repo, "worktree", "add", "-q", "--detach", str(linked))
        with _in_directory(linked):
            hooks = local_hook_git.hooks_dir()
            top = local_hook_git.top_level()
        # A linked worktree's own git directory holds no hooks/ directory;
        # Git runs the common checkout's hooks, which is where the tool must
        # write.
        self.assertEqual((repo / ".git" / "hooks").resolve(), hooks)
        self.assertEqual(linked.resolve(), top)

    def test_top_level_is_the_work_tree_root_from_a_subdirectory(self):
        repo = make_repo(self)
        sub = repo / "sub"
        sub.mkdir()
        with _in_directory(sub):
            top = local_hook_git.top_level()
        self.assertTrue(top.is_absolute())
        self.assertEqual(repo.resolve(), top)


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

    def test_non_utf8_repo_path_is_handled_and_escaped(self):
        # A non-UTF-8 repository path must not crash the tool: install
        # succeeds, writes the hook at the right byte path, and prints the
        # path escaped so no surrogate reaches the terminal.
        repo = make_non_utf8_repo(self)
        result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("\\udcff", result.stdout)
        self.assertIn(
            local_hook.MARKER,
            hook_path(repo).read_text(encoding="utf-8"),
        )

    def test_reinstall_leaves_the_same_bytes(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        first = hook_path(repo).read_bytes()
        result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertEqual(first, hook_path(repo).read_bytes())

    def test_refuses_a_foreign_hook_and_leaves_it_alone(self):
        assert_refuses_a_foreign_hook(self, "install")

    def test_refuses_an_oversize_hook_without_reading_it_whole(self):
        # A hook far larger than the read cap cannot be one this tool wrote.
        # The tool must refuse it by name instead of loading the whole file
        # into memory; a multi-gigabyte hook would otherwise raise MemoryError
        # (which is not an OSError) and escape as a traceback.
        repo, hook = make_repo_with_hook(self)
        oversize = b"#!/bin/sh\n" + b"x" * local_hook._MAX_HOOK_BYTES
        hook.write_bytes(oversize)
        result = run_tool(repo, "install")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(oversize, hook.read_bytes())

    def test_refuses_a_dangling_symlinked_hook_without_writing_through(self):
        repo, hook = make_repo_with_hook(self)
        target = Path(repo) / "outside"
        hook.symlink_to(target)
        result = run_tool(repo, "install")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertTrue(hook.is_symlink())
        self.assertFalse(target.exists(), "install wrote through the symlink")

    def test_refuses_an_unreadable_hook(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses file permissions")
        repo, hook = make_repo_with_hook(self)
        foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
        hook.write_bytes(foreign)
        hook.chmod(0o000)
        self.addCleanup(hook.chmod, 0o644)
        result = run_tool(repo, "install")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(hook), result.stderr)
        hook.chmod(0o644)
        self.assertEqual(foreign, hook.read_bytes())

    def test_refuses_a_directory_at_the_hook_path(self):
        repo, hook = make_repo_with_hook(self)
        hook.mkdir()
        result = run_tool(repo, "install")
        assert_exit_2_without_traceback(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertIn("non-regular", result.stderr)
        self.assertTrue(hook.is_dir(), "install replaced the directory")

    def test_reports_a_hook_path_it_cannot_inspect(self):
        # A path component in front of the hook that is not a directory
        # makes ``lstat`` raise ``NotADirectoryError``. The tool must turn
        # that into a diagnostic and exit 2, not a traceback.
        repo = make_repo(self)
        hooks = Path(repo) / ".git" / "hooks"
        shutil.rmtree(hooks)
        hooks.write_bytes(b"not a directory\n")
        result = run_tool(repo, "install")
        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot inspect", result.stderr)
        self.assertEqual(hooks.read_bytes(), b"not a directory\n")

    def test_a_crash_mid_write_leaves_the_old_hook_intact(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        hook = hook_path(repo)
        complete = hook.read_bytes()

        # Simulate a process death after a partial write: the temporary
        # file is left truncated, then the write raises.
        crash = crashing_fdopen(OSError("simulated crash mid-write"))
        with mock.patch.object(local_hook_git, "hooks_dir", lambda: hook.parent), \
                mock.patch.object(local_hook_git, "top_level", lambda: Path(repo)), \
                mock.patch.object(os, "fdopen", crash):
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

    def test_failed_fdopen_closes_descriptor(self):
        import tempfile
        directory = tempfile.mkdtemp(prefix="local-hook-fdopen-")
        path = Path(directory) / "hook"
        with failing_fdopen() as closed:
            with self.assertRaises(OSError):
                local_hook._write_hook(path, local_hook.HOOK_SCRIPT)
        self.assertEqual(1, len(closed))
        # no leftover temp files
        self.assertEqual([], [n for n in os.listdir(directory) if n.startswith(".")])

    def test_script_entry_point(self):
        # ``run_tool`` calls ``main`` in-process for speed; this spawns the
        # script once so its `if __name__ == "__main__": sys.exit(main())`
        # wrapper and direct-run imports stay covered.
        repo = make_repo(self)
        script = Path(repo_root.ROOT) / "tools" / "local_hook.py"
        result = theme_install.run_captured(
            [sys.executable, str(script), "install"],
            cwd=repo,
            env=dict(os.environ),
        )
        assert_succeeded(self, result)
        self.assertTrue(hook_path(repo).is_file(), result.stdout + result.stderr)

    def test_a_planted_symlink_does_not_redirect_the_write(self):
        # A local user who can write the hooks directory can create a symlink
        # at the fixed temporary name the tool used to build. The write must
        # not follow it: the tool has to pick its own fresh temporary name.
        repo, hook = make_repo_with_hook(self)
        victim = Path(repo) / "victim.txt"
        victim.write_bytes(b"do not overwrite")
        planted = hook.with_name(f".{local_hook.HOOK_NAME}-{os.getpid()}.tmp")
        planted.symlink_to(victim)

        result = run_tool(repo, "install")

        assert_succeeded(self, result)
        self.assertEqual(b"do not overwrite", victim.read_bytes())
        self.assertIn(local_hook.MARKER, hook.read_text(encoding="utf-8"))

    def test_a_swap_after_the_exclusive_create_does_not_redirect_the_write(self):
        # ``mkstemp`` creates the temporary file exclusively, but another local
        # user who can write the hooks directory can still unlink it and park a
        # symlink at the name between the create and the write. The bytes must
        # go through the descriptor ``mkstemp`` returned, not the path, so the
        # symlink's target is left alone.
        repo, hook = make_repo_with_hook(self)
        victim = Path(repo) / "victim.txt"
        victim.write_bytes(b"do not overwrite")

        with mock.patch.object(
            atomic_write.tempfile, "mkstemp", swapping_mkstemp(victim)
        ):
            local_hook._write_hook(hook, local_hook.HOOK_SCRIPT)

        self.assertEqual(b"do not overwrite", victim.read_bytes())


class TestUninstall(unittest.TestCase):
    def test_removes_a_hook_it_installed(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)
        self.assertFalse(hook_path(repo).exists())

    def test_non_utf8_repo_path_is_handled_and_escaped(self):
        # uninstall resolves its path without git's --show-toplevel, so it
        # reaches the success line even in a non-UTF-8 repository; the path
        # there must be escaped too, not printed raw.
        repo = make_non_utf8_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("\\udcff", result.stdout)
        self.assertFalse(hook_path(repo).exists())

    def test_refuses_a_foreign_hook_and_leaves_it_alone(self):
        assert_refuses_a_foreign_hook(self, "uninstall")

    def test_refuses_an_oversize_hook(self):
        repo, hook = make_repo_with_hook(self)
        oversize = b"#!/bin/sh\n" + b"x" * local_hook._MAX_HOOK_BYTES
        hook.write_bytes(oversize)
        result = run_tool(repo, "uninstall")
        assert_exit_2_without_traceback(self, result)
        self.assertIn("larger than", result.stderr)
        self.assertEqual(oversize, hook.read_bytes())

    def test_refuses_a_symlinked_hook(self):
        repo, hook = make_repo_with_hook(self)
        target = Path(repo) / "outside"
        target.write_text("keep me", encoding="utf-8")
        hook.symlink_to(target)
        result = run_tool(repo, "uninstall")
        assert_failed(self, result)
        self.assertIn(str(hook), result.stderr)
        self.assertTrue(hook.is_symlink())
        self.assertEqual("keep me", target.read_text(encoding="utf-8"))

    def test_reports_a_hook_it_cannot_remove(self):
        # The hook it wrote can still fail to unlink (a read-only hooks
        # directory, for example). The OSError must become the tool's own
        # exit-2 diagnostic naming the path -- not a traceback -- and the
        # hook must stay in place so the operator can retry.
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        hook = hook_path(repo)
        complete = hook.read_bytes()

        with unlink_failing_for(hook, "simulated unlink failure"):
            result = run_tool(repo, "uninstall")

        assert_exit_2_without_traceback(self, result)
        self.assertIn("cannot remove", result.stderr)
        self.assertIn(str(hook), result.stderr)
        self.assertEqual(hook.read_bytes(), complete)

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

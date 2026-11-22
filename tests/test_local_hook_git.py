"""Tests for tools/local_hook_git.py: Git plumbing behind the local hook.

These cover how ``_git`` reports a missing git, a timeout or a bad reply, the
environment it passes to git, and the ``hooks_dir``/``top_level`` path
discovery. The hook installer CLI itself is tested in ``test_local_hook.py``.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.executable_stubs import write_executable
from support.local_hook.repos import (
    hook_path,
    in_directory,
    make_repo,
    run_git,
    run_tool,
)
from support.process_assertions import assert_succeeded
from tools import local_hook, local_hook_git


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
        write_executable(fake, "#!/bin/sh\nprintf '\\377\\376\\n'\n")
        with mock.patch.dict(os.environ, {"PATH": str(bindir)}):
            self.assertEqual(
                local_hook_git._git("rev-parse", "--show-toplevel"),
                "\udcff\udcfe",
            )

    def test_success_preserves_path_whitespace(self):
        with mock.patch.object(
            local_hook_git.subprocess,
            "run",
            return_value=mock.Mock(
                returncode=0, stderr="", stdout=" /hooks \n"
            ),
        ):
            self.assertEqual(
                local_hook_git._git("rev-parse", "--git-path", "hooks"),
                " /hooks ",
            )

    def test_success_with_empty_path_reply_is_rejected(self):
        with mock.patch.object(
            local_hook_git.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stderr="", stdout="\n"),
        ):
            with self.assertRaisesRegex(
                local_hook_git.LocalHookError, "empty path"
            ):
                local_hook_git.hooks_dir()

    def test_success_with_nul_path_reply_is_rejected(self):
        with mock.patch.object(
            local_hook_git.subprocess,
            "run",
            return_value=mock.Mock(
                returncode=0, stderr="", stdout="/hooks\0garbage\n"
            ),
        ):
            with self.assertRaisesRegex(
                local_hook_git.LocalHookError, "NUL in path"
            ):
                local_hook_git.hooks_dir()

    def test_hooks_dir_reports_path_resolution_errors(self):
        # A symlink loop reaches pathlib as RuntimeError; a filesystem error
        # during the walk (permissions, I/O) reaches it as OSError. Both must
        # become the CLI's LocalHookError diagnostic, so both are pinned.
        cases = (
            (RuntimeError("symlink loop"), "symlink loop"),
            (OSError(13, "Permission denied"), "[Errno 13] Permission denied"),
        )
        for failure, detail in cases:
            with self.subTest(failure=type(failure).__name__):
                self._assert_hooks_dir_error(failure, detail)

    def _assert_hooks_dir_error(self, failure, detail):
        """Pin a path-resolution failure's LocalHookError diagnostic."""
        with mock.patch.object(
            local_hook_git, "_git", return_value="/hooks"
        ), mock.patch.object(
            Path, "resolve", side_effect=failure
        ):
            with self.assertRaisesRegex(
                local_hook_git.LocalHookError,
                "cannot resolve path from git rev-parse --git-path hooks: "
                + re.escape(detail),
            ):
                local_hook_git.hooks_dir()

    def test_top_level_reports_path_resolution_errors_with_its_own_command(self):
        # top_level() names its own git command in the diagnostic, not the
        # hooks-directory command, so a copied-over command string would show.
        cases = (
            (RuntimeError("symlink loop"), "symlink loop"),
            (OSError(13, "Permission denied"), "[Errno 13] Permission denied"),
        )
        for failure, detail in cases:
            with self.subTest(failure=type(failure).__name__):
                self._assert_top_level_resolve_error(failure, detail)

    def _assert_top_level_resolve_error(self, failure, detail):
        with mock.patch.object(
            local_hook_git, "_git", return_value="/repo"
        ), mock.patch.object(
            Path, "resolve", side_effect=failure
        ):
            with self.assertRaisesRegex(
                local_hook_git.LocalHookError,
                "^cannot resolve path from git rev-parse --show-toplevel: "
                + re.escape(detail) + "$",
            ):
                local_hook_git.top_level()


class TestGitEnvironment(unittest.TestCase):
    """Pin the environment ``_git`` hands to git.

    Repository-override and ``GIT_CONFIG_*`` variables must not reach git,
    because an inherited value would select another repository or redirect
    ``core.hooksPath`` away from the checkout the installer operates on. Every
    other variable (PATH, HOME) must still pass through unchanged, or git
    cannot be found or configured. The command is patched, so the test
    observes the ``env`` keyword without running git.
    """

    OVERRIDES = (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_CEILING_DIRECTORIES",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
        "GIT_CONFIG_COUNT",
        "GIT_CONFIG_KEY_0",
        "GIT_CONFIG_VALUE_0",
        "GIT_CONFIG_GLOBAL",
    )

    def _env_seen_by_git(self, inherited):
        """Run ``_git`` with *inherited* as the whole environment; return git's env."""
        run = mock.Mock(
            return_value=mock.Mock(returncode=0, stderr="", stdout="/hooks\n")
        )
        with mock.patch.dict(os.environ, inherited, clear=True):
            with mock.patch.object(local_hook_git.subprocess, "run", run):
                local_hook_git._git("rev-parse", "--git-path", "hooks")
        return run.call_args.kwargs["env"]

    def test_repository_override_and_config_variables_are_withheld(self):
        inherited = {"PATH": "/usr/bin:/bin", "HOME": "/home/tester"}
        inherited.update({name: "/elsewhere" for name in self.OVERRIDES})
        env = self._env_seen_by_git(inherited)
        for name in self.OVERRIDES:
            with self.subTest(name=name):
                self.assertNotIn(name, env)

    def test_ordinary_variables_pass_through_unchanged(self):
        inherited = {"PATH": "/usr/bin:/bin", "HOME": "/home/tester"}
        inherited["GIT_DIR"] = "/elsewhere"
        env = self._env_seen_by_git(inherited)
        self.assertEqual(env, {"PATH": "/usr/bin:/bin", "HOME": "/home/tester"})


class TestGitDiscovery(unittest.TestCase):
    """Pin the Git path discovery ``local_hook_git`` documents.

    One install test replaces ``hooks_dir`` and ``top_level`` with lambdas,
    and every other real-git case is a plain fresh checkout, so no existing
    test reaches a configured ``core.hooksPath``, a linked worktree or a
    relative Git path. Each of those selects where Git actually runs the
    hook; getting it wrong writes a hook Git never runs.
    """

    def _git(self, cwd, *args):
        result = run_git(self, cwd, *args)
        return result.stdout.strip()

    def test_default_hooks_dir_is_the_resolved_dot_git_hook_dir(self):
        repo = make_repo(self)
        with in_directory(repo):
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
        with in_directory(sub):
            hooks = local_hook_git.hooks_dir()
        self.assertTrue(hooks.is_absolute())
        self.assertEqual((repo / ".git" / "hooks").resolve(), hooks)

    def test_a_relative_core_hooks_path_is_honoured(self):
        repo = make_repo(self)
        self._git(repo, "config", "core.hooksPath", "team-hooks")
        sub = repo / "sub"
        sub.mkdir()
        with in_directory(sub):
            hooks = local_hook_git.hooks_dir()
        self.assertTrue(hooks.is_absolute())
        self.assertEqual((repo / "team-hooks").resolve(), hooks)

    def test_an_absolute_core_hooks_path_is_used_as_given(self):
        repo = make_repo(self)
        shared = tmp_dir.make_tmp_dir(self) / "shared-hooks"
        shared.mkdir()
        self._git(repo, "config", "core.hooksPath", str(shared))
        with in_directory(repo):
            hooks = local_hook_git.hooks_dir()
        self.assertEqual(shared.resolve(), hooks)

    def test_config_environment_cannot_redirect_hook_install(self):
        repo = make_repo(self)
        outside = tmp_dir.make_tmp_dir(self) / "attacker-hooks"
        hostile = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.hooksPath",
            "GIT_CONFIG_VALUE_0": str(outside),
        }
        with mock.patch.dict(os.environ, hostile):
            result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertEqual(local_hook.HOOK_SCRIPT.encode(),
                         hook_path(repo).read_bytes())
        self.assertFalse(outside.exists())

    def test_git_dir_environment_cannot_redirect_hook_install(self):
        repo = make_repo(self)
        outside = make_repo(self)
        hostile = {"GIT_DIR": str(Path(outside) / ".git")}
        with mock.patch.dict(os.environ, hostile):
            result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertEqual(local_hook.HOOK_SCRIPT.encode(),
                         hook_path(repo).read_bytes())
        self.assertFalse(hook_path(outside).exists())

    def test_whitespace_in_core_hooks_path_survives_install_and_uninstall(self):
        repo = make_repo(self)
        configured = " team-hooks \t"
        self._git(repo, "config", "core.hooksPath", configured)
        expected = repo / configured / local_hook.HOOK_NAME
        trimmed = repo / configured.strip() / local_hook.HOOK_NAME

        assert_succeeded(self, run_tool(repo, "install"))
        self.assertEqual(local_hook.HOOK_SCRIPT.encode(), expected.read_bytes())
        self.assertFalse(trimmed.exists())
        assert_succeeded(self, run_tool(repo, "uninstall"))
        self.assertFalse(expected.exists())

    def test_top_level_preserves_a_trailing_space_in_the_repository_name(self):
        repo = make_repo(self)
        renamed = repo / "checkout "
        self._git(repo, "init", "-q", str(renamed))
        with in_directory(renamed):
            self.assertEqual(renamed.resolve(), local_hook_git.top_level())

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
        with in_directory(linked):
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
        with in_directory(sub):
            top = local_hook_git.top_level()
        self.assertTrue(top.is_absolute())
        self.assertEqual(repo.resolve(), top)


if __name__ == "__main__":
    unittest.main()

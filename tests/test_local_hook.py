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

import os
import shutil
import stat
import sys
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import theme_install
from support import tmp_dir
from support.atomic_write_failures import crashing_fdopen, swapping_mkstemp
from support.close_tracking import failing_fdopen
from support.executable_stubs import write_executable
from support.local_hook.repos import (
    assert_refuses_a_foreign_hook,
    assert_refuses_an_oversize_hook,
    hook_path,
    make_non_utf8_repo,
    make_repo,
    make_repo_with_hook,
    run_tool,
)
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from tools import atomic_write, local_hook, local_hook_git


def write_fake_make(bindir, record, exit_status=0):
    """Write an executable ``make`` that records its cwd and argv, then exits."""
    bindir.mkdir(parents=True, exist_ok=True)
    make = bindir / "make"
    write_executable(
        make,
        "#!/bin/sh\n"
        f'printf \'%s\\n\' "$PWD" > "{record}"\n'
        f'printf \'%s\\n\' "$*" >> "{record}"\n'
        f"exit {exit_status}\n",
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

    def test_install_announces_the_hook_path_and_the_root_it_runs_from(self):
        repo = make_repo(self)
        result = run_tool(repo, "install")
        assert_succeeded(self, result)
        self.assertEqual("", result.stderr)
        # The success line tells the operator which hook was written and the
        # worktree root the hook's `make apply` runs from; both must be named.
        self.assertIn(str(hook_path(repo)), result.stdout)
        # The root is a prefix of the hook path, so pin it in its own clause.
        self.assertIn(f"(runs make apply from {repo})", result.stdout)

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

    def test_marker_inside_a_foreign_hook_does_not_claim_ownership(self):
        repo, hook = make_repo_with_hook(self)
        foreign = (
            b"#!/bin/sh\n"
            b"# unrelated hook\n"
            + local_hook.MARKER.encode("ascii")
            + b"\nrm -f important-file\n"
        )
        hook.write_bytes(foreign)

        result = run_tool(repo, "install")

        assert_failed(self, result)
        self.assertEqual(foreign, hook.read_bytes())

    def test_fifo_swapped_after_lstat_is_rejected_without_opening_blocking(self):
        repo, hook = make_repo_with_hook(self)
        hook.write_bytes(b"regular hook")
        # Model the lstat/open race: lstat reports a regular file, then the
        # pathname is replaced by a FIFO before the descriptor open.
        real_lstat = Path.lstat
        changed = False

        def swap_after_lstat(path):
            nonlocal changed
            result = real_lstat(path)
            if path == hook and not changed:
                changed = True
                hook.unlink()
                hook.write_bytes(b"regular during check")
                result = real_lstat(path)
                hook.unlink()
                os.mkfifo(hook)
            return result

        with mock.patch.object(Path, "lstat", swap_after_lstat):
            with self.assertRaises(local_hook.LocalHookError) as caught:
                local_hook._existing_hook(hook)
        self.assertIn("non-regular", str(caught.exception))

    def test_refuses_an_oversize_hook_without_reading_it_whole(self):
        # A hook far larger than the read cap cannot be one this tool wrote.
        # The tool must refuse it by name instead of loading the whole file
        # into memory; a multi-gigabyte hook would otherwise raise MemoryError
        # (which is not an OSError) and escape as a traceback.
        assert_refuses_an_oversize_hook(self, "install")

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

    def test_a_refused_write_exits_2_naming_the_hook_without_a_traceback(self):
        # The hook is written through write_atomically; a PermissionError
        # there (a read-only hooks directory, say) must become the tool's
        # own exit-2 diagnostic naming the hook path and the error, not an
        # escaped traceback. The fresh repository has no hook, so nothing
        # is left behind at the hook path either.
        repo = make_repo(self)
        hook = hook_path(repo)
        refused = PermissionError(13, "Permission denied")
        with mock.patch.object(local_hook, "write_atomically", side_effect=refused):
            result = run_tool(repo, "install")

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {hook}", result.stderr)
        self.assertIn("Permission denied", result.stderr)
        self.assertFalse(hook.exists(), "a refused write must not create the hook")

    def test_a_refused_hooks_directory_creation_exits_2(self):
        repo = make_repo(self)
        hook = hook_path(repo)
        hooks = hook.parent
        refused = PermissionError(13, "Permission denied")
        original_mkdir = Path.mkdir

        def refuse_hooks_directory(path, *args, **kwargs):
            if path == hooks:
                raise refused
            return original_mkdir(path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", refuse_hooks_directory):
            result = run_tool(repo, "install")

        assert_exit_2_without_traceback(self, result)
        self.assertIn(f"cannot write {hook}", result.stderr)
        self.assertIn("Permission denied", result.stderr)
        self.assertFalse(hook.exists())

    def test_failed_fdopen_closes_descriptor(self):
        path = tmp_dir.make_tmp_dir(self) / "hook"
        with failing_fdopen() as closed:
            with self.assertRaises(OSError):
                local_hook._write_hook(path, local_hook.HOOK_SCRIPT)
        self.assertEqual(1, len(closed))
        # no leftover temp files
        self.assertEqual(
            [], [n for n in os.listdir(path.parent) if n.startswith(".")]
        )

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

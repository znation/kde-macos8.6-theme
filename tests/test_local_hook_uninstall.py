"""Tests for the ``uninstall`` subcommand of tools/local_hook.py.

The install side, the hook body and the Makefile targets are tested in
``test_local_hook.py``. Each test makes a throwaway ``git init`` repository
through the fixtures in ``support.local_hook.repos``.
"""

import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
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
from support.unlink_failure import unlink_failing_for
from tools import local_hook


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

    def test_marker_inside_a_foreign_hook_does_not_authorize_removal(self):
        repo, hook = make_repo_with_hook(self)
        foreign = (
            b"#!/bin/sh\n"
            + local_hook.MARKER.encode("ascii")
            + b"\n# another tool's hook\n"
        )
        hook.write_bytes(foreign)

        result = run_tool(repo, "uninstall")

        assert_failed(self, result)
        self.assertEqual(foreign, hook.read_bytes())

    def test_refuses_an_oversize_hook(self):
        assert_refuses_an_oversize_hook(self, "uninstall")

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

    def test_uninstall_announces_the_hook_it_removed(self):
        repo = make_repo(self)
        assert_succeeded(self, run_tool(repo, "install"))
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)
        self.assertEqual("", result.stderr)
        self.assertIn("removed", result.stdout)
        self.assertIn(str(hook_path(repo)), result.stdout)

    def test_uninstall_without_a_hook_names_the_missing_path_and_claims_no_removal(self):
        repo = make_repo(self)
        result = run_tool(repo, "uninstall")
        assert_succeeded(self, result)
        self.assertEqual("", result.stderr)
        self.assertIn(str(hook_path(repo)), result.stdout)
        self.assertNotIn("removed", result.stdout)


if __name__ == "__main__":
    unittest.main()

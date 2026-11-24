"""Repository fixtures shared by the local-hook test modules.

``tests/test_local_hook.py`` (the hook installer CLI),
``tests/test_local_hook_uninstall.py`` (its ``uninstall`` subcommand) and
``tests/test_local_hook_git.py`` (the Git plumbing that ``tools/local_hook_git.py``
provides) all build throwaway ``git init`` repositories and run the
``local_hook`` CLI inside them. Test modules never import each other, so these
fixtures live here.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import theme_install
from support import tmp_dir
from support.cli_fixtures import run_main
from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_succeeded,
)
from tools import local_hook


def run_git(case, cwd, *args):
    """Run a Git command in *cwd* and attach output if it fails."""
    result = theme_install.run_captured(
        ["git", *args], cwd=cwd, env=dict(os.environ)
    )
    assert_succeeded(case, result)
    return result


def make_repo(case):
    """Create a fresh ``git init`` repository and return its root path."""
    repo = tmp_dir.make_tmp_dir(case)
    run_git(case, repo, "init", "-q")
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
    run_git(case, repo, "init", "-q")
    return repo


@contextlib.contextmanager
def in_directory(path):
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
    with in_directory(repo):
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
    place. ``TestInstall`` in ``tests/test_local_hook.py`` and ``TestUninstall`` in
    ``tests/test_local_hook_uninstall.py`` each call this once, so the
    sequence is stated here.
    """
    repo, hook = make_repo_with_hook(case)
    foreign = b"#!/bin/sh\ngit lfs post-commit \"$@\"\n"
    hook.write_bytes(foreign)
    result = run_tool(repo, command)
    assert_failed(case, result)
    case.assertIn(str(hook), result.stderr)
    case.assertEqual(foreign, hook.read_bytes())


def assert_refuses_an_oversize_hook(case, command):
    """Assert *command* rejects an oversized hook and preserves its bytes.

    ``install`` and ``uninstall`` share the capped-read refusal; both tests
    use this fixture and verify the hook remains intact.
    """
    repo, hook = make_repo_with_hook(case)
    oversize = b"#!/bin/sh\n" + b"x" * local_hook._MAX_HOOK_BYTES
    hook.write_bytes(oversize)
    result = run_tool(repo, command)
    assert_exit_2_without_traceback(case, result)
    case.assertIn(str(hook), result.stderr)
    case.assertIn("larger than", result.stderr)
    case.assertEqual(oversize, hook.read_bytes())


FOREIGN_HOOK_REFUSALS = {
    "install": "refusing to overwrite a foreign hook",
    "uninstall": "refusing to remove a foreign hook",
}


def assert_exactly_cap_hook_is_refused_as_foreign(case, command):
    """Assert a hook of exactly ``_MAX_HOOK_BYTES`` bytes misses the cap.

    The reader reads one byte past the cap and refuses only
    ``len(data) > _MAX_HOOK_BYTES``, so a hook of exactly the cap is not an
    oversize hook: the ownership check runs on its bytes and rejects it as
    foreign. A ``>=`` cap check would flip exactly this file to the oversize
    refusal. (A capped ``read(_MAX_HOOK_BYTES)`` would leave this file's
    verdict alone -- it fills the read either way -- but would truncate
    over-cap hooks below the cap, which ``assert_refuses_an_oversize_hook``
    already catches.) Both subcommands share the boundary, so each suite
    pins its own verdict.
    """
    repo, hook = make_repo_with_hook(case)
    at_cap = b"#!/bin/sh\n" + b"x" * (local_hook._MAX_HOOK_BYTES - 10)
    case.assertEqual(local_hook._MAX_HOOK_BYTES, len(at_cap))
    hook.write_bytes(at_cap)

    result = run_tool(repo, command)

    assert_exit_2_without_traceback(case, result)
    case.assertIn(str(hook), result.stderr)
    case.assertIn(FOREIGN_HOOK_REFUSALS[command], result.stderr)
    case.assertNotIn("larger than", result.stderr)
    case.assertEqual(at_cap, hook.read_bytes())

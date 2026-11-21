"""Repository fixtures shared by the local-hook test modules.

``tests/test_local_hook.py`` (the hook installer CLI) and
``tests/test_local_hook_git.py`` (the Git plumbing that ``tools/local_hook_git.py``
provides) both build throwaway ``git init`` repositories and run the
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
from support.process_assertions import assert_succeeded
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

"""Git path discovery and command failures for the local hook installer.

Resolve the current worktree and its effective hooks directory through Git,
including linked worktrees and ``core.hooksPath``. Hook file ownership and
publication stay in ``tools/local_hook.py``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

COMMAND_TIMEOUT = 30.0


class LocalHookError(Exception):
    """A git invocation or filesystem condition the tool reports and refuses."""


def _git(*args: str) -> str:
    """Run ``git *args*`` in the current directory; return its stripped stdout.

    A missing git, a timeout, an unrunnable git, or a non-zero exit becomes a
    `LocalHookError` whose message is git's own diagnostic where there is one.
    Git prints a path raw, and a repository path may hold bytes that are not
    UTF-8 (Linux allows that), so the output is decoded with
    ``surrogateescape`` instead of strictly: the bytes round-trip through
    ``os.fsencode`` for the filesystem calls, and a strict decode would
    otherwise raise an uncaught ``UnicodeDecodeError`` naming neither the tool
    nor the command.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            errors="surrogateescape",
            timeout=COMMAND_TIMEOUT,
        )
    except FileNotFoundError as exc:
        raise LocalHookError("git not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise LocalHookError(
            f"git {' '.join(args)} timed out after {COMMAND_TIMEOUT:g}s"
        ) from exc
    except OSError as exc:
        # Git exists but cannot be launched (a permission error, a directory
        # on PATH, a deleted working directory). Report it as this tool's own
        # error so the caller prints a diagnostic and exits 2, instead of a
        # traceback naming neither the tool nor the command.
        raise LocalHookError(f"cannot run git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise LocalHookError(
            detail
            or f"git {' '.join(args)} exited {result.returncode}"
        )
    return result.stdout.strip()


def hooks_dir() -> Path:
    """Return the absolute hooks directory of the current repository.

    ``git rev-parse --git-path hooks`` honours ``core.hooksPath`` and, in a
    linked worktree, names the common hooks directory shared with the main
    checkout. Its output may be relative to the current directory, so it is
    resolved to an absolute path here.
    """
    return Path(_git("rev-parse", "--git-path", "hooks")).resolve()


def top_level() -> Path:
    """Return the absolute root of the current work tree."""
    return Path(_git("rev-parse", "--show-toplevel")).resolve()

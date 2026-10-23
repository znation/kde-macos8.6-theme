"""Install a local-only post-commit hook that re-applies the theme.

``make install-local-hook`` writes a ``post-commit`` hook into this clone's
git hooks directory -- the common ``.git/hooks`` that the
``.tumwater/worktrees/*`` linked worktrees share -- so that every commit
installs and applies the freshly built theme through ``make apply``. The hook
is never committed, so other clones and contributors are unaffected.
``make uninstall-local-hook`` removes it.

The tool refuses to touch a ``post-commit`` it did not write: overwriting a
hook another tool owns (this clone's Git LFS hook, for example) would silently
break it.

Usage::

    python3 tools/local_hook.py install
    python3 tools/local_hook.py uninstall

Exit status: 0 on success, 2 when an existing hook blocks the operation (a
foreign hook, a symlink, a non-regular file, an oversize file, or an
unreadable file), a git invocation fails, or the arguments are a usage error.
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

if __package__:
    from tools.argument_parsing import EscapingArgumentParser
    from tools.diagnostics import report_error
    from tools.terminal import escape_controls
else:  # run directly: python3 tools/local_hook.py
    from argument_parsing import EscapingArgumentParser
    from diagnostics import report_error
    from terminal import escape_controls

TOOL = "local_hook"
HOOK_NAME = "post-commit"
# The line that marks a hook as this tool's; a hook without it is foreign.
MARKER = "# installed by kde-macos8.6-theme: make install-local-hook"
COMMAND_TIMEOUT = 30.0
# The hook this tool writes is a few hundred bytes. An existing hook is read
# only to look for MARKER, and the path holds whatever another tool or the
# user put there, at any size, so a huge file must not be loaded whole: a
# multi-gigabyte hook would exhaust memory and raise MemoryError (which is not
# an OSError and would escape as a traceback) instead of the documented exit-2
# refusal. Read at most this many bytes plus one; a longer file is refused by
# name rather than read.
_MAX_HOOK_BYTES = 1 << 20

# The hook body. It re-derives the worktree root at run time so a commit in
# any linked worktree applies that worktree's tree, sends both output streams
# to stderr, and exits 0 so a failed apply never blocks the commit.
HOOK_SCRIPT = f"""\
#!/bin/sh
{MARKER}
# Local-only post-commit hook: install and re-apply the theme after each
# commit. Output goes to stderr; a failed apply is swallowed so it never
# blocks the commit. Remove it with `make uninstall-local-hook`.
cd "$(git rev-parse --show-toplevel)" && make apply 1>&2
exit 0
"""


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


def _existing_hook(path: Path) -> bytes | None:
    """Return *path*'s bytes, or None when nothing occupies that path.

    ``lstat`` sees a symlink as itself rather than as its target, so a
    symlink (a dangling one included) is refused: writing through it could
    clobber a file outside the hooks directory. A non-regular file and an
    unreadable file are refused too, so the marker check can never silently
    pass. A file larger than ``_MAX_HOOK_BYTES`` is refused without being read
    whole, so an oversize hook cannot exhaust memory. Each refusal raises
    `LocalHookError`, which the callers report with exit status 2.
    """
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise LocalHookError(f"cannot inspect {path}: {exc}") from exc
    if stat.S_ISLNK(mode):
        raise LocalHookError(f"refusing to touch a symlinked hook: {path}")
    if not stat.S_ISREG(mode):
        raise LocalHookError(f"refusing to touch a non-regular hook: {path}")
    try:
        # Read at most one byte past the cap: enough to detect an oversize
        # hook without loading the rest of it.
        with path.open("rb") as handle:
            data = handle.read(_MAX_HOOK_BYTES + 1)
    except OSError as exc:
        raise LocalHookError(f"cannot read {path}: {exc}") from exc
    if len(data) > _MAX_HOOK_BYTES:
        raise LocalHookError(
            f"refusing to touch a hook larger than {_MAX_HOOK_BYTES} bytes: "
            f"{path}"
        )
    return data


def _write_hook(path: Path, content: str) -> None:
    """Write *content* to *path* atomically, with the executable bit set.

    The hook is written to a sibling temporary file, made executable, and then
    renamed over *path*, so a crash mid-write leaves either the previous hook
    or the complete new one -- never a truncated file that git would run. The
    temporary file is removed when the write fails.

    The temporary file's name is picked by :func:`tempfile.mkstemp`, which
    creates it exclusively: a fixed, guessable name would let another local
    user who can write the hooks directory park a symlink there first and make
    the write clobber whatever file it names. The bytes go through the file
    descriptor ``mkstemp`` returned rather than the path being reopened by
    name, so a path swapped after the exclusive create cannot redirect them.
    """
    descriptor, partial_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{HOOK_NAME}-", suffix=".tmp"
    )
    partial = Path(partial_name)
    descriptor_closed = False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as destination:
            descriptor_closed = True
            # mkstemp opens the file 0600; the hook must be executable.
            os.chmod(destination.fileno(), 0o755)
            destination.write(content)
        os.replace(partial, path)
    except BaseException:
        if not descriptor_closed:
            os.close(descriptor)
        partial.unlink(missing_ok=True)
        raise


def install() -> int:
    """Write the local post-commit hook; return the process exit status."""
    try:
        hooks = hooks_dir()
        top = top_level()
        path = hooks / HOOK_NAME
        existing = _existing_hook(path)
    except LocalHookError as exc:
        return report_error(TOOL, str(exc))
    if existing is not None and MARKER.encode() not in existing:
        return report_error(
            TOOL, f"refusing to overwrite a foreign hook: {path}"
        )
    try:
        hooks.mkdir(parents=True, exist_ok=True)
        _write_hook(path, HOOK_SCRIPT)
    except OSError as exc:
        return report_error(TOOL, f"cannot write {path}: {exc}")
    print(
        f"{TOOL}: installed {escape_controls(str(path))} "
        f"(runs make apply from {escape_controls(str(top))})"
    )
    return 0


def uninstall() -> int:
    """Remove the local post-commit hook; return the process exit status."""
    try:
        hooks = hooks_dir()
        path = hooks / HOOK_NAME
        existing = _existing_hook(path)
    except LocalHookError as exc:
        return report_error(TOOL, str(exc))
    if existing is None:
        print(
            f"{TOOL}: no {HOOK_NAME} hook to remove at "
            f"{escape_controls(str(path))}"
        )
        return 0
    if MARKER.encode() not in existing:
        return report_error(TOOL, f"refusing to remove a foreign hook: {path}")
    try:
        path.unlink()
    except OSError as exc:
        return report_error(TOOL, f"cannot remove {path}: {exc}")
    print(f"{TOOL}: removed {escape_controls(str(path))}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the local-hook CLI; *argv* is the argument list without a program name."""
    parser = EscapingArgumentParser(
        prog=TOOL,
        description=(
            "Install or remove the local-only post-commit hook that runs "
            "'make apply'."
        ),
        epilog=(
            "exit status: 0 on success, 2 when an existing hook blocks the "
            "operation (a foreign hook, a symlink, a non-regular file, an "
            "oversize file, or an unreadable file), a git invocation fails, "
            "or the arguments are a usage error"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "install", help="write the local post-commit hook"
    )
    subparsers.add_parser(
        "uninstall", help="remove the local post-commit hook"
    )
    args = parser.parse_args(argv)
    if args.command == "install":
        return install()
    return uninstall()


if __name__ == "__main__":
    sys.exit(main())

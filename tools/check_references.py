#!/usr/bin/env python3
"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail. It also rejects
unmaterialized Git LFS pointer files, files whose bytes are not a known image
format (such as an HTML error page saved under an image name), and source URLs
that are not well-formed absolute URLs (a bare host, a relative path, or a raw
space is a broken citation).

Usage::

    python3 tools/check_references.py              # check the repository
    python3 tools/check_references.py --self-test  # exercise the checks
    python3 tools/check_references.py --help       # show usage
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from tools.check_references_selftest import run_self_test
    from tools.reference_validation import (
        SOURCES_NAME,
        _check_entries,
        _check_undeclared,
        _read_sources_text,
        _resolves_within,
    )
    from tools.terminal import escape_controls
except ImportError:  # run directly: python3 tools/check_references.py
    from check_references_selftest import run_self_test
    from reference_validation import (
        SOURCES_NAME,
        _check_entries,
        _check_undeclared,
        _read_sources_text,
        _resolves_within,
    )
    from terminal import escape_controls

REFERENCE_DIR = "macos8.6-screenshots"

USAGE = """\
usage: check_references.py [--self-test | --help]

Check that macos8.6-screenshots/sources.txt matches the images on disk.

options:
  --self-test  run the checker's own fixtures instead of the repository
  -h, --help   show this message and exit
"""


def check_references(directory: Path) -> list[str]:
    """Return a list of human-readable problems in *directory*.

    An empty list means every source entry names an existing image, every image
    has exactly one entry, and every entry has the three expected fields with an
    absolute source URL.
    """
    sources = directory / SOURCES_NAME
    if not _resolves_within(directory, sources):
        return [f"{sources}: points outside {directory}/ (a symlink escape)"]
    if not sources.is_file():
        return [f"{sources}: missing sources file"]

    sources_text, read_problem = _read_sources_text(sources)
    if sources_text is None:
        return [read_problem]

    problems, entries = _check_entries(directory, sources, sources_text)
    return problems + _check_undeclared(directory, entries)


def _self_test() -> int:
    """Run the checker against its built-in fixtures; return 0 when all behave."""
    return run_self_test(check_references, main, SOURCES_NAME)


def _plural(count: int, singular: str) -> str:
    """Return *singular*, pluralized with ``s`` when *count* is not one.

    Both count-bearing diagnostics this module prints (the unknown-argument
    error and the problem summary) read as broken English when a single item
    is followed by ``(s)``; this picks the form from the actual count.
    """
    return singular if count == 1 else singular + "s"


def main(argv: list[str] | None = None) -> int:
    """Run the checker; *argv* is the argument list without a program name.

    Following ``argparse`` and the sibling ``tools/fidelity.py``, ``None``
    reads ``sys.argv``. A caller that passes ``["--help"]`` gets usage instead
    of having its first real argument silently dropped as a program name and
    the repository check run instead.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--self-test"]:
        return _self_test()
    if args in (["-h"], ["--help"]):
        print(USAGE, end="")
        return 0
    if args:
        print(
            f"error: unknown {_plural(len(args), 'argument')}: "
            f"{escape_controls(' '.join(args))}",
            file=sys.stderr,
        )
        print(USAGE, end="", file=sys.stderr)
        return 2

    directory = Path(__file__).resolve().parent.parent / REFERENCE_DIR
    problems = check_references(directory)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        print(
            f"{len(problems)} {_plural(len(problems), 'problem')} "
            "in the reference set",
            file=sys.stderr,
        )
        return 1
    print(f"{directory}: reference set is consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())

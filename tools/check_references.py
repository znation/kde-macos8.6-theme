"""Check that the Mac OS 8.6 reference screenshot set is self-consistent.

``macos8.6-screenshots/sources.txt`` is the provenance record for the reference
set: one ``<filename> | <source URL> | <version label>`` line per image. This
script verifies that record against the files actually on disk, so a renamed or
forgotten image cannot silently drop out of the evidence trail. It also rejects
unmaterialized Git LFS pointer files, files whose bytes are not a known image
format (such as an HTML error page saved under an image name), and source URLs
that are not well-formed absolute URLs (a bare host, a relative path, or a raw
space is a broken citation). A reference directory that resolves outside the
repository (a checked-in symlink) is refused before anything inside it is read.

Usage::

    python3 tools/check_references.py              # check the repository
    python3 tools/check_references.py --self-test  # exercise the checks
    python3 tools/check_references.py --help       # show usage

Exit status: 0 when the repository check or the self-test passes (and for
``--help``/``-h``), 1 when the reference set has problems or a self-test case
misbehaves, and 2 for an unrecognized argument.
"""

from __future__ import annotations

import sys

try:
    from tools.check_references_selftest import run_self_test
    from tools.diagnostics import report_error
    from tools.reference_validation import SOURCES_NAME, check_references
    from tools.repo_root import ROOT
    from tools.terminal import escape_controls
except ImportError:  # run directly: python3 tools/check_references.py
    from check_references_selftest import run_self_test
    from diagnostics import report_error
    from reference_validation import SOURCES_NAME, check_references
    from repo_root import ROOT
    from terminal import escape_controls

TOOL = "check_references"
REFERENCE_DIR = "macos8.6-screenshots"

USAGE = """\
usage: check_references.py [--self-test | --help]

Check that macos8.6-screenshots/sources.txt matches the images on disk.

options:
  --self-test  run the checker's own fixtures instead of the repository
  -h, --help   show this message and exit
"""


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
        status = report_error(
            TOOL,
            f"unknown {_plural(len(args), 'argument')}: {' '.join(args)}",
        )
        print(USAGE, end="", file=sys.stderr)
        return status

    directory = ROOT / REFERENCE_DIR
    problems = check_references(directory)
    if problems:
        for problem in problems:
            # A problem line names contributor-supplied text -- a reference-set
            # filename, or the ``str(exc)`` of the read that failed -- so it is
            # escaped here, the way ``report_error`` escapes the tool's other
            # diagnostics, instead of driving the operator's terminal with a
            # raw ESC byte when it is printed.
            print(escape_controls(problem), file=sys.stderr)
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

"""Shared helpers for tests that plant a FIFO where a tool expects a file.

A FIFO's ``open()`` blocks until a writer appears, so a tool that reads one
without refusing it would stall ``make check`` with no diagnostic. A suite
plants a pipe and runs the tool in a child process so a regression is a
bounded timeout instead of a hung run; these helpers name the two halves of
that::

    make_fifo(self, path)               # skip the test when unsupported
    assert_fifo_refused(self, result, path)

*result* is a completed child process with decoded-text ``stdout``/``stderr``,
as ``support.snippet_child.run`` returns. ``assert_fifo_refused`` pins the
by-name refusal: exit status 2, a ``cannot read <path>`` diagnostic naming the
pipe, the ``not a regular file`` reason, and the pipe still in place. The GTK
apply and Firefox install suites use it where the tool's public contract is
that exit status; suites that only promise a refusal without exit status 2
assert their own wording.
"""

from __future__ import annotations

import os
import stat


def make_fifo(case, path):
    """Create the FIFO at *path*, skipping *case* when the platform lacks one."""
    if not hasattr(os, "mkfifo"):
        case.skipTest("os.mkfifo is not available on this platform")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkfifo(path)
    except OSError as exc:
        case.skipTest(f"cannot create a FIFO: {exc}")


def assert_fifo_refused(case, result, path):
    """Assert the child refused the FIFO at *path* by name instead of reading it.

    *result* must be the completed child process running the tool; its output
    is attached to a failure. The exit status is 2, stderr names *path* with
    ``cannot read`` and says ``not a regular file``, and *path* is still a
    FIFO after the run.
    """
    case.assertEqual(2, result.returncode, result.stdout + result.stderr)
    case.assertIn(f"cannot read {path}", result.stderr)
    case.assertIn("not a regular file", result.stderr)
    case.assertTrue(stat.S_ISFIFO(path.stat().st_mode))

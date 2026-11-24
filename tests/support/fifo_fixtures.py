"""Shared helpers for tests that plant a FIFO where a tool expects a file.

A FIFO's ``open()`` blocks until a writer appears, so a tool that reads one
without refusing it would stall ``make check`` with no diagnostic. A suite
plants a pipe and runs the tool in a child process so a regression is a
bounded timeout instead of a hung run; these helpers name the pieces of
that::

    make_fifo(self, path)                     # skip the test when unsupported
    fifo_swap_opener(fifo)                    # os.open stand-in for a swap
    assert_fifo_refused(self, result, path)
    assert_fifo_read_refused(self, result, path)
    assert_read_refused_in_child(self, fifo, code, *args, cwd=...)

*result* is a completed child process with decoded-text ``stdout``/``stderr``,
as ``support.snippet_child.run`` returns. ``assert_fifo_refused`` pins the
by-name refusal: exit status 2, a ``cannot read <path>`` diagnostic naming the
pipe, the ``not a regular file`` reason, and the pipe still in place. The GTK
apply and Firefox install suites use it where the tool's public contract is
that exit status. ``assert_fifo_read_refused`` is the looser check for tools
whose contract only promises a non-zero exit and a diagnostic naming the pipe
as not a regular file.
"""

from __future__ import annotations

import os
import stat

from support import snippet_child


def make_fifo(case, path):
    """Create the FIFO at *path*, skipping *case* when the platform lacks one."""
    if not hasattr(os, "mkfifo"):
        case.skipTest("os.mkfifo is not available on this platform")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.mkfifo(path)
    except OSError as exc:
        case.skipTest(f"cannot create a FIFO: {exc}")


def fifo_swap_opener(fifo):
    """Return an ``os.open`` replacement that opens *fifo* instead of the path.

    For a ``mock.patch.object(..., "open", side_effect=...)`` that makes a
    regular file look swapped for a FIFO between a path check and the open.
    The replacement opens *fifo* ``O_RDWR | O_NONBLOCK``: ``O_RDWR`` keeps the
    test independent of the flags under test, so a missing ``O_NONBLOCK``
    fails the assertion instead of blocking, and ``O_NONBLOCK`` keeps the open
    off any waiting path. Call this before patching ``os.open``: it captures
    the real ``os.open`` at call time.
    """
    real_open = os.open

    def open_the_fifo(target, flags, *args, **kwargs):
        return real_open(fifo, os.O_RDWR | os.O_NONBLOCK)

    return open_the_fifo


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


def assert_fifo_read_refused(case, result, path):
    """Assert the child refused the FIFO at *path* instead of reading it.

    The looser companion to :func:`assert_fifo_refused` for a tool that must
    refuse a non-regular file by name but does not promise that function's
    exit status or ``cannot read`` wording: the child exits non-zero, and its
    stderr names *path* and says ``not a regular file``. *result* is the
    completed child process, and its output is attached to a failure.
    """
    case.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
    case.assertIn("not a regular file", result.stderr)
    case.assertIn(str(path), result.stderr)


def assert_read_refused_in_child(case, fifo, code, *args, cwd, timeout=10):
    """Plant a FIFO at *fifo* and assert the reader *code* refuses it in a child.

    The full choreography of a suite's ``test_refuses_a_fifo_instead_of_blocking``:
    :func:`make_fifo` plants the pipe (skipping *case* when the platform lacks
    one), :func:`support.snippet_child.run` runs *code* in a child process with
    the *args* as its ``sys.argv[1:]`` -- so a reader that blocks is a bounded
    timeout, not a stalled run -- and :func:`assert_fifo_read_refused` pins the
    refusal. *cwd* is the child's working directory, passed through; *timeout*
    bounds the child and defaults to the 10 seconds the suites pinned.

    The single-read guard suites use it: ``test_kde_config``,
    ``test_package_metadata``, ``test_splash_qml``, ``test_placeholders`` (both
    reader guards), ``test_theme_defaults``, ``test_desktoptheme_provenance``,
    ``test_readme_theme_files`` and ``test_containment`` (through its two-reader
    wrapper). The ``assert_fifo_refused`` suites (``test_fidelity_sources``,
    ``test_remove_firefox``, ``test_apply_gtk_unreadable_config``) pin the
    stronger exit-status-2 contract and run their own children, and
    ``test_aurorae_frame``'s guard drives two readers in one test under
    ``subTest``, where a :func:`make_fifo` skip would report wrongly, so both
    keep their own runs.
    """
    make_fifo(case, fifo)
    child = snippet_child.run([code, *args], cwd=cwd, timeout=timeout)
    assert_fifo_read_refused(case, child, fifo)

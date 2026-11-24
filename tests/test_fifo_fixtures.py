"""Tests for tests/support/fifo_fixtures.py -- the FIFO-planting helpers.

The suites that share these helpers (``test_apply_gtk_unreadable_config``,
``test_check_parallel_order`` and the Firefox install suites) drive
``make_fifo`` on the happy path and ``fifo_swap_opener`` only as a patched
``os.open`` stand-in: nothing failed if ``make_fifo`` stopped creating a FIFO
when one is asked for, if its skip branches broke, or if ``fifo_swap_opener``
started honouring the flags under test (an ``O_RDONLY``-shaped open would
block until a writer appears and hang the suite). This module pins those
behaviours: ``make_fifo`` creates the FIFO (creating parents), skips when the
platform lacks ``os.mkfifo`` or the node cannot be created,
``fifo_swap_opener`` opens the FIFO ``O_RDWR | O_NONBLOCK`` whatever target,
flags and keyword arguments the caller passes, using the ``os.open`` it
captured at call time, and ``assert_read_refused_in_child`` chains the three
steps a suite's FIFO-refusal guard needs: plant, run the reader snippet in a
bounded child, pin the refusal.
"""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import stat
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fifo_fixtures import assert_read_refused_in_child  # noqa: E402
from support.fifo_fixtures import fifo_swap_opener  # noqa: E402
from support.fifo_fixtures import make_fifo  # noqa: E402


class TempRootCase(unittest.TestCase):
    """A per-test scratch directory for the FIFO paths."""

    def setUp(self):
        import tempfile

        self.root = tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)

    def path(self, *parts):
        return Path(self.root.name, *parts)


class TestMakeFifo(TempRootCase):
    def test_creates_a_fifo_at_the_path(self):
        target = self.path("nested", "pipe")
        make_fifo(self, target)
        self.assertTrue(stat.S_ISFIFO(os.stat(target).st_mode))

    def test_skips_when_the_platform_lacks_mkfifo(self):
        saved = os.mkfifo
        del os.mkfifo
        try:
            with self.assertRaises(unittest.SkipTest):
                make_fifo(self, self.path("pipe"))
        finally:
            os.mkfifo = saved

    def test_skips_when_the_fifo_cannot_be_created(self):
        # A directory already occupies the node, so os.mkfifo raises
        # FileExistsError (an OSError) and the helper must skip, not die.
        target = self.path("pipe")
        os.mkdir(target)
        with self.assertRaises(unittest.SkipTest):
            make_fifo(self, target)


class TestFifoSwapOpener(TempRootCase):
    def test_opens_the_fifo_regardless_of_the_requested_flags(self):
        fifo = self.path("pipe")
        make_fifo(self, fifo)
        open_the_fifo = fifo_swap_opener(fifo)
        # A reader-shaped request (O_RDONLY plus O_CREAT and extra keyword
        # arguments) must still open the FIFO read-write and non-blocking:
        # O_RDWR makes the open independent of the flags under test and
        # O_NONBLOCK keeps it off any waiting path.
        fd = open_the_fifo(
            self.path("elsewhere"), os.O_RDONLY | os.O_CREAT, 0o644, dir_fd=None
        )
        self.addCleanup(os.close, fd)
        self.assertTrue(stat.S_ISFIFO(os.fstat(fd).st_mode))
        mode = fcntl.fcntl(fd, fcntl.F_GETFL)
        self.assertEqual(os.O_RDWR, mode & os.O_ACCMODE)
        self.assertTrue(mode & os.O_NONBLOCK)

    def test_uses_the_open_captured_at_call_time(self):
        fifo = self.path("pipe")
        make_fifo(self, fifo)
        open_the_fifo = fifo_swap_opener(fifo)
        with mock.patch.object(os, "open", side_effect=AssertionError("not used")):
            fd = open_the_fifo(fifo, os.O_RDONLY)
        self.addCleanup(os.close, fd)
        self.assertTrue(stat.S_ISFIFO(os.fstat(fd).st_mode))


REFUSER_SNIPPET = (
    "import os, stat, sys\n"
    "path = sys.argv[1]\n"
    "if not stat.S_ISREG(os.stat(path).st_mode):\n"
    "    sys.stderr.write(f'cannot read {path}: not a regular file\\n')\n"
    "    sys.exit(2)\n"
)


class TestAssertReadRefusedInChild(TempRootCase):
    """The helper plants the pipe, runs the snippet and pins the refusal."""

    def test_plants_the_fifo_and_pins_the_childs_refusal(self):
        # The refusal snippet reads its path from sys.argv[1], so a wiring
        # bug -- an argument dropped or reordered in the helper's run call --
        # fails here instead of passing while every converted guard breaks.
        fifo = self.path("nested", "pipe")
        assert_read_refused_in_child(
            self, fifo, REFUSER_SNIPPET, str(fifo), cwd=self.root.name
        )
        self.assertTrue(stat.S_ISFIFO(os.stat(fifo).st_mode))

    def test_a_snippet_that_does_not_refuse_fails_the_assertion(self):
        # A reader that exits cleanly without refusing the pipe must not
        # pass: the helper pins the refusal, not just a completed child.
        fifo = self.path("pipe")
        with self.assertRaises(AssertionError):
            assert_read_refused_in_child(
                self, fifo, "import sys; sys.exit(0)", cwd=self.root.name
            )

    def test_skips_when_the_platform_lacks_mkfifo(self):
        # The plant runs before the child: the skip guard fires before any
        # snippet runs, as the converted suites relied on their own guards.
        saved = os.mkfifo
        del os.mkfifo
        try:
            with self.assertRaises(unittest.SkipTest):
                assert_read_refused_in_child(
                    self, self.path("pipe"), REFUSER_SNIPPET,
                    cwd=self.root.name,
                )
        finally:
            os.mkfifo = saved


if __name__ == "__main__":
    unittest.main()

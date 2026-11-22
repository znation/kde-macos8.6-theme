"""Tests for tools/bounded_wait.py: a bounded wait names the wait that expired."""

from __future__ import annotations

import subprocess
import sys
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import bounded_wait  # noqa: E402


def spawn(code: str) -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-c", code])


class TestWaitBounded(unittest.TestCase):
    def test_returns_the_exit_status_of_a_process_that_finishes(self):
        process = spawn("import sys; sys.exit(3)")
        self.addCleanup(process.wait)
        self.assertEqual(bounded_wait.wait_bounded(process, 30, "fast step"), 3)

    def test_expired_wait_raises_naming_the_label_and_budget(self):
        process = spawn("import time; time.sleep(60)")
        # Cleanups run last-in first-out: register wait first so kill runs
        # before it, otherwise wait blocks until the child's 60 s sleep ends.
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        with self.assertRaises(bounded_wait.WaitExpired) as caught:
            bounded_wait.wait_bounded(process, 0.2, "client termination")
        message = str(caught.exception)
        self.assertIn("client termination", message)
        self.assertIn("0.2s", message)
        self.assertIn(str(process.pid), message)

    def test_expired_wait_is_a_timeout_error_and_leaves_the_process_running(self):
        process = spawn("import time; time.sleep(60)")
        # Same ordering as above: kill must run before wait.
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        with self.assertRaises(TimeoutError):
            bounded_wait.wait_bounded(process, 0.2, "splash settle")
        self.assertIsNone(process.poll())


if __name__ == "__main__":
    unittest.main()

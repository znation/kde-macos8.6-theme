"""Direct tests for the shared completed-process assertions.

Every other suite reaches ``support.process_assertions`` through its happy
path only: a child exits the way the caller expected and the helper passes.
These tests exercise each helper's refusal side directly, so a dropped
output attachment or a weakened status pin fails here first rather than as
a milder diagnostic inside the suites that lean on the helpers.

Expected values come from the helpers' own contracts in their docstrings:
exit 0 for success, any non-zero for failure, exit 2 with no escaped
``Traceback`` for a refusal, and the holder message plus the locked path
for a bounded-wait lock refusal.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from support.process_assertions import (
    assert_exit_2_without_traceback,
    assert_failed,
    assert_lock_time_out,
    assert_succeeded,
)

STDOUT_REPORT = "stdout line\n"
STDERR_DIAGNOSTIC = "stderr line\n"
LOCK_PATH = Path("/run/lock/theme-install.lock")
LOCK_MESSAGE = "another holder keeps the lock"
TRACEBACK_LINE = "Traceback (most recent call last):"


def _result(returncode, stdout="", stderr=""):
    """Return a CompletedProcess shaped like the callers' text captures."""
    return subprocess.CompletedProcess(
        args=["tool"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class TestAssertSucceeded(unittest.TestCase):
    def test_passes_on_exit_zero(self):
        assert_succeeded(self, _result(0, STDOUT_REPORT, ""))

    def test_failure_message_carries_both_streams(self):
        with self.assertRaises(AssertionError) as caught:
            assert_succeeded(self, _result(1, STDOUT_REPORT, STDERR_DIAGNOSTIC))

        message = str(caught.exception)
        self.assertIn(STDOUT_REPORT, message)
        self.assertIn(STDERR_DIAGNOSTIC, message)


class TestAssertFailed(unittest.TestCase):
    def test_passes_on_any_non_zero_exit(self):
        assert_failed(self, _result(1, STDOUT_REPORT, STDERR_DIAGNOSTIC))
        assert_failed(self, _result(2, "", STDERR_DIAGNOSTIC))

    def test_failure_on_exit_zero_carries_both_streams(self):
        with self.assertRaises(AssertionError) as caught:
            assert_failed(self, _result(0, STDOUT_REPORT, STDERR_DIAGNOSTIC))

        message = str(caught.exception)
        self.assertIn(STDOUT_REPORT, message)
        self.assertIn(STDERR_DIAGNOSTIC, message)


class TestAssertExit2WithoutTraceback(unittest.TestCase):
    def test_passes_on_exit_two_refusal(self):
        assert_exit_2_without_traceback(
            self, _result(2, "", "refused: bad input\n")
        )

    def test_fails_when_the_exit_is_not_two(self):
        with self.assertRaises(AssertionError):
            assert_exit_2_without_traceback(
                self, _result(1, "", "refused: bad input\n")
            )

    def test_fails_when_a_traceback_escapes(self):
        with self.assertRaises(AssertionError):
            assert_exit_2_without_traceback(
                self, _result(2, "", TRACEBACK_LINE + "\n boom\n")
            )


class TestAssertLockTimeOut(unittest.TestCase):
    def _refusal(self, stderr):
        return _result(2, "", stderr)

    def test_passes_on_holder_refusal_naming_the_path(self):
        assert_lock_time_out(
            self,
            self._refusal(f"{LOCK_MESSAGE}: {LOCK_PATH}\n"),
            LOCK_MESSAGE,
            LOCK_PATH,
        )

    def test_fails_when_stderr_omits_the_locked_path(self):
        with self.assertRaises(AssertionError):
            assert_lock_time_out(
                self,
                self._refusal(LOCK_MESSAGE + "\n"),
                LOCK_MESSAGE,
                LOCK_PATH,
            )

    def test_fails_when_stderr_omits_the_holder_message(self):
        with self.assertRaises(AssertionError):
            assert_lock_time_out(
                self,
                self._refusal(f"other refusal: {LOCK_PATH}\n"),
                LOCK_MESSAGE,
                LOCK_PATH,
            )

    def test_fails_when_the_exit_is_not_two(self):
        with self.assertRaises(AssertionError):
            assert_lock_time_out(
                self,
                _result(1, "", f"{LOCK_MESSAGE}: {LOCK_PATH}\n"),
                LOCK_MESSAGE,
                LOCK_PATH,
            )


if __name__ == "__main__":
    unittest.main()

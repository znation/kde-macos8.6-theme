"""Tests for the shared in-process CLI test helper."""

from __future__ import annotations

import unittest

from support.cli_fixtures import run_main


class TestRunMain(unittest.TestCase):
    def test_non_integer_system_exit_code_becomes_failure_status(self):
        def exit_with_message(_args):
            raise SystemExit("failed")

        result = run_main(exit_with_message, "tool", [])

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()

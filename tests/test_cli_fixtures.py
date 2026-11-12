"""Tests for the shared in-process CLI test helper."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support.cli_fixtures import run_main, run_main_with_env


class TestRunMain(unittest.TestCase):
    def test_non_integer_system_exit_code_becomes_failure_status(self):
        def exit_with_message(_args):
            raise SystemExit("failed")

        result = run_main(exit_with_message, "tool", [])

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


class TestRunMainWithEnv(unittest.TestCase):
    def test_env_replaces_the_environment_for_the_call_only(self):
        seen = {}

        def record_environment(_args):
            seen.update(os.environ)
            return 0

        with mock.patch.dict(os.environ, {"OUTER_ONLY": "1"}, clear=False):
            result = run_main_with_env(
                record_environment, "tool", [], {"ONLY_IN_CALL": "2"}
            )
            restored = dict(os.environ)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(seen, {"ONLY_IN_CALL": "2"})
        self.assertEqual(restored.get("OUTER_ONLY"), "1")
        self.assertNotIn("ONLY_IN_CALL", restored)


if __name__ == "__main__":
    unittest.main()

"""Tests for general render CLI argument validation and workflow delegation."""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.cli_cases import (  # noqa: E402
    assert_usage_error,
    delegated_render_args,
)
from tools import render_surface, render_workflow  # noqa: E402


class TestRenderCliArguments(unittest.TestCase):

    def setUp(self):
        # Pin off host package discovery; these cases cover argument handling.
        patcher = mock.patch.object(
            render_surface, "applet_problem", return_value=None
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_usage_error(self, *argv):
        return assert_usage_error(self, *argv)

    def test_cli_delegates_validated_options_to_render_workflow(self):
        args = delegated_render_args(
            self, ("out.png", "--applet", "test.applet"), 7
        )
        self.assertEqual("test.applet", args.applet)
        self.assertEqual((320, 240), (args.width, args.height))
        self.assertIs(render_workflow.render, render_surface.render)

    def test_cli_delegates_the_settle_and_timeout_to_the_workflow(self):
        # Non-default values must reach the workflow after parsing.
        args = delegated_render_args(
            self, ("out.png", "--settle", "1.25", "--timeout", "33")
        )
        self.assertEqual(1.25, args.settle)
        self.assertEqual(33.0, args.timeout)

    def test_an_applet_render_defaults_to_an_8_second_settle_and_90_second_timeout(self):
        # The --help text documents the plain-render defaults as "default 8"
        # for --settle and "default 90" for --timeout; only the desktop and
        # splash modes override them, so an applet render with no duration
        # flags must keep these values.
        args = delegated_render_args(self, ("out.png",))
        self.assertEqual((8.0, 90.0), (args.settle, args.timeout))

    def test_accepts_the_minimum_settle_and_timeout(self):
        args = delegated_render_args(
            self, ("out.png", "--settle", "0", "--timeout", "1")
        )
        self.assertEqual(0.0, args.settle)
        self.assertEqual(1.0, args.timeout)

    def test_a_single_custom_dimension_keeps_the_other_default(self):
        for option, value, expected in (
            ("--width", "640", (640, 240)),
            ("--height", "480", (320, 480)),
        ):
            with self.subTest(option=option):
                args = delegated_render_args(self, ("out.png", option, value))
                self.assertEqual(expected, (args.width, args.height))

    def test_rejects_non_positive_and_non_plain_sizes(self):
        for option in ("--width", "--height"):
            for value in ("0", "-3", "1_0", "abc", "1.5"):
                with self.subTest(option=option, value=value):
                    self.assertIn(option, self.assert_usage_error("out.png", option, value))

    def test_rejects_bad_durations(self):
        for argv in (
            ("--settle", "-1"),
            ("--settle", "nan"),
            ("--settle", "inf"),
            ("--timeout", "0"),
            ("--timeout", "1_0"),
        ):
            with self.subTest(argv=argv):
                self.assertIn(argv[0], self.assert_usage_error("out.png", *argv))

    def test_rejects_an_infinite_timeout(self):
        # A timeout is a finite upper bound on the render session; accepting
        # infinity would disable the CLI's documented session limit.
        stderr = self.assert_usage_error("out.png", "--timeout", "inf")
        self.assertIn("--timeout", stderr)
        self.assertIn("finite number of seconds", stderr)

    def test_rejects_a_nan_timeout(self):
        # NaN does not compare greater than or equal to the one-second
        # minimum, so it cannot provide the session's required time bound.
        stderr = self.assert_usage_error("out.png", "--timeout", "nan")
        self.assertIn("--timeout", stderr)
        self.assertIn("finite number of seconds", stderr)

    def test_rejects_a_timeout_not_longer_than_settle(self):
        for settle, timeout in (("10", "10"), ("10", "9.5"), ("10", "1")):
            with self.subTest(settle=settle, timeout=timeout):
                stderr = self.assert_usage_error(
                    "out.png", "--settle", settle, "--timeout", timeout
                )
                self.assertIn("--timeout", stderr)
                self.assertIn("--settle", stderr)
                self.assertIn("must be longer than", stderr)

    def test_rejects_option_like_applet(self):
        self.assertIn("--applet", self.assert_usage_error("out.png", "--applet=--help-all"))

    def test_rejects_empty_applet(self):
        self.assertIn("--applet", self.assert_usage_error("out.png", "--applet="))

    def test_rejects_a_path_carrying_applet(self):
        for bad in ("a/b", "a\\b"):
            with self.subTest(bad=bad):
                self.assertIn("--applet", self.assert_usage_error("out.png", "--applet", bad))

    def test_applet_refusals_name_the_actual_defect(self):
        cases = {
            "": "not empty",
            "--help-all": "not option-like",
            "a/b": "not a path",
            "a\\b": "not a path",
            "org.example\0widget": "without NUL",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertIn(expected, self.assert_usage_error("out.png", "--applet=" + value))

    def test_requires_an_output_path(self):
        self.assert_usage_error()


if __name__ == "__main__":
    unittest.main()

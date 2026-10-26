"""Tests for tools/render_surface.py's argument parsing and session script.

The render's end-to-end capture and its failure orchestration live in
``tests/test_render_surface.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: ``main``'s argument validation and ``_session_script``'s in-session
commands.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import call_main  # noqa: E402
from tools import render_surface  # noqa: E402


class TestArguments(unittest.TestCase):
    def assert_usage_error(self, *argv):
        """Assert a usage error (exit 2) and return its stderr."""
        status, stderr = call_main(render_surface.main, *argv)
        self.assertEqual(2, status)
        return stderr

    def test_rejects_non_positive_and_non_plain_sizes(self):
        for option in ("--width", "--height"):
            for value in ("0", "-3", "1_0", "abc", "1.5"):
                with self.subTest(option=option, value=value):
                    self.assertIn(
                        option, self.assert_usage_error("out.png", option, value)
                    )

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

    def test_rejects_a_timeout_not_longer_than_settle(self):
        # The session sleeps for --settle before it asks for the capture, so a
        # timeout at or below it can never capture: refuse rather than wait
        # out the timeout and report "render timed out" without naming the
        # option that cannot work.
        for settle, timeout in (("10", "10"), ("10", "9.5"), ("10", "1")):
            with self.subTest(settle=settle, timeout=timeout):
                stderr = self.assert_usage_error(
                    "out.png", "--settle", settle, "--timeout", timeout
                )
                self.assertIn("--timeout", stderr)
                self.assertIn("--settle", stderr)
                self.assertIn("must be longer than", stderr)

    def test_rejects_option_like_applet(self):
        self.assertIn(
            "--applet", self.assert_usage_error("out.png", "--applet=--help-all")
        )

    def test_rejects_empty_applet(self):
        # ``--applet=`` passes the empty string to the type; the guard rejects
        # it with the same diagnostic as the option-like half, so an empty
        # plasmoid id never reaches the render session.
        self.assertIn("--applet", self.assert_usage_error("out.png", "--applet="))

    def test_requires_an_output_path(self):
        self.assert_usage_error()


class TestSessionScript(unittest.TestCase):
    """The in-session shell script applies the scheme and captures the applet.

    It is the only place the colour scheme is applied inside the throwaway
    session and the only place ``spectacle`` is told what to capture. A
    dropped flag or a wrong positional parameter there renders an unthemed or
    empty surface, which the fidelity gate then reports as a pixel difference
    rather than as the renderer's own bug.
    """

    def test_applies_the_scheme_before_opening_the_applet(self):
        script = render_surface._session_script()
        # The installed scheme id, applied inside the session; `|| exit 1`
        # aborts the session on a failed apply instead of capturing an
        # unthemed window. The applet opens before the settle sleep, so the
        # sleep is the wait for it to paint.
        self.assertIn(
            f"plasma-apply-colorscheme {render_surface.COLOR_SCHEME} || exit 1",
            script,
        )
        self.assertLess(script.index("plasmawindowed"), script.index("sleep"))

    def test_captures_to_the_third_positional_argument_with_spectacle(self):
        # `-b` runs without a GUI, `-n` suppresses the notification, `-f`
        # captures the full screen, and `-o` writes the surface path that
        # `_render` passes as the third positional parameter.
        self.assertIn('spectacle -b -n -f -o "$3"', render_surface._session_script())

    def test_stops_the_applet_and_exits_with_the_capture_status(self):
        script = render_surface._session_script()
        self.assertIn('kill "$applet"', script)
        self.assertIn("exit $status", script)
        # The applet is stopped before the session exits, so no applet
        # outlives the capture.
        self.assertLess(script.index("kill"), script.index("exit $status"))


if __name__ == "__main__":
    unittest.main()

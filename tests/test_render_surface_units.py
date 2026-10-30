"""Tests for the render CLI's arguments and its throwaway session units.

The render's end-to-end capture and its failure orchestration live in
``tests/test_render_surface.py``, and the output publication in
``tests/test_render_output.py``; this module covers the units they are built
from: ``render_surface.main``'s argument validation and the session setup,
environment and in-session commands in ``tools/render_session.py``.
"""

from __future__ import annotations

import os
import stat
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from support.cli_fixtures import call_main  # noqa: E402
from tools import render_session, render_surface  # noqa: E402


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


class TestSessionSetup(unittest.TestCase):
    def test_creates_the_scratch_layout_and_removes_it(self):
        with render_session.Session.create() as session:
            root = session.root
            self.assertTrue(root.name.startswith("render-surface-"))
            for directory in (session.runtime, session.config, session.data):
                with self.subTest(directory=directory.name):
                    self.assertTrue(directory.is_dir())
                    self.assertEqual(root, directory.parent)
            self.assertEqual(0o700, stat.S_IMODE(session.runtime.stat().st_mode))
            self.assertEqual(session.root / "surface.png", session.surface)
            self.assertEqual(session.root / "install.log", session.install_log)
            self.assertEqual(session.root / "render.log", session.render_log)
        self.assertFalse(root.exists())

    def test_environment_points_at_the_scratch_homes(self):
        with render_session.Session.create() as session:
            self.assertEqual(
                str(session.runtime), session.environment["XDG_RUNTIME_DIR"]
            )
            self.assertEqual(
                str(session.config), session.environment["XDG_CONFIG_HOME"]
            )
            self.assertEqual(str(session.data), session.environment["XDG_DATA_HOME"])

    def test_environment_drops_the_callers_session(self):
        ambient = {
            "WAYLAND_DISPLAY": "wl",
            "DISPLAY": ":9",
            "DESTDIR": "/stage",
            "MAKEFLAGS": "-- DESTDIR=/stage",
            "XDG_CONFIG_DIRS": "/ambient",
        }
        with mock.patch.dict(os.environ, ambient):
            with render_session.Session.create() as session:
                environment = session.environment
        for key in ambient:
            with self.subTest(key=key):
                self.assertNotIn(key, environment)

    def test_a_setup_failure_removes_the_partial_scratch_root(self):
        # Session.create promises to remove the scratch root when setup fails.
        # A file where the runtime directory belongs makes the first mkdir
        # fail after mkdtemp has created the root, so the except arm is the
        # only thing that can remove it.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()
        (prepared / "rt").write_bytes(b"in the way")

        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ):
            with self.assertRaises(FileExistsError):
                render_session.Session.create()

        self.assertFalse(prepared.exists())

    def test_a_failure_after_the_layout_is_created_removes_the_scratch_root(self):
        # The runtime directory's mode is the last setup step; if it fails
        # after all three directories exist, the whole root must still go.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()

        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ), mock.patch.object(
            render_session.os, "chmod", side_effect=PermissionError("denied")
        ):
            with self.assertRaises(PermissionError):
                render_session.Session.create()

        self.assertFalse(prepared.exists())


class TestSessionScript(unittest.TestCase):
    """The in-session shell script applies the scheme and captures the applet.

    It is the only place the colour scheme is applied inside the throwaway
    session and the only place ``spectacle`` is told what to capture. A
    dropped flag or a wrong positional parameter there renders an unthemed or
    empty surface, which the fidelity gate then reports as a pixel difference
    rather than as the renderer's own bug.
    """

    def test_applies_the_scheme_before_opening_the_applet(self):
        script = render_session.session_script()
        # The installed scheme id, applied inside the session; `|| exit 1`
        # aborts the session on a failed apply instead of capturing an
        # unthemed window. The applet opens before the settle sleep, so the
        # sleep is the wait for it to paint.
        self.assertIn(
            f"plasma-apply-colorscheme {render_session.COLOR_SCHEME} || exit 1",
            script,
        )
        self.assertLess(script.index("plasmawindowed"), script.index("sleep"))

    def test_captures_to_the_third_positional_argument_with_spectacle(self):
        # `-b` runs without a GUI, `-n` suppresses the notification, `-f`
        # captures the full screen, and `-o` writes the surface path that the
        # session command passes as the third positional parameter.
        self.assertIn(
            'spectacle -b -n -f -o "$3"', render_session.session_script()
        )

    def test_stops_the_applet_and_exits_with_the_capture_status(self):
        script = render_session.session_script()
        self.assertIn('kill "$applet"', script)
        self.assertIn("exit $status", script)
        # The applet is stopped before the session exits, so no applet
        # outlives the capture. Match the applet kill exactly: the earlier
        # liveness check also spells `kill`.
        self.assertLess(
            script.index('kill "$applet"'), script.index("exit $status")
        )


class TestSessionCommand(unittest.TestCase):
    def test_carries_the_geometry_the_script_and_the_surface_path(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, "a b", 2.5, 64, 48, 9.5
            )
            self.assertEqual(session.render_log, command.log)
            self.assertEqual(9.5, command.timeout)
            self.assertEqual(
                [
                    "dbus-run-session",
                    "--",
                    "kwin_wayland",
                    "--virtual",
                    "--no-lockscreen",
                    "--width",
                    "64",
                    "--height",
                    "48",
                    "--socket",
                    render_session.SOCKET,
                    "--exit-with-session",
                ],
                command.argv[:-1],
            )
            self.assertIn(str(session.surface), command.argv[-1])
            self.assertIn(render_session.session_script(), command.argv[-1])
            # The applet is a positional parameter, so its space cannot become
            # shell syntax.
            self.assertIn("'a b' 2.5", command.argv[-1])


class TestSessionThemeSources(unittest.TestCase):
    """``install_theme`` and ``write_session_configs`` source the session.

    The pipeline tests stub ``make`` or observe only ``kwinrc``'s decoration
    block through the session, so a wiring mistake in these two calls -- the
    install staged outside the scratch data home, or ``plasmarc`` or its
    theme-defaults section dropped -- would be invisible to the offline suite
    and surface only in the slow real render. These tests drive the two
    functions directly against a real scratch session.
    """

    def test_install_theme_installs_the_theme_into_the_scratch_data_home(self):
        # Run the real `make install` with the session's environment: it is a
        # fast copy into the scratch data home, so this is the visible result
        # of the wiring (argv, environment, cwd) rather than a re-derivation.
        with render_session.Session.create() as session:
            status, install_log = render_session.install_theme(session)
            self.assertEqual(0, status)
            self.assertTrue(install_log.exists(), "the install log is missing")
            for artifact in (
                "color-schemes/MacOS8.colors",
                "aurorae/themes/org.macos8.desktop",
                "themes/org.macos8.desktop/Kvantum/org.macos8.desktop.kvconfig",
                "plasma/look-and-feel/org.macos8.desktop",
                "fonts/org.macos8.desktop",
                "wallpapers",
            ):
                with self.subTest(artifact=artifact):
                    self.assertTrue(
                        (session.data / artifact).exists(),
                        f"{artifact} did not land in the scratch data home",
                    )

    def test_write_session_configs_writes_both_themed_configs_into_the_config_home(self):
        with render_session.Session.create() as session:
            render_session.write_session_configs(session)
            written = sorted(
                path.name for path in session.config.iterdir() if path.is_file()
            )
            kwinrc = (session.config / "kwinrc").read_text(encoding="utf-8")
            plasmarc = (session.config / "plasmarc").read_text(encoding="utf-8")
        # Exactly the two files the session's in-session commands read; extra
        # files here would also end up in the caller-visible default config.
        self.assertEqual(["kwinrc", "plasmarc"], written)
        self.assertIn("theme=__aurorae__svg__org.macos8.desktop", kwinrc)
        self.assertEqual("[Theme]\nname=org.macos8.desktop\n", plasmarc)


if __name__ == "__main__":
    unittest.main()

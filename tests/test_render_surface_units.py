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
from support.cli_fixtures import assert_missing_tool_named, call_main  # noqa: E402
from tools import apply_theme, render_session, render_surface  # noqa: E402
from tools.render_session import (
    checkbox_dialog_client,
    combobox_dialog_client,
)  # noqa: E402


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

    def test_rejects_an_applet_with_the_checkbox_dialog(self):
        # The dialog render opens its own kdialog client; a plasmoid id
        # combined with it would silently draw nothing.
        self.assertIn(
            "--checkbox-dialog",
            self.assert_usage_error("out.png", "--checkbox-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_checkbox_dialog(self):
        # The gate byte-compares the dialog capture at 480x360; any other
        # size moves the KDialog window the comparison crops assume.
        stderr = self.assert_usage_error(
            "out.png", "--checkbox-dialog", "--width", "320"
        )
        self.assertIn("480x360", stderr)

    def test_rejects_two_dialog_modes(self):
        # Each dialog mode opens its own kdialog client; two flags cannot
        # pick one client, so the CLI refuses the combination by name.
        stderr = self.assert_usage_error(
            "out.png", "--checkbox-dialog", "--combobox-dialog"
        )
        self.assertIn("--checkbox-dialog", stderr)
        self.assertIn("--combobox-dialog", stderr)

    def test_rejects_an_applet_with_the_combobox_dialog(self):
        self.assertIn(
            "--combobox-dialog",
            self.assert_usage_error("out.png", "--combobox-dialog", "--applet", "x"),
        )

    def test_rejects_a_capture_size_with_the_combobox_dialog(self):
        stderr = self.assert_usage_error(
            "out.png", "--combobox-dialog", "--height", "240"
        )
        self.assertIn("480x360", stderr)

    def test_the_combobox_dialog_requires_kdialog(self):
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--combobox-dialog")
        )

    def test_the_checkbox_dialog_requires_kdialog(self):
        # The default applet render cannot need every tool the dialog mode
        # needs, so the dialog requirement is refused per mode: with kdialog
        # absent the CLI names it instead of starting a session.
        tools = render_surface.REQUIRED_TOOLS + ("kdialog",)
        assert_missing_tool_named(
            self, render_surface.main, tools, ("out.png", "--checkbox-dialog")
        )


class TestSessionSetup(unittest.TestCase):
    def test_creates_the_scratch_layout_and_removes_it(self):
        with render_session.Session.create() as session:
            root = session.root
            self.assertTrue(root.name.startswith("render-surface-"))
            for directory in (session.runtime, session.config, session.data, session.home):
                with self.subTest(directory=directory.name):
                    self.assertTrue(directory.is_dir())
            self.assertEqual(0o700, stat.S_IMODE(session.runtime.stat().st_mode))
            self.assertEqual(session.root / "surface.png", session.surface)

    def test_creation_leaves_the_themes_link_to_link_kvantum_themes(self):
        # `link_kvantum_themes` is the one place the scratch home's themes
        # link is made, and only after `make install` has populated the data
        # home's `themes/`: at creation there is nothing to link, so creation
        # leaves no `.local` tree behind either.
        with render_session.Session.create() as session:
            self.assertFalse((session.home / ".local").exists())

    def test_links_the_scratch_homes_themes_for_the_kvantum_lookups(self):
        # Kvantum searches its theme under the literal
        # `$HOME/.local/share/themes/` path, which no `XDG_DATA_HOME` a
        # throwaway install targets satisfies: the session links the two, so
        # a Qt client in the session reads the installed theme directory.
        with render_session.Session.create() as session:
            error, themes = render_session.link_kvantum_themes(session)
            self.assertIsNone(error)
            self.assertTrue(themes.is_symlink())
            self.assertEqual(str(session.data / "themes"), os.readlink(themes))
            # A session is linked once, so a second call is refused with the
            # first link still in place: the CLI reports it to the caller
            # rather than overwrite a working session link.
            second, link = render_session.link_kvantum_themes(session)
            self.assertIsInstance(second, FileExistsError)
            self.assertTrue(link.is_symlink())

    def test_the_settings_and_scripts_paths_are_reported(self):
        with render_session.Session.create() as session:
            self.assertEqual(session.root / "install.log", session.install_log)
            self.assertEqual(session.root / "render.log", session.render_log)

    def test_environment_points_at_the_scratch_homes(self):
        with render_session.Session.create() as session:
            self.assertEqual(
                str(session.home), session.environment["HOME"]
            )
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

    def test_applies_the_scheme_before_opening_the_client(self):
        script = render_session.session_script()
        # The installed scheme id, applied inside the session; `|| exit 1`
        # aborts the session on a failed apply instead of capturing an
        # unthemed window. The client opens before the settle sleep, so the
        # sleep is the wait for it to paint.
        self.assertIn(
            f"plasma-apply-colorscheme {render_session.COLOR_SCHEME} || exit 1",
            script,
        )
        self.assertLess(script.index('"$@"'), script.index("sleep"))

    def test_captures_to_the_capture_positional_with_spectacle(self):
        # `-b` runs without a GUI, `-n` suppresses the notification, `-f`
        # captures the full screen, and `-o` writes the surface path that the
        # session command passes as the second positional parameter.
        self.assertIn(
            'spectacle -b -n -f -o "$capture"', render_session.session_script()
        )

    def test_stops_the_client_and_exits_with_the_capture_status(self):
        script = render_session.session_script()
        self.assertIn('kill "$client"', script)
        self.assertIn("exit $status", script)
        # The client is stopped before the session exits, so no client
        # outlives the capture. Match the client kill exactly: the earlier
        # liveness check also spells `kill`.
        self.assertLess(
            script.index('kill "$client"'), script.index("exit $status")
        )


class TestSessionCommand(unittest.TestCase):
    def test_carries_the_geometry_the_script_and_the_surface_path(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, ["plasmawindowed", "a b"], 2.5, 64, 48, 9.5
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
            # The client words are positional parameters of the in-session
            # `sh -c`, so their space cannot become shell syntax.
            self.assertIn("'a b'", command.argv[-1])

    def test_carries_the_checkbox_dialog_client_words(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session,
                list(checkbox_dialog_client(session)),
                2.5,
                480,
                360,
                9.5,
            )
            self.assertIn("kdialog", command.argv[-1])
            # The dontagain config file lands in the scratch config home, so
            # the client never writes the caller's configuration.
            self.assertIn(
                f"{session.config / 'kde-dontagain'}:widgets", command.argv[-1]
            )

    def test_carries_the_combobox_dialog_client_words(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session,
                list(combobox_dialog_client(session)),
                2.5,
                480,
                360,
                9.5,
            )
            self.assertIn("kdialog", command.argv[-1])
            # The chooser's items travel as separate positional words of the
            # in-session script, so a space inside one cannot become shell
            # syntax.
            self.assertIn("'Macintosh HD'", command.argv[-1])


class TestSessionThemeSources(unittest.TestCase):
    """``install_theme``, ``write_session_configs`` and the Kvantum selection
    source the session.

    The pipeline tests stub ``make`` or observe only ``kwinrc``'s decoration
    block through the session, so a wiring mistake in these three calls -- the
    install staged outside the scratch data home, ``plasmarc`` or its
    theme-defaults section dropped, or a Kvantum selection with the wrong
    theme id -- would be invisible to the offline suite and surface only in
    the slow real render. These tests drive the functions directly against a
    real scratch session.
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

    def test_write_kvantum_selection_names_the_theme_for_qt_clients(self):
        # kdialog and other Qt clients style through the engine, which reads
        # the selected theme name from this file; without it the scratch
        # render shows the engine's compiled-in default theme, and the
        # pipeline tests (which read only kwinrc) would stay green.
        with render_session.Session.create() as session:
            render_session.write_kvantum_selection(session)
            selection = (
                session.config / "Kvantum" / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_write_kvantum_selection_overwrites_a_stale_selection(self):
        # The scratch config home starts empty, but the function still has to
        # cope with an existing Kvantum directory and file in one call, so a
        # stale selection cannot survive a rewritten session.
        with render_session.Session.create() as session:
            directory = session.config / "Kvantum"
            directory.mkdir()
            (directory / "kvantum.kvconfig").write_text(
                "[General]\ntheme=Another\n", encoding="utf-8"
            )
            render_session.write_kvantum_selection(session)
            selection = (
                directory / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_the_session_selection_names_the_theme_id_the_cli_pins(self):
        # The session's Kvantum selection and `make apply`'s best-effort
        # selection are two modules each holding the theme id: a drift
        # between them would leave `make render` on the engine's compiled-in
        # default while `make apply` selects the real theme, with the
        # scratch session's reference gates comparing against the wrong
        # engine output. The id must also be the shipped package directory
        # `make install` copies, which tests/test_apply_theme.py pins from
        # the apply side.
        self.assertEqual(
            render_session.KVANTUM_THEME, apply_theme.KVANTUM_THEME
        )
        self.assertTrue(
            (apply_theme.ROOT / "theme" / "kvantum" / render_session.KVANTUM_THEME)
            .is_dir(),
            "the session's Kvantum id is not the shipped package directory",
        )


if __name__ == "__main__":
    unittest.main()

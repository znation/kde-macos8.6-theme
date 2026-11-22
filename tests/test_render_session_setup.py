"""Tests for the scratch-session setup checks in the render tools.

Moved out of ``tests/test_render_surface_units.py``: the layout, environment
and cleanup that ``tools/render/session.py``'s ``Session.create`` makes, and
the Kvantum themes link that ``tools/render/setup.py`` makes. The session
command and dialog argv checks live in ``tests/test_render_session_command.py``.
"""

from __future__ import annotations

import os
import stat
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import tmp_dir
from tools.render import session as render_session, setup as render_setup  # noqa: E402


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
            error, themes = render_setup.link_kvantum_themes(session)
            self.assertIsNone(error)
            self.assertTrue(themes.is_symlink())
            self.assertEqual(str(session.data / "themes"), os.readlink(themes))
            # A session is linked once, so a second call is refused with the
            # first link still in place: the CLI reports it to the caller
            # rather than overwrite a working session link.
            second, link = render_setup.link_kvantum_themes(session)
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

    def test_environment_disables_kwin_screenshot_authorization(self):
        # The nested compositor cannot map its clients to a desktop-file
        # identity, and KWin 6.6 rejects an unauthorized ScreenShot2 call
        # before Spectacle can write the capture. The switch must reach KWin
        # through the session environment, so the capture still works there.
        with render_session.Session.create() as session:
            self.assertEqual(
                "1",
                session.environment["KWIN_SCREENSHOT_NO_PERMISSION_CHECKS"],
            )

    def test_environment_forces_spectacles_null_video_platform(self):
        # Spectacle would otherwise build its Wayland video platform even for
        # a still capture and wait on a nonexistent PipeWire/screencast
        # service before the capture starts.
        with render_session.Session.create() as session:
            self.assertEqual(
                "VideoPlatformNull",
                session.environment["SPECTACLE_VIDEO_PLATFORM"],
            )

    def test_environment_forces_dbus_services_to_use_offscreen_qt(self):
        # D-Bus-activated Qt services inherit this environment before the
        # nested Wayland socket is ready, so they must not try that display.
        with mock.patch.dict(os.environ, {"QT_QPA_PLATFORM": "wayland"}):
            with render_session.Session.create() as session:
                self.assertEqual("offscreen", session.environment["QT_QPA_PLATFORM"])

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
        # The host display is replaced, not inherited: the nested session
        # must point at its own compositor socket.
        self.assertEqual(render_session.SOCKET, environment["WAYLAND_DISPLAY"])
        self.assertNotEqual("wl", environment["WAYLAND_DISPLAY"])
        for key in ambient:
            if key == "WAYLAND_DISPLAY":
                continue
            with self.subTest(key=key):
                self.assertNotIn(key, environment)

    def test_environment_pins_the_measurement_locale(self):
        ambient = {
            "LANG": "de_DE.UTF-8",
            "LANGUAGE": "de",
            "LC_ALL": "C",
            "LC_TIME": "de_DE.UTF-8",
        }
        with mock.patch.dict(os.environ, ambient):
            with render_session.Session.create() as session:
                environment = session.environment
        # The caller's locale is not session state: kdialog starts the
        # calendar's day grid on the locale's first day of week (Monday
        # first in the C locale an unset LANG gives), so a leaked caller
        # locale moves every calendar pin one column left. The session
        # pins the locale the capture pins were measured under instead,
        # and drops the message-language override with it.
        self.assertEqual(render_session.MEASUREMENT_LOCALE, environment["LANG"])
        self.assertEqual(render_session.MEASUREMENT_LOCALE, environment["LC_ALL"])
        self.assertNotIn("LANGUAGE", environment)

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

    def test_an_interruption_after_the_layout_is_created_removes_the_scratch_root(self):
        # Session.create catches BaseException so an interrupted setup cannot
        # leave its private root behind. Exercise that broader cleanup arm
        # with a catchable process interruption after the directories exist.
        prepared = tmp_dir.make_tmp_dir(self) / "render-surface-fixed"
        prepared.mkdir()

        with mock.patch.object(
            render_session.tempfile, "mkdtemp", return_value=str(prepared)
        ), mock.patch.object(
            render_session.os, "chmod", side_effect=KeyboardInterrupt
        ):
            with self.assertRaises(KeyboardInterrupt):
                render_session.Session.create()

        self.assertFalse(prepared.exists())


if __name__ == "__main__":
    unittest.main()

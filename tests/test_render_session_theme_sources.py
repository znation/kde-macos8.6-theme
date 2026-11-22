"""Tests for the session theme-source writes in the render tools.

Moved out of ``tests/test_render_surface_units.py``: ``tools/render/setup.py``'s
``install_theme``, ``write_session_configs``, ``write_kvantum_selection``,
``write_desktop_selection`` and ``install_gtk_selection`` calls against a real
scratch session. The class starts no session or display, so it has no skip guard.
"""

import contextlib
import io
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import apply_theme, apply_optional  # noqa: E402
from tools.render import session as render_session, setup as render_setup  # noqa: E402
from tools.gtk.selection import ConfigError as _ConfigError  # noqa: E402
from tools.gtk.selection import installed_sheet  # noqa: E402
from tools.gtk.user_files import GTK4_CSS_MARKER  # noqa: E402


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
            status, install_log = render_setup.install_theme(session)
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
            render_setup.write_session_configs(session)
            written = sorted(
                path.name for path in session.config.iterdir() if path.is_file()
            )
            kwinrc = (session.config / "kwinrc").read_text(encoding="utf-8")
            plasmarc = (session.config / "plasmarc").read_text(encoding="utf-8")
        # Exactly the two files the session's in-session commands read; extra
        # files here would also end up in the caller-visible default config.
        self.assertEqual(["kwinrc", "plasmarc"], written)
        self.assertIn("theme=org.macos8.desktop", kwinrc)
        self.assertEqual("[Theme]\nname=org.macos8.desktop\n", plasmarc)

    def test_write_kvantum_selection_names_the_theme_for_qt_clients(self):
        # kdialog and other Qt clients style through the engine, which reads
        # the selected theme name from this file; without it the scratch
        # render shows the engine's compiled-in default theme, and the
        # pipeline tests (which read only kwinrc) would stay green.
        with render_session.Session.create() as session:
            render_setup.write_kvantum_selection(session)
            selection = (
                session.config / "Kvantum" / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_write_desktop_selection_names_the_look_and_feel(self):
        # plasmashell only builds the themed menu bar when the scratch
        # session selects the look-and-feel, so both keys the published
        # apply records must stand in the scratch config home.
        with render_session.Session.create() as session:
            render_setup.write_desktop_selection(session)
            for name in ("plasmarc", "kdeglobals"):
                text = (session.config / name).read_text(encoding="utf-8")
                with self.subTest(file=name):
                    self.assertEqual(
                        "[KDE]\nLookAndFeelPackage=org.macos8.desktop\n", text
                    )

    def test_write_desktop_selection_appends_beside_the_defaults(self):
        # The defaults writer has already published plasmarc's [Theme] name
        # when the desktop selection runs, so the selection is appended, not
        # written over it: replacing the file would drop the desktop theme
        # name the shell reads.
        with render_session.Session.create() as session:
            (session.config / "plasmarc").write_text(
                "[Theme]\nname=org.macos8.desktop\n", encoding="utf-8"
            )
            render_setup.write_desktop_selection(session)
            self.assertEqual(
                "[Theme]\nname=org.macos8.desktop\n"
                "[KDE]\nLookAndFeelPackage=org.macos8.desktop\n",
                (session.config / "plasmarc").read_text(encoding="utf-8"),
            )

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
            render_setup.write_kvantum_selection(session)
            selection = (
                directory / "kvantum.kvconfig"
            ).read_text(encoding="utf-8")
        self.assertEqual("[General]\ntheme=org.macos8.desktop\n", selection)

    def test_write_kvantum_selection_keeps_previous_file_when_publication_fails(self):
        with render_session.Session.create() as session:
            directory = session.config / "Kvantum"
            directory.mkdir()
            target = directory / "kvantum.kvconfig"
            target.write_text("previous selection\n", encoding="utf-8")
            def fail_publication(source, destination):
                self.assertEqual(target, destination)
                self.assertEqual(
                    b"[General]\ntheme=org.macos8.desktop\n", source.read_bytes()
                )
                self.assertEqual("previous selection\n", target.read_text(encoding="utf-8"))
                raise OSError("disk full")

            with mock.patch("tools.atomic_write.os.replace", side_effect=fail_publication):
                with self.assertRaisesRegex(OSError, "disk full"):
                    render_setup.write_kvantum_selection(session)
            self.assertEqual("previous selection\n", target.read_text(encoding="utf-8"))
            self.assertEqual([target], list(directory.iterdir()))

    @staticmethod
    def stage_installed_sheets(session, versions):
        """Stage the installed GTK *versions*' sheets in *session*'s data home."""
        for version in versions:
            sheet = installed_sheet(session.data, version)
            sheet.parent.mkdir(parents=True, exist_ok=True)
            sheet.write_text("", encoding="utf-8")

    def test_install_gtk_selection_publishes_both_settings_and_the_user_css(
        self,
    ):
        # The lone --gtk-dialog pipeline test stubs this function, so without
        # a direct drive a swapped sheet path, a dropped settings version or
        # a Kvantum-facing theme id in the published CSS would reach the
        # scratch session unobserved and fail only in the slow real render.
        with render_session.Session.create() as session:
            self.stage_installed_sheets(session, ("gtk-4.0", "gtk-3.0"))

            render_setup.install_gtk_selection(session)

            for version in ("gtk-4.0", "gtk-3.0"):
                with self.subTest(version=version):
                    settings = (
                        session.config / version / "settings.ini"
                    ).read_text(encoding="utf-8")
                    self.assertIn("gtk-theme-name=org.macos8.desktop", settings)
            css = (session.config / "gtk-4.0" / "gtk.css").read_text(
                encoding="utf-8"
            )
            expected_sheet = installed_sheet(session.data, "gtk-4.0")
            self.assertEqual(
                f'{GTK4_CSS_MARKER}\n@import url("{expected_sheet.as_uri()}");\n',
                css,
                "the user CSS must be marker-led and import the gtk-4.0 sheet",
            )

    def test_install_gtk_selection_raises_naming_a_missing_sheet(self):
        # `installed_sheets` reports the first missing sheet and returns None,
        # which this function must turn into the `--gtk-dialog` workflow's
        # ConfigError so `main` reports the failure and removes the scratch
        # session instead of starting an unthemed zenity client.
        with render_session.Session.create() as session:
            # Only gtk-3.0 is present, so the report must name gtk-4.0,
            # the version `installed_sheets` checks first.
            self.stage_installed_sheets(session, ("gtk-3.0",))
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                with self.assertRaises(_ConfigError) as caught:
                    render_setup.install_gtk_selection(session)
            self.assertIn(
                "installed gtk-4.0 sheet is missing", stderr.getvalue()
            )
            self.assertEqual(
                "the scratch install left a GTK sheet missing; the zenity "
                "client would start unthemed",
                str(caught.exception),
            )

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
            render_setup.KVANTUM_THEME, apply_optional.KVANTUM_THEME
        )
        self.assertTrue(
            (apply_theme.ROOT / "theme" / "kvantum" / render_setup.KVANTUM_THEME)
            .is_dir(),
            "the session's Kvantum id is not the shipped package directory",
        )


if __name__ == "__main__":
    unittest.main()

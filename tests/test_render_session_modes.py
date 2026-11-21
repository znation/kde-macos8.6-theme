"""The render CLI's per-mode session wiring, against shell stubs of the external tools.

Each render mode's session is pinned against the same stub executables as the
failure paths in ``tests/test_render_failure_paths.py``: the client each mode
launches (the kdialog menu, the two-window inactive wrapper, plasmashell,
ksplashqml), which modes write ``kdeglobals``, the window rules and the GTK
selection. The failure paths stay in ``tests/test_render_failure_paths.py``.
"""

from __future__ import annotations

import shlex
import unittest
from unittest import mock

from support.render_stub_tools import StubTools
from tools import (
    render_setup,
    render_window_rules,
    render_workflow,
)


class TestSessionModes(StubTools, unittest.TestCase):
    def test_menu_dialog_launches_its_kdialog_menu_client(self):
        # The menu mode must reach the session as a KDialog menu client (and
        # therefore apply the dialog's Kvantum configuration path), not fall
        # through to the default Plasma calculator applet.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection:
            status, stderr, output = self.run_main("--menu-dialog")

        # The menu mode takes the dialog path: the dialog's config files (the
        # global theme's kdeglobals) and the Kvantum selection, not the
        # applet render's session-only set. The rendered siblings pin this
        # path too, but only for the checkbox and combobox modes.
        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("kdialog", argv[-1])
        self.assertIn("--menu", argv[-1])
        self.assertIn("Alpha", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_inactive_dialog_launches_its_two_window_wrapper(self):
        # The inactive mode must reach the session as the two-window sh -c
        # wrapper (one kdialog per fixed title, opened inactive-window
        # first), not fall through to the default Plasma calculator applet.
        # Its session also writes the forced-geometry rules the two titles
        # are matched by, beside the dialog's Kvantum selection.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as selection, \
                mock.patch.object(render_workflow, "write_window_rules") as rules:
            status, stderr, output = self.run_main("--inactive-dialog")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        rules.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn('readiness=""', shlex.split(argv[-1])[2])
        self.assertIn("kdialog", argv[-1])
        self.assertIn(render_window_rules.INACTIVE_TITLE, argv[-1])
        self.assertIn(render_window_rules.FOCUSED_TITLE, argv[-1])
        # The mode's session also carries its focus-settle KWin script (the
        # newest-window activation is a race under the parallel check's
        # load), loaded by the scratch path the workflow wrote it to.
        self.assertIn("org.kde.kwin.Scripting.loadScript", argv[-1])
        self.assertIn(render_window_rules.FOCUS_SETTLE_SCRIPT, argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_desktop_render_launches_the_plasmashell_client(self):
        # The desktop mode must reach the session as plasmashell (the shell
        # draws the menu bar itself), with the look-and-feel selection
        # written beside the session configs, not fall through to the
        # default Plasma calculator applet or a dialog client.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as selection:
            status, stderr, output = self.run_main("--desktop")

        self.assertEqual(
            render_setup.CONFIG_FILES + ("kdeglobals",),
            configs.call_args.kwargs["files"],
        )
        selection.assert_called_once_with(configs.call_args.args[0])
        argv = run.call_args.args[0]
        self.assertIn("plasmashell", argv[-1])
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_splash_render_launches_the_ksplashqml_client(self):
        # The splash mode must reach the session as ksplashqml pointing at
        # the session-local installed look-and-feel package (the splash
        # paints its own Splash.qml from the scratch data home, never the
        # caller's), writing only the applet's session configs: the splash
        # reads no selection, so no look-and-feel, Kvantum, GTK or window
        # rules write may ride the session.
        with mock.patch.object(render_workflow, "run_logged", return_value=1) as run, \
                mock.patch.object(render_workflow, "write_session_configs") as configs, \
                mock.patch.object(render_workflow, "write_desktop_selection") as look, \
                mock.patch.object(render_workflow, "write_kvantum_selection") as kvantum, \
                mock.patch.object(render_workflow, "write_window_rules") as rules, \
                mock.patch.object(render_workflow, "install_gtk_selection") as gtk:
            status, stderr, output = self.run_main("--splash")

        self.assertEqual(render_setup.CONFIG_FILES, configs.call_args.kwargs["files"])
        look.assert_not_called()
        kvantum.assert_not_called()
        rules.assert_not_called()
        gtk.assert_not_called()
        argv = run.call_args.args[0]
        self.assertIn('readiness=""', shlex.split(argv[-1])[2])
        self.assertIn("ksplashqml", argv[-1])
        self.assertIn("--nofork", argv[-1])
        self.assertIn(
            "plasma/look-and-feel/org.macos8.desktop", argv[-1]
        )
        self.assertNotIn("org.kde.plasma.calculator", argv[-1])
        self.assertNotIn("plasmawindowed", argv[-1])
        self.assertNotIn("kdialog", argv[-1])
        self.assert_failed_run(
            status, stderr, output, 1, "render session exited 1",
        )

    def test_only_the_inactive_dialog_writes_the_window_rules(self):
        # The two-window forced-geometry rules are the inactive mode's own
        # session config: no applet render and no one-window dialog render
        # may write a kwinrulesrc the other sessions never asked for.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_window_rules"
        ) as rules, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            for extra in ((), ("--checkbox-dialog",)):
                with self.subTest(extra=extra):
                    status, _, _ = self.run_main(*extra)
                    self.assertEqual(1, status)
                    rules.assert_not_called()
            status, _, _ = self.run_main("--inactive-dialog")
            self.assertEqual(1, status)

        rules.assert_called_once()
        self.assert_scratch_removed()

    def test_only_dialog_renders_add_kdeglobals_to_the_session_configs(self):
        # Dialog clients are Qt applications, so the scratch session must
        # apply the global theme defaults that select Kvantum. The applet
        # render deliberately writes only the window-decoration configs.
        self.stub("kdialog", "exit 0")
        with mock.patch.object(
            render_workflow, "write_session_configs"
        ) as write_configs, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, _, _ = self.run_main()
            self.assertEqual(1, status)
            applet_files = write_configs.call_args.kwargs["files"]

            status, _, _ = self.run_main("--checkbox-dialog")
            self.assertEqual(1, status)
            dialog_files = write_configs.call_args.kwargs["files"]

        self.assertEqual(("kwinrc", "plasmarc"), applet_files)
        self.assertEqual(
            ("kwinrc", "plasmarc", "kdeglobals"), dialog_files
        )
        self.assert_scratch_removed()

    def test_gtk_dialog_installs_the_gtk_selection_beside_the_kvatum_one(self):
        # The GTK mode's zenity client wears the theme through the selection
        # the workflow publishes into the scratch config home, so the GTK
        # selection install must run beside the Kvantum one, not be
        # forgotten the way a fourth copy of the fan-out could omit it.
        self.stub("zenity", "exit 0")
        with mock.patch.object(
            render_workflow, "install_gtk_selection"
        ) as install, mock.patch.object(
            render_workflow, "write_kvantum_selection"
        ) as kvantum, mock.patch.object(
            render_workflow, "run_logged", return_value=1
        ):
            status, stderr, output = self.run_main("--gtk-dialog")

        self.assert_failed_run(status, stderr, output, 1)
        install.assert_called_once()
        kvantum.assert_called_once()


if __name__ == "__main__":
    unittest.main()

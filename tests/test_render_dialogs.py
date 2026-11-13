"""Tests for the shared dialog-mode table in tools/render_dialogs.py.

``DIALOG_MODES`` is the single declaration of the render CLI's fourteen dialog
modes: the parser builds one ``--*-dialog`` flag per entry from it, the CLI's
mutual-exclusion refusal and required-tool list read it, and the workflow maps
the chosen flag to its client and its theme-selection fan-out from it. A wrong
entry here would put a stale flag, client or tool into one of those surfaces,
so the table is pinned whole.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import render_clients, render_dialogs  # noqa: E402
from tools.render_clients import inactive_dialog_client


class TestDialogModes(unittest.TestCase):
    """The table names every mode the CLI and workflow already ship."""

    def test_lists_every_dialog_flag_in_the_cli_listing_order(self):
        # The parser adds one flag per entry in table order, so this order is
        # the CLI's --help order and the mutual-exclusion refusal's listing
        # order; a reordered table would silently change both surfaces.
        self.assertEqual(
            (
                "--checkbox-dialog",
                "--combobox-dialog",
                "--lineedit-dialog",
                "--menu-dialog",
                "--radiolist-dialog",
                "--calendar-dialog",
                "--color-dialog",
                "--progressbar-dialog",
                "--slider-dialog",
                "--textbox-dialog",
                "--gtk-dialog",
                "--icon-dialog",
                "--inactive-dialog",
                "--file-dialog",
            ),
            tuple(mode.flag for mode in render_dialogs.DIALOG_MODES),
        )

    def test_derives_each_namespace_attribute_from_its_flag(self):
        # The parsed attribute is the flag name in identifier form, so the
        # workflow's getattr(args, mode.attr) reads the flag the parser set.
        for mode in render_dialogs.DIALOG_MODES:
            with self.subTest(flag=mode.flag):
                self.assertEqual("--" + mode.attr.replace("_dialog", "-dialog"), mode.flag)
                self.assertTrue(mode.help)

    def test_every_one_window_mode_ends_its_help_with_the_shared_capture_tail(self):
        # Every mode except the inactive pair capture tails its help text with
        # the module's shared capture tail, so the capture size is declared in
        # one place beside the gate it feeds; a mode that re-spelled the tail
        # would advertise another size the widget gate does not byte-compare.
        tail = "and capture it at the 480x360 size the widget gate byte-compares"
        for mode in render_dialogs.DIALOG_MODES:
            if mode.attr == "inactive_dialog":
                continue
            with self.subTest(flag=mode.flag):
                self.assertTrue(mode.help.endswith(tail), mode.help)

    def test_pairs_each_mode_with_its_render_clients_factory(self):
        # The workflow builds the mode's window through mode.client, so a
        # swapped factory would open one dialog while its flag's help text
        # describes another.
        self.assertEqual(
            (
                render_clients.checkbox_dialog_client,
                render_clients.combobox_dialog_client,
                render_clients.lineedit_dialog_client,
                render_clients.menu_dialog_client,
                render_clients.radio_dialog_client,
                render_clients.calendar_dialog_client,
                render_clients.color_dialog_client,
                render_clients.progressbar_dialog_client,
                render_clients.slider_dialog_client,
                render_clients.textbox_dialog_client,
                render_clients.gtk_dialog_client,
                render_clients.icon_dialog_client,
                inactive_dialog_client,
                render_clients.file_dialog_client,
            ),
            tuple(mode.client for mode in render_dialogs.DIALOG_MODES),
        )

    def test_runs_every_client_on_kdialog_except_the_zenity_gtk_mode(self):
        # The CLI requires each mode's client tool on PATH, and the workflow
        # installs the GTK selection beside the Kvantum one for the zenity
        # modes, so a swapped tool column would demand kdialog for --gtk-dialog.
        self.assertEqual(
            ("kdialog",) * 10 + ("zenity", "kdialog", "kdialog", "kdialog"),
            tuple(mode.client_tool for mode in render_dialogs.DIALOG_MODES),
        )
        gtk_modes = [
            mode for mode in render_dialogs.DIALOG_MODES
            if mode.client_tool == "zenity"
        ]
        self.assertEqual(("gtk_dialog",), tuple(m.attr for m in gtk_modes))

    def test_only_inactive_dialog_requests_the_window_rules_config(self):
        # The workflow writes the forced-geometry rules file only when a
        # selected mode declares it; the inactive capture needs those rules
        # to keep both windows in frame. A missing or misplaced declaration
        # would make the inactive render use incidental window placement.
        self.assertEqual(
            {
                "inactive_dialog": ("kwinrulesrc",),
            },
            {
                mode.attr: mode.extra_config_files
                for mode in render_dialogs.DIALOG_MODES
                if mode.extra_config_files
            },
        )


if __name__ == "__main__":
    unittest.main()

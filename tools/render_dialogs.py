"""The dialog render modes the render CLI and workflow share.

``tools/render_surface.py`` defines one ``--*-dialog`` flag per mode and
refuses more than one at a time; ``tools/render_workflow.py`` maps the chosen
flag to the dialog client it opens and installs the matching theme
selections. Both read this module's ``DIALOG_MODES`` table so a mode is
declared once: its namespace attribute, CLI flag, help text, client factory
and the external tool the client needs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NamedTuple

try:
    from tools.render_clients import (
        calendar_dialog_client,
        checkbox_dialog_client,
        color_dialog_client,
        combobox_dialog_client,
        file_dialog_client,
        gtk_dialog_client,
        icon_dialog_client,
        inactive_dialog_client,
        lineedit_dialog_client,
        menu_dialog_client,
        progressbar_dialog_client,
        radio_dialog_client,
        slider_dialog_client,
        textbox_dialog_client,
    )
except ImportError:  # imported from a directly run tool
    from render_clients import (
        calendar_dialog_client,
        checkbox_dialog_client,
        color_dialog_client,
        combobox_dialog_client,
        file_dialog_client,
        gtk_dialog_client,
        icon_dialog_client,
        inactive_dialog_client,
        lineedit_dialog_client,
        menu_dialog_client,
        progressbar_dialog_client,
        radio_dialog_client,
        slider_dialog_client,
        textbox_dialog_client,
    )

if TYPE_CHECKING:
    from tools.render_session import Session


class DialogMode(NamedTuple):
    """One dialog render mode the CLI parser and the workflow share.

    ``attr`` is the parsed-arguments attribute the flag sets, ``client`` the
    render client factory the workflow builds the mode's window with, and
    ``client_tool`` the external tool that client runs (the CLI requires it
    on PATH, and the workflow installs the GTK selection for it).
    ``extra_config_files`` names further config files the workflow writes
    into the scratch config home beside the dialog defaults (empty for
    every one-window mode).
    """

    attr: str
    flag: str
    help: str
    client: Callable[[Session], tuple[str, ...]]
    client_tool: str
    extra_config_files: tuple[str, ...] = ()


# The help-text tail every one-window dialog mode shares: the mode opens one
# dialog and the CLI captures it at 480x360, the size the widget gate
# byte-compares. Declared once so the capture size is edited in one place;
# the inactive pair capture tails differently and keeps its own wording.
_CAPTURE_TAIL = "and capture it at the 480x360 size the widget gate byte-compares"


# One entry per dialog mode, in the order the CLI lists the flags: the parser
# adds one ``--*-dialog`` flag per entry in this order, and the workflow walks
# it to pick the client for the flag set on the command line. The CLI accepts
# at most one flag, so no other ordering is observable.
DIALOG_MODES = (
    DialogMode(
        "checkbox_dialog",
        "--checkbox-dialog",
        (
            f"open a KDialog warning box whose dontagain check box the Kvantum "
            f"engine draws with the theme's checkbox art, {_CAPTURE_TAIL}"
        ),
        checkbox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "combobox_dialog",
        "--combobox-dialog",
        (
            f"open a KDialog chooser whose combo box the Kvantum engine draws "
            f"with the theme's comboarrow art, {_CAPTURE_TAIL}"
        ),
        combobox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "lineedit_dialog",
        "--lineedit-dialog",
        (
            f"open a KDialog input box whose line edit the Kvantum engine "
            f"draws with the theme's sunken-field art, {_CAPTURE_TAIL}"
        ),
        lineedit_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "menu_dialog",
        "--menu-dialog",
        (
            f"open a KDialog menu list whose item-view frame the Kvantum "
            f"engine draws with the theme's GenericFrame art, {_CAPTURE_TAIL}"
        ),
        menu_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "radiolist_dialog",
        "--radiolist-dialog",
        (
            f"open a KDialog radio list whose sunken list field, selected- "
            f"row selection band and checked and unchecked radio indicators "
            f"the Kvantum engine draws with the theme's palette and radio "
            f"art, {_CAPTURE_TAIL}"
        ),
        radio_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "calendar_dialog",
        "--calendar-dialog",
        (
            f"open a KDialog calendar whose day table the Kvantum engine "
            f"paints with the theme's colorscheme palette, {_CAPTURE_TAIL}"
        ),
        calendar_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "color_dialog",
        "--color-dialog",
        (
            f"open a KDialog color picker whose swatch grid, line edits and "
            f"push buttons the Kvantum engine draws with the theme's palette "
            f"and art, {_CAPTURE_TAIL}"
        ),
        color_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "progressbar_dialog",
        "--progressbar-dialog",
        (
            f"open a KDialog progress meter whose at-rest trough the Kvantum "
            f"engine draws with the theme's progress art, {_CAPTURE_TAIL}"
        ),
        progressbar_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "slider_dialog",
        "--slider-dialog",
        (
            f"open a KDialog slider whose QSlider the Kvantum engine draws "
            f"with the theme's slider and slidercursor art, {_CAPTURE_TAIL}"
        ),
        slider_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "textbox_dialog",
        "--textbox-dialog",
        (
            f"open a KDialog text box whose vertical scrollbar the Kvantum "
            f"engine draws with the theme's scrollbar art, {_CAPTURE_TAIL}"
        ),
        textbox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "gtk_dialog",
        "--gtk-dialog",
        (
            f"open a zenity text-entry dialog whose content-area GtkEntry the "
            f"GTK 4 toolkit draws with the published theme selection, "
            f"{_CAPTURE_TAIL}"
        ),
        gtk_dialog_client,
        "zenity",
    ),
    DialogMode(
        "icon_dialog",
        "--icon-dialog",
        (
            f"open a KDialog icon chooser whose sunken icon-list field, search "
            f"field and push buttons the Kvantum engine draws with the theme's "
            f"palette and art, {_CAPTURE_TAIL}"
        ),
        icon_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "inactive_dialog",
        "--inactive-dialog",
        (
            "open two KDialog message boxes with two distinct fixed titles "
            "and capture the 480x360 pair at the size the inactive-window "
            "gate byte-compares: KWin activates the newest, so the earlier "
            "window stands beside it drawn in the frame's inactive state, "
            "placed by the forced-geometry window rules the session reads"
        ),
        inactive_dialog_client,
        "kdialog",
        ("kwinrulesrc",),
    ),
    DialogMode(
        "file_dialog",
        "--file-dialog",
        (
            f"open a KDialog file chooser whose places sidebar, file list "
            f"view, toolbar and name-filter surfaces the Kvantum engine draws "
            f"with the theme's palette and art, {_CAPTURE_TAIL}"
        ),
        file_dialog_client,
        "kdialog",
    ),
)

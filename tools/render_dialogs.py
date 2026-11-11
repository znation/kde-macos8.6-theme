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
        gtk_dialog_client,
        icon_dialog_client,
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
        gtk_dialog_client,
        icon_dialog_client,
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
    """

    attr: str
    flag: str
    help: str
    client: Callable[[Session], tuple[str, ...]]
    client_tool: str


# One entry per dialog mode, in the order the CLI lists the flags: the parser
# adds one ``--*-dialog`` flag per entry in this order, and the workflow walks
# it to pick the client for the flag set on the command line. The CLI accepts
# at most one flag, so no other ordering is observable.
DIALOG_MODES = (
    DialogMode(
        "checkbox_dialog",
        "--checkbox-dialog",
        (
            "open a KDialog warning box whose dontagain check box the Kvantum "
            "engine draws with the theme's checkbox art, and capture it at "
            "the 480x360 size the widget gate byte-compares"
        ),
        checkbox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "combobox_dialog",
        "--combobox-dialog",
        (
            "open a KDialog chooser whose combo box the Kvantum engine draws "
            "with the theme's comboarrow art, and capture it at the 480x360 "
            "size the widget gate byte-compares"
        ),
        combobox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "lineedit_dialog",
        "--lineedit-dialog",
        (
            "open a KDialog input box whose line edit the Kvantum engine "
            "draws with the theme's sunken-field art, and capture it at the "
            "480x360 size the widget gate byte-compares"
        ),
        lineedit_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "menu_dialog",
        "--menu-dialog",
        (
            "open a KDialog menu list whose item-view frame the Kvantum "
            "engine draws with the theme's GenericFrame art, and capture it "
            "at the 480x360 size the widget gate byte-compares"
        ),
        menu_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "radiolist_dialog",
        "--radiolist-dialog",
        (
            "open a KDialog radio list whose sunken list field, selected- "
            "row selection band and checked and unchecked radio indicators "
            "the Kvantum engine draws with the theme's palette and radio "
            "art, and capture it at the 480x360 size the widget gate "
            "byte-compares"
        ),
        radio_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "calendar_dialog",
        "--calendar-dialog",
        (
            "open a KDialog calendar whose day table the Kvantum engine "
            "paints with the theme's colorscheme palette, and capture it at "
            "the 480x360 size the widget gate byte-compares"
        ),
        calendar_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "color_dialog",
        "--color-dialog",
        (
            "open a KDialog color picker whose swatch grid, line edits and "
            "push buttons the Kvantum engine draws with the theme's palette "
            "and art, and capture it at the 480x360 size the widget gate "
            "byte-compares"
        ),
        color_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "progressbar_dialog",
        "--progressbar-dialog",
        (
            "open a KDialog progress meter whose at-rest trough the Kvantum "
            "engine draws with the theme's progress art, and capture it at "
            "the 480x360 size the widget gate byte-compares"
        ),
        progressbar_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "slider_dialog",
        "--slider-dialog",
        (
            "open a KDialog slider whose QSlider the Kvantum engine draws "
            "with the theme's slider and slidercursor art, and capture it "
            "at the 480x360 size the widget gate byte-compares"
        ),
        slider_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "textbox_dialog",
        "--textbox-dialog",
        (
            "open a KDialog text box whose vertical scrollbar the Kvantum "
            "engine draws with the theme's scrollbar art, and capture it at "
            "the 480x360 size the widget gate byte-compares"
        ),
        textbox_dialog_client,
        "kdialog",
    ),
    DialogMode(
        "gtk_dialog",
        "--gtk-dialog",
        (
            "open a zenity text-entry dialog whose content-area GtkEntry the "
            "GTK 4 toolkit draws with the published theme selection, and "
            "capture it at the 480x360 size the widget gate byte-compares"
        ),
        gtk_dialog_client,
        "zenity",
    ),
    DialogMode(
        "icon_dialog",
        "--icon-dialog",
        (
            "open a KDialog icon chooser whose sunken icon-list field, search "
            "field and push buttons the Kvantum engine draws with the theme's "
            "palette and art, and capture it at the 480x360 size the widget "
            "gate byte-compares"
        ),
        icon_dialog_client,
        "kdialog",
    ),
)

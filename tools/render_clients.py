"""Build the client argv for the render's dialog surfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.render_session import Session


def checkbox_dialog_client(session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the widget gate renders.

    A ``kdialog`` warning whose ``--dontagain`` check box is a real
    ``QCheckBox``: the engine draws its indicator through this theme's
    ``checkbox-*`` art and ``check_size``, the pixels the widget gate
    byte-compares. The ``--dontagain`` config file lands in the scratch
    config home, never the caller's.
    """
    dontagain = session.config / "kde-dontagain"
    return (
        "kdialog",
        "--title",
        "Test",
        "--warningyesno",
        "Delete?",
        "--dontagain",
        f"{dontagain}:widgets",
    )


def combobox_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the combo arrow gate renders.

    A ``kdialog`` chooser with a real ``QComboBox``: the engine draws its
    indicator through this theme's ``comboarrow-*`` art and
    ``[ComboBox] indicator.size``, the pixels the widget gate byte-compares.
    """
    return (
        "kdialog",
        "--title",
        "Test",
        "--combobox",
        "Choose a disk:",
        "Macintosh HD",
        "Zip Disk",
    )


def menu_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the list dialog whose QAbstractScrollArea uses GenericFrame."""
    return ("kdialog", "--title", "Test", "--menu", "Pick an item:", "Alpha", "a", "Beta", "b")

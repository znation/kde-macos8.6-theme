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


def gtk_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the GTK 4 client argv the GTK dialog gate renders.

    A ``zenity`` text-entry dialog with a content-area ``GtkEntry``: zenity
    is a GTK 4 client (no theme-name CSS switch exists) and wears this theme
    exactly through the selection ``tools/gtk_selection.py::apply`` publishes
    into the scratch config home -- the settings theme-name keys and the
    user CSS ``@import`` of the installed gtk-4.0 sheet, whose relative
    ``../assets/*`` icon URLs resolve beneath the scratch data home. The
    entry field is the cell the gtk dialog gate byte-compares; the fresh
    scratch config home means the selection never finds foreign user CSS to
    back up, and nothing writes to the caller's real config.
    """
    return ("zenity", "--title", "Test", "--entry", "--text", "Choose a name:")


def lineedit_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the line-edit field gate renders.

    A ``kdialog`` input box with a real empty ``QLineEdit``: the engine draws
    its sunken field through this theme's ``[LineEdit]`` art, the pixels the
    widget gate byte-compares. The empty field keeps the caret at the
    field's left padding, so the pinned crop right of the caret carries no
    caret byte.
    """
    return ("kdialog", "--title", "Test", "--inputbox", "Choose a name:")


def progressbar_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the progressbar trough gate renders.

    A progress meter with a real at-rest ``QProgressBar`` at value zero:
    the engine draws its trough frame through this theme's
    ``[Progressbar]`` ``progress`` element (a 2px frame margin), the pixels
    the widget gate byte-compares. The meter never moves -- only its D-Bus
    interface drives it, and this client calls none of it -- so no striped
    ``progress-pattern`` tile and no busy animation enters any crop. The
    session script kills the client after the capture, so the D-Bus
    reference kdialog prints never receives a call.

    The client is the helper daemon ``kdialog`` itself execs for a
    ``--progressbar`` dialog, not ``kdialog``: measured on this host
    (kdialog 25.04.0, 2026-11-10), a ``kdialog --progressbar`` launcher
    prints the D-Bus reference and exits within the first second, so the
    shared session script's liveness check would fail the render after the
    settle and the dialog would outlive its killed launcher.
    ``kdialog_progress_helper`` runs the same dialog itself and survives
    the settle (verified 2026-11-10, alive at 1 s and 8 s offscreen), so
    the liveness check sees it and the session script still ends it after
    the capture. It is installed with ``kdialog``, so the CLI's missing-
    tool check names ``kdialog`` as before.
    """
    return ("kdialog_progress_helper", "--title", "Test", "--progressbar", "Working:")


def slider_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the slider thumb and trough gate renders.

    A ``kdialog`` slider with a real at-rest ``QSlider`` at value zero: the
    engine draws the trough through this theme's ``[Slider]`` ``slider``
    element and the thumb at the trough's left end through the
    ``[SliderCursor]`` ``slidercursor`` art, the pixels the widget gate
    byte-compares. Value zero keeps the thumb in its resting state, so no
    pressed or hover byte enters any crop.
    """
    return (
        "kdialog",
        "--title",
        "Test",
        "--slider",
        "Brightness:",
        "0",
        "100",
        "10",
    )


def textbox_dialog_client(session: Session) -> tuple[str, ...]:
    """Return the Qt client argv the scrollbar dialog gate renders.

    A ``kdialog`` text box over a fresh plain-text scratch file under the
    session root the render's context manager removes: the text view is a
    real ``QTextEdit`` with a vertical ``QScrollBar``, and the engine draws
    the bar through this theme's ``[Scrollbar]``/``[ScrollbarSlider]``/
    ``[ScrollbarGroove]`` sections, the pixels the widget gate byte-compares.
    At value zero the scrollbar rests, so no hover, press or focus byte
    enters any crop: value zero disables the up arrow (its triangle paints
    the disabled #999999 ``arrow`` tint, the same disabled tint the pinned
    ``comboarrow-*`` disabled families draw) while the down arrow stays
    enabled in the normal #000000 state.

    The file holds 40 numbered lines: on this host (2026-11-10) that count
    keeps the at-rest handle tall enough (its interior spans its full 13px
    ``grip`` indicator inside the 2px ``scrollbarslider`` frame margins)
    and still leaves a trough band below the handle, while no line wraps
    (so no horizontal scrollbar enters the capture) and at least one full
    line scrolls out of view.
    """
    textbox_file = session.root / "textbox.txt"
    textbox_file.write_text(
        "".join(
            f"Line {number:02d} fills the text box for the scroll gate.\n"
            for number in range(1, 41)
        )
    )
    return ("kdialog", "--title", "Test", "--textbox", str(textbox_file))


def menu_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the list dialog whose QAbstractScrollArea uses GenericFrame."""
    return ("kdialog", "--title", "Test", "--menu", "Pick an item:", "Alpha", "a", "Beta", "b")


def calendar_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the calendar dialog whose date table the engine palette paints.

    ``--dateformat`` is load-bearing: without it ``--default``'s date is
    ignored and the dialog opens today's month with today selected, while
    with it the default applies in either option order. The pinned default
    (1970-01-07, a Wednesday in January 1970) keeps every gate band
    clock-independent forever: the view never contains today's date, so no
    today marker, no clock-driven selection and no month-by-month layout
    drift can enter any crop.
    """
    return (
        "kdialog", "--title", "Test", "--calendar", "Calendar:",
        "--default", "1970-01-07", "--dateformat", "yyyy-MM-dd",
    )


def color_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the color dialog whose widgets the engine palette paints.

    ``--getcolor`` opens KDE's color dialog: the engine draws its basic-color
    swatch grid, sunken value fields and push buttons with this theme's
    colorscheme palette and shipped art, the pixels the widget gate
    byte-compares. The dialog shows no clock-dependent content -- no date,
    no today marker and no clock-driven selection can enter any band -- so
    the capture needs no date or default pin.
    """
    return ("kdialog", "--title", "Test", "--getcolor")

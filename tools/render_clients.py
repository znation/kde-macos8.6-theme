"""Build the client argv for the render's dialog surfaces."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

try:
    from tools import render_window_rules
except ImportError:  # imported from a directly run tool
    import render_window_rules

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


def radio_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the radio list whose radio indicators the engine draws.

    ``--radiolist`` opens KDE's radio-list chooser: the engine draws the
    sunken list field, the selected row's selection band and the checked
    and unchecked radio indicators with this theme's palette and shipped
    ``radio`` art. The ``on`` status pins the checked item as a fixed
    default, so the selection never depends on clock, network or input,
    and the capture needs no date or default pin.
    """
    return (
        "kdialog", "--title", "Test", "--radiolist", "Pick an item:",
        "a", "Alpha", "on", "b", "Beta", "off", "c", "Gamma", "off",
    )


def icon_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the icon chooser whose fields the engine palette paints.

    ``--geticon`` opens KDE's icon chooser: the engine draws its top-row
    search field, sunken icon-list field and push buttons with this theme's
    colorscheme palette and shipped art, the pixels the widget gate
    byte-compares. The pinned bands avoid the icon-grid's cells entirely:
    the grid's picture content is the fallback icon theme's art, not
    theme-owned, so no band may pin any icon's pixels. The dialog shows no
    clock-dependent content -- no date, no today marker and no clock-driven
    selection can enter any band -- so the capture needs no date or default
    pin.
    """
    return ("kdialog", "--title", "Test", "--geticon", "application", "")


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


def inactive_dialog_client(_session: Session) -> tuple[str, ...]:
    """Return the two-window wrapper argv the inactive-window gate renders.

    A ``sh -c`` wrapper backgrounds two ``kdialog --msgbox`` windows with
    two distinct fixed titles -- the to-be-inactive window first, the
    focused one last -- so KWin activates the newest and the earlier one
    draws the frame in its inactive state: the flat buttonless bar whose
    centered title paints the colorscheme's ``InactiveTextColor``. The
    wrapper then ``wait``s, so it is the single client PID the session
    script liveness-checks after the settle and reaps after the capture,
    exactly like every one-window client; its death after the capture
    leaves the two kdialogs to the private bus's teardown, the session
    lifecycle every client already relies on.

    The titles are the exact matches the session's forced-geometry
    ``kwinrulesrc`` rules (``tools/render_window_rules.py``) pin, and the
    inter-spawn sleep keeps the mapping order that decides which window
    KWin activates: the second window spawns after the first has had time
    to map, so KWin's newest-window activation lands on the focused one.
    """
    return (
        "sh",
        "-c",
        (
            # The titles travel inside double quotes: the outer session
            # script shlex-quotes this wrapper as one word, and single
            # quotes inside it would be escaped beyond recognition there.
            f'kdialog --title "{render_window_rules.INACTIVE_TITLE}" '
            "--msgbox Unfocused &\n"
            "first=$!\n"
            "sleep 2\n"
            f'kdialog --title "{render_window_rules.FOCUSED_TITLE}" '
            "--msgbox Focused\n"
            "wait\n"
        ),
        "inactive-dialog-wrapper",
    )


# The seeded file-dialog listing's fixed mtime, in seconds since the Unix
# epoch (2005-01-01 00:00:00 UTC): a constant keeps the details view's Date
# column text -- and with it the column widths the header pins re-derive --
# identical in every session, whatever the wall clock says.
FILE_DIALOG_SEED_EPOCH = 1104537600


def file_dialog_client(session: Session) -> tuple[str, ...]:
    """Return the file-chooser argv the file-dialog mode renders.

    ``--getopenfilename`` opens KDE's KIO file chooser: the engine draws its
    places sidebar, file list view, toolbar and name-filter surfaces with
    this theme's colorscheme palette and shipped art, the pixels the
    file-dialog gate byte-compares. The chooser opens on a fixed scratch
    ``Documents`` directory holding exactly three fixed empty files
    (``alpha.txt``, ``bravo.txt``, ``delta.rtf``) whose mtimes are pinned to
    ``FILE_DIALOG_SEED_EPOCH``: KIO sizes the details view's Date column
    from the rendered mtime text, so a live-clock touch would let that
    column's width -- and every header x-position beside it -- move with
    the time of day. The fresh session home, the fixed filenames, the
    pinned mtimes and the absence of any other clock-dependent content
    keep every capture deterministic, with no directory the caller's disk
    can vary. The per-file type icons the chooser draws are the fallback icon
    theme's, not theme-owned, so the gate must keep its crops off icon
    cells the way ``TestIconDialogRender``'s bands do.
    """
    documents = session.home / "Documents"
    documents.mkdir(exist_ok=True)
    for name in ("alpha.txt", "bravo.txt", "delta.rtf"):
        path = documents / name
        path.touch()
        os.utime(path, (FILE_DIALOG_SEED_EPOCH, FILE_DIALOG_SEED_EPOCH))
    return (
        "kdialog",
        "--title",
        "Test",
        "--getopenfilename",
        str(documents),
    )


def splash_client(session: Session) -> tuple[str, ...]:
    """Return the splash argv the splash mode renders.

    ``ksplashqml --test --nofork`` opens the look-and-feel package's own
    ``contents/splash/Splash.qml`` painted from the session's installed tree,
    never the caller's data home: the fullscreen layer-shell surface whose
    ``#63639C`` field the queued splash gate will compare. ``--test`` is the
    shape the bare nested session can capture: upstream 6.3.6
    ``ksplash/ksplashqml/splashapp.cpp`` advances one stage every 2 s in test
    mode and exits 0 at stage 7 (about 10 s in), so the client is alive at
    the existing 8 s settle but keeps its lifetime deterministic instead of
    drifting, while a plain ``--nofork`` client died on its own between the
    25 s and 45 s marks in the 2026-11-11 probe, taking the mapped splash
    with it -- a 30 s settle captured an already-vanished splash. The
    argument is the installed package *directory*
    (``.../plasma/look-and-feel/org.macos8.desktop``): a bare theme id would
    resolve outside the scratch data home.
    """
    return (
        "ksplashqml",
        "--test",
        "--nofork",
        str(session.data / "plasma" / "look-and-feel" / "org.macos8.desktop"),
    )

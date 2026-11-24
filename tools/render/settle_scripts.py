"""The KWin settle scripts the render session loads and re-runs.

Three KWin scripts serve the session's settle. The readiness script reports
the session's mapped windows over the scratch D-Bus so the settle ends
when the client's surface exists: a single-window report for the applet,
dialog, splash and desktop renders, and a pair report for the two-window
inactive-dialog render that fires at most once, only when both titled
windows are in the gate's focus states. The focus-settle script
re-activates the focused-title window whenever KWin does not already
treat it as active, from the client's start until the capture has
returned, because the newest-window activation the two-window wrapper
relies on is a race under the parallel check's load. The session loads
each script through KWin's scripting D-Bus (``loadScript`` on
``org.kde.KWin /Scripting``, repeated ``run`` on ``/Scripting/Script<id>``);
the fixed titles both scripts match on are written and matched by
``tools.render.window_rules``. The window-report script is a one-shot
capture-time report the session runs once after the settle ends and
before the capture starts: one ``print`` line per
``workspace.windowList()`` entry, so a failed gate's log shows whether
the client's window had actually mapped, not only when the settle path
and the capture ran.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.render.session import Session

try:
    from tools.atomic_write import write_bytes_atomically
except ImportError:  # imported from a directly run tool
    from atomic_write import write_bytes_atomically

try:
    from tools.render.window_rules import FOCUSED_TITLE, INACTIVE_TITLE
except ImportError:  # imported from a directly run tool
    from render.window_rules import FOCUSED_TITLE, INACTIVE_TITLE

FOCUS_SETTLE_SCRIPT = "inactive-dialog-focus-settle.js"
READINESS_SETTLE_SCRIPT = "render-readiness-settle.js"
WINDOW_REPORT_SCRIPT = "render-window-report.js"
READINESS_SERVICE = "org.platinumtheme.RenderSession"
READINESS_PATH = "/"
READINESS_INTERFACE = "org.platinumtheme.RenderSession"
READINESS_MEMBER = "ClientReady"


def focus_settle_text() -> str:
    """Return the one-shot KWin script the inactive-dialog session re-runs.

    Newest-window activation is a race, not a guarantee: under the parallel
    check's load the focused ``kdialog`` can map after the settle ends and
    after the capture started, so the capture catches the earlier window
    while KWin still treats it as active and every inactive pin meets the
    active decoration. The session therefore runs this script in a loop
    from the client's start until the capture has returned: each run finds
    the focused-title window and, when KWin does not already treat it as
    active, activates it directly through ``workspace.activeWindow``, so
    the pair's focus state is settled before the frame is read whenever
    the focused window has mapped at all. If it never maps, the capture
    still fails the inactive pins -- a genuine failure, not a flake.

    Probed on this host's KWin 6.3.6 (2026-11-13): ``loadScript`` on
    ``org.kde.KWin /Scripting`` registers the script at
    ``/Scripting/Script<id>`` and each ``org.kde.kwin.Script.run``
    re-executes the file, so repeated runs repeat the settle; the
    ``workspace.activeWindow`` assignment and the ``window.active`` read
    both landed in the probe (a focused-title window reported
    ``focusedActive=false`` and read ``active=Other window``, then read
    ``after=Focused window``).
    """
    return (
        "for (const window of workspace.windowList()) {\n"
        f'    if (window.caption === "{FOCUSED_TITLE}" && !window.active) {{\n'
        "        workspace.activeWindow = window;\n"
        "        print(\"render-session: settled the focused window's "
        "activation\");\n"
        "    }\n"
        "}\n"
    )


def write_focus_settle_script(session: Session) -> Path:
    """Write the focus-settle KWin script into *session*'s scratch root."""
    return _write_session_script(session, FOCUS_SETTLE_SCRIPT, focus_settle_text())


def readiness_settle_text() -> str:
    """Return the KWin script that reports when a render client maps.

    Probed on this host's KWin 6.3.6 (2026-11-18) with a 12-second bound around
    ``dbus-run-session -- kwin_wayland --virtual``. The session ran
    ``dbus-monitor --session "type='method_call',interface='org.platinumtheme.RenderSession',member='ClientReady'"``,
    loaded this script with ``qdbus6 org.kde.KWin /Scripting
    org.kde.kwin.Scripting.loadScript <path>`` and ran it through
    ``qdbus6 org.kde.KWin /Scripting/Script<id> run``. With
    ``QT_QPA_PLATFORM=wayland``, ``kdialog --msgbox`` mapped and the
    ``workspace.windowAdded`` handler's ``callDBus`` appeared in the monitor as
    a ``ClientReady`` method call to ``org.platinumtheme.RenderSession`` even
    though that destination name was unowned; the probe then stopped at its
    bound.
    """
    return (
        "function report(window) {\n"
        "    if (window.normalWindow || window.dialog || window.splash || "
        "window.desktopWindow) {\n"
        f'        callDBus("{READINESS_SERVICE}", "{READINESS_PATH}", '
        f'"{READINESS_INTERFACE}", "{READINESS_MEMBER}");\n'
        "    }\n"
        "}\n"
        "for (const window of workspace.windowList()) report(window);\n"
        "workspace.windowAdded.connect(report);\n"
    )


def pair_readiness_text() -> str:
    """Return the KWin script that reports once the two-window pair is settled.

    The inactive-dialog render needs both windows, and the first mapped
    window is not enough: the pair is ready when a window captioned
    ``INACTIVE_TITLE`` is not active and a window captioned
    ``FOCUSED_TITLE`` is. ``check()`` tests that state for every window
    KWin lists, and runs again on each ``windowAdded``,
    ``windowActivated`` and per-window ``captionChanged``, since a caption
    can be set after the window is added. It reports at most once, through
    the same ``ClientReady`` call the single-window script makes.
    """
    return (
        "let reported = false;\n"
        "function check() {\n"
        "    if (reported) {\n"
        "        return;\n"
        "    }\n"
        "    let inactive = false;\n"
        "    let focused = false;\n"
        "    for (const window of workspace.windowList()) {\n"
        f'        if (window.caption === "{INACTIVE_TITLE}" && !window.active) {{\n'
        "            inactive = true;\n"
        "        }\n"
        f'        if (window.caption === "{FOCUSED_TITLE}" && window.active) {{\n'
        "            focused = true;\n"
        "        }\n"
        "    }\n"
        "    if (inactive && focused) {\n"
        "        reported = true;\n"
        f'        callDBus("{READINESS_SERVICE}", "{READINESS_PATH}", '
        f'"{READINESS_INTERFACE}", "{READINESS_MEMBER}");\n'
        "    }\n"
        "}\n"
        "function watch(window) {\n"
        "    window.captionChanged.connect(check);\n"
        "}\n"
        "for (const window of workspace.windowList()) watch(window);\n"
        "workspace.windowAdded.connect(function (window) {\n"
        "    watch(window);\n"
        "    check();\n"
        "});\n"
        "workspace.windowActivated.connect(check);\n"
        "check();\n"
    )


def write_readiness_settle_script(session: Session, pair: bool = False) -> Path:
    """Write the readiness KWin script into *session*'s scratch root.

    ``pair=True`` writes :func:`pair_readiness_text` (the two-window
    inactive-dialog gate) instead of the single-window :func:`readiness_settle_text`.
    """
    text = pair_readiness_text() if pair else readiness_settle_text()
    return _write_session_script(session, READINESS_SETTLE_SCRIPT, text)


def window_report_text() -> str:
    """Return the one-shot KWin script that reports the capture-time windows.

    A failed pixel gate names the settle path and the stage timestamps, but
    not whether the client's window had mapped by then: this script prints
    one ``render-session: window at capture:`` line per listed window with
    its caption, whether KWin treats it as active and the kind tag the
    readiness scripts filter on, so a recurrence shows the capture-time
    mapping state. It has no signal handlers and no ``callDBus``: the
    session runs it exactly once, and KWin script ``print`` output already
    reaches the session log, as the focus-settle script's
    settled-activation line does.
    """
    return (
        "for (const window of workspace.windowList()) {\n"
        '    let kind = "other";\n'
        "    if (window.normalWindow) {\n"
        '        kind = "normalWindow";\n'
        "    } else if (window.dialog) {\n"
        '        kind = "dialog";\n'
        "    } else if (window.splash) {\n"
        '        kind = "splash";\n'
        "    } else if (window.desktopWindow) {\n"
        '        kind = "desktopWindow";\n'
        "    }\n"
        '    print("render-session: window at capture: caption=" + window.caption '
        '+ " active=" + window.active + " kind=" + kind);\n'
        "}\n"
    )


def write_window_report_script(session: Session) -> Path:
    """Write the window-report KWin script into *session*'s scratch root."""
    return _write_session_script(session, WINDOW_REPORT_SCRIPT, window_report_text())


def _write_session_script(session: Session, name: str, text: str) -> Path:
    """Atomically write UTF-8 script *text* to a named session-root file."""
    path = session.root / name
    write_bytes_atomically(path, text.encode("utf-8"))
    return path

"""Write the forced-geometry window rules the inactive-dialog render needs.

KWin activates a session's newest window, so a two-window client opens the
to-be-inactive window first and the focused one last. Without forced
geometry the placement engine, not the render, would decide where the two
windows land, and they could overlap, leave the 480x360 dialog capture, or
stack so one hides the other. This module writes a ``kwinrulesrc`` into the
scratch config home holding exactly two rules, one per fixed title, each
forcing both position and size so the two windows stand side by side, fully
inside the capture, at deterministic places.

The rule grammar probed on this host's installed KWin 6.3.6
(``libkwin.so.6`` carries the ``RuleSettings`` KConfigXT properties, whose
bound-check diagnostics name ``setTitlematch``, ``setSizerule`` and
``setPositionrule``; the KCM ``kcm_kwinrules`` comboboxes list ``Unimportant
/ Exact match / Substring match / Regular expression`` and ``Do not affect /
Apply initially / Remember / Force / Apply now / Force temporarily``):

- one group per rule, named ``1``, ``2``, ... below a ``[General]`` group
  whose ``count`` key states the rule count;
- a match criterion ``title`` with ``titlematch`` selecting the string
  match (``1`` = exact match, ``0`` = unimportant);
- a forced setting ``position`` (``x,y``) with ``positionrule=3`` (``3`` =
  force, the value the KCM's ``Force`` choice writes) and ``size``
  (``width,height``) with ``sizerule=3``.

The rendered application of these keys is verified by the inactive-dialog
render itself (``make render RENDER_MODE=inactive-dialog``), whose capture
shows the two windows at the forced places; the pinned geometry below is
re-derived from that render, never assumed.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.render_session import Session

try:
    from tools.atomic_write import write_bytes_atomically
except ImportError:  # imported from a directly run tool
    from atomic_write import write_bytes_atomically

RULES_FILE = "kwinrulesrc"
FOCUS_SETTLE_SCRIPT = "inactive-dialog-focus-settle.js"
READINESS_SETTLE_SCRIPT = "render-readiness-settle.js"
READINESS_SERVICE = "org.platinumtheme.RenderSession"
READINESS_PATH = "/"
READINESS_INTERFACE = "org.platinumtheme.RenderSession"
READINESS_MEMBER = "ClientReady"
INACTIVE_TITLE = "Inactive window"
FOCUSED_TITLE = "Focused window"
# The two forced geometries, re-derived from this host's first measured
# inactive-dialog render (KWin 6.3.6, 2026-11-11): each kdialog message box
# takes its frame to the forced client size, and the two frames stand side
# by side at their forced positions, non-overlapping and fully inside the
# 480x360 dialog capture.
INACTIVE_GEOMETRY = ((4, 8), (224, 344))
FOCUSED_GEOMETRY = ((252, 8), (224, 344))


def _rule(number: int, title: str, position: tuple[int, int], size: tuple[int, int]) -> str:
    """Return one forced-geometry rule group's INI text."""
    (x, y), (width, height) = position, size
    return (
        f"[{number}]\n"
        f"Description=forced geometry for {title}\n"
        f"title={title}\n"
        "titlematch=1\n"
        f"position={x},{y}\n"
        "positionrule=3\n"
        f"size={width},{height}\n"
        "sizerule=3\n"
    )


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


def write_readiness_settle_script(session: Session) -> Path:
    """Write the readiness KWin script into *session*'s scratch root."""
    return _write_session_script(
        session, READINESS_SETTLE_SCRIPT, readiness_settle_text()
    )


def _write_session_script(session: Session, name: str, text: str) -> Path:
    """Atomically write UTF-8 script *text* to a named session-root file."""
    path = session.root / name
    write_bytes_atomically(path, text.encode("utf-8"))
    return path


def rules_text() -> str:
    """Return the whole ``kwinrulesrc`` the inactive-dialog session reads."""
    return (
        "[General]\n"
        "count=2\n"
        "\n"
        + _rule(1, INACTIVE_TITLE, *INACTIVE_GEOMETRY)
        + "\n"
        + _rule(2, FOCUSED_TITLE, *FOCUSED_GEOMETRY)
    )


def write_window_rules(session: Session) -> None:
    """Write the two-window forced-geometry rules into *session*'s config home."""
    write_bytes_atomically(
        session.config / RULES_FILE,
        rules_text().encode("utf-8"),
    )

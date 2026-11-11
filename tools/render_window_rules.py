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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tools.render_session import Session

try:
    from tools.atomic_write import write_bytes_atomically
except ImportError:  # imported from a directly run tool
    from atomic_write import write_bytes_atomically

RULES_FILE = "kwinrulesrc"
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

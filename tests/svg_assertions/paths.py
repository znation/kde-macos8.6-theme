"""SVG path parsing for the SVG test helpers.

Reads the M/A/L/Z commands the widget artwork uses into arcs, and reconstructs
a circular arc's centre from its endpoint form.
"""

from __future__ import annotations

import math
import re

_PATH_COMMAND = re.compile(r"([MALZ])([^MALZ]*)")

_PATH_LETTER = re.compile(r"[A-Za-z]")

_SUPPORTED_PATH_COMMANDS = frozenset("MALZ")

_PATH_COMMAND_ARITY = {"M": 2, "L": 2, "A": 7, "Z": 0}

def _path_commands(d):
    """Yield (command, numbers) for each command letter in an SVG path *d*.

    Only the M/A/L/Z commands the widget artwork uses are interpreted. Any
    other letter -- H/V/C/Q/S/T, a lowercase relative command, or an exponent
    marker -- would otherwise fold into the preceding command's number body
    and be silently misread (or raise on a later tuple unpack), so name it and
    fail instead.
    """
    unsupported = sorted(set(_PATH_LETTER.findall(d)) - _SUPPORTED_PATH_COMMANDS)
    if unsupported:
        raise ValueError(
            f"unsupported SVG path command {', '.join(unsupported)} in {d!r}; "
            "this helper reads only M, A, L and Z"
        )
    for letter, body in _PATH_COMMAND.findall(d):
        yield letter, [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", body)]

def path_arcs(d):
    """Yield (start, (rx, ry, large_arc, sweep), end) for each arc in path *d*.

    Only the M/A/L/Z commands the button corner paths use are interpreted; an
    `A` command advances the current point to its endpoint, and `Z` closes the
    subpath and returns the current point to the subpath start, as SVG
    requires, so an arc after `Z` starts where the closed subpath began.

    Raise ValueError, naming the command and the path, when a command's body
    does not carry the number of coordinates that command takes: a fixture
    defect would otherwise surface as a bare tuple-unpack error naming neither.
    """
    x = y = 0.0
    subpath_start = (0.0, 0.0)
    for command, numbers in _path_commands(d):
        expected = _PATH_COMMAND_ARITY[command]
        if len(numbers) != expected:
            raise ValueError(
                f"SVG path command {command} takes {expected} numbers but got "
                f"{len(numbers)} in {d!r}"
            )
        if command == "M":
            x, y = numbers
            subpath_start = (x, y)
        elif command == "L":
            x, y = numbers
        elif command == "Z":
            x, y = subpath_start
        elif command == "A":
            rx, ry, _rotation, large_arc, sweep, nx, ny = numbers
            yield (x, y), (rx, ry, int(large_arc), int(sweep)), (nx, ny)
            x, y = nx, ny

def arc_center(start, arc, end):
    """Return the centre of a circular SVG arc given its endpoint form.

    *arc* is (rx, ry, large_arc, sweep) with no x-axis rotation, so the centre
    lies on the perpendicular bisector of start->end and the flags pick which
    side. A flipped sweep flag puts the centre on the opposite side, which is
    exactly the arc defect the button corner test computes against.

    Raise ValueError, naming the arc, when it has no centre to reconstruct: a
    zero-length chord (start == end) has no perpendicular bisector, and a
    radius shorter than half the chord cannot reach both endpoints. Both are
    fixture defects the arithmetic would otherwise report as a bare
    ZeroDivisionError or "math domain error".
    """
    (x1, y1), (rx, _ry, large_arc, sweep), (x2, y2) = start, arc, end
    x1p = (x1 - x2) / 2
    y1p = (y1 - y2) / 2
    denom = x1p * x1p + y1p * y1p
    if denom == 0:
        raise ValueError(
            f"arc from {start} to {end} is a zero-length chord: a circular "
            "arc cannot start and end at the same point"
        )
    if rx * rx < denom:
        raise ValueError(
            f"arc from {start} to {end} has radius {rx:g} smaller than half "
            f"its chord {math.sqrt(denom):g}"
        )
    factor = math.sqrt((rx * rx - denom) / denom)
    if large_arc == sweep:
        factor = -factor
    return (factor * y1p + (x1 + x2) / 2, -factor * x1p + (y1 + y2) / 2)

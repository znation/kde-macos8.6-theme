"""Verify one pixel of a render capture against a pinned colour.

The desktop session uses this probe in-session: plasmashell maps its desktop
window before the wallpaper paints, so a capture taken after the measured
settle ceiling can still show the unpainted field (measured by the feature
role 2026-11-21: four consecutive runs, two black and two painted). The
session runs this probe after each capture and recaptures bounded when the
field is unpainted, instead of failing the render and asking for a manual
retry.

Usage::

    python3 tools/render/field_probe.py <png> <RRGGBB> <x> <y>

Exit status: 0 when the pixel at ``(x, y)`` is exactly ``<RRGGBB>``, 1 when
it is another colour, and 2 when the capture is missing, unreadable, not a
PNG, or ``(x, y)`` is outside it, or the arguments are malformed. The reason
goes to stderr; nothing is ever written to stdout.
"""

from __future__ import annotations

import sys

if __package__:
    from tools.argument_parsing import is_plain_ascii_number
    from tools.png import PngError, read_png
else:  # run directly: python3 tools/render/field_probe.py
    # A directly run script's sys.path[0] is this file's directory, so the
    # project's ``png`` package one level up is named explicitly.
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from argument_parsing import is_plain_ascii_number
    from png import PngError, read_png

TOOL = "field_probe"
USAGE = "usage: python3 tools/render/field_probe.py <png> <RRGGBB> <x> <y>"


def _fail(reason: str) -> int:
    print(f"{TOOL}: {reason}", file=sys.stderr)
    return 2


def _parse_colour(value: str) -> bytes | None:
    """Return the three bytes of *value*, or None when it is not ``RRGGBB``."""
    if len(value) != 6 or any(
        c not in "0123456789ABCDEFabcdef" for c in value
    ):
        return None
    return bytes.fromhex(value)


def main(argv: list[str] | None = None) -> int:
    """Run the probe; *argv* is the argument list without a program name."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 4:
        return _fail(USAGE)
    capture, colour_text, x_text, y_text = args
    expected = _parse_colour(colour_text)
    if expected is None:
        return _fail(f"{colour_text!r} is not an RRGGBB colour")
    # int() accepts Python-only spellings a command-line coordinate should
    # not: underscore digit separators, non-ASCII decimal digits and
    # surrounding whitespace (see tools/argument_parsing.py), each silently
    # naming a different pixel. The shared plain-ASCII check refuses them
    # before parsing, naming the received text; an empty field still needs
    # the int() failure path beneath it.
    if not (is_plain_ascii_number(x_text) and is_plain_ascii_number(y_text)):
        return _fail(
            f"coordinates ({x_text!r}, {y_text!r}) are not plain ASCII integers"
        )
    try:
        x, y = int(x_text), int(y_text)
    except ValueError:
        return _fail(f"coordinates ({x_text!r}, {y_text!r}) are not integers")
    try:
        image = read_png(capture)
    except (PngError, OSError) as exc:
        return _fail(f"cannot read {capture}: {exc}")
    if not (0 <= x < image.width and 0 <= y < image.height):
        return _fail(
            f"pixel ({x}, {y}) is outside {capture} "
            f"({image.width}x{image.height})"
        )
    # The plane is tightly packed RGB: one pixel is three consecutive bytes.
    offset = (y * image.width + x) * 3
    actual = image.rgb[offset:offset + 3]
    if actual != expected:
        # The actual colour is evidence: in the session log it names what the
        # capture showed at the field pixel on each failed attempt.
        print(
            f"{TOOL}: pixel ({x}, {y}) of {capture} is #{actual.hex().upper()}",
            f"expected #{expected.hex().upper()}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Nine-slice rendering for the SVG test helpers.

Composites an id-bearing ``<g>`` of a nine-slice SVG into a ``{(x, y): fill}``
map, and builds the same-shaped map from a flat colour sequence, so a widget
test can compare a slice's pixels against an expected tile.
"""

from __future__ import annotations

import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.ints import is_plain_int

from .tree import _numeric_attribute, children_named, groups_with_id

def _slice_where(rect):
    """Name *rect* for an error, by id when it has one."""
    rect_id = rect.get("id")
    return f"rect {rect_id!r}" if rect_id else "rect"

def _slice_offset(rect, name):
    """Return *rect*'s integer *name* offset, defaulting to 0 when absent.

    An SVG rect's x and y default to 0, so an omitted offset is valid. A
    present but non-integer one is malformed and would otherwise surface as a
    bare ``int()`` ValueError naming no rect.
    """
    value = rect.get(name)
    if value is None:
        return 0
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{_slice_where(rect)} has a non-integer {name!r} of {value!r}: "
            "a nine-slice tile rect's x and y must be integers"
        ) from None

def _slice_extent(rect, name):
    """Return *rect*'s positive integer *name* extent, naming it when invalid.

    ``render_slices`` iterates ``range(extent)``, so a zero or negative width
    or height silently paints no pixels and weakens every pixel assertion built
    on it, and an absent one would surface as a bare ``int(None)`` TypeError.
    """
    contract = "a nine-slice tile rect must declare a positive width and height"
    value = _numeric_attribute(
        rect, name,
        where=_slice_where(rect),
        cast=int,
        kind="integer",
        missing=contract,
        invalid=contract,
    )
    extent = int(value)
    if extent <= 0:
        raise ValueError(
            f"{_slice_where(rect)} has a non-positive {name!r} of {value!r}: "
            "a nine-slice tile rect must declare a positive width and height"
        )
    return extent

def render_slices(tree):
    """Composite each id-bearing <g> of a nine-slice SVG into a {(x, y): fill} map.

    The frame's corner slices and the button's edge slices are both read this
    way. Coordinates are slice-local: the groups are pure translations, so a
    slice's appearance is its rects painted in document order, with a later
    rect overriding an earlier one as KSvg composites one nine-slice tile.
    Raise ValueError, naming the rect, when one of its width/height attributes
    is absent, non-integer or non-positive, its x/y is non-integer, or it
    carries a `transform`; a silently empty or mis-sampled tile would
    otherwise pass the pixel checks.
    """
    slices = {}
    for group in groups_with_id(tree):
        pixels = {}
        for rect in children_named(group, "rect"):
            transform = rect.get("transform")
            if transform is not None:
                raise ValueError(
                    f"{_slice_where(rect)} has a transform {transform!r}: "
                    "render_slices composites tile rects slice-local and "
                    "does not apply a rect-level transform, so the tile "
                    "would be read from the wrong pixels"
                )
            x = _slice_offset(rect, "x")
            y = _slice_offset(rect, "y")
            # The width, height and fill are the same for every pixel of the
            # rect, so read and validate each once instead of per column.
            width = _slice_extent(rect, "width")
            height = _slice_extent(rect, "height")
            fill = rect.get("fill")
            for dx in range(width):
                for dy in range(height):
                    pixels[(x + dx, y + dy)] = fill
        slices[group.get("id")] = pixels
    return slices

def pixel_map(colours, width, height):
    """Return the {(x, y): colour} map for a row-major *colours* sequence.

    *colours* is read left to right, top to bottom, filling *height* rows of
    *width* entries; a solid rectangle passes the same colour ``width *
    height`` times. The map has the same shape as one entry of
    `render_slices`, so a caller can compare the two directly.

    Raise ValueError when *width* or *height* is not a positive integer, or
    when *colours* does not hold exactly ``width * height`` entries. Without
    the count check *height* is inert -- the comprehension lays out rows from
    *width* alone -- so a caller passing the wrong height would get a
    differently shaped map instead of an error naming the mismatch, and a
    zero width would surface as a bare ``ZeroDivisionError``.
    """
    for name, value in (("width", width), ("height", height)):
        if not is_plain_int(value):
            raise ValueError(
                f"pixel_map {name} must be an integer: {name}={value!r}"
            )
        if value <= 0:
            raise ValueError(
                f"pixel_map {name} must be positive: {name}={value!r}"
            )
    expected = width * height
    if len(colours) != expected:
        raise ValueError(
            f"pixel_map got {len(colours)} colours; a {width}x{height} map "
            f"needs {expected} (width*height)"
        )
    return {
        (index % width, index // width): colour
        for index, colour in enumerate(colours)
    }

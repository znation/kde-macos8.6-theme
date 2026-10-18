"""Nine-slice margin, hint and tile geometry for the SVG test helpers.

Derives a centred nine-slice SVG's margin hints, its full hint geometry and
each tile's size, reads each slice group's transform origin, and yields each
state's margin hints.
"""

from __future__ import annotations

import re

from .elements import rect_geometry
from .tree import groups_with_id

def nine_slice_margins(prefix, border, size):
    """Return the four margin-hint rects of a centred nine-slice tile.

    A nine-slice SVG whose *size*-square centre tile is inset by a *border*
    on every side declares four margin hints, each naming an edge tile's
    canvas region as ``(x, y, width, height)``. The tile is centred, so the
    canvas is ``size + 2 * border`` square and the bottom/right hints start
    at ``size + border``. *prefix* is the state prefix (``""`` for an
    unprefixed SVG). The shared ``hint-tile-center`` is not included; use
    `nine_slice_hint_geometry` when every state shares one centred tile.
    """
    sep = "-" if prefix else ""
    return {
        f"{prefix}{sep}hint-top-margin": (
            str(border), "0", str(size), str(border)
        ),
        f"{prefix}{sep}hint-bottom-margin": (
            str(border), str(size + border), str(size), str(border)
        ),
        f"{prefix}{sep}hint-left-margin": (
            "0", str(border), str(border), str(size)
        ),
        f"{prefix}{sep}hint-right-margin": (
            str(size + border), str(border), str(border), str(size)
        ),
    }

def nine_slice_hint_geometry(prefixes, border, size):
    """Return the full hint geometry of a centred nine-slice SVG.

    Every state in these SVGs shares one ``hint-tile-center`` -- the
    *size*-square centre tile at ``(border, border)`` -- so it is pinned once
    alongside each state's four margin hints from `nine_slice_margins`.
    *prefixes* lists every state prefix (pass ``[""]`` for an unprefixed
    SVG). Callers whose SVG declares extra hints (an inset band, a track
    size) merge those in themselves.
    """
    geometry = {
        "hint-tile-center": (str(border), str(border), str(size), str(size))
    }
    for prefix in prefixes:
        geometry.update(nine_slice_margins(prefix, border, size))
    return geometry

def nine_slice_tile_sizes(canvas_w, canvas_h, left, right, top, bottom):
    """Return the ``(width, height)`` of each of a nine-slice's nine tiles.

    *left*, *right*, *top* and *bottom* are the four border thicknesses and
    the canvas is *canvas_w* x *canvas_h*. Each corner tile is border x
    border; each edge tile spans the canvas between its two opposite borders
    and is one border thick; the centre is the canvas inside all four
    borders. Keys are the tile names (``top``, ``topleft``, ...) that the
    margin-hint ids and the slice group ids share.
    """
    edge_w = canvas_w - left - right
    edge_h = canvas_h - top - bottom
    return {
        "top": (edge_w, top),
        "bottom": (edge_w, bottom),
        "left": (left, edge_h),
        "right": (right, edge_h),
        "center": (edge_w, edge_h),
        "topleft": (left, top),
        "topright": (right, top),
        "bottomleft": (left, bottom),
        "bottomright": (right, bottom),
    }

_TRANSLATE = re.compile(r"translate\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")

def tile_origins(tree):
    """Return {id: (x, y)} for every id-bearing <g> in *tree*.

    KSvg composites a nine-slice tile from the canvas region its group's
    `transform` names, so a group translated off its slice draws the tile from
    the wrong pixels. `render_slices` reads each group's rects slice-local and
    ignores the transform, so the pixel tests cannot see this; read the
    transform directly. A group with no transform sits at the origin.
    """
    origins = {}
    for group in groups_with_id(tree):
        transform = group.get("transform")
        if transform is None:
            origins[group.get("id")] = (0, 0)
            continue
        match = _TRANSLATE.fullmatch(transform.strip())
        if match:
            origins[group.get("id")] = (int(match.group(1)), int(match.group(2)))
        else:
            # Keep the raw text so a transform this test cannot parse fails
            # loudly instead of silently reading as the origin.
            origins[group.get("id")] = transform
    return origins

def _state_margin_hints(tree, prefixes, hint_aliases=None):
    """Yield each state's margin hints as ``(state, top, bottom, left, right)``.

    A margin hint names an edge tile's canvas region. For every prefix in
    *prefixes*, the four rects name that state's edge tiles and *state* is the
    id prefix its tile ids carry (``""`` for the unprefixed state). *tree*
    supplies the rects via `rect_geometry`; *hint_aliases* maps a state that
    declares no hints of its own to the state whose hints place its tiles.
    """
    hints = rect_geometry(tree)
    aliases = hint_aliases or {}
    for prefix in prefixes:
        state = f"{prefix}-" if prefix else ""
        source = aliases.get(prefix, prefix)
        source_sep = "-" if source else ""
        yield (
            state,
            hints[f"{source}{source_sep}hint-top-margin"],
            hints[f"{source}{source_sep}hint-bottom-margin"],
            hints[f"{source}{source_sep}hint-left-margin"],
            hints[f"{source}{source_sep}hint-right-margin"],
        )

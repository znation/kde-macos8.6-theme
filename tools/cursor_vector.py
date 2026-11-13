"""Antialiased vector rasterizer for the Platinum cursor art.

A :class:`VectorCursor` describes one simple polygon (its ``face``) in design
units, with an optional white ``outline_width`` band just outside its edges.
:func:`render_vector_rgba` draws it at a nominal pixel size by supersampling
each pixel on a ``samples`` by ``samples`` grid. A sample inside the face under
the even-odd rule is black; a sample outside the face but within
``outline_width`` of an edge is white. The pixel's alpha is the covered share
of its samples and its grey level is the white share of the covered ones, so
an edge pixel is antialiased instead of stepping between two colours.

The colours are the set's pinned palette: the face is ``#000000`` and the
outline is ``#FFFFFF``, as in ``tools/cursor_art.py``. No reference screenshot
in ``macos8.6-screenshots/`` shows a pointer, so the shapes are our own; the
antialiased style follows the user's 2026-11-12 answer to the cursor-direction
question in QUESTIONS.md. Each nominal size is rasterized from the vectors, so
no shipped frame is resampled from another frame.

The module uses the standard library only. ``checked_size`` owns the frame-size
rule, and it reads the writer's limit ``MAX_IMAGE_SIZE`` from
``tools/xcursor.py`` so that one bound covers every renderer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

if __package__:
    from tools.ints import is_plain_int
    from tools.xcursor import MAX_IMAGE_SIZE
else:
    from ints import is_plain_int
    from xcursor import MAX_IMAGE_SIZE

DEFAULT_SAMPLES = 4


def checked_size(size, noun="size"):
    """Return *size* after checking it fits an Xcursor image frame.

    The renderer allocates ``size * size * 4`` bytes, so a value above the
    writer's frame-dimension limit is refused here, naming the limit, instead
    of attempting an enormous allocation and only then failing in
    :func:`tools.xcursor.write_rgba_cursor`.
    """
    if not is_plain_int(size) or size < 1:
        raise ValueError(f"{noun} must be a positive integer: {noun}={size!r}")
    if size > MAX_IMAGE_SIZE:
        raise ValueError(
            f"{noun} must be at most {MAX_IMAGE_SIZE} (the Xcursor frame "
            f"limit): {noun}={size}"
        )
    return size


def _checked_coordinate(value, limit, name):
    """Return *value* if it is a real number in ``0..limit``, else refuse it.

    ``bool`` is refused as in :func:`tools.ints.is_plain_int`. NaN and infinity
    fail the range test, because every comparison with them is false.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number: {value!r}")
    if not 0 <= value <= limit:
        raise ValueError(f"{name} must lie in 0..{limit}: {value!r}")
    return value


@dataclass(frozen=True)
class VectorCursor:
    """One polygon face with an optional outline band, in design units.

    ``face`` is a sequence of at least three ``(x, y)`` vertices, stored as a
    tuple of tuples so the instance is hashable. ``outline_width`` is the
    non-negative band width, and ``design_size`` is the positive integer grid
    the coordinates are measured on.
    """

    face: tuple
    outline_width: float = 0
    design_size: int = 32

    def __post_init__(self):
        size = self.design_size
        if not is_plain_int(size) or size < 1:
            raise ValueError(
                f"design_size must be a positive integer: design_size={size!r}"
            )
        face = self.face
        if not isinstance(face, (tuple, list)) or len(face) < 3:
            count = len(face) if isinstance(face, (tuple, list)) else 0
            raise ValueError(
                f"face must have at least three vertices, not {count}"
            )
        checked = []
        for index, vertex in enumerate(face):
            if not isinstance(vertex, (tuple, list)) or len(vertex) != 2:
                raise ValueError(
                    f"face vertex {index} must be an (x, y) pair: {vertex!r}"
                )
            x = _checked_coordinate(vertex[0], size, f"face vertex {index} x")
            y = _checked_coordinate(vertex[1], size, f"face vertex {index} y")
            checked.append((x, y))
        width = self.outline_width
        if isinstance(width, bool) or not isinstance(width, (int, float)):
            raise ValueError(f"outline_width must be a number: {width!r}")
        if not 0 <= width < math.inf:
            raise ValueError(
                f"outline_width must be a finite non-negative number: {width!r}"
            )
        object.__setattr__(self, "face", tuple(checked))


def _inside(x, y, edges):
    """Return True when ``(x, y)`` is inside the polygon under even-odd."""
    inside = False
    for (x1, y1), (x2, y2) in edges:
        if (y1 > y) != (y2 > y):
            crossing = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < crossing:
                inside = not inside
    return inside


def _segment_distance(x, y, x1, y1, x2, y2):
    """Return the distance from ``(x, y)`` to the segment ``(x1, y1)-(x2, y2)``."""
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        t = 0.0
    else:
        t = ((x - x1) * dx + (y - y1) * dy) / length_sq
        t = min(1.0, max(0.0, t))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def _edges(face):
    """Return the polygon's edges as pairs of vertices, closing the loop."""
    count = len(face)
    return tuple((face[k], face[(k + 1) % count]) for k in range(count))


def _distance_to_edges(x, y, edges):
    return min(
        _segment_distance(x, y, x1, y1, x2, y2)
        for (x1, y1), (x2, y2) in edges
    )


def _pixel_counts(edges, width, scale, samples, px, py):
    """Count the black and white sub-samples of pixel (*px*, *py*).

    Each pixel takes ``samples * samples`` sub-samples at the centres
    ``(px + (i + 0.5) / samples, py + (j + 0.5) / samples)``, scaled into
    design units by *scale*. A centre inside the face polygon counts black;
    one within *width* of the outline counts white.
    """
    black = 0
    white = 0
    for j in range(samples):
        sy = (py + (j + 0.5) / samples) * scale
        for i in range(samples):
            sx = (px + (i + 0.5) / samples) * scale
            if _inside(sx, sy, edges):
                black += 1
            elif _distance_to_edges(sx, sy, edges) <= width:
                white += 1
    return black, white


def render_vector_rgba(art, size, samples=DEFAULT_SAMPLES):
    """Return ``size * size * 4`` straight (non-premultiplied) RGBA bytes.

    Each pixel takes ``samples * samples`` sub-samples at the centres
    ``(px + (i + 0.5) / samples, py + (j + 0.5) / samples)``, scaled into design
    units by ``design_size / size``. Let ``B`` and ``W`` count the black and
    white samples, ``N = samples**2`` and ``K = B + W``. A pixel with ``K == 0``
    is ``(0, 0, 0, 0)``. Otherwise it is ``(g, g, g, a)`` with
    ``a = (510*K + N) // (2*N)`` and ``g = (510*W + K) // (2*K)``, both integer
    round-half-up.
    """
    if not isinstance(art, VectorCursor):
        raise ValueError(f"art must be a VectorCursor: {art!r}")
    size = checked_size(size)
    if not is_plain_int(samples) or samples < 1:
        raise ValueError(f"samples must be a positive integer: {samples!r}")
    total = samples * samples
    scale = art.design_size / size
    edges = _edges(art.face)
    width = art.outline_width
    out = bytearray(size * size * 4)
    for py in range(size):
        for px in range(size):
            black, white = _pixel_counts(
                edges, width, scale, samples, px, py)
            covered = black + white
            if covered == 0:
                continue
            alpha = (510 * covered + total) // (2 * total)
            grey = (510 * white + covered) // (2 * covered)
            offset = (py * size + px) * 4
            out[offset:offset + 4] = bytes((grey, grey, grey, alpha))
    return bytes(out)


def vector_hotspot(hotspot, art, size):
    """Return the pixel hotspot for a design-unit *hotspot* at *size*.

    The result is ``(min(floor(hx * size / design_size), size - 1), ...)``.
    *hotspot* must be two numbers in ``[0, design_size)``.
    """
    if not isinstance(art, VectorCursor):
        raise ValueError(f"art must be a VectorCursor: {art!r}")
    size = checked_size(size)
    if not isinstance(hotspot, (tuple, list)) or len(hotspot) != 2:
        raise ValueError(f"hotspot must be an (x, y) pair: {hotspot!r}")
    limit = art.design_size
    pixels = []
    for name, value in zip(("x", "y"), hotspot):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"hotspot {name} must be a number: {value!r}")
        if not 0 <= value < limit:
            raise ValueError(
                f"hotspot {name} must lie in [0, {limit}): {value!r}"
            )
        pixels.append(min(math.floor(value * size / limit), size - 1))
    return (pixels[0], pixels[1])

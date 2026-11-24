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
outline is ``#FFFFFF``, as in ``tools/cursor/art.py``. No reference screenshot
in ``macos8.6-screenshots/`` shows a pointer, so the shapes are our own; the
antialiased style follows the user's 2026-11-12 answer to the cursor-direction
question in QUESTIONS.md. Each nominal size is rasterized from the vectors, so
no shipped frame is resampled from another frame.

The module uses the standard library only. ``checked_size`` owns the frame-size
rule, and it reads the writer's limit ``MAX_IMAGE_SIZE`` from
``tools/xcursor.py`` so that one bound covers every renderer.
"""

from __future__ import annotations

import functools
import math
from dataclasses import dataclass

if __package__ == "tools.cursor":
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


def _edges(face):
    """Return the polygon's edges as pairs of vertices, closing the loop."""
    count = len(face)
    return tuple((face[k], face[(k + 1) % count]) for k in range(count))


def _distance_to_edges(x, y, edges):
    """Return the distance from ``(x, y)`` to the nearest polygon edge.

    This is the per-segment nearest-point distance looped into one pass: the
    segment's own parameter is clamped to ``0..1`` with the same comparisons
    ``min(1.0, max(0.0, t))`` applied, and the running minimum replaces the
    ``min`` over a generator, so the result is the same float without a
    function call and two builtin calls per segment. A degenerate segment
    (zero length) measures straight to its single endpoint, as the
    ``t = 0.0`` branch did.
    """
    best = math.inf
    for (x1, y1), (x2, y2) in edges:
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            distance = math.hypot(x - x1, y - y1)
        else:
            t = ((x - x1) * dx + (y - y1) * dy) / length_sq
            if t < 0.0:
                t = 0.0
            elif t > 1.0:
                t = 1.0
            distance = math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
        if distance < best:
            best = distance
    return best


def _pixel_counts(edges, width, scale, offsets, px, py):
    """Count the black and white sub-samples of pixel (*px*, *py*).

    Each pixel takes ``samples * samples`` sub-samples at the centres
    ``(px + (i + 0.5) / samples, py + (j + 0.5) / samples)``, scaled into
    design units by *scale*. A centre inside the face polygon counts black;
    one within *width* of the outline counts white.

    *offsets* carries the precomputed ``(j + 0.5) / samples`` fractions the
    sub-sample centres share across every pixel, so the per-pixel work is
    one add and one multiply per coordinate instead of recomputing each
    fraction; the values are the same floats the inline expression produced.
    The even-odd and nearest-edge tests run inline, so a sub-sample costs no
    helper-function call.
    """
    black = 0
    white = 0
    for dy in offsets:
        sy = (py + dy) * scale
        for dx in offsets:
            sx = (px + dx) * scale
            inside = False
            for (x1, y1), (x2, y2) in edges:
                if (y1 > sy) != (y2 > sy):
                    crossing = x1 + (sy - y1) * (x2 - x1) / (y2 - y1)
                    if sx < crossing:
                        inside = not inside
            if inside:
                black += 1
                continue
            distance = _distance_to_edges(sx, sy, edges)
            if distance <= width:
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

    The arguments are checked on every call -- including a cache hit -- and
    only then delegated to the cached raster below: a render depends only on
    the art, the size and the sample count, so the alias cursors that share
    one art (each alias writes its own named Xcursor file) rasterize once,
    not once per name.
    """
    if not isinstance(art, VectorCursor):
        raise ValueError(f"art must be a VectorCursor: {art!r}")
    size = checked_size(size)
    if not is_plain_int(samples) or samples < 1:
        raise ValueError(f"samples must be a positive integer: {samples!r}")
    return _cached_vector_rgba(art, size, samples)


# One raster per (art, size, samples): the pure renderer below is the render
# docstring's recipe with nothing else in scope, so equal arguments always
# produce equal bytes. The alias names sharing one art make the repeat calls
# the common case in ``make_cursors``, and the manifest checks rebuild the
# whole set several times per check; the bound keeps a caller generating many
# variants from growing the cache without limit. Validation lives above the
# cache, so a malformed argument is refused on every call rather than being
# answered by an earlier entry whose key it merely compares equal to.
_MAX_CACHED_RASTERS = 128


@functools.lru_cache(maxsize=_MAX_CACHED_RASTERS)
def _cached_vector_rgba(art, size, samples):
    """Rasterize validated *art* at *size* on *samples* sub-samples per pixel."""
    total = samples * samples
    scale = art.design_size / size
    edges = _edges(art.face)
    width = art.outline_width
    offsets = tuple((j + 0.5) / samples for j in range(samples))
    out = bytearray(size * size * 4)
    for py in range(size):
        for px in range(size):
            black, white = _pixel_counts(
                edges, width, scale, offsets, px, py)
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

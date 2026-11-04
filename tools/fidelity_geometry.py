"""Crop rectangle validation and image slicing for fidelity tooling."""

from __future__ import annotations

if __package__:
    from tools.ints import is_plain_int
    from tools.png import Image
else:  # imported from a directly run tool
    from ints import is_plain_int
    from png import Image


class FidelityError(Exception):
    """A candidate and reference image could not be compared."""


def crop_rect_problem(x: int, y: int, width: int, height: int) -> str | None:
    """Return why ``(x, y, width, height)`` is not a valid crop rectangle.

    Public because it is the shared crop-rectangle contract: the CLI's
    ``--crop`` parser calls it before reading an image, and :func:`crop`
    calls it before slicing one, so both reject the same rectangles with the
    same wording.

    Every value must be an integer: :func:`crop` slices the image's RGB byte
    string, so a float coordinate would reach the slice as a raw
    ``TypeError`` naming neither the argument nor its value. The origin must
    be non-negative (``x=0``/``y=0`` is the top-left pixel, not a fault) and
    the size positive.
    """
    for name, value in (
        ("x", x),
        ("y", y),
        ("width", width),
        ("height", height),
    ):
        if not is_plain_int(value):
            return f"crop rectangle values must be integers: {name}={value!r}"
    if x < 0 or y < 0:
        return (
            f"crop rectangle origin must not be negative: "
            f"x={x} y={y} w={width} h={height}"
        )
    if width <= 0 or height <= 0:
        return (
            f"crop rectangle must have positive size: "
            f"x={x} y={y} w={width} h={height}"
        )
    return None


def crop(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """Return the ``width x height`` region of ``image`` at ``(x, y)``."""
    if not isinstance(image, Image):
        raise FidelityError(
            f"crop image must be an Image, not {type(image).__name__}"
        )
    problem = crop_rect_problem(x, y, width, height)
    if problem is not None:
        raise FidelityError(problem)
    if x + width > image.width or y + height > image.height:
        raise FidelityError(
            f"crop rectangle x={x} y={y} w={width} h={height} falls outside "
            f"the {image.width}x{image.height} image"
        )
    rows = []
    alpha_rows = [] if image.alpha is not None else None
    for row in range(y, y + height):
        start = (row * image.width + x) * 3
        rows.append(image.rgb[start : start + width * 3])
        if alpha_rows is not None:
            alpha_start = row * image.width + x
            alpha_rows.append(image.alpha[alpha_start : alpha_start + width])
    alpha = None if alpha_rows is None else b"".join(alpha_rows)
    return Image(width, height, b"".join(rows), alpha)

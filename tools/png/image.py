"""The in-memory image type and error class of the PNG reader.

:class:`PngError` is the one exception every PNG-reading module raises,
:class:`Image` is the 8-bit RGB buffer the decoder returns and the fidelity
tools compare, and :func:`pixel_at` is the bounds-checked accessor the palette
and metric tests sample through. They carry no decoding logic, so a consumer
can build or inspect an image without importing the codec; ``tools/png/__init__.py``
re-exports all three.
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from tools.ints import is_plain_int
except ImportError:  # imported as the top-level package `png` by a directly run tool
    from ints import is_plain_int


class PngError(Exception):
    """A PNG file could not be read or decoded."""


@dataclass(frozen=True)
class Image:
    """An 8-bit RGB image with tightly packed ``width * height * 3`` bytes."""

    width: int
    height: int
    rgb: bytes

    def __post_init__(self) -> None:
        # A non-int dimension reaches the comparison below as an opaque
        # TypeError (or, for a float, a byte count that is not a whole
        # number); require genuine integers here and name the offending
        # dimension.
        for name, value in (("width", self.width), ("height", self.height)):
            if not is_plain_int(value):
                raise PngError(
                    f"Image {name} must be an integer: {name}={value!r}"
                )
        if self.width <= 0 or self.height <= 0:
            raise PngError(
                f"Image dimensions must be positive: {self.width}x{self.height}"
            )
        # The annotation says bytes, but only the length was checked: a str
        # or list of the right length passed here and reached fidelity_metrics'
        # _abs_diff as an opaque TypeError ("can only concatenate str (not
        # bytes) to str") that named neither the field nor its type. bytes and
        # bytearray are both accepted -- the decoder returns bytes and a caller
        # may build a buffer in place, and a bytearray supports every operation
        # the tool performs -- while anything else is rejected by type here.
        if not isinstance(self.rgb, (bytes, bytearray)):
            raise PngError(
                f"Image rgb must be bytes or bytearray, not "
                f"{type(self.rgb).__name__}"
            )
        expected = self.width * self.height * 3
        if len(self.rgb) != expected:
            raise PngError(
                f"Image has {len(self.rgb)} RGB bytes; a {self.width}x"
                f"{self.height} image needs {expected} (width*height*3)"
            )


def pixel_at(image: Image, x: int, y: int) -> tuple[int, int, int]:
    """Return the RGB pixel at ``(x, y)`` in *image*.

    A coordinate outside the image is rejected instead of read: the RGB slice
    would be empty, and an ``x`` past the row end would wrap to the next row
    and return the wrong pixel. Naming the coordinate and the image size turns
    that silent misread into a diagnostic. Sampling a reference screenshot's
    palette or metric value goes through this accessor.

    Both coordinates must be genuine integers, checked as the :class:`Image`
    dimensions are: ``bool`` is an ``int`` subclass, so ``True``/``False``
    would pass the bounds comparison as 1/0 and silently read a different
    pixel, while a float, string or ``None`` raised an opaque ``TypeError``
    from the comparison or the RGB index that named neither the coordinate nor
    this function.
    """
    for name, value in (("x", x), ("y", y)):
        if not is_plain_int(value):
            raise ValueError(
                f"pixel coordinate {name} must be an integer: {name}={value!r}"
            )
    if not (0 <= x < image.width and 0 <= y < image.height):
        raise ValueError(
            f"pixel ({x}, {y}) is outside the {image.width}x{image.height} image"
        )
    offset = (y * image.width + x) * 3
    return (image.rgb[offset], image.rgb[offset + 1], image.rgb[offset + 2])

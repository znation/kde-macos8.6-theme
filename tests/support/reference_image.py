"""Loader and skip guard for tests that read a Git LFS reference screenshot.

``make check`` must not require the reference set (that is what
``make check-references`` is for), so a test whose reference image is not
materialized skips instead of failing. The loaders differ -- one image per
class, a dict of images, a lazily read pixel -- but the diagnostic and the
skip are the same, so they live here once; `read_reference` also loads the
one-image-per-class case.

`ReferenceScreenshotMixin` packages that one-image-per-class case for the
common test class, so a class names its image once.
"""

from __future__ import annotations

import os

from support import containment
from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.repo_root import ROOT

from tools import png  # noqa: E402
from tools.png.stream import validate_max_cols, validate_max_rows  # noqa: E402

# Decoded references, keyed by (absolute path, alpha flag, max_cols). A
# reference is a read-only Git LFS asset that cannot change during a run, so a
# path is unfiltered at most once per decode shape: each entry remembers the
# ``max_rows`` bound its decode used, and a later request reuses the decode
# whenever the decode already holds the rows it needs (a bound that exceeded
# the image height means the whole image is held). A request needing more rows
# re-decodes and replaces the entry. ``alpha`` is part of the key because it
# changes the returned planes: an RGB decode has no alpha plane, so serving it
# to an ``alpha=True`` request would silently drop the transparency the caller
# asked for. ``max_cols`` is part of the key too: the image width is the bound
# its decode used, so a different column bound cannot reuse a narrower plane.
_DECODED_REFERENCES = {}


def _bounded(image, max_rows):
    """Return *image*, truncated to *max_rows* rows when it is taller.

    The rows are copied (a ``bytes`` slice), not re-decoded: PNG filtering is
    sequential, so the top *max_rows* rows of a taller decode are exactly what
    a fresh bounded decode would produce. An alpha plane, when the decode has
    one, is truncated to the same rows; dropping it would hand an
    ``alpha=True`` request an image with no transparency.
    """
    if max_rows is None or image.height <= max_rows:
        return image
    alpha = (
        None
        if image.alpha is None
        else image.alpha[: max_rows * image.width]
    )
    return png.Image(
        image.width,
        max_rows,
        image.rgb[: max_rows * image.width * 3],
        alpha,
    )


def read_reference(path, **kwargs):
    """Read the PNG at *path* for a ``setUpClass``; return ``(image, error)``.

    *kwargs* go to ``png.read_png``. A ``PngError`` (the image is absent or an
    unmaterialized LFS pointer) comes back as ``(None, error)`` instead of
    raising, ready to hand to `skip_unless_materialized`. The decode is cached
    per absolute path, ``alpha`` mode and ``max_cols`` for the process: a later
    request reuses it whenever the cached decode already holds the rows it
    needs (a bound that exceeded the image height holds the whole image), so a
    screenshot several classes read at different ``max_rows`` bounds is
    unfiltered once, not once per bound. A request that needs more rows
    re-decodes and replaces the entry. The ``alpha`` mode is part of the cache
    key because it changes the returned planes: an RGB-only decode cannot
    answer a request for transparency. An invalid ``max_rows`` or ``max_cols``
    (not a positive plain int) is reported as an error whether or not a decode
    is cached. A path that resolves outside the repository (a checked-in
    symlink escape) is refused before the cache is consulted, so a swapped
    symlink is refused even when an earlier request cached its target.
    """
    containment.require_within_repo(path, ROOT)
    max_rows = kwargs.get("max_rows")
    max_cols = kwargs.get("max_cols")
    key = (
        os.path.abspath(str(path)),
        bool(kwargs.get("alpha", False)),
        max_cols,
    )
    try:
        validate_max_rows(max_rows)
        validate_max_cols(max_cols)
    except png.PngError as exc:
        # The cold path gets this check from ``read_png``; run it here so a
        # cached decode cannot let an invalid bound reach ``_bounded`` (whose
        # ``png.Image`` raises a less specific error, or a non-int comparison
        # a ``TypeError``).
        return None, exc
    cached = _DECODED_REFERENCES.get(key)
    if cached is not None:
        cached_rows, image, error = cached
        if error is not None:
            return None, error
        if (
            cached_rows is None
            or cached_rows > image.height
            or (max_rows is not None and max_rows <= image.height)
        ):
            return _bounded(image, max_rows), None
    try:
        image = png.read_png(path, **kwargs)
    except png.PngError as exc:
        _DECODED_REFERENCES[key] = (max_rows, None, exc)
        return None, exc
    _DECODED_REFERENCES[key] = (max_rows, image, None)
    return image, None


def skip_unless_materialized(case, path, error):
    """Skip *case* when the reference at *path* failed to materialize.

    *error* is the ``PngError`` raised while reading *path*, or ``None`` once
    it decoded; a non-``None`` error means the image is absent, so *case*
    skips with *path* and the error named rather than failing.
    """
    if error is not None:
        case.skipTest(f"{path} is not a materialized PNG: {error}")


class ReferenceScreenshotMixin:
    """Mix in before ``unittest.TestCase``: load ``REFERENCE`` once, skip without it.

    A class sets ``REFERENCE`` to the PNG path and may set ``MAX_ROWS`` and
    ``MAX_COLS`` to decode only that many rows and columns (the default
    ``None`` decodes the whole image). ``setUpClass`` reads it into
    ``cls.image`` / ``cls.image_error``, ``setUp`` skips each test when the
    image is not materialized, and `pixel` reads one pixel of it. A mixin, not
    a ``TestCase``, so importing it never makes a test module collect it.
    """

    REFERENCE = None
    MAX_ROWS = None
    MAX_COLS = None

    @classmethod
    def setUpClass(cls):
        cls.image, cls.image_error = read_reference(
            cls.REFERENCE, max_rows=cls.MAX_ROWS, max_cols=cls.MAX_COLS
        )

    def setUp(self):
        skip_unless_materialized(self, self.REFERENCE, self.image_error)

    def pixel(self, x, y):
        """Return the class reference's pixel at ``(x, y)``; ``setUp`` guards absence."""
        return png.pixel_at(self.image, x, y)

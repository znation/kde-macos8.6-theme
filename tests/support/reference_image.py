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

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)

from tools import png  # noqa: E402

# Decoded references, keyed by absolute path and ``max_rows``. A reference is
# a read-only Git LFS asset that cannot change during a run, and several test
# classes decode the same screenshot (with the same bound), so the second and
# later classes reuse the first class's decode instead of re-unfiltering it.
_DECODED_REFERENCES = {}


def read_reference(path, **kwargs):
    """Read the PNG at *path* for a ``setUpClass``; return ``(image, error)``.

    *kwargs* go to ``png.read_png``. A ``PngError`` (the image is absent or an
    unmaterialized LFS pointer) comes back as ``(None, error)`` instead of
    raising, ready to hand to `skip_unless_materialized`. The result is cached
    per ``(absolute path, max_rows)`` for the process, so a screenshot read by
    several classes is decoded once.
    """
    key = (os.path.abspath(str(path)), kwargs.get("max_rows"))
    if key not in _DECODED_REFERENCES:
        try:
            _DECODED_REFERENCES[key] = (png.read_png(path, **kwargs), None)
        except png.PngError as exc:
            _DECODED_REFERENCES[key] = (None, exc)
    return _DECODED_REFERENCES[key]


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

    A class sets ``REFERENCE`` to the PNG path and may set ``MAX_ROWS`` to
    decode only that many rows (the default ``None`` decodes the whole image).
    ``setUpClass`` reads it into ``cls.image`` / ``cls.image_error``, ``setUp``
    skips each test when the image is not materialized, and `pixel` reads one
    pixel of it. A mixin, not a ``TestCase``, so importing it never makes a
    test module collect it.
    """

    REFERENCE = None
    MAX_ROWS = None

    @classmethod
    def setUpClass(cls):
        cls.image, cls.image_error = read_reference(
            cls.REFERENCE, max_rows=cls.MAX_ROWS
        )

    def setUp(self):
        skip_unless_materialized(self, self.REFERENCE, self.image_error)

    def pixel(self, x, y):
        """Return the class reference's pixel at ``(x, y)``; ``setUp`` guards absence."""
        return png.pixel_at(self.image, x, y)

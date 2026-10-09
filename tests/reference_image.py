"""Skip guard for tests that read a Git LFS reference screenshot.

``make check`` must not require the reference set (that is what
``make check-references`` is for), so a test whose reference image is not
materialized skips instead of failing. The loaders differ -- one image per
class, a dict of images, a lazily read pixel -- but the diagnostic and the
skip are the same, so they live here once.
"""


def skip_unless_materialized(case, path, error):
    """Skip *case* when the reference at *path* failed to materialize.

    *error* is the ``PngError`` raised while reading *path*, or ``None`` once
    it decoded; a non-``None`` error means the image is absent, so *case*
    skips with *path* and the error named rather than failing.
    """
    if error is not None:
        case.skipTest(f"{path} is not a materialized PNG: {error}")

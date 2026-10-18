"""Shared paths, reference loader and constants for the Aurorae decoration tests.

The package paths, the two reference screenshots the artwork is re-derived
from, the inactive-state grey, and the `ReferenceImageCase` mixin that loads
them. The `test_aurorae_*` modules each cover one concern of the
`org.macos8.desktop` window decoration and import what they share from here.
"""

from __future__ import annotations

import os

from support.platinum_palette import hex_colour
from support.reference_image import read_reference, skip_unless_materialized
from support.theme_install import ROOT

from tools import png  # noqa: E402


AURORAE_ID = "org.macos8.desktop"
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", AURORAE_ID)
DECORATION_SVG = os.path.join(AURORAE_DIR, "decoration.svg")

REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
# The deepest reference row this module reads is the bottom border at y=424.
REFERENCE_ROWS = 425
# The retail Japanese 8.6 System Profiler window shows the close, zoom and
# collapse boxes in one title bar (aboutsystem's window cannot be zoomed).
PROFILER_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "systemprofiler_betawiki.png"
)
# The deepest profiler row this module reads is the highlight row at y=38.
PROFILER_ROWS = 39

# The flat grey every inactive-state tile uses in place of the active tile's
# highlight and pinstripe fills. The reference set has no inactive window, so
# this value is KDE-required provenance: it is the active title field's flat
# row, sampled at (250, 27).
INACTIVE_GREY = "#CCCCCC"
# The zoom face's local x in the 21x13 zoom canvas: the stripe-free gap to its left.
ZOOM_BOX_X = 5


class ReferenceImageCase:
    """Mixin: load the reference once and skip when it is not materialized.

    ``make check`` must not require the Git LFS reference set (that is what
    ``make check-references`` is for), so a test whose reference image is not
    materialized skips instead of failing. It is a plain mixin, not a
    `TestCase`, so importing it does not collect an unconfigured base.
    """

    image = None
    image_error = None
    profiler_image = None
    profiler_error = None
    # A class that reads the System Profiler screenshot sets this True, so
    # ``setUpClass`` loads PROFILER_REFERENCE as well as REFERENCE.
    needs_profiler = False

    @classmethod
    def setUpClass(cls):
        cls.image, cls.image_error = read_reference(
            REFERENCE, max_rows=REFERENCE_ROWS
        )
        if cls.needs_profiler:
            cls.load_profiler_reference()

    def reference_pixel(self, x, y):
        skip_unless_materialized(self, REFERENCE, self.image_error)
        return png.pixel_at(self.image, x, y)

    @classmethod
    def load_profiler_reference(cls):
        cls.profiler_image, cls.profiler_error = read_reference(
            PROFILER_REFERENCE, max_rows=PROFILER_ROWS
        )

    def profiler_pixel(self, x, y):
        skip_unless_materialized(
            self, PROFILER_REFERENCE, self.profiler_error
        )
        return png.pixel_at(self.profiler_image, x, y)

    def profiler_region(self, x0, y0, width, height):
        """Return a profiler region as region-local {(x, y): '#RRGGBB'}."""
        return {
            (x, y): hex_colour(self.profiler_pixel(x0 + x, y0 + y))
            for y in range(height)
            for x in range(width)
        }

    def profiler_box(self, x0, y0, size=13):
        """Return a *size* x *size* profiler region as {(x, y): '#RRGGBB'}."""
        return self.profiler_region(x0, y0, size, size)

    def reference_box(self, x0, y0, size=13):
        """Return a *size* x *size* reference region as {(x, y): '#RRGGBB'}.

        The keys are the region-local coordinates (0, 0)..(*size*-1,
        *size*-1), so the map can be compared directly against a rendered
        slice. Used for the 13x13 button boxes: the 12x12 face plus its
        1px white highlight.
        """
        return {
            (x, y): hex_colour(self.reference_pixel(x0 + x, y0 + y))
            for y in range(size)
            for x in range(size)
        }

"""Shared paths, reference loader and constants for the Aurorae decoration art.

The package paths, the three reference screenshots the artwork is re-derived
from, the inactive-state greys and outline, the zoom box's local x offset, and
the `ReferenceImageCase` mixin that loads the screenshots. The
`test_aurorae_*` modules each cover one concern of the `org.macos8.desktop`
window decoration, the GTK title-button test reuses the package path and zoom
offset, and the other reference tests that sample the same screenshots import
the paths and decoder bounds from here, loading them through
`support.reference_image`.
"""

from __future__ import annotations

import os

from support.desktoptheme_paths import FANDOM_MAX_ROWS, FANDOM_REFERENCE
from support.platinum_palette import hex_colour
from support.reference_image import read_reference, skip_unless_materialized
from support.repo_root import ROOT

from tools import png  # noqa: E402


AURORAE_ID = "org.macos8.desktop"
AURORAE_DIR = os.path.join(ROOT, "theme", "aurorae", "themes", AURORAE_ID)
DECORATION_SVG = os.path.join(AURORAE_DIR, "decoration.svg")

REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "aboutsystem_betawiki.png"
)
# The deepest reference row this module reads is the bottom border at y=424.
REFERENCE_ROWS = 425
# The retail 8.6 desktop shows four unfocused windows (the "Mac OS 8.6",
# "Utilities", "Applications" and "Apple System Profiler" windows); their
# flat #DDDDDD title field and 1px #555555 outline are the inactive frame's
# ground truth. The image is 2 image px per logical px.
INACTIVE_REFERENCE = FANDOM_REFERENCE
# The deepest inactive reference row this module reads is the Applications
# window's title field at y=880; it shares the fandom bound so that whichever
# desktop_fandom.png reader runs first decodes the screenshot once.
INACTIVE_REFERENCE_ROWS = FANDOM_MAX_ROWS
# The retail Japanese 8.6 System Profiler window shows the close, zoom and
# collapse boxes in one title bar (aboutsystem's window cannot be zoomed).
PROFILER_REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "systemprofiler_betawiki.png"
)
# The deepest profiler row any reader samples is the left/right border at
# y=255 (the reference-equivalence test's chrome regions); the Aurorae boxes
# read only the title bar. Sharing this bound keeps the single decode
# independent of discovery order.
PROFILER_ROWS = 256

# The flat grey every inactive-state box uses in place of the active box's
# gradient face. The inactive frame's field is `INACTIVE_FRAME_GREY`; this
# value is the button boxes' KDE-required grey (the reference's inactive
# windows draw no close/collapse boxes in their title bars).
INACTIVE_GREY = "#CCCCCC"
# The inactive frame's field, sampled from the four unfocused windows' title
# fields in `INACTIVE_REFERENCE`.
INACTIVE_FRAME_GREY = "#DDDDDD"
# The inactive frame's 1px outline, sampled from the same windows' outer
# frame edge.
INACTIVE_OUTLINE = "#555555"
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
    inactive_image = None
    inactive_error = None
    profiler_image = None
    profiler_error = None
    # A class that reads the inactive reference sets this True, so
    # ``setUpClass`` loads INACTIVE_REFERENCE as well as REFERENCE.
    needs_inactive = False
    # A class that reads the System Profiler screenshot sets this True, so
    # ``setUpClass`` loads PROFILER_REFERENCE as well as REFERENCE.
    needs_profiler = False

    @classmethod
    def setUpClass(cls):
        cls.image, cls.image_error = read_reference(
            REFERENCE, max_rows=REFERENCE_ROWS
        )
        if cls.needs_inactive:
            cls.load_inactive_reference()
        if cls.needs_profiler:
            cls.load_profiler_reference()

    def reference_pixel(self, x, y):
        """Return the desktop reference's pixel at ``(x, y)``, skipping if absent."""
        skip_unless_materialized(self, REFERENCE, self.image_error)
        return png.pixel_at(self.image, x, y)

    @classmethod
    def load_inactive_reference(cls):
        """Load the inactive reference into ``inactive_image``/``error``."""
        cls.inactive_image, cls.inactive_error = read_reference(
            INACTIVE_REFERENCE, max_rows=INACTIVE_REFERENCE_ROWS
        )

    def inactive_pixel(self, x, y):
        """Return the inactive reference's pixel at ``(x, y)``, skipping if absent."""
        skip_unless_materialized(
            self, INACTIVE_REFERENCE, self.inactive_error
        )
        return png.pixel_at(self.inactive_image, x, y)

    @classmethod
    def load_profiler_reference(cls):
        """Load the System Profiler reference into ``profiler_image``/``error``."""
        cls.profiler_image, cls.profiler_error = read_reference(
            PROFILER_REFERENCE, max_rows=PROFILER_ROWS
        )

    def profiler_pixel(self, x, y):
        """Return the profiler reference's pixel at ``(x, y)``, skipping if absent."""
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

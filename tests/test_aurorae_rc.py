"""Tests for the org.macos8.desktop Aurorae layout file (`org.macos8.desktoprc`).

Each metric the Aurorae engine reads -- title-bar height, border widths, the
button boxes and their margins -- is re-derived from the reference screenshots
`aboutsystem_betawiki.png` and `systemprofiler_betawiki.png` through
`tools/png.py`. The reference is stored with Git LFS, so a clone without it
skips these tests rather than failing `make check`.
"""

from __future__ import annotations

import os
import unittest

from aurorae_fixtures import (
    AURORAE_DIR,
    AURORAE_ID,
    ReferenceImageCase,
    ZOOM_BOX_X,
)
from kde_config import read as read_kde_config


RC = os.path.join(AURORAE_DIR, AURORAE_ID + "rc")


def _kde(rgb):
    return ",".join(str(channel) for channel in rgb)



def _black_run_length(colours, start=0):
    """Return the length of the first black->black run in *colours*.

    *colours* are RGB triples sampled at consecutive coordinates beginning at
    *start*; the run spans the first black pixel through the next black pixel
    after a gap.
    """
    blacks = [
        start + i
        for i, colour in enumerate(colours)
        if colour == (0, 0, 0)
    ]
    first = blacks[0]
    second = next(index for index in blacks if index > first + 1)
    return second - first + 1



class TestRc(ReferenceImageCase, unittest.TestCase):
    needs_profiler = True

    def setUp(self):
        self.parser = read_kde_config(RC)

    def _title_bar_height(self):
        """Return the black->black title-bar run at a clear column x=250."""
        column = [self.reference_pixel(250, y) for y in range(20, 60)]
        return _black_run_length(column, 20)

    def _side_border_thickness(self):
        """Return the black->black side-border run at a clear row y=100."""
        row = [self.reference_pixel(x, 100) for x in range(0, 16)]
        return _black_run_length(row)

    def _bottom_border_thickness(self):
        """Return the black->black bottom-border run at a clear column x=250."""
        column = [self.reference_pixel(250, y) for y in range(417, 425)]
        return _black_run_length(column, 417)

    def _frame_edges(self):
        """Return the frame's (left, right, top) reference coordinates.

        At the title bar's top row (y=25) the black outline spans the frame's
        full width, so its first and last black pixels are the outer left and
        right edges; the first black pixel down the clear column x=250 is the
        outer top edge. These are the edges the button offsets are measured
        from.
        """
        top_row = [self.reference_pixel(x, 25) for x in range(0, 400)]
        blacks = [x for x, colour in enumerate(top_row) if colour == (0, 0, 0)]
        column = [self.reference_pixel(250, y) for y in range(20, 60)]
        top = 20 + next(
            i for i, colour in enumerate(column) if colour == (0, 0, 0)
        )
        return blacks[0], blacks[-1], top

    def _box_bounds(self, x0, x1):
        """Return the (x, y, width, height) of a #888888 button face.

        The close and collapse boxes are the only #888888 faces in this band
        of the title bar of aboutsystem's window; ``x0`` and ``x1`` bound the
        columns searched so each box's bounds are measured from its own face.
        """
        points = [
            (x, y)
            for y in range(26, 44)
            for x in range(x0, x1)
            if self.reference_pixel(x, y) == (136, 136, 136)
        ]
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        return min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1

    def _close_box_size(self):
        """Return the (width, height) of the close button, highlight included.

        The #888888 bounding box is the 12x12 face; the white highlight is
        the column just right of it and the row just below it, so the
        button is one pixel wider and taller than the face.
        """
        x, y, width, height = self._box_bounds(8, 26)
        column = x + width
        row = y + height
        for dy in range(1, height + 1):
            self.assertEqual(
                self.reference_pixel(column, y + dy), (255, 255, 255), dy
            )
        for dx in range(1, width + 1):
            self.assertEqual(
                self.reference_pixel(x + dx, row), (255, 255, 255), dx
            )
        return width + 1, height + 1

    def test_layout_metrics_match_reference(self):
        layout = "Layout"
        title_height = self._title_bar_height()
        side = self._side_border_thickness()
        bottom = self._bottom_border_thickness()
        box_w, box_h = self._close_box_size()
        self.assertEqual(int(self.parser.get(layout, "TitleHeight")), title_height)
        self.assertEqual(int(self.parser.get(layout, "BorderTop")), title_height)
        self.assertEqual(int(self.parser.get(layout, "BorderLeft")), side)
        self.assertEqual(int(self.parser.get(layout, "BorderRight")), side)
        self.assertEqual(int(self.parser.get(layout, "BorderBottom")), bottom)
        self.assertEqual(int(self.parser.get(layout, "ButtonWidth")), box_w)
        self.assertEqual(int(self.parser.get(layout, "ButtonHeight")), box_h)

    def test_button_offsets_match_reference(self):
        # The close and collapse boxes are drawn over the frame at the offsets the
        # rc names: Aurorae anchors the left button group TitleEdgeLeft from
        # the frame's left edge and the right group TitleEdgeRight from its
        # right edge, both ButtonMarginTop below the frame's top edge, and the
        # decoration declares no padding hints, so those rc values are the
        # boxes' frame-local offsets. Re-deriving them from the reference is
        # what pins the rc to the artwork instead of trusting it.
        layout = "Layout"
        left, right, top = self._frame_edges()
        close_x, close_y, _, _ = self._box_bounds(8, 26)
        collapse_x, collapse_y, collapse_w, _ = self._box_bounds(338, 360)
        self.assertEqual(close_y, collapse_y)
        self.assertEqual(
            int(self.parser.get(layout, "TitleEdgeLeft")), close_x - left
        )
        self.assertEqual(
            int(self.parser.get(layout, "TitleEdgeRight")),
            right - (collapse_x + collapse_w),
        )
        # The profiler window has the same right-hand offset: its outline's
        # last black pixel on row y=22 (x<816) against the collapse box's
        # highlight column at x=809.
        outline = [
            x
            for x in range(0, 816)
            if self.profiler_pixel(x, 22) == (0, 0, 0)
        ]
        self.assertEqual(
            int(self.parser.get(layout, "TitleEdgeRight")),
            outline[-1] - 809,
        )
        self.assertEqual(
            int(self.parser.get(layout, "ButtonMarginTop")), close_y - top
        )

    def _zoom_and_collapse_faces(self):
        """Return (zoom face's last column, collapse face's first column).

        The profiler's #888888 columns in this band split into two runs, one
        per box, with the zoom box's highlight column right after the first.
        """
        columns = sorted(
            {
                x
                for y in range(26, 38)
                for x in range(775, 816)
                if self.profiler_pixel(x, y) == (136, 136, 136)
            }
        )
        jumps = [
            (a, b) for a, b in zip(columns, columns[1:]) if b - a > 1
        ]
        self.assertEqual(len(jumps), 1, columns)
        zoom_right, collapse_left = jumps[0]
        for y in range(27, 39):
            self.assertEqual(
                self.profiler_pixel(zoom_right + 1, y), (255, 255, 255), y
            )
        return zoom_right, collapse_left

    def test_button_spacing_matches_reference(self):
        # The 3-column gap from the zoom highlight to the collapse face is
        # baked into the zoom widget, so Aurorae adds no spacing of its own.
        zoom_right, collapse_left = self._zoom_and_collapse_faces()
        gap = collapse_left - zoom_right - 2
        layout = "Layout"
        self.assertEqual(int(self.parser.get(layout, "ButtonSpacing")), 0)
        self.assertEqual(
            gap,
            int(self.parser.get(layout, "ButtonWidthMaximizeRestore"))
            - ZOOM_BOX_X
            - int(self.parser.get(layout, "ButtonWidth")),
        )

    def test_zoom_button_width_matches_reference(self):
        # The pinstripes stop one column after the last #777777 stripe; the
        # zoom widget starts there and ends at the collapse face.
        stripe_end = max(
            x
            for y in range(26, 38)
            for x in range(760, 781)
            if self.profiler_pixel(x, y) == (119, 119, 119)
        )
        self.assertEqual(stripe_end, 776)
        zoom_right, collapse_left = self._zoom_and_collapse_faces()
        zoom_left = min(
            x
            for y in range(26, 38)
            for x in range(775, 816)
            if self.profiler_pixel(x, y) == (136, 136, 136)
        )
        self.assertEqual(
            int(self.parser.get("Layout", "ButtonWidthMaximizeRestore")),
            collapse_left - stripe_end,
        )
        self.assertEqual(ZOOM_BOX_X, zoom_left - stripe_end)

    def test_caption_colour_matches_reference(self):
        # ActiveTextColor is the caption glyph colour; (198, 30) is inside a
        # glyph stroke of the "About This Computer" caption.
        glyph = self.reference_pixel(198, 30)
        self.assertEqual(glyph, (0, 0, 0))
        self.assertEqual(self.parser.get("General", "ActiveTextColor"), _kde(glyph))

if __name__ == "__main__":
    unittest.main()

"""Pixel-reading assertions the render capture gates share.

A plain mixin: unittest discovers test methods only on the ``TestCase``
subclasses that mix :class:`PixelPins` in, so the mixin itself never runs
as a test. The skip guards, the render session batch, the capture
diagnostics and the dialog-gate scaffolding live in the sibling modules
(``skip_guards.py``, ``renders.py``, ``capture_diagnostics.py`` and
``gates.py``).
"""

from __future__ import annotations

from collections import Counter

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.platinum_palette import hex_colour  # noqa: E402
from tools.png import pixel_at  # noqa: E402

# How many trailing stderr lines a band mismatch quotes: enough for the
# render's last messages, short enough to read in a failure report.
BAND_TAIL_LINES = 12


def band_mismatch_context(colours, stderr):
    """Return the failure context that names a band's cause.

    *colours* is every cell colour of the band, row by row, and *stderr* the
    render's stderr. A first-cell mismatch (a desktop-face ``#CCCCCC`` where a
    dialog pixel belongs means the capture ran before the dialog mapped) does
    not name that cause by itself, so this quotes the band's distinct colours
    with their cell counts and the last :data:`BAND_TAIL_LINES` non-blank
    stderr lines, or says the render printed nothing.
    """
    counts = Counter(colours)
    summary = " ".join(f"{colour}:{counts[colour]}" for colour in sorted(counts))
    lines = [line for line in (stderr or "").splitlines() if line.strip()]
    if lines:
        render = "render stderr tail:\n" + "\n".join(lines[-BAND_TAIL_LINES:])
    else:
        render = "render printed no stderr"
    return f"whole band colours: {summary}\n{render}"


def first_differing_pixel_note(x, y, expected, observed):
    """Return the failing band row's first differing cell as a note line.

    *x*/*y* are the band's top-left capture coordinates and *expected*/*observed*
    the row's colour lists; the note names the first differing cell's absolute
    capture coordinates beside both hex colours, so a mismatch points at a
    pixel instead of only a row. A matching row (a length mismatch fails on
    the list comparison itself) adds nothing.
    """
    for offset, (want, got) in enumerate(zip(expected, observed)):
        if want != got:
            return (
                f"\nfirst differing pixel ({x + offset}, {y}): "
                f"expected {want}, observed {got}"
            )
    return ""


class PixelPins:
    """Pixel-reading assertions the render gates share.

    A plain mixin: unittest discovers test methods only on the
    ``TestCase`` subclasses that mix it in, so the mixin itself never
    runs as a test. ``TestRender``, ``TestSplashRender`` and ``DialogGate``'s concrete
    subclasses inherit these helpers beside their own ``candidate_image``
    accessors.
    """

    def assert_pixel(self, x, y, colour):
        # The coordinates ride in the failure message (after the standard
        # ``'expected' != 'observed'`` text) so a mismatch names the pixel.
        self.assertEqual(
            colour,
            hex_colour(pixel_at(self.candidate_image(), x, y)),
            f"pixel ({x}, {y})",
        )

    def assert_raised_frame(self, rect, *, flat_rows=(), corner_blend=0):
        """Pin a raised frame's outline/bevel and optional label-free rows.

        *corner_blend* excludes the antialiased corner arc some buttons
        draw over the sharp rectangle's ends: 0 (the default, and the
        dialog buttons' shape) asserts the full outline rows and columns;
        *n* > 0 shrinks each asserted span by *n* pixels at the row ends
        and by *n* - 1 at the column ends (the arc covers one fewer row),
        leaving the blend greys to the caller's row pins.
        """
        x, y, width, height = rect
        if corner_blend:
            rows = range(x + corner_blend, x + width - corner_blend)
            columns = range(y + corner_blend, y + height - corner_blend)
        else:
            rows = range(x, x + width)
            columns = range(y + 1, y + height - 1)
        for xx in rows:
            self.assert_pixel(xx, y, "#000000")
            self.assert_pixel(xx, y + height - 1, "#000000")
        for yy in columns:
            self.assert_pixel(x, yy, "#000000")
            self.assert_pixel(x + 1, yy, "#FFFFFF")
            self.assert_pixel(x + width - 2, yy, "#AAAAAA")
            self.assert_pixel(x + width - 1, yy, "#000000")
        for row in flat_rows:
            self.assert_pixel(x + 2, row, "#DDDDDD")
            self.assert_pixel(x + width - 3, row, "#DDDDDD")

    def assert_band(self, rect, rows):
        """Pin every cell of *rect* at the per-row colours *rows*.

        A blended bevel arm, a lost outline row, a swapped arm colour, a
        resampled grip bar or a one-pixel crop slip shows up here
        immediately. Each mismatch also carries :func:`band_mismatch_context`
        so a failure names the band's whole colour set and the render's
        stderr, not only the first cell that differed, and
        :func:`first_differing_pixel_note` names that cell's absolute capture
        coordinates beside both colours at the call site below.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        band = [
            hex_colour(pixel_at(image, x + dx, y + row))
            for row in range(height)
            for dx in range(width)
        ]
        context = band_mismatch_context(band, getattr(self, "stderr", ""))
        for row in range(height):
            expected = list(rows[row])
            observed = band[row * width:(row + 1) * width]
            with self.subTest(row=y + row):
                self.assertEqual(
                    expected,
                    observed,
                    context + first_differing_pixel_note(x, y + row, expected, observed),
                )

    def candidate_colour_map(self, rect):
        """Return *rect*'s candidate pixels as a rect-relative colour map.

        The byte-compare gates re-derive an expected ``{(x, y): "#RRGGBB"}``
        map keyed from the rect's top-left and compare it with the capture;
        the seven call sites (the GTK window gate's four cell pins, the
        file-dialog gate's ``assert_box_matches_svg``, the checkbox gate's
        close-box pin and :meth:`DialogGate.assert_cell_matches`) build the
        actual side here so their key schemes cannot drift apart.
        """
        image = self.candidate_image()
        x0, y0, width, height = rect
        return {
            (x, y): hex_colour(pixel_at(image, x0 + x, y0 + y))
            for x in range(width)
            for y in range(height)
        }

    def assert_flat_window_face(self, rect):
        """Pin every cell of *rect* at the flat #DDDDDD window face.

        The calendar, colour and icon dialog gates each pin one
        face crop this way: the rows must show the window body colour
        column to column, so a stray glyph row, a title-bar bleed or a
        repaint of the chrome above the widget inside fails row by row.
        """
        self.assert_band(
            rect, [["#DDDDDD"] * rect[2] for _ in range(rect[3])]
        )

    def assert_inks_off_the_face(self, x0, y0, x1, y1, message):
        """Assert the inclusive rect draws at least one pixel off the face.

        The live-ink probe the app-drawn label, caption and mark pins
        share (9 call sites in tests/test_render_file_dialog.py): the
        glyphs themselves stay unpinned, but a band that drew nothing
        over the flat #DDDDDD face fails here. The rectangle is
        inclusive on all four edges, the form the measured band
        constants already carry.
        """
        image = self.candidate_image()
        self.assertTrue(
            any(
                hex_colour(pixel_at(image, x, y)) != "#DDDDDD"
                for x in range(x0, x1 + 1)
                for y in range(y0, y1 + 1)
            ),
            message,
        )

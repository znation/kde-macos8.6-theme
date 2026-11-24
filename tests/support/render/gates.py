"""Scaffolding the dialog render gates share.

``tests/test_render_dialog_gates.py`` (the thirteen kdialog widget gates),
``tests/test_render_calendar_dialog.py`` (the two calendar gates),
``tests/test_render_file_dialog.py`` (the file-dialog gate) and
``tests/test_render_gtk_dialog.py`` (the GTK 4 window gate) all pin
``tools/render_surface.py``'s captures through :class:`DialogGate`. The
skip guards, the pixel-reading mixin, the render session batch and the
capture diagnostics live in the sibling modules (``skip_guards.py``,
``pixel_pins.py``, ``renders.py`` and ``capture_diagnostics.py``) so the
applet, desktop and splash gates share them without the dialog scaffolding.
"""

from __future__ import annotations

import os

from support.repo_root import ROOT  # noqa: F401  (puts the repository root on sys.path)
from support.kvantum_fixtures import SVG  # noqa: E402
from support.svg_case import parse_svg  # noqa: E402
from support.platinum_palette import hex_colour  # noqa: E402
from support.render.candidate_png import CachedCandidatePng  # noqa: E402
from support.render.capture_diagnostics import preserve_capture  # noqa: E402
from support.render.pixel_pins import PixelPins  # noqa: E402
from support.render.renders import Renders, render_output_note  # noqa: E402
from svg_assertions import render_slices  # noqa: E402
from tools.png import pixel_at  # noqa: E402

# The dialog render's engine-drawn widget gate: `--checkbox-dialog` opens a
# kdialog warning at the headless KWin session's centre in a 480x360 capture,
# and its dontagain check box draws the theme's `checkbox-normal` art through
# `[Session] check_size`. KWin centres the session's only window in the
# virtual framebuffer, so these crops are measured on this capture size; they
# assume the session the CLI builds for `--checkbox-dialog` (the same scratch
# config home, the applied kdeglobals defaults and the Kvantum selection).
DIALOG_WIDTH = 480
DIALOG_HEIGHT = 360


class RenderOutputMessages:
    """Append the render's own output to every pixel assertion's failure.

    A pixel assertion passes no message, so the render's stdout and stderr
    join the mismatch: a recurrence then names the settle path that ran
    instead of a bare colour pair. An explicit message is kept as given, and
    every failure additionally names the preserved capture's path (or says
    the render wrote no capture) through :meth:`capture_preservation_note`.
    The mixin reads ``stdout`` and ``stderr`` from the gate's ``setUpClass``.
    """

    def assertEqual(self, first, second, msg=None):
        if msg is None:
            msg = render_output_note(self.stdout, self.stderr) or None
        try:
            super().assertEqual(first, second, msg)
        except AssertionError as error:
            note = self.capture_preservation_note()
            if note:
                # unittest builds the ``msg`` argument eagerly even for
                # passing assertions, so the preservation must happen here,
                # in the failure path only; the note is spliced into the
                # caught error instead of a re-raise with a new traceback.
                error.args = (f"{error}\n{note}",)
            raise

    def capture_preservation_note(self):
        """Preserve this gate's capture on a failure and return the note line.

        A gate without a ``directory`` -- the plain message probes -- adds
        nothing. The capture's filename comes from the gate's ``output``
        when it sets one (the dialog gates' ``dialog.png``) and defaults to
        the dialog capture otherwise, and the kind label from the gate's
        ``KIND`` when it has one.
        """
        directory = getattr(self, "directory", None)
        if directory is None:
            return ""
        filename = os.path.basename(
            getattr(self, "output", "") or os.path.join(directory, "dialog.png")
        )
        preserved = preserve_capture(getattr(self, "KIND", "gate"), directory, filename)
        if preserved is None:
            return "the render wrote no capture"
        return f"capture preserved at {preserved}"


class DialogGate(CachedCandidatePng, RenderOutputMessages, PixelPins):
    """Test scaffolding the fifteen dialog render gates share.

    Each gate is a ``unittest.TestCase`` only through its concrete subclass
    (unittest discovers tests on the subclasses alone) and waits on its own
    ``Renders`` render; the gates differ in the kind key they wait
    on, in the shipped slice and cell geometry they byte-compare and in the
    extra widget-specific tests their modules add.
    """

    KIND: str

    def __init_subclass__(cls, **kwargs):
        # Register the kind this concrete gate waits on at class-definition
        # (import) time, so the first gate class to set up can start every
        # kind this process needs as one batch (see Renders). A gate whose
        # skip guard holds never calls ensure, so its registration never
        # starts a render.
        super().__init_subclass__(**kwargs)
        Renders.request(cls.KIND)

    @classmethod
    def setUpClass(cls):
        # All renders run concurrently (see Renders); this class
        # waits for its own and leaves its siblings' to their own classes.
        cls.stdout, cls.stderr, cls.returncode, cls.directory = (
            Renders.ensure(cls.KIND)
        )
        cls.output = os.path.join(cls.directory, "dialog.png")
        cls._candidate = None

    def test_writes_a_480x360_png(self):
        image = self.candidate_image()
        self.assertEqual((DIALOG_WIDTH, DIALOG_HEIGHT), (image.width, image.height))

    def assert_cell_matches(self, slice_name, cell):
        """Byte-compare the engine-drawn cell at *cell* with the shipped art.

        The expected pixels are the named shipped slice itself, at its canvas
        size, re-derived from the same SVG the Kvantum reference suites use:
        the engine may neither resample the art nor fill the cell from a
        foreign element.
        """
        expected = dict(render_slices(parse_svg(SVG))[slice_name])
        self.assertEqual(expected, self.candidate_colour_map(cell))

    def assert_push_button_recipe(self, rect, cell, flat_rows):
        """Pin the raised push-button recipe over its full-height cell.

        The engine's raised button recipe is one contract, so its outline,
        bevel arms, face rows and shadow arm are asserted here and both
        gates that pin a push button walk their own rect and cell through
        it (the color and icon dialog gates below).
        """
        self.assert_raised_frame(rect, flat_rows=flat_rows)
        face_row = [
            "#FFFFFF",
            *["#DDDDDD"] * 4,
        ]
        arm_row = [
            "#FFFFFF",
            *["#AAAAAA"] * 4,
        ]
        rows = (
            [["#000000"] * 5]
            + [["#FFFFFF"] * 5]
            + [face_row] * 20
            + [arm_row]
            + [["#000000"] * 5]
        )
        self.assert_band(cell, rows)

    def assert_push_button_face_reaches_its_row(self, rect):
        """Pin the raised recipe's flat face across its label-free row.

        The raised recipe's flat face must reach the whole label-free
        row: a rounded stock face, a duplicated or shifted bevel arm or
        a recoloured face fails on the row's columns. Shared with
        ``assert_push_button_recipe`` by the color and icon dialog gates.
        """
        image = self.candidate_image()
        x, y, width, height = rect
        self.assertEqual(
            ["#DDDDDD"] * (width - 4),
            [hex_colour(pixel_at(image, x + 2 + dx, y + height - 4))
             for dx in range(width - 4)],
        )

"""Pin ``DialogGate``'s class-definition registration and its decode cache.

``support.render.gates.DialogGate`` has two pieces of bookkeeping that no
rendered gate observes directly. ``__init_subclass__`` must register each
concrete gate's ``KIND`` with ``Renders`` at import time, or the first gate to
set up starts a batch that omits the render its sibling waits on. And
``candidate_image`` must decode the dialog PNG once, because every pixel pin
of a gate reads through it; a re-decode per read is slow but silent. A
mis-registered kind or a dropped cache would pass every unit in the tree
until a real Plasma host runs the gates, so these tests pin both on a
stubbed ``Renders`` and ``process_runner``: no render is ever started.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support import process_runner
from support.render import candidate_png
from support.render.gates import DialogGate, Renders
from support.render.pixel_pins import band_mismatch_context


class TestDialogGateRegistration(unittest.TestCase):
    def test_defining_a_concrete_gate_requests_its_kind(self):
        with mock.patch.object(Renders, "requested", set()), \
                mock.patch.object(process_runner, "start") as start:
            class ProbeGate(DialogGate):
                KIND = "probe-kind"

            self.assertIn("probe-kind", Renders.requested)
            # Registration only records the kind; it starts no render.
            start.assert_not_called()

    def test_each_concrete_gate_registers_its_own_kind(self):
        with mock.patch.object(Renders, "requested", set()):
            class FirstGate(DialogGate):
                KIND = "first-kind"

            class SecondGate(DialogGate):
                KIND = "second-kind"

            self.assertEqual({"first-kind", "second-kind"}, Renders.requested)

    def test_registration_does_not_complete_the_batch(self):
        with mock.patch.object(Renders, "requested", set()), \
                mock.patch.object(Renders, "completed", False):
            class ProbeGate(DialogGate):
                KIND = "probe-kind"

            self.assertFalse(Renders.completed)


class TestIconRenderSettleBudget(unittest.TestCase):
    """The icon dialog's render waits a generous settle before it captures.

    Every dialog render sleeps its settle budget before the capture, and
    the icon kind's default 8 s is a bare sleep: under the parallel check's
    load the chooser can still be unmapped when the capture lands, so the
    pins read the desktop face where the dialog's outline belongs (the
    seven icon-dialog quarantines, BUGS.md). The GTK dialog already takes
    the 20 s budget for the same reason; the icon kind takes it too. The
    flags are read from the render table, so no render is started.
    """

    def test_the_icon_render_settles_for_twenty_seconds(self):
        flags = {kind: args for kind, args, _ in Renders.KINDS}["icon"]
        self.assertIn("--settle", flags)
        settle = float(flags[flags.index("--settle") + 1])
        self.assertGreaterEqual(settle, 20.0)


class TestCandidateImageCache(unittest.TestCase):
    def _make_gate(self):
        # Mirror what setUpClass leaves on a concrete gate, without starting
        # a render: the output path and an empty decode cache.
        class ProbeGate(DialogGate):
            KIND = "probe-cache-kind"

        ProbeGate.output = os.path.join("scratch-dir", "dialog.png")
        ProbeGate._candidate = None
        return ProbeGate

    def test_the_dialog_png_is_decoded_once_across_reads(self):
        sentinel = object()
        with mock.patch.object(Renders, "requested", set()), \
                mock.patch.object(candidate_png, "read_png", return_value=sentinel) as read:
            gate = self._make_gate()
            first = gate.candidate_image()
            second = gate.candidate_image()

        read.assert_called_once_with(os.path.join("scratch-dir", "dialog.png"))
        self.assertIs(sentinel, first)
        self.assertIs(first, second)

    def test_each_gate_class_decodes_its_own_output(self):
        with mock.patch.object(Renders, "requested", set()), \
                mock.patch.object(candidate_png, "read_png", side_effect=lambda path: path) as read:
            first_gate = self._make_gate()

            class OtherGate(DialogGate):
                KIND = "other-cache-kind"

            OtherGate.output = os.path.join("other-dir", "dialog.png")
            OtherGate._candidate = None

            first = first_gate.candidate_image()
            other = OtherGate.candidate_image()

        self.assertEqual(
            [os.path.join("scratch-dir", "dialog.png"), os.path.join("other-dir", "dialog.png")],
            [c.args[0] for c in read.call_args_list],
        )
        self.assertEqual(os.path.join("scratch-dir", "dialog.png"), first)
        self.assertEqual(os.path.join("other-dir", "dialog.png"), other)



class TestBandMismatchContext(unittest.TestCase):
    """Pin the context a band mismatch quotes so a failure names its cause.

    A first-cell mismatch alone cannot tell a capture that ran before the
    dialog mapped (a desktop-face ``#CCCCCC`` band) from a crop or colour
    slip, so the context must carry every colour of the band with its cell
    count and the render's last stderr lines. Each expected value below comes
    from the inputs: a band of two ``#CCCCCC`` cells and one ``#000000`` cell,
    and a 30-line stderr whose last 12 lines are line18 through line29.
    """

    def test_names_every_colour_of_the_band_with_its_count(self):
        message = band_mismatch_context(
            ["#CCCCCC", "#CCCCCC", "#000000"], "",
        )
        self.assertIn("#CCCCCC:2", message)
        self.assertIn("#000000:1", message)

    def test_quotes_the_last_twelve_stderr_lines(self):
        stderr = "".join(f"line{index:02d}\n" for index in range(30))
        message = band_mismatch_context(["#CCCCCC"], stderr)
        self.assertIn("line18", message)
        self.assertIn("line29", message)
        self.assertNotIn("line17", message)

    def test_says_when_the_render_printed_nothing(self):
        message = band_mismatch_context(["#CCCCCC"], "  \n\n")
        self.assertIn("render printed no stderr", message)


if __name__ == "__main__":
    unittest.main()

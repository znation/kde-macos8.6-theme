"""Pixel-gate failures carry the render's own output.

A passing render keeps its session log's tail on stdout, and a pixel gate's
failure message must include the render output so a recurrence shows which
settle path ran. These tests drive the mixin and its note helper directly,
without starting a render.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import (
    DialogGate,
    PixelPins,
    RenderOutputMessages,
    diagnostics_root,
    preserve_capture,
    render_output_note,
)

CAPTURE_BYTES = b"\x89PNG probe capture bytes"


def _write_capture(directory, name="dialog.png"):
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        handle.write(CAPTURE_BYTES)
    return path


def _preserved_path(message):
    """Return the path the message's ``capture preserved at`` line names."""
    line = next(
        line for line in message.splitlines() if line.startswith("capture preserved at ")
    )
    return line[len("capture preserved at "):]


class _GateProbe(RenderOutputMessages, unittest.TestCase):
    """A gate stand-in that runs ``DialogGate.test_exits_zero``.

    ``DialogGate`` itself registers a batch kind at class-definition time
    and starts a render in ``setUpClass``; the probe reuses only its
    ``test_exits_zero`` message building, driven on the attributes a
    gate's ``setUpClass`` would set. It declares no ``test_`` methods of
    its own, so like ``_Probe`` below it contributes only a no-op
    ``runTest`` placeholder the suite counts as one trivial pass.
    """

    def runTest(self):
        pass

    def exit_status(self):
        DialogGate.test_exits_zero(self)


class _Probe(RenderOutputMessages, unittest.TestCase):
    def runTest(self):
        pass


class _BandProbe(RenderOutputMessages, PixelPins, unittest.TestCase):
    """A gate stand-in that drives ``assert_band`` without a render.

    The pixel reading is replaced per test with fixed colours; the probe
    carries a ``directory`` so the mixin's preservation note joins the band
    failures like it does in a real gate class.
    """

    stdout = ""
    stderr = ""

    def runTest(self):
        pass

    def candidate_image(self):
        return None


def _probe(stdout, stderr):
    probe = _Probe()
    probe.stdout = stdout
    probe.stderr = stderr
    return probe


class TestRenderOutputNote(unittest.TestCase):
    def test_both_streams_are_joined_under_a_heading(self):
        self.assertEqual(
            "render output:\nlog line\nerror line",
            render_output_note("log line\n", "error line\n"),
        )

    def test_empty_streams_add_no_note(self):
        self.assertEqual("", render_output_note("", "   \n"))


class TestPixelAssertionMessages(unittest.TestCase):
    def test_a_mismatch_without_a_message_carries_the_render_output(self):
        probe = _probe("render log (12 bytes), last lines:\n  settle marker\n", "")
        with self.assertRaises(AssertionError) as caught:
            probe.assertEqual(1, 2)
        self.assertEqual(
            "1 != 2 : render output:\n"
            "render log (12 bytes), last lines:\n  settle marker",
            str(caught.exception),
        )

    def test_an_explicit_message_is_kept_as_given(self):
        probe = _probe("render log output\n", "")
        with self.assertRaises(AssertionError) as caught:
            probe.assertEqual(1, 2, "given text")
        self.assertEqual("1 != 2 : given text", str(caught.exception))

    def test_a_silent_render_adds_nothing_to_the_mismatch(self):
        probe = _probe("", "")
        with self.assertRaises(AssertionError) as caught:
            probe.assertEqual(1, 2)
        self.assertEqual("1 != 2", str(caught.exception))

    def test_a_matching_pair_passes(self):
        _probe("out", "").assertEqual("#000000", "#000000")


class TestCapturePreservation(unittest.TestCase):
    """``preserve_capture`` copies a capture where the sweep cannot reach it.

    The diagnostics root is steered into this test's own scratch tree with
    ``TMPDIR``, so the pruning assertions see only directories this probe
    seeded.
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix="preservation-probe-")
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        parent = tempfile.mkdtemp(prefix="preservation-root-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"TMPDIR": parent})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = os.path.join(parent, "platinum-render-diagnostics")

    def _write_capture(self):
        return _write_capture(self.directory)

    def test_the_copy_is_byte_identical_and_outside_the_scratch_tree(self):
        self._write_capture()
        preserved = preserve_capture("probe", self.directory, "dialog.png")
        self.assertIsNotNone(preserved)
        self.assertTrue(preserved.startswith(self.root))
        self.assertFalse(preserved.startswith(self.directory))
        with open(preserved, "rb") as handle:
            self.assertEqual(CAPTURE_BYTES, handle.read())

    def test_the_diagnostics_directory_carries_stamp_pid_and_kind(self):
        self._write_capture()
        preserved = preserve_capture("probe", self.directory, "dialog.png")
        name = os.path.basename(os.path.dirname(preserved))
        stamp, pid, kind = name.split("-")
        self.assertRegex(stamp, r"^\d{8}T\d{6}Z$")
        self.assertEqual(str(os.getpid()), pid)
        self.assertEqual("probe", kind)

    def test_a_directory_without_the_capture_returns_none(self):
        self.assertIsNone(preserve_capture("probe", self.directory, "dialog.png"))
        self.assertFalse(os.path.isdir(self.root))

    def test_pruning_keeps_the_newest_eight_directories(self):
        for index in range(10):
            os.makedirs(os.path.join(self.root, f"20200101T0000{index:02d}Z-1-old"))
        self._write_capture()
        preserved = preserve_capture("probe", self.directory, "dialog.png")
        names = os.listdir(self.root)
        self.assertEqual(8, len(names))
        self.assertIn(os.path.basename(os.path.dirname(preserved)), names)
        # The three oldest pre-seeded directories were removed; the newest
        # ones and the fresh copy remain.
        self.assertNotIn("20200101T000000Z-1-old", names)
        self.assertNotIn("20200101T000001Z-1-old", names)
        self.assertNotIn("20200101T000002Z-1-old", names)
        self.assertIn("20200101T000009Z-1-old", names)


class TestFailureMessagesNameThePreservedCapture(unittest.TestCase):
    """A failing gate's message names the preserved capture's path.

    A gate whose scratch directory holds the capture fails with a note
    naming a byte-identical copy outside the scratch tree; one whose render
    wrote no capture says so instead, and a passing assertion creates no
    diagnostics at all (the preservation runs only in the failure path).
    """

    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix="preservation-probe-")
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        parent = tempfile.mkdtemp(prefix="preservation-root-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"TMPDIR": parent})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.root = os.path.join(parent, "platinum-render-diagnostics")
        self.probe = _probe("", "")
        self.probe.directory = self.directory

    def test_a_failing_assertion_names_a_byte_identical_copy(self):
        _write_capture(self.directory)
        with self.assertRaises(AssertionError) as caught:
            self.probe.assertEqual(1, 2)
        preserved = _preserved_path(str(caught.exception))
        self.assertTrue(preserved.startswith(self.root))
        self.assertFalse(preserved.startswith(self.directory))
        with open(preserved, "rb") as handle:
            self.assertEqual(CAPTURE_BYTES, handle.read())

    def test_a_failing_assertion_without_a_capture_says_the_render_wrote_none(self):
        with self.assertRaises(AssertionError) as caught:
            self.probe.assertEqual(1, 2)
        message = str(caught.exception)
        self.assertIn("the render wrote no capture", message)
        self.assertNotIn("capture preserved at", message)
        self.assertFalse(os.path.isdir(self.root))

    def test_a_passing_assertion_creates_no_diagnostics(self):
        _write_capture(self.directory)
        self.probe.assertEqual(1, 1)
        self.assertFalse(os.path.isdir(self.root))

    def test_an_exit_status_failure_carries_the_same_note(self):
        _write_capture(self.directory)
        gate = _GateProbe()
        gate.directory = self.directory
        gate.returncode = 1
        gate.stdout = "log tail\n"
        gate.stderr = ""
        with self.assertRaises(AssertionError) as caught:
            gate.exit_status()
        message = str(caught.exception)
        self.assertIn("capture preserved at", message)
        preserved = _preserved_path(message)
        with open(preserved, "rb") as handle:
            self.assertEqual(CAPTURE_BYTES, handle.read())


class TestBandMismatchNamesTheFailingPixel(unittest.TestCase):
    """A band mismatch names the first differing cell's pixel.

    ``assert_band``'s failure adds the failing row's first differing cell —
    its absolute capture coordinates beside both hex colours — to the
    whole-band context, so a mismatch points at a pixel, not only a row.
    """

    def setUp(self):
        self.probe = _BandProbe()
        self.directory = tempfile.mkdtemp(prefix="band-probe-")
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        self.probe.directory = self.directory
        parent = tempfile.mkdtemp(prefix="band-root-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        patcher = mock.patch.dict(os.environ, {"TMPDIR": parent})
        patcher.start()
        self.addCleanup(patcher.stop)

    BAND = (310, 300, 4, 2)
    ROWS = [["#DDDDDD"] * 4] * 2

    def test_a_failing_row_names_the_first_differing_pixel_and_preserves(self):
        _write_capture(self.directory)
        colours = {(313, 300): (0xCC, 0xCC, 0xCC)}
        with mock.patch(
            "support.render.gates.pixel_at",
            side_effect=lambda image, x, y: colours.get((x, y), (0xDD, 0xDD, 0xDD)),
        ):
            with self.assertRaises(AssertionError) as caught:
                self.probe.assert_band(self.BAND, self.ROWS)
        message = str(caught.exception)
        self.assertIn(
            "first differing pixel (313, 300): expected #DDDDDD, observed #CCCCCC",
            message,
        )
        preserved = _preserved_path(message)
        with open(preserved, "rb") as handle:
            self.assertEqual(CAPTURE_BYTES, handle.read())

    def test_a_failing_row_without_a_capture_says_the_render_wrote_none(self):
        with mock.patch(
            "support.render.gates.pixel_at", return_value=(0xDD, 0xDD, 0xDD)
        ):
            with self.assertRaises(AssertionError) as caught:
                self.probe.assert_band(self.BAND, [["#000000"] * 4] * 2)
        message = str(caught.exception)
        self.assertIn(
            "first differing pixel (310, 300): expected #000000, observed #DDDDDD",
            message,
        )
        self.assertIn("the render wrote no capture", message)

    def test_a_fully_matching_band_creates_no_diagnostics_copy(self):
        _write_capture(self.directory)
        with mock.patch(
            "support.render.gates.pixel_at", return_value=(0xDD, 0xDD, 0xDD)
        ):
            self.probe.assert_band(self.BAND, self.ROWS)
        self.assertFalse(os.path.isdir(diagnostics_root()))

    def test_the_pixel_note_lands_inside_the_subtest_row_context(self):
        # The pixel note is added at the assert_band call site, per row, so
        # each row's subTest carries its own failing cell: a row whose first
        # cell differs names that cell, not a later row's.
        colours = {(310, 301): (0xEE, 0xEE, 0xEE)}
        with mock.patch(
            "support.render.gates.pixel_at",
            side_effect=lambda image, x, y: colours.get((x, y), (0xDD, 0xDD, 0xDD)),
        ):
            with self.assertRaises(AssertionError) as caught:
                self.probe.assert_band(self.BAND, self.ROWS)
        self.assertIn(
            "first differing pixel (310, 301): expected #DDDDDD, observed #EEEEEE",
            str(caught.exception),
        )
        self.assertNotIn("first differing pixel (310, 300)", str(caught.exception))


class TestExitStatusMessage(unittest.TestCase):
    """A failed render's exit-status message quotes both streams.

    A passing render's session-log tail lands on stdout and prints nothing
    on stderr, so a gate whose render exits non-zero must build its
    failure message from both streams: quoting stderr alone would report
    a bare ``0 != 1`` with the log the render did print discarded.
    """

    @staticmethod
    def _gate(returncode, stdout, stderr):
        probe = _GateProbe()
        probe.returncode = returncode
        probe.stdout = stdout
        probe.stderr = stderr
        return probe

    def test_a_failed_render_quotes_its_stdout_tail_when_stderr_is_empty(self):
        gate = self._gate(
            1, "render log (12 bytes), last lines:\n  settle marker\n", ""
        )
        with self.assertRaises(AssertionError) as caught:
            gate.exit_status()
        message = str(caught.exception)
        self.assertIn("0 != 1", message)
        self.assertIn("render output:", message)
        self.assertIn("settle marker", message)

    def test_a_failed_render_quotes_both_streams(self):
        gate = self._gate(2, "log tail\n", "diagnostic\n")
        with self.assertRaises(AssertionError) as caught:
            gate.exit_status()
        message = str(caught.exception)
        self.assertIn("0 != 2", message)
        self.assertIn("log tail", message)
        self.assertIn("diagnostic", message)

    def test_a_silent_failed_render_stays_bare(self):
        gate = self._gate(1, "", "")
        with self.assertRaises(AssertionError) as caught:
            gate.exit_status()
        self.assertEqual("0 != 1", str(caught.exception))

    def test_a_passing_render_raises_nothing(self):
        self._gate(0, "render log\n", "").exit_status()


if __name__ == "__main__":
    unittest.main()

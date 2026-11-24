"""Pixel-gate failures carry the render's own output.

A passing render keeps its session log's tail on stdout, and a pixel gate's
failure message must include the render output so a recurrence shows which
settle path ran. These tests drive the mixin and its note helper directly,
without starting a render.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.render.gates import DialogGate, RenderOutputMessages, render_output_note


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

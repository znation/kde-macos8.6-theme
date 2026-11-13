"""Pin the shared GTK 3 child-probe harness in ``support.gtk_child_probe``.

The harness's program-string constants and runner moved here from
``tests/test_gtk_theme_controls.py``; these checks are its contract:
the child head's gi requirement and exit-77 skip guards, the pixel
head's reader, and ``run_gtk_child``'s three exit-status behaviors.
The children below import no GTK, so the suite process stays GTK-free.
"""

import unittest

from support.gtk_child_probe import (
    _GTK3_CHILD_HEAD,
    _GTK3_PIXEL_HEAD,
    _GTK3_SHEET_AND_WINDOW,
    _GTK3_SHEET_PROVIDER,
    run_gtk_child,
)


class _Skipped(Exception):
    """The recorder's stand-in for ``unittest.SkipTest``.

    ``unittest.TestCase.skipTest`` raises, so the caller's subsequent
    failure assertion is never reached -- recording alone would conflate
    the 77 branch with the nonzero branch. A local sentinel keeps the
    skip inside the recorder instead of skipping the contract test that
    drives it.
    """


class _Recorder:
    """Record ``skipTest`` and ``assertEqual`` calls instead of acting."""

    def __init__(self):
        self.skips = []
        self.assertions = []

    def skipTest(self, reason):
        self.skips.append(reason)
        raise _Skipped(reason)

    def assertEqual(self, a, b, msg=None):
        # unittest.TestCase.assertEqual is silent when a == b and raises
        # AssertionError with *msg* attached otherwise; record only the
        # failures, so a passing child records neither a skip nor an
        # assertion.
        if a != b:
            self.assertions.append((a, b, msg))
            raise AssertionError(msg)


class TestGtkChildProbeSupport(unittest.TestCase):
    def test_child_head_requires_gtk3_and_guards_the_skip(self):
        self.assertIn('gi.require_version("Gtk", "3.0")', _GTK3_CHILD_HEAD)
        self.assertIn('gi.require_version("Gdk", "3.0")', _GTK3_CHILD_HEAD)
        # The parent judges the child's printed reason, so the wording is
        # the contract.
        self.assertIn('print("GTK 3 introspection is not installed")', _GTK3_CHILD_HEAD)
        self.assertIn('print("no display for GTK 3")', _GTK3_CHILD_HEAD)
        self.assertEqual(2, _GTK3_CHILD_HEAD.count("sys.exit(77)"))

    def test_sheet_provider_registers_the_sheet_on_the_screen(self):
        self.assertIn("provider = Gtk.CssProvider()", _GTK3_SHEET_PROVIDER)
        self.assertIn("provider.load_from_data(css)", _GTK3_SHEET_PROVIDER)
        self.assertIn("Gtk.StyleContext.add_provider_for_screen(", _GTK3_SHEET_PROVIDER)
        # The and-window constant is exactly the provider block plus the
        # one window line, so single-window probes reuse the same bytes.
        self.assertEqual(
            _GTK3_SHEET_PROVIDER + "window = Gtk.OffscreenWindow()\n",
            _GTK3_SHEET_AND_WINDOW,
        )

    def test_sheet_and_window_paints_the_offscreen_window(self):
        self.assertIn("provider.load_from_data(css)", _GTK3_SHEET_AND_WINDOW)
        self.assertIn("window = Gtk.OffscreenWindow()", _GTK3_SHEET_AND_WINDOW)

    def test_pixel_head_defines_the_pixel_reader(self):
        self.assertIn("def at(x, y):", _GTK3_PIXEL_HEAD)
        self.assertIn(
            "pixels, stride, n = pixbuf.get_pixels(), "
            "pixbuf.get_rowstride(), pixbuf.get_n_channels()",
            _GTK3_PIXEL_HEAD,
        )
        self.assertIn(
            'return "#%02X%02X%02X" % tuple(pixels[y * stride + x * n:][:3])',
            _GTK3_PIXEL_HEAD,
        )

    def test_run_gtk_child_skips_on_exit_77_with_the_childs_reason(self):
        recorder = _Recorder()
        program = 'print("no display for GTK 3")\nraise SystemExit(77)\n'
        with self.assertRaises(_Skipped):
            run_gtk_child(recorder, program)
        self.assertEqual(["no display for GTK 3"], recorder.skips)
        # The skip short-circuits: no failure assertion is recorded for a
        # skipped child.
        self.assertEqual([], recorder.assertions)

    def test_run_gtk_child_fails_on_a_nonzero_exit_with_the_output(self):
        recorder = _Recorder()
        program = 'print("boom")\nraise SystemExit(1)\n'
        with self.assertRaises(AssertionError) as raised:
            run_gtk_child(recorder, program)
        self.assertEqual([], recorder.skips)
        self.assertEqual(1, len(recorder.assertions))
        a, b, msg = recorder.assertions[0]
        self.assertEqual(1, a)
        self.assertEqual(0, b)
        self.assertIn("boom", msg)
        self.assertIn("boom", str(raised.exception))

    def test_run_gtk_child_passes_a_child_that_exits_zero(self):
        recorder = _Recorder()
        run_gtk_child(recorder, 'print("ok")\n')
        self.assertEqual([], recorder.skips)
        self.assertEqual([], recorder.assertions)


if __name__ == "__main__":
    unittest.main()

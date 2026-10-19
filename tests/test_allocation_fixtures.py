"""Tests for tests/support/allocation_fixtures.py -- the traced-peak helper.

``peak_allocation`` wraps the memory-bound tests: it runs a callable under
``tracemalloc`` and returns the call's result beside the peak traced
allocation. The three suites that use it (``test_png_read``,
``test_png_malformed`` and ``test_check_references_io``) always pass a
callable that returns -- their guards catch the ``PngError`` and hand back a
message -- so only the normal path was ever driven. This module pins the two
behaviours those callers rely on: the peak really measures the call, and the
tracer is stopped even when the call raises, so a raising guard cannot leave
``tracemalloc`` running for the rest of the process.
"""

import tracemalloc
import unittest

from support.allocation_fixtures import peak_allocation


class Boom(Exception):
    """The exception the raising-call test expects to see propagated."""


class TestPeakAllocation(unittest.TestCase):
    def setUp(self):
        # If an earlier test ever left the tracer running (the bug this module
        # guards against), stop it here so this test measures its own call and
        # still leaves the process clean when it ends.
        tracemalloc.stop()
        self.addCleanup(tracemalloc.stop)

    def test_returns_the_call_result_beside_a_peak_that_covers_it(self):
        # The bound the memory tests assert (`peak < limit`) is only meaningful
        # if the peak is measured for the call itself; a peak that ignored the
        # call would let any guard pass. A buffer larger than the tracer's own
        # bookkeeping makes the lower bound a real check, not a tautology.
        size = 100_000
        result, peak = peak_allocation(lambda: bytes(size))
        self.assertEqual(result, bytes(size))
        self.assertGreaterEqual(peak, size)

    def test_stops_the_tracer_when_the_call_raises(self):
        # A guard that raises (the oversize/bomb guards do) must still stop the
        # tracer: the `finally` is what keeps `tracemalloc` from running for
        # every later test after the first raising call. Pin both halves -- the
        # exception propagates to the caller that inspects it, and the tracer
        # is off afterwards.
        def raise_boom():
            raise Boom("the guard rejected the input")

        with self.assertRaises(Boom):
            peak_allocation(raise_boom)
        self.assertFalse(tracemalloc.is_tracing())


if __name__ == "__main__":
    unittest.main()

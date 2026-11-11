"""Direct tests for the per-tolerance flag table in fidelity_metrics.

The table maps every possible byte delta (0-255) to 1 when the delta is
strictly over the tolerance and 0 otherwise; the rest of the fidelity
comparison translates whole channel byte strings through it.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import fidelity_metrics


class TestOverTable(unittest.TestCase):
    """Test per-byte delta counts across tolerance thresholds."""
    def test_one_entry_per_byte_delta(self):
        for tolerance in (0, 7, 255):
            self.assertEqual(len(fidelity_metrics.over_table(tolerance)), 256)

    def test_zero_tolerance_flags_every_nonzero_delta(self):
        table = fidelity_metrics.over_table(0)
        self.assertEqual(table[0], 0)
        self.assertEqual(table[1], 1)
        self.assertEqual(table[128], 1)
        self.assertEqual(table[255], 1)

    def test_a_delta_equal_to_the_tolerance_is_not_over_it(self):
        table = fidelity_metrics.over_table(7)
        self.assertEqual(table[7], 0)
        self.assertEqual(table[8], 1)

    def test_every_entry_follows_the_strict_comparison(self):
        for tolerance in (0, 7, 100, 254, 255):
            table = fidelity_metrics.over_table(tolerance)
            expected = bytes(1 if d > tolerance else 0 for d in range(256))
            self.assertEqual(table, expected, f"tolerance {tolerance}")

    def test_the_maximum_tolerance_flags_nothing(self):
        self.assertEqual(fidelity_metrics.over_table(255), bytes(256))

    def test_flagged_count_is_the_deltas_above_the_tolerance(self):
        # Deltas t+1 through 255 are over a tolerance t: 255 - t of them.
        for tolerance in (0, 7, 200):
            self.assertEqual(
                sum(fidelity_metrics.over_table(tolerance)), 255 - tolerance)

    def test_the_table_for_a_tolerance_is_reused(self):
        # over_table's docstring promises a per-tolerance cache, so repeated
        # calls for one tolerance return the same table object.
        self.assertIs(fidelity_metrics.over_table(42),
                      fidelity_metrics.over_table(42))


if __name__ == "__main__":
    unittest.main()

"""Tests for tools/byteops.py -- the shared equal-length precondition.

``png._byte_add`` and ``fidelity_metrics._abs_diff`` both pack byte strings
into big-integer lanes and call ``require_equal_lengths`` first. Their own
tests exercise only the length-mismatch branch and check that the raised
message names *their* function, so they pin neither the value the helper
returns on success nor the full diagnostic. These tests pin that shared
contract directly, so a change to the check or its wording is caught here
instead of in both callers at once.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import byteops  # noqa: E402


class TestRequireEqualLengths(unittest.TestCase):
    def test_returns_the_common_length(self):
        # Both callers use the return value as the lane width, so it must be
        # the length of the byte strings, not a fixed 0/1 success flag.
        for length in (0, 1, 2, 7, 64, 1000):
            with self.subTest(length=length):
                a = b"\x00" * length
                b = b"\xff" * length
                self.assertEqual(
                    byteops.require_equal_lengths(a, b, "_byte_add"), length
                )

    def test_two_empty_strings_return_zero(self):
        # A zero-width lane is the one success case a truthiness check would
        # mistake for failure; pin that it still returns the length.
        self.assertEqual(
            byteops.require_equal_lengths(b"", b"", "_abs_diff"), 0
        )

    def test_unequal_lengths_raise_naming_the_caller_and_both_lengths(self):
        # The diagnostic must let a caller bug be traced without a debugger:
        # name the caller and both lengths, in a's-then-b's order.
        with self.assertRaisesRegex(
            ValueError,
            r"^_byte_add\(\) requires equal-length byte strings: "
            r"len\(a\)=3 len\(b\)=2$",
        ):
            byteops.require_equal_lengths(b"\x01\x02\x03", b"\x01\x02", "_byte_add")

    def test_the_longer_side_is_reported_in_its_own_slot(self):
        # Swapping which argument is longer must swap the reported lengths,
        # not always print them the same way round.
        with self.assertRaisesRegex(
            ValueError,
            r"len\(a\)=1 len\(b\)=3$",
        ):
            byteops.require_equal_lengths(b"\x01", b"\x01\x02\x03", "_abs_diff")

    def test_the_caller_name_is_interpolated_not_hardcoded(self):
        # Each name must appear verbatim, so the helper cannot pass its
        # caller tests by always printing one fixed function name.
        for name in ("_byte_add", "_abs_diff", "custom_lane_op"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"^{name}\(\) requires equal-length byte strings: ",
                ):
                    byteops.require_equal_lengths(b"\x01", b"", name)


if __name__ == "__main__":
    unittest.main()

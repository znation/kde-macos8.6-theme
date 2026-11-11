"""Streaming page selection for horizontal fidelity intervals."""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401

from tools.fidelity_run_page import collect_run_page


class TrackedRun(dict):
    """Dict that counts its live instances and records the concurrency peak."""

    live = peak = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        type(self).live += 1
        type(self).peak = max(type(self).peak, type(self).live)

    def __del__(self):
        type(self).live -= 1


class TestCollectRunPage(unittest.TestCase):
    def test_filters_paging_totals_and_first_longest(self):
        intervals = [
            {"x": 0, "y": 0, "length": 1}, {"x": 2, "y": 0, "length": 2},
            {"x": 5, "y": 0, "length": 3}, {"x": 0, "y": 1, "length": 4},
            {"x": 8, "y": 1, "length": 1},
        ]
        page, omitted, total, longest = collect_run_page(
            iter(intervals), 2, 3, 1, 1)
        self.assertEqual(page, [{"x": 5, "y": 0, "length": 3}])
        self.assertEqual((omitted, total), (1, 5))
        self.assertEqual(longest, {"x": 0, "y": 1, "length": 4})

        page, omitted, _, _ = collect_run_page(iter(intervals), 2, 3, 9, 1)
        self.assertEqual((page, omitted), ([], 2))
        page, omitted, total, longest = collect_run_page(iter(intervals), 4, 2, 0, 1)
        self.assertEqual((page, omitted, total, longest),
                         ([], 0, 5, {"x": 0, "y": 1, "length": 4}))
        self.assertEqual(collect_run_page(iter(()), None, None, 0, 2),
                         ([], 0, 0, None))
        tied = [{"x": 0, "y": 0, "length": 3}, {"x": 4, "y": 0, "length": 3}]
        self.assertEqual(collect_run_page(iter(tied), None, None, 0, 2)[3], tied[0])

    def test_large_offset_retains_only_page_and_longest_records(self):
        TrackedRun.live = TrackedRun.peak = 0

        def generated():
            for i in range(5000):
                yield TrackedRun(x=i, y=0, length=(i % 7) + 1)

        page, omitted, total, longest = collect_run_page(
            generated(), None, None, 4990, 2)
        self.assertEqual([run["x"] for run in page], [4990, 4991])
        self.assertEqual((omitted, total, longest["x"]), (4998, 5000, 6))
        self.assertLessEqual(TrackedRun.peak, 5)

    def test_column_major_records_page_with_full_summaries(self):
        intervals = [
            {"x": 0, "y": 0, "length": 1},
            {"x": 0, "y": 2, "length": 2},
            {"x": 0, "y": 5, "length": 3},
            {"x": 1, "y": 0, "length": 4},
            {"x": 1, "y": 8, "length": 1},
        ]
        self.assertEqual(collect_run_page(iter(intervals), 2, 3, 1, 1), (
            [{"x": 0, "y": 5, "length": 3}], 1, 5,
            {"x": 1, "y": 0, "length": 4},
        ))


if __name__ == "__main__":
    unittest.main()

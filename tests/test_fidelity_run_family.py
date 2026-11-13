"""One shared assembly recipe drives both difference-run families.

``tools/fidelity_run_family.py::collect_run_family`` routes one family's
option values to its scans: a count cap pages the lazy scan, an uncapped
enabled family scans once and filters its list, and the count and longest
pick read the page or the list when either exists, else scan on their own.
The two families use the same recipe with their own callables, so this
suite drives :func:`collect_run_family` twice with stubbed callables and
asserts the mirror results.
"""

from __future__ import annotations

import unittest

from support import repo_root  # noqa: F401
from tools.fidelity_run_family import (
    COLUMN_RUN_CALLS,
    HORIZONTAL_RUN_CALLS,
    collect_run_family,
)


def _runs(*lengths):
    """Return run records with the given lengths at distinct positions."""
    return [{"x": index, "y": 0, "length": length}
            for index, length in enumerate(lengths)]


def _stub_calls(*run_lists, bundle=HORIZONTAL_RUN_CALLS):
    """Return a callables bundle whose scans serve canned run lists.

    Every scan call appends its name to *log* so the suite can assert
    which scans ran; the returned records ignore the images. *bundle*
    selects the family whose callables are stubbed.
    """
    log = []
    runs_list, count_value, longest_value = run_lists

    def runs(candidate, reference, tolerance, flags=None):
        log.append("runs")
        return list(runs_list)

    def iter_runs(candidate, reference, tolerance, flags=None):
        log.append("iter_runs")
        return iter(runs_list)

    def run_count(candidate, reference, tolerance, flags=None):
        log.append("run_count")
        return count_value

    def longest_run(candidate, reference, tolerance, flags=None):
        log.append("longest_run")
        return longest_value

    return log, bundle._replace(
        runs=runs, iter_runs=iter_runs, run_count=run_count,
        longest_run=longest_run)


class TestCollectRunFamily(unittest.TestCase):
    """The recipe's routing, read from stubbed scans, not recomputed data."""

    def test_capped_family_pages_and_derives_count_and_longest_from_page(self):
        log, calls = _stub_calls(
            [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 3}],
            99, {"x": 9, "y": 0, "length": 8})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=True,
            minimum=1, maximum=7, cap=1, offset=1,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["iter_runs"])
        self.assertEqual(report.runs, [{"x": 1, "y": 0, "length": 3}])
        self.assertEqual(report.omitted, 1)
        self.assertEqual(report.count, 2)
        self.assertEqual(report.longest, {"x": 1, "y": 0, "length": 3})

    def test_none_offset_acts_as_zero(self):
        # The offset option is None when it was not given; the family
        # assembly treats None as 0 instead of making every caller coerce.
        log, calls = _stub_calls(
            [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 3}],
            99, {"x": 9, "y": 0, "length": 8})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=True,
            minimum=None, maximum=None, cap=None, offset=None,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["runs"])
        self.assertEqual(report.runs, [{"x": 0, "y": 0, "length": 1},
                                       {"x": 1, "y": 0, "length": 3}])
        self.assertIsNone(report.omitted)
        self.assertEqual(report.count, 2)
        self.assertEqual(report.longest, {"x": 1, "y": 0, "length": 3})

        log, calls = _stub_calls(
            [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 3}],
            99, {"x": 9, "y": 0, "length": 8})
        capped = collect_run_family(
            None, None, 0, None, calls, enabled=True,
            minimum=None, maximum=None, cap=2, offset=None,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["iter_runs"])
        self.assertEqual(capped.runs, report.runs)
        self.assertEqual(capped.count, report.count)
        self.assertEqual(capped.longest, report.longest)
        # A capped page always reports omitted, so an empty page is 0.
        self.assertEqual(capped.omitted, 0)

    def test_uncapped_family_scans_once_and_filters_the_list(self):
        log, calls = _stub_calls(
            [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 3},
             {"x": 2, "y": 0, "length": 2}],
            99, {"x": 9, "y": 0, "length": 8})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=True,
            minimum=2, maximum=None, cap=None, offset=0,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["runs"])
        self.assertEqual(report.runs, [{"x": 1, "y": 0, "length": 3},
                                       {"x": 2, "y": 0, "length": 2}])
        self.assertIsNone(report.omitted)
        self.assertEqual(report.count, 3)
        self.assertEqual(report.longest, {"x": 1, "y": 0, "length": 3})

    def test_count_and_longest_scan_on_their_own_without_the_list(self):
        log, calls = _stub_calls([], 7, {"x": 3, "y": 0, "length": 4})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=False,
            minimum=None, maximum=None, cap=None, offset=0,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["run_count", "longest_run"])
        self.assertIsNone(report.runs)
        self.assertIsNone(report.omitted)
        self.assertEqual(report.count, 7)
        self.assertEqual(report.longest, {"x": 3, "y": 0, "length": 4})

    def test_disabled_family_without_count_or_longest_runs_no_scan(self):
        log, calls = _stub_calls([], 7, {"x": 3, "y": 0, "length": 4})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=False,
            minimum=None, maximum=None, cap=None, offset=0,
            wants_count=False, wants_longest=False)
        self.assertEqual(log, [])
        self.assertIsNone(report.runs)
        self.assertIsNone(report.omitted)
        self.assertIsNone(report.count)
        self.assertIsNone(report.longest)

    def test_count_is_pre_filter_and_longest_is_unfiltered(self):
        log, calls = _stub_calls(
            [{"x": 0, "y": 0, "length": 1}, {"x": 1, "y": 0, "length": 5},
             {"x": 2, "y": 0, "length": 3}],
            99, {"x": 9, "y": 0, "length": 8})
        report = collect_run_family(
            None, None, 0, None, calls, enabled=True,
            minimum=3, maximum=5, cap=None, offset=0,
            wants_count=True, wants_longest=True)
        self.assertEqual(log, ["runs"])
        self.assertEqual(report.count, 3)
        self.assertEqual(report.longest, {"x": 1, "y": 0, "length": 5})
        self.assertEqual(report.runs, [{"x": 1, "y": 0, "length": 5},
                                       {"x": 2, "y": 0, "length": 3}])
        self.assertIsNone(report.omitted)

    def test_column_family_uses_the_same_recipe_with_its_own_callables(self):
        expected = _runs(2)
        column_log, column_calls = _stub_calls(
            expected, 5, expected[0], bundle=COLUMN_RUN_CALLS)
        horizontal_log, horizontal_calls = _stub_calls(
            expected, 5, expected[0])
        column = collect_run_family(
            None, None, 0, None, column_calls, enabled=True,
            minimum=None, maximum=None, cap=None, offset=0,
            wants_count=True, wants_longest=True)
        horizontal = collect_run_family(
            None, None, 0, None, horizontal_calls, enabled=True,
            minimum=None, maximum=None, cap=None, offset=0,
            wants_count=True, wants_longest=True)
        self.assertEqual(column, horizontal)
        self.assertEqual(column_log, ["runs"])
        self.assertEqual(horizontal_log, ["runs"])


if __name__ == "__main__":
    unittest.main()

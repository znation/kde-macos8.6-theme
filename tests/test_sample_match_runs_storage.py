"""The horizontal match-run collector retains only the requested page."""

import unittest

from support import repo_root  # noqa: F401
from tools.sample_match_runs import MatchRuns


class TestMatchRunsStorage(unittest.TestCase):

    def test_capped_collector_bounds_retained_runs_during_scan_and_final_flush(self):
        collector = MatchRuns(10, 4, 39, 1, horizontal=True, vertical=False,
                               run_limit=3, run_offset=12)
        for relative_x in range(39):
            collector.observe(10 + relative_x, 4, relative_x % 2 == 0)
            assert len(collector.runs) <= 3

        runs, _ = collector.finish()

        assert runs == [{"x": 34, "y": 4, "length": 1},
                        {"x": 36, "y": 4, "length": 1},
                        {"x": 38, "y": 4, "length": 1}]
        assert collector.eligible_run_count == 20
        assert len(collector.runs) == 3

    def test_cutoffs_count_skipped_and_trailing_eligible_runs_without_retaining_them(self):
        collector = MatchRuns(0, 0, 11, 1, horizontal=True, vertical=False,
                               min_run_length=2, run_limit=1, run_offset=1)
        matches = {0, 2, 3, 5, 6, 7, 9, 10}
        for x in range(11):
            collector.observe(x, 0, x in matches)

        runs, _ = collector.finish()

        assert runs == [{"x": 5, "y": 0, "length": 3}]
        assert collector.eligible_run_count == 3


if __name__ == "__main__":
    unittest.main()

"""Dispatch tests for the reference pixel sampler's report modes."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

from support import repo_root  # noqa: F401
from tools import sample_reports


class TestReportDispatch(unittest.TestCase):
    """The report dispatcher's mode selection and precedence."""

    def test_runs_takes_precedence_and_returns(self):
        args = SimpleNamespace(runs=True, histogram=True, find_color="#010203")
        image = object()
        with (mock.patch.object(sample_reports, "report_runs") as runs,
              mock.patch.object(sample_reports, "report_histogram") as histogram,
              mock.patch.object(sample_reports, "report_search") as search,
              mock.patch.object(sample_reports, "report_pixels") as pixels):
            sample_reports.report(args, image, 17, 9, "header")

        runs.assert_called_once_with(args, image, 17, 9, "header")
        histogram.assert_not_called()
        search.assert_not_called()
        pixels.assert_not_called()

    def test_histogram_dispatches_before_search(self):
        args = SimpleNamespace(runs=False, histogram=True, find_color="#010203")
        image = object()
        with (mock.patch.object(sample_reports, "report_runs") as runs,
              mock.patch.object(sample_reports, "report_histogram") as histogram,
              mock.patch.object(sample_reports, "report_search") as search,
              mock.patch.object(sample_reports, "report_pixels") as pixels):
            sample_reports.report(args, image, 17, 9, "header")

        runs.assert_not_called()
        histogram.assert_called_once_with(args, image, 17, 9, "header")
        search.assert_not_called()
        pixels.assert_not_called()

    def test_search_dispatches_when_color_is_requested(self):
        args = SimpleNamespace(runs=False, histogram=False, find_color="#010203")
        image = object()
        with (mock.patch.object(sample_reports, "report_runs") as runs,
              mock.patch.object(sample_reports, "report_histogram") as histogram,
              mock.patch.object(sample_reports, "report_search") as search,
              mock.patch.object(sample_reports, "report_pixels") as pixels):
            sample_reports.report(args, image, 17, 9, "header")

        runs.assert_not_called()
        histogram.assert_not_called()
        search.assert_called_once_with(args, image, 17, 9, "header")
        pixels.assert_not_called()

    def test_pixel_report_is_the_default(self):
        args = SimpleNamespace(runs=False, histogram=False, find_color=None)
        image = object()
        with (mock.patch.object(sample_reports, "report_runs") as runs,
              mock.patch.object(sample_reports, "report_histogram") as histogram,
              mock.patch.object(sample_reports, "report_search") as search,
              mock.patch.object(sample_reports, "report_pixels") as pixels):
            sample_reports.report(args, image, 17, 9, "header")

        runs.assert_not_called()
        histogram.assert_not_called()
        search.assert_not_called()
        pixels.assert_called_once_with(args, image, 17, 9, "header")


if __name__ == "__main__":
    unittest.main()

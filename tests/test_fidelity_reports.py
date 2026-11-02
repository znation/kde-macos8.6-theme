"""Tests for tools/fidelity_reports.py's report assembly and rendering.

The module holds the comparison report's shape -- the budget-to-verdict
rule, the source-position translation, the JSON object and the text lines --
while ``tools/fidelity.py`` reads and compares. These tests drive the report
functions with explicit values (metrics records, hand-built worst records,
images built by the fixtures), so each pins one rendering decision without
exercising the reads or the comparison the CLI is otherwise covered by.
"""

from __future__ import annotations

import json
import unittest

from support import repo_root  # noqa: F401
from support.png_fixtures import solid_rgb  # noqa: E402
from tools.fidelity_metrics import Image, Metrics, compare  # noqa: E402
from tools.fidelity_reports import (  # noqa: E402
    budget_verdict,
    locate_worst_pixels,
    report_data,
    render_json,
    render_text,
    source_bounds,
)


def _metrics(**overrides) -> Metrics:
    """Return a Metrics record with explicit RGB-only no-difference fields.

    Any field named in *overrides* takes its place, so a test states only
    the values the expectation under test depends on.
    """
    values = dict(
        width=2, height=2, pixels=4, mae=0.0, mae_r=0.0, mae_g=0.0, mae_b=0.0,
        rmse=0.0, max_delta=0, max_x=0, max_y=0, differing=0, frac_differing=0.0,
    )
    values.update(overrides)
    return Metrics(**values)


class TestBudgetVerdict(unittest.TestCase):
    def test_without_a_budget_the_default_gate_requires_no_differing_pixel(self):
        self.assertTrue(budget_verdict(_metrics()))
        self.assertFalse(budget_verdict(_metrics(frac_differing=0.5)))

    def test_an_aggregate_budget_replaces_the_default_gate(self):
        # A wide per-pixel union (frac 1.0) passes under a met MAE budget:
        # the default no-differing-pixel gate is not still applied.
        self.assertTrue(budget_verdict(_metrics(mae=1.0), max_mae=2.0))
        self.assertFalse(budget_verdict(_metrics(mae=3.0), max_mae=2.0))

    def test_a_budget_on_the_boundary_is_met(self):
        self.assertTrue(budget_verdict(_metrics(mae=2.0), max_mae=2.0))
        self.assertTrue(budget_verdict(_metrics(frac_differing=0.5), max_frac=0.5))

    def test_every_set_budget_must_be_met(self):
        self.assertTrue(budget_verdict(_metrics(mae=1.0, frac_differing=0.4),
                                       max_mae=2.0, max_frac=0.5))
        self.assertFalse(budget_verdict(_metrics(mae=1.0, frac_differing=0.6),
                                        max_mae=2.0, max_frac=0.5))
        self.assertFalse(budget_verdict(_metrics(mae=3.0, frac_differing=0.4),
                                        max_mae=2.0, max_frac=0.5))


class TestSourceBounds(unittest.TestCase):
    def test_absent_bounds_stay_none(self):
        self.assertIsNone(source_bounds(None, (1, 2, 3, 4)))

    def test_a_rectangle_translates_by_the_crop_origin(self):
        self.assertEqual(source_bounds((1, 2, 3, 4), (10, 20, 3, 4)),
                         [11, 22, 3, 4])

    def test_an_omitted_crop_has_origin_zero(self):
        self.assertEqual(source_bounds((1, 2, 3, 4), None), [1, 2, 3, 4])


class TestLocateWorstPixels(unittest.TestCase):
    def test_positions_add_the_crop_origins(self):
        records = [{"x": 1, "y": 0}, {"x": 0, "y": 2}]
        located = locate_worst_pixels(records, (10, 20, 3, 4), (5, 6, 3, 4))
        self.assertEqual(located[0]["candidate_position"], [11, 20])
        self.assertEqual(located[0]["reference_position"], [6, 6])
        self.assertEqual(located[1]["candidate_position"], [10, 22])
        self.assertEqual(located[1]["reference_position"], [5, 8])

    def test_an_omitted_crop_has_origin_zero_and_returns_the_records(self):
        records = [{"x": 1, "y": 2}]
        located = locate_worst_pixels(records, None, None)
        self.assertIs(located, records)
        self.assertEqual(located[0]["candidate_position"], [1, 2])
        self.assertEqual(located[0]["reference_position"], [1, 2])


class TestReportData(unittest.TestCase):
    def test_a_default_run_carries_no_optional_keys(self):
        data = report_data("candidate.png", "reference.png", None, None,
                           0, None, None, _metrics())
        self.assertEqual(list(data), [
            "candidate", "reference", "candidate_crop", "reference_crop",
            "thresholds", "metrics", "candidate_difference_bounds",
            "reference_difference_bounds", "passed",
        ])
        self.assertEqual(data["thresholds"],
                         {"tolerance": 0, "max_mae": None, "max_frac": None})
        self.assertEqual(data["candidate_crop"], None)
        self.assertEqual(data["candidate_difference_bounds"], None)
        self.assertIs(data["passed"], False)

    def test_the_requested_records_appear_only_when_requested(self):
        worst = [{"x": 1, "y": 0, "candidate_position": [1, 0],
                  "reference_position": [1, 0]}]
        data = report_data("c", "r", None, None, 5, 1.0, 0.5, _metrics(),
                           worst=worst, channels={"r": 1, "g": 0, "b": 0, "a": 0},
                           explanation={"position": [1, 0]}, passed=True)
        self.assertEqual(list(data)[-3:], ["channel_counts", "worst_pixels", "worst_pixel"])
        self.assertEqual(data["worst_pixels"], worst)
        self.assertEqual(data["channel_counts"], {"r": 1, "g": 0, "b": 0, "a": 0})
        self.assertEqual(data["worst_pixel"], {"position": [1, 0]})
        self.assertIs(data["passed"], True)

    def test_crop_bounds_translate_from_the_metrics_rectangle(self):
        metrics = _metrics(difference_bounds=(1, 2, 3, 4))
        data = report_data("c", "r", (10, 20, 3, 4), None, 0, None, None, metrics)
        self.assertEqual(data["candidate_difference_bounds"], [11, 22, 3, 4])
        self.assertEqual(data["reference_difference_bounds"], [1, 2, 3, 4])


class TestRenderJson(unittest.TestCase):
    def test_the_line_is_ascii_escaped_json(self):
        data = report_data("café.png", "reference.png", None, None,
                           0, None, None, _metrics())
        self.assertEqual(render_json(data), json.dumps(data, ensure_ascii=True))
        self.assertIn("caf\\u00e9.png", render_json(data))


class TestRenderText(unittest.TestCase):
    def test_identical_images_print_the_full_default_report(self):
        candidate, _ = solid_rgb(2, 2)
        data = report_data("candidate.png", "reference.png", None, None,
                           0, None, None, compare(candidate, candidate), passed=True)
        self.assertEqual(
            render_text(data, candidate, candidate),
            [
                "candidate: candidate.png  2x2",
                "reference: reference.png  2x2",
                "pixels compared: 4",
                "mean absolute error: 0.0000",
                "per-channel MAE (R, G, B): 0.0000 0.0000 0.0000",
                "RMSE: 0.0000",
                "max channel delta: 0 at (0, 0)",
                "differing pixels: 0 / 4 (0.000000)",
                "difference bounds: none",
                "candidate difference bounds: none",
                "reference difference bounds: none",
                "PASS: max-mae=unset max-frac=unset tolerance=0",
            ],
        )

    def test_a_compared_alpha_channel_prints_four_per_channel_values(self):
        candidate = Image(1, 1, bytes(3), bytes([200]))
        reference = Image(1, 1, bytes(3), bytes([255]))
        data = report_data("c", "r", None, None, 0, None, None,
                           compare(candidate, reference), passed=False)
        lines = render_text(data, candidate, reference)
        self.assertIn(
            "per-channel MAE (R, G, B, A): 0.0000 0.0000 0.0000 55.0000",
            lines,
        )
        self.assertEqual(lines[-1], "FAIL: max-mae=unset max-frac=unset tolerance=0")

    def test_crops_are_echoed_after_the_size_lines(self):
        candidate, _ = solid_rgb(1, 1)
        reference, _ = solid_rgb(1, 1)
        data = report_data("c", "r", (1, 2, 3, 4), (5, 6, 7, 8),
                           0, None, None, _metrics(width=3, height=4))
        lines = render_text(data, candidate, reference)
        self.assertEqual(lines[2], "candidate crop: 1,2,3,4")
        self.assertEqual(lines[3], "reference crop: 5,6,7,8")

    def test_a_difference_bounds_rect_prints_the_local_and_source_values(self):
        candidate, _ = solid_rgb(1, 1)
        reference, _ = solid_rgb(1, 1)
        data = report_data("c", "r", (10, 20, 4, 4), None, 0, None, None,
                           _metrics(difference_bounds=(1, 2, 3, 4)))
        lines = render_text(data, candidate, reference)
        self.assertIn("difference bounds: 1,2,3,4", lines)
        self.assertIn("candidate difference bounds: 11,22,3,4", lines)
        self.assertIn("reference difference bounds: 1,2,3,4", lines)

    def test_worst_records_print_the_rank_count_and_both_source_positions(self):
        candidate, _ = solid_rgb(1, 1)
        reference, _ = solid_rgb(1, 1)
        worst = locate_worst_pixels(
            [{"x": 1, "y": 0, "candidate_rgba": [30, 0, 0, 255],
              "reference_rgba": [0, 10, 2, 255], "max_delta": 30}],
            (10, 20, 3, 4), (5, 6, 3, 4),
        )
        data = report_data("c", "r", None, None, 0, None, None, _metrics(),
                           worst=worst, passed=False)
        self.assertIn(
            "pixel (1, 0): candidate=30,0,0,255 reference=0,10,2,255 "
            "max_delta=30 candidate_position=11,20 reference_position=6,6",
            render_text(data, candidate, reference),
        )

    def test_the_worst_explanation_prints_before_the_verdict_as_json(self):
        candidate, _ = solid_rgb(1, 1)
        reference, _ = solid_rgb(1, 1)
        explanation = {"position": [0, 0], "absolute_delta": [1, 2, 3, 0]}
        data = report_data("c", "r", None, None, 0, None, None, _metrics(),
                           explanation=explanation, passed=True)
        last = render_text(data, candidate, reference)[-2:]
        self.assertEqual(last[0], "worst pixel: " + json.dumps(explanation, ensure_ascii=True))
        self.assertEqual(last[1], "PASS: max-mae=unset max-frac=unset tolerance=0")

    def test_channel_counts_print_one_line_before_the_verdict(self):
        candidate, _ = solid_rgb(1, 1)
        reference, _ = solid_rgb(1, 1)
        data = report_data("c", "r", None, None, 0, None, None, _metrics(),
                           channels={"r": 1, "g": 0, "b": 2, "a": 0}, passed=False)
        last = render_text(data, candidate, reference)[-2:]
        self.assertEqual(last[0], "channel differing pixels (R, G, B, A): 1 0 2 0")
        self.assertEqual(last[1], "FAIL: max-mae=unset max-frac=unset tolerance=0")

    def test_threshold_budgets_print_in_the_verdict_line(self):
        candidate, _ = solid_rgb(2, 2)
        reference, _ = solid_rgb(2, 2)
        data = report_data("c", "r", None, None, 7, 1.5, 0.25,
                           compare(candidate, candidate), passed=True)
        self.assertEqual(render_text(data, candidate, reference)[-1],
                         "PASS: max-mae=1.5000 max-frac=0.250000 tolerance=7")


if __name__ == "__main__":
    unittest.main()

"""Tests for fidelity report assembly and rendering.

The report's shape -- the budget-to-verdict rule and the
source-position translation -- lives in ``tools/fidelity_reports.py``,
its text and JSON rendering in ``tools/fidelity_rendering.py``, while
``tools/fidelity.py`` reads and compares. These tests drive the report
functions with explicit values (metrics records, hand-built worst records,
images built by the fixtures), so each pins one rendering decision without
exercising the reads or the comparison the CLI is otherwise covered by.
"""

from __future__ import annotations

import copy
import json
import unittest

from support import repo_root  # noqa: F401
from support.png_fixtures import solid_rgb  # noqa: E402
from tools.fidelity_metrics import Image, Metrics, compare  # noqa: E402
from tools.fidelity_reports import (  # noqa: E402
    budget_verdict,
    locate_worst_pixels,
    report_data,
    source_bounds,
)
from tools.fidelity_rendering import render_json, render_text  # noqa: E402


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
    """Test comparison verdicts with and without metric budgets."""
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

    def test_rmse_and_max_delta_budgets_must_each_be_met(self):
        metrics = _metrics(rmse=2.5, max_delta=7)
        self.assertTrue(budget_verdict(metrics, max_rmse=2.5, max_delta=7))
        self.assertFalse(budget_verdict(metrics, max_rmse=2.4, max_delta=7))
        self.assertFalse(budget_verdict(metrics, max_rmse=2.5, max_delta=6))


class TestSourceBounds(unittest.TestCase):
    """Test translation of crop-relative bounds to source coordinates."""
    def test_absent_bounds_stay_none(self):
        self.assertIsNone(source_bounds(None, (1, 2, 3, 4)))

    def test_a_rectangle_translates_by_the_crop_origin(self):
        self.assertEqual(source_bounds((1, 2, 3, 4), (10, 20, 3, 4)),
                         [11, 22, 3, 4])

    def test_an_omitted_crop_has_origin_zero(self):
        self.assertEqual(source_bounds((1, 2, 3, 4), None), [1, 2, 3, 4])


class TestLocateWorstPixels(unittest.TestCase):
    """Test translation of ranked pixel positions to source coordinates."""
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
    """Test mapping optional diagnostics into report data."""
    def test_optional_diagnostics_map_each_keyword_to_its_output_key(self):
        diagnostics = (
            ("channels", "channel_counts", {"r": 1}),
            ("bias", "channel_bias", {"r": -1.0}),
            ("maxima", "channel_maxima", {"r": 1}),
            ("rows", "difference_rows", [1]),
            ("columns", "difference_columns", [1]),
            ("row_bounds", "difference_row_bounds", [[0, 1]]),
            ("column_bounds", "difference_column_bounds", [[0, 1]]),
            ("runs", "difference_runs", [[0, 1]]),
            ("column_runs", "difference_column_runs", [[0, 1]]),
            ("histogram", "delta_histogram", [{"delta": 1, "count": 1}]),
            ("percentiles", "delta_percentiles", {"p50": 1}),
            ("worst", "worst_pixels", [{"x": 0, "y": 0}]),
            ("explanation", "worst_pixel", {"position": [0, 0]}),
        )
        optional_keys = {output_key for _, output_key, _ in diagnostics}
        for keyword, output_key, value in diagnostics:
            with self.subTest(keyword=keyword):
                data = report_data("c", "r", None, None, 0, None, None,
                                   _metrics(), **{keyword: value})
                self.assertEqual(data[output_key], value)
                self.assertIs(data[output_key], value)
                self.assertEqual(optional_keys.intersection(data), {output_key})

    def test_none_omits_diagnostics_but_empty_collections_are_present(self):
        diagnostics = (
            ("channels", "channel_counts", {}),
            ("bias", "channel_bias", {}),
            ("rows", "difference_rows", []),
            ("histogram", "delta_histogram", []),
        )
        for keyword, output_key, empty_value in diagnostics:
            with self.subTest(keyword=keyword, value="None"):
                data = report_data("c", "r", None, None, 0, None, None,
                                   _metrics(), **{keyword: None})
                self.assertNotIn(output_key, data)
            with self.subTest(keyword=keyword, value="empty"):
                data = report_data("c", "r", None, None, 0, None, None,
                                   _metrics(), **{keyword: empty_value})
                self.assertIn(output_key, data)
                self.assertIs(data[output_key], empty_value)

    def test_combined_diagnostics_keep_mapping_order_and_nested_values(self):
        diagnostics = (
            ("channels", "channel_counts", {"r": 1}),
            ("bias", "channel_bias", {"r": -1.0}),
            ("maxima", "channel_maxima", {"r": 1}),
            ("rows", "difference_rows", [1]),
            ("columns", "difference_columns", [2]),
            ("row_bounds", "difference_row_bounds", [[0, 1]]),
            ("column_bounds", "difference_column_bounds", [[0, 2]]),
            ("runs", "difference_runs", [[0, 1]]),
            ("column_runs", "difference_column_runs", [[0, 2]]),
            ("histogram", "delta_histogram", [{"delta": 1, "count": 1}]),
            ("percentiles", "delta_percentiles", {"p50": 1}),
            ("worst", "worst_pixels", [{"x": 0, "y": 0}]),
            ("explanation", "worst_pixel", {"position": [0, 0]}),
        )
        original = [(keyword, output_key, copy.deepcopy(value))
                    for keyword, output_key, value in diagnostics]
        data = report_data("c", "r", None, None, 0, None, None, _metrics(),
                           **{keyword: value for keyword, _, value in diagnostics})
        self.assertEqual([key for key in data if key in {k for _, k, _ in diagnostics}],
                         [output_key for _, output_key, _ in diagnostics])
        for keyword, output_key, value in diagnostics:
            with self.subTest(keyword=keyword):
                self.assertEqual(value, next(copy for name, key, copy in original
                                              if name == keyword and key == output_key))
                self.assertIs(data[output_key], value)

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
    """Test JSON serialization of fidelity report data."""
    def test_the_line_is_ascii_escaped_json(self):
        data = report_data("café.png", "reference.png", None, None,
                           0, None, None, _metrics())
        self.assertEqual(render_json(data), json.dumps(data, ensure_ascii=True))
        self.assertIn("caf\\u00e9.png", render_json(data))

    def test_exact_default_json_serialization(self):
        data = {
            "candidate": "c\x1bafé.png", "reference": "r.png",
            "candidate_crop": None, "reference_crop": None,
            "thresholds": {"tolerance": 0, "max_mae": None, "max_frac": None},
            "metrics": {"width": 1, "height": 1},
            "candidate_difference_bounds": None,
            "reference_difference_bounds": None, "passed": True,
        }
        self.assertEqual(
            render_json(data),
            '{"candidate": "c\\u001baf\\u00e9.png", "reference": "r.png", '
            '"candidate_crop": null, "reference_crop": null, "thresholds": '
            '{"tolerance": 0, "max_mae": null, "max_frac": null}, "metrics": '
            '{"width": 1, "height": 1}, "candidate_difference_bounds": null, '
            '"reference_difference_bounds": null, "passed": true}',
        )


class TestRenderText(unittest.TestCase):
    """Test text rendering of fidelity report data."""
    def test_renderer_needs_only_dimensions_and_does_not_mutate_input(self):
        class Size:
            width = 1
            height = 1

        candidate = Size()
        data = {
            "candidate": "c\x1bafé", "reference": "r",
            "candidate_crop": None, "reference_crop": None,
            "metrics": {"pixels": 1, "mae": 0.0, "mae_r": 0.0,
                        "mae_g": 0.0, "mae_b": 0.0, "mae_a": None,
                        "rmse": 0.0, "max_delta": 0, "max_x": 0, "max_y": 0,
                        "differing": 0, "frac_differing": 0.0,
                        "difference_bounds": None},
            "candidate_difference_bounds": None,
            "reference_difference_bounds": None,
            "thresholds": {"tolerance": 0, "max_mae": None, "max_frac": None},
            "passed": True,
        }
        original = {key: value.copy() if isinstance(value, dict) else value
                    for key, value in data.items()}
        lines = render_text(data, candidate, candidate)
        self.assertEqual(lines[0], "candidate: c\\u001bafé  1x1")
        self.assertEqual(lines[-1], "PASS: max-mae=unset max-frac=unset tolerance=0")
        self.assertEqual(data, original)

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

    def test_rmse_delta_and_differing_budgets_print_in_order_before_tolerance(self):
        candidate, _ = solid_rgb(2, 2)
        reference, _ = solid_rgb(2, 2)
        data = report_data("c", "r", None, None, 0, None, None,
                           compare(candidate, candidate), passed=False,
                           max_rmse=1.5, max_delta=9, max_differing=3)
        self.assertEqual(render_text(data, candidate, reference)[-1],
                         "FAIL: max-mae=unset max-frac=unset max-rmse=1.5000 "
                         "max-delta=9 max-differing=3 tolerance=0")

    def test_a_lone_delta_budget_prints_its_own_segment(self):
        candidate, _ = solid_rgb(2, 2)
        reference, _ = solid_rgb(2, 2)
        data = report_data("c", "r", None, None, 0, None, None,
                           compare(candidate, candidate), passed=True,
                           max_delta=9)
        self.assertEqual(render_text(data, candidate, reference)[-1],
                         "PASS: max-mae=unset max-frac=unset max-delta=9 tolerance=0")


if __name__ == "__main__":
    unittest.main()

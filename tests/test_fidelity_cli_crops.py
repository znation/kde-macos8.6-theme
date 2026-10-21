"""Tests for the fidelity CLI's crop options in tools/fidelity.py.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v

``--crop`` and ``--candidate-crop`` select a region of the reference and the
candidate before comparison; this module pins their pass/fail verdicts, their
reproducibility echo and their usage errors. The shared fixtures live in
``support.fidelity_cli_case``.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import make_png, rgb_image  # noqa: E402
from tools import fidelity, png  # noqa: E402


class TestCliCrops(FidelityCliTestCase):
    """The ``--crop`` and ``--candidate-crop`` options."""

    def test_crop_region_passes(self):
        tmp = self._tmp_dir()
        candidate, reference = self._write_padded_surface_pair(tmp)
        result = self._run(candidate, reference, "--crop", "1,1,2,2")
        self._assert_pass(result)

    def test_crop_rectangle_is_echoed_for_reproducibility(self):
        # The reference line prints the cropped size, which does not say where
        # the crop came from, so a transcript cannot be replayed without the
        # rectangle. A run without --crop must not print the line at all.
        reference = self._solid_reference()
        uncropped = self._run(reference, reference)
        tmp = self._tmp_dir()
        candidate, padded = self._write_padded_surface_pair(tmp)
        cropped = self._run(candidate, padded, "--crop", "1,1,2,2")
        self._assert_success(cropped)
        self.assertIn("reference crop: 1,1,2,2", cropped.stdout)
        self._assert_success(uncropped)
        self.assertNotIn("reference crop:", uncropped.stdout)

    def test_a_crop_decodes_only_the_rows_it_covers(self):
        # The crop slices the decoded rows anyway, so reading the whole image
        # first wastes the decoder's predictor work on every row below the
        # crop. A --crop reads the reference to its bottom edge and leaves the
        # candidate unbounded; --candidate-crop does the reverse.
        tmp = self._tmp_dir()
        surface, padded = self._write_padded_surface_pair(tmp)
        for option, candidate, reference, bounded, other in (
            ("--crop", surface, padded, padded, surface),
            ("--candidate-crop", padded, surface, padded, surface),
        ):
            with self.subTest(option=option):
                with mock.patch.object(
                    fidelity, "read_png", wraps=png.read_png
                ) as spy:
                    result = self._run(candidate, reference, option, "1,1,2,2")
                self._assert_pass(result)
                rows = {
                    call.args[0]: call.kwargs.get("max_rows")
                    for call in spy.call_args_list
                }
                # The crop's bottom edge is y=1 + height=2, so three rows.
                self.assertEqual(rows[bounded], 3)
                self.assertIsNone(rows[other])

    def test_a_crop_still_rejects_a_palette_index_below_it(self):
        # max_rows bounds the returned rows, not validation: a palette
        # reference whose bad index is below the crop is malformed, not a
        # clean comparison of the top rows.
        palette = bytes([255, 0, 0, 0, 255, 0])
        reference = make_png(
            2,
            3,
            [bytes([0, 1]), bytes([0, 1]), bytes([2, 2])],
            color_type=3,
            palette=palette,
        )
        _, candidate = rgb_image(
            2, 2, lambda x, y: (255, 0, 0) if x == 0 else (0, 255, 0)
        )
        tmp = self._tmp_dir()
        result = self._run(
            self._write(tmp, "candidate.png", candidate),
            self._write(tmp, "reference.png", reference),
            "--crop",
            "0,0,2,2",
        )
        self._assert_usage_error(result, "palette PNG index 2")

    def test_a_sideways_overflow_is_reported_against_the_real_height(self):
        # The bounded decode shortens the returned height, but a rectangle
        # that overflows the width while fitting vertically must still name
        # the file's real dimensions in its diagnostic.
        tmp = self._tmp_dir()
        _, data = rgb_image(2, 3, lambda x, y: (x * 9, y * 9, 5))
        path = self._write(tmp, "image.png", data)
        for option in ("--crop", "--candidate-crop"):
            with self.subTest(option=option):
                result = self._run(path, path, option, "1,0,2,2")
                self._assert_usage_error(
                    result, "falls outside the 2x3 image"
                )

    def test_a_vertical_overflow_is_reported_against_the_real_height(self):
        # A crop that fits horizontally but runs past the bottom edge asks
        # _read_source for more rows than the image has. The decoder clamps
        # that bound, so the returned image keeps its real height and crop()
        # rejects the rectangle. If the bound were not clamped, the rectangle
        # would fit the over-long image and the run would silently pass.
        tmp = self._tmp_dir()
        _, data = rgb_image(2, 3, lambda x, y: (x * 9, y * 9, 5))
        path = self._write(tmp, "image.png", data)
        for option in ("--crop", "--candidate-crop"):
            with self.subTest(option=option):
                result = self._run(path, path, option, "0,1,2,3")
                self._assert_usage_error(
                    result, "falls outside the 2x3 image"
                )

    def test_crop_accepts_whitespace_between_fields(self):
        # A comma-separated rectangle is conventionally written with a space
        # after each comma ("0, 0, 10, 10"); that whitespace is formatting,
        # not a value, so --crop must accept it. The scalar options still
        # reject surrounding whitespace (test_python_literal_numeric_args_rejected).
        tmp = self._tmp_dir()
        candidate, reference = self._write_padded_surface_pair(tmp)
        tight = self._run(candidate, reference, "--crop", "1,1,2,2")
        spaced = self._run(candidate, reference, "--crop", "1, 1, 2, 2")
        self._assert_success(tight)
        self._assert_success(spaced)
        # Identical output proves the spaced form selects the same rectangle.
        self.assertEqual(spaced.stdout, tight.stdout)

    def test_candidate_crop_region_passes(self):
        # The padded image is the candidate and the embedded surface is the
        # reference, so --candidate-crop trims the candidate to the 2x2 the
        # reference already is; the two are then byte-identical.
        tmp = self._tmp_dir()
        surface, padded = self._write_padded_surface_pair(tmp)
        result = self._run(padded, surface, "--candidate-crop", "1,1,2,2")
        self._assert_pass(result)

    def test_candidate_and_reference_crops_apply_together(self):
        # The render gate crops a strip from the candidate and the matching
        # strip from the reference in one run, so both options must trim their
        # own image. The candidate's surface sits at (1, 1) and the reference's
        # at (2, 2), so a pass proves each crop selected the surface.
        tmp = self._tmp_dir()
        _, candidate = self._write_padded_surface_pair(tmp)
        reference = self._write(
            tmp, "reference.png", self._padded_surface_png(5, 5, 2, 2)
        )
        result = self._run(
            candidate,
            reference,
            "--candidate-crop",
            "1,1,2,2",
            "--crop",
            "2,2,2,2",
        )
        self._assert_pass(result)
        self.assertIn("candidate crop: 1,1,2,2", result.stdout)
        self.assertIn("reference crop: 2,2,2,2", result.stdout)

    def test_candidate_crop_rectangle_is_echoed_for_reproducibility(self):
        # The candidate line prints the cropped size, which does not say where
        # the crop came from, so a transcript cannot be replayed without the
        # rectangle. A run without --candidate-crop must not print the line.
        tmp = self._tmp_dir()
        surface, padded = self._write_padded_surface_pair(tmp)
        cropped = self._run(padded, surface, "--candidate-crop", "1,1,2,2")
        self._assert_success(cropped)
        self.assertIn("candidate crop: 1,1,2,2", cropped.stdout)
        uncropped = self._run(surface, surface)
        self._assert_success(uncropped)
        self.assertNotIn("candidate crop:", uncropped.stdout)

    def test_candidate_crop_outside_candidate_is_error(self):
        # A candidate crop with valid syntax can still fall outside the
        # candidate; crop() raises FidelityError and main() must report it at
        # exit 2, not crash.
        self._assert_outside_crop_is_error("--candidate-crop", "candidate.png")

    def test_malformed_candidate_crop_is_usage_error(self):
        # A bad --candidate-crop must be rejected as a usage error before
        # either image is read, naming the option and the offending value.
        tmp = self._tmp_dir()
        missing = str(tmp / "missing.png")
        result = self._run(missing, missing, "--candidate-crop", "1,2,3")
        self._assert_usage_error(
            result, "1,2,3", "argument --candidate-crop:"
        )

    def test_crop_outside_reference_is_error(self):
        # A crop with valid syntax can still fall outside the reference; crop()
        # raises FidelityError and main() must report it at exit 2, not crash.
        self._assert_outside_crop_is_error("--crop", "reference.png")

    def test_malformed_crop_is_usage_error(self):
        # A bad --crop must be rejected as a usage error before either image is
        # read, and the message must name the offending value so the user does
        # not have to re-derive which field was wrong. Both paths are
        # nonexistent: a crop that reached the comparison would instead fail as
        # a read error, without argparse's "argument --crop:" prefix.
        tmp = self._tmp_dir()
        missing = str(tmp / "missing.png")
        base = [missing, missing]
        for extra, expected in (
            (["--crop", "1,2,3"], "1,2,3"),
            (["--crop", "a,2,3,4"], "'a'"),
            (["--crop", "1,,3,4"], "field 2 is empty"),
            (["--crop", "1, ,3,4"], "field 2 is empty"),
            (["--crop", "0,0,0,2"], "x=0 y=0 w=0 h=2"),
            (["--crop=-1,0,2,2"], "x=-1 y=0 w=2 h=2"),
        ):
            with self.subTest(extra=extra):
                result = self._run(*base, *extra)
                self._assert_usage_error(
                    result, expected, "argument --crop:"
                )

if __name__ == "__main__":
    unittest.main()

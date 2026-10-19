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

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402


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

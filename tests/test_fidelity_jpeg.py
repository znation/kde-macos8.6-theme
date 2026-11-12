"""The fidelity CLI's JPEG branch: one convert decode before the comparison.

``tools/fidelity.py`` refuses every non-PNG input, but the reference set
ships JPEG screenshots. This module pins the loader's bridge reuse: a JPEG
candidate or reference is sniffed, decoded once through ImageMagick into a
private temporary PNG (``tools/jpeg_convert.py``), and read exactly like
any PNG input, while PNG inputs never convert and every diagnostic names
the paths the operator gave, never the temporary decode. The lossy decode
is never pinned by pixel value: identical inputs decode identically on any
``convert`` build, so the self-comparison must report zero differences
whatever the decoder writes.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support.repo_root import ROOT  # noqa: F401  (puts root on sys.path)
from support.fidelity_cli_case import FidelityCliTestCase
from support.jpeg_sampler_fixture import QUILT_HEIGHT, QUILT_JPEG, QUILT_WIDTH
from support.png_fixtures import solid_rgb
from tools import fidelity_sources, jpeg_convert


class TestJpegFidelity(FidelityCliTestCase):
    """The JPEG branch's end-to-end comparisons against the shared fixture."""

    def _jpeg_pair(self, name: str = "quilt.jpg") -> tuple[str, str]:
        """Write two copies of the fixture JPEG and return their paths."""
        directory = self._tmp_dir()
        candidate = self._write(directory, "candidate-" + name, QUILT_JPEG)
        reference = self._write(directory, "reference-" + name, QUILT_JPEG)
        return candidate, reference

    def test_script_entry_point(self):
        """The JPEG branch also runs end to end as ``python3 tools/fidelity.py``."""
        candidate, reference = self._jpeg_pair()
        result = self._run_script(candidate, reference)
        self._assert_success(result)
        self.assertEqual(
            result.stdout.splitlines()[:2],
            [
                f"candidate: {candidate}  {QUILT_WIDTH}x{QUILT_HEIGHT}",
                f"reference: {reference}  {QUILT_WIDTH}x{QUILT_HEIGHT}",
            ],
        )

    def test_self_comparison_reports_zero_differences(self):
        """Two copies of the fixture decode identically, so no pixel differs.

        The assertion pins zero metrics, not decoded pixel values: whatever
        ``convert`` writes for the fixture, both copies of the input go
        through the same decode, so the comparison is exact on any build.
        """
        candidate, reference = self._jpeg_pair()
        result = self._run(candidate, reference)
        self._assert_success(result)
        self.assertIn("PASS", result.stdout)
        self.assertIn(f"candidate: {candidate}  {QUILT_WIDTH}x{QUILT_HEIGHT}", result.stdout)
        self.assertIn(f"reference: {reference}  {QUILT_WIDTH}x{QUILT_HEIGHT}", result.stdout)
        self.assertIn("mean absolute error: 0.0000", result.stdout)
        self.assertIn("differing pixels: 0", result.stdout)
        # The private temporary decode must not leak into the report.
        self.assertNotIn("fidelity-jpeg-", result.stdout)
        self.assertNotIn("decoded.png", result.stdout)

    def test_out_of_bounds_crop_names_the_decoded_dimensions(self):
        """A crop past the decoded JPEG's size fails on the decoded geometry.

        The failure is the standing crop-rectangle refusal against the
        decoded image, so it pins the convert bridge's 32x24 output without
        pinning any lossy pixel value.
        """
        candidate, reference = self._jpeg_pair()
        result = self._run(candidate, reference, "--crop", "0,0,64,64")
        self._assert_usage_error(
            result, f"falls outside the {QUILT_WIDTH}x{QUILT_HEIGHT} image"
        )

    def test_within_bounds_crop_reports_the_empty_difference(self):
        """A within-bounds cropped JPEG pair compares like the same PNG pair."""
        candidate, reference = self._jpeg_pair()
        result = self._run(
            candidate,
            reference,
            "--candidate-crop",
            "0,0,16,8",
            "--crop",
            "0,0,16,8",
            "--difference-run-count",
        )
        self._assert_success(result)
        self.assertIn("difference run count: 0", result.stdout)


class TestJpegCallRouting(FidelityCliTestCase):
    """The branch routing: JPEG converts, PNG never converts."""

    def _png_pair(self) -> tuple[str, str]:
        """Write two identical PNGs and return their paths."""
        directory = self._tmp_dir()
        _, data = solid_rgb(2, 2)
        candidate = self._write(directory, "candidate.png", data)
        reference = self._write(directory, "reference.png", data)
        return candidate, reference

    def test_png_pair_never_enters_the_conversion_path(self):
        """A PNG comparison runs unchanged even if the converter would fire."""
        candidate, reference = self._png_pair()
        with mock.patch.object(
            jpeg_convert,
            "convert_jpeg",
            side_effect=AssertionError("PNG input converted"),
        ) as convert:
            result = self._run(candidate, reference)
        self._assert_success(result)
        self.assertIn("PASS", result.stdout)
        convert.assert_not_called()


class TestJpegFailureRoutes(FidelityCliTestCase):
    """The JPEG branch's failure diagnostics name the given paths only."""

    def _jpeg_pair(self, data: bytes = QUILT_JPEG) -> tuple[str, str]:
        """Write the same *data* as both sides of a comparison."""
        directory = self._tmp_dir()
        candidate = self._write(directory, "candidate.jpg", data)
        reference = self._write(directory, "reference.jpg", data)
        return candidate, reference

    def test_missing_convert_is_refused_before_any_decode(self):
        """Without ImageMagick's convert a JPEG side fails naming that side.

        ``main`` reads the candidate first, so a JPEG candidate is refused
        before the reference is opened; a PNG candidate over a JPEG
        reference reaches the same refusal on the reference side.
        """
        candidate, reference = self._jpeg_pair()
        with mock.patch.object(jpeg_convert.shutil, "which", return_value=None):
            result = self._run(candidate, reference)
        self._assert_usage_error(result, "convert", "ImageMagick")
        self.assertIn(candidate, result.stderr)
        self.assertEqual(result.stdout, "")

        _, png = solid_rgb(2, 2)
        png_path = self._write(self._tmp_dir(), "candidate.png", png)
        with mock.patch.object(jpeg_convert.shutil, "which", return_value=None):
            result = self._run(png_path, reference)
        self._assert_usage_error(result, "convert", "ImageMagick")
        self.assertIn(reference, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_truncated_jpeg_names_the_given_path_only(self):
        """A converter failure's diagnostic carries no private path.

        The failing side is compared both ways: a truncated candidate and,
        separately, a truncated reference, so each side's diagnostic is
        pinned to name the path the operator gave and nothing private.
        """
        truncated = QUILT_JPEG[: len(QUILT_JPEG) // 4] + b"garbage tail"
        for failing_index in (0, 1):
            with self.subTest(side=("candidate", "reference")[failing_index]):
                data = [QUILT_JPEG, QUILT_JPEG]
                data[failing_index] = truncated
                directory = self._tmp_dir()
                candidate = self._write(directory, "candidate.jpg", data[0])
                reference = self._write(directory, "reference.jpg", data[1])
                result = self._run(candidate, reference)
                self._assert_usage_error(result)
                failing_path = (candidate, reference)[failing_index]
                self.assertIn(failing_path, result.stderr)
                # None of the private scratch names may leak.
                self.assertNotIn("fidelity-jpeg-", result.stderr)
                self.assertNotIn("decoded.png", result.stderr)
                self.assertNotIn("magick-", result.stderr)

    def test_webp_head_keeps_the_standing_refusal(self):
        """A non-PNG non-JPEG head is refused exactly as before the bridge."""
        webp = b"RIFF\x24\x00\x00\x00WEBPVP8 " + bytes(range(32))
        candidate, reference = self._jpeg_pair(webp)
        result = self._run(candidate, reference)
        self._assert_usage_error(
            result,
            "cannot decode",
            "not a PNG file: the input is a WebP image, not a PNG; "
            "convert it to PNG first",
        )


class TestJpegSourcePolicy(unittest.TestCase):
    """The loader's own policy at the ``read_source`` boundary."""

    def test_repository_escape_is_refused_before_any_sniff_or_conversion(self):
        """A checked-in symlink that resolves outside the repo is refused."""
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            target = Path(directory) / "quilt.jpg"
            target.write_bytes(QUILT_JPEG)
            link = repo / "link.jpg"
            link.symlink_to(target)
            with (
                mock.patch.object(fidelity_sources, "ROOT", repo),
                mock.patch.object(fidelity_sources, "read_png") as read,
                mock.patch.object(jpeg_convert, "convert_jpeg") as convert,
                mock.patch.object(fidelity_sources, "is_jpeg") as sniff,
            ):
                with self.assertRaisesRegex(ValueError, "resolves outside"):
                    fidelity_sources.read_source(str(link), None)
        sniff.assert_not_called()
        convert.assert_not_called()
        read.assert_not_called()

    def test_external_jpeg_path_is_converted_and_read(self):
        """A path outside the repository goes through the bridge as before."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quilt.jpg"
            path.write_bytes(QUILT_JPEG)
            with mock.patch.object(fidelity_sources, "ROOT", Path(directory) / "repo"):
                image = fidelity_sources.read_source(str(path), None)
        self.assertEqual((image.width, image.height), (QUILT_WIDTH, QUILT_HEIGHT))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

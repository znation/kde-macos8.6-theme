"""Tests for tools/fidelity.py -- comparison metrics and the CLI.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import fidelity  # noqa: E402
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    make_png,
    rgb_image,
)

TOOL = REPO_ROOT / "tools" / "fidelity.py"


class TestCompare(unittest.TestCase):
    def test_identical_is_zero(self):
        image, _ = rgb_image(4, 4, lambda x, y: (x * 5, y * 5, 100))
        metrics = fidelity.compare(image, image)
        self.assertEqual(metrics.mae, 0.0)
        self.assertEqual(metrics.mae_r, 0.0)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertEqual(metrics.rmse, 0.0)
        self.assertEqual(metrics.max_delta, 0)
        self.assertEqual((metrics.max_x, metrics.max_y), (0, 0))
        self.assertEqual(metrics.differing, 0)
        self.assertEqual(metrics.frac_differing, 0.0)

    def test_single_pixel_difference(self):
        a, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[0] = 10  # one red channel on the first pixel
        b = fidelity.Image(a.width, a.height, bytes(changed))
        metrics = fidelity.compare(a, b)
        self.assertEqual(metrics.pixels, 4)
        self.assertAlmostEqual(metrics.mae, 10 / 12)
        self.assertAlmostEqual(metrics.mae_r, 10 / 4)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertAlmostEqual(metrics.rmse, (100 / 12) ** 0.5)
        self.assertEqual(metrics.max_delta, 10)
        self.assertEqual(metrics.differing, 1)
        self.assertEqual(metrics.frac_differing, 0.25)

    def test_per_channel_mae_locates_colour_cast(self):
        # A uniform bias in one channel must show up in that channel's MAE and
        # nowhere else, so a colour cast is distinguishable from per-pixel noise.
        a, _ = rgb_image(2, 2, lambda x, y: (10, 20, 30))
        cast = bytes(
            a.rgb[i] + (5 if i % 3 == 0 else 0) for i in range(len(a.rgb))
        )
        metrics = fidelity.compare(a, fidelity.Image(a.width, a.height, cast))
        self.assertAlmostEqual(metrics.mae_r, 5.0)
        self.assertEqual(metrics.mae_g, 0.0)
        self.assertEqual(metrics.mae_b, 0.0)
        self.assertAlmostEqual(metrics.mae, 5 / 3)

    def test_worst_delta_location(self):
        # max_x/max_y must locate the pixel carrying the worst channel delta,
        # so a failing comparison can be inspected at the right coordinate.
        a, _ = rgb_image(3, 2, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[15] = 40  # red channel of pixel (2, 1)
        b = fidelity.Image(a.width, a.height, bytes(changed))
        metrics = fidelity.compare(a, b)
        self.assertEqual(metrics.max_delta, 40)
        self.assertEqual((metrics.max_x, metrics.max_y), (2, 1))

    def test_tolerance_absorbs_small_deltas(self):
        a, _ = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        b = fidelity.Image(1, 1, bytes([3, 0, 0]))
        self.assertEqual(fidelity.compare(a, b, tolerance=3).differing, 0)
        self.assertEqual(fidelity.compare(a, b, tolerance=2).differing, 1)

    def test_size_mismatch_raises(self):
        a, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        b, _ = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity.FidelityError) as caught:
            fidelity.compare(a, b)
        message = str(caught.exception)
        self.assertIn("candidate 2x2", message)
        self.assertIn("reference 1x1", message)

    def test_crop_extracts_region(self):
        image, _ = rgb_image(4, 4, lambda x, y: (x, y, 0))
        region = fidelity.crop(image, 1, 2, 2, 2)
        self.assertEqual(region.width, 2)
        self.assertEqual(region.height, 2)
        self.assertEqual(region.rgb, bytes([1, 2, 0, 2, 2, 0, 1, 3, 0, 2, 3, 0]))

    def test_crop_out_of_bounds_raises(self):
        image, _ = rgb_image(2, 2, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity.FidelityError):
            fidelity.crop(image, 1, 1, 2, 2)

    def test_crop_nonpositive_rect_error_names_values(self):
        # The message must echo the rejected rectangle so a CLI user can see
        # which of x/y/w/h was wrong without re-deriving it from the input.
        image, _ = rgb_image(4, 4, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity.FidelityError) as caught:
            fidelity.crop(image, 0, 0, 0, 2)
        message = str(caught.exception)
        self.assertIn("x=0 y=0 w=0 h=2", message)

    def test_crop_out_of_bounds_error_names_rect_and_image(self):
        # The message must name both the offending rectangle and the image it
        # was measured against, since neither is otherwise visible.
        image, _ = rgb_image(4, 4, lambda x, y: (0, 0, 0))
        with self.assertRaises(fidelity.FidelityError) as caught:
            fidelity.crop(image, 3, 3, 2, 2)
        message = str(caught.exception)
        self.assertIn("x=3 y=3 w=2 h=2", message)
        self.assertIn("4x4", message)


class TestCli(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run the fidelity CLI with *args* and capture its output."""
        return subprocess.run(
            [sys.executable, str(TOOL), *args],
            capture_output=True,
            text=True,
        )

    def _write(self, directory: Path, name: str, data: bytes) -> str:
        path = directory / name
        path.write_bytes(data)
        return str(path)

    def test_pass_and_fail(self):
        a, a_png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
        changed = bytearray(a.rgb)
        # Pixel (1, 0) is (20, 0, 60); raise its green channel so exactly one
        # byte differs from the candidate.
        changed[4] = 50
        b_png = make_png(3, 3, [bytes(changed[i : i + 9]) for i in range(0, 27, 9)])
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", a_png)
            reference = self._write(tmpdir, "reference.png", a_png)
            altered = self._write(tmpdir, "altered.png", b_png)

            same = self._run(candidate, reference)
            self.assertEqual(same.returncode, 0, same.stderr)
            self.assertIn("PASS", same.stdout)

            different = self._run(candidate, altered)
            self.assertEqual(different.returncode, 1, different.stderr)
            self.assertIn("FAIL", different.stdout)
            self.assertIn("differing pixels: 1 / 9", different.stdout)
            self.assertIn("max channel delta: 50 at (1, 0)", different.stdout)

    def test_reports_worst_delta_location(self):
        a, a_png = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[3] = 50  # red channel of pixel (1, 0)
        b_png = make_png(2, 1, [bytes(changed)])
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", a_png)
            altered = self._write(tmpdir, "altered.png", b_png)
            result = self._run(candidate, altered)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("max channel delta: 50 at (1, 0)", result.stdout)

    def test_reports_per_channel_mae(self):
        # The CLI must expose each channel's MAE so a colour cast is visible
        # from a run without importing the module.
        a, a_png = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        b_png = make_png(1, 1, [bytes([10, 0, 0])])
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", a_png)
            altered = self._write(tmpdir, "altered.png", b_png)
            result = self._run(candidate, altered)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "per-channel MAE (R, G, B): 10.0000 0.0000 0.0000", result.stdout
        )

    def test_crop_region_passes(self):
        surface, surface_png = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
        rows = [
            bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
            bytes([0, 0, 0] + list(surface.rgb[0:6]) + [0, 0, 0]),
            bytes([0, 0, 0] + list(surface.rgb[6:12]) + [0, 0, 0]),
            bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        ]
        full_png = make_png(4, 4, rows)
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "surface.png", surface_png)
            reference = self._write(tmpdir, "full.png", full_png)
            result = self._run(candidate, reference, "--crop", "1,1,2,2")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)

    def test_help_documents_exit_status(self):
        # --help must state what each exit status means; the module docstring
        # promises the legend, and a caller scripting the tool cannot tell a
        # tolerance FAIL (1) from a usage or read error (2) without it.
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = " ".join(result.stdout.split())
        self.assertIn(
            "exit status: 0 within tolerance, 1 outside tolerance, "
            "2 usage or read error",
            help_text,
        )

    def test_malformed_png_is_error(self):
        # A PNG whose IHDR payload is not the 13 bytes the spec requires must
        # fail with the tool's clean error path (exit 2), not a struct.error
        # traceback from the unpack in decode_png.
        _, good = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        short_ihdr = (
            _PNG_SIGNATURE
            + _chunk(
                b"IHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00"
            )
            + _chunk(b"IEND", b"")
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "broken.png", short_ihdr)
            reference = self._write(tmpdir, "reference.png", good)
            result = self._run(candidate, reference)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn("error", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_decode_error_names_offending_file(self):
        # With two file inputs, the error must say which one could not be
        # decoded; the message is otherwise identical for either ordering.
        _, good = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "broken.png", b"not a png")
            reference = self._write(tmpdir, "reference.png", good)
            for first, second in ((candidate, reference), (reference, candidate)):
                with self.subTest(first=first):
                    result = self._run(first, second)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("error", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertIn(candidate, result.stderr)
                    self.assertNotIn(reference, result.stderr)

    def test_missing_file_is_error(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            result = self._run("/nonexistent.png", reference)
            self.assertEqual(result.returncode, 2)
            self.assertIn("error", result.stderr)

    def test_invalid_numeric_args_are_usage_errors(self):
        # Negative/NaN thresholds silently invert the verdict (a negative
        # tolerance makes every pixel differ, a NaN max-mae always fails), so
        # they must be rejected as usage errors rather than acted on.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            base = [reference, reference]
            for extra in (
                ["--tolerance", "-1"],
                ["--tolerance", "1.5"],
                ["--max-mae", "-1"],
                ["--max-mae", "nan"],
                ["--max-mae", "inf"],
                ["--max-frac", "-0.1"],
                ["--max-frac", "1.5"],
                ["--max-frac", "nan"],
            ):
                with self.subTest(extra=extra):
                    result = self._run(*base, *extra)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("error", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_malformed_crop_is_usage_error(self):
        # A bad --crop must be rejected as a usage error before either image is
        # read, and the message must name the offending value so the user does
        # not have to re-derive which field was wrong. Both paths are
        # nonexistent: a crop that reached the comparison would instead fail as
        # a read error, without argparse's "argument --crop:" prefix.
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "missing.png")
            base = [missing, missing]
            for extra, expected in (
                (["--crop", "1,2,3"], "1,2,3"),
                (["--crop", "a,2,3,4"], "'a'"),
                (["--crop", "0,0,0,2"], "x=0 y=0 w=0 h=2"),
                (["--crop=-1,0,2,2"], "x=-1 y=0 w=2 h=2"),
            ):
                with self.subTest(extra=extra):
                    result = self._run(*base, *extra)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn(expected, result.stderr)
                    self.assertIn("argument --crop:", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_tolerance_above_channel_range_rejected(self):
        # A per-channel delta is at most 255, so a larger tolerance can never
        # mark a pixel as differing and would silently disable that metric.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            for value in ("256", "1000"):
                with self.subTest(value=value):
                    result = self._run(reference, reference, "--tolerance", value)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("255", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_max_mae_above_channel_range_rejected(self):
        # Mean absolute error averages per-channel deltas, so it can never
        # exceed 255; a larger threshold would silently always pass.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            for value in ("255.5", "256", "1e9"):
                with self.subTest(value=value):
                    result = self._run(reference, reference, "--max-mae", value)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("255", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_valid_numeric_boundaries_accepted(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            result = self._run(
                reference,
                reference,
                "--tolerance",
                "255",
                "--max-mae",
                "255",
                "--max-frac",
                "1",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()

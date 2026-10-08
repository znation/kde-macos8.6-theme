"""Tests for tools/fidelity.py -- the objective fidelity comparison.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import fidelity  # noqa: E402

TOOL = REPO_ROOT / "tools" / "fidelity.py"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(ctype: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + ctype
        + payload
        + struct.pack(">I", zlib.crc32(ctype + payload) & 0xFFFFFFFF)
    )


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _filter_line(ftype: int, line: bytes, prev: bytes, bpp: int) -> bytes:
    if ftype == 0:
        return line
    out = bytearray(len(line))
    for i in range(len(line)):
        a = line[i - bpp] if i >= bpp else 0
        b = prev[i]
        c = prev[i - bpp] if i >= bpp else 0
        if ftype == 1:
            pred = a
        elif ftype == 2:
            pred = b
        elif ftype == 3:
            pred = (a + b) >> 1
        else:
            pred = _paeth(a, b, c)
        out[i] = (line[i] - pred) & 0xFF
    return bytes(out)


def make_png(
    width: int,
    height: int,
    rows: list[bytes],
    color_type: int = 2,
    palette: bytes | None = None,
    filter_types: list[int] | None = None,
) -> bytes:
    """Encode an 8-bit non-interlaced PNG from raw scanlines (test-only)."""
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    bpp = channels
    filtered = bytearray()
    prev = bytes(width * channels)
    for index, row in enumerate(rows):
        ftype = filter_types[index] if filter_types else 0
        filtered += bytes([ftype]) + _filter_line(ftype, row, prev, bpp)
        prev = row
    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    out = _PNG_SIGNATURE + _chunk(b"IHDR", ihdr)
    if palette is not None:
        out += _chunk(b"PLTE", palette)
    out += _chunk(b"IDAT", zlib.compress(bytes(filtered))) + _chunk(b"IEND", b"")
    return out


def rgb_image(width: int, height: int, pixel) -> tuple[fidelity.Image, bytes]:
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            row += bytes(pixel(x, y))
        rows.append(bytes(row))
    image = fidelity.Image(width, height, b"".join(rows))
    return image, make_png(width, height, rows)


class TestDecode(unittest.TestCase):
    def test_rgb_roundtrip(self):
        image, data = rgb_image(3, 2, lambda x, y: (x * 10, y * 20, 30))
        self.assertEqual(fidelity.decode_png(data), image)

    def test_all_filter_types(self):
        rows = [
            bytes([1, 2, 3, 4, 5, 6, 7, 8, 9]),
            bytes([10, 20, 30, 40, 50, 60, 70, 80, 90]),
            bytes([200, 150, 100, 50, 25, 12, 6, 3, 1]),
            bytes([0, 255, 0, 255, 0, 255, 0, 255, 0]),
            bytes([17, 34, 51, 68, 85, 102, 119, 136, 153]),
        ]
        # One row per PNG filter type: 0 None, 1 Sub, 2 Up, 3 Average, 4 Paeth.
        data = make_png(3, 5, rows, filter_types=[0, 1, 2, 3, 4])
        image = fidelity.decode_png(data)
        self.assertEqual(image.rgb, b"".join(rows))

    def test_palette(self):
        palette = bytes([255, 0, 0, 0, 255, 0])
        rows = [bytes([0, 1])]
        data = make_png(2, 1, rows, color_type=3, palette=palette)
        self.assertEqual(fidelity.decode_png(data).rgb, bytes([255, 0, 0, 0, 255, 0]))

    def test_grayscale_and_rgba(self):
        gray = make_png(2, 1, [bytes([7, 200])], color_type=0)
        self.assertEqual(fidelity.decode_png(gray).rgb, bytes([7, 7, 7, 200, 200, 200]))
        rgba = make_png(1, 1, [bytes([1, 2, 3, 4])], color_type=6)
        self.assertEqual(fidelity.decode_png(rgba).rgb, bytes([1, 2, 3]))

    def test_rejects_non_png(self):
        with self.assertRaises(fidelity.FidelityError):
            fidelity.decode_png(b"not a png")

    def test_read_png_names_undecodable_file(self):
        # A decode failure must name the file it came from, so a two-input
        # invocation can tell which of the candidate/reference was bad.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.png"
            path.write_bytes(b"not a png")
            with self.assertRaises(fidelity.FidelityError) as ctx:
                fidelity.read_png(path)
            self.assertIn(str(path), str(ctx.exception))


class TestCompare(unittest.TestCase):
    def test_identical_is_zero(self):
        image, _ = rgb_image(4, 4, lambda x, y: (x * 5, y * 5, 100))
        metrics = fidelity.compare(image, image)
        self.assertEqual(metrics.mae, 0.0)
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
        self.assertAlmostEqual(metrics.rmse, (100 / 12) ** 0.5)
        self.assertEqual(metrics.max_delta, 10)
        self.assertEqual(metrics.differing, 1)
        self.assertEqual(metrics.frac_differing, 0.25)

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
        with self.assertRaises(fidelity.FidelityError):
            fidelity.compare(a, b)

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
    def _write(self, directory: Path, name: str, data: bytes) -> str:
        path = directory / name
        path.write_bytes(data)
        return str(path)

    def test_pass_and_fail(self):
        a, a_png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
        changed = bytearray(a.rgb)
        changed[4] = 0
        b_png = make_png(3, 3, [bytes(changed[i : i + 9]) for i in range(0, 9, 3)])
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", a_png)
            reference = self._write(tmpdir, "reference.png", a_png)
            altered = self._write(tmpdir, "altered.png", b_png)

            same = subprocess.run(
                [sys.executable, str(TOOL), candidate, reference],
                capture_output=True,
                text=True,
            )
            self.assertEqual(same.returncode, 0, same.stderr)
            self.assertIn("PASS", same.stdout)

            different = subprocess.run(
                [sys.executable, str(TOOL), candidate, altered],
                capture_output=True,
                text=True,
            )
            self.assertEqual(different.returncode, 1, different.stderr)
            self.assertIn("FAIL", different.stdout)

    def test_reports_worst_delta_location(self):
        a, a_png = rgb_image(2, 1, lambda x, y: (0, 0, 0))
        changed = bytearray(a.rgb)
        changed[3] = 50  # red channel of pixel (1, 0)
        b_png = make_png(2, 1, [bytes(changed)])
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", a_png)
            altered = self._write(tmpdir, "altered.png", b_png)
            result = subprocess.run(
                [sys.executable, str(TOOL), candidate, altered],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("max channel delta: 50 at (1, 0)", result.stdout)

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
            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    candidate,
                    reference,
                    "--crop",
                    "1,1,2,2",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)

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
            result = subprocess.run(
                [sys.executable, str(TOOL), candidate, reference],
                capture_output=True,
                text=True,
            )
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
                    result = subprocess.run(
                        [sys.executable, str(TOOL), first, second],
                        capture_output=True,
                        text=True,
                    )
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
            result = subprocess.run(
                [sys.executable, str(TOOL), "/nonexistent.png", reference],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("error", result.stderr)

    def test_invalid_numeric_args_are_usage_errors(self):
        # Negative/NaN thresholds silently invert the verdict (a negative
        # tolerance makes every pixel differ, a NaN max-mae always fails), so
        # they must be rejected as usage errors rather than acted on.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            base = [sys.executable, str(TOOL), reference, reference]
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
                    result = subprocess.run(
                        base + extra, capture_output=True, text=True
                    )
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("error", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_tolerance_above_channel_range_rejected(self):
        # A per-channel delta is at most 255, so a larger tolerance can never
        # mark a pixel as differing and would silently disable that metric.
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            for value in ("256", "1000"):
                with self.subTest(value=value):
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(TOOL),
                            reference,
                            reference,
                            "--tolerance",
                            value,
                        ],
                        capture_output=True,
                        text=True,
                    )
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
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(TOOL),
                            reference,
                            reference,
                            "--max-mae",
                            value,
                        ],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn("255", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_valid_numeric_boundaries_accepted(self):
        _, data = rgb_image(1, 1, lambda x, y: (0, 0, 0))
        with tempfile.TemporaryDirectory() as tmp:
            reference = self._write(Path(tmp), "reference.png", data)
            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    reference,
                    reference,
                    "--tolerance",
                    "255",
                    "--max-mae",
                    "255",
                    "--max-frac",
                    "1",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()

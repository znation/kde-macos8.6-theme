"""Tests for the sampler's JPEG branch: ImageMagick conversion before sampling.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support.repo_root import ROOT  # noqa: F401  (puts root on sys.path)
from support.cli_fixtures import CliTestCase
from support.jpeg_sampler_fixture import (
    QUILT_BLOCK_HEX,
    QUILT_BLOCK_TRIPLE,
    QUILT_FIND_BOUNDS,
    QUILT_FIND_COUNT,
    QUILT_FIND_HEX,
    QUILT_FIND_TOTALS,
    QUILT_HEIGHT,
    QUILT_HISTOGRAM_ROWS,
    QUILT_JPEG,
    QUILT_RUN_ROWS,
    QUILT_WIDTH,
)
from support.png_fixtures import make_png, solid_rgb


def _rgba_png_bytes() -> bytes:
    """A two-pixel one-row RGBA PNG with transparent and opaque pixels."""
    return make_png(
        2,
        1,
        rows=[bytes((12, 34, 56, 0, 78, 90, 123, 255))],
        color_type=6,
    )
from tools import jpeg_convert, sample


class TestIsJpeg(unittest.TestCase):
    """The three-byte sniff that routes JPEG inputs to the conversion bridge."""

    def test_full_magic_head_is_jpeg(self):
        self.assertTrue(jpeg_convert.is_jpeg(bytes((0xFF, 0xD8, 0xFF, 0xE0))))

    def test_shorter_and_foreign_heads_are_not_jpeg(self):
        for head in (
            b"",
            bytes((0xFF, 0xD8)),
            bytes((0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A)),
            b"GIF89a",
            bytes((0xFF, 0xD9, 0xFF)),
        ):
            with self.subTest(head=head):
                self.assertFalse(jpeg_convert.is_jpeg(head))


class TestConvertJpegArguments(unittest.TestCase):
    """The conversion bridge's argument validation."""

    def test_rejects_non_bytes_input_with_argument_name(self):
        with self.assertRaisesRegex(
            ValueError,
            r"^convert_jpeg\(\) requires bytes: input_bytes must be bytes, not str$",
        ):
            jpeg_convert.convert_jpeg("jpeg", Path("out.png"))

    def test_rejects_non_path_output_with_argument_name(self):
        with self.assertRaisesRegex(
            ValueError,
            r"^convert_jpeg\(\) requires pathlib\.Path: temp_png must be Path, not str$",
        ):
            jpeg_convert.convert_jpeg(b"jpeg", "out.png")


class TestConvertJpegFailureDiagnostic(unittest.TestCase):
    """The conversion bridge's failure diagnostics and their private-path scrubbing."""

    def test_nonzero_converter_status_keeps_output_and_scrubs_private_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def fail_with_private_path(
                argv, env, stdout_log, stderr_log, *args, **kwargs
            ):
                Path(stderr_log).write_text(f"cannot decode {temp_png}")
                return 7

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=fail_with_private_path,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(
            problem,
            "convert exited 7: cannot decode <the temporary decoded PNG>",
        )
        self.assertNotIn(str(temp_png), problem)

    def test_a_log_naming_an_imagemagick_temporary_path_is_scrubbed(self):
        # A failing converter's own output can name the scratch files
        # ImageMagick creates for itself; the diagnostic must blank those
        # occurrences as well, so it names only surfaces the operator chose
        # and never a converter-internal temporary path.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def fail_naming_magick_temporary(
                argv, env, stdout_log, stderr_log, *args, **kwargs
            ):
                Path(stdout_log).write_text(
                    "convert-im6.q16: cannot open /tmp/magick-abc123 : "
                    "no decode delegate for the JPEG input"
                )
                return 3

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=fail_naming_magick_temporary,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(
            problem,
            "convert exited 3: convert-im6.q16: cannot open "
            "<an ImageMagick temporary> : no decode delegate for the JPEG input",
        )
        self.assertNotIn("magick-abc123", problem)

    def test_a_silent_converter_failure_reports_only_the_status(self):
        # A converter can exit nonzero without writing anything: the logs
        # run_logged_split opens exist but hold no text. The diagnostic must
        # still name the exit status — the headline alone — and must not
        # crash looking for a first log line that is not there.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def fail_silently(argv, env, stdout_log, stderr_log, *args, **kw):
                # run_logged_split opens both logs ('wb') before the child
                # runs, so an empty failure leaves two zero-byte files.
                Path(stdout_log).touch()
                Path(stderr_log).touch()
                return 1

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=fail_silently,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(problem, "convert exited 1")

    def test_whitespace_only_converter_output_is_not_quoted(self):
        # Blank output is stripped before the headline check, so a converter
        # that fails writing only whitespace is reported like a silent one:
        # quoting blank text would add nothing the operator can act on.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def fail_with_blank_stderr(argv, env, stdout_log, stderr_log, *a, **kw):
                Path(stdout_log).touch()
                Path(stderr_log).write_text("\n  \n")
                return 2

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=fail_with_blank_stderr,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(problem, "convert exited 2")

    def test_flooding_converter_log_is_read_and_quoted_only_to_its_cap(self):
        flood = 1 << 20  # one MiB of stderr from a failing converter
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def flood_stderr(argv, env, stdout_log, stderr_log, *args, **kwargs):
                Path(stderr_log).write_text("W" * flood)
                return 1

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=flood_stderr,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertTrue(problem.startswith("convert exited 1: W"))
        quoted = problem[len("convert exited 1: "):]
        self.assertEqual(len(quoted), 4096)
        self.assertEqual(set(quoted), {"W"})

    def test_a_converter_that_cannot_start_is_reported_naming_the_os_error(self):
        # convert_jpeg() resolves the executable with shutil.which() first, so
        # the one start failure it can still meet is the executable vanishing
        # (or becoming unstartable) between that lookup and the spawn: the
        # Popen call raises OSError, and the sampler must print it as its
        # "cannot run convert" diagnostic instead of dying with a traceback.
        failure = OSError(2, "No such file or directory", "/usr/bin/convert")
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=failure,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(problem, f"cannot run convert: {failure}")

    def test_a_converter_that_hits_its_timeout_is_reported_with_the_budget(self):
        # A hung converter returns None from run_logged_split (the shared
        # runner's timeout verdict); the diagnostic must name the decode and
        # the documented 60-second budget, not the exit-status wording a
        # nonzero status would print.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    return_value=None,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(
            problem,
            "convert did not decode the JPEG input within 60s",
        )

    def test_a_converter_that_writes_no_png_is_refused(self):
        # A converter that exits 0 without producing the temporary PNG (or
        # with an empty one) must still be a refusal: returning success would
        # send the sampler after a missing or empty file whose own diagnostic
        # names the private scratch path instead of the JPEG input.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    return_value=0,
                ),
            ):
                missing = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)
                self.assertEqual(
                    missing, "convert wrote no PNG for the JPEG input"
                )

                temp_png.write_bytes(b"")
                empty = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)
                self.assertEqual(
                    empty, "convert wrote no PNG for the JPEG input"
                )


class TestJpegSampler(CliTestCase):
    """The JPEG branch's end-to-end reports, pinned to the fixture's constants."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self, name: str = "quilt.jpg", data: bytes = QUILT_JPEG) -> str:
        return self._write(self._tmp_dir(), name, data)

    def test_script_entry_point(self):
        """The JPEG branch also runs end to end as ``python3 tools/sample.py``."""
        path = self._image()
        result = self._run_script(path, "8", "8")
        self._assert_success(result)
        self.assertEqual(result.stdout.splitlines()[0], f"image: {path}  {QUILT_WIDTH}x{QUILT_HEIGHT}")

    def test_pixel_region_reports_recorded_triples(self):
        path = self._image()
        result = self._run(path, "8", "8", "--width", "3", "--height", "2")
        self._assert_success(result)
        triple = (
            f"{QUILT_BLOCK_TRIPLE[0]},{QUILT_BLOCK_TRIPLE[1]},{QUILT_BLOCK_TRIPLE[2]}"
            f"  {QUILT_BLOCK_HEX}"
        )
        expected = [f"image: {path}  {QUILT_WIDTH}x{QUILT_HEIGHT}", "region (8, 8) 3x2:"]
        for y in (8, 9):
            for x in (8, 9, 10):
                expected.append(f"({x}, {y}): " + triple)
        self.assertEqual(result.stdout.splitlines(), expected)

    def test_histogram_reports_recorded_counts(self):
        path = self._image()
        result = self._run(
            path, "0", "0", "--width", "16", "--height", "8", "--histogram", "--top-colors", "6"
        )
        self._assert_success(result)
        self.assertEqual(
            result.stdout.splitlines(),
            [f"image: {path}  {QUILT_WIDTH}x{QUILT_HEIGHT}", "region (0, 0) 16x8:", *QUILT_HISTOGRAM_ROWS],
        )

    def test_runs_reports_recorded_boundaries(self):
        path = self._image()
        result = self._run(path, "0", "0", "--height", "24", "--runs")
        self._assert_success(result)
        self.assertEqual(
            result.stdout.splitlines(),
            [f"image: {path}  {QUILT_WIDTH}x{QUILT_HEIGHT}", *QUILT_RUN_ROWS],
        )

    def test_find_color_reports_recorded_matches(self):
        path = self._image()
        result = self._run(
            path,
            "10",
            "10",
            "--width",
            "8",
            "--height",
            "8",
            "--find-color",
            QUILT_FIND_HEX,
            "--match-pixels",
            "3",
        )
        self._assert_success(result)
        self.assertIn(f"image: {path}  {QUILT_WIDTH}x{QUILT_HEIGHT}", result.stdout)
        self.assertIn(f"color: {QUILT_FIND_HEX}", result.stdout)
        self.assertIn(f"count: {QUILT_FIND_COUNT}", result.stdout)
        self.assertIn(QUILT_FIND_BOUNDS, result.stdout)
        for line in QUILT_FIND_TOTALS:
            self.assertIn(line, result.stdout)


class TestJpegCallRouting(CliTestCase):
    """The branch routing: JPEG converts, PNG never converts, refusals precede."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self, name: str = "quilt.jpg", data: bytes = QUILT_JPEG) -> str:
        return self._write(self._tmp_dir(), name, data)

    def _png(self) -> str:
        _, data = solid_rgb(2, 2)
        return self._write(self._tmp_dir(), "reference.png", data)

    def test_png_input_never_enters_the_jpeg_branch(self):
        path = self._png()
        with mock.patch.object(
            jpeg_convert, "convert_jpeg", side_effect=AssertionError("PNG input converted")
        ) as convert:
            result = self._run(path, "0", "0")
        self._assert_success(result)
        convert.assert_not_called()

    def test_png_alpha_flags_still_work_exactly(self):
        path = self._write(self._tmp_dir(), "alpha.png", _rgba_png_bytes())
        with mock.patch.object(
            jpeg_convert, "convert_jpeg", side_effect=AssertionError("PNG input converted")
        ) as convert:
            result = self._run(path, "0", "0", "--width", "2", "--alpha")
        self._assert_success(result)
        convert.assert_not_called()
        self.assertIn("alpha=0", result.stdout)
        self.assertIn("alpha=255", result.stdout)

    def test_jpeg_with_alpha_refuses_before_conversion(self):
        path = self._image()
        with mock.patch.object(
            jpeg_convert, "convert_jpeg", side_effect=AssertionError("alpha JPEG converted")
        ) as convert:
            result = self._run(path, "0", "0", "--alpha")
        convert.assert_not_called()
        self._assert_usage_error(result, "--alpha", "PNG", "JPEG")
        self.assertEqual(result.stdout, "")

    def test_jpeg_with_match_alpha_refuses_before_conversion(self):
        path = self._image()
        with mock.patch.object(
            jpeg_convert, "convert_jpeg", side_effect=AssertionError("alpha JPEG converted")
        ) as convert:
            result = self._run(path, "0", "0", "--match-alpha", "255", "--find-color", "#000000")
        convert.assert_not_called()
        self._assert_usage_error(result, "--match-alpha", "PNG", "JPEG")
        self.assertEqual(result.stdout, "")


class TestJpegFailureRoutes(CliTestCase):
    """The JPEG branch's failure diagnostics follow the sampler's shapes."""

    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self, name: str = "quilt.jpg", data: bytes = QUILT_JPEG) -> str:
        return self._write(self._tmp_dir(), name, data)

    def test_missing_convert_is_refused_naming_it(self):
        path = self._image()
        with mock.patch.object(jpeg_convert.shutil, "which", return_value=None):
            result = self._run(path, "0", "0")
        self._assert_usage_error(result, "convert", "ImageMagick")
        self.assertIn(path, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_non_png_non_jpeg_keeps_the_standing_refusal(self):
        path = self._write(
            self._tmp_dir(), "blob.bin", bytes(range(32)) * 8
        )
        result = self._run(path, "0", "0")
        self._assert_usage_error(result, "cannot decode", "not a PNG file")

    def test_truncated_jpeg_names_the_given_path_only(self):
        truncated = QUILT_JPEG[: len(QUILT_JPEG) // 4]
        path = self._image("truncated.jpg", truncated)
        result = self._run(path, "0", "0")
        self._assert_usage_error(result)
        # The diagnostic must name the path the operator gave; none of the
        # private scratch names may leak.
        self.assertIn(path, result.stderr)
        self.assertNotIn("sample-jpeg-", result.stderr)
        self.assertNotIn("sample-convert-", result.stderr)
        self.assertNotIn("decoded.png", result.stderr)
        self.assertNotIn("magick-", result.stderr)

    def test_out_of_bounds_pixel_reports_the_decoded_size(self):
        path = self._image()
        result = self._run(path, str(QUILT_WIDTH), "0")
        self._assert_usage_error(
            result, f"outside the {QUILT_WIDTH}x{QUILT_HEIGHT} image"
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

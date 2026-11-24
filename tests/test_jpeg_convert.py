"""Tests for tools/jpeg_convert.py: the JPEG sniff, argument validation and
conversion-failure diagnostics, with ``convert`` stubbed.

``decoded_png`` is covered in ``tests/test_jpeg_decoded_png.py``, and the
sampler's JPEG CLI reports are in ``tests/test_sample_jpeg.py``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from support.repo_root import ROOT  # noqa: F401  (puts root on sys.path)
from tools import image_format, jpeg_convert


class TestIsJpeg(unittest.TestCase):
    """The three-byte sniff that routes JPEG inputs to the conversion bridge."""

    def test_full_magic_head_is_jpeg(self):
        self.assertTrue(jpeg_convert.is_jpeg(bytes((0xFF, 0xD8, 0xFF, 0xE0))))

    def test_magic_is_the_shared_signature_constant(self):
        self.assertEqual(jpeg_convert.JPEG_MAGIC, image_format.JPEG_MAGIC)

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

    def test_a_log_naming_the_temporary_directory_blanks_the_directory(self):
        # The decoded PNG's own path is blanked first; a converter log that
        # names a different file in the same private directory must still
        # lose the directory part, so the diagnostic never reveals it.
        with tempfile.TemporaryDirectory() as directory:
            temp_png = Path(directory) / "decoded.png"

            def fail_naming_the_directory(
                argv, env, stdout_log, stderr_log, *args, **kwargs
            ):
                Path(stderr_log).write_text(
                    f"cannot write {directory}/scratch.txt"
                )
                return 4

            with (
                mock.patch.object(
                    jpeg_convert.shutil,
                    "which",
                    return_value="/usr/bin/convert",
                ),
                mock.patch.object(
                    jpeg_convert,
                    "run_logged_split",
                    side_effect=fail_naming_the_directory,
                ),
            ):
                problem = jpeg_convert.convert_jpeg(b"jpeg bytes", temp_png)

        self.assertEqual(
            problem,
            "convert exited 4: cannot write <a temporary directory>/scratch.txt",
        )
        self.assertNotIn(directory, problem)

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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

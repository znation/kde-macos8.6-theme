"""Tests for the reference-pixel sampling CLI in tools/sample.py.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.cli_fixtures import CliTestCase  # noqa: E402
from support.error_assertions import assert_escapes_escape_character  # noqa: E402
from support.png_fixtures import (  # noqa: E402
    control_named_missing,
    control_named_png,
    make_png,
    rgb_image,
    solid_rgb,
)
from support.symlink_fixtures import symlinked_repo  # noqa: E402
from tools import sample  # noqa: E402


class TestSampleCli(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self) -> str:
        """Write a 4x3 PNG whose pixel ``(x, y)`` is ``(x, y, x + y)``."""
        _, data = rgb_image(4, 3, lambda x, y: (x, y, x + y))
        return self._write(self._tmp_dir(), "reference.png", data)

    def test_script_entry_point(self):
        """The CLI still runs end to end as ``python3 tools/sample.py``.

        Every other test calls ``sample.main`` in-process; this one spawns the
        script so the ``if __name__ == "__main__": sys.exit(main())`` wrapper
        and the module's direct-run import path stay covered.
        """
        _, data = solid_rgb(1, 1)
        tmp = self._tmp_dir()
        path = self._write(tmp, "reference.png", data)
        result = self._run_script(path, "0", "0")
        self._assert_success(result)
        self.assertIn("pixel (0, 0): 0,0,0  #000000", result.stdout)

    def test_reports_rgb_and_hex(self):
        path = self._image()
        result = self._run(path, "2", "1")
        self._assert_success(result)
        self.assertIn("image: " + path + "  4x3", result.stdout)
        # Pixel (2, 1) is (2, 1, 3); each channel is zero-padded to two hex
        # digits, so the low green value reads "01" rather than "1".
        self.assertIn("pixel (2, 1): 2,1,3  #020103", result.stdout)

    def test_corner_pixels_are_addressable(self):
        path = self._image()
        for x, y, expected in (
            ("0", "0", "0,0,0  #000000"),
            ("3", "2", "3,2,5  #030205"),
        ):
            with self.subTest(x=x, y=y):
                result = self._run(path, x, y)
                self._assert_success(result)
                self.assertIn(
                    f"pixel ({x}, {y}): {expected}", result.stdout
                )

    def test_width_samples_a_row(self):
        # --width extends the sample to the right of (x, y).
        path = self._image()
        result = self._run(path, "1", "1", "--width", "3")
        self._assert_success(result)
        self.assertIn("region (1, 1) 3x1:", result.stdout)
        for line in (
            "(1, 1): 1,1,2  #010102",
            "(2, 1): 2,1,3  #020103",
            "(3, 1): 3,1,4  #030104",
        ):
            self.assertIn(line, result.stdout)

    def test_height_samples_a_column(self):
        path = self._image()
        result = self._run(path, "0", "0", "--height", "3")
        self._assert_success(result)
        self.assertIn("region (0, 0) 1x3:", result.stdout)
        for line in (
            "(0, 0): 0,0,0  #000000",
            "(0, 1): 0,1,1  #000101",
            "(0, 2): 0,2,2  #000202",
        ):
            self.assertIn(line, result.stdout)

    def test_decodes_only_through_the_samples(self):
        # A reference PNG can take seconds to unfilter; the sampler only needs
        # the rows its rectangle occupies, so the decode bound is the
        # rectangle's bottom edge for both a pixel and a taller region.
        path = self._image()
        for arguments, rows in (
            (("2", "1"), 2),
            (("1", "1", "--width", "2", "--height", "2"), 3),
        ):
            with self.subTest(arguments=arguments):
                with mock.patch.object(
                    sample, "read_png", wraps=sample.read_png
                ) as read:
                    result = self._run(path, *arguments)
                self._assert_success(result)
                read.assert_called_once()
                self.assertEqual(read.call_args.kwargs["max_rows"], rows)

    def test_out_of_bounds_request_skips_the_row_decode(self):
        # The requested pixel or region is checked against the header size
        # before the sampler's bounded row decode, so an out-of-bounds request
        # on a large (or undecodable) reference names the coordinate without
        # being handed to the decoder. Patch the decode entry point to fail if
        # it is reached at all.
        path = self._image()
        for arguments in (("4", "1"), ("2", "1", "--width", "3")):
            with self.subTest(arguments=arguments):
                with mock.patch.object(
                    sample,
                    "read_png",
                    side_effect=AssertionError("decoded an out-of-bounds request"),
                ):
                    result = self._run(path, *arguments)
                self._assert_usage_error(result, "outside the 4x3 image")

    def test_corruption_below_the_sampled_row_is_still_reported(self):
        # The sampler bounds its decode to the sampled rectangle's bottom row,
        # but that only skips predictor work: every scanline's filter type is
        # still validated. A corrupt reference whose bad filter type sits
        # below the sample must fail the run, not print a pixel from a file
        # the decoder would reject. This is the guarantee the bounded-read
        # change stated in its RISK line.
        data = make_png(
            4, 3, [bytes(12), bytes(12), bytes(12)], filter_types=[0, 9, 0]
        )
        path = self._write(self._tmp_dir(), "corrupt.png", data)
        result = self._run(path, "0", "0")
        self._assert_usage_error(
            result, "unsupported PNG filter type 9 in row 1"
        )
        self.assertNotIn("pixel (", result.stdout)

    def test_region_is_row_major(self):
        path = self._image()
        result = self._run(path, "1", "0", "--width", "2", "--height", "2")
        self._assert_success(result)
        self.assertIn("region (1, 0) 2x2:", result.stdout)
        expected = [
            "(1, 0): 1,0,1  #010001",
            "(2, 0): 2,0,2  #020002",
            "(1, 1): 1,1,2  #010102",
            "(2, 1): 2,1,3  #020103",
        ]
        positions = [result.stdout.index(line) for line in expected]
        self.assertEqual(positions, sorted(positions))

    def test_zero_or_negative_extent_is_usage_error(self):
        # --width/--height count pixels, so 0 and negative would name an empty
        # or inverted region; both must be rejected with the option named.
        path = self._image()
        for option, value in (("--width", "0"), ("--height", "-1")):
            with self.subTest(option=option):
                result = self._run(path, "0", "0", option, value)
                self._assert_usage_error(
                    result, f"{option} must be at least 1"
                )

    def test_region_past_edge_is_error(self):
        # The whole rectangle is validated before any pixel is printed, so an
        # out-of-bounds region names the region and the image size once.
        path = self._image()
        result = self._run(path, "2", "1", "--width", "3")
        self._assert_usage_error(
            result, "region (2, 1) 3x1 is outside the 4x3 image"
        )

    def test_region_past_bottom_edge_is_error(self):
        # The bounds check has two disjuncts, one per axis. The test above
        # exercises only the horizontal one (x + width past the right edge),
        # so a regression that dropped the vertical check would still pass it
        # and then run the region loop off the bottom: pixel_at is not guarded
        # inside the loop, so the run would traceback after a partial dump.
        # A region that overshoots only the bottom must instead fail as one
        # diagnostic before any pixel is printed.
        path = self._image()
        result = self._run(path, "0", "1", "--height", "3")
        self._assert_usage_error(
            result, "region (0, 1) 1x3 is outside the 4x3 image"
        )
        self.assertNotIn("region", result.stdout)
        self.assertNotIn("(0, 1):", result.stdout)

    def test_coordinate_past_edge_is_error(self):
        # x == width and y == height are the first coordinates outside the
        # image; pixel_at must name both the coordinate and the image size.
        path = self._image()
        result = self._run(path, "4", "1")
        self._assert_usage_error(result, "outside the 4x3 image")

    def test_negative_coordinate_is_error(self):
        path = self._image()
        result = self._run(path, "-1", "0")
        self._assert_usage_error(result, "outside the 4x3 image")

    def test_negative_region_origin_names_the_region(self):
        # A region is validated as a whole before its origin is sampled, so a
        # negative origin is reported as the requested region, not as a single
        # out-of-bounds pixel, and no partial dump is printed.
        path = self._image()
        for arguments, region in (
            (("-1", "0", "--width", "2"), "region (-1, 0) 2x1"),
            (("0", "-1", "--height", "2"), "region (0, -1) 1x2"),
        ):
            with self.subTest(region=region):
                result = self._run(path, *arguments)
                self._assert_usage_error(
                    result, f"{region} is outside the 4x3 image"
                )
                self.assertNotIn("pixel (", result.stderr)
                self.assertNotIn("region", result.stdout)

    def test_missing_file_is_error(self):
        tmp = self._tmp_dir()
        missing = str(tmp / "absent.png")
        result = self._run(missing, "0", "0")
        self._assert_usage_error(result, "cannot read", missing)

    def test_rejects_an_image_that_symlinks_outside_the_repository(self):
        # A checked-in symlink at a reference image can point at a private
        # image; sampling it would print that image's pixels. The path is
        # refused before either the header or the rows are read.
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(
            self._tmp_dir(), "reference.png", data
        )
        with mock.patch.object(sample, "ROOT", str(root)):
            result = self._run(str(link), "0", "0")
        self._assert_usage_error(result, "resolves outside", str(root))
        self.assertNotIn("pixel (", result.stdout)

    def test_rejects_an_escaping_symlink_reached_through_a_checkout_alias(self):
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(
            self._tmp_dir(), "reference.png", data
        )
        alias = root.parent / "alias"
        alias.symlink_to(root)
        with mock.patch.object(sample, "ROOT", str(root.resolve())):
            result = self._run(str(alias / link.name), "0", "0")
        self._assert_usage_error(result, "resolves outside", "reference.png")
        self.assertNotIn("pixel (", result.stdout)

    def test_rejects_an_image_under_a_symlinked_folder_that_escapes(self):
        _, data = solid_rgb(1, 1)
        tmp = self._tmp_dir()
        root = tmp / "repo"
        root.mkdir()
        private = tmp / "private"
        private.mkdir()
        (private / "secret.png").write_bytes(data)
        (root / "refs").symlink_to(private)
        with mock.patch.object(sample, "ROOT", str(root)):
            result = self._run(str(root / "refs" / "secret.png"), "0", "0")
        self._assert_usage_error(result, "resolves outside", str(root))
        self.assertNotIn("pixel (", result.stdout)

    def test_rejects_a_symlinked_folder_that_escapes_via_a_checkout_alias(self):
        _, data = solid_rgb(1, 1)
        tmp = self._tmp_dir()
        root = tmp / "repo"
        root.mkdir()
        private = tmp / "private"
        private.mkdir()
        (private / "secret.png").write_bytes(data)
        (root / "refs").symlink_to(private)
        alias = tmp / "alias"
        alias.symlink_to(root)
        with mock.patch.object(sample, "ROOT", str(root.resolve())):
            result = self._run(str(alias / "refs" / "secret.png"), "0", "0")
        self._assert_usage_error(result, "resolves outside", "secret.png")
        self.assertNotIn("pixel (", result.stdout)

    def test_rejects_a_dotdot_path_that_climbs_out_of_an_escaping_folder(self):
        # ``refs/../secret.png`` is ``repo/secret.png`` lexically, but the OS
        # resolves ``refs`` first and opens ``private/../secret.png``.
        _, data = solid_rgb(1, 1)
        tmp = self._tmp_dir()
        root = tmp / "repo"
        root.mkdir()
        private = tmp / "private"
        (private / "sub").mkdir(parents=True)
        (private / "secret.png").write_bytes(data)
        (root / "refs").symlink_to(private / "sub")
        with mock.patch.object(sample, "ROOT", str(root)):
            result = self._run(
                f"{root}/refs/../secret.png", "0", "0"
            )
        self._assert_usage_error(result, "resolves outside", "secret.png")
        self.assertNotIn("pixel (", result.stdout)

    def test_reads_a_symlink_that_stays_within_the_repository(self):
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(
            self._tmp_dir(), "reference.png", data, target="real.png"
        )
        with mock.patch.object(sample, "ROOT", str(root)):
            result = self._run(str(link), "0", "0")
        self._assert_success(result)
        self.assertIn("pixel (0, 0): 0,0,0  #000000", result.stdout)

    def test_non_integer_coordinate_is_usage_error(self):
        path = self._image()
        result = self._run(path, "a", "0")
        self._assert_usage_error(result, "x must be an integer")

    def test_python_literal_coordinates_rejected(self):
        # int() would accept "1_0" as 10 and "\u0661" as 1, silently naming a
        # different pixel; both must be rejected as usage errors.
        path = self._image()
        for bad in ("1_0", "\u0661", " 1"):
            with self.subTest(value=bad):
                result = self._run(path, bad, "0")
                self._assert_usage_error(
                    result, "x must be a plain ASCII integer"
                )

    def test_help_documents_exit_status(self):
        result = self._run("--help")
        self._assert_success(result)
        self.assertIn(
            "exit status: 0 on success, 2 usage or read error", result.stdout
        )

    def test_error_message_escapes_control_characters_in_path(self):
        # read_png embeds the path in its error message, and the documented
        # workflow hands this tool a file from the contributor-owned screenshot
        # directory, so a missing name carrying an ESC must not print the raw
        # byte to the terminal.
        with control_named_missing() as missing:
            result = self._run(missing, "0", "0")
        self._assert_usage_error(result)
        assert_escapes_escape_character(self, result.stderr)

    def test_success_output_escapes_control_characters_in_path(self):
        # The success header names the path; a shell glob over the reference
        # directory passes a contributor-supplied filename through unchanged.
        with control_named_png() as path:
            result = self._run(path, "0", "0")
        self._assert_success(result)
        assert_escapes_escape_character(self, result.stdout)

    def test_usage_error_escapes_control_characters_in_arguments(self):
        # argparse builds its own "unrecognized arguments: ..." diagnostic from
        # raw argv, so it bypasses main()'s escaping of the image path. An
        # ESC-bearing extra positional must not print the raw byte.
        path = self._image()
        result = self._run(path, "0", "0", "evil\x1b[31m.png")
        self._assert_usage_error(result, "unrecognized arguments")
        assert_escapes_escape_character(self, result.stderr)


if __name__ == "__main__":
    unittest.main()

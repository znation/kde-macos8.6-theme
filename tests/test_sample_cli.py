"""Tests for the reference-pixel sampling CLI in tools/sample.py.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import sample  # noqa: E402
from cli_fixtures import CliTestCase  # noqa: E402
from error_assertions import assert_escapes_escape_character  # noqa: E402
from png_fixtures import control_named_png, rgb_image, solid_rgb  # noqa: E402
from theme_install import run_captured  # noqa: E402

TOOL = REPO_ROOT / "tools" / "sample.py"


class TestSampleCli(CliTestCase):
    MAIN = staticmethod(sample.main)
    PROGRAM = "sample"

    def _image(self, directory: Path) -> str:
        """Write a 4x3 PNG whose pixel ``(x, y)`` is ``(x, y, x + y)``."""
        _, data = rgb_image(4, 3, lambda x, y: (x, y, x + y))
        return self._write(directory, "reference.png", data)

    def test_script_entry_point(self):
        """The CLI still runs end to end as ``python3 tools/sample.py``.

        Every other test calls ``sample.main`` in-process; this one spawns the
        script so the ``if __name__ == "__main__": sys.exit(main())`` wrapper
        and the module's direct-run import path stay covered.
        """
        _, data = solid_rgb(1, 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "reference.png", data)
            result = run_captured(
                [sys.executable, str(TOOL), path, "0", "0"],
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("pixel (0, 0): 0,0,0  #000000", result.stdout)

    def test_reports_rgb_and_hex(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "2", "1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("image: " + path + "  4x3", result.stdout)
        # Pixel (2, 1) is (2, 1, 3); each channel is zero-padded to two hex
        # digits, so the low green value reads "01" rather than "1".
        self.assertIn("pixel (2, 1): 2,1,3  #020103", result.stdout)

    def test_corner_pixels_are_addressable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            for x, y, expected in (
                ("0", "0", "0,0,0  #000000"),
                ("3", "2", "3,2,5  #030205"),
            ):
                with self.subTest(x=x, y=y):
                    result = self._run(path, x, y)
                    self.assertEqual(
                        result.returncode, 0, result.stdout + result.stderr
                    )
                    self.assertIn(
                        f"pixel ({x}, {y}): {expected}", result.stdout
                    )

    def test_width_samples_a_row(self):
        # --width extends the sample to the right of (x, y).
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "1", "1", "--width", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("region (1, 1) 3x1:", result.stdout)
        for line in (
            "(1, 1): 1,1,2  #010102",
            "(2, 1): 2,1,3  #020103",
            "(3, 1): 3,1,4  #030104",
        ):
            self.assertIn(line, result.stdout)

    def test_height_samples_a_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "0", "0", "--height", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("region (0, 0) 1x3:", result.stdout)
        for line in (
            "(0, 0): 0,0,0  #000000",
            "(0, 1): 0,1,1  #000101",
            "(0, 2): 0,2,2  #000202",
        ):
            self.assertIn(line, result.stdout)

    def test_region_is_row_major(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "1", "0", "--width", "2", "--height", "2")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
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
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            for option, value in (("--width", "0"), ("--height", "-1")):
                with self.subTest(option=option):
                    result = self._run(path, "0", "0", option, value)
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn(
                        f"{option} must be at least 1", result.stderr
                    )

    def test_region_past_edge_is_error(self):
        # The whole rectangle is validated before any pixel is printed, so an
        # out-of-bounds region names the region and the image size once.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "2", "1", "--width", "3")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "region (2, 1) 3x1 is outside the 4x3 image", result.stderr
        )

    def test_region_past_bottom_edge_is_error(self):
        # The bounds check has two disjuncts, one per axis. The test above
        # exercises only the horizontal one (x + width past the right edge),
        # so a regression that dropped the vertical check would still pass it
        # and then run the region loop off the bottom: pixel_at is not guarded
        # inside the loop, so the run would traceback after a partial dump.
        # A region that overshoots only the bottom must instead fail as one
        # diagnostic before any pixel is printed.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "0", "1", "--height", "3")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(
            "region (0, 1) 1x3 is outside the 4x3 image", result.stderr
        )
        self.assertNotIn("region", result.stdout)
        self.assertNotIn("(0, 1):", result.stdout)

    def test_coordinate_past_edge_is_error(self):
        # x == width and y == height are the first coordinates outside the
        # image; pixel_at must name both the coordinate and the image size.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "4", "1")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outside the 4x3 image", result.stderr)

    def test_negative_coordinate_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "-1", "0")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("outside the 4x3 image", result.stderr)

    def test_missing_file_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "absent.png")
            result = self._run(missing, "0", "0")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("cannot read", result.stderr)
        self.assertIn(missing, result.stderr)

    def test_non_integer_coordinate_is_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "a", "0")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("x must be an integer", result.stderr)

    def test_python_literal_coordinates_rejected(self):
        # int() would accept "1_0" as 10 and "\u0661" as 1, silently naming a
        # different pixel; both must be rejected as usage errors.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            for bad in ("1_0", "\u0661", " 1"):
                with self.subTest(value=bad):
                    result = self._run(path, bad, "0")
                    self.assertEqual(
                        result.returncode, 2, result.stdout + result.stderr
                    )
                    self.assertIn(
                        "x must be a plain ASCII integer", result.stderr
                    )

    def test_help_documents_exit_status(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "exit status: 0 on success, 2 usage or read error", result.stdout
        )

    def test_error_message_escapes_control_characters_in_path(self):
        # read_png embeds the path in its error message, and the documented
        # workflow hands this tool a file from the contributor-owned screenshot
        # directory, so a missing name carrying an ESC must not print the raw
        # byte to the terminal.
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "evil\x1b[31m.png")
            result = self._run(missing, "0", "0")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        assert_escapes_escape_character(self, result.stderr)

    def test_success_output_escapes_control_characters_in_path(self):
        # The success header names the path; a shell glob over the reference
        # directory passes a contributor-supplied filename through unchanged.
        with control_named_png() as path:
            result = self._run(path, "0", "0")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        assert_escapes_escape_character(self, result.stdout)

    def test_usage_error_escapes_control_characters_in_arguments(self):
        # argparse builds its own "unrecognized arguments: ..." diagnostic from
        # raw argv, so it bypasses main()'s escaping of the image path. An
        # ESC-bearing extra positional must not print the raw byte.
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            result = self._run(path, "0", "0", "evil\x1b[31m.png")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unrecognized arguments", result.stderr)
        assert_escapes_escape_character(self, result.stderr)


if __name__ == "__main__":
    unittest.main()

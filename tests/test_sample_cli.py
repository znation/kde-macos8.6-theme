"""Tests for the reference-pixel sampling CLI in tools/sample.py.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import sample  # noqa: E402
from error_assertions import assert_escapes_escape_character  # noqa: E402
from png_fixtures import rgb_image, solid_rgb  # noqa: E402
from theme_install import run  # noqa: E402

TOOL = REPO_ROOT / "tools" / "sample.py"


class TestSampleCli(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run the sampling CLI's ``main`` with *args* and capture its output.

        Every assertion here reads only the exit status and the printed
        diagnostics, both of which live in ``sample.main``; spawning
        ``python3 tools/sample.py`` per assertion would pay interpreter
        startup and module import for each one. Calling ``main`` in-process
        exercises the same argument parsing, output and statuses. The script
        entry point itself is covered once by :meth:`test_script_entry_point`.
        """
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(
            stderr
        ):
            try:
                returncode = sample.main(list(args))
            except SystemExit as exc:
                # argparse exits through SystemExit: 0 for --help and 2 for a
                # usage error. ``main`` itself returns its status instead.
                returncode = 0 if exc.code is None else exc.code
                if not isinstance(returncode, int):
                    returncode = 1
        return subprocess.CompletedProcess(
            ["sample", *args], returncode, stdout.getvalue(), stderr.getvalue()
        )

    def _write(self, directory: Path, name: str, data: bytes) -> str:
        path = directory / name
        path.write_bytes(data)
        return str(path)

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
            result = run(
                [sys.executable, str(TOOL), path, "0", "0"],
                capture_output=True,
                text=True,
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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evil\x1b]0;pwned\x07.png"
            _, data = solid_rgb(1, 1)
            path.write_bytes(data)
            result = self._run(str(path), "0", "0")
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

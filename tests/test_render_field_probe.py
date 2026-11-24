"""The render capture's in-session field pixel probe.

``tools/render/field_probe.py`` is the desktop session's capture verifier:
after each ``spectacle`` capture the session runs it on the surface and
recaptures bounded while the wallpaper field is unpainted. Its verdicts and
its direct-script/package agreement are pinned here; the session script's
recapture loop lives in ``tests/test_render_surface_units.py`` and the
desktop mode's wiring in ``tests/test_render_session_modes.py`` and
``tests/test_render_live_capture.py``.
"""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.render.field_probe import main  # noqa: E402
from tools.png.write import encode_png  # noqa: E402

FIELD_COLOR = "63639C"
FIELD_PIXEL = (2, 398)
WIDTH, HEIGHT = 640, 400


def field_png() -> bytes:
    """Return the PNG bytes of a capture whose field pixel is the gate's."""
    return encode_png(WIDTH, HEIGHT, bytes([0x63, 0x63, 0x9C]) * (WIDTH * HEIGHT))


def black_png() -> bytes:
    """Return the PNG bytes of an entirely black capture."""
    return encode_png(WIDTH, HEIGHT, bytes(WIDTH * HEIGHT * 3))


def probe_argv(png, colour=FIELD_COLOR, x=None, y=None) -> list[str]:
    """Build the probe's argv for *png* at the pinned pixel."""
    return [
        str(png), colour,
        str(FIELD_PIXEL[0] if x is None else x),
        str(FIELD_PIXEL[1] if y is None else y),
    ]


def run_probe(argv: list[str]) -> tuple[int, str, str]:
    """Run the pinned callable on *argv* and return (status, stderr, stdout)."""
    stderr, stdout = io.StringIO(), io.StringIO()
    with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
        status = main(argv)
    return status, stderr.getvalue(), stdout.getvalue()


class TestFieldProbe(unittest.TestCase):
    """The probe's verdicts and its empty-stdout contract."""

    def test_a_painted_field_pixel_exits_0_with_empty_stdout_and_stderr(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            status, stderr, stdout = run_probe(probe_argv(png))
            self.assertEqual((0, "", ""), (status, stderr, stdout))

    def test_a_different_field_pixel_exits_1_naming_both_colours(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(black_png())
            status, stderr, stdout = run_probe(probe_argv(png))
            self.assertEqual(1, status)
            self.assertEqual("", stdout)
            self.assertIn(f"#{FIELD_COLOR}", stderr)
            self.assertIn("#000000", stderr)

    def test_a_missing_capture_exits_2_naming_it(self):
        with tempfile.TemporaryDirectory() as root:
            absent = Path(root) / "absent.png"
            status, stderr, stdout = run_probe(probe_argv(absent))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)
            self.assertIn("absent.png", stderr)

    def test_a_non_png_capture_exits_2(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_text("certainly not a PNG", encoding="utf-8")
            status, stderr, stdout = run_probe(probe_argv(png))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)
            self.assertIn("capture.png", stderr)

    def test_a_capture_too_small_for_the_probe_pixel_exits_2(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(encode_png(8, 8, bytes(8 * 8 * 3)))
            status, stderr, stdout = run_probe(probe_argv(png))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)
            self.assertIn("(2, 398)", stderr)

    def test_a_negative_probe_pixel_exits_2(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            status, stderr, stdout = run_probe(probe_argv(png, x=-1, y=0))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)

    def test_the_wrong_argument_count_prints_the_usage_and_exits_2(self):
        # The usage line is the probe's only diagnostic for a misshapen
        # invocation, and the session log shows stderr verbatim, so it must
        # carry the four-argument form and nothing else.
        for argv in ([], ["capture.png", "63639C", "2"],
                     ["capture.png", "63639C", "2", "398", "extra"]):
            with self.subTest(argv=argv):
                status, stderr, stdout = run_probe(argv)
                self.assertEqual(2, status)
                self.assertEqual("", stdout)
                # The literal is the usage line the tool's docstring
                # documents, pinned here so a drift in the constant the
                # probe composes its diagnostic from cannot slip through.
                self.assertEqual(
                    "field_probe: usage: python3 tools/render/field_probe.py"
                    " <png> <RRGGBB> <x> <y>\n",
                    stderr,
                )

    def test_non_integer_coordinates_exits_2_naming_them(self):
        # The coordinates are read as integers, so a stray decimal or word
        # is refused by name before the capture is even opened; the raw
        # texts stay in the diagnostic the session log records.
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            for x_text, y_text in (("2.5", "398"), ("2", "398.0")):
                with self.subTest(x=x_text, y=y_text):
                    status, stderr, stdout = run_probe(
                        [str(png), FIELD_COLOR, x_text, y_text]
                    )
                    self.assertEqual(2, status)
                    self.assertEqual("", stdout)
                    self.assertIn(x_text, stderr)
                    self.assertIn(y_text, stderr)
                    self.assertIn("are not integers", stderr)

    def test_a_six_character_non_hex_colour_exits_2(self):
        # Six characters of the wrong alphabet still fail: the length check
        # alone would accept a colour bytes.fromhex cannot parse.
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            status, stderr, stdout = run_probe(probe_argv(png, colour="63639G"))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)
            self.assertIn("'63639G' is not an RRGGBB colour", stderr)

    def test_a_malformed_colour_exits_2(self):
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            status, stderr, stdout = run_probe(probe_argv(png, colour="6363"))
            self.assertEqual(2, status)
            self.assertEqual("", stdout)

    def test_a_python_only_coordinate_spelling_exits_2_naming_the_text(self):
        # int() would silently accept underscore separators, surrounding
        # whitespace and non-ASCII digits as coordinates; the probe refuses
        # them like every other command-line number in tools/. Each axis is
        # probed so a check of only one coordinate could not pass here.
        with tempfile.TemporaryDirectory() as root:
            png = Path(root) / "capture.png"
            png.write_bytes(field_png())
            spellings = (("1_0", "398"), ("2", "39_8"), (" 2", "398"), ("\u0662", "398"))
            for x_text, y_text in spellings:
                argv = [str(png), FIELD_COLOR, x_text, y_text]
                with self.subTest(spelling=(x_text, y_text)):
                    status, stderr, stdout = run_probe(argv)
                    self.assertEqual(2, status)
                    self.assertEqual("", stdout)
                    self.assertIn(repr(x_text), stderr)
                    self.assertIn(repr(y_text), stderr)


class TestFieldProbeScript(unittest.TestCase):
    """Direct-script invocation agrees with the pinned callable."""

    def test_the_direct_script_and_the_package_callable_agree(self):
        script = Path(repo_root.ROOT) / "tools" / "render" / "field_probe.py"
        with tempfile.TemporaryDirectory() as root:
            captures = (
                ("painted", field_png(), 0),
                ("black", black_png(), 1),
            )
            for name, data, expected in captures:
                png = Path(root) / f"{name}.png"
                png.write_bytes(data)
                argv = probe_argv(png)
                with self.subTest(capture=name):
                    result = subprocess.run(
                        [sys.executable, str(script), *argv],
                        capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(
                        (expected, ""), (result.returncode, result.stdout)
                    )
                    self.assertEqual(run_probe(argv)[1], result.stderr)
            # An underscore coordinate exits 2 the same way, and the direct
            # script's shared plain-ASCII check reaches the bare-run path.
            # The capture exists and its (320, 398) pixel is painted, so a
            # bare int() would exit 0 here and only the refusal can exit 2.
            plain_ascii = Path(root) / "plain_ascii.png"
            plain_ascii.write_bytes(field_png())
            underscored = probe_argv(plain_ascii, x="3_20")
            result = subprocess.run(
                [sys.executable, str(script), *underscored],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual((2, ""), (result.returncode, result.stdout))
            self.assertEqual(run_probe(underscored)[1], result.stderr)
            # A missing capture exits 2 the same way.
            absent = probe_argv(Path(root) / "absent.png")
            result = subprocess.run(
                [sys.executable, str(script), *absent],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual((2, ""), (result.returncode, result.stdout))
            self.assertEqual(run_probe(absent)[1], result.stderr)


if __name__ == "__main__":
    unittest.main()

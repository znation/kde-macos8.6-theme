"""Tests for the fidelity command-line interface in tools/fidelity.py.

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
from cli_fixtures import CliTestCase  # noqa: E402
from error_assertions import assert_escapes_escape_character  # noqa: E402
from png_fixtures import (  # noqa: E402
    _PNG_SIGNATURE,
    _chunk,
    control_named_missing,
    control_named_png,
    make_png,
    rgb_image,
    solid_rgb,
)
from theme_install import run_captured  # noqa: E402

TOOL = REPO_ROOT / "tools" / "fidelity.py"


class TestCli(CliTestCase):
    MAIN = staticmethod(fidelity.main)
    PROGRAM = "fidelity"

    def _write_altered_pair(self, directory: Path) -> tuple[str, str]:
        """Write a 3x3 candidate and a one-pixel-altered copy of it.

        Pixel (1, 0) of the candidate is (20, 0, 60); the altered copy raises
        its green channel to 50, so exactly one of the 27 bytes differs by 50
        (MAE 50/27, differing fraction 1/9). Returns the two paths.
        """
        surface, png = rgb_image(3, 3, lambda x, y: (x * 20, y * 20, 60))
        changed = bytearray(surface.rgb)
        changed[4] = 50
        altered_png = make_png(
            3, 3, [bytes(changed[i : i + 9]) for i in range(0, 27, 9)]
        )
        return (
            self._write(directory, "candidate.png", png),
            self._write(directory, "altered.png", altered_png),
        )

    def _run_png_pair(
        self, candidate_png: bytes, reference_png: bytes
    ) -> subprocess.CompletedProcess:
        """Write two PNGs to a temp dir and run the CLI on them.

        *candidate_png* is written as ``candidate.png`` and *reference_png* as
        ``reference.png``. The temp dir is removed before the result returns,
        which is safe because ``_run`` reads both files before it returns.
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate = self._write(tmpdir, "candidate.png", candidate_png)
            reference = self._write(tmpdir, "reference.png", reference_png)
            return self._run(candidate, reference)

    def _write_padded_surface_pair(self, directory: Path) -> tuple[str, str]:
        """Write a 2x2 surface PNG and a 4x4 reference with a 1px black border.

        The reference embeds the surface at (1, 1), so ``--crop 1,1,2,2``
        selects exactly the surface. Returns the surface path and the
        reference path.
        """
        surface, surface_png = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
        border = bytes([0, 0, 0] * 4)
        rows = [
            border,
            bytes([0, 0, 0] + list(surface.rgb[0:6]) + [0, 0, 0]),
            bytes([0, 0, 0] + list(surface.rgb[6:12]) + [0, 0, 0]),
            border,
        ]
        full_png = make_png(4, 4, rows)
        return (
            self._write(directory, "surface.png", surface_png),
            self._write(directory, "full.png", full_png),
        )

    def _solid_reference(self) -> str:
        """Write a 1x1 black PNG to a temp dir removed when the test ends."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        _, data = solid_rgb(1, 1)
        return self._write(Path(tmp.name), "reference.png", data)

    def _assert_usage_error(
        self, result: subprocess.CompletedProcess, *needles: str
    ) -> None:
        """Assert *result* is a clean exit-2 usage error naming *needles*."""
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        for needle in needles:
            self.assertIn(needle, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def _assert_pass(self, result: subprocess.CompletedProcess) -> None:
        """Assert *result* is a clean exit-0 pass whose stdout says PASS."""
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def _assert_fail(self, result: subprocess.CompletedProcess) -> None:
        """Assert *result* is an exit-1 fidelity failure whose stdout says FAIL."""
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL", result.stdout)

    def test_script_entry_point(self):
        """The CLI still runs end to end as ``python3 tools/fidelity.py``.

        Every other test calls ``fidelity.main`` in-process; this one spawns
        the script so the ``if __name__ == "__main__": sys.exit(main())``
        wrapper and the module's direct-run import path stay covered.
        """
        _, reference = solid_rgb(1, 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(Path(tmp), "reference.png", reference)
            result = run_captured(
                [sys.executable, str(TOOL), path, path],
            )
        self._assert_pass(result)

    def test_pass_and_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            candidate, altered = self._write_altered_pair(tmpdir)
            # The reference is byte-identical to the candidate, so this first
            # run must pass before the altered copy is shown to fail.
            reference = candidate

            same = self._run(candidate, reference)
            self._assert_pass(same)

            different = self._run(candidate, altered)
            self._assert_fail(different)
            self.assertIn("differing pixels: 1 / 9", different.stdout)
            self.assertIn("max channel delta: 50 at (1, 0)", different.stdout)

    def test_tolerance_is_the_default_gate(self):
        # --tolerance alone decides the verdict: a candidate whose worst
        # channel delta equals the requested tolerance passes even though its
        # mean absolute error is non-zero, because no aggregate budget is set
        # by default. Before the fix, --max-mae defaulted to 0 and forced a
        # FAIL here.
        with tempfile.TemporaryDirectory() as tmp:
            candidate, altered = self._write_altered_pair(Path(tmp))

            within = self._run(candidate, altered, "--tolerance", "50")
            self._assert_pass(within)

            outside = self._run(candidate, altered, "--tolerance", "49")
            self._assert_fail(outside)

            default = self._run(candidate, altered)
            self.assertEqual(
                default.returncode, 1, default.stdout + default.stderr
            )

    def test_explicit_budget_replaces_default_gate(self):
        # A budget set with --max-mae is the verdict criterion, not an extra
        # constraint on top of the default all-pixels-within-tolerance gate:
        # the candidate has a 50-level pixel but passes when its MAE (50/27,
        # about 1.85) is within the budget.
        with tempfile.TemporaryDirectory() as tmp:
            candidate, altered = self._write_altered_pair(Path(tmp))

            generous = self._run(candidate, altered, "--max-mae", "2")
            self._assert_pass(generous)

            tight = self._run(candidate, altered, "--max-mae", "1")
            self._assert_fail(tight)

    def test_max_frac_budget_is_the_verdict(self):
        # --max-frac is a budget on its own: with no --max-mae, the verdict is
        # the differing-pixel fraction against the threshold, not the default
        # no-differing-pixel gate. The candidate differs at 1 of 9 pixels
        # (fraction 1/9, about 0.111).
        with tempfile.TemporaryDirectory() as tmp:
            candidate, altered = self._write_altered_pair(Path(tmp))

            generous = self._run(candidate, altered, "--max-frac", "0.12")
            self._assert_pass(generous)

            tight = self._run(candidate, altered, "--max-frac", "0.10")
            self._assert_fail(tight)

    def test_both_budgets_must_be_met(self):
        # --max-mae and --max-frac are both budgets: when both are set the run
        # passes only when each is met, so one generous and one tight budget
        # fails. If the verdict used any() instead of all(), each mixed case
        # here would pass and hide a budget that is not being enforced.
        with tempfile.TemporaryDirectory() as tmp:
            candidate, altered = self._write_altered_pair(Path(tmp))

            both = self._run(
                candidate, altered, "--max-mae", "2", "--max-frac", "0.12"
            )
            self._assert_pass(both)

            for extra in (
                ("--max-mae", "2", "--max-frac", "0.10"),  # frac fails
                ("--max-mae", "1", "--max-frac", "0.12"),  # mae fails
            ):
                with self.subTest(extra=extra):
                    result = self._run(candidate, altered, *extra)
                    self._assert_fail(result)

    def test_reports_worst_delta_location(self):
        a, a_png = solid_rgb(2, 1)
        changed = bytearray(a.rgb)
        changed[3] = 50  # red channel of pixel (1, 0)
        b_png = make_png(2, 1, [bytes(changed)])
        result = self._run_png_pair(a_png, b_png)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("max channel delta: 50 at (1, 0)", result.stdout)

    def test_reports_per_channel_mae(self):
        # The CLI must expose each channel's MAE so a colour cast is visible
        # from a run without importing the module.
        a, a_png = solid_rgb(1, 1)
        b_png = make_png(1, 1, [bytes([10, 0, 0])])
        result = self._run_png_pair(a_png, b_png)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "per-channel MAE (R, G, B): 10.0000 0.0000 0.0000", result.stdout
        )

    def test_crop_region_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate, reference = self._write_padded_surface_pair(Path(tmp))
            result = self._run(candidate, reference, "--crop", "1,1,2,2")
            self._assert_pass(result)

    def test_crop_rectangle_is_echoed_for_reproducibility(self):
        # The reference line prints the cropped size, which does not say where
        # the crop came from, so a transcript cannot be replayed without the
        # rectangle. A run without --crop must not print the line at all.
        reference = self._solid_reference()
        uncropped = self._run(reference, reference)
        with tempfile.TemporaryDirectory() as tmp:
            candidate, padded = self._write_padded_surface_pair(Path(tmp))
            cropped = self._run(candidate, padded, "--crop", "1,1,2,2")
        self.assertEqual(cropped.returncode, 0, cropped.stdout + cropped.stderr)
        self.assertIn("reference crop: 1,1,2,2", cropped.stdout)
        self.assertEqual(
            uncropped.returncode, 0, uncropped.stdout + uncropped.stderr
        )
        self.assertNotIn("reference crop:", uncropped.stdout)

    def test_crop_accepts_whitespace_between_fields(self):
        # A comma-separated rectangle is conventionally written with a space
        # after each comma ("0, 0, 10, 10"); that whitespace is formatting,
        # not a value, so --crop must accept it. The scalar options still
        # reject surrounding whitespace (test_python_literal_numeric_args_rejected).
        with tempfile.TemporaryDirectory() as tmp:
            candidate, reference = self._write_padded_surface_pair(Path(tmp))
            tight = self._run(candidate, reference, "--crop", "1,1,2,2")
            spaced = self._run(candidate, reference, "--crop", "1, 1, 2, 2")
        self.assertEqual(tight.returncode, 0, tight.stdout + tight.stderr)
        self.assertEqual(spaced.returncode, 0, spaced.stdout + spaced.stderr)
        # Identical output proves the spaced form selects the same rectangle.
        self.assertEqual(spaced.stdout, tight.stdout)

    def test_help_documents_exit_status(self):
        # --help must state what each exit status means; the module docstring
        # promises the legend, and a caller scripting the tool cannot tell a
        # tolerance FAIL (1) from a usage or read error (2) without it.
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        help_text = " ".join(result.stdout.split())
        self.assertIn(
            "exit status: 0 when the comparison passes, 1 when it fails, "
            "2 usage or read error",
            help_text,
        )

    def test_malformed_png_is_error(self):
        # A PNG whose IHDR payload is not the 13 bytes the spec requires must
        # fail with the tool's clean error path (exit 2), not a struct.error
        # traceback from the unpack in decode_png.
        short_ihdr = (
            _PNG_SIGNATURE
            + _chunk(
                b"IHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00"
            )
            + _chunk(b"IEND", b"")
        )
        reference = self._solid_reference()
        with tempfile.TemporaryDirectory() as tmp:
            candidate = self._write(Path(tmp), "broken.png", short_ihdr)
            result = self._run(candidate, reference)
            self._assert_usage_error(result, "error")

    def test_decode_error_names_offending_file(self):
        # With two file inputs, the error must say which one could not be
        # decoded; the message is otherwise identical for either ordering.
        reference = self._solid_reference()
        with tempfile.TemporaryDirectory() as tmp:
            candidate = self._write(Path(tmp), "broken.png", b"not a png")
            for first, second in ((candidate, reference), (reference, candidate)):
                with self.subTest(first=first):
                    result = self._run(first, second)
                    self._assert_usage_error(result, "error")
                    self.assertIn(candidate, result.stderr)
                    self.assertNotIn(reference, result.stderr)

    def test_missing_file_is_error(self):
        reference = self._solid_reference()
        result = self._run("/nonexistent.png", reference)
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", result.stderr)

    def test_size_mismatch_is_error(self):
        # A candidate render whose dimensions differ from the reference is the
        # most common real failure. compare() raises FidelityError; main() must
        # report it on the clean exit-2 path rather than leaking a traceback.
        _, small = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
        _, large = rgb_image(4, 4, lambda x, y: (x * 9, y * 9, 5))
        result = self._run_png_pair(small, large)
        self._assert_usage_error(result, "size mismatch")

    def test_crop_outside_reference_is_error(self):
        # A crop with valid syntax can still fall outside the reference; crop()
        # raises FidelityError and main() must report it at exit 2, not crash.
        with tempfile.TemporaryDirectory() as tmp:
            _, reference = rgb_image(2, 2, lambda x, y: (x * 9, y * 9, 5))
            path = self._write(Path(tmp), "reference.png", reference)
            result = self._run(path, path, "--crop", "1,1,2,2")
            self._assert_usage_error(result, "falls outside")

    def test_invalid_numeric_args_are_usage_errors(self):
        # Negative/NaN thresholds silently invert the verdict (a negative
        # tolerance makes every pixel differ, a NaN max-mae always fails), so
        # they must be rejected as usage errors rather than acted on.
        reference = self._solid_reference()
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
                self._assert_usage_error(result, "error")

    def test_python_literal_numeric_args_rejected(self):
        # int()/float() accept underscore digit separators, non-ASCII decimal
        # digits and surrounding whitespace, so --tolerance 1_0 silently means
        # 10 and --max-frac ١ means 1. A command-line number is plain ASCII
        # text; each of these must be a usage error naming the rejection, not
        # a value that quietly changes the argument.
        reference = self._solid_reference()
        base = [reference, reference]
        for extra in (
            ["--tolerance", "1_0"],
            ["--tolerance", " 255 "],
            ["--max-mae", "1_0.5"],
            ["--max-frac", "\u0661"],
            ["--crop", "1_0,0,1,1"],
            ["--crop", "\u0661,0,1,1"],
        ):
            with self.subTest(extra=extra):
                result = self._run(*base, *extra)
                self._assert_usage_error(result, "plain ASCII")

    def test_non_numeric_threshold_is_usage_error(self):
        # _is_plain_ascii_number accepts any ASCII text without separators or
        # surrounding space, so a word such as "abc" passes it and reaches
        # float(). Without _finite_float's ValueError handler argparse would
        # still exit 2, but with its generic "invalid <type> value" fallback
        # that names neither the option nor the value; the threshold must
        # instead report which option was not a number.
        reference = self._solid_reference()
        base = [reference, reference]
        for option, value in (("--max-mae", "abc"), ("--max-frac", "abc")):
            with self.subTest(option=option):
                result = self._run(*base, option, value)
                self._assert_usage_error(
                    result, f"{option} must be a number: {value!r}"
                )

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

    def test_tolerance_above_channel_range_rejected(self):
        # A per-channel delta is at most 255, so a larger tolerance can never
        # mark a pixel as differing and would silently disable that metric.
        reference = self._solid_reference()
        for value in ("256", "1000"):
            with self.subTest(value=value):
                result = self._run(reference, reference, "--tolerance", value)
                self._assert_usage_error(result, "255")

    def test_max_mae_above_channel_range_rejected(self):
        # Mean absolute error averages per-channel deltas, so it can never
        # exceed 255; a larger threshold would silently always pass.
        reference = self._solid_reference()
        for value in ("255.5", "256", "1e9"):
            with self.subTest(value=value):
                result = self._run(reference, reference, "--max-mae", value)
                self._assert_usage_error(result, "255")

    def test_valid_numeric_boundaries_accepted(self):
        reference = self._solid_reference()
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
        self._assert_pass(result)

    def test_verdict_line_echoes_budget_values(self):
        # The verdict line is the run's audit record: it echoes the parsed
        # --max-mae/--max-frac values, or "unset" when the option was absent,
        # so a transcript can be replayed. No other test asserts those fields,
        # so a format regression (.4f -> .2f, .6f -> .3f) or a swapped label
        # would pass every other test. The fractional case also pins the
        # documented four- and six-decimal rounding.
        reference = self._solid_reference()
        cases = (
            ((), "PASS: max-mae=unset max-frac=unset tolerance=0"),
            (
                ("--max-mae", "2"),
                "PASS: max-mae=2.0000 max-frac=unset tolerance=0",
            ),
            (
                ("--max-frac", "0.12"),
                "PASS: max-mae=unset max-frac=0.120000 tolerance=0",
            ),
            (
                ("--max-mae", "1.5", "--max-frac", "0.1234567"),
                "PASS: max-mae=1.5000 max-frac=0.123457 tolerance=0",
            ),
        )
        for extra, verdict in cases:
            with self.subTest(extra=extra):
                result = self._run(reference, reference, *extra)
                self.assertEqual(
                    result.returncode, 0, result.stdout + result.stderr
                )
                self.assertIn(verdict, result.stdout)

    def test_error_message_escapes_control_characters_in_path(self):
        # read_png embeds the path in its error message, and the documented
        # workflow hands this tool a reference file from the contributor-owned
        # screenshot directory, so a missing name carrying an ESC must not
        # print the raw byte to the terminal.
        with control_named_missing() as missing:
            result = self._run(missing, missing)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        assert_escapes_escape_character(self, result.stderr)

    def test_success_output_escapes_control_characters_in_paths(self):
        # The success lines name both paths; a shell glob over the reference
        # directory passes a contributor-supplied filename through unchanged.
        with control_named_png() as path:
            result = self._run(path, path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        assert_escapes_escape_character(self, result.stdout)

    def test_usage_error_escapes_control_characters_in_arguments(self):
        # argparse builds its own "unrecognized arguments: ..." diagnostic from
        # raw argv, so it bypasses main()'s escaping of the candidate and
        # reference paths. A shell glob over the contributor-owned screenshot
        # directory can put an ESC-bearing name there as an extra positional
        # argument, which must not print the raw byte to the terminal.
        reference = self._solid_reference()
        extra = "evil\x1b[31m.png"
        result = self._run(reference, reference, extra)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("unrecognized arguments", result.stderr)
        assert_escapes_escape_character(self, result.stderr)


if __name__ == "__main__":
    unittest.main()

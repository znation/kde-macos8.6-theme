"""Tests for the fidelity command-line interface in tools/fidelity.py.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v

The crop options are covered in ``test_fidelity_cli_crops``; this module keeps
the verdict and budget gate, the usage and numeric errors, the read errors and
the terminal escaping.
"""

from __future__ import annotations

import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.error_assertions import assert_escapes_escape_character  # noqa: E402
from support.fidelity_cli_case import FidelityCliTestCase  # noqa: E402
from support.png_fixtures import (  # noqa: E402
    _chunk,
    control_named_missing,
    control_named_png,
    make_png,
    png_stream,
    rgb_image,
    solid_rgb,
)
from support.symlink_fixtures import symlinked_repo  # noqa: E402
from tools import fidelity  # noqa: E402


class TestCli(FidelityCliTestCase):
    """The fidelity gate, its usage errors, read errors and escaping."""

    def test_script_entry_point(self):
        """The CLI still runs end to end as ``python3 tools/fidelity.py``.

        Every other test calls ``fidelity.main`` in-process; this one spawns
        the script so the ``if __name__ == "__main__": sys.exit(main())``
        wrapper and the module's direct-run import path stay covered.
        """
        _, reference = solid_rgb(1, 1)
        tmp = self._tmp_dir()
        path = self._write(tmp, "reference.png", reference)
        result = self._run_script(path, path)
        self._assert_pass(result)

    def test_pass_and_fail(self):
        candidate, altered = self._write_altered_pair(self._tmp_dir())
        # The reference is byte-identical to the candidate, so this first
        # run must pass before the altered copy is shown to fail.
        reference = candidate

        same = self._run(candidate, reference)
        self._assert_pass(same)

        different = self._run(candidate, altered)
        self._assert_fail(different)
        self.assertIn("differing pixels: 1 / 9", different.stdout)
        self.assertIn("max channel delta: 50 at (1, 0)", different.stdout)

    def test_alpha_difference_fails_the_default_gate(self):
        # A candidate matching the reference's RGB but fully transparent must
        # not pass the byte-exact gate: the alpha byte is part of the pixel.
        # Before alpha was compared, both images decoded to the same RGB bytes
        # and this pair passed with zero differing pixels.
        clear = make_png(
            2, 1, [bytes([10, 20, 30, 0, 10, 20, 30, 0])], color_type=6
        )
        opaque = make_png(
            2, 1, [bytes([10, 20, 30, 255, 10, 20, 30, 255])], color_type=6
        )
        result = self._run_png_pair(clear, opaque)
        self._assert_fail(result)
        self.assertIn("differing pixels: 2 / 2", result.stdout)
        self.assertIn("max channel delta: 255 at (0, 0)", result.stdout)
        self.assertIn(
            "per-channel MAE (R, G, B, A): 0.0000 0.0000 0.0000 255.0000",
            result.stdout,
        )

    def test_tolerance_is_the_default_gate(self):
        # --tolerance alone decides the verdict: a candidate whose worst
        # channel delta equals the requested tolerance passes even though its
        # mean absolute error is non-zero, because no aggregate budget is set
        # by default. Before the fix, --max-mae defaulted to 0 and forced a
        # FAIL here.
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)

        within = self._run(candidate, altered, "--tolerance", "50")
        self._assert_pass(within)

        outside = self._run(candidate, altered, "--tolerance", "49")
        self._assert_fail(outside)

        default = self._run(candidate, altered)
        self._assert_fail(default)

    def test_explicit_budget_replaces_default_gate(self):
        # A budget set with --max-mae is the verdict criterion, not an extra
        # constraint on top of the default all-pixels-within-tolerance gate:
        # the candidate has a 50-level pixel but passes when its MAE (50/36,
        # about 1.39 over the 3x3 RGB and alpha channels) is within the budget.
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)

        generous = self._run(candidate, altered, "--max-mae", "2")
        self._assert_pass(generous)

        tight = self._run(candidate, altered, "--max-mae", "1")
        self._assert_fail(tight)

    def test_max_frac_budget_is_the_verdict(self):
        # --max-frac is a budget on its own: with no --max-mae, the verdict is
        # the differing-pixel fraction against the threshold, not the default
        # no-differing-pixel gate. The candidate differs at 1 of 9 pixels
        # (fraction 1/9, about 0.111).
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)

        generous = self._run(candidate, altered, "--max-frac", "0.12")
        self._assert_pass(generous)

        tight = self._run(candidate, altered, "--max-frac", "0.10")
        self._assert_fail(tight)

    def test_both_budgets_must_be_met(self):
        # --max-mae and --max-frac are both budgets: when both are set the run
        # passes only when each is met, so one generous and one tight budget
        # fails. If the verdict used any() instead of all(), each mixed case
        # here would pass and hide a budget that is not being enforced.
        tmp = self._tmp_dir()
        candidate, altered = self._write_altered_pair(tmp)

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
        self._assert_fail(result)
        self.assertIn("max channel delta: 50 at (1, 0)", result.stdout)

    def test_reports_per_channel_mae(self):
        # The CLI must expose each channel's MAE so a colour cast is visible
        # from a run without importing the module.
        _, a_png = solid_rgb(1, 1)
        b_png = make_png(1, 1, [bytes([10, 0, 0])])
        result = self._run_png_pair(a_png, b_png)
        self._assert_fail(result)
        self.assertIn(
            "per-channel MAE (R, G, B, A): 10.0000 0.0000 0.0000 0.0000",
            result.stdout,
        )

    def test_help_documents_exit_status(self):
        # --help must state what each exit status means; the module docstring
        # promises the legend, and a caller scripting the tool cannot tell a
        # tolerance FAIL (1) from a usage or read error (2) without it.
        result = self._run("--help")
        self._assert_success(result)
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
        short_ihdr = png_stream(
            _chunk(
                b"IHDR", b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00"
            ),
            _chunk(b"IEND", b""),
        )
        reference = self._solid_reference()
        tmp = self._tmp_dir()
        candidate = self._write(tmp, "broken.png", short_ihdr)
        result = self._run(candidate, reference)
        self._assert_usage_error(result, "error")

    def test_decode_error_names_offending_file(self):
        # With two file inputs, the error must say which one could not be
        # decoded; the message is otherwise identical for either ordering.
        reference = self._solid_reference()
        tmp = self._tmp_dir()
        candidate = self._write(tmp, "broken.png", b"not a png")
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
        # is_plain_ascii_number accepts any ASCII text without separators or
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
                self._assert_success(result)
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
        self._assert_success(result)
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

    def test_rejects_a_reference_that_symlinks_outside_the_repository(self):
        # A checked-in symlink at a reference name can point at a private
        # image; comparing against it would leak its pixels through the
        # worst-delta report and the verdict. It is refused before the read.
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(self._tmp_dir(), "reference.png", data)
        candidate = self._write(self._tmp_dir(), "candidate.png", data)
        with mock.patch.object(fidelity, "ROOT", str(root)):
            result = self._run(candidate, str(link))
        self._assert_usage_error(result, "resolves outside", str(root))
        self.assertNotIn("max channel delta", result.stdout)

    def test_rejects_a_candidate_that_symlinks_outside_the_repository(self):
        # The guard sits in _read_source, so it covers the candidate too, and
        # both the whole-image and the cropped read paths.
        _, data = solid_rgb(2, 2)
        root, link = symlinked_repo(self._tmp_dir(), "candidate.png", data)
        reference = self._write(self._tmp_dir(), "reference.png", data)
        for extra in ((), ("--candidate-crop", "0,0,1,1")):
            with self.subTest(extra=extra), mock.patch.object(fidelity, "ROOT", str(root)):
                result = self._run(str(link), reference, *extra)
            self._assert_usage_error(result, "resolves outside", str(root))
            self.assertNotIn("max channel delta", result.stdout)

    def test_reads_a_symlink_that_stays_inside_the_repository(self):
        _, data = solid_rgb(1, 1)
        root, link = symlinked_repo(
            self._tmp_dir(), "reference.png", data, target="real/target.png"
        )
        candidate = self._write(self._tmp_dir(), "candidate.png", data)
        with mock.patch.object(fidelity, "ROOT", str(root)):
            result = self._run(candidate, str(link))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

"""Tests for tools/cli.py -- the shared argument-parsing helpers.

``tools/fidelity.py``, ``tools/sample.py``, ``tools/render_surface.py`` and
``tools/apply_theme.py`` parse their command lines through this module, but
their own tests reach the helpers only through a tool's usage diagnostic.
These tests pin the helpers' contracts directly, so a
change to the plain-ASCII predicate, the option-named rejection or the
control-character escaping of argparse's own diagnostics is caught here
instead of through one tool and not the others.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import argparse
import contextlib
import io
import unittest
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools import cli


class TestIsPlainAsciiNumber(unittest.TestCase):
    def test_accepts_plain_ascii_text(self):
        # The predicate judges the *text*, not whether it parses as a number:
        # numericness is the caller's parser's job, so "nan"/"inf" and an empty
        # string are plain text here and rejected later by the parse.
        for value in ("0", "1", "-1", "+5", "255", "1.5", "1e3", "nan", "inf", ""):
            with self.subTest(value=value):
                self.assertTrue(cli.is_plain_ascii_number(value))

    def test_rejects_underscore_digit_separators(self):
        # int("1_0") is 10, so a CLI that accepted the text would silently name
        # a different value than the one typed.
        for value in ("1_0", "1_0.5", "_1", "1_"):
            with self.subTest(value=value):
                self.assertFalse(cli.is_plain_ascii_number(value))

    def test_rejects_non_ascii_decimal_digits(self):
        # Arabic-Indic and fullwidth digits are decimal digits to int()/float(),
        # so without the ASCII check "١٢" would parse as 12.
        for value in ("\u0661\u0662", "\uff11\uff12", "1\u0660"):
            with self.subTest(value=value):
                self.assertFalse(cli.is_plain_ascii_number(value))

    def test_rejects_surrounding_whitespace(self):
        # Whitespace around a scalar option signals a quoting mistake; only the
        # crop parser strips fields before calling this.
        for value in (" 1", "1 ", "\t1", "1\n", " 1 "):
            with self.subTest(value=value):
                self.assertFalse(cli.is_plain_ascii_number(value))


class TestPlainNumber(unittest.TestCase):
    def test_returns_the_parsed_int_and_float(self):
        self.assertEqual(
            cli.plain_number("42", "--tolerance", "integer", "an", int), 42
        )
        self.assertEqual(
            cli.plain_number("1.5", "--max-mae", "number", "a", float), 1.5
        )

    def test_python_only_spelling_is_rejected_naming_the_option(self):
        # The diagnostic must name the option and call the text non-plain, not
        # fall through to the parser's ValueError wording.
        for value in ("1_0", "\u0661", " 1"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError) as caught:
                    cli.plain_number(value, "--tolerance", "integer", "an", int)
                message = str(caught.exception)
                self.assertIn("--tolerance", message)
                self.assertIn("plain ASCII integer", message)

    def test_unparsable_text_names_the_option_and_article(self):
        with self.assertRaises(argparse.ArgumentTypeError) as caught:
            cli.plain_number("abc", "--tolerance", "integer", "an", int)
        self.assertEqual(
            str(caught.exception), "--tolerance must be an integer: 'abc'"
        )

    def test_the_article_and_noun_are_interpolated(self):
        # A float option passes article "a" and noun "number"; pinning both
        # spellings catches a hardcoded "an integer" in the helper.
        with self.assertRaises(argparse.ArgumentTypeError) as caught:
            cli.plain_number("abc", "--max-mae", "number", "a", float)
        self.assertEqual(
            str(caught.exception), "--max-mae must be a number: 'abc'"
        )

    def test_parse_is_not_called_for_a_rejected_spelling(self):
        # The plain-text check runs first: a parser that would accept "1_0"
        # must never see it, or the rejection could be bypassed by a lenient
        # parse callable.
        calls = []

        def recording_parse(value: str) -> int:
            calls.append(value)
            return int(value)

        with self.assertRaises(argparse.ArgumentTypeError):
            cli.plain_number("1_0", "--x", "integer", "an", recording_parse)
        self.assertEqual(calls, [])

    def test_a_parse_failure_chains_the_original_value_error(self):
        # ``from exc`` keeps the stdlib's reason (e.g. "invalid literal") on
        # the cause, so a caller can still see why the text did not parse.
        with self.assertRaises(argparse.ArgumentTypeError) as caught:
            cli.plain_number("abc", "--tolerance", "integer", "an", int)
        self.assertIsInstance(caught.exception.__cause__, ValueError)


class TestPositiveInt(unittest.TestCase):
    def test_returns_the_parsed_integer(self):
        self.assertEqual(cli.positive_int("--width")("7"), 7)

    def test_zero_and_negative_are_rejected_naming_the_option(self):
        for value in ("0", "-3"):
            with self.subTest(value=value):
                with self.assertRaises(argparse.ArgumentTypeError) as caught:
                    cli.positive_int("--height")(value)
                self.assertEqual(
                    str(caught.exception),
                    f"--height must be at least 1: {value!r}",
                )

    def test_plain_ascii_check_is_delegated_to_plain_number(self):
        # A Python-only spelling must be rejected with the plain-ASCII
        # wording, so the helper does not parse it as a different value.
        with self.assertRaises(argparse.ArgumentTypeError) as caught:
            cli.positive_int("--width")("1_0")
        self.assertEqual(
            str(caught.exception),
            "--width must be a plain ASCII integer: '1_0'",
        )

    def test_the_option_is_interpolated(self):
        # Two options share the helper; the returned parser must carry the
        # option it was built with, not a hardcoded one.
        with self.assertRaises(argparse.ArgumentTypeError) as caught:
            cli.positive_int("--height")("0")
        self.assertIn("--height", str(caught.exception))


class TestEscapingArgumentParser(unittest.TestCase):
    def _run(self, call):
        """Call *call* and return its SystemExit status and stderr text."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as caught:
                call()
        return caught.exception.code, stderr.getvalue()

    def test_error_method_escapes_control_characters(self):
        # argparse formats some diagnostics from raw argv; error() is the one
        # boundary every such message passes through, so escaping here covers
        # all of them at once.
        parser = cli.EscapingArgumentParser(prog="tool")
        code, err = self._run(lambda: parser.error("bad \x1b[31m flag"))
        self.assertEqual(code, 2)
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)
        # The ordinary text still names the problem.
        self.assertIn("bad", err)
        self.assertIn("flag", err)

    def test_unrecognized_argument_is_escaped(self):
        # The documented workflow fills argv from a shell glob over the
        # contributor-owned screenshot directory, so an ESC in an extra
        # positional must not reach the terminal raw.
        parser = cli.EscapingArgumentParser(prog="tool")
        code, err = self._run(
            lambda: parser.parse_args(["evil\x1b[31m.png"])
        )
        self.assertEqual(code, 2)
        self.assertIn("unrecognized arguments", err)
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)

    def test_ordinary_usage_error_is_unchanged(self):
        parser = cli.EscapingArgumentParser(prog="tool")
        code, err = self._run(lambda: parser.error("no such option"))
        self.assertEqual(code, 2)
        self.assertIn("no such option", err)


class TestReportError(unittest.TestCase):
    def _report(self, tool, message):
        """Call report_error and return its status and stderr text."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = cli.report_error(tool, message)
        return status, stderr.getvalue()

    def test_prefixes_the_tool_name_and_returns_two(self):
        # Both CLIs return report_error()'s result directly as the process
        # exit status, so the helper must supply the 2 itself.
        status, err = self._report("sample", "could not be read")
        self.assertEqual(status, 2)
        self.assertEqual(err, "sample: error: could not be read\n")

    def test_escapes_control_characters_in_the_message(self):
        # The message often carries a contributor-supplied path; an ESC or
        # newline must not reach the terminal raw or forge a second line.
        status, err = self._report("fidelity", "bad \x1b[31m path\nname")
        self.assertEqual(status, 2)
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)
        self.assertIn("\\u000a", err)


class TestReportMissingTool(unittest.TestCase):
    def _report(self, tool, required, present=()):
        """Call report_missing_tool with which() finding only *present*."""
        stderr = io.StringIO()
        with mock.patch.object(
            cli.shutil, "which", lambda name: name if name in present else None
        ):
            with contextlib.redirect_stderr(stderr):
                status = cli.report_missing_tool(tool, required)
        return status, stderr.getvalue()

    def test_returns_none_and_prints_nothing_when_all_are_present(self):
        # None means "proceed": the callers continue only when every required
        # tool was found, so the helper must not report a success line.
        status, err = self._report("sample", ("a", "b"), present=("a", "b"))
        self.assertIsNone(status)
        self.assertEqual(err, "")

    def test_names_the_first_missing_tool_in_order(self):
        # The tools depend on the order, so the first absent name is the one
        # reported even when a later one is missing too.
        status, err = self._report(
            "render_surface", ("a", "b", "c"), present=("a", "c")
        )
        self.assertEqual(status, 2)
        self.assertEqual(
            err, "render_surface: error: required tool not found on PATH: b\n"
        )

    def test_escapes_control_characters_in_the_tool_name(self):
        status, err = self._report("apply_theme", ("bad\x1b[31m",))
        self.assertEqual(status, 2)
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)


class TestReportFailure(unittest.TestCase):
    def _report(self, message, log=None):
        """Call report_failure and return its status and stderr text."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = cli.report_failure("apply_theme", message, log)
        return status, stderr.getvalue()

    def _cr_preceded_log(self, body):
        """Write *body* padded to one tail window, preceded by ``f\\r``.

        The window's first byte then lands exactly on ``body[0]`` with a
        ``\\r`` immediately before it, so a test can pin how that carriage
        return at the window's left edge is treated.
        """
        body += b"x" * (cli._LOG_TAIL_BYTES - len(body))
        log = make_tmp_dir(self) / "cmd.log"
        log.write_bytes(b"f\r" + body)
        self.assertEqual(log.stat().st_size, cli._LOG_TAIL_BYTES + 2)
        return log

    def test_prefixes_the_tool_name_and_returns_one(self):
        # The tools that call this return its result directly as the process
        # exit status, so the helper must supply the 1 itself.
        status, err = self._report("make install exited 2")
        self.assertEqual(status, 1)
        self.assertEqual(err, "apply_theme: error: make install exited 2\n")

    def test_escapes_control_characters_in_the_message(self):
        status, err = self._report("bad \x1b[31m path\nname")
        self.assertEqual(status, 1)
        self.assertNotIn("\x1b", err)
        self.assertIn("\\u001b", err)
        self.assertIn("\\u000a", err)

    def test_appends_the_log_tail_indented_and_escaped(self):
        log = make_tmp_dir(self) / "cmd.log"
        log.write_text("one\nbad \x1b[31m\ntwo\n", encoding="utf-8")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertEqual(
            err,
            "apply_theme: error: command failed\n"
            "  one\n"
            "  bad \\u001b[31m\n"
            "  two\n",
        )

    def test_keeps_only_the_last_twelve_log_lines(self):
        log = make_tmp_dir(self) / "cmd.log"
        log.write_text(
            "".join(f"line {i}\n" for i in range(15)), encoding="utf-8"
        )
        _, err = self._report("command failed", log)
        self.assertNotIn("line 2\n", err)
        self.assertIn("  line 3\n", err)
        self.assertIn("  line 14\n", err)

    def test_a_missing_log_adds_no_tail(self):
        log = make_tmp_dir(self) / "absent.log"
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertEqual(err, "apply_theme: error: command failed\n")

    def test_reads_only_a_bounded_tail_of_a_huge_log(self):
        # A failing external command writes its log for up to its timeout; the
        # helper must not load that file whole just to print twelve lines. The
        # log is one unterminated line, so the bounded read still shows it, but
        # only the last _LOG_TAIL_BYTES of it.
        log = make_tmp_dir(self) / "cmd.log"
        log.write_text("A" * (cli._LOG_TAIL_BYTES * 4), encoding="utf-8")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("A", err)
        self.assertLess(len(err), cli._LOG_TAIL_BYTES * 2)

    def test_tail_of_a_log_larger_than_the_window_keeps_the_last_lines(self):
        # The window boundary falls mid-line here; the last twelve complete
        # lines must still be the ones reported.
        log = make_tmp_dir(self) / "cmd.log"
        lines = [f"line {i} " + "x" * 100 for i in range(2000)]
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertGreater(log.stat().st_size, cli._LOG_TAIL_BYTES)
        _, err = self._report("command failed", log)
        self.assertIn(f"  {lines[-1]}\n", err)
        self.assertIn(f"  {lines[-12]}\n", err)
        self.assertNotIn(lines[-13], err)

    def test_tail_window_starting_after_a_carriage_return_keeps_its_first_line(self):
        # A log's bounded window can begin right after a `\r` (a progress line
        # the command rewrote in place). `splitlines` treats `\r` as a line
        # break, so that byte is a line boundary too: the window's first line
        # is complete and must not be dropped as a partial one. Build a log
        # whose byte immediately before the read window is exactly `\r`.
        log = self._cr_preceded_log(b"FIRST\nSECOND\nTHIRD\n")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("  FIRST\n", err)

    def test_tail_window_opening_on_a_crlf_newline_drops_the_break(self):
        # A window can open on the `\n` half of a `\r\n` pair. `splitlines`
        # yields an empty first element there, but that empty line is the tail
        # of the break whose `\r` lies outside the window -- not a log line --
        # so it must be dropped like any other partial first line.
        log = self._cr_preceded_log(b"\nFIRST\nSECOND\nTHIRD\n")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertEqual(err.splitlines()[1], "  FIRST")

    def test_an_exotic_break_byte_inside_a_line_does_not_split_it(self):
        # Only CR and LF end a log line. `str.splitlines` also breaks on a
        # vertical tab (and the other C0/C1 separators), which would split one
        # line into two and, at the twelve-line tail boundary, push a complete
        # line out of the diagnostic. The line must stay whole, with the tab
        # escaped by the shared escaper, and no complete line may be lost.
        log = make_tmp_dir(self) / "cmd.log"
        lines = [f"line {i}" for i in range(13)]
        lines[1] = "line 1a\x0bline 1b"
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("  line 1a\\u000bline 1b\n", err)
        self.assertNotIn("  line 0\n", err)
        self.assertIn("  line 12\n", err)


if __name__ == "__main__":
    unittest.main()

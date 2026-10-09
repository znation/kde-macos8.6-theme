"""Tests for tools/cli.py -- the shared argument-parsing helpers.

``tools/fidelity.py`` and ``tools/sample.py`` both parse their command lines
through this module, but their own tests reach the helpers only through a
tool's usage diagnostic. These tests pin the helpers' contracts directly, so a
change to the plain-ASCII predicate, the option-named rejection or the
control-character escaping of argparse's own diagnostics is caught here
instead of through one tool and not the other.

Run with the project's check harness (stdlib unittest):
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import argparse
import contextlib
import io
import unittest

import repo_root  # noqa: F401  (puts the repository root on sys.path)
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


if __name__ == "__main__":
    unittest.main()

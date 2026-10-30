"""Tests for tools/diagnostics.py -- the shared reporting contract.

``tools/fidelity.py``, ``tools/sample.py``, ``tools/apply_theme.py``,
``tools/local_hook.py`` and ``tools/render_surface.py`` report a failure
through this module, but their own tests reach the helpers only through a
tool's diagnostic. These tests pin the helpers' contracts directly: the
``<tool>: error:`` line, the 2-for-input / 1-for-command exit statuses, the
control-character escaping, the non-str type guards, the ``<tool>: note:``
line and the stream it is written to, and the bounded log tail. The log-tail
cases pin
the CR/LF line-boundary rules that several BUGS-FIXED.md entries fixed.

Argument parsing lives in the sibling ``tools/argument_parsing.py`` and is pinned by
``tests/test_argument_parsing.py``.

Run with the project's check harness (stdlib unittest)::

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from support.tmp_dir import make_tmp_dir
from tools import diagnostics


class TestReportError(unittest.TestCase):
    def _report(self, tool, message):
        """Call report_error and return its status and stderr text."""
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = diagnostics.report_error(tool, message)
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

    def test_non_str_tool_or_message_raises_naming_type(self):
        # A non-str argument must be rejected by type, not mis-formatted or
        # silently coerced; the diagnostic names the offending parameter and
        # type. escape_controls() rejects text the same way.
        for kwargs, name, parameter in (
            ({"tool": 42, "message": "m"}, "int", "tool"),
            ({"tool": "t", "message": b"nope"}, "bytes", "message"),
        ):
            with self.subTest(parameter=parameter, value=kwargs[parameter]):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"^report_error\(\) requires str: {parameter} must be str, "
                    rf"not {name}$",
                ):
                    diagnostics.report_error(**kwargs)


class TestReportMissingTool(unittest.TestCase):
    def test_bare_str_required_and_non_str_arguments_raise(self):
        for args, pattern in (
            (("t", "git"), r"required must not be a bare str$"),
            (("t", b"git"), r"required must not be a bare bytes$"),
            ((7, ["git"]), r"tool must be str, not int$"),
            (("t", ["git", 3]), r"required item must be str, not int$"),
        ):
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, pattern):
                    diagnostics.report_missing_tool(*args)

    def _report(self, tool, required, present=()):
        """Call report_missing_tool with which() finding only *present*."""
        stderr = io.StringIO()
        with mock.patch.object(
            diagnostics.shutil, "which", lambda name: name if name in present else None
        ):
            with contextlib.redirect_stderr(stderr):
                status = diagnostics.report_missing_tool(tool, required)
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
            status = diagnostics.report_failure("apply_theme", message, log)
        return status, stderr.getvalue()

    def _window_preceded_log(self, preceding, body):
        """Write *body* padded to one tail window, preceded by *preceding*.

        The window's first byte then lands exactly on ``body[0]`` with
        *preceding*'s last byte immediately before it, so a test can pin how
        the byte at the window's left edge is treated.
        """
        body += b"x" * (diagnostics._LOG_TAIL_BYTES - len(body))
        log = make_tmp_dir(self) / "cmd.log"
        log.write_bytes(preceding + body)
        self.assertEqual(
            log.stat().st_size, len(preceding) + diagnostics._LOG_TAIL_BYTES
        )
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

    def test_non_str_tool_or_message_raises_naming_type(self):
        # Same type contract as report_error(); a caller passes an exception's
        # str() or a diagnostic it built itself, never a bare object.
        for kwargs, name, parameter in (
            ({"tool": 42, "message": "m"}, "int", "tool"),
            ({"tool": "t", "message": b"nope"}, "bytes", "message"),
        ):
            with self.subTest(parameter=parameter, value=kwargs[parameter]):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"^report_failure\(\) requires str: {parameter} must be str, "
                    rf"not {name}$",
                ):
                    diagnostics.report_failure(**kwargs)

    def test_non_path_log_raises_naming_type(self):
        # A str log would silently skip the tail (str has no .is_file), hiding
        # the command output the caller meant to attach, so only Path is
        # accepted.
        with self.assertRaisesRegex(
            ValueError,
            r"^report_failure\(\) requires pathlib\.Path or None: log must be "
            r"Path or None, not str$",
        ):
            diagnostics.report_failure("t", "m", "cmd.log")

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

    def test_a_log_read_failure_keeps_the_command_error_and_reports_the_log_error(self):
        log = make_tmp_dir(self) / "cmd.log"
        log.write_text("available at preflight", encoding="utf-8")
        with mock.patch.object(Path, "open", side_effect=PermissionError("denied")):
            status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("apply_theme: error: command failed\n", err)
        self.assertIn("  log could not be read: denied\n", err)

    def test_an_empty_log_adds_no_tail(self):
        # A command can fail without writing anything -- it never started, or
        # produced no output -- leaving the log file it was pointed at empty.
        # The tail reader must return no lines rather than one blank one, so
        # the diagnostic stays just the message with no stray indent.
        log = make_tmp_dir(self) / "cmd.log"
        log.write_bytes(b"")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertEqual(err, "apply_theme: error: command failed\n")

    def test_reads_only_a_bounded_tail_of_a_huge_log(self):
        # A failing external command writes its log for up to its timeout; the
        # helper must not load that file whole just to print twelve lines. The
        # log is one unterminated line, so the bounded read still shows it, but
        # only the last _LOG_TAIL_BYTES of it.
        log = make_tmp_dir(self) / "cmd.log"
        log.write_text("A" * (diagnostics._LOG_TAIL_BYTES * 4), encoding="utf-8")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("A", err)
        self.assertLess(len(err), diagnostics._LOG_TAIL_BYTES * 2)

    def test_tail_of_a_log_larger_than_the_window_keeps_the_last_lines(self):
        # The window boundary falls mid-line here; the last twelve complete
        # lines must still be the ones reported.
        log = make_tmp_dir(self) / "cmd.log"
        lines = [f"line {i} " + "x" * 100 for i in range(2000)]
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertGreater(log.stat().st_size, diagnostics._LOG_TAIL_BYTES)
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
        log = self._window_preceded_log(b"f\r", b"FIRST\nSECOND\nTHIRD\n")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("  FIRST\n", err)

    def test_tail_window_opening_on_a_crlf_newline_drops_the_break(self):
        # A window can open on the `\n` half of a `\r\n` pair. `splitlines`
        # yields an empty first element there, but that empty line is the tail
        # of the break whose `\r` lies outside the window -- not a log line --
        # so it must be dropped like any other partial first line.
        log = self._window_preceded_log(b"f\r", b"\nFIRST\nSECOND\nTHIRD\n")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertEqual(err.splitlines()[1], "  FIRST")

    def test_tail_window_starting_at_a_line_boundary_keeps_its_first_line(self):
        # A window can begin exactly at a line boundary: the byte just before
        # it is the `\n` that ended the previous line. That byte is a break,
        # so the window's first line is complete and must be kept; without the
        # `previous == b"\n"` arm it is read as a partial first line and a
        # complete line is dropped from the diagnostic.
        log = self._window_preceded_log(b"f\n", b"FIRST\nSECOND\nTHIRD\n")
        status, err = self._report("command failed", log)
        self.assertEqual(status, 1)
        self.assertIn("  FIRST\n", err)

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


class TestReportNote(unittest.TestCase):
    def _note(self, message, *, err=False):
        """Call report_note and return its stdout and stderr text."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            diagnostics.report_note("apply_gtk", message, err=err)
        return stdout.getvalue(), stderr.getvalue()

    def test_prefixes_the_tool_name_and_goes_to_stdout(self):
        # A note is operator output for a run that succeeded, so it belongs
        # on stdout unless the caller asks for stderr.
        out, err = self._note("restart running GTK applications")
        self.assertEqual(
            out, "apply_gtk: note: restart running GTK applications\n"
        )
        self.assertEqual(err, "")

    def test_err_sends_the_note_to_stderr_instead(self):
        # apply_theme's notes describe failed optional steps and sit beside
        # its error diagnostics on stderr; nothing may reach stdout.
        out, err = self._note("kvantummanager is absent", err=True)
        self.assertEqual(out, "")
        self.assertEqual(err, "apply_gtk: note: kvantummanager is absent\n")

    def test_escapes_control_characters_in_the_message(self):
        # Notes carry contributor-supplied paths too; an ESC or newline must
        # not reach the terminal raw or forge a second line.
        out, _ = self._note("bad \x1b[31m path\nname")
        self.assertNotIn("\x1b", out)
        self.assertIn("\\u001b", out)
        self.assertIn("\\u000a", out)

    def test_non_str_tool_or_message_raises_naming_type(self):
        # Same type contract as the error reporters.
        for kwargs, name, parameter in (
            ({"tool": 42, "message": "m"}, "int", "tool"),
            ({"tool": "t", "message": b"nope"}, "bytes", "message"),
        ):
            with self.subTest(parameter=parameter, value=kwargs[parameter]):
                with self.assertRaisesRegex(
                    ValueError,
                    rf"^report_note\(\) requires str: {parameter} must be str, "
                    rf"not {name}$",
                ):
                    diagnostics.report_note(**kwargs)


class TestPlural(unittest.TestCase):
    def test_pluralizes_only_when_the_count_is_not_one(self):
        # check_references prints the bare word and check_parallel the
        # '<count> <noun>' phrase; both must agree that zero reads as more
        # than one ('0 problems', '1 module failed', '2 workers').
        for count, expected in ((0, "problems"), (1, "problem"), (2, "problems")):
            with self.subTest(count=count):
                self.assertEqual(diagnostics.plural(count, "problem"), expected)

    def test_non_str_noun_raises_naming_type(self):
        # Same type contract as the error reporters.
        with self.assertRaisesRegex(
            ValueError,
            r"^plural\(\) requires str: singular must be str, not int$",
        ):
            diagnostics.plural(2, 7)


if __name__ == "__main__":
    unittest.main()

"""Tests for the KWin session command and the dialog client argv recipes.

The session-command and dialog argv checks moved out of
``tests/test_render_surface_units.py``. They check the KWin session command
``tools/render_session.py`` builds and the argv each dialog client builder in
``tools/render_clients.py`` hands that command.
"""

from __future__ import annotations

import contextlib
import shlex
import unittest

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools import render_session, render_window_rules  # noqa: E402
from tools.render_clients import (  # noqa: E402
    calendar_dialog_client,
    checkbox_dialog_client,
    color_dialog_client,
    combobox_dialog_client,
    file_dialog_client,
    gtk_dialog_client,
    icon_dialog_client,
    inactive_dialog_client,
    lineedit_dialog_client,
    menu_dialog_client,
    progressbar_dialog_client,
    radio_dialog_client,
    slider_dialog_client,
    textbox_dialog_client,
)


class TestSessionCommand(unittest.TestCase):
    @contextlib.contextmanager
    def _dialog_command(self, client_builder):
        """Yield ``(session, command)`` for one dialog client's render command.

        The three dialog clients share the render's dialog geometry, settle
        and supervision timeout, and each puts the ``kdialog`` word into the
        in-session script, so one context manager drives the three wording
        tests: each passes its client builder and asserts the words specific
        to that dialog. The shared surface geometry and time values are the
        dialog render's, so this helper must not serve the non-dialog case
        with its own window size.
        """
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session,
                list(client_builder(session)),
                2.5,
                480,
                360,
                9.5,
            )
            self.assertIn("kdialog", command.argv[-1])
            yield session, command

    def test_carries_the_geometry_the_script_and_the_surface_path(self):
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, ["plasmawindowed", "a b"], 2.5, 64, 48, 9.5,
                readiness_script="/scratch/readiness.js",
            )
            self.assertEqual(session.render_log, command.log)
            self.assertEqual(9.5, command.timeout)
            self.assertEqual(
                [
                    "dbus-run-session",
                    "--",
                    "kwin_wayland",
                    "--virtual",
                    "--no-lockscreen",
                    "--width",
                    "64",
                    "--height",
                    "48",
                    "--socket",
                    render_session.SOCKET,
                    "--exit-with-session",
                ],
                command.argv[:-1],
            )
            self.assertIn(str(session.surface), command.argv[-1])
            self.assertIn("readiness.js", command.argv[-1])
            # The client words are positional parameters of the in-session
            # `sh -c`, so their space cannot become shell syntax.
            self.assertIn("'a b'", command.argv[-1])
            # After `sh -c <script> sh`, the positional parameters carry the
            # settle seconds first, the capture path second and the client
            # words from the third on: the script reads `settle="$1"` and
            # `capture="$2"`, so a dropped or swapped value here would sleep
            # on the surface path or put the client where the capture goes.
            self.assertEqual(
                [
                    "2.5",
                    str(session.surface),
                    "plasmawindowed",
                    "a b",
                ],
                shlex.split(command.argv[-1])[4:],
            )

    def test_client_words_with_shell_syntax_and_empty_words_stay_positional(self):
        client = ["client", "two words", "quote'and $HOME; $(false)", ""]
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, client, 1, 64, 48, 9.5
            )

            self.assertEqual(
                ["1", str(session.surface), *client],
                shlex.split(command.argv[-1])[4:],
            )

    def test_embeds_the_focus_script_path_without_reaching_the_client(self):
        # The two-window mode hands its scratch settle script to the
        # session: the in-session script must load exactly that file, and
        # the client positionals must stay free of it -- a path leaked into
        # the client argv would become a kdialog argument, not a script.
        with render_session.Session.create() as session:
            command = render_session.session_command(
                session, ["kdialog", "--msgbox"], 2.5, 480, 360, 9.5,
                "/scratch focus/inactive-dialog-focus-settle.js",
            )
        script = command.argv[-1]
        self.assertIn("org.kde.kwin.Scripting.loadScript", script)
        self.assertIn(
            shlex.quote("/scratch focus/inactive-dialog-focus-settle.js"), script
        )
        self.assertEqual(
            ["2.5", str(session.surface), "kdialog", "--msgbox"],
            shlex.split(script)[4:],
        )

    def test_carries_the_inactive_dialog_wrapper_words(self):
        # The two-window client is one sh -c wrapper the session script
        # backgrounds as a single client PID: it opens the to-be-inactive
        # kdialog first and the focused one last, so KWin's newest-window
        # activation lands on the second, then waits so the wrapper stays
        # the PID the script liveness-checks and reaps. The wrapper's kdialog
        # titles are the exact matches the forced-geometry kwinrulesrc pins.
        with self._dialog_command(inactive_dialog_client) as (_, command):
            script = command.argv[-1]
            self.assertIn("sh -c", script)
            # The titles travel inside double quotes in the wrapper, which
            # the outer session script shlex-quotes as one word: single
            # quotes inside the wrapper would be escaped out of recognition
            # there.
            self.assertIn(
                f'kdialog --title "{render_window_rules.INACTIVE_TITLE}"', script
            )
            self.assertIn(
                f'kdialog --title "{render_window_rules.FOCUSED_TITLE}"', script
            )
            self.assertIn("--msgbox", script)
            self.assertIn("wait", script)
            self.assertLess(
                script.index(render_window_rules.INACTIVE_TITLE),
                script.index(render_window_rules.FOCUSED_TITLE),
                "the to-be-inactive window must spawn first so KWin "
                "activates the focused one",
            )

    def test_carries_the_checkbox_dialog_client_words(self):
        with self._dialog_command(checkbox_dialog_client) as (session, command):
            # The dontagain config file lands in the scratch config home, so
            # the client never writes the caller's configuration. Recovering
            # the shell words also pins the warning, prompt and flag order.
            self.assertEqual(
                (
                    "kdialog",
                    "--title",
                    "Test",
                    "--warningyesno",
                    "Delete?",
                    "--dontagain",
                    f"{session.config / 'kde-dontagain'}:widgets",
                ),
                tuple(shlex.split(command.argv[-1])[-7:]),
            )

    def test_carries_the_combobox_dialog_client_words(self):
        with self._dialog_command(combobox_dialog_client) as (_, command):
            # The chooser's items travel as separate positional words of the
            # in-session script, so a space inside one cannot become shell
            # syntax.
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--combobox",
                    "Choose a disk:",
                    "Macintosh HD",
                    "Zip Disk",
                ],
                list(combobox_dialog_client(None)),
            )
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(combobox_dialog_client(None)),
                words[-len(combobox_dialog_client(None)) :],
            )

    def test_carries_the_lineedit_dialog_client_words(self):
        with self._dialog_command(lineedit_dialog_client) as (session, command):
            # The input box's prompt travels as one quoted word despite its
            # space, and no initial value follows it: the empty field keeps
            # the caret at the field's left padding, which the gate's crop
            # stays clear of.
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--inputbox",
                    "Choose a name:",
                ],
                list(lineedit_dialog_client(session)),
            )
            self.assertIn("'Choose a name:'", command.argv[-1])
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(lineedit_dialog_client(session)),
                words[len(words) - len(lineedit_dialog_client(session)) :],
            )

    def test_carries_the_file_dialog_client_words(self):
        with self._dialog_command(file_dialog_client) as (session, command):
            # The factory seeds the scratch home's Documents directory with
            # exactly the three fixed empty files the capture lists, so the
            # chooser opens on a deterministic listing: no caller disk, no
            # clock and no seventh file can enter a capture.
            documents = session.home / "Documents"
            self.assertEqual(
                ["alpha.txt", "bravo.txt", "delta.rtf"],
                sorted(path.name for path in documents.iterdir()),
            )
            for path in documents.iterdir():
                self.assertTrue(path.is_file())
                self.assertEqual(0, path.stat().st_size)
            self.assertEqual(
                (
                    "kdialog",
                    "--title",
                    "Test",
                    "--getopenfilename",
                    str(documents),
                ),
                tuple(file_dialog_client(session)),
            )
            words = shlex.split(command.argv[-1])
            self.assertEqual(
                list(file_dialog_client(session)),
                words[len(words) - len(file_dialog_client(session)) :],
            )

    def test_pins_the_seeded_file_dialog_files_mtime(self):
        with self._dialog_command(file_dialog_client) as (session, _):
            # KIO sizes the details view's Date column from the rendered
            # mtime text, and a live-clock touch would let that column's
            # width -- and the header band's divider, caption, sort-arrow
            # and size-text x-positions beside it -- move with the time of
            # day, so the seeding pins both timestamps to one constant the
            # gate's existing pins can re-derive against.
            documents = session.home / "Documents"
            for name in ("alpha.txt", "bravo.txt", "delta.rtf"):
                # 1104537600 = the seed epoch tools/render_clients.py pins
                # (2005-01-01 00:00:00 UTC), spelled as a literal so the
                # expectation here is independent of the code under test.
                self.assertEqual(1104537600, (documents / name).stat().st_mtime)

    def test_carries_the_icon_dialog_client_words(self):
        with self._dialog_command(icon_dialog_client) as (_, command):
            # The icon chooser's category default travels as its own quoted
            # word: the empty string keeps the chooser on the application
            # group's default listing, so no chooser-state pin can enter a
            # capture. shlex quotes nothing, so the words stay script text.
            client = list(icon_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--geticon",
                    "application",
                    "",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `$@` hands kdialog -- recovers exactly that argv, so
            # the empty category word is still its own word.
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_gtk_dialog_client_opens_a_zenity_text_entry(self):
        self.assertEqual(
            ("zenity", "--title", "Test", "--entry", "--text", "Choose a name:"),
            gtk_dialog_client(None),
        )

    def test_carries_the_slider_dialog_client_words(self):
        with self._dialog_command(slider_dialog_client) as (_, command):
            # The slider's prompt, minimum, maximum and step travel as
            # separate quoted words of the in-session script, so a space in
            # the prompt cannot become shell syntax. Value zero rests the
            # thumb at the trough's left end in its resting state.
            client = list(slider_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--slider",
                    "Brightness:",
                    "0",
                    "100",
                    "10",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv, so
            # each number is still its own word (the prompt carries no space,
            # so shlex quotes nothing).
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_progressbar_dialog_client_words(self):
        with self._dialog_command(progressbar_dialog_client) as (_, command):
            # The helper daemon's prompt travels as its own word, and the
            # meter never moves: no D-Bus call follows the printed
            # reference, so no striped progress-pattern tile or busy
            # animation enters any capture. shlex.join never quotes a
            # colon, so the Working: prompt stays unquoted script text.
            client = list(progressbar_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog_progress_helper",
                    "--title",
                    "Test",
                    "--progressbar",
                    "Working:",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands the helper -- recovers exactly that
            # argv, so the colon-tailed prompt is still its own word.
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_calendar_dialog_client_words(self):
        with self._dialog_command(calendar_dialog_client) as (_, command):
            # The calendar's prompt, pinned default date and date format
            # travel as separate quoted words of the in-session script. The
            # pinned date is load-bearing: without --dateformat kdialog
            # ignores --default and opens today's month, with it the view
            # never contains today's date and the gate's bands stay
            # clock-independent.
            client = list(calendar_dialog_client(None))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--calendar",
                    "Calendar:",
                    "--default",
                    "1970-01-07",
                    "--dateformat",
                    "yyyy-MM-dd",
                ],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_color_dialog_client_words(self):
        with self._dialog_command(color_dialog_client) as (session, command):
            # The prompt name travels as its own quoted word of the in-session
            # script. The dialog shows no clock-dependent content -- no date
            # and no clock-driven selection can enter any capture -- so the
            # client carries no default pin.
            client = list(color_dialog_client(session))
            self.assertEqual(
                ["kdialog", "--title", "Test", "--getcolor"],
                client,
            )
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])

    def test_carries_the_menu_dialog_client_words(self):
        with self._dialog_command(menu_dialog_client) as (session, command):
            # The whole client suffix serializes exactly as built, with the
            # prompt kept as one quoted word despite its space.
            client = list(menu_dialog_client(session))
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertIn("'Pick an item:'", command.argv[-1])
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv, so
            # each menu item and its tag is still a separate word.
            words = shlex.split(command.argv[-1])
            self.assertEqual(client, words[len(words) - len(client) :])

    def test_carries_the_radiolist_dialog_client_words(self):
        with self._dialog_command(radio_dialog_client) as (session, command):
            # The whole client suffix serializes exactly as built, with the
            # prompt kept as one quoted word despite its space. The ``on``
            # status pins the checked item as a fixed default, so the
            # selection never depends on clock, network or input.
            client = list(radio_dialog_client(session))
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertIn("'Pick an item:'", command.argv[-1])
            # And shell word-splitting of the script's arguments -- what the
            # script's `"$@"` hands kdialog -- recovers exactly that argv,
            # so each radio item's tag, label and status is still a separate
            # word.
            words = shlex.split(command.argv[-1])
            self.assertEqual(client, words[len(words) - len(client) :])

    def test_carries_the_textbox_dialog_client_words(self):
        with self._dialog_command(textbox_dialog_client) as (session, command):
            # The scratch text file's path travels as its own word under the
            # session root the render's context manager removes, and the
            # file exists by the time the client argv is built (the text
            # view's scrollbar geometry depends on its 40 lines).
            client = list(textbox_dialog_client(session))
            self.assertEqual(
                [
                    "kdialog",
                    "--title",
                    "Test",
                    "--textbox",
                    str(session.root / "textbox.txt"),
                ],
                client,
            )
            self.assertTrue((session.root / "textbox.txt").is_file())
            self.assertTrue(command.argv[-1].endswith(shlex.join(client)))
            self.assertEqual(client, shlex.split(command.argv[-1])[-len(client) :])


if __name__ == "__main__":
    unittest.main()

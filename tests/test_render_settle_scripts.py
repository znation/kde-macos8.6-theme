"""Tests for the render session's KWin settle scripts.

``tools/render/settle_scripts.py`` writes the two KWin scripts the
session loads through KWin's scripting D-Bus: the readiness script that
reports the session's mapped windows over the scratch D-Bus (a
single-window report, or the pair report for the two-window
inactive-dialog render), and the focus-settle script that re-activates
the focused-title window whenever KWin does not already treat it as
active. The capture-time window-report script the session runs once
after the settle is pinned here too. All are pinned byte for byte here;
the window rules the pair matches on are pinned in
``tests/test_render_window_rules.py``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from support import repo_root  # noqa: F401  (puts the repository root on sys.path)
from tools.render.window_rules import FOCUSED_TITLE, INACTIVE_TITLE
from tools.render.settle_scripts import (
    FOCUS_SETTLE_SCRIPT,
    READINESS_INTERFACE,
    READINESS_SERVICE,
    READINESS_SETTLE_SCRIPT,
    READINESS_MEMBER,
    WINDOW_REPORT_SCRIPT,
    focus_settle_text,
    pair_readiness_text,
    readiness_settle_text,
    window_report_text,
    write_focus_settle_script,
    write_readiness_settle_script,
    write_window_report_script,
)


class _FakeSession:
    """The attributes the writers read: the config and scratch homes."""

    def __init__(self, config: Path, root: Path | None = None):
        self.config = config
        self.root = root if root is not None else config


def _assert_writes_script_bytes(
    test: unittest.TestCase,
    writer,
    script_name: str,
    text: str,
    **kwargs,
) -> None:
    """Pin one settle-script writer in a scratch root.

    The writer must return the scratch-root path under ``script_name``
    and put exactly the pinned ``text`` bytes there. Covers the four
    writer pins in this suite; it has no other call sites.
    """
    with tempfile.TemporaryDirectory() as root:
        session = _FakeSession(Path(root) / "cfg", Path(root))
        path = writer(session, **kwargs)
        test.assertEqual(Path(root) / script_name, path)
        test.assertEqual(text.encode("utf-8"), path.read_bytes())


class TestSettleScripts(unittest.TestCase):
    def test_readiness_script_reports_existing_and_new_render_windows(self):
        script = readiness_settle_text()
        self.assertIn("workspace.windowList()", script)
        self.assertIn("workspace.windowAdded.connect(report)", script)
        self.assertIn(READINESS_INTERFACE, script)
        self.assertIn(READINESS_MEMBER, script)
        for kind in ("normalWindow", "dialog", "splash", "desktopWindow"):
            self.assertIn(f"window.{kind}", script)

    def test_the_readiness_script_reports_eligible_window_additions_over_dbus(self):
        script = readiness_settle_text()
        self.assertIn("workspace.windowAdded.connect(report)", script)
        self.assertIn("workspace.windowList()", script)
        self.assertIn("window.normalWindow || window.dialog || window.splash || window.desktopWindow", script)
        self.assertIn(
            f'callDBus("{READINESS_SERVICE}", "/", "{READINESS_INTERFACE}", "ClientReady")',
            script,
        )

    def test_write_readiness_settle_script_writes_the_script_into_the_scratch_root(self):
        _assert_writes_script_bytes(
            self, write_readiness_settle_script, READINESS_SETTLE_SCRIPT,
            readiness_settle_text(),
        )

    def test_the_pair_readiness_script_names_both_titles_and_their_focus_states(self):
        # The pair is settled only when the inactive-titled window is not
        # active and the focused-titled window is. A swapped focus state, or
        # a missing "not active" test, would report a pair that the gate's
        # pins still read as active on the wrong window.
        script = pair_readiness_text()
        self.assertIn(f'window.caption === "{INACTIVE_TITLE}" && !window.active', script)
        self.assertIn(f'window.caption === "{FOCUSED_TITLE}" && window.active)', script)
        self.assertNotIn(f'window.caption === "{FOCUSED_TITLE}" && !window.active', script)
        self.assertNotIn(f'window.caption === "{INACTIVE_TITLE}" && window.active', script)

    def test_the_pair_readiness_script_reports_at_most_once(self):
        script = pair_readiness_text()
        self.assertIn("let reported = false;", script)
        self.assertIn("if (reported) {", script)
        self.assertIn("reported = true;", script)

    def test_the_pair_readiness_script_connects_added_activated_and_caption_signals(self):
        script = pair_readiness_text()
        self.assertIn("workspace.windowList()", script)
        self.assertIn("workspace.windowAdded.connect(function (window) {", script)
        self.assertIn("workspace.windowActivated.connect(check)", script)
        self.assertIn("window.captionChanged.connect(check)", script)
        self.assertIn("watch(window);", script)

    def test_the_pair_readiness_script_calls_the_readiness_service(self):
        script = pair_readiness_text()
        self.assertIn(
            f'callDBus("{READINESS_SERVICE}", "/", "{READINESS_INTERFACE}", "ClientReady")',
            script,
        )

    def test_the_pair_readiness_script_has_no_any_window_eligibility_test(self):
        # The single-window script reports any normal, dialog, splash or
        # desktop window. The pair must not, or the first mapped window would
        # end the settle before the second window exists.
        script = pair_readiness_text()
        self.assertNotIn("window.normalWindow", script)
        self.assertNotIn("window.dialog ||", script)
        self.assertNotIn("window.splash", script)

    def test_write_readiness_settle_script_pair_writes_the_pair_text(self):
        _assert_writes_script_bytes(
            self, write_readiness_settle_script, READINESS_SETTLE_SCRIPT,
            pair_readiness_text(), pair=True,
        )
        self.assertNotEqual(readiness_settle_text(), pair_readiness_text())

    def test_the_focus_settle_script_activates_the_focused_window_only(self):
        # Byte-for-byte: the one-shot script the session re-runs must
        # activate exactly the focused title and only when KWin does not
        # already treat it as active -- a script that touched the inactive
        # window's state, matched a prefix instead of the exact title or
        # logged on every no-op run would either flip the gate's own
        # subject or spam the render log. workspace.activeWindow and
        # window.active were probed on the installed KWin 6.3.6
        # (2026-11-13, a throwaway --virtual session): the probe read
        # focusedActive=false and active=Other window, assigned the
        # focused window and then read after=Focused window, so the
        # assignment is what settles the pair's focus state.
        self.assertEqual(
            "for (const window of workspace.windowList()) {\n"
            f'    if (window.caption === "{FOCUSED_TITLE}" && !window.active) {{\n'
            "        workspace.activeWindow = window;\n"
            '        print("render-session: settled the focused window\'s '
            'activation");\n'
            "    }\n"
            "}\n",
            focus_settle_text(),
        )

    def test_the_focus_settle_script_never_names_the_inactive_title(self):
        # The settle must not touch the inactive window: activating it
        # would draw the gate's own subject in the active decoration and
        # fail every left-window pin.
        self.assertNotIn(INACTIVE_TITLE, focus_settle_text())

    def test_write_focus_settle_script_writes_the_script_into_the_scratch_root(
        self,
    ):
        # The session script loads the file by its scratch path, so the
        # writer must put exactly the probed script bytes there.
        _assert_writes_script_bytes(
            self, write_focus_settle_script, FOCUS_SETTLE_SCRIPT,
            focus_settle_text(),
        )

    def test_the_window_report_script_names_each_window_caption_active_state_and_kind(
        self,
    ):
        # Byte-for-byte: the one-shot report must print one capture-time
        # line per listed window carrying its caption, active state and the
        # kind tag the readiness scripts filter on -- a report that dropped
        # the caption or a kind would leave a recurrence's mapping state
        # unreadable, the exact evidence the parked pixel-flake entries ask
        # for.
        self.assertEqual(
            "for (const window of workspace.windowList()) {\n"
            '    let kind = "other";\n'
            "    if (window.normalWindow) {\n"
            '        kind = "normalWindow";\n'
            "    } else if (window.dialog) {\n"
            '        kind = "dialog";\n'
            "    } else if (window.splash) {\n"
            '        kind = "splash";\n'
            "    } else if (window.desktopWindow) {\n"
            '        kind = "desktopWindow";\n'
            "    }\n"
            '    print("render-session: window at capture: caption=" + window.caption '
            '+ " active=" + window.active + " kind=" + kind);\n'
            "}\n",
            window_report_text(),
        )

    def test_the_window_report_script_is_one_shot(self):
        # The report runs once at capture time: no signal handler may fire
        # it again and no callDBus may replace the print, or the capture-
        # time snapshot would become a second settle participant.
        script = window_report_text()
        self.assertNotIn("callDBus", script)
        self.assertNotIn(".connect(", script)

    def test_write_window_report_script_writes_the_script_into_the_scratch_root(
        self,
    ):
        # The session script loads the file by its scratch path, so the
        # writer must put exactly the pinned script bytes there, under the
        # name the mode pins carry.
        _assert_writes_script_bytes(
            self, write_window_report_script, WINDOW_REPORT_SCRIPT,
            window_report_text(),
        )


if __name__ == "__main__":
    unittest.main()

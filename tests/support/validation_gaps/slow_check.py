"""The ``slow-check`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The four ``slow-check`` records the archive held when the newest entry
# joined, plus the quarantined inactive-dialog title-ink pin fixed 2026-11-24,
# whose flake only ever surfaced under the full parallel check's render load;
# the pair readiness script that removed it is pinned offline by the test
# naming both titles and their focus states. Each failure was only
# confirmable under render or wall-clock-shaped load; its reproduction now
# pins the shipped paint budget offline -- a shipped flag list, or a
# stubbed save whose diagnosis runs without the wall clock.
# A new record must name such a test instead of raising this.
SLOW_CHECK_BASELINE = 5

SLOW_CHECK_REPRODUCTIONS = (
    Reproduction(
        "loaded-host-gtk-dialog-gate",
        ("Under a loaded host the live GTK dialog gate flakes",),
        "tests/test_render_surface.py"
        "::TestRenderBudgets"
        "::test_gtk_dialog_gets_a_longer_settle_budget",
    ),
    Reproduction(
        "applet-gate-default-settle",
        ("The render gate captures an unpainted frame on a loaded host",),
        "tests/test_render_surface.py"
        "::TestRenderBudgets"
        "::test_the_applet_gate_renders_at_the_documented_default_settle",
    ),
    Reproduction(
        "crashed-applet-setup-wait",
        ("setup wait expires before its crashed applet starts",),
        "tests/test_render_live_capture.py"
        "::TestLiveCapture"
        "::test_an_expired_setup_wait_is_reported_by_name_not_as_a_status_mismatch",
    ),
    Reproduction(
        "inactive-dialog-title-ink-quarantine",
        (
            "test_render_dialog_gates.TestInactiveDialogRender."
            "test_title_ink_is_the_inactive_text_colour",
        ),
        "tests/test_render_settle_scripts.py::TestSettleScripts"
        "::test_the_pair_readiness_script_names_both_titles_and_their_focus_states",
    ),
    Reproduction(
        "inactive-dialog-focus-settle",
        (
            "The inactive-dialog render gate's pixel pins can fail under a "
            "full parallel `make check`",
        ),
        "tests/test_render_session_focus_settle.py"
        "::TestSessionFocusSettle"
        "::test_runs_the_focus_settle_loop_until_the_capture_has_returned",
    ),
)

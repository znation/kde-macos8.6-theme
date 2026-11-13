"""The ``slow-check`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The three ``slow-check`` records the archive held when the ledger was added.
# Each failure was only confirmable under render or wall-clock-shaped load;
# its reproduction now pins the shipped paint budget offline -- a shipped
# flag list, or a stubbed save whose diagnosis runs without the wall clock.
# A new record must name such a test instead of raising this.
SLOW_CHECK_BASELINE = 3

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
        "tests/test_render_failure_paths.py"
        "::TestFailurePaths"
        "::test_an_expired_setup_wait_is_reported_by_name_not_as_a_status_mismatch",
    ),
)

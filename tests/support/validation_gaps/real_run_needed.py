"""The ``real-run-needed`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The five ``real-run-needed`` records the archive held when the ledger was added,
# plus the check-box indicator resample fixed 2026-10-30, whose confirmation
# drew the indicator through a real ``kwin_wayland`` ``kdialog`` render; that
# render's size bound is pinned offline by the new test. Plus the Aurorae
# title-edge band fixed 2026-10-30, whose band and one-row gap were only
# visible in a real ``kwin_wayland`` render; the gap the rc's
# ``TitleEdgeBottom`` must leave is pinned offline by the rc metrics test.
# Plus the Aurorae-only live render gate fixed 2026-10-30: confirming the
# widget pixels the engine drew needed a real ``kwin_wayland`` ``kdialog``
# render, and the dialog render that suite now runs in ``make check`` pins
# the rendered checkbox cell against the shipped art. Plus the combo arrow
# resample fixed 2026-10-30: the squashed observation came from a pass session
# that the theme-selection plumbing predates, so only a fresh real
# ``kwin_wayland`` render could say what the engine now draws, and the dialog
# render that suite now runs in ``make check`` pins the rendered combo arrow
# cell against the shipped art. Plus the Aurorae hover/press button erasure
# fixed 2026-11-04: showing the erasure needed a live KWin hover on an
# unfocused window, diagnosed against the installed AuroraeButton.qml state
# logic; the nothing-shipped ``inactive-center`` slices the fix ships are
# pinned offline by the button fixture's test. Plus the render-session capture-buffer denial fixed 2026-11-09
# (originally tagged the bespoke ``runner-side``; re-tagged in the same
# change that pinned the archive's tag vocabulary): the workflow's
# forced-llvmpipe env was never observed on the hosted runner, and its
# bound is pinned offline by the test that refuses driver-name overrides
# in the workflow env. Plus the nested-session portal crash loop fixed
# 2026-11-10: the window between the private bus opening and the nested KWin
# socket serving could only be observed in a real render against the host's
# coredump journal, and the bound (the activated portal must never try to
# open the nested Wayland socket) is pinned offline by the session-
# environment test that pins the bus subtree to a display-free Qt platform.
# Plus the splash black-capture report fixed 2026-11-12 (two BUGS.md records,
# the original and its duplicate, sharing one subject): the intermittency
# could only be confirmed against a real splash capture under the gate's
# concurrent-render load, and the repair's bound — the splash client is
# frozen with SIGSTOP between the settle's liveness check and the capture and
# resumed with SIGCONT before the termination — is pinned offline by the
# session-script hold test. A new record must name an
# offline test instead of raising this.

REAL_RUN_NEEDED_REPRODUCTIONS = (
    Reproduction(
        "firefox-profile-discovery-ini-cap",
        ("Firefox profile-discovery INI",),
        "tests/test_firefox_profile.py::TestProfileResolution"
        "::test_an_oversize_ini_file_is_refused_by_name",
    ),
    Reproduction(
        "gtk-config-cap",
        ("An oversize GTK settings or user-CSS file",),
        "tests/test_apply_gtk_errors.py::TestUnreadableConfig"
        "::test_apply_refuses_an_oversize_settings_file_before_writing_anything",
    ),
    Reproduction(
        "firefox-profile-file-cap",
        ("An oversize Firefox profile file",),
        "tests/test_install_firefox.py::TestInstall"
        "::test_an_oversize_user_chrome_is_refused_by_name",
    ),
    Reproduction(
        "colorscheme-uninstall-still-selected",
        ("Uninstalling the scheme while it is selected",),
        "tests/test_colorscheme_install.py::TestInstall"
        "::test_make_uninstall_warns_when_the_removed_scheme_is_still_selected",
    ),
    Reproduction(
        "colorscheme-restart-id",
        ("`plasma-apply-colorscheme` writes a scheme ID",),
        "tests/test_colorscheme_install.py::TestInstall"
        "::test_make_install_names_the_scheme_after_its_source_basename",
    ),
    Reproduction(
        "check-box-indicator-resample",
        ("check box indicator is a resampled",),
        "tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference"
        "::test_config_draws_the_indicator_at_the_canvas_size",
    ),
    Reproduction(
        "aurorae-title-edge-bottom-band",
        ("band of the decoration's centre tile",),
        "tests/test_aurorae_rc.py::TestRc"
        "::test_layout_metrics_match_reference",
    ),
    Reproduction(
        "live-render-gate-aurorae-only",
        ("live render gate byte-compares only Aurorae window chrome",),
        "tests/test_render_surface.py::TestCheckboxDialogRender"
        "::test_draws_the_check_box_cell_1_to_1",
    ),
    Reproduction(
        "combo-arrow-indicator-resample",
        ("combo box indicator is a squashed",),
        "tests/test_render_surface.py::TestComboboxDialogRender"
        "::test_draws_the_combo_arrow_cell_1_to_1",
    ),
    Reproduction(
        "render-session-capture-buffer-denial",
        ("KWin session cannot allocate its capture buffers",),
        "tests/test_ci_workflow.py::TestCiWorkflow"
        "::test_workflow_runs_the_suite_on_the_headless_qt_platform",
    ),
    Reproduction(
        "aurorae-hover-press-erasure",
        ("Hovering or pressing an unfocused window",),
        "tests/test_aurorae_buttons.py::TestButtons"
        "::test_inactive_center_ships_nothing",
    ),
    Reproduction(
        "aurorae-inactive-button-art-bounds",
        ("Clicking where an unfocused window",),
        "tests/test_aurorae_ui_qml.py::TestHitSurfaces"
        "::test_aurorae_button_gates_the_subclass_item",
    ),
    Reproduction(
        "nested-session-portal-crash-loop",
        ("crash-loop xdg-desktop-portal-kde with SIGABRT",),
        "tests/test_render_surface.py::TestFailurePaths"
        "::test_session_pins_the_nested_bus_to_a_display_free_qt_platform",
    ),
    Reproduction(
        "hosted-ci-imagemagick-convert",
        ("The hosted CI image lacks ImageMagick",),
        "tests/test_ci_workflow.py::TestCiWorkflow"
        "::test_workflow_provisions_and_verifies_imagemagick_convert",
    ),
    Reproduction(
        "splash-capture-client-hold",
        (
            "The splash render intermittently captures a black frame at the 8-second settle",
        ),
        "tests/test_render_surface_units.py::TestSessionScript"
        "::test_holds_the_client_across_the_capture_and_resumes_it_before_the_termination",
    ),
)

# coverage. A new record must name its offline test, and raise this by one in
# the same change instead of landing uncovered.
REAL_RUN_NEEDED_BASELINE = 16

"""The ``no-repro`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The five ``no-repro`` records the archive held when the newest entry joined.
# Each failure was not deterministic when filed; its test now reproduces it every
# run. A new record must name such a test instead of raising this.
NO_REPRO_BASELINE = 5

NO_REPRO_REPRODUCTIONS = (
    Reproduction(
        "cursor-write-helper-patch",
        ("The cursor generator test patches a removed `_write_atomic` symbol",),
        "tests/test_make_cursors.py::TestMainErrors"
        "::test_reports_a_failed_write_and_stops_at_that_cursor",
    ),
    Reproduction(
        "check-pattern-whitespace",
        ("`CHECK_PATTERN` guard accepts a pattern with surrounding whitespace",),
        "tests/test_make_check.py::TestCheckPattern"
        "::test_surrounding_whitespace_pattern_is_stripped",
    ),
    Reproduction(
        "home-make-function-injection",
        (
            "An environment-supplied HOME value executes GNU make functions "
            "during Makefile parsing",
        ),
        "tests/test_make_refusals.py::TestShellUnsafeInstallPaths"
        "::test_make_function_text_in_HOME_is_refused_without_evaluation",
    ),
    Reproduction(
        "client-exit-stub-pidfile-race",
        (
            "The client-exit stub regression is load-sensitive and can turn a "
            "parallel `make check` red",
        ),
        "tests/test_render_failure_paths.py::TestFailurePaths"
        "::test_a_client_that_exits_during_the_capture_is_not_blamed_on_the_paint_budget",
    ),
    Reproduction(
        "desktoptheme-session-theme",
        ("fails when `XDG_CONFIG_DIRS` already names a session theme",),
        "tests/test_desktoptheme.py::TestApplyDesktopTheme"
        "::test_apply_ignores_a_session_theme_in_the_config_search_path",
    ),
)

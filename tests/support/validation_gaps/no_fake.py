"""The ``no-fake`` validation-gap ledger's reproduction entries and baseline.

Each entry names the archived record's markers and the offline test that
reproduces its failure. The suite caps the tag's record count at the
baseline, so a new archived record must name its reproduction entry here
(and raise the baseline by one in the same change) instead of growing the
gap untested.
"""

from __future__ import annotations

from .records import Reproduction

# The number of ``no-fake`` records the archive holds with ledger coverage. A
# new record must name its fixture and reproducing test, and raise this by one
# in the same change instead of merging uncovered.
NO_FAKE_BASELINE = 36

NO_FAKE_REPRODUCTIONS = (
    Reproduction(
        "apply-kvantum-note-theme-already-at-default-home",
        (
            "off-default data-home note fires when the theme already exists at the default data home",
        ),
        "tests/test_apply_theme.py::TestKvantumDataHomeNote"
        "::test_a_theme_already_at_the_default_data_home_stays_silent",
    ),
    Reproduction(
        "check-parallel-forged-empty-summary",
        ("accepts a forged empty-run summary from a started test",),
        "tests/test_check_parallel.py::TestCoordinator"
        "::test_a_forged_no_tests_ran_summary_fails_the_run",
    ),
    Reproduction(
        "check-parallel-stray-file-discovery",
        ("a stray file matching a broad pattern",),
        "tests/test_check_parallel_discovery.py::TestDiscovery"
        "::test_files_unittest_cannot_load_are_skipped",
    ),
    Reproduction(
        "check-parallel-package-init-tests",
        ("tests defined in the package's __init__.py",),
        "tests/test_suite_discovery.py::TestSuiteDiscovery"
        "::test_no_package_init_collects_tests_or_load_tests",
    ),
    Reproduction(
        "check-parallel-log-stem-collision",
        ("two modules sharing one _-joined log stem",),
        "tests/test_check_parallel.py::TestCoordinator"
        "::test_modules_with_the_same_log_stem_get_distinct_logs",
    ),
    Reproduction(
        "check-parallel-testless-module",
        ("a pattern-matched module that collects no tests",),
        "tests/test_check_parallel.py::TestCoordinator"
        "::test_a_module_with_no_tests_does_not_fail_the_run",
    ),
    Reproduction(
        "check-parallel-forged-exit-5",
        ("a module that dies of its own os._exit(5) skips its tests silently",),
        "tests/test_check_parallel.py::TestCoordinator"
        "::test_an_exit_5_without_the_no_tests_ran_summary_fails_the_run",
    ),
    Reproduction(
        "check-parallel-unterminated-log",
        ("a worker log that never ends its last line",),
        "tests/test_check_parallel.py::TestCoordinator"
        "::test_an_unterminated_log_never_merges_with_the_next_section",
    ),
    Reproduction(
        "firefox-content-at-rule-escaped-quote",
        ("escaped quote in a body value",),
        "tests/test_firefox_content_theme.py::TestAtRuleBodies"
        "::test_escaped_quote_in_a_body_value_ends_at_the_at_rule_brace",
    ),
    Reproduction(
        "unused-imports-facade-reexport",
        ("only feeds a package facade's re-export",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_a_package_facade_re_export_keeps_the_submodule_import",
    ),
    Reproduction(
        "unused-imports-reassignment-as-read",
        ("counts a re-assignment of an imported name as a read",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_a_reassignment_of_the_imported_name_keeps_the_flag",
    ),
    Reproduction(
        "unused-imports-annotated-all",
        ("misses an annotated `__all__` assignment",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_an_annotated_all_entry_re_exports_the_import",
    ),
    Reproduction(
        "unused-imports-aliased-reexport",
        ("matches an aliased import by its binding name",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_an_aliased_import_from_here_keeps_the_imported_name",
    ),
    Reproduction(
        "unused-imports-all-extend-call",
        ("re-export grown by `__all__.extend`",),
        "tests/test_no_unused_imports.py::TestNoUnusedImports"
        "::test_an_all_extend_call_re_exports_the_import",
    ),
    Reproduction(
        "firefox-ini-fifo",
        ("Firefox profile-discovery INI",),
        "tests/test_firefox_profile.py::TestProfileResolution"
        "::test_a_fifo_at_either_ini_file_is_refused_without_blocking",
    ),
    Reproduction(
        "firefox-profile-file-fifo",
        ("Firefox profile file blocks the install",),
        "tests/test_install_firefox.py::TestRemove"
        "::test_a_fifo_at_either_profile_file_is_refused_without_blocking",
    ),
    Reproduction(
        "uninstall-diagnostics-fifo-swap",
        ("a FIFO between the uninstall diagnostics",),
        "tests/test_uninstall_config_read_cap.py::TestReaderFifo"
        "::test_a_fifo_swapped_in_for_a_regular_file_is_refused",
    ),
    Reproduction(
        "png-trns-before-plte",
        ("palette image with tRNS before PLTE",),
        "tests/test_png_malformed.py::TestTrnsColorTypeValidation"
        "::test_palette_trns_before_plte_is_refused",
    ),
    Reproduction(
        "placeholders-symlinked-register",
        ("reads a symlinked `PLACEHOLDERS.md` bare",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_cross_check_refuses_a_symlinked_register_that_escapes",
    ),
    Reproduction(
        "invariants-symlinked-register",
        ("reads a symlinked register bare",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_refuses_a_symlinked_register_that_escapes",
    ),
    Reproduction(
        "checker-mutations-symlinked-register",
        ("register reads follow a symlinked register outside",),
        "tests/test_checker_mutations.py::TestCheckerMutations"
        "::test_register_reads_refuse_a_symlink_escape",
    ),
    Reproduction(
        "colorscheme-provenance-symlink",
        ("color-scheme provenance test",),
        "tests/test_containment.py::TestReadText"
        "::test_rejects_a_symlink_that_escapes_the_root",
    ),
    Reproduction(
        "desktoptheme-copy-symlink",
        ("secondary SVG copy unguarded",),
        "tests/test_containment.py::TestReadBytes"
        "::test_rejects_a_symlink_that_escapes_the_root",
    ),
    Reproduction(
        "splash-symlink",
        ("follows a symlinked `Splash.qml`",),
        "tests/test_splash_qml.py::TestSplashQmlContainment"
        "::test_rejects_a_symlink_that_escapes_the_repository",
    ),
    Reproduction(
        "metadata-symlink",
        ("load_metadata` follows a symlinked `metadata.json`",),
        "tests/test_package_metadata.py::TestLoadMetadataContainment"
        "::test_rejects_a_symlink_that_escapes_the_repository",
    ),
    Reproduction(
        "invariants-unreadable-register",
        ("`tests/invariants.py`'s `cross_check` lets an unreadable register",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_rejects_an_unreadable_register",
    ),
    Reproduction(
        "metadata-unreadable",
        ("lets an unreadable `metadata.json`",),
        "tests/test_package_metadata.py::TestLoadMetadata"
        "::test_unreadable_file_names_the_path",
    ),
    Reproduction(
        "placeholders-unreadable-register",
        ("`tests/placeholders.py` lets an unreadable register",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_register_entries_rejects_an_unreadable_register",
    ),
    Reproduction(
        "placeholders-dangling-symlink",
        ("dangling symlink inside `theme/`",),
        "tests/test_placeholders.py::TestHelpers"
        "::test_markers_rejects_a_dangling_symlink_within_the_theme_root",
    ),
    Reproduction(
        "invariants-nul-row",
        ("register reference with a NUL byte",),
        "tests/test_invariants.py::TestHelpers"
        "::test_cross_check_rejects_a_reference_with_a_nul_byte",
    ),
    Reproduction(
        "invariants-unreadable-test-file",
        ("reference to an unreadable test file",),
        "tests/test_checker_mutations.py::TestCheckerMutations"
        "::test_invariants_mutations",
    ),
    Reproduction(
        "apply-cursor-unrunnable-selector",
        ("unstartable cursor selector",),
        "tests/test_apply_cursor.py::TestSelection"
        "::test_unrunnable_selector_exits_2_without_a_traceback",
    ),
    Reproduction(
        "run-logged-start-sigterm",
        ("A SIGTERM that arrives while a child starts",),
        "tests/test_process_group.py::TestRunLogged"
        "::test_a_sigterm_while_popen_returns_still_kills_the_child",
    ),
    Reproduction(
        "run-logged-start-sigint",
        ("A Ctrl-C that arrives while a child starts",),
        "tests/test_process_group.py::TestRunLogged"
        "::test_a_sigint_while_popen_returns_still_kills_the_child",
    ),
    Reproduction(
        "run-logged-custom-sigterm",
        ("post-merge review of bdcedf73",),
        "tests/test_process_group.py::TestRunLogged"
        "::test_a_custom_sigterm_handler_keeps_its_behavior_during_start",
    ),
    Reproduction(
        "required-output-log-removal-fails",
        ("stderr log cannot be removed",),
        "tests/test_required_command.py::TestRunRequiredOutput"
        "::test_a_stderr_log_that_cannot_be_removed_keeps_the_value",
    ),
)

# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Uninstall selection diagnostics: split the oversized dispatcher by config surface (planned 2026-11-09 by the organize role)

**Goal.** Reduce the 508-line `tools/uninstall_diagnostics.py` outlier and make each selection family's checks readable without changing the diagnostics, their order, or parsing. The production Python median is 136 lines; `diagnostics()` alone spans roughly lines 203–472 and owns unrelated live selections and defaults-layer selections in one dispatcher.

**Target structure and files.** Keep `tools/uninstall_diagnostics.py` as the CLI and ordered coordinator. Move the parser state and helpers (`config_home`, bounded `read_text`, `read_selected_values`, `latched_match`, `_flat_text`, and constants) into `tools/uninstall_config.py`, updating the parity corpus declaration in `tests/support/kde_ini_corpus.py` and `tests/test_kde_ini_parity.py` so the extracted scanner remains directly covered. Move live-config handlers (kdeglobals, GTK settings/CSS, Kvantum, plasmarc, kcminputrc, kwinrc) into `tools/uninstall_live_diagnostics.py`; move defaults-layer handlers (ksplashrc, package, and kdedefaults mirrors) into `tools/uninstall_defaults_diagnostics.py`. Each handler accepts the config root and the ids it needs and returns messages; the coordinator calls them in the existing recipe order and retains `_font_diagnostics` with the KDE handler. Update every import and path reference in tests and docs.

**Cost removed.** Today a single large `diagnostics()` function interleaves live settings with the defaults layer, while the same module also owns CLI parsing, bounded file reads, and INI scanning. That makes a change to one selection family require navigating a long function and obscures the boundary between active and fallback config state.

**Acceptance criteria.** Message text, message ordering, missing/unreadable-file behavior, caps, and direct-script and package CLI behavior remain unchanged. The parity test continues to exercise the moved reader and its special GTK latch behavior. Tests still cover each diagnostic; grep across source, tests, and Markdown finds no stale old module paths or moved function references. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

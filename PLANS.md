# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

**Needs review 2026-11-19 by feature: too large for one run**

**Needs review 2026-11-19 by feature: too large for one run.** Measured in this checkout: 106 flat `tools/*.py` modules (the entry says 107), 199 Python files that import a prefixed flat module (the entry says 97), 172 test files that call `mock.patch`, and 11 markdown/Makefile files naming flat modules. One change touching all of these, with per-module patch-target ownership decisions and the `tools/render_workflow.py` anchor (absent; its successor is not found by `git log --follow`), exceeds one run's budget. Suggest the plan role split it into one subsystem family per entry (e.g. `render_` first), each landing its own package and its importers together.

**Goal.** `tools/` holds 106 flat modules with no grouping beyond their name
prefixes: `render_` (12), `fidelity_` (12), `sample_` (11), `cursor_` (10),
`check_` (7), `firefox_` (5), `apply_` (5), `uninstall_` (4), `gtk_` (4), plus
single files for other subsystems. A reader cannot see subsystem boundaries from
the directory listing, and 97 files import these modules by their flat names.
Regroup them into subpackages, following the existing `tools/png/` package.

**Cost today.** Evidence: `ls tools/*.py | wc -l` gives 106 modules; `rg -l` finds 97
files that import a prefixed flat module; `render_` names appear in 123 files
(code, tests and docs). Nothing marks which `render_*` modules form the render
subsystem, so a change to one family is found by grepping names, not by path.

**Target structure.** One subpackage per subsystem, each with `__init__.py`:
`tools/render/`, `tools/fidelity/`, `tools/sample/`, `tools/cursor/`,
`tools/firefox/`, `tools/uninstall/`, `tools/gtk/`, `tools/check/`. The module
names lose their prefix inside the package (`tools/render_workflow.py` becomes
`tools/render/workflow.py`). The CLI entry points stay in `tools/` and keep their
paths, because the Makefile, `docs/*.md` and the help text run
`python3 tools/sample.py`, `tools/fidelity.py` and similar commands. Shared
modules (`atomic_write`, `text_lines`, `process_group`, `repo_root`, ...) stay at
the top of `tools/`. Modules that serve two families are assigned to one owner,
and the other family imports it.

**Files touched.** Every moved module; every importer in `tools/` and `tests/`
(about 97 files); every `mock.patch` target string (retarget each moved name to
the module whose global the caller resolves, per the L4 lesson); the Makefile;
`docs/*.md`, README, `docs/invariants.md`, and the rendered help text.

**Approach.** Land the whole move in one change so the tree never sits between
two layouts. Order: create the packages, move modules with `git mv`, rewrite
imports, retarget `mock.patch` strings, then grep every old flat name across
source, tests and markdown before running `make check`.

**Acceptance criteria.**

- `ls tools/*.py` lists only the CLI entry points and shared top-level modules;
  each subsystem family lives in its own package directory.
- A grep for every old flat name (`render_workflow`, `fidelity_metrics`, ...) over
  `*.py`, `*.md` and `Makefile` finds no stale reference.
- Every `mock.patch` string that names a moved module resolves; the tests that patch
  them still pass.
- The CLI entry points run unchanged: `python3 tools/sample.py --help` and
  `python3 tools/fidelity.py --help` exit 0 and print the same usage text as before.
- `make check` passes after the final edit.
- No behavior change: `git diff` shows moves, import lines and patch targets only.

### Group the flat tests/support/ modules into per-family packages (planned 2026-11-21 by the organize role)

**Needs review 2026-11-21 by feature: too large for one run.** The entry covers 89 flat modules and 513 importing test files (counts re-verified: `ls tests/support/*.py | wc -l` gives 89; `rg -l 'from support\.|import support\.' tests` gives 513), plus per-module `mock.patch` retargeting and a family-by-family import graph analysis to decide which modules stay at top level. That is well beyond one run. Suggested split for the plan role: one entry per family slice (starting with `install_`), each landing its modules, importers, patch targets and doc paths together.

**Needs review 2026-11-21 by feature: too large for one run** — 89 flat modules and 513 importing files (`rg -l 'from support\.|import support\.' tests`), plus `mock.patch` targets and docs; the entry's own slicing by family needs several runs.

**Needs review 2026-11-21 by feature: too large for one run** — 89 flat modules and about 513 importing files (`rg -l`) must move family by family, each family landed whole with its patch targets and doc paths; that exceeds one run's budget. The entry's own `install_` slice is a reasonable first step for a later run.

**Needs review 2026-11-21 by feature: too large for one run.** 89 modules and 513 importers; the acceptance criteria need every family moved (`ls tests/support/*.py` lists only shared modules), beyond one run's reading and tool-call budget. The entry's own approach slices it by family, so a later run can land one family whole (install_ first, as the entry suggests).

**Needs review 2026-11-21 by feature: too large for one run.** Measured on this checkout: `ls tests/support/*.py | wc -l` is 89 and `rg -l 'from support\.|import support\.' tests` matches 513 files, so every family slice rewrites hundreds of importers and patch targets. The entry's own approach requires family-by-family landings, and a single tick cannot satisfy the acceptance criterion that `ls tests/support/*.py` lists only shared modules. Needs a plan role to split it into per-family entries.

**Goal.** `tests/support/` holds 89 flat `.py` modules beside its `validation_gaps/`
package. Shared plumbing (temp dirs, process runners, stubs, assertions) sits next to
per-suite case data and reference constants, all with the same flat namespace. A reader
cannot tell from the directory which helper belongs to which suite. Split the flat
modules into a shared top level plus one subpackage per family, following the
`tests/support/validation_gaps/` package that already exists.

**Cost today.** Evidence: `ls tests/support/*.py | wc -l` gives 89. `rg -l 'from support\.|import support\.' tests`
finds 513 files that import a flat support module by name, so a change to one family
is found by grepping names, not by path. Family prefixes are visible in the listing:
`gtk_` and `gtk4_` (8 modules together, 2 of them `gtk4_`), `firefox_` (4), `file_dialog_`
and `file_identity` (3), `install_` (3), `check_` (3), `render_` (3), and `splash_`,
`kvantum_`, `cursor_`, `apply_`, `svg_`, `fidelity_`, `kde_`, `process_` (2 each).
Several of these are per-suite case data (for example `gtk_osd_cases.py`,
`firefox_chrome_cases.py`), not shared helpers.

**Target structure.**
- `tests/support/` keeps only modules whose importers span more than one family:
  process and temp-dir helpers, stubs, error and rejection assertions, and the
  `containment.py`, `repo_root.py` and `xcursor.py` copies that stay on purpose (L7).
- One subpackage per family with `__init__.py`: `tests/support/gtk/`,
  `tests/support/firefox/`, `tests/support/render/`, `tests/support/splash/`,
  `tests/support/kvantum/`, `tests/support/cursor/`, `tests/support/apply/`,
  `tests/support/install/`, `tests/support/fidelity/`, and so on for the families
  above. A module moves into the family whose tests import it; a module that two
  families import stays at the top level.
- The module names lose their family prefix inside the package
  (`tests/support/gtk_css.py` becomes `tests/support/gtk/css.py`). When two modules
  would share a name inside one package, keep the `gtk4_`/`gtk_` distinction in the
  file name.
- `validation_gaps/` and any other existing subpackage keep their paths.

**Files touched.** Each moved module; every importer under `tests/` (the 513 files
above, counted by `rg -l`); every `mock.patch` target string that names a moved module
(retarget each to the module whose global the caller resolves, per the L4 lesson);
`docs/invariants.md` and any doc that names a `tests/support/` path (grep
`tests/support/`).

**Approach.** Cut the work into slices by family, and land each family whole: its
modules, its importers, its patch targets and its doc references in one change. A slice
never leaves one family under two paths. Do the smallest family first (`install_`, 3
modules) to measure the import-rewrite cost, then `gtk`, which is the largest. The
`tools/` regroup (`## Planned`, "Group the flat tools/ modules") is independent: it
touches `tools/` and the `tools/` imports, not `tests/support/`.

**Acceptance criteria.**

- `ls tests/support/*.py` lists only the shared top-level modules; each family lives in
  its own subpackage directory with an `__init__.py`.
- For every moved module, `rg -n` for its old flat import (`support\.<old_name>` and
  `from support import <old_name>`) over `tests/`, `tools/`, `Makefile` and `*.md` finds no
  stale reference.
- Every `mock.patch` string that names a moved module resolves, and the tests that patch
  them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets and doc paths
  only.
- `make check` passes after the final edit, apart from main's known-red tests.


### Reference-checker suite extraction: move the declared-image stream tests into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_check_references_validation.py` (504 lines) mixes two kinds of check:
sources.txt record and URL rules, and the declared-image payload checks. Three classes pin the
payload side — `TestAcceptedImageFormats` (six tests: the JPEG, GIF87a/89a and WebP signatures,
the RIFF/WAVE refusal and the one-open prefix read), `TestImageStreamCompleteness` (thirteen
tests: `tools.image_format.is_complete` direction by direction for every format) and
`TestTruncatedDeclaredImage` (seven tests: the truncation diagnostics and their CLI status).
Together they are about 240 lines. The other five classes (`TestSourceParser`,
`TestLineSplitting`, `TestFilenameMustBeBare`, `TestEmptyUrlRemainder`,
`TestUrlProblemDiagnostics`) and the name-safety classes (`TestUndeclaredImageExtension`,
`TestControlCharactersInFilenames`, `TestNullByteFilename`) stay. PRINCIPLES.md asks for one
responsibility per file, so move the three payload classes whole into a new
`tests/test_check_references_image_streams.py`. Keep class names, docstrings, comments and
every test body unchanged. No tool, Makefile or check behavior changes. This plan is
independent of every other Planned entry and of the pending changes: none of them touches
these files. The module-level helper `assert_url_problem_not_the_scheme` stays with its only
caller `TestUrlProblemDiagnostics`, so nothing moves into `tests/support/` (L4).

**Approach and files touched.**

- **New `tests/test_check_references_image_streams.py`.** Start with a module docstring saying
  it pins the checker's declared-image payload rules — accepted raster signatures and each
  format's stream ending — with the checker's filesystem loader as the unit under test, and
  that the sources.txt record rules and the undeclared-scan and name-safety checks stay in
  `tests/test_check_references_validation.py`. Then add the three classes in their current
  order, above an `if __name__ == "__main__": unittest.main()` guard (L1). A planning read
  found the moved bodies use `contextlib`, `io`, `unittest`, `from unittest import mock`,
  `CheckerTestCase`, `assert_problem`, `check_references_in`, `reference_set` (from
  `support.check_references_fixtures`), `GIF_MAGICS`, `JPEG_MAGIC`, `PNG_MAGIC`,
  `TERMINAL_GIF`, `TERMINAL_JPEG`, `TERMINAL_PNG`, `is_complete` (from `tools.image_format`)
  and `reference_validation`. Import those the way the file they leave does; the module also
  defines its own `COMPLETE_PNG = PNG_MAGIC + TERMINAL_PNG`, which `TestAcceptedImageFormats`'s
  one-open test uses.
- **`tests/test_check_references_validation.py`.** Delete the three classes. A planning grep
  found `contextlib`, `io`, `from unittest import mock`, `GIF_MAGICS`, `JPEG_MAGIC`,
  `TERMINAL_GIF`, `TERMINAL_JPEG`, `is_complete` and `reference_validation` unused by the
  remaining classes, so drop them from the imports (`tests/test_no_unused_imports.py` enforces
  this); keep `tempfile`, `Path`, `PNG_MAGIC`, `TERMINAL_PNG` (both feed `COMPLETE_PNG`, still
  used by the staying classes), `reference_sources`, `CheckerTestCase`, `assert_problem`,
  `check_references_in`, `reference_set` and `assert_escapes_escape_character` — the
  implementer re-checks each with grep. Rewrite the module docstring to describe the record,
  URL and name checks it still pins, and add a sentence naming
  `test_check_references_image_streams.py` for the declared-image payload tests.
- **`docs/invariants.md`.** The reference-checker rows anchor the moved classes:
  the row on the missing stream terminator names
  `tests/test_check_references_validation.py::TestImageStreamCompleteness` and
  `::TestTruncatedDeclaredImage`, and the declared-image-prefix row names
  `::TestAcceptedImageFormats::test_declared_image_prefix_is_read_with_one_open`. Repoint those
  three anchors to `tests/test_check_references_image_streams.py::<same path>`, leaving both
  rows' prose and other anchors unchanged. The `reference_sources.py` ownership row anchors
  `::TestSourceParser`, which stays, so it is untouched.
- **Prose touch-ups.** `tests/support/check_references_fixtures.py`'s module docstring lists
  the modules that use the fixtures; add `test_check_references_image_streams` to that list.
  `tools/reference_validation.py`'s module docstring names
  `tests/test_check_references_validation.py` in the suite-split sentence; name both test
  modules there. No other prose mentions the moved classes.
- **Anchors.** A planning grep of the whole tree (excluding `.git`, `__pycache__` and the
  archives) found the three class names only in `tests/test_check_references_validation.py`
  and the two `docs/invariants.md` rows, and found no mention of them in
  `tests/support/validation_gaps/`, `tests/test_ci_workflow.py`, `docs/rendering.md` or
  `docs/fidelity.md` (L1, L3). Re-run the grep and repoint any new anchor.

**Acceptance criteria.**

- Running `python3 -m unittest test_check_references_image_streams` from `tests/` runs the
  moved tests, named as the methods of `TestAcceptedImageFormats`,
  `TestImageStreamCompleteness` and `TestTruncatedDeclaredImage` were before the move, and
  they pass.
- `tests/test_check_references_validation.py` defines none of the moved classes. Every staying
  class and test method keeps its name, and the module passes.
- Run `grep -rn 'TestAcceptedImageFormats\|TestImageStreamCompleteness\|TestTruncatedDeclaredImage'
  --exclude-dir=.git --exclude-dir=__pycache__ .`, excluding `PLANS.md`, `PLANS-DONE.md` and
  `BUGS-FIXED.md`. It finds only `tests/test_check_references_image_streams.py`,
  `docs/invariants.md`, the two prose touch-ups and the rewritten docstring of
  `tests/test_check_references_validation.py`, and every invariants anchor for these classes
  names `tests/test_check_references_image_streams.py`.
- `wc -l` shows `tests/test_check_references_validation.py` under 300 lines and the new module
  under 290.
- Nothing under `theme/`, `tools/` except `reference_validation.py`'s docstring, or the
  `Makefile` changes.
- `make check` passes after the final edit. The only allowed exception is main's known-red
  `TestNoReproLedger` tests, if main still fails them (L6). Do not edit `BUGS-FIXED.md` or the
  ledger baseline to make them pass.

### PNG chunk suite extraction: move the byte-framing rules and the iterator tests into their own module (planned 2026-11-21 by the plan role)

**Needs review 2026-11-21 by feature: plan defect — the extraction and both named files already landed on main in commit b269bf2; complete against that commit rather than re-running the assigned work.**

**Needs review 2026-11-21 by feature: plan defect — the deliverable is already on main in b269bf29, which adds `tests/test_png_chunk_framing.py` and removes the moved tests from `tests/test_png_chunks.py`.**

**Goal.** `tests/test_png_chunks.py` (512 lines) mixes two concerns. Most of
`TestChunkFraming` pins the chunk-stream ordering rules through `decode_png`
(consecutive IDATs, one IHDR/PLTE/tRNS each, IHDR first, nothing after IEND,
unknown ancillary chunks ignored). Eight tests plus `TestIterChunks` instead pin
how a byte stream is cut into chunks at all: chunk-type validity, the 2^31-1
length cap, CRC integrity and the truncation diagnostics, and the
`tools/png/chunks.iter_chunks` iterator contract tested directly. PRINCIPLES.md
asks for files small enough to read in one sitting. Move that second group into
a new `tests/test_png_chunk_framing.py`. No fixture behavior and no test body
changes. This plan is independent of the other Planned entries and of every
pending change; none of them touches these files (`tools/png/` is already a
package, so the tools/ regroup entry does not repoint these imports).

**Approach.**

- Create `tests/test_png_chunk_framing.py`. Give it a module docstring saying it
  pins `tools/png/chunks.py`'s byte framing — that a chunk type is four ASCII
  letters with an uppercase reserved third letter, that a length stays at or
  under the spec maximum, that every chunk's CRC is checked even when the chunk
  is ignored, and how truncation is named — plus the `iter_chunks` iterator
  contract, and that the ordering, duplication and IEND rules through
  `decode_png` stay in `tests/test_png_chunks.py`. Import `struct`, `unittest`,
  `from support import repo_root`, `from support.png_fixtures import`
  `_chunk, decode_error_message, ihdr_chunk, ihdr_end, png_stream, rgb_image,
  solid_rgb, splice_after_ihdr`, `from tools import png` and
  `from tools.png import chunks`.
- Define `class TestChunkFramingRules(unittest.TestCase)` holding these eight
  methods verbatim, in their current order: `test_rejects_chunk_type_that_is_not_four_ascii_letters`,
  `test_rejects_chunk_type_with_lowercase_reserved_bit`,
  `test_rejects_chunk_length_above_the_spec_maximum`,
  `test_a_chunk_length_at_the_spec_maximum_is_not_refused_as_oversized`,
  `test_ignored_ancillary_chunk_still_has_its_crc_checked`,
  `test_rejects_bad_chunk_crc`, `test_rejects_truncated_chunk_crc`,
  `test_rejects_truncated_chunk_payload`.
- Move `class TestIterChunks` (its docstring included) verbatim, after
  `TestChunkFramingRules`; both classes sit above an
  `if __name__ == "__main__": unittest.main()` guard (L1).
- In `tests/test_png_chunks.py`, delete the moved tests and `TestIterChunks`,
  keep the surviving tests under the unchanged class name `TestChunkFraming`,
  and update the module docstring: drop the moved framing items (bad chunk
  types, oversized lengths, bad or truncated CRCs, the iterator) from its list,
  and say byte framing and the iterator live in `tests/test_png_chunk_framing.py`
  while header-field validation keeps its tests here and the tRNS length rules
  in `test_png_malformed`. Drop the now-unused `from tools.png import chunks`
  and the `ihdr_end` fixture import (a grep while planning found both used only
  by moved code); re-check every remaining import with grep —
  `test_no_unused_imports` enforces this.
- Repoint the `docs/invariants.md` row that begins "PNG chunk types contain four
  ASCII letters" from
  `tests/test_png_chunks.py::TestChunkFraming::...` to
  `tests/test_png_chunk_framing.py::TestChunkFramingRules::...` for both of its
  anchors, leaving the row's prose and other columns alone. The rows that anchor
  the ordering, duplication and IEND rules by the bare `TestChunkFraming` name
  stay as they are: the class still exists in `tests/test_png_chunks.py`. A grep
  while planning found no other reference to the moved tests, to `TestIterChunks`
  or to `iter_chunks` test anchors in `docs/`, `tests/support/validation_gaps/`
  or `tests/test_ci_workflow.py` (L1). Re-grep before finishing.

**Files touched.** `tests/test_png_chunks.py`, `tests/test_png_chunk_framing.py`
(new), `docs/invariants.md`.

**Acceptance criteria.**

- `python3 -m unittest test_png_chunk_framing`, run from `tests/`, runs the
  eight `TestChunkFramingRules` tests and the four `TestIterChunks` tests, and
  they pass.
- `tests/test_png_chunks.py` defines neither `TestChunkFramingRules` nor
  `TestIterChunks`, does not import `chunks` or `ihdr_end`, and still defines
  `TestChunkFraming` with its surviving ordering, duplication and IEND tests
  under their unchanged names; the module passes.
- The `docs/invariants.md` four-ASCII-letters row names both tests by their
  `tests/test_png_chunk_framing.py::TestChunkFramingRules::` paths, and a
  repo-wide grep (excluding `PLANS-DONE.md` and `BUGS-FIXED.md`) for
  `test_png_chunks.py::TestChunkFraming::test_rejects_chunk_type_that_is_not_four_ascii_letters`
  or either length-cap test path finds nothing.
- `wc -l` shows `tests/test_png_chunks.py` under 330 lines and the new module
  under 250.
- Nothing under `theme/`, `tools/`, `tests/support/` or the `Makefile` changes.
- `make check` passes after the final edit. The only allowed exception is main's
  known-red `TestNoReproLedger` tests, if main still fails them (L6). Do not edit
  `BUGS-FIXED.md` or the ledger baseline to make them pass.

## Done

### GTK 3 suite extraction: isolate drag-and-drop declarations (planned 2026-11-18 by the plan role) — done 2026-11-18 by the feature role

**Goal.** Give GTK 3 header drag-feedback declaration checks a focused
suite outside the oversized views module. This relocation is independent
of the waiting paned-handle and pending message-dialog extractions.

**Approach and files touched.** Move
`TestGtkThemeViews.test_header_drop_indicator`,
`test_header_drop_arm_carries_no_padding` and
`test_no_dndtarget_node_declared` from `tests/test_gtk_theme_views.py` to
new `tests/test_gtk_theme_drag_drop.py::TestGtkThemeDragDrop`, preserving
their bodies. Inherit `support.gtk_rule_cases.GtkSheetRuleCases` and
`unittest.TestCase`; set
`CSS_PATH = ROOT / "theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css"`, importing
`ROOT` from `support.repo_root` and `BLACK` and `SELECTION` from
`support.platinum_palette`. The base supplies sheet parsing and assertions;
no shared helper change is needed. Update the source routing docstring and
repoint the moved anchors in the GTK 3 drag-and-drop row of
`docs/invariants.md`, retaining its guarantee and stock-resource provenance.
Search `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
and `tests/support/` for other moved anchors. Keep GTK 4 coverage and GTK 3
rubberband checks in their existing suites; theme sheets need no changes.

**Acceptance criteria.**

- Discovery exposes the named methods in the destination without duplicate
  methods in views or inherited shared-control tests in the destination.
  Source and destination pass independently through project check selectors.
- The plain, legacy dotted-header and spaced-header selector spellings,
  each with plain, hover, active and selected states, retain selection fill,
  black ink, cleared background image and shadows, no border and zero
  radius checks. Changing just the legacy hovered header arm's fill fails
  a moved check.
- Adding padding to `treeview.view button.dnd` or declaring a `dndtarget`
  node in the GTK 3 sheet fails a moved check.
- Invariant anchors resolve and full `make check` passes. This relocation
  adds no rendered-pixel claim.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

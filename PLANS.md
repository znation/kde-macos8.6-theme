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

### PNG read suite extraction: move the size-read tests into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_png_read.py` (330 lines) mixes two units of
`tools/png/loader.py`: `read_png`'s whole-file input guards — the file-size
cap, the regular-file check, the fd lifecycle under failing `fstat`/`fdopen`
and `read`, and the FIFO refusal — and `read_png_size`'s bounded prefix read
and its refusal parity with the decoder. The ten `test_read_png_size_*`
methods plus the `_assert_size_matches_decode` helper are about 150 lines and
concern only the size read, so per PRINCIPLES.md move them into a new
`tests/test_png_read_size.py` as `TestReadPngSize`. Keep class name,
docstrings, comments and every test body unchanged. This is independent of the
waiting PNG chunk entry: that one moves `TestChunkFraming` and `TestIterChunks`
out of `tests/test_png_chunks.py` and touches none of these files, and no other
Planned entry, pending change or finished plan covers `test_png_read.py`.

**Approach and files touched.**

- **New `tests/test_png_read_size.py`.** Module docstring: it pins
  `tools/png/loader.py`'s `read_png_size` — the header-prefix read whose peak
  allocation stays small, the inclusive file-size cap, the refusal to decode,
  and that every malformed-stream refusal names the file with exactly the
  message `read_png` gives, so a sampler that only wants dimensions cannot
  accept a header the decoder refuses — and says `read_png`'s whole-file
  guards stay in `tests/test_png_read.py`. Then `TestReadPngSize` with the
  ten `test_read_png_size_*` methods and `_assert_size_matches_decode` in
  their current order, above an `if __name__ == "__main__":` guard (L1).
  Imports: `unittest`, `zlib`, `from unittest import mock`,
  `error_message` from `support.error_assertions`, `_chunk`, `ihdr_chunk`,
  `png_stream`, `rgb_image`, `with_ihdr_byte` and the new `input_file` from
  `support.png_fixtures`, `from tools import png`, and `loader` and `header`
  from `tools.png` (`header` for the pixel-limit test's `MAX_PIXELS` pin).
- **Shared `_file` helper goes to support, not to a test-module import (L4).**
  Both modules' tests call `self._file(name, data)`, so add
  `input_file(case, name, data) -> Path` to `tests/support/png_fixtures.py`
  (a fresh `make_tmp_dir` directory from `support.tmp_dir` with *data*
  written to *name*), and keep a one-line `def _file(self, name, data):`
  delegation in both `TestReadPng` and `TestReadPngSize` so the test bodies
  stay byte-identical. `png_fixtures.py`'s module docstring's suite list
  gains `tests/test_png_read_size.py`.
- **`tests/test_png_read.py` after the move.** Keeps `TestDecoderInputAnnotations`
  and `TestReadPng` with the ten `test_read_png_*` methods,
  `_assert_size_matches_decode` deleted with its callers, and the module
  docstring rewritten to say it pins `read_png`'s input guards and error
  paths, pointing the size read at `tests/test_png_read_size.py`. The import
  block drops what only the size tests used: `zlib`, `_chunk`, `ihdr_chunk`,
  `png_stream`, `with_ihdr_byte` and `header` (keep `loader` for the cap and
  fd patches, `png_read` for the annotation test, and
  `peak_allocation`, `tracking_closes`, `failing_fdopen`, `make_fifo`,
  `snippet_child`, `repo_root` and `rgb_image` for the staying tests).
- **Docstring counts (L4).** `tests/test_allocation_fixtures.py`'s docstring
  names the suites using `peak_allocation`: add `test_png_read_size` beside
  `test_png_read`.
- **Anchors (L1).** `docs/invariants.md`'s declared-size row repoints its
  three anchors to `tests/test_png_read_size.py::TestReadPngSize::`
  paths; the row's guarantee text is unchanged. Grep
  `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/` for `TestReadPng` and `read_png_size` to
  confirm no other anchor moved (a planning grep found only the
  `docs/invariants.md` row above).

**Acceptance criteria.**

- `python3 -m unittest test_png_read_size test_png_read`, run from `tests/`,
  passes, with all ten `test_read_png_size_*` methods under `TestReadPngSize`
  and none left in `tests/test_png_read.py`; both modules keep their
  `Test*` classes above the `__main__` guard.
- Refusal parity stays pinned: changing `read_png_size`'s diagnosis for a
  corrupt IHDR CRC, an unsupported IHDR field or a stream whose first chunk is
  not IHDR fails a `_assert_size_matches_decode` test, because the size read's
  message must equal `read_png`'s for the same bytes.
- A repo-wide grep (excluding `PLANS-DONE.md` and `BUGS-FIXED.md`) for
  `test_png_read.py::TestReadPng::test_read_png_size_` finds nothing, and the
  repointed `docs/invariants.md` anchors all name existing tests.
- `wc -l` shows `tests/test_png_read.py` under 200 lines and the new module
  under 170.
- `make check` passes after the final edit. The only allowed exception is
  main's known-red `TestNoReproLedger` tests, if main still fails them (L6).
  Do not edit `BUGS-FIXED.md` or the ledger baseline to make them pass.

### Group the tests/support fidelity and kvantum modules into subpackages (part 3/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Needs review 2026-11-21 by feature: too large for one run**

**Goal.** Land the fidelity- and kvantum-family slices of the
tests/support regroup (see part 1/6 for the split's counts and rules; the
parts are independent).

**Modules to move (importer files counted on main).** `fidelity_cli_case`
(40) and `fidelity_delta_fixtures` (4) → `tests/support/fidelity/` with
`__init__.py`: `cli_case.py`, `delta_fixtures.py`. `kvantum_config_spec`
(4) → `tests/support/kvantum/` with `__init__.py`: `config_spec.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `kvantum_fixtures` (imported by
kvantum tests and the render dialog-gate tests), `jpeg_sampler_fixture`
(fidelity and sample tests), `png_fixtures` (fidelity, png and sample
tests), `sunken_field_reference` and `firstboot_lineedit` (each spans
desktoptheme, kvantum and render tests).

**Files touched.** The three moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/fidelity/ tests/support/kvantum/` lists both
  `__init__.py` files and the three moved modules;
  `rg -n 'support\.(fidelity_cli_case|fidelity_delta_fixtures|kvantum_config_spec)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Group the tests/support gtk modules into a subpackage (part 4/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Goal.** Land the gtk-family slice of the tests/support regroup (see
part 1/6 for the split's counts and rules; the parts are independent).

**Modules to move (importer files counted on main).** `gtk_osd_cases` (5),
`gtk_staging_case` (2), `gtk_child_probe` (7) → `tests/support/gtk/` with
`__init__.py`: `osd_cases.py`, `staging_case.py`, `child_probe.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `gtk_fixtures` (imported by the
cross-family `gtk_rule_cases`), `gtk_rule_cases` and `gtk_theme_spec`
(each also imported by firefox tests), `gtk_css` (firefox, gtk and gtk4
tests), `gtk4_sheet`, `gtk4_child_probe` and `gui_tests` (each spans gtk
and gtk4 tests). There is no gtk4 slice: every `gtk4_*` module is
cross-family on main today.

**Files touched.** The three moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/gtk/` lists `__init__.py` and the three moved
  modules; `rg -n 'support\.(gtk_osd_cases|gtk_staging_case|gtk_child_probe)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Group the tests/support apply, cursor, xcursor, splash, icon and desktoptheme modules into subpackages (part 5/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Goal.** Land the six small single-family slices of the tests/support
regroup (see part 1/6 for the split's counts and rules; the parts are
independent).

**Modules to move (importer files counted on main).** `apply_target_cases`
(2), `apply_theme_stubs` (2), `cursor_case` (3; all importers are apply
tests) → `tests/support/apply/` with `__init__.py`: `target_cases.py`,
`theme_stubs.py`, `cursor_case.py`. `cursor_artifact_cases` (3) →
`tests/support/cursor/` with `__init__.py`: `artifact_cases.py`.
`xcursor_frames` (2) → `tests/support/xcursor/` with `__init__.py`:
`frames.py`. `splash_fixtures` (3) → `tests/support/splash/` with
`__init__.py`: `fixtures.py`. `icon_theme_inventory` (2) →
`tests/support/icon/` with `__init__.py`: `theme_inventory.py`.
`raised_face_case` (2), `thumb_fixtures` (3) → `tests/support/desktoptheme/`
with `__init__.py`: `raised_face_case.py`, `thumb_fixtures.py`.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: `xcursor` (imported by `tools/` and
file-identity tests), `cursor_theme_fixtures` (imported by apply tests and
a support module), `firstboot_lineedit`, `sunken_field_reference` and
`reference_button` (each spans two families).

**Files touched.** The nine moved modules, their importer files under
`tests/`, any `mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/{apply,cursor,xcursor,splash,icon,desktoptheme}/`
  lists each `__init__.py` and the nine moved modules;
  `rg -n 'support\.(apply_target_cases|apply_theme_stubs|cursor_case|cursor_artifact_cases|xcursor_frames|splash_fixtures|icon_theme_inventory|raised_face_case|thumb_fixtures)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

### Group the tests/support kde, local_hook and svg_assertions modules into their packages (part 6/6 of the tests/support regroup) (planned 2026-11-21 by the plan role)

**Goal.** Land the kde-config, local-hook and svg-assertions slices of the
tests/support regroup (see part 1/6 for the split's counts and rules; the
parts are independent).

**Modules to move (importer files counted on main).** `kde_ini_corpus` (1),
`kdedefaults_mirror_cases` (2), `kwinrc_uninstall_wording` (4) →
`tests/support/kde/` with `__init__.py`: `ini_corpus.py`,
`kdedefaults_mirror_cases.py`, `kwinrc_uninstall_wording.py`.
`local_hook_repos` (3) → `tests/support/local_hook/` with `__init__.py`:
`repos.py`. `svg_fixtures` (7) → `tests/svg_assertions/fixtures.py`, per
the recorded lesson that generic SVG test helpers live in
`tests/svg_assertions/<concern>.py`, not under `tests/support/`; update
the re-exporting modules and their tests there.

**Approach.** As in part 1/6: move, rewrite importer lines and bare
references, retarget `mock.patch` strings, verify importers before each
move. Known stays, already measured: the meta-test fixtures
(`unused_imports`, `mutant_module`, `invariants_mutations`,
`placeholders_mutations`, `check_parallel_fixtures`) stay flat — they
police the whole suite, not one family — as does `config_home_cases`
(spans the kde config surfaces and the other install families).

**Files touched.** The five moved modules, their importer files under
`tests/` (for `svg_fixtures`, the `tests/svg_assertions/` modules), any
`mock.patch` target strings, and docs naming the old paths.

**Acceptance criteria.**

- `ls tests/support/kde/ tests/support/local_hook/` lists both
  `__init__.py` files and the four moved modules, and
  `tests/svg_assertions/fixtures.py` exists;
  `rg -n 'support\.(kde_ini_corpus|kdedefaults_mirror_cases|kwinrc_uninstall_wording|local_hook_repos|svg_fixtures)'`
  over `tests/`, `tools/`, `Makefile`, `docs/` and `*.md` finds no stale
  reference.
- Every `mock.patch` string naming a moved module resolves, and the tests
  that patch them pass.
- No behavior change: `git diff` shows moves, import lines, patch targets
  and doc paths only.
- `make check` passes after the final edit, apart from main's known-red
  tests.

## Done

### PNG chunk suite extraction: move the byte-framing rules and the iterator tests into their own module (planned 2026-11-21 by the plan role) — done 2026-11-21 by the feature role

**Needs review 2026-11-21 by feature: plan defect — the deliverable is already on main: b269bf29 adds `tests/test_png_chunk_framing.py` (a copy at first) and the reviewer fix da0b8da8d deletes the duplicated tests from `tests/test_png_chunks.py`; complete against those two commits rather than re-running the assigned work.**

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

**Done note 2026-11-21.** Completed against b269bf29 as the plan-defect notes
direct: the framing module and its tests were already on main, so the remaining
work was deleting the moved tests from `tests/test_png_chunks.py`, dropping the
now-unused `chunks`/`ihdr_end` imports, updating the module docstring and
repointing the second invariants anchor. `python3 -m unittest
test_png_chunk_framing` from `tests/` runs the eight `TestChunkFramingRules`
and four `TestIterChunks` tests, OK; the two modules together run 35 tests, OK.
`wc -l` shows `tests/test_png_chunks.py` at 334 lines (the plan estimated under
330; the file is still one concern and reads in one sitting) and the framing
module at 140. The repo-wide grep for the old
`test_png_chunks.py::TestChunkFraming::` anchor paths finds nothing outside
PLANS-DONE.md and BUGS-FIXED.md.

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

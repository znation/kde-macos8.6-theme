# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Group the flat tools/ modules into per-subsystem packages (planned 2026-11-19 by the organize role)

**Needs review 2026-11-19 by feature: too large for one run**

**Needs review 2026-11-19 by feature: too large for one run.** Measured in this checkout: 106 flat `tools/*.py` modules (the entry says 107), 199 Python files that import a prefixed flat module (the entry says 97), 172 test files that call `mock.patch`, and 11 markdown/Makefile files naming flat modules. One change touching all of these, with per-module patch-target ownership decisions and the `tools/render_workflow.py` anchor (absent; its successor is not found by `git log --follow`), exceeds one run's budget. Suggest the plan role split it into one subsystem family per entry (e.g. `render_` first), each landing its own package and its importers together.

**Needs review 2026-11-19 by feature: too large for one run** — 106 modules in `tools/`, about 195 import lines matching the prefixed families across the tree (grep `from tools.<family>_` / `import <family>_`), plus every `mock.patch` target, the Makefile and docs; the whole move must land as one change, which exceeds one run's scope.

**Goal.** `tools/` holds 107 flat modules with no grouping beyond their name
prefixes: `render_` (12), `fidelity_` (12), `sample_` (11), `cursor_` (10),
`check_` (7), `firefox_` (5), `apply_` (5), `uninstall_` (4), `gtk_` (4), plus
single files for other subsystems. A reader cannot see subsystem boundaries from
the directory listing, and 97 files import these modules by their flat names.
Regroup them into subpackages, following the existing `tools/png/` package.

**Cost today.** Evidence: `ls tools | wc -l` gives 107 modules; `rg -l` finds 97
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

### Cursor set suite extraction: move the per-glyph shape pins into their own module (planned 2026-11-20 by the plan role)

**Goal.** Shrink the 853-line `tests/test_cursors_theme.py` and keep it on
the Xcursor container, alias bytes and generator output. Its
`TestCursorSet(unittest.TestCase)` class also holds the per-glyph drawing
pins. Each of those checks one glyph's geometry: a symmetry, a ring, a
plus, a watch face, a pencil or a zoom pair. Together they fill most of the
class's second half. Changes test organization only. Independent of the
waiting "Firefox panels suite extraction" and "Group the flat tools/ modules"
entries: it shares no file with either.

**Approach.** Create `tests/test_cursor_glyph_shapes.py` with one class,
`TestCursorGlyphShapes(unittest.TestCase)`. Move these `TestCursorSet` methods
into it, keeping their names and bodies:
`test_size_ver_is_the_horizontal_glyph_rotated_a_quarter_turn`,
`test_move_and_axis_resize_grids_are_mirror_symmetric`,
`test_fleur_grid_is_symmetric_about_its_diagonal`,
`test_size_bdiag_is_the_forward_diagonal_mirrored`,
`test_crosshair_black_cells_lie_on_the_centre_row_or_column`,
`test_not_allowed_is_a_ring_with_a_slash`,
`test_dnd_copy_plus_outline_separates_the_arms`,
`test_not_allowed_ring_interior_is_transparent_except_the_slash` and its
helpers `_is_slash_cell`, `_is_inside_not_allowed_ring` and
`_assert_white_ring_shield`, `test_dnd_copy_is_a_centred_plus`,
`test_grab_and_grabbing_pin_open_and_closed_hands`,
`test_context_menu_keeps_the_arrow_cells`,
`test_context_menu_pins_the_menu_panel`, the `_sixteen_pixel_image` helper,
`test_watch_draws_the_round_faced_wristwatch`,
`test_help_pins_the_arrow_and_question_mark`,
`test_progress_pins_the_arrow_and_watch_face`,
`test_help_and_progress_draw_the_arrow_cells_at_the_same_coordinates`,
`test_pencil_draws_a_diagonal_shaft_to_its_writing_tip` and
`test_zoom_in_and_out_differ_only_at_the_plus_arms`.

Keep these in `TestCursorSet`. They are whole-set or alias-byte checks, and
they use `_repo_bytes` or `VECTOR_CURSORS`, which stay in the original module:
`test_every_cursor_grid_shields_its_black_from_transparent` with
`_assert_grid_is_shielded` and `_assert_black_cell_is_shielded`,
`test_dnd_aliases_reuse_the_existing_glyphs` and
`test_help_and_progress_alias_names_reuse_their_canonical`.

The moved methods use only `cursor_art`, `make_cursors`, `decode_rgba` and the
`support.cursor_artifact_cases` names `BLACK`, `WHITE`, `TRANSPARENT`,
`CURSORS`, `_pixel` and `_read_cursor`. None of them use `_repo_bytes`,
`_scaled`, `HOTSPOTS`, `cursor_art_pointers` or the original module's
constants, so no new `tests/support` module is needed. Import those names in
the new module the same way the original does (`from support import repo_root`
first). The original module keeps the imports its remaining tests still use;
re-grep each one after the move and drop any that no longer has a use. Give
the new module a docstring that says it pins each canonical grid's drawn
shape, and that this is our own art (no reference screenshot shows the
pointer). Add one sentence to the original module's docstring that points at
the new module, beside its existing pointer to
`tests/test_cursors_vector_artifacts.py`.

**Files.** `tests/test_cursors_theme.py`, new
`tests/test_cursor_glyph_shapes.py`, `docs/invariants.md` (the `## icons`
cursor-set row's test column: add
`tests/test_cursor_glyph_shapes.py::TestCursorGlyphShapes` beside the
existing `TestCursorSet` anchors, which stay valid). A grep of `docs/`,
`README.md`, `Makefile`, `tests/support/` and `tests/test_ci_workflow.py` on
2026-11-20 found no other live reference to the moved method names or to
`test_cursors_theme`, apart from the `tests/test_make_cursors.py` docstring,
which still holds. Re-run that grep at implementation.

**Acceptance criteria.**

- `make check CHECK_TESTS='test_cursor_glyph_shapes'` runs every moved test
  name listed above under `TestCursorGlyphShapes`, and they pass.
  `git diff --color-moved` shows their bodies unchanged.
- `tests/test_cursors_theme.py` no longer defines any moved method name.
  It still defines `TestCursorArtifact` and the remaining `TestCursorSet`
  cases, including the three kept ones named above.
- No test module imports another test module. Nothing under `theme/`,
  `tools/` or the committed cursor files changes.
- The cursor-set row in `docs/invariants.md` names the new anchor, and
  `make check CHECK_TESTS='test_cursors_theme test_cursor_glyph_shapes test_invariants'`
  passes. A full `make check` after the final edit fails nothing beyond
  main's own known-red `test_validation_gaps.TestNoReproLedger` cases. Those
  fail on main without this change: `BUGS-FIXED.md` holds seven `no-repro`
  records against `NO_REPRO_BASELINE = 6` in
  `tests/support/validation_gaps/no_repro.py`, and the ci role owns that fix.
  This change edits neither `BUGS-FIXED.md` nor that baseline.

### Render CLI tests: move the output-publication cases into their own module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_render_failure_paths.py` is 846 lines, and PRINCIPLES.md asks for files
small enough to read in one sitting. Six tests near the end of `TestFailurePaths` check how the
render CLI publishes its output path, not how the session fails: whether it refuses an unusable
output before installing, copies a capture over the output, keeps the previous output when a
copy fails, and passes a dash-leading output through `make render`. This plan moves them,
unchanged, into a new `tests/test_render_output_cli.py`, next to the unit-level
`tests/test_render_output.py` that tests `tools/render_output.py` directly. No tool behavior and
no test body changes. Nothing under `## Planned` touches these files. The held "Group the flat
tools/ modules" entry would rename `tools.render_*` imports, but it only conflicts at merge time.

The six tests to move, keeping their names and order:
`test_unwritable_output_is_refused_before_installing`,
`test_a_read_only_output_directory_is_refused_before_installing`,
`test_a_capture_is_copied_to_the_output`,
`test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file`,
`test_a_fifo_refusal_is_reported_as_a_failed_render`,
`test_make_render_passes_a_dash_leading_output_as_a_path`.
The session timeout and SIGTERM tests after them
(`test_timeout_kills_the_session_group_and_exits_1`,
`test_sigterm_kills_the_session_group_and_removes_scratch`) are failure paths and stay.

**Approach and files touched.**

- `tests/support/render_stub_tools.py`: move `TestFailurePaths.stub_capture` and
  `TestFailurePaths.hidden_files` onto `StubTools`, keeping their bodies. `stub_capture` is
  also called by two tests that stay (`test_a_capture_of_the_wrong_size_exits_1_and_writes_nothing`
  and `test_an_unpainted_capture_exits_1_and_writes_nothing`). Per L4, a helper shared by both
  modules goes in `tests/support/` and neither test module imports the other. Add the
  `encode_png` import (`from tools.png.write import encode_png`) that `stub_capture` needs. Update
  the module docstring so it names both test modules as users. `assert_failed_run`'s docstring
  says "Shared by the 22 failure-path tails". None of the six moved tests calls it, so recount
  `self.assert_failed_run(` in `tests/test_render_failure_paths.py` with grep after the move and
  keep only a number grep confirms.
- New `tests/test_render_output_cli.py`:
  - Module docstring: it pins the render CLI's output-path contract (refusal before installing,
    copy-over, previous output kept on a failed or refused copy, no hidden leftovers, and
    `make render` passing a dash-leading `RENDER_OUTPUT` as a path) against the shell stubs. The
    publication unit tests stay in `tests/test_render_output.py`.
  - `class TestRenderOutputCli(StubTools, unittest.TestCase)` holds the six methods verbatim, in
    their current order. End the file with the `if __name__ == "__main__": unittest.main()` footer.
  - Import only what the bodies use. As of this plan that is `errno`, `os`, `shutil`,
    `subprocess`, `unittest`, `Path`, `mock`, `repo_root` from `support`, `call_main` from
    `support.cli_fixtures`, and
    `render_surface` and `render_workflow` from `tools`, plus `StubTools`. Confirm each import
    with grep.
- `tests/test_render_failure_paths.py`: delete the six methods and the two helpers. Drop the
  imports nothing left uses; `encode_png` stays, because the test that builds an all-black
  fixture inline still calls it. Check every import with grep, including `errno`, `shutil` and
  `subprocess`. Add one sentence to the module docstring pointing the output-publication cases
  at `tests/test_render_output_cli.py`.
- `docs/invariants.md`: change the two anchors that name moved tests from
  `tests/test_render_failure_paths.py::TestFailurePaths::<name>` to
  `tests/test_render_output_cli.py::TestRenderOutputCli::<name>`:
  `test_a_failed_copy_keeps_the_previous_output_and_leaves_no_partial_file` in the "The
  rendered surface is published atomically" row, and
  `test_a_fifo_refusal_is_reported_as_a_failed_render` in the "Render publication opens its
  capture source as a regular file" row. Leave the other anchors in those rows alone.
- `tests/test_render_output.py`: the `TestOutputProblem` docstring says "The CLI test in
  ``tests/test_render_failure_paths.py``". Point it at `tests/test_render_output_cli.py`.
- Per L1/L3, grep `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and
  `tests/support/validation_gaps/*.py` for the six moved names. As of this plan, the only hits
  outside the test file are the two invariants rows above. The validation-gap entries that
  name `TestFailurePaths` (`client-exit-stub-pidfile-race` in `no_repro.py` and
  `crashed-applet-setup-wait` in `slow_check.py`) name tests that stay. None of the moved
  tests is a `Test*DialogRender` gate, so `_GATE_FILES` does not apply. Archives keep their
  historical anchors.

**Acceptance criteria.**

- `tests/test_render_output_cli.py::TestRenderOutputCli` defines the six listed tests with the
  bodies they had in `TestFailurePaths`, and `tests/test_render_failure_paths.py` no longer
  defines any of them.
- The union of `test_*` method names across the two modules equals the set the original
  `tests/test_render_failure_paths.py` defined, with nothing lost or duplicated, and
  `tests/test_render_failure_paths.py` is under 730 lines (`wc -l`).
- `grep -n 'def stub_capture\|def hidden_files' tests/test_render_failure_paths.py` prints
  nothing. The wrong-size and unpainted-capture tests that stay still pass using the shared
  `stub_capture`.
- No test module imports another test module. Nothing under `tools/`, `theme/` or the
  `Makefile` changes.
- No anchor in `docs/` or `tests/` names a moved test under `tests/test_render_failure_paths.py`
  (`grep -rn` over the six names, excluding the two test modules). `make check
  CHECK_TESTS='test_render_failure_paths test_render_output_cli test_render_output test_invariants'`
  passes, and `make check` passes after the final edit, apart from main's known-red cases below.
- Main's known-red `TestNoReproLedger` cases
  (`test_every_record_names_a_reproduction` and `test_the_record_count_does_not_grow` in
  `tests/test_validation_gaps.py`) may still fail; they fail on main because BUGS-FIXED.md holds
  seven `no-repro` records against `NO_REPRO_BASELINE = 6`, and the ci role owns them. This change
  does not edit `BUGS-FIXED.md`, `tests/support/validation_gaps/no_repro.py` or
  `tests/test_validation_gaps.py`, and no other test fails.

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

### Install suite extraction: move the support-helper sharing pins into the support pins module (planned 2026-11-21 by the plan role)

**Goal.** `tests/test_theme_install.py` is 783 lines. Its module docstring says it pins
`make install`/`uninstall` behaviour, and that the pins of the shared install helpers
live in `tests/test_theme_install_support.py`. Two of its classes break that rule: they
pin test-support helpers, not `make`. `TestInstalledDestdirSharing` pins
`support/theme_install.py`'s `installed_destdir`, and `TestFailedInstallSharing` pins
`support/install_failure_cases.py`'s `FailedInstallPreservesPackage._install_ok`. Move
both classes, unchanged, into `tests/test_theme_install_support.py`, the module that
already pins the shared install helpers. Nothing else moves.

**Approach.**
- Cut `TestInstalledDestdirSharing` and `TestFailedInstallSharing` from
  `tests/test_theme_install.py`. Keep every method body, the private helpers
  `_forget_templates`, `_fake_install` and `_succeeded`, the class docstrings and the
  test names as they are. Paste both classes into `tests/test_theme_install_support.py`
  after `TestCopyShippedFile` and above the `if __name__ == "__main__":` guard (L1).
- In `tests/test_theme_install_support.py`, add the imports the moved classes need:
  `install_failure_cases` (added to the existing `from support import ...` line),
  `from support.install_failure_cases import FailedInstallPreservesPackage`, and
  `from support.tmp_dir import make_tmp_dir`, and `import contextlib`, because
  `test_an_escaping_template_symlink_is_refused` patches in `contextlib.nullcontext`.
  `os`, `unittest.mock`, `Path` and `theme_install` are already imported there.
- In `tests/test_theme_install.py`, drop the imports that only the moved classes used:
  `install_failure_cases` from the `from support import ...` line and the
  `from support.install_failure_cases import FailedInstallPreservesPackage` line, and
  `import contextlib`: nothing outside the moved classes uses it. Keep `os`,
  `unittest.mock` and `make_tmp_dir`, because the code that stays still uses them
  (`_assert_install_packages_refused`, `TestThemeSymlinkGuard`, `TestMakeEnv`). Check
  each remaining import with grep before you keep or drop it.
- Update the docstring of `tests/test_theme_install_support.py`. It now says the module
  pins helpers in `support/theme_install.py` only. Make it also name `installed_destdir`
  and `FailedInstallPreservesPackage._install_ok` from `support/install_failure_cases.py`.
  It should say these pins check that each helper installs once per class and copies
  the template per test. Leave the docstring of `tests/test_theme_install.py` as it is:
  it already sends readers to the support pins module.
- In `docs/invariants.md`, retarget the three anchors in the installed-template copy
  row ("The installed-template copy shared by `installed_destdir` and ...") from
  `tests/test_theme_install.py::TestInstalledDestdirSharing::...` and
  `tests/test_theme_install.py::TestFailedInstallSharing::...` to the same
  class/method under `tests/test_theme_install_support.py`. Leave the row's text alone.
- Grep `tests/support/validation_gaps/*.py`, `docs/`, `tests/` and `README.md` for
  `TestInstalledDestdirSharing` and `TestFailedInstallSharing`, and for
  `test_theme_install.py::` anchors naming either class (L1, L3). When this plan was
  written, only the `docs/invariants.md` row had any. Retarget any others you find.
- Out of scope: the `tests/support/` regroup (`## Planned`, "Group the flat
  tests/support/ modules into per-family packages"). If that entry's `install_` slice
  lands first, use whatever import path `install_failure_cases` has on main then.

**Files touched.** `tests/test_theme_install.py`, `tests/test_theme_install_support.py`,
`docs/invariants.md`.

**Acceptance criteria.**
- `tests/test_theme_install_support.py` defines `TestInstalledDestdirSharing`, with
  `test_repeated_calls_install_once_and_copy_the_tree`,
  `test_each_package_family_gets_its_own_template`, `test_a_failed_install_is_not_reused`,
  `test_an_escaping_template_symlink_is_refused` and
  `test_a_contained_template_symlink_is_copied_as_a_link`. It also defines
  `TestFailedInstallSharing`, with `test_install_ok_installs_once_and_copies_per_test` and
  `test_install_ok_refuses_an_escaping_template_symlink`. Each body matches the one it
  had in `tests/test_theme_install.py`; `git diff --color-moved` shows the classes as
  moved, not rewritten.
- `grep -n 'TestInstalledDestdirSharing\|TestFailedInstallSharing\|install_failure_cases\|contextlib' tests/test_theme_install.py`
  prints nothing, and `tests/test_theme_install.py` is under 600 lines (`wc -l`).
- Every other test class in `tests/test_theme_install.py` is still there with the same
  methods.
- `docs/invariants.md`'s installed-template copy row names its three tests under
  `tests/test_theme_install_support.py`. `tests/test_invariants.py` passes, which checks
  that each anchor resolves.
- No anchor in `docs/`, `tests/` or `README.md` names either moved class under
  `tests/test_theme_install.py`. Grep shows this.
- `make check` passes after the final edit, apart from main's known-red
  `TestNoReproLedger` tests (L6). Do not edit `BUGS-FIXED.md` or the ledger baseline to
  turn them green.

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

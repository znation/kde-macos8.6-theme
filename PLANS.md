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

### Ghostty terminal theme, part 1/2: ship and install a Platinum Ghostty theme file (planned 2026-11-21 by the director role)

**Goal.** The user asked on 2026-11-21 to "make the theme apply to ghostty".
Ghostty 1.3.1 is installed here (`/usr/bin/ghostty`, a GTK 4/libadwaita build).
It already draws inside our Aurorae frame, and its GTK chrome reads the
`gtk-4.0/gtk.css` that `tools/apply_gtk.py` writes. Its terminal surface
(font, colors) comes only from Ghostty's own config, so it ignores the theme
today. A Ghostty theme file is a normal Ghostty config file that can set any
option except `theme` and `config-file`. An absolute path selects it with
`theme = /abs/path` (see `ghostty +show-config --default --docs`, option
`theme`). This part ships that file and installs it. Part 2/2 ("Ghostty
terminal theme, part 2/2: select the installed theme in the user's Ghostty
config") writes the selection.

**Approach and files touched.**

1. New package directory `theme/ghostty/org.macos8.desktop/` holding one file,
   `Platinum`, with exactly these keys, one per line in `key = value` form:
   - `font-family = JetBrains Mono`, `font-style = Medium` and `font-size = 10`:
     the same face, weight and size as `FIXED_VALUE` in `tools/apply_theme.py`.
   - `background = #ffffff` and `foreground = #000000`: `[Colors:View]`
     `BackgroundNormal` and `ForegroundNormal` in
     `theme/color-schemes/MacOS8.colors`.
   - `selection-background = #ccccff` and `selection-foreground = #000000`:
     `[Colors:Selection]` `BackgroundNormal` and `ForegroundNormal` in the
     same file.
   - `cursor-color = #000000`, the View foreground.
   - Sixteen `palette = N=#rrggbb` lines that map the classic Platinum-era
     16-color system table to the ANSI slots. Use this mapping and do not
     re-decide it: 0 `#000000`, 1 `#dd0806`, 2 `#006411`, 3 `#562c05`,
     4 `#0000d4`, 5 `#4600a5`, 6 `#02abea`, 7 `#c0c0c0`, 8 `#808080`,
     9 `#ff6403`, 10 `#1fb714`, 11 `#fcf305`, 12 `#0000d4`, 13 `#f20884`,
     14 `#02abea`, 15 `#ffffff`. The table has no bright blue or bright cyan,
     so 12 and 14 repeat 4 and 6. Its tan `#90713a` and dark gray `#404040`
     go unused.
   Open the file with a `#` comment that names its sources and says no
   reference screenshot shows a terminal. Keep the file free of Apple
   trademarks (PRINCIPLES.md branding rule).
2. `Makefile`: add `GHOSTTY_ID := org.macos8.desktop`,
   `GHOSTTY_PACKAGE := theme/ghostty/$(GHOSTTY_ID)` and
   `GHOSTTY_INSTALL_DIR := $(DATA_HOME)/ghostty/themes`, next to the other
   family variables. Append `ghostty` to `INSTALL_FAMILIES`. Add a `_install`
   line `$(if $(filter ghostty,$(INSTALL_PACKAGES)),$(call install_package,$(GHOSTTY_ID),$(GHOSTTY_PACKAGE),$(GHOSTTY_INSTALL_DIR)))`.
   Add `$(call remove_installed_package,$(GHOSTTY_INSTALL_DIR),$(GHOSTTY_ID))`
   to `_uninstall`. Add `"$(GHOSTTY_INSTALL_DIR)"` to
   `require_uninstall_parents` and to whatever install-side symlink guard the
   other directory packages use. Have uninstall remove the
   `$(DATA_HOME)/ghostty/themes` and `$(DATA_HOME)/ghostty` directories only
   when they are empty (`rmdir` that ignores a non-empty directory), the same
   way it treats the `themes/` theme-id directories.
3. New `tests/test_ghostty_theme.py`. Parse `Platinum` with a small local
   `key = value` reader. Each color pin re-derives its expected value by
   reading `MacOS8.colors` with `configparser` and formatting the RGB triple.
   Each font pin parses `tools.apply_theme.FIXED_VALUE`: the family from the
   first field, the size from the second, and the style from the last field.
   Pin the palette against a table written into the test with its provenance
   comment. Also assert that every key is in the set above, that `theme` and
   `config-file` are absent, and that each `palette` index 0-15 appears
   exactly once.
4. Install tests in `tests/test_theme_install.py`, or beside them if that
   module is near its size cap: a staged `make install
   INSTALL_PACKAGES=ghostty` writes
   `<DATA_HOME>/ghostty/themes/org.macos8.desktop/Platinum` byte-identical to
   the source, and `make uninstall` removes it along with the then-empty
   `ghostty/themes` and `ghostty` directories. A foreign file under
   `ghostty/themes` survives uninstall, and so does its directory.
5. Docs: add `ghostty` to the family list in README.md's "Staging packages"
   paragraph (outside the brief markers) and to `docs/installing.md`'s
   per-family install list. Add a `docs/invariants.md` row for the theme file
   that names `tests/test_ghostty_theme.py`. Its provenance cell says no
   reference shows a terminal: the base colors come from `MacOS8.colors`, the
   font from the approved fixed-width face (QUESTIONS.md 2026-11-12), and the
   palette from the classic 16-color system table.

**Acceptance criteria.**

- `make install DESTDIR=$scratch XDG_DATA_HOME=/usr/share INSTALL_PACKAGES=ghostty`
  installs exactly `usr/share/ghostty/themes/org.macos8.desktop/Platinum`
  under the scratch root. A plain `make install` installs it along with the
  other families.
- When the `ghostty` binary is on `PATH`, a test runs `ghostty +show-config`
  (a CLI action that opens no window). It runs with a scratch
  `XDG_CONFIG_HOME` whose `ghostty/config.ghostty` holds only
  `theme = <absolute path of the shipped file>`, and `HOME` points at a
  scratch directory. The test asserts that the printed `background`,
  `foreground`, `font-family` and `palette = 1=` values equal the shipped
  file's. When the binary is absent, the test skips and names the binary.
- The test module fails if any shipped color or font value drifts from
  `MacOS8.colors` or `FIXED_VALUE`. Breaking one would catch it: swapping
  `selection-background` to the View background must fail a pin.
- `make check` passes apart from main's known-red tests.

### Ghostty terminal theme, part 2/2: select the installed theme in the user's Ghostty config (planned 2026-11-21 by the director role; "requires part 1/2 landed")

**Goal.** Make `make apply` point Ghostty at the theme file that part 1/2
("Ghostty terminal theme, part 1/2: ship and install a Platinum Ghostty theme
file") installs, and give the user a removal target, while leaving every
other line of the user's Ghostty config alone.

**Approach and files touched.**

1. New `tools/apply_ghostty.py`. Follow `tools/apply_cursor.py`'s CLI shape
   (`--optional`, `--remove`, the exit-2 diagnostic conventions). Resolve the
   config home as `tools/apply_gtk.py` does: an absolute `XDG_CONFIG_HOME`,
   else `$HOME/.config`. The target file is
   `<config home>/ghostty/config.ghostty`, the path Ghostty 1.3's
   `config-default-files` docs name. Apply writes or replaces one
   marker-delimited block at the end of that file, creating the file and the
   `ghostty/` directory when absent:
   `# >>> Platinum theme (managed by make apply-ghostty) >>>`, then
   `theme = <DATA_HOME>/ghostty/themes/org.macos8.desktop/Platinum`, then
   `# <<< Platinum theme <<<`. `DATA_HOME` is resolved the way
   `tools/apply_theme.py` resolves it. Every byte outside the block is
   preserved. A repeat apply leaves the file byte-identical. The write is
   atomic through `tools/atomic_write.py`. Refuse with exit 2 when the
   installed theme file is missing (name `make install` as the fix), when
   the target is a symlink, or when the block's markers are unbalanced.
   `--remove` deletes only the block. If the file then holds nothing at all,
   delete it; otherwise leave the rest byte-identical. `--optional` skips with
   one note and exit 0 when `ghostty` is not on `PATH`. Ghostty also loads
   the legacy `<config home>/ghostty/config`. Neither apply nor remove reads
   or writes that file, so a `theme =` line the user wrote in either file
   stays theirs. Ghostty's documented rule that explicit color keys in the
   user config override the theme is what keeps the user's own colors.
2. `Makefile`: add `$(PYTHON) tools/apply_ghostty.py --optional` to `apply`
   after `apply_cursor.py`. Add `apply-ghostty` (refuse_destdir,
   require_python_ready, `$(MAKE) --no-print-directory install
   INSTALL_PACKAGES=ghostty`, then the tool) and `remove-ghostty` (the tool
   with `--remove`), each with a comment in the style of the neighbouring
   targets.
3. New `tests/test_apply_ghostty.py`, using scratch config and data homes and
   a stub `ghostty` on a scratch `PATH`. Cover: the file is created when
   absent; foreign lines before and after the block are preserved byte for
   byte; a repeat apply is idempotent; remove restores the original bytes
   exactly; a file holding only the block is deleted; the missing theme file,
   symlinked target and unbalanced markers each exit 2 with a diagnostic;
   `--optional` without `ghostty` on `PATH` writes nothing and exits 0; the
   legacy `config` file is never opened for writing.
4. Docs: a Ghostty paragraph in `docs/installing.md` beside the Konsole one,
   covering what apply writes, the restart need (new windows read the theme;
   Ghostty's reload-config binding also reloads it), and the undo command.
   Add `make remove-ghostty` to README.md's "Removing the theme" table and
   a `docs/invariants.md` row naming `tests/test_apply_ghostty.py`.

Out of scope: restyling Ghostty's libadwaita tab bar beyond what the existing
GTK 4 sheet already does. Record any visible gap found during this work as
its own BUGS.md or PLANS.md entry.

**Acceptance criteria.**

- On a scratch config home, `make apply-ghostty` leaves `config.ghostty`
  ending in the three-line block with the absolute installed path, and a
  real `ghostty +show-config` (when installed, with scratch homes) reports
  the theme's `background = #ffffff`.
- `make remove-ghostty` after an apply on a pre-existing `config.ghostty`
  restores that file's original bytes.
- `make apply` on a machine without `ghostty` prints one skip note and still
  exits 0.
- `make check` passes apart from main's known-red tests.

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

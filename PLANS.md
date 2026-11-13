# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; merged-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; merged-series narration trimmed 2026-11-11 by the
steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for general, toolbar and smallest-readable fonts,
`ChicagoFLF` for menus and window titles, and the user-approved `JetBrains Mono Medium` for
KDE's fixed-width font (`[kdeglobals][General] fixed`, part 2/3 of the fixed-width series);
the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has merged inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widened the scope, and both are recorded below in their merged
state (their merged-series entry narration trimmed 2026-11-11 by the steward role;
the entries themselves are archived in PLANS-DONE.md).
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19): the GTK 3
and GTK 4/libadwaita Platinum stylesheets under `theme/gtk/` are installed — and selected —
only by the opt-in `install-gtk` and `apply-gtk` targets (`make install` copies no GTK
files), and the opt-in `install-firefox` target copies the Firefox `userChrome.css` and
`userContent.css` sheets into a profile and writes the preference that selects them.
**The UI font** is vendored (QUESTIONS.md, answered 2026-10-19): Lato is installed as the
Charcoal-style body face and selected by the global theme for general, toolbar and
smallest-readable fonts, and ChicagoFLF, a
public-domain Chicago-style face, is selected for menus and window titles (its licence was checked 2026-11-12 by the director role);
JetBrains Mono (the user-approved fixed-width face, QUESTIONS.md answered 2026-11-12)
is selected for KDE's fixed-width font.
GTK and Firefox applications keep their own chrome unless the opt-in GTK targets or the
Firefox install are used. Firefox chrome work since that series merged as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Split the 2584-line tests/test_gtk_theme_controls.py into per-surface suites (planned 2026-11-13 by the organize role; ordering clause — this entry queues behind the waiting "GTK 4 suite extraction: isolate paned, frame and corner-family declarations" entry, since both edit `docs/invariants.md`, and it is the GTK 3 analogue of the extraction series that entry continues: it may itself be decomposed into per-family entries the way that series was, each merging one family; at implementation re-grep every anchor this entry names)

**Needs review 2026-11-13 by feature: too large for one run.** Measured at
worktree base 149973fa4: tests/test_gtk_theme_controls.py is 2567 lines,
docs/invariants.md carries 53 `TestGtkThemeControls` mentions, and eleven
by-name sibling reference sites remain (test_gtk_theme.py,
test_gtk_theme_views.py, test_gtk_theme_osd.py,
test_no_gtk_introspection.py, test_gtk_child_probe_support.py,
support/validation_gaps/unclear_invariant.py) — roughly ten new modules plus
the invariants repointing and sibling doc updates, beyond a single run. As
the entry's own ordering clause suggests, the plan role should decompose it
into per-family entries as the GTK 4 extraction series was.

**Goal and cost.** `tests/test_gtk_theme_controls.py` is the repository's
largest file — 2584 lines at this plan's base commit, 67 test methods of
which 54 sit in the single `TestGtkThemeControls` class spanning every GTK 3
control surface (progress bar and meter, entry progress and state faces,
scale, switch, level bar, spinner, notebook tab faces, button arms,
spin-button steppers, linked border pairs, frame and scrolled viewport,
check/radio motion, menu-bar and toolbar titles), plus the trailing
`TestCheckGlyphs` (7 methods) and `TestArrowGlyphs` (6 methods) SVG asset
classes. Ten methods are rendered probes that run a GTK 3 child interpreter
through `_run_gtk_child` (the helper at line 504 at this plan's base
commit); nine share the module-level `_GTK3_SHEET_PROLOGUE` constant and one
(the mixed-check probe) carries a different prelude. `docs/invariants.md`
pins 67 `TestGtkThemeControls` mentions plus 4 `TestCheckGlyphs` and 4
`TestArrowGlyphs` mentions, and five sibling files reference the module by
name in doc comments — evidence that one file is a shared edit point for
every new GTK 3 control check, the same cost the merged GTK 4 extraction
series removes for `tests/test_gtk4_theme.py`. A 54-method grab-bag class
also hides which surface a method covers. The split is not a one-run move
(the invariants repointing alone spans ~75 mentions across ~30 rows), so it
is planned rather than started.

**Target structure.** Designed up front; no assertion, expected value, probe
pixel or child-program byte changes — only module placement, class
composition and imports move.

1. Per-surface suites `tests/test_gtk_theme_<surface>.py`, each
   `class TestGtkTheme<Surface>(GtkSheetRuleCases, unittest.TestCase)`
   binding `CSS_PATH` to the shipped `gtk-3.0/gtk.css` exactly as
   `GtkSheetRuleCases` documents (`tests/support/gtk_rule_cases.py:166`),
   partitioning `TestGtkThemeControls`'s 54 methods by the surface each
   asserts (the leading widget token of the test name: progress, meter,
   button, scale, entry, spinbutton, linked, switch, check, radio,
   notebook, levelbar, spinner, frame, viewport, menubar), grouped so no
   module exceeds roughly one sitting (~800 lines); a cross-surface method
   such as the shared focus-outline checks joins the suite of the surface
   it names. A method names exactly one module, moves unchanged, and keeps
   its method name.
2. Each of the ten rendered probes moves with its surface's declaration
   methods — each probe pins that surface's pixels, so co-locating avoids
   the second module per surface the GTK 4 series needed because its probe
   entries were independent plans appending to one file. Each child program
   moves byte-identical.
3. The shared `_GTK3_SHEET_PROLOGUE` moves once into
   `tests/support/gtk_child_probe.py` beside the `_GTK3_CHILD_HEAD` it
   assembles (the GTK 3 counterpart of the GTK 4 split's probe-prelude
   extraction); the mixed-check probe's differing prelude stays with its
   test. The module's `THEME_DIR`/`CSS`/asset-path constants move into the
   suites that use them, each suite binding its own `CSS_PATH` per the base
   class's contract — no new support fixture is needed, unlike the GTK 4
   split's `tests/support/gtk4_sheet.py`, because
   `GtkSheetRuleCases.setUpClass` already parses the sheet.
4. `TestCheckGlyphs` and `TestArrowGlyphs` move into
   `tests/test_gtk_theme_glyphs.py` with their `svg_assertions` and
   `support.svg_case` imports: they check shipped SVG assets, not the
   sheet.
5. `TestGtkThemeControls` and `tests/test_gtk_theme_controls.py` disappear
   — no half-moved state: every method is moved into a suite and the file is
   deleted at the end of the series.
6. Reference updates in the same change as each family's move: every
   `tests/test_gtk_theme_controls.py` anchor in `docs/invariants.md` is
   repointed at the module and class the named test merged into (67
   `TestGtkThemeControls` mentions, 4 `TestCheckGlyphs`, 4
   `TestArrowGlyphs` at this plan's base commit), and the by-name doc
   references in `tests/test_gtk_theme.py` (line 328 comment),
   `tests/test_gtk_theme_views.py` (three comment sites around lines
   830–852), `tests/test_gtk_theme_osd.py` (three comment sites around
   lines 415–711), `tests/test_no_gtk_introspection.py` (docstring line 4
   and line 96), `tests/test_gtk_child_probe_support.py` (docstring line 4)
   and `tests/support/validation_gaps/unclear_invariant.py` (line 385,
   naming `TestCheckGlyphs`) are repointed likewise. PLANS-DONE.md and
   BUGS-FIXED.md history is never rewritten.

**Files.** New: the per-surface `tests/test_gtk_theme_<surface>.py` suites
and `tests/test_gtk_theme_glyphs.py`. Deleted: `tests/test_gtk_theme_controls.py`.
Updated: `docs/invariants.md`, `tests/support/gtk_child_probe.py`,
`tests/test_gtk_theme.py`, `tests/test_gtk_theme_views.py`,
`tests/test_gtk_theme_osd.py`, `tests/test_no_gtk_introspection.py`,
`tests/test_gtk_child_probe_support.py`,
`tests/support/validation_gaps/unclear_invariant.py`. No production tool,
sheet or GTK 4 change; the GTK 3 sibling suites (`test_gtk_theme.py`,
`test_gtk_theme_views.py`, `test_gtk_theme_osd.py`) are outside this
entry's scope.

**Acceptance criteria.**

- The split changes no behavior: the full test-set union before and after
  is identical (same method names, same assertions, same skips; the GUI
  probes skip identically without `PLATINUM_RUN_GUI_TESTS=1` through the
  `run_gtk_child` exit-77 guard), and `make check` passes after the final
  edit.
- For each moved method, the AST of its function definition is identical to
  the original's at this plan's base commit (for example by comparing
  `ast.dump` output); this is a run-time check, not a new committed test.
- Unittest discovery lists each of the 67 methods exactly once, none of
  them under `test_gtk_theme_controls`, and every by-name reference site
  listed above reads the merged module and class.
- A grep over the repository (source, tests, docs) finds no remaining
  `test_gtk_theme_controls` reference outside PLANS-DONE.md and
  BUGS-FIXED.md: the file is gone and every invariants row names the module
  the test merged into, with the invariants checker inside `make check`
  resolving every new anchor.
- Each new suite stays under roughly one sitting (~800 lines), imports only
  names it uses (the unused-import scanner inside `make check` reports no
  finding), and the moved `_GTK3_SHEET_PROLOGUE` is defined exactly once
  with no duplicated prelude line remaining in any suite (a diff of the
  moved constant against the original shows only the moved lines).

### GTK 4 suite extraction: isolate the split-button container and band corner declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (87 `test_` methods at this plan's base commit,
before the waiting widget-corner extraction merges). Move the coupled
split-button pair — `test_split_button_container_corners` and
`test_splitbutton_band_corners` — into their own module, the way the
merged frame-corner, dropdown, popover, paned and selection extractions
moved theirs. The pair is coupled by construction: both methods build
the same ten-member band selector list, and
`test_split_button_container_corners`'s comment names
`test_splitbutton_band_corners` as the pin for the band spellings, so
they move together into one module and are never split across two
entries. This entry is independent of the waiting "GTK 4 suite
extraction: isolate assistant, pill, circular, video-OSD and
tab-thumbnail corner declarations" entry: that entry moves the five
corner methods immediately above this pair and states it never touches
the pair, while this one moves only the pair below the block that entry
deletes — but both delete contiguous runs in `tests/test_gtk4_theme.py`
and rewrite rows of `docs/invariants.md`, so whichever merges later
re-reads the file and the rows before writing and rewrites only its own
member mentions. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_splitbutton.py` with `class
  TestGtk4SplitButton(Gtk4SheetRuleCases, unittest.TestCase)`, a
  one-line module docstring on the existing extraction modules'
  pattern (`tests/test_gtk4_frame_corners.py`), and the `if __name__
  == "__main__":` guard. Move exactly two `TestGtk4Theme` methods,
  keeping each body, comment and docstring unchanged:
  `test_split_button_container_corners` and
  `test_splitbutton_band_corners`. At this plan's base commit they form
  one contiguous run between the `test_tab_thumbnail_corners` method
  above (which the waiting widget-corner entry moves) and the staying
  `test_navigation_sidebar_item_corners` below — the move touches one
  contiguous deletion in the source module. If the widget-corner entry
  merges first, re-grep and delete the same two methods wherever they
  then sit. Never import `tests/test_gtk4_theme.py` or inherit
  `TestGtk4Theme`. At implementation re-grep every anchor this entry
  names.
- The new module imports `Gtk4SheetRuleCases` from `support.gtk4_sheet`
  and nothing else beyond `unittest`. Every helper the two bodies call
  comes with the base classes: `assert_exact_rule_once`
  (`tests/support/gtk4_sheet.py:92`), `assert_rule` (a method of
  `GtkRuleCases`, `tests/support/gtk_rule_cases.py:155`),
  `assert_matches_frame` (`tests/support/gtk4_sheet.py:169`) and
  `assert_square_corner` (`tests/support/gtk4_sheet.py:183`), and
  `self.rules` and `self.selectors` come from the shared `setUpClass`.
  Neither body spells a palette or spec constant or uses `re`,
  `tempfile` or `mock`, so no import moves and none is pruned from
  `tests/test_gtk4_theme.py`.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_split_button_container_corners`
  and
  `…::TestGtk4Theme::test_splitbutton_band_corners` anchor to
  `tests/test_gtk4_splitbutton.py::TestGtk4SplitButton::…`,
  wherever it appears. `grep -o
  'TestGtk4Theme::test_split_button_container_corners\|TestGtk4Theme::test_splitbutton_band_corners'
  docs/invariants.md` finds exactly three member mentions across two
  rows at this plan's base commit: the `splitbutton` container row
  names `test_split_button_container_corners` once, and the
  toolbar-band row names both methods. Rewrite only those three member
  mentions and leave every other anchor in the two rows as it reads.
  The `splitbutton` selector spellings in `tests/support/gtk4_sheet.py`'s
  `BAR_FAMILY_FOCUS_SUFFIXES` name selectors, not tests, and stay as
  they read. Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the two moved methods exactly
  once, under `test_gtk4_splitbutton.TestGtk4SplitButton`, and
  none of them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_navigation_sidebar_item_corners`, `test_boxed_list_corners`
  and `test_infobar`.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n
  'TestGtk4Theme::test_split_button_container_corners\|TestGtk4Theme::test_splitbutton_band_corners'
  docs/invariants.md` prints nothing, each of the three touched member
  mentions reads `tests/test_gtk4_splitbutton.py::TestGtk4SplitButton`,
  every other anchor in the two touched rows stays as it reads, and the
  invariants checker inside `make check` resolves every new anchor.
- `git diff` leaves every import block in `tests/test_gtk4_theme.py`
  unchanged, the new module's import block names only `unittest` and
  `support.gtk4_sheet`, and the unused-import scanner inside
  `make check` reports no finding for either module.
- `tests/test_gtk4_theme.py` shrinks by at least 130 lines, and
  `tests/test_gtk4_splitbutton.py` stays under about 180 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_splitbutton.py` and `docs/invariants.md`.
  `make check` passes after the final edit.

### GTK 4 suite extraction: isolate the navigation-sidebar, boxed-list and swatch corner declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class. Move the contiguous run of four square-corner
restate methods — `test_navigation_sidebar_item_corners`,
`test_boxed_list_corners`, `test_separate_boxed_row_corners` and
`test_color_swatch_corners` — into their own module, the way the
merged frame-corner, dropdown, popover, paned, widget-corner and
split-button extractions moved theirs. All four pin the same
`border-radius: 0` restatement family — three over list-row surfaces
(navigation sidebar, boxed lists, separate boxed rows) and one over
the colour-button swatch, which also carries the 2026-11-04 container
restatement's `extra_declarations` — and each carries its focus-twin
comment naming the test that pins the focus spelling, so one module
houses the family and no pair of them is ever split across two
entries. This entry is independent of the waiting "GTK 4 suite
extraction: isolate the split-button container and band corner
declarations" entry: that entry moves the two split-button methods
immediately above this run and states it never touches these four,
while this one moves only the four below the block that entry
deletes — but both delete contiguous runs in
`tests/test_gtk4_theme.py` and rewrite rows of `docs/invariants.md`,
so whichever merges later re-reads the file and the rows before
writing and rewrites only its own member mentions. No stylesheet or
production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_row_corners.py` with `class
  TestGtk4RowCorners(Gtk4SheetRuleCases, unittest.TestCase)`, a
  one-line module docstring on the existing extraction modules'
  pattern (`tests/test_gtk4_widget_corners.py`), and the `if __name__
  == "__main__":` guard. Move exactly four `TestGtk4Theme` methods,
  keeping each body, comment and docstring unchanged:
  `test_navigation_sidebar_item_corners`, `test_boxed_list_corners`,
  `test_separate_boxed_row_corners` and `test_color_swatch_corners`.
  At this plan's base commit they form one contiguous run between the
  `test_splitbutton_band_corners` method above (which the waiting
  split-button entry moves) and the staying
  `test_columnview_and_listview_rows` below — the move touches one
  contiguous deletion in the source module. If the split-button entry
  merges first, re-grep and delete the same four methods wherever
  they then sit. Never import `tests/test_gtk4_theme.py` or inherit
  `TestGtk4Theme`. At implementation re-grep every anchor this entry
  names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet`, `BLACK` from `support.platinum_palette`, and
  nothing else beyond `unittest`. Every helper the four bodies call
  comes with the base classes: `assert_rule` (a method of
  `GtkRuleCases`, `tests/support/gtk_rule_cases.py`),
  `assert_square_corner` (`tests/support/gtk4_sheet.py`) and
  `assert_color_swatch_corners` (a method of `GtkRuleCases`,
  `tests/support/gtk_rule_cases.py`), and `self.rules` comes from the
  shared `setUpClass`. No body spells a palette or spec constant
  beyond `BLACK` or uses `re`, `tempfile` or `mock`; `BLACK` stays
  imported in `tests/test_gtk4_theme.py` (other methods use it), so
  no import is pruned from the source module.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_navigation_sidebar_item_corners`,
  `…::test_boxed_list_corners`, `…::test_separate_boxed_row_corners`
  and `…::test_color_swatch_corners` anchor to
  `tests/test_gtk4_row_corners.py::TestGtk4RowCorners::…`, wherever
  it appears. `grep -o
  'TestGtk4Theme::test_navigation_sidebar_item_corners\|TestGtk4Theme::test_boxed_list_corners\|TestGtk4Theme::test_separate_boxed_row_corners\|TestGtk4Theme::test_color_swatch_corners'
  docs/invariants.md` finds exactly six member mentions across six
  rows at this plan's base commit: the boxed-list row names
  `test_boxed_list_corners` once, the separate-row row names
  `test_separate_boxed_row_corners` once, the navigation-sidebar
  corner row and the places-sidebar row each name
  `test_navigation_sidebar_item_corners` once, and the swatch-corner
  row and the colour-button container row each name
  `test_color_swatch_corners` once. Rewrite only those six member
  mentions and leave every other anchor in those rows as it reads
  (the places-sidebar row also anchors `test_places_sidebar`, which
  stays). Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the four moved methods exactly
  once, under `test_gtk4_row_corners.TestGtk4RowCorners`, and none
  of them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_columnview_and_listview_rows`, `test_undershoot_bands_cleared`
  and `test_split_button_container_corners` until the split-button
  entry merges.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n
  'TestGtk4Theme::test_navigation_sidebar_item_corners\|TestGtk4Theme::test_boxed_list_corners\|TestGtk4Theme::test_separate_boxed_row_corners\|TestGtk4Theme::test_color_swatch_corners'
  docs/invariants.md` prints nothing, each of the six touched member
  mentions reads `tests/test_gtk4_row_corners.py::TestGtk4RowCorners`,
  every other anchor in the six touched rows stays as it reads, and
  the invariants checker inside `make check` resolves every new
  anchor.
- `git diff` leaves the import block of `tests/test_gtk4_theme.py`
  unchanged (no import becomes unused there), the new module's
  import block names only `unittest`, `support.gtk4_sheet` and
  `support.platinum_palette`, and the unused-import scanner inside
  `make check` reports no finding for either module.
- `tests/test_gtk4_theme.py` shrinks by at least 100 lines, and
  `tests/test_gtk4_row_corners.py` stays under about 150 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_row_corners.py` and `docs/invariants.md`.
  `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; landed-series narration trimmed 2026-11-11 by the
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
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widened the scope, and both are recorded below in their landed
state (their landed-series entry narration trimmed 2026-11-11 by the steward role;
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
Firefox install are used. Firefox chrome work since that series landed as single-surface
chrome plans (the downloads-panel and all-tabs rows, the sidebar frame, the menu-bar title
box, the tab faces and the app-menu rows). The `userContent.css` sheet styles surfaces
within six internal pages — about:downloads, about:config, about:preferences,
about:support, about:networking and about:telemetry — including preferences navigation and
controls, support tables and buttons, and telemetry navigation, tables and histograms; this
is surface coverage, not a claim of complete page theming. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### GTK 4 suite extraction: isolate paned, frame and corner-family declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (110 `test_` methods at this plan's base
commit). Move the eight structural-etch and square-corner
declaration checks (about 112 contiguous lines at this plan's base
commit) into their own module, the same way the landed OSD
(`tests/test_gtk4_osd.py`), scale, spinbutton, disabled, emoji,
entry, notebook, scrollbar, switch, progressbar, levelbar, view,
selected, button, row, treeview, tabbar, sidebar, checkbutton,
menu and expander parts moved theirs, and the way the waiting
"GTK 4 suite extraction: isolate dropdown declarations" and "GTK 4
suite extraction: isolate popover and toast declarations" entries
move theirs. This is independent of both waiting entries: none of
the three moves a method another names — this entry's block starts
immediately below `test_dropdown_arrow` (which the dropdown entry
moves as the last of its three separate deletions) and ends
immediately above `test_iconview_selected_arms`, which nothing
waiting touches, so all three entries edit
`tests/test_gtk4_theme.py` and `docs/invariants.md` and whichever
merges later re-reads those two files before writing. This entry
prunes no import: the moved bodies use no module-level import name
at all (they call only base-class helpers, `self.rules` and
unittest's `assertEqual`/`subTest`), so every import in
`tests/test_gtk4_theme.py` keeps its users and the unused-import
scanner (`tests/test_no_unused_imports.py`, which scans `tests/`)
needs no import block change in either module. No stylesheet or
production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_frame_corners.py` with
  `class TestGtk4FrameCorners(Gtk4SheetRuleCases,
  unittest.TestCase)` and a one-line module docstring on the landed
  extraction modules' pattern (`tests/test_gtk4_menu.py`), ending
  with the `if __name__ == "__main__":` guard like the landed
  modules. Move exactly eight `TestGtk4Theme` methods, keeping each
  method's body and docstring unchanged: `test_separator`,
  `test_paned_handle`, `test_paned_handle_stock_clearances`,
  `test_frame`, `test_shortcut_keycap_corners`,
  `test_card_corners`, `test_flowbox_item_corners` and
  `test_gridview_item_corners`. At this plan's base commit they
  form one contiguous block between the staying `test_dropdown_arrow`
  above and `test_iconview_selected_arms` below — the move touches
  one contiguous deletion in the source module. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. At
  implementation re-grep every anchor this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet` and nothing else beyond `unittest` (the
  landed `tests/test_gtk4_menu.py` import block shows the shape).
  Every helper the bodies call comes with the base classes:
  `assert_rule` (`tests/support/gtk_rule_cases.py:155`),
  `assert_separators` (`:415`), `assert_paned_handles` (`:424`)
  and `assert_frame` (`:434`) are methods of `Gtk4SheetRuleCases`'s
  `GtkRuleCases` base, `assert_exact_rule_once`
  (`tests/support/gtk4_sheet.py:92`), `assert_matches_frame`
  (`:169`) and `assert_square_corner` (`:183`) are methods of
  `Gtk4SheetRuleCases` itself, and `self.css`, `self.rules` and
  `self.selectors` come from the shared `setUpClass`. No moved body
  spells a palette name, a `support.gtk_theme_spec` name, a
  `support.gtk_css` name, or uses `re`, `tempfile` or `mock`, so no
  import moves and none is pruned.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_separator…`,
  `…::TestGtk4Theme::test_paned_handle…`,
  `…::TestGtk4Theme::test_shortcut_keycap_corners`,
  `…::TestGtk4Theme::test_card_corners`,
  `…::TestGtk4Theme::test_flowbox_item_corners` and
  `…::TestGtk4Theme::test_gridview_item_corners` anchor to
  `tests/test_gtk4_frame_corners.py::TestGtk4FrameCorners::…`,
  wherever it appears. `grep -o 'TestGtk4Theme::test_separator\b\|TestGtk4Theme::test_paned_handle\b\|TestGtk4Theme::test_paned_handle_stock_clearances\|TestGtk4Theme::test_shortcut_keycap_corners\|TestGtk4Theme::test_card_corners\|TestGtk4Theme::test_flowbox_item_corners\|TestGtk4Theme::test_gridview_item_corners'
  docs/invariants.md` finds exactly ten member mentions across nine
  rows at this plan's base commit: `test_card_corners`,
  `test_flowbox_item_corners` and `test_gridview_item_corners`
  twice each (the card row and the extended card-focus row; the
  focus-outlines row names both flowbox and gridview), and
  `test_separator`, `test_paned_handle`,
  `test_paned_handle_stock_clearances` and
  `test_shortcut_keycap_corners` once each. `test_frame` has no
  per-method invariants anchor (its work is named only in prose
  such as "matching `frame > border` and `.frame`", which stays as
  it reads, and inside the class-level `TestGtk4Theme` row). The
  same rows also carry the GTK 3 twins
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_separator`,
  `…::TestGtkThemeViews::test_paned_handle` and
  `…::test_paned_handle_background_images`/`…::test_paned_handle_direction_margins`
  — rewrite only the `TestGtk4Theme`-qualified mentions and leave
  every GTK 3 anchor as it reads; likewise the staying
  `TestGtk4Theme::test_separator_label_foreground` anchor is a
  different method and stays. Do not rewrite history in
  PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the eight moved methods exactly
  once, under `test_gtk4_frame_corners.TestGtk4FrameCorners`, and
  none of them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_separator_label_foreground`, `test_iconview_selected_arms`
  and `test_dropdown_arrow` (or, if the dropdown entry landed
  first, `test_iconview_selected_arms` alone of these).
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_separator\b\|TestGtk4Theme::test_paned_handle\b\|TestGtk4Theme::test_paned_handle_stock_clearances\|TestGtk4Theme::test_shortcut_keycap_corners\|TestGtk4Theme::test_card_corners\|TestGtk4Theme::test_flowbox_item_corners\|TestGtk4Theme::test_gridview_item_corners'
  docs/invariants.md` prints nothing, each of the nine touched rows
  names its moved methods under
  `tests/test_gtk4_frame_corners.py::TestGtk4FrameCorners`, the
  GTK 3 anchors in those rows and the class-level
  `tests/test_gtk4_theme.py::TestGtk4Theme` anchor row stay, and
  the invariants checker inside `make check` resolves every new
  anchor.
- `git diff` leaves every import block in
  `tests/test_gtk4_theme.py` unchanged, the new module's import
  block names only `unittest` and `support.gtk4_sheet`, and the
  unused-import scanner inside `make check` reports no finding for
  either module.
- `tests/test_gtk4_theme.py` shrinks by at least 110 lines, and
  `tests/test_gtk4_frame_corners.py` stays under about 150 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_frame_corners.py` and `docs/invariants.md`.
  `make check` passes after the final edit.

### GTK 4 suite extraction: isolate selection, focus-outline and cursor-handle declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (100 `test_` methods at this plan's base
commit). Move the five selection-restatement, focus-outline and
cursor-handle declaration checks (about 150 contiguous lines at this
plan's base commit) into their own module, the same way the landed OSD
(`tests/test_gtk4_osd.py`), scale, spinbutton, disabled, emoji, entry,
notebook, scrollbar, switch, progressbar, levelbar, view, selected,
button, row, treeview, tabbar, sidebar, checkbutton, menu, expander,
linked, dropdown and popover parts moved theirs, and the way the
waiting "GTK 4 suite extraction: isolate paned, frame and
corner-family declarations" entry moves its eight. The cursor-handle
method rides in this module because its body is source-order-tied to
the focus groups: `test_cursor_handle_corners` asserts its selector's
parsed index against `label:focus:focus-visible` and
`.card:focus:focus-visible`, so the checks belong together. This is
independent of the paned entry: neither moves a method the other
names — this entry's block starts immediately below
`test_gridview_item_corners` (the last method the paned entry moves)
and ends immediately above `test_assistant_step_label_corners`, which
nothing waiting touches — but both entries delete contiguous runs in
`tests/test_gtk4_theme.py` and rewrite rows of `docs/invariants.md`,
and the shared rows 484-area and 497-area each name methods of both
entries (the view-children focus-outline row names
`test_flowbox_item_corners` and `test_gridview_item_corners` beside
this entry's `test_iconview_selected_arms`; the card-focus row names
`test_card_corners` beside this entry's
`test_card_focus_outline_color`), so whichever merges later re-reads
both files before writing and rewrites only its own member mentions
there. This entry prunes no import: the moved bodies use `BLACK`,
`SELECTION` and `SELECTION_CHECK_STATES`, and all three keep users in
`tests/test_gtk4_theme.py` after the move (`BLACK` in dozens of
staying bodies, `SELECTION` in the row-selection and view bodies,
`SELECTION_CHECK_STATES` in `test_tile_check_faces`), so the
unused-import scanner (`tests/test_no_unused_imports.py`, which scans
`tests/`) needs no import block change in the source module. No
stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_selection_focus.py` with
  `class TestGtk4SelectionFocus(Gtk4SheetRuleCases,
  unittest.TestCase)` and a one-line module docstring on the landed
  extraction modules' pattern (`tests/test_gtk4_menu.py`), ending
  with the `if __name__ == "__main__":` guard like the landed
  modules. Move exactly five `TestGtk4Theme` methods, keeping each
  method's body and docstring unchanged: `test_iconview_selected_arms`,
  `test_residual_focus_outline_color`,
  `test_card_focus_outline_color`, `test_cursor_handle_corners` and
  `test_generic_view_selected_arms`. At this plan's base commit they
  form one contiguous block between the staying
  `test_gridview_item_corners` above and
  `test_assistant_step_label_corners` below — the move touches one
  contiguous deletion in the source module. If the paned entry merges
  first, re-grep and delete the same five methods wherever they then
  sit. Never import `tests/test_gtk4_theme.py` or inherit
  `TestGtk4Theme`. At implementation re-grep every anchor this entry
  names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet`, `BLACK` and `SELECTION` from
  `support.platinum_palette`, `SELECTION_CHECK_STATES` from
  `support.gtk_theme_spec`, and nothing else beyond `unittest` (the
  landed `tests/test_gtk4_menu.py` import block shows the shape).
  Every helper the bodies call comes with the base classes:
  `assert_rule` (`tests/support/gtk_rule_cases.py:155`) and
  `assert_disabled_text` (`:449`) are methods of
  `Gtk4SheetRuleCases`'s `GtkRuleCases` base;
  `assert_scale_anchored_focus_outline`
  (`tests/support/gtk4_sheet.py:144`), `assert_matches_frame`
  (`:169`) and `assert_square_corner` (`:183`) are methods of
  `Gtk4SheetRuleCases` itself; and `self.css`, `self.rules` and
  `self.selectors` come from the shared `setUpClass`. No moved body
  spells a palette name, a `support.gtk_theme_spec` name beyond
  `SELECTION_CHECK_STATES`, a `support.gtk_css` name, or uses `re`,
  `tempfile` or `mock`, so no further import moves and none is
  pruned.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_iconview_selected_arms`,
  `…::test_residual_focus_outline_color`,
  `…::test_card_focus_outline_color`,
  `…::test_cursor_handle_corners` and
  `…::test_generic_view_selected_arms` anchor to
  `tests/test_gtk4_selection_focus.py::TestGtk4SelectionFocus::…`,
  wherever it appears. `grep -o
  'TestGtk4Theme::test_iconview_selected_arms\|TestGtk4Theme::test_residual_focus_outline_color\|TestGtk4Theme::test_card_focus_outline_color\|TestGtk4Theme::test_cursor_handle_corners\|TestGtk4Theme::test_generic_view_selected_arms'
  docs/invariants.md` finds exactly seven member mentions across
  seven rows at this plan's base commit:
  `test_iconview_selected_arms` twice (the view-children
  focus-outline row and the iconview-selection row),
  `test_generic_view_selected_arms` twice (the generic-view
  selection row and the disabled-selected row), and
  `test_residual_focus_outline_color`,
  `test_card_focus_outline_color` and `test_cursor_handle_corners`
  once each. The iconview-selection row also carries the GTK 3 twin
  `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_iconview_selected_arms`
  — rewrite only the `TestGtk4Theme`-qualified mentions and leave
  every GTK 3 anchor as it reads. Do not rewrite history in
  PLANS-DONE.md or BUGS-FIXED.md.
- In `tests/support/gtk_theme_spec.py`, update the comment above
  `SELECTION_CHECK_STATES` (the "Exactly four tests read it" block,
  `grep -n 'test_iconview_selected_arms in'`): it names
  `test_iconview_selected_arms in tests/test_gtk4_theme.py` — point
  that one mention at `tests/test_gtk4_selection_focus.py`; the
  staying `test_tile_check_faces` and the two `test_gtk_theme_views`
  readers keep their mentions as they read.

**Acceptance criteria.**
- Unittest discovery lists each of the five moved methods exactly
  once, under `test_gtk4_selection_focus.TestGtk4SelectionFocus`, and
  none of them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_gridview_item_corners` (or, if the paned entry landed first,
  `test_assistant_step_label_corners` and `test_tile_check_faces`
  among the staying).
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n
  'TestGtk4Theme::test_iconview_selected_arms\|TestGtk4Theme::test_residual_focus_outline_color\|TestGtk4Theme::test_card_focus_outline_color\|TestGtk4Theme::test_cursor_handle_corners\|TestGtk4Theme::test_generic_view_selected_arms'
  docs/invariants.md` prints nothing, each of the seven touched rows
  names its moved method under
  `tests/test_gtk4_selection_focus.py::TestGtk4SelectionFocus`, the
  GTK 3 anchors in those rows and the class-level
  `tests/test_gtk4_theme.py::TestGtk4Theme` anchor row stay, and
  the invariants checker inside `make check` resolves every new
  anchor.
- `git diff` leaves every import block in
  `tests/test_gtk4_theme.py` unchanged, the new module's import
  block names only `unittest`, `support.gtk4_sheet`,
  `support.platinum_palette` and `support.gtk_theme_spec`, and the
  unused-import scanner inside `make check` reports no finding for
  either module.
- `tests/test_gtk4_theme.py` shrinks by at least 148 lines, and
  `tests/test_gtk4_selection_focus.py` stays under about 190 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_selection_focus.py`,
  `tests/support/gtk_theme_spec.py` and `docs/invariants.md`.
  `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

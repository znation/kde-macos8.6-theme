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

### GTK 4 suite extraction: isolate expander declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class. Move the four expander declaration checks
(about 68 lines at this plan's base commit) into their own module,
the same way the landed OSD (`tests/test_gtk4_osd.py`), scale,
spinbutton, disabled, emoji, entry, notebook, scrollbar, switch,
progressbar, levelbar, view, selected, button, row, treeview,
tabbar and sidebar parts moved theirs, and the way the waiting
"GTK 4 suite extraction: isolate linked declarations" entry moves
its three (a held merge-pin change moves the landed menu entry out
of `## Planned` and the landed checkbutton entry under `## Done`,
so this entry is written against main without them). This is
independent of the waiting linked entry: neither moves a method the
other names, and this entry prunes no import at all — the moved
bodies call no `support.gtk_theme_spec` or palette name, and
`grep -n EXPANDER tests/test_gtk4_theme.py` prints nothing at this
plan's base commit (`EXPANDER_COLLAPSED`/`EXPANDER_EXPANDED` live
only in `support.gtk_theme_spec` and the base method
`assert_expander_arrows` at `tests/support/gtk_rule_cases.py:593`,
which the base class carries) — while the linked entry also prunes
nothing. Both entries edit `tests/test_gtk4_theme.py` and
`docs/invariants.md`, so whichever merges later re-reads those two
files before writing. The GTK 3 twins
(`tests/test_gtk_theme.py::TestGtkTheme::test_expander_arrows` and
`…::test_rtl_collapsed_expander_arrows`) stay where they are. No
stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_expander.py` with
  `class TestGtk4Expander(Gtk4SheetRuleCases, unittest.TestCase)`
  and a one-line module docstring on the landed extraction modules'
  pattern (`tests/test_gtk4_view.py`). Move exactly four
  `TestGtk4Theme` methods, keeping each method's body and docstring
  unchanged: `test_expander_arrows`,
  `test_rtl_collapsed_expander_arrows` (the RTL twin the
  disclosure-arrow row anchors, though its name starts
  `test_rtl_collapsed_`), `test_expander_row_arrow_transition_motion`
  and `test_expander_widget_title_corners`. At this plan's base
  commit they sit in three spots: the first two contiguous between
  the staying `test_csd_window_shell_state_cascade` above and
  `test_submenu_arrow` below, the third alone between the staying
  `test_checkbutton_corners` above (which the merge-pin change
  moves out of this module, so at implementation the staying
  neighbor above is whatever then precedes the block) and
  `test_server_list_button_rotation_motion` below, and the fourth
  alone between the staying `test_selection_surface_corners` above
  and `test_sheet_widget_corners` below — so the move touches three
  separate deletions in the source module. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. At
  implementation re-grep every anchor this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet` and nothing else beyond `unittest`. Every
  helper the bodies call comes with the base class:
  `assert_expander_arrows`, `assert_rule` and `assert_square_corner`
  are methods of `Gtk4SheetRuleCases` and its bases
  (`tests/support/gtk4_sheet.py`, `tests/support/gtk_rule_cases.py`),
  and `self.css`, `self.rules` and `self.selectors` come from the
  shared `setUpClass`. No moved body spells a
  `support.gtk_theme_spec`, `support.platinum_palette` or
  `support.gtk_css` name, and none uses `re`, `tempfile` or `mock`,
  so no import moves and no import is pruned in either module.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_expander…` and
  `…::TestGtk4Theme::test_rtl_collapsed_expander_arrows` anchor to
  `tests/test_gtk4_expander.py::TestGtk4Expander::…`, wherever it
  appears. `grep -o 'TestGtk4Theme::test_expander[a-z_]*\|TestGtk4Theme::test_rtl_collapsed_expander_arrows'
  docs/invariants.md` finds exactly four member mentions at this
  plan's base commit across three rows: the two disclosure-arrow
  methods in the both-sheets arrows row (where they stand beside
  their staying GTK 3 twins and the staying
  `tests/test_gtk_theme_controls.py::TestArrowGlyphs` anchor),
  `test_expander_widget_title_corners` alone in the title-corners
  row, and `test_expander_row_arrow_transition_motion` alone in the
  expander-row-arrow motion row; no provenance prose in
  `docs/invariants.md` names any of the four. Rewrite only the moved
  anchors in place and leave every staying anchor as it reads. Do
  not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the four moved methods exactly
  once, under `test_gtk4_expander.TestGtk4Expander`, and none of
  them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_submenu_arrow`, `test_server_list_button_rotation_motion`
  and `test_sheet_widget_corners`.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_expander\|TestGtk4Theme::test_rtl_collapsed'
  docs/invariants.md` prints nothing, each of the three touched
  rows still names its staying anchors under their original modules
  (the GTK 3 twins and `TestArrowGlyphs` unchanged), and the
  invariants checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 60 lines, and
  `tests/test_gtk4_expander.py` stays under about 90 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_expander.py` and `docs/invariants.md`. `make
  check` passes after the final edit.

### GTK 4 suite extraction: isolate dropdown declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (107 `test_` methods at this plan's base
commit). Move the three dropdown/combobox declaration checks (about
85 lines at this plan's base commit) into their own module, the same
way the landed OSD (`tests/test_gtk4_osd.py`), scale, spinbutton,
disabled, emoji, entry, notebook, scrollbar, switch, progressbar,
levelbar, view, selected, button, row, treeview, tabbar, sidebar,
checkbutton and menu parts moved theirs, and the way the waiting
"GTK 4 suite extraction: isolate expander declarations" entry moves
its four (the change that landed the linked part removed that
entry from `## Planned`, so this entry is written against main
without it). This is independent of the waiting
expander entry: neither moves a method the other names. Unlike the
expander and linked entries, this one does prune an import: after
the move, `test_gtk4_theme.py`'s `test_dropdown_arrow` is gone, and
at this plan's base commit `COMBO_ARROW` has no other direct use in
that module (`grep -n 'COMBO_ARROW' tests/test_gtk4_theme.py`
finds only its import line and the moved method's one call, while
`ETCH_DARK`, `WHITE` and `ROW_SELECTED` keep many staying users —
lines 853/887, 854/888 and 1060 among others), so the unused-import
scanner (`tests/test_no_unused_imports.py`, which scans `tests/`)
requires pruning `COMBO_ARROW` from the `support.gtk_theme_spec`
import block. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_dropdown.py` with
  `class TestGtk4Dropdown(Gtk4SheetRuleCases, unittest.TestCase)` and
  a one-line module docstring on the landed extraction modules'
  pattern (`tests/test_gtk4_checkbutton.py`), ending with the
  `if __name__ == "__main__":` guard like the landed modules. Move
  the three `TestGtk4Theme` methods `test_dropdown_searchbar_rim`,
  `test_dropdown_list_rows` and `test_dropdown_arrow`, keeping each
  method's body and docstring unchanged. At this plan's base commit
  they sit between the staying neighbors `test_status_bar` (above
  `test_dropdown_searchbar_rim`), `test_list_row_press_and_popup_faces`
  (between searchbar and list rows), `test_list_row_focus_outlines`
  (below `test_dropdown_list_rows`) and `test_toast`-style
  `assert_toast_matches_popover` users plus `test_separator` (below
  `test_dropdown_arrow`) — the move touches three separate deletions
  in the source module. Never import `tests/test_gtk4_theme.py` or
  inherit `TestGtk4Theme`. At implementation re-grep every anchor
  this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet`; `COMBO_ARROW`, `ETCH_DARK`, `ROW_SELECTED`
  and `WHITE` from `support.gtk_theme_spec`; and nothing else beyond
  `unittest`. Every assertion helper the bodies call comes with the
  base classes: `assert_rule` and `assert_exact_rule_once` are
  methods of `Gtk4SheetRuleCases`' bases
  (`tests/support/gtk_rule_cases.py:155` and
  `tests/support/gtk4_sheet.py:92`), and `self.css`, `self.rules`
  and `self.selectors` come from the shared `setUpClass`. No moved
  body spells a palette name, a `support.gtk_css` name, or uses
  `re`, `tempfile` or `mock`, so nothing else moves — `ETCH_DARK`,
  `WHITE` and `ROW_SELECTED` keep their places in
  `tests/test_gtk4_theme.py`'s import blocks. In the same change,
  prune `COMBO_ARROW` from `tests/test_gtk4_theme.py`'s
  `support.gtk_theme_spec` import block: no staying method reads it.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_dropdown…`
  anchor to `tests/test_gtk4_dropdown.py::TestGtk4Dropdown::…`.
  `grep -o 'TestGtk4Theme::test_dropdown[a-z_]*' docs/invariants.md`
  finds exactly two member mentions at this plan's base commit —
  `test_dropdown_list_rows` and `test_dropdown_searchbar_rim`, one
  each in the anchor column of their GTK 4 dropdown rows — and
  `test_dropdown_arrow` has no per-method invariants anchor (its
  work is named only inside the class-level `TestGtk4Theme` row and
  other entries' prose, which stay as they read). Rewrite only the
  two moved anchors in place; the GTK 3 rows and every other anchor
  stay as they read. Do not rewrite history in PLANS-DONE.md or
  BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the three moved methods exactly
  once, under `test_gtk4_dropdown.TestGtk4Dropdown`, and none of
  them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_list_row_focus_outlines`, `test_list_row_press_and_popup_faces`
  and `test_path_bar_tabs`.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_dropdown' docs/invariants.md`
  prints nothing, both dropdown rows name their moved methods under
  `tests/test_gtk4_dropdown.py::TestGtk4Dropdown`, the class-level
  `tests/test_gtk4_theme.py::TestGtk4Theme` anchor row stays, and
  the invariants checker inside `make check` resolves every new
  anchor.
- `grep -n 'COMBO_ARROW' tests/test_gtk4_theme.py` prints nothing,
  `grep -n 'COMBO_ARROW' tests/test_gtk4_dropdown.py` finds exactly
  the import and the moved `test_dropdown_arrow` body, and the
  unused-import scanner inside `make check` reports no finding for
  either module.
- `tests/test_gtk4_theme.py` shrinks by at least 80 lines, and
  `tests/test_gtk4_dropdown.py` stays under about 110 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_dropdown.py` and `docs/invariants.md`. `make
  check` passes after the final edit.

### GTK 4 suite extraction: isolate popover and toast declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (110 `test_` methods at this plan's base
commit). Move the three popover/toast declaration checks (about 124
contiguous lines at this plan's base commit) into their own module,
the same way the landed OSD (`tests/test_gtk4_osd.py`), scale,
spinbutton, disabled, emoji, entry, notebook, scrollbar, switch,
progressbar, levelbar, view, selected, button, row, treeview,
tabbar, sidebar, checkbutton and menu parts moved theirs, and the
way the waiting "GTK 4 suite extraction: isolate dropdown
declarations" entry moves its three (a held merge-pin change moves
the landed expander entry out of `## Planned`, so this entry is
written against main without it). This is independent of the
waiting dropdown entry: neither moves a method the other names —
this entry's block ends immediately above `test_dropdown_arrow`,
which the dropdown entry moves, so both entries edit
`tests/test_gtk4_theme.py` and `docs/invariants.md` and whichever
merges later re-reads those two files before writing. Unlike the
dropdown entry, this one prunes no import: every palette and spec
name the moved bodies spell (`FACE`, `BLACK`, `SELECTION`,
`DISABLED_TEXT`, `ETCH_DARK`) keeps many staying users in
`tests/test_gtk4_theme.py` (for example `FACE` in
`test_banner_surface` and `test_toolbar_and_menubar`, `BLACK` in
`test_links` and `test_places_sidebar`, `SELECTION` in
`test_dropdown_list_rows` and `test_iconview_drop_border`,
`DISABLED_TEXT` in `test_header_subtitle_foreground` and
`test_inline_link_interaction_colours`, `ETCH_DARK` in
`test_label_error_colour_class` and `test_search_bar`), and the
unused-import scanner (`tests/test_no_unused_imports.py`, which
scans `tests/`) keeps requiring all five in the source module. No
stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_popover.py` with
  `class TestGtk4Popover(Gtk4SheetRuleCases, unittest.TestCase)`
  and a one-line module docstring on the landed extraction
  modules' pattern (`tests/test_gtk4_menu.py`), ending with the
  `if __name__ == "__main__":` guard like the landed modules. Move
  exactly three `TestGtk4Theme` methods, keeping each method's
  body and docstring unchanged: `test_popover`,
  `test_popover_menu_accelerator_foreground` and
  `test_toast_surface`. At this plan's base commit they form one
  contiguous block between the staying `test_message_dialog_action_area`
  above and `test_dropdown_arrow` below (which the waiting dropdown
  entry moves, so at implementation the staying neighbor below is
  whatever then follows the block) — the move touches one
  contiguous deletion in the source module. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. At
  implementation re-grep every anchor this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet`; `DISABLED_TEXT` and `ETCH_DARK` from
  `support.gtk_theme_spec`; `BLACK`, `FACE` and `SELECTION` from
  `support.platinum_palette`; and nothing else beyond `unittest`
  (the landed `tests/test_gtk4_menu.py` import block shows the
  split between the two name sources). Every helper the bodies
  call comes with the base classes: `assert_rule` and
  `assert_exact_rule_once` are methods of `Gtk4SheetRuleCases`'
  bases (`tests/support/gtk_rule_cases.py:155` and
  `tests/support/gtk4_sheet.py:92`), `assert_disabled_text` is a
  method of `tests/support/gtk_rule_cases.py:449`,
  `_assert_toast_matches_popover` is a method of
  `tests/support/gtk4_sheet.py:275`, and `self.css`, `self.rules`
  and `self.selectors` come from the shared `setUpClass`. No moved
  body spells a `support.gtk_css` name or uses `re`, `tempfile` or
  `mock`, so no other import moves.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_popover…` and
  `…::TestGtk4Theme::test_toast_surface` anchor to
  `tests/test_gtk4_popover.py::TestGtk4Popover::…`, wherever it
  appears. `grep -o 'TestGtk4Theme::test_popover[a-z_]*\|TestGtk4Theme::test_toast[a-z_]*'
  docs/invariants.md` finds exactly four member mentions at this
  plan's base commit across four rows: `test_popover` in the
  modelbutton-corners row and again (as `test_popover` (extended))
  in the modelbutton-colour-states row,
  `test_popover_menu_accelerator_foreground` alone in the
  accelerator row, and `test_toast_surface` alone in the toast
  row. Prose back-references that spell the bare name
  `` `test_popover` `` (the "pinned by the same `test_popover`"
  phrases in the corners and colour-states rows) stay as they
  read: the method keeps its name in the new module, so the
  references stay true. Rewrite only the module-qualified anchors
  in place and leave every staying anchor as it reads. Do not
  rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the three moved methods exactly
  once, under `test_gtk4_popover.TestGtk4Popover`, and none of
  them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_message_dialog_action_area`, `test_dropdown_arrow` and
  `test_separator` (or, if the dropdown entry landed first,
  `test_message_dialog_action_area` and `test_separator`).
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_popover\|TestGtk4Theme::test_toast'
  docs/invariants.md` prints nothing, each of the four touched
  rows names its moved method under
  `tests/test_gtk4_popover.py::TestGtk4Popover`, the
  class-level `tests/test_gtk4_theme.py::TestGtk4Theme` anchor row
  stays, and the invariants checker inside `make check` resolves
  every new anchor.
- `grep -n 'COMBO_ARROW\|ETCH_DARK\|DISABLED_TEXT\|\bFACE\b\|\bBLACK\b\|\bSELECTION\b'
  tests/test_gtk4_theme.py` still finds each name's staying import
  and users, and the unused-import scanner inside `make check`
  reports no finding for either module.
- `tests/test_gtk4_theme.py` shrinks by at least 120 lines, and
  `tests/test_gtk4_popover.py` stays under about 160 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_popover.py` and `docs/invariants.md`. `make
  check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

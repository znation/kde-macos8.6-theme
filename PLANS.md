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

### GTK 4 suite extraction: isolate menu declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (127 `test_` methods at this plan's base
commit). Move the five `test_menu`-prefixed declaration checks
(about 60 lines at this plan's base commit) into their own module,
the same way the landed OSD (`tests/test_gtk4_osd.py`), scale,
spinbutton, disabled, emoji, entry, notebook, scrollbar, switch,
progressbar, levelbar, view, selected, button, row and treeview
parts moved theirs, and the waiting "GTK 4 suite extraction:
isolate tabbar declarations" and "… isolate sidebar declarations"
entries move their own. This is independent of those waiting
entries (neither moves a `test_menu`-prefixed method, and the only
shared files are `tests/test_gtk4_theme.py` and `docs/invariants.md`,
which all three edit — whichever merges later re-reads those two
files before writing). Methods that only contain `menu` mid-name
(`test_submenu_arrow`, `test_popover_menu_accelerator_foreground`,
`test_toolbar_and_menubar`,
`test_color_button_and_menubutton_container_corners`) stay where
they are. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_menu.py` with
  `class TestGtk4Menu(Gtk4SheetRuleCases, unittest.TestCase)` and a
  one-line module docstring on the landed extraction modules'
  pattern (`tests/test_gtk4_selected.py`). Move every
  `TestGtk4Theme` method whose name starts with `test_menu` (the
  five are `test_menubutton_arrows`,
  `test_menu_check_and_radio_are_boxless`, `test_menu_separator`,
  `test_menubar_titles` and `test_menu_selection_corners`), keeping
  each method's body and docstring unchanged. At this plan's base
  commit they sit in two contiguous blocks, each between staying
  neighbors: `test_menubutton_arrows` through `test_menu_separator`
  between `test_dropdown_arrow` (stays) and `test_separator`
  (stays), and `test_menubar_titles` through
  `test_menu_selection_corners` between `test_toolbar_and_menubar`
  (stays) and `test_linked_members_strip_their_trailing_border`
  (stays) — so the move touches two separate deletions in the
  source module. Never import `tests/test_gtk4_theme.py` or
  inherit `TestGtk4Theme`. At implementation re-grep every anchor
  this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet`, `MENUBUTTON_ARROWS` and `MENU_CHECK` from
  `support.gtk_theme_spec`, and `SELECTION` from
  `support.platinum_palette` (the moved bodies use each:
  `MENUBUTTON_ARROWS` in `test_menubutton_arrows`, `MENU_CHECK` in
  `test_menu_check_and_radio_are_boxless`, `SELECTION` in
  `test_menubar_titles`; only base helpers and
  `self.rules`/`self.selectors` elsewhere). Every assertion helper
  the bodies call comes with the base classes:
  `assert_rule`, `assert_menu_separator` and `assert_menubar_titles`
  are methods of `Gtk4SheetRuleCases` and its bases
  (`tests/support/gtk4_sheet.py`, `tests/support/gtk_rule_cases.py`),
  `assert_square_corner` is a `Gtk4SheetRuleCases` method, and
  `self.css`, `self.rules` and `self.selectors` come from the
  shared `setUpClass`; none of them is imported as a name anywhere,
  so no helper import moves.
- Grep-checked at this plan's base commit, the source module's only
  other `MENUBUTTON_ARROWS` and `MENU_CHECK` references are their
  two import lines, so after the move `tests/test_gtk4_theme.py`
  no longer uses either name: prune both from the `from
  support.gtk_theme_spec import (...)` block (`COMBO_ARROW` stays —
  `test_dropdown_arrow` still uses it — and every other name in the
  block keeps its place). `SELECTION` stays imported: staying
  methods such as `test_row_selected_background_arms` still use it.
  The moved bodies call no other support name (no `HEX`,
  `parse_css`, `strip_comments`, `gtk_css`, palette constant other
  than `SELECTION`, spec constant other than the two above, mock,
  tempfile or `re` use).
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_menu…` anchor to
  `tests/test_gtk4_menu.py::TestGtk4Menu::test_menu…`, wherever it
  appears — in the anchor column and in provenance prose.
  `grep -o 'TestGtk4Theme::test_menu[a-z_]*' docs/invariants.md`
  finds exactly three member mentions at this plan's base commit,
  one per touched invariant row: `test_menubar_titles` beside the
  staying `test_toolbar_and_menubar` in the menu-bar padding row,
  `test_menubutton_arrows` alone in the menu-button arrows row, and
  `test_menu_selection_corners` alone in the menu-selection
  square-corners row. The `test_menu_check_and_radio_are_boxless`
  and `test_menu_separator` invariants mentions name only the GTK 3
  module `tests/test_gtk_theme_views.py` and stay as they read.
  Rewrite only the moved anchors in place and leave every staying
  anchor as it reads. Do not rewrite history in PLANS-DONE.md or
  BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the five moved methods exactly
  once, under `test_gtk4_menu.TestGtk4Menu`, and none of them under
  `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme`
  method is still listed there, including `test_submenu_arrow`,
  `test_popover_menu_accelerator_foreground`,
  `test_toolbar_and_menubar` and
  `test_color_button_and_menubutton_container_corners`.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_menu' docs/invariants.md` prints
  nothing, each of the three touched rows still names its staying
  anchors under their original modules, and the invariants checker
  inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 55 lines, and
  `tests/test_gtk4_menu.py` stays under about 130 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_menu.py` and `docs/invariants.md`. `make
  check` passes after the final edit.

### GTK 4 suite extraction: isolate checkbutton declarations (planned 2026-11-13 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large
`TestGtk4Theme` class (124 `test_` methods at this plan's base
commit). Move the three `test_checkbutton`-prefixed declaration
checks (about 52 lines at this plan's base commit) into their own
module, the same way the landed OSD (`tests/test_gtk4_osd.py`),
scale, spinbutton, disabled, emoji, entry, notebook, scrollbar,
switch, progressbar, levelbar, view, selected, button, row,
treeview, tabbar and sidebar parts moved theirs, and the waiting
"GTK 4 suite extraction: isolate menu declarations" entry moves its
own. This is independent of that waiting entry: neither moves a
`test_checkbutton` method, and this entry prunes no import at all
(the moved bodies call no `support` module name — see below), while
that one prunes `MENUBUTTON_ARROWS` and `MENU_CHECK` from the
`support.gtk_theme_spec` block; both edit
`tests/test_gtk4_theme.py` and `docs/invariants.md`, so whichever
merges later re-reads those two files before writing. Methods that
only contain `check` or `checkbutton` mid-name
(`test_tile_check_faces`, `test_osd_check_radio` in
`tests/test_gtk4_osd.py`, `test_menu_check_and_radio_are_boxless`)
stay where they are. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_checkbutton.py` with
  `class TestGtk4Checkbutton(Gtk4SheetRuleCases, unittest.TestCase)`
  and a one-line module docstring on the landed extraction modules'
  pattern (`tests/test_gtk4_view.py`). Move every `TestGtk4Theme`
  method whose name starts with `test_checkbutton_`, keeping each
  method's body and docstring unchanged:
  `test_checkbutton_focus_outline_color`,
  `test_checkbutton_focus_transition` and
  `test_checkbutton_corners`. At this plan's base commit they sit
  at two spots in `tests/test_gtk4_theme.py` — the first alone
  between the staying `test_sidebar_button_focus_outline_color`
  and `test_suggested_action_plain_arms`, the other two contiguous
  between the staying `test_flat_button_arms` and
  `test_expander_row_arrow_transition_motion` — so the move touches
  two separate deletions in the source module. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. At
  implementation re-grep every anchor this entry names.
- The new module imports `Gtk4SheetRuleCases` from
  `support.gtk4_sheet` and nothing else beyond `unittest`. Every
  helper the bodies call comes with the base class:
  `assert_scale_focus_outline`, `assert_scale_slider_transition`,
  `assert_rule`, `assert_matches_frame` and `assert_square_corner`
  are methods of `Gtk4SheetRuleCases` and its bases
  (`tests/support/gtk4_sheet.py`), and `self.css`, `self.rules` and
  `self.selectors` come from the shared `setUpClass`; no body
  spells a `support.gtk_theme_spec`, `support.platinum_palette` or
  `support.gtk_css` name, and none uses `re`, `tempfile` or
  `mock`, so no import moves and no import is pruned in either
  module.
- In `docs/invariants.md`, rewrite each
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_checkbutton…`
  anchor to
  `tests/test_gtk4_checkbutton.py::TestGtk4Checkbutton::test_checkbutton…`,
  wherever it appears — in the anchor column and in provenance
  prose. `grep -o 'TestGtk4Theme::test_checkbutton[a-z_]*'
  docs/invariants.md` finds exactly five member mentions at this
  plan's base commit across four rows:
  `test_checkbutton_focus_transition` as the motion row's anchor
  and again in the prose of the server-list-button row and the
  expander-row-arrow row,
  `test_checkbutton_focus_outline_color` alone in the focus-outline
  row, and `test_checkbutton_corners` alone in the wrapper-corners
  row. Rewrite only the moved anchors in place and leave every
  staying anchor as it reads — the bare prose mention of
  `test_checkbutton_focus_outline_color` inside the row-focus
  record keeps its wording, since the name persists in the new
  module and that prose names no module path. Do not rewrite
  history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the three moved methods exactly
  once, under `test_gtk4_checkbutton.TestGtk4Checkbutton`, and none
  of them under `test_gtk4_theme.TestGtk4Theme`. Every other
  `TestGtk4Theme` method is still listed there, including
  `test_tile_check_faces`.
- For each moved method, the AST of its function definition is
  identical to the original's at this plan's base commit, checked
  once during the run (for example by comparing `ast.dump` output).
  This is a run-time check, not a new committed test.
- `grep -n 'TestGtk4Theme::test_checkbutton' docs/invariants.md`
  prints nothing, each of the four touched rows still names its
  staying anchors under their original modules, and the invariants
  checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 50 lines, and
  `tests/test_gtk4_checkbutton.py` stays under about 60 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_checkbutton.py` and `docs/invariants.md`. `make
  check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

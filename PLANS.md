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

### GTK 4 suite extraction: isolate entry declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still about 4,900 lines in one `TestGtk4Theme`
class. That breaks the principle that a file is small enough to read in one sitting.
Move the five `test_entry_*` declaration checks (about 140 lines at this plan's base
commit) into their own module, the same way the landed OSD (`tests/test_gtk4_osd.py`)
and scale (`tests/test_gtk4_scale.py`) parts moved theirs. This is independent of
"README split, part 5/5" (that entry moves user-facing prose) and of the two waiting
"GTK 4 suite extraction: isolate spinbutton declarations" and "… isolate emoji
declarations" entries (those move only `test_spinbutton_*` and `test_emoji_*`
methods; no method set overlaps and neither entry edits this entry's invariants
rows). This is the one extraction entry that prunes a `tests/test_gtk4_theme.py`
import, so at implementation re-grep every anchor and every constant this entry
names. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_entry.py` with
  `class TestGtk4Entry(Gtk4SheetRuleCases, unittest.TestCase)` and a one-line
  module docstring (model it on `tests/test_gtk4_scale.py`). Move every
  `TestGtk4Theme` method whose name starts with `test_entry_` into it, keeping
  each method's body and comments unchanged: `test_entry_focus_outline_color`,
  `test_entry_focus_transition`, `test_entry_colour_classes`,
  `test_entry_image_inks` and `test_entry_progress`. Entry-named methods that do
  not start with `test_entry_` stay where they are: `test_flat_entry_fields`,
  `test_treeview_entry_fields` and `test_caps_lock_indicator` (plus the spin
  field methods the spinbutton plan already scoped out). `test_label_error_colour_class`
  stays in `tests/test_gtk4_theme.py`: the label colour-class row keeps its
  anchor to it and only swaps this entry's member.
- The new module imports exactly the names the moved bodies use:
  `ENTRY_PROGRESS_GTK4` from `support.gtk_theme_spec` and `BLACK` from
  `support.platinum_palette`. Every assertion helper the bodies call
  (`assert_rule`, `assert_rule_after`, `assert_exact_rule_once`,
  `assert_scale_focus_outline`, `assert_scale_slider_transition`) and the
  `self.rules`/`self.selectors` attributes come with `Gtk4SheetRuleCases` and its
  base classes (grep-checked at this plan's base commit: all five helpers are
  defined in `tests/support/gtk4_sheet.py` or `tests/support/gtk_rule_cases.py`).
  The moved bodies call no other support name (no `gtk_css`, `strip_comments`,
  `parse_css`, `HEX`, mock, tempfile or `re` use), and no other constant:
  unlike the spinbutton and emoji extractions, this move empties one import —
  `grep -n 'ENTRY_PROGRESS_GTK4' tests/test_gtk4_theme.py` at this plan's base
  commit prints only the import and the one moved use in `test_entry_progress` —
  so prune `ENTRY_PROGRESS_GTK4` from `tests/test_gtk4_theme.py`'s
  `support.gtk_theme_spec` import in the same change and import it in the new
  module. `BLACK` stays in `tests/test_gtk4_theme.py`'s import block: the whole
  file still far out-references the moved bodies' five uses. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`.
- In `docs/invariants.md`, rewrite each dotted anchor
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_entry_…` to
  `tests/test_gtk4_entry.py::TestGtk4Entry::test_entry_…` (`grep -n
  'TestGtk4Theme::test_entry' docs/invariants.md` finds six anchors across five
  rows at this plan's base commit: the focus-outline row, the focus-transition
  row, the entry-progress row, the entry colour-class row, the label colour-class
  row and the entry-icon-ink row). In the entry-progress row rewrite only the
  GTK 4 member and leave its two GTK 3 `tests/test_gtk_theme_controls.py`
  anchors and the row's prose alone; in the label colour-class row rewrite only
  this entry's member and leave the `test_label_error_colour_class` anchor alone.
  Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the five moved methods exactly once, under
  `test_gtk4_entry.TestGtk4Entry`, and none of them under
  `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still
  listed there, including `test_flat_entry_fields`, `test_treeview_entry_fields`,
  `test_caps_lock_indicator` and `test_label_error_colour_class`.
- For each moved method, the AST of its function definition is identical to the
  original's at this plan's base commit, checked once during the run (for example
  by comparing `ast.dump` output). This is a run-time check, not a new committed
  test.
- `grep -n 'TestGtk4Theme::test_entry' docs/invariants.md` prints nothing, and
  the invariants checker inside `make check` resolves every new anchor; the
  progress row's GTK 3 anchors and the label row's `test_label_error_colour_class`
  anchor are still present and resolve.
- `grep -n 'ENTRY_PROGRESS_GTK4' tests/test_gtk4_theme.py` prints nothing.
- `tests/test_gtk4_theme.py` shrinks by at least 130 lines, and
  `tests/test_gtk4_entry.py` stays under about 300 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_entry.py` and `docs/invariants.md`. `make check` passes after
  the final edit.

### GTK 4 suite extraction: isolate notebook declarations (planned 2026-11-12 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large `TestGtk4Theme` class
(about 4,400 lines at this plan's base commit). That breaks the principle that a
file is small enough to read in one sitting. Move the five `test_notebook_*`
declaration checks (about 135 lines at this plan's base commit) into their own
module, the same way the landed OSD (`tests/test_gtk4_osd.py`), scale
(`tests/test_gtk4_scale.py`), spinbutton (`tests/test_gtk4_spinbutton.py`) and
disabled (`tests/test_gtk4_disabled.py`) parts moved theirs. This is independent
of the waiting "GTK 4 suite extraction: isolate entry declarations" entry (that
entry moves only `test_entry_*` methods; the two method sets do not overlap and
neither entry edits the other's invariants rows, though both edit
`tests/test_gtk4_theme.py` and `docs/invariants.md`). At implementation re-grep
every anchor this entry names. No stylesheet or production behavior changes.

**Approach and files.**
- Create `tests/test_gtk4_notebook.py` with
  `class TestGtk4Notebook(Gtk4SheetRuleCases, unittest.TestCase)` and a one-line
  module docstring on the landed extraction modules' pattern. Move every
  `TestGtk4Theme` method whose name starts with `test_notebook_` into it,
  keeping each method's body and docstring unchanged:
  `test_notebook_focus_transition`, `test_notebook_tab_close_button_arms`,
  `test_notebook_tab_scroll_arrow_faces`, `test_notebook_focus_outline_color`
  and `test_notebook_header`. The first four are contiguous in the file; the
  header check sits later. No other method shares the prefix (the
  `test_tabbar_*`, `test_tab_thumbnail_*` and `test_tabgrid_*` names are
  separate prefixes and stay); the landed GTK 3 notebook checks live in
  `tests/test_gtk_theme.py` and stay there.
- The new module imports exactly the names the moved bodies use:
  `BLACK` and `FACE` from `support.platinum_palette`, and `BUTTON_BEVEL`,
  `INVERTED_BUTTON_BEVEL` and `DISABLED_TEXT` from `support.gtk_theme_spec`
  (the source module the original import block draws each name from). Every
  assertion helper the bodies call (`assert_rule`, `assert_rule_group` in
  `tests/support/gtk_rule_cases.py`; `assert_scale_focus_outline` and
  `assert_scale_slider_transition` in `tests/support/gtk4_sheet.py`) and the
  `self.rules`/`self.selectors` attributes come with `Gtk4SheetRuleCases` and
  its base classes (grep-checked at this plan's base commit); the moved bodies
  call no other support name (no `gtk_css`, `parse_css`, `HEX`, mock, tempfile
  or `re` use). Each of the five constants is still referenced by remaining
  methods after the move (whole-file grep count exceeds the moved bodies'
  count for every name: `BLACK` 89 vs 10, `FACE` 28 vs 4, `BUTTON_BEVEL` 11
  vs 3, `INVERTED_BUTTON_BEVEL` 7 vs 2, `DISABLED_TEXT` 12 vs 2), so
  `tests/test_gtk4_theme.py`'s import block needs no change. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`.
- In `docs/invariants.md`, rewrite each dotted anchor
  `tests/test_gtk4_theme.py::TestGtk4Theme::test_notebook_…` to
  `tests/test_gtk4_notebook.py::TestGtk4Notebook::test_notebook_…` (`grep -n
  'TestGtk4Theme::test_notebook' docs/invariants.md` finds four rows at this
  plan's base commit: the focus-transition row, the focus-outline-color row,
  the close-button row shared with the GTK 3 suite, and the scroll-arrow row).
  On the shared close-button row, rewrite only the GTK 4 member and leave the
  GTK 3 `tests/test_gtk_theme.py::TestGtkTheme::test_notebook_tab_close_button_arms`
  member and the row's prose alone. `test_notebook_header` carries no
  invariants anchor. Do not rewrite history in PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of the five moved methods exactly once, under
  `test_gtk4_notebook.TestGtk4Notebook`, and none of them under
  `test_gtk4_theme.TestGtk4Theme`. Every other `TestGtk4Theme` method is still
  listed there.
- For each moved method, the AST of its function definition is identical to the
  original's at this plan's base commit, checked once during the run (for
  example by comparing `ast.dump` output). This is a run-time check, not a new
  committed test.
- `grep -n 'TestGtk4Theme::test_notebook' docs/invariants.md` prints nothing,
  the GTK 3 member of the shared close-button row still reads
  `tests/test_gtk_theme.py::TestGtkTheme::test_notebook_tab_close_button_arms`,
  and the invariants checker inside `make check` resolves every new anchor.
- `tests/test_gtk4_theme.py` shrinks by at least 130 lines, and
  `tests/test_gtk4_notebook.py` stays under about 250 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_notebook.py` and `docs/invariants.md`. `make check` passes
  after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

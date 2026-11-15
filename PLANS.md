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

**Size drift (2026-11-14, steward; re-measured 2026-11-14 by the steward role):** PRINCIPLES.md
asks each file to stay small enough to read in one sitting, and this plan set's working budget is
roughly 800 lines (the suite-split entries below). Measured with `wc -l` over `tests/`, `tools/`
and `theme/` at this worktree's base, 23 files exceed 800 lines: `theme/gtk/.../gtk-3.0/gtk.css`
(7111) and `gtk-4.0/gtk.css` (6523), `theme/firefox/.../chrome/userChrome.css` (1581) and
`userContent.css` (941), and these tests: `test_render_surface_units.py` (1960),
`test_gtk4_theme.py` (1947), `test_render_dialog_gates.py` (1721), `test_render_file_dialog.py`
(1462), `test_gtk_theme.py` (1274), `test_render_surface.py` (1234), `test_gtk_theme_views.py`
(1179), `test_install_firefox.py` (1173), `test_gtk_css.py` (1170), `test_make_refusals.py`
(1063), `test_gtk_theme_osd.py` (1008), `test_render_failure_paths.py` (998),
`test_cursors_theme.py` (964), `test_apply_theme.py` (956), `test_theme_install.py` (940),
`test_check_parallel.py` (931), `tests/support/gtk_rule_cases.py` (881),
`test_firefox_theme_library.py` (864) and `test_local_hook.py` (857).
`test_gtk_theme_controls.py` has left the list (283 lines after GTK 3 split parts 1/11 to 10/11
landed). The only queued splits that touch a listed file are the two GTK 4 extraction entries for
`test_gtk4_theme.py`; together they move the scrolled-window run and the scroll-bar breadth tail,
which leaves it well above 800 lines. The render-test files (`test_render_surface_units.py`,
`test_render_dialog_gates.py`, `test_render_file_dialog.py`) have no plan. The plan role should
decompose those per family, as the GTK 4 extraction series did, before adding features to them.
The two GTK sheets and the Firefox `userChrome.css` are a different problem: the sheets are
single-file theme artifacts, so splitting them needs a packaging choice (for example GTK
`@import`) that is not settled here. This note queues nothing and changes no behavior.

### GTK 4 suite extraction: isolate the link checks (planned 2026-11-14 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large `TestGtk4Theme`
class. Move its three link checks into their own module, the way the merged
entry-field and close-button extractions moved theirs. The three are
`test_links`, `test_inline_link_interaction_colours` and
`test_link_button_follows_the_button_state_rules`. At this plan's base
commit they sit together, directly after `test_tile_check_faces` and
directly before `test_suggested_action_plain_arms`. The move also lets the
source module drop its `LINK` import. No stylesheet or production behavior
changes.

This entry is independent of the tile-check extraction above and the
title-band extraction waiting to merge. Neither moves these methods. All
three edit `tests/test_gtk4_theme.py` and `docs/invariants.md`, so whichever
merges later re-reads the file and the rows before writing and rewrites only
its own anchors. If the tile-check move has landed first, the three methods
then sit directly after `test_content_view_field_and_hover`.

**Approach and files.**
- Create `tests/test_gtk4_links.py` with `class
  TestGtk4Links(Gtk4SheetRuleCases, unittest.TestCase)`. Give it a one-line
  module docstring following the existing extraction modules' pattern
  (`tests/test_gtk4_widget_corners.py`), `from __future__ import
  annotations`, and the `if __name__ == "__main__":` guard. Move the three
  methods in their current order with their bodies, comments and docstrings
  unchanged. Never import `tests/test_gtk4_theme.py` or inherit
  `TestGtk4Theme`. At implementation, re-grep every anchor this entry names.
- The moved bodies get every helper they call from the base-class chain
  (`tests/support/gtk4_sheet.py` → `tests/support/gtk_rule_cases.py`):
  `assert_links`, `assert_rule` and `assert_disabled_text`, plus `self.css`
  from the shared `setUpClass`.
- The new module imports `Gtk4SheetRuleCases` from `support.gtk4_sheet`,
  `strip_comments` from `support.gtk_css`, and `LINK` from
  `support.gtk_theme_spec`. It imports nothing else beyond `unittest`. Check
  the list by grep over the moved bodies before writing the import block.
- At this plan's base commit, `LINK` is named in `tests/test_gtk4_theme.py`
  only by its import line and `test_inline_link_interaction_colours`. Drop it
  from the source module's import block once `grep -nw LINK` shows nothing
  but its import line. `strip_comments` stays, because other `TestGtk4Theme`
  methods (`test_only_palette_hex_literals`,
  `test_no_status_or_translucent_shade_roles`, the dim-label check) still use
  it. Leave every other import alone.
- In `docs/invariants.md`, rewrite the GTK 4 anchors in two rows:
  - the "Both GTK sheets colour link text" row: change
    `tests/test_gtk4_theme.py::TestGtk4Theme::test_links` to
    `tests/test_gtk4_links.py::TestGtk4Links::test_links`, and leave its
    GTK 3 anchor `tests/test_gtk_theme.py::TestGtkTheme::test_links`
    untouched;
  - the "Ordinary GTK 4 inline links" row: change both its
    `tests/test_gtk4_theme.py::TestGtk4Theme::` anchors
    (`test_inline_link_interaction_colours` and `test_links`) to the
    `tests/test_gtk4_links.py::TestGtk4Links::` spelling.
  Leave the rest of each row's text, and the GTK 3 inline-link row,
  untouched. Then grep `docs/invariants.md` for
  `TestGtk4Theme::test_link` to catch any other row naming the moved
  methods, and rewrite only those anchors. Do not rewrite history in
  PLANS-DONE.md or BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of `test_links`,
  `test_inline_link_interaction_colours` and
  `test_link_button_follows_the_button_state_rules` exactly once, under
  `test_gtk4_links.TestGtk4Links`, and none under
  `test_gtk4_theme.TestGtk4Theme`. `test_suggested_action_plain_arms` is
  still listed under `test_gtk4_theme.TestGtk4Theme`. The GTK 3 methods of
  the same names in `tests/test_gtk_theme.py` are still listed there.
- Each moved method's function-definition AST is identical to the
  original's at this plan's base commit. Check this once during the run (for
  example by comparing `ast.dump` output); it is a run-time check, not a new
  committed test.
- `grep -n 'TestGtk4Theme::test_link\|TestGtk4Theme::test_inline_link' docs/invariants.md`
  prints nothing, and the invariants checker inside `make check` resolves
  the new anchors.
- `grep -nw LINK tests/test_gtk4_theme.py` prints nothing. The unused-import
  scanner inside `make check` (`tests/test_no_unused_imports.py`) reports no
  finding for either module.
- `tests/test_gtk4_theme.py` shrinks by at least 25 lines, and
  `tests/test_gtk4_links.py` stays under about 50 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_links.py` and `docs/invariants.md`. `make check` passes
  after the final edit.

### GTK 4 suite extraction: isolate the action and flat button arm checks (planned 2026-11-14 by the plan role)

**Goal.** `tests/test_gtk4_theme.py` is still one large `TestGtk4Theme`
class. Move its four push-button arm checks into their own module, the way
the merged entry-field and close-button extractions moved theirs. The four
are `test_suggested_action_plain_arms`, `test_destructive_action_plain_arms`,
`test_action_class_flat_arms` and `test_flat_button_arms`. At this plan's
base commit they sit together, directly after
`test_link_button_follows_the_button_state_rules` and directly before
`test_server_list_button_rotation_motion`. The move also lets the source
module drop its `BUTTON_BEVEL` and `INVERTED_BUTTON_BEVEL` imports. No
stylesheet or production behavior changes.

This entry is independent of the link extraction above and the tile-check
extraction waiting to merge. Neither moves these methods. All three edit
`tests/test_gtk4_theme.py` and `docs/invariants.md`, and the link entry
also edits the source module's `support.gtk_theme_spec` import block, so
whichever merges later re-reads the file and the rows before writing and
rewrites only its own anchors and import names. If the link move has landed
first, the four methods then sit directly after
`test_tile_check_faces` (or `test_content_view_field_and_hover`, if the
tile-check move has landed too).

**Approach and files.**
- Create `tests/test_gtk4_action_buttons.py` with `class
  TestGtk4ActionButtons(Gtk4SheetRuleCases, unittest.TestCase)`. Give it a
  one-line module docstring following the existing extraction modules'
  pattern (`tests/test_gtk4_button.py`: "GTK 4 … checks moved out of
  ``test_gtk4_theme``."), `from __future__ import annotations`, and the
  `if __name__ == "__main__":` guard. Move the four methods in their current
  order with their bodies and comments unchanged. Never import
  `tests/test_gtk4_theme.py` or inherit `TestGtk4Theme`. Do not merge them
  into `tests/test_gtk4_button.py`; keeping a separate module keeps both
  files short. At implementation, re-grep every anchor this entry names.
- The moved bodies get every helper they call from the base-class chain
  (`tests/support/gtk4_sheet.py` → `tests/support/gtk_rule_cases.py`):
  `assert_plain_action_arms` and `assert_rule`, plus `self.rules` from the
  shared `setUpClass`.
- The new module imports `Gtk4SheetRuleCases` from `support.gtk4_sheet`;
  `BUTTON_BEVEL`, `DISABLED_TEXT` and `INVERTED_BUTTON_BEVEL` from
  `support.gtk_theme_spec`; and `BLACK` and `FACE` from
  `support.platinum_palette`. It imports nothing else beyond `unittest`.
  Check the list by grep over the moved bodies before writing the import
  block.
- At this plan's base commit, `BUTTON_BEVEL` and `INVERTED_BUTTON_BEVEL`
  are named in `tests/test_gtk4_theme.py` only by their import lines and the
  moved methods. Drop each from the source module's import block once
  `grep -nw` shows nothing but its import line. `DISABLED_TEXT`, `FACE` and
  `BLACK` stay, because other `TestGtk4Theme` methods (the placeholder,
  dimmed-label and dim-label checks; the window, banner and places-sidebar
  checks) still use them. Leave every other import alone.
- In `docs/invariants.md`, rewrite the four GTK 4 anchors that name the
  moved methods, changing
  `tests/test_gtk4_theme.py::TestGtk4Theme::<method>` to
  `tests/test_gtk4_action_buttons.py::TestGtk4ActionButtons::<method>`:
  - the "A Platinum GTK flat button keeps the existing push-button face"
    row (`test_flat_button_arms`);
  - the "A Platinum GTK flat action button keeps the existing push-button
    face" row (`test_action_class_flat_arms`);
  - the "GTK 4 plain suggested-action push buttons" row
    (`test_suggested_action_plain_arms`);
  - the "GTK 4 plain destructive-action push buttons" row
    (`test_destructive_action_plain_arms`).
  Leave the rest of each row's text, and the GTK 3 rows naming
  `tests/test_gtk_theme_buttons.py` methods of the same names, untouched.
  Then grep `docs/invariants.md` for `TestGtk4Theme::test_` followed by any
  of the four names to catch another row, and rewrite only those anchors.
  The bare-name comment mentions in `tests/support/gtk4_sheet.py`
  (`assert_plain_action_arms` and the plain-family bound) carry no module
  path and stay as they are. Do not rewrite history in PLANS-DONE.md or
  BUGS-FIXED.md.

**Acceptance criteria.**
- Unittest discovery lists each of `test_suggested_action_plain_arms`,
  `test_destructive_action_plain_arms`, `test_action_class_flat_arms` and
  `test_flat_button_arms` exactly once under
  `test_gtk4_action_buttons.TestGtk4ActionButtons`, and none under
  `test_gtk4_theme.TestGtk4Theme`. `test_server_list_button_rotation_motion`
  is still listed under `test_gtk4_theme.TestGtk4Theme`. The GTK 3 methods
  of the same names in `tests/test_gtk_theme_buttons.py` are still listed
  there.
- Each moved method's function-definition AST is identical to the
  original's at this plan's base commit. Check this once during the run (for
  example by comparing `ast.dump` output); it is a run-time check, not a new
  committed test.
- `grep -nE 'TestGtk4Theme::test_(suggested_action_plain|destructive_action_plain|action_class_flat|flat_button)_arms' docs/invariants.md`
  prints nothing, and the invariants checker inside `make check` resolves
  the new anchors.
- `grep -nw 'BUTTON_BEVEL\|INVERTED_BUTTON_BEVEL' tests/test_gtk4_theme.py`
  prints nothing. The unused-import scanner inside `make check`
  (`tests/test_no_unused_imports.py`) reports no finding for either module.
- `tests/test_gtk4_theme.py` shrinks by at least 120 lines, and
  `tests/test_gtk4_action_buttons.py` stays under about 150 lines.
- `git diff --stat` touches only `tests/test_gtk4_theme.py`,
  `tests/test_gtk4_action_buttons.py` and `docs/invariants.md`.
  `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

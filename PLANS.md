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

**Size drift (2026-11-14, steward):** PRINCIPLES.md asks each file to stay small enough to read
in one sitting, and this plan set's working budget is roughly 800 lines (the suite-split entries
below). Measured with `wc -l` over `tests/`, `tools/` and `theme/` at this worktree's base, 24
files exceed 800 lines: `theme/gtk/.../gtk-3.0/gtk.css` (7111) and `gtk-4.0/gtk.css` (6523),
`theme/firefox/.../chrome/userChrome.css` (1581) and `userContent.css` (941), and these tests:
`test_gtk_theme_controls.py` (2567), `test_gtk4_theme.py` (2052), `test_render_surface_units.py`
(1825), `test_render_dialog_gates.py` (1721), `test_render_file_dialog.py` (1462),
`test_gtk_theme.py` (1274), `test_render_surface.py` (1234), `test_gtk_theme_views.py` (1179),
`test_install_firefox.py` (1174), `test_gtk_css.py` (1170), `test_make_refusals.py` (1063),
`test_gtk_theme_osd.py` (1008), `test_render_failure_paths.py` (993), `test_cursors_theme.py`
(964), `test_apply_theme.py` (952), `test_theme_install.py` (940), `test_check_parallel.py` (937),
`tests/support/gtk_rule_cases.py` (881), `test_firefox_theme_library.py` (864) and
`test_local_hook.py` (836). Only `test_gtk_theme_controls.py` and `test_gtk4_theme.py` have queued splits. The first is
blocked for review; the second moves four methods (at least 100 lines) and leaves its file above
800 lines. The render-test files (`test_render_surface_units.py`,
`test_render_dialog_gates.py`, `test_render_file_dialog.py`) have no plan. The plan role should
decompose those per family, as the GTK 4 extraction series did, before adding features to them.
The two GTK sheets and the Firefox `userChrome.css` are a different problem: the sheets are
single-file theme artifacts, so splitting them needs a packaging choice (for example GTK
`@import`) that is not settled here. This note queues nothing and changes no behavior.

### GTK 3 controls suite split, part 2/11: move the shared probe prologue and `_run_gtk_child` delegate into tests/support/gtk_child_probe.py (planned 2026-11-14 by the plan role)

**Goal.** Ten probes in `tests/test_gtk_theme_controls.py` call the
`TestGtkThemeControls._run_gtk_child` delegate. Nine of them build their
program from the module-level `_GTK3_SHEET_PROLOGUE`. Once the probe
families move (parts 6–11), several suites need both. Move
`_GTK3_SHEET_PROLOGUE` (byte-identical value, with its comment)
into `tests/support/gtk_child_probe.py` beside the `_GTK3_CHILD_HEAD` it
builds on. Add a mixin class `Gtk3ChildProbeCases` there whose only member
is the `_run_gtk_child(self, program, *paths)` delegate, moved verbatim
(it returns `run_gtk_child(self, program, *paths)`). Then
`TestGtkThemeControls` becomes
`class TestGtkThemeControls(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`,
imports `_GTK3_SHEET_PROLOGUE` from support, and drops its own copies.
Later probe parts reuse the mixin, so the moved probe methods keep calling
`self._run_gtk_child` unchanged. The mixed-check probe's own prelude stays
in its test.

**Reference sites.** The `tests/test_no_gtk_introspection.py` module
docstring and its assertion message both name
`tests/test_gtk_theme_controls.py` as the module that runs GTK in child
interpreters. Both are reworded to name `tests/support/gtk_child_probe.py`
and the GTK 3 suites that use it. So is the `tests/test_gtk_child_probe_support.py`
docstring's "moved here from `tests/test_gtk_theme_controls.py`", which also
gains a mention of the prologue and mixin. The support module docstring
gains one sentence on the two new names.

**Acceptance criteria.**
- `tests/test_gtk_child_probe_support.py` gains tests showing three things.
  `_GTK3_SHEET_PROLOGUE` starts with `"\nimport re\n"` followed by
  `_GTK3_CHILD_HEAD`, and ends with the `css = re.sub(...)` url()-stripping
  line. A `unittest.TestCase` subclass mixing in `Gtk3ChildProbeCases` passes
  a child program that exits 0 and is skipped on one that exits 77. Both
  child programs import no GTK.
- `_GTK3_SHEET_PROLOGUE` and `_run_gtk_child` are each defined exactly once
  in the repository, in `tests/support/gtk_child_probe.py`, and the
  prologue's value equals the original. Check this at run time by comparing
  against the base commit's evaluated constant.
- Discovery lists the same `TestGtkThemeControls` methods as before. The ten
  probes skip identically without `PLATINUM_RUN_GUI_TESTS=1`.
- `tests/test_no_gtk_introspection.py` still passes. Neither its docstring
  nor its message, nor the probe-support docstring, names
  `test_gtk_theme_controls` any more. `make check` passes, and its
  unused-import scanner reports nothing.

### GTK 3 controls suite split, part 3/11: move the linked-border methods into tests/test_gtk_theme_linked.py (planned 2026-11-14 by the plan role)

**Goal.** Move `test_linked_members_strip_their_trailing_border`,
`test_linked_last_member_restores_the_border`,
`test_linked_end_field_corners` and
`test_linked_protection_keeps_the_path_bar_and_stack_switcher_outlines`
into new `tests/test_gtk_theme_linked.py`, as
`class TestGtkThemeLinked(GtkSheetRuleCases, unittest.TestCase)` with
`CSS_PATH = CSS`. None of them renders.

**Reference sites.** These are `docs/invariants.md` mentions of the four
methods, the `tests/test_gtk_theme_views.py` comment naming
`TestGtkThemeControls::test_linked_end_field_corners`, and the
`tests/test_gtk_theme_osd.py` comment naming the same method.

**Acceptance criteria.**
- Discovery lists the four methods exactly once each, under
  `test_gtk_theme_linked`, and none under `test_gtk_theme_controls`. Each
  moved method's `ast.dump` equals the original's. This is a run-time
  check, not a committed test.
- Every invariants row and comment site naming a moved method names
  `test_gtk_theme_linked`/`TestGtkThemeLinked`. The invariants checker inside
  `make check` resolves them.
- The unused-import scanner reports nothing for either module, and
  `make check` passes. If this leaves `TestGtkThemeControls` with no test
  method, the file deletion and grep from part 1/11's series rules apply.

### GTK 3 controls suite split, part 4/11: move the scale methods into tests/test_gtk_theme_scale.py (planned 2026-11-14 by the plan role)

**Goal.** Move `test_scale`, `test_scale_decoration_ink`,
`test_scale_focus_outline`, `test_scale_plain_container_geometry`,
`test_scale_fine_tune_container_geometry` and
`test_scale_marks_indicator_geometry` into new
`tests/test_gtk_theme_scale.py`, as
`class TestGtkThemeScale(GtkSheetRuleCases, unittest.TestCase)`. None of
them renders. `test_meter_state_and_backdrop_faces`, which sits between
`test_scale` and `test_scale_decoration_ink`, stays for part 8/11.

**Reference sites.** These are `docs/invariants.md` mentions of the six
methods and the two `tests/test_gtk_theme_views.py` comments naming
`test_scale_fine_tune_container_geometry` and
`test_scale_marks_indicator_geometry`. The other is the
`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` scale tick-mark/value-label
ink record (dated 2026-11-09), whose
`tests/test_gtk_theme_controls.py::TestGtkThemeControls` names the GTK 3
decoration-ink record. It becomes
`tests/test_gtk_theme_scale.py::TestGtkThemeScale::test_scale_decoration_ink`,
a comment-only edit.

**Acceptance criteria.**
- Discovery lists the six methods exactly once each, under
  `test_gtk_theme_scale`, and none under `test_gtk_theme_controls`. The
  `ast.dump` of each matches the original's.
- Every listed site names the new module, the invariants checker resolves
  it, and `git diff` of the GTK 4 sheet touches only that comment.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 5/11: move the button methods into tests/test_gtk_theme_buttons.py (planned 2026-11-14 by the plan role)

**Goal.** Move the `assert_plain_action_arms` helper and
`test_suggested_action_plain_arms`, `test_flat_button_plain_arms`,
`test_selected_row_button_arms`, `test_destructive_action_plain_arms`,
`test_action_class_flat_arms`, `test_button_focus_outline` and
`test_button_disabled_and_backdrop` into new
`tests/test_gtk_theme_buttons.py`, as
`class TestGtkThemeButtons(GtkSheetRuleCases, unittest.TestCase)`. None of
them renders. Grep first to confirm that no remaining controls method calls
`assert_plain_action_arms`. If one does, the helper stays in both classes.

**Reference sites.** These are `docs/invariants.md` mentions of the seven
methods and the two `tests/test_gtk_theme_osd.py` comments naming
`test_suggested_action_plain_arms` and `test_destructive_action_plain_arms`.
They also include the two `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`
`transition: none` records that cite "the `button.flat:hover:active` and
backdrop assertions in tests/test_gtk_theme_controls.py". Those are
comment-only edits naming `tests/test_gtk_theme_buttons.py`.

**Acceptance criteria.**
- Discovery lists the seven methods exactly once each, under
  `test_gtk_theme_buttons`, and none under `test_gtk_theme_controls`. The
  `ast.dump` of each moved function matches the original's.
- Every listed site names the new module, the invariants checker resolves
  it, and `git diff` of the GTK 3 sheet touches only comment lines.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 6/11: move the spin-button methods into tests/test_gtk_theme_spinbutton.py (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_horizontal_spinbutton_focus_outline`,
`test_vertical_spinbutton_focus_outline`,
`test_horizontal_spinbutton_steppers_share_one_seam` and the three probes
into new `tests/test_gtk_theme_spinbutton.py`, as
`class TestGtkThemeSpinbutton(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.
The probes are `test_horizontal_spinbutton_steppers_render_one_pixel_seams`,
`test_osd_spin_field_renders_the_mirrored_etch_in_rtl` and
`test_vertical_spinbutton_renders_one_pixel_joins`. The probes import
`_GTK3_SHEET_PROLOGUE` and the `_GTK3_*` heads they use from
`support.gtk_child_probe`.

**Reference sites.** These are `docs/invariants.md` mentions of the six
methods and the `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` OSD
spin-field record naming
`TestGtkThemeControls::test_osd_spin_field_renders_the_mirrored_etch_in_rtl`
(comment-only edit). They also include the `tests/test_gtk_theme.py`
comment saying the horizontal-seam probe lives in
`tests/test_gtk_theme_controls.py`.

**Acceptance criteria.**
- Discovery lists the six methods exactly once each, under
  `test_gtk_theme_spinbutton`, and none under `test_gtk_theme_controls`.
  Each `ast.dump` matches the original's, so every child program string is
  byte-identical.
- Without `PLATINUM_RUN_GUI_TESTS=1` the three probes skip exactly as
  before. Every listed site names the new module, and the invariants checker
  resolves it.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 7/11: move the entry methods into tests/test_gtk_theme_entry.py (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_entry_progress`,
`test_entry_progress_draws_a_two_pixel_strip` (probe),
`test_entry_focus_outline`, `test_entry_error_warning_colour_classes`,
`test_entry_state_faces`, `test_entry_image_inks` and
`test_entry_tag_faces` into new `tests/test_gtk_theme_entry.py`, as
`class TestGtkThemeEntry(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.

**Reference sites.** These are `docs/invariants.md` mentions of the seven
methods. Before editing, grep for any other by-name site naming one of them
and repoint it too.

**Acceptance criteria.**
- Discovery lists the seven methods exactly once each, under
  `test_gtk_theme_entry`, and none under `test_gtk_theme_controls`. Each
  `ast.dump` matches the original's.
- The probe skips as before without `PLATINUM_RUN_GUI_TESTS=1`. Every
  invariants mention of a moved method names the new module, and the checker
  resolves it.
- The new module stays under ~800 lines, the unused-import scanner reports
  nothing, and `make check` passes. The deletion rule from part 1/11
  applies.

### GTK 3 controls suite split, part 8/11: move the progress-bar and meter methods into tests/test_gtk_theme_progress.py (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_progressbar`, `test_meter_geometry`,
`test_treeview_progress_bar`, `test_meter_label_ink`,
`test_progressbar_fill_spans_the_trough` (probe) and
`test_meter_state_and_backdrop_faces` into new
`tests/test_gtk_theme_progress.py`, as
`class TestGtkThemeProgress(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.

**Reference sites.** These are `docs/invariants.md` mentions of the six
methods and the `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`
disabled-trough record naming
`TestGtkThemeControls::test_meter_state_and_backdrop_faces` (comment-only
edit).

**Acceptance criteria.**
- Discovery lists the six methods exactly once each, under
  `test_gtk_theme_progress`, and none under `test_gtk_theme_controls`. Each
  `ast.dump` matches the original's.
- The probe skips as before without `PLATINUM_RUN_GUI_TESTS=1`. Every
  listed site names the new module, the checker resolves it, and `git diff`
  of the GTK 4 sheet touches only that comment.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 9/11: move the view-field, viewport and frame probes into tests/test_gtk_theme_frames.py (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_disabled_view_renders_the_white_field_and_grey_ink`
(probe), `test_scrolled_viewport_draws_no_frame`,
`test_scrolled_viewport_renders_one_frame` (probe),
`test_flat_frame_draws_no_border` and `test_flat_frame_renders_no_frame`
(probe) into new `tests/test_gtk_theme_frames.py`, as
`class TestGtkThemeFrames(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.
The module docstring says it covers the view field as well as the viewport
and frame borders.

**Reference sites.** These are `docs/invariants.md` mentions of the five
methods. Grep for any other by-name site and repoint it.

**Acceptance criteria.**
- Discovery lists the five methods exactly once each, under
  `test_gtk_theme_frames`, and none under `test_gtk_theme_controls`. Each
  `ast.dump` matches the original's.
- The three probes skip as before without `PLATINUM_RUN_GUI_TESTS=1`, and
  the invariants checker resolves every repointed mention.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 10/11: move the check and radio methods into tests/test_gtk_theme_check.py (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_mixed_check_draws_a_black_dash` (the probe with its own
prelude, which moves with it), `test_checkbutton_focus_outline`,
`test_radiobutton_focus_outline`, `test_check_radio_tick_motion` and
`test_check_radio_backdrop_motion_disabled_and_selected_row` into new
`tests/test_gtk_theme_check.py`, as
`class TestGtkThemeCheck(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.
The mixed-check probe passes the assets directory, so the module binds its
own `THEME_DIR`.

**Reference sites.** These are `docs/invariants.md` mentions of the five
methods. Grep for any other by-name site and repoint it.

**Acceptance criteria.**
- Discovery lists the five methods exactly once each, under
  `test_gtk_theme_check`, and none under `test_gtk_theme_controls`. Each
  `ast.dump` matches the original's.
- The probe skips as before without `PLATINUM_RUN_GUI_TESTS=1`, and the
  invariants checker resolves every repointed mention.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

### GTK 3 controls suite split, part 11/11: move the switch, spinner, level-bar, notebook and bar-title methods into two suites (planned 2026-11-14 by the plan role; "requires part 2/11 landed")

**Goal.** Move `test_spinner`, `test_levelbar`, `test_switch`,
`test_switch_focus_outline` and `test_switch_state_and_backdrop_faces` into
new `tests/test_gtk_theme_switch.py`, as
`class TestGtkThemeSwitch(GtkSheetRuleCases, unittest.TestCase)`. Its
docstring covers the switch and the spinner and level-bar status
indicators. Move `test_notebook_tab_faces_render` (probe),
`test_menubar_titles` and `test_toolbar_and_menubar` into new
`tests/test_gtk_theme_bars.py`, as
`class TestGtkThemeBars(Gtk3ChildProbeCases, GtkSheetRuleCases, unittest.TestCase)`.

**Reference sites.** These are `docs/invariants.md` mentions of the eight
methods. Grep for any other by-name site and repoint it.

**Acceptance criteria.**
- Discovery lists the eight methods exactly once each, under their new
  module, and none under `test_gtk_theme_controls`. Each `ast.dump` matches
  the original's.
- The notebook probe skips as before without `PLATINUM_RUN_GUI_TESTS=1`, and
  the invariants checker resolves every repointed mention.
- The unused-import scanner reports nothing, and `make check` passes. The
  deletion rule from part 1/11 applies.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

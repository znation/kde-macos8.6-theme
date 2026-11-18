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

**Size drift (2026-11-14, steward; re-measured 2026-11-18 by the steward role):** PRINCIPLES.md
asks each file to stay small enough to read in one sitting, and this plan set's working budget is
roughly 800 lines (the suite-split entries below). Measured with `wc -l` over text files in
`tests/`, `tools/` and `theme/` at this worktree's base, the largest remaining files include
`theme/gtk/.../gtk-3.0/gtk.css` (7111) and `gtk-4.0/gtk.css` (6523), Firefox
`userChrome.css` (1581) and `userContent.css` (941), and test modules
`test_render_file_dialog.py` (1464), `test_gtk_theme.py` (1274),
`test_render_surface.py` (1234), `test_gtk_theme_views.py` (1179),
`test_install_firefox.py` (1173), `test_gtk_css.py` (1170), `test_make_refusals.py`
(1063), `test_gtk_theme_osd.py` (1008), `test_render_failure_paths.py` (999),
`test_apply_theme.py` (970), `test_cursors_theme.py` (964), `test_theme_install.py` (940),
`test_render_surface_units.py` (940), `test_check_parallel.py` (931),
`test_render_dialog_gates.py` (887), `test_local_hook.py` (885),
`tests/support/gtk_rule_cases.py` (881) and `test_firefox_theme_library.py` (864).
`test_gtk4_theme.py` is now 108 lines after its extraction series landed. The render-test files
(`test_render_surface_units.py`, `test_render_dialog_gates.py`, `test_render_file_dialog.py`)
remain above the working budget and have no decomposition plan; the plan role should split them
per family before adding features. The GTK sheets and Firefox `userChrome.css` are single-file
theme artifacts, so splitting them needs a packaging choice (for example GTK `@import`) that is
not settled here. This note queues nothing and changes no behavior.

### Render dialog gates suite extraction: isolate the line-input dialog gate (planned 2026-11-18 by the plan role)

**Goal.** Give the line-input pixel gate a focused module and bring the remaining
`tests/test_render_dialog_gates.py` below the roughly 800-line working budget in
the size-drift note. This is independent of the queued render-readiness plan:
it moves gate coverage, without changing the session implementation.

**Approach and files touched.** Move `TestLineInputDialogRender`, its
`@dialog_gate_guard()` decorator, and `LINEEDIT_DIALOG_FIELD`,
`LINEEDIT_DIALOG_FIELD_CROP`, `LINEEDIT_DIALOG_OK_BUTTON` with their measurement
comments to new `tests/test_render_lineedit_dialog.py`. Preserve the class and
method names, `KIND = "lineedit"`, crops, reference-role expectations and caret
exclusion. Import `DialogGate` from `support.render_gates` and the existing
`FIELD_BORDER_RUNS` / `FIELD_CORNER_PIXELS` from `support.firstboot_lineedit`;
remove imports that become unused in the original module. No test-module imports
or new support helper are needed for this move.

Remove the moved class from `TestDialogGateSkipGuards`' local tuple, and add
`TestLineInputDialogGateSkipGuards` beside the new gate, following
`tests/test_render_slider_dialog.py::TestSliderDialogGateSkipGuards`: verify the
gate's real skip flag and simulate each missing tool on disposable classes with
`probe_gate_skip`, without starting a GUI. Update the original module's routing
docstring and skip-guard comment. Add the new module to `_GATE_FILES` in both
`tests/test_dialog_gate_count_prose.py` and `tests/test_readme_render_gates.py`.
Update the line-input gate anchor in `docs/rendering.md` and `docs/invariants.md`,
and add the new skip-guard anchor to the invariant row that lists dialog guards.
Check `docs/fidelity.md`, `tests/test_ci_workflow.py` and
`tests/support/validation_gaps/*.py` for moved anchors; change any that name the
old location. Production tools, theme assets and render geometry stay outside
this extraction.

**Acceptance criteria.**
- Discovery finds `TestLineInputDialogRender` in the new module and no definition
  in the old module; its existing pixel assertions retain their inputs and
  expected values. The original gate module is below 800 lines.
- With a required dialog tool absent, or a software renderer forced, the moved
  gate skips. The new guard tests run without a capture and detect a removed
  decorator or omitted tool requirement.
- Gate inventory and documentation checks still recognize the line-input gate;
  published file/class anchors resolve to its new location, and its measurement
  provenance remains beside the moved crops.
- Focused checks for the original and new gate modules, both gate-inventory
  suites and the invariant register pass (capability skips reported as such),
  followed by `make check`. Routine GUI work uses the existing isolated harness.

### Render units suite extraction: isolate general CLI argument validation (planned 2026-11-18 by the plan role)

**Goal.** Give the render CLI's general argument contract a focused test module,
reducing `tests/test_render_surface_units.py` independently of the waiting
line-input pixel-gate extraction. The pending readiness implementation owns
session behavior; this extraction stays within argument tests.

**Approach and files touched.** Create `tests/test_render_cli_arguments.py`
with `TestRenderCliArguments`. Move these methods from `TestArguments` in
`tests/test_render_surface_units.py`, preserving their fixtures and assertions:
`test_cli_delegates_validated_options_to_render_workflow`,
`test_cli_delegates_the_settle_and_timeout_to_the_workflow`,
`test_accepts_the_minimum_settle_and_timeout`,
`test_a_single_custom_dimension_keeps_the_other_default`,
`test_rejects_non_positive_and_non_plain_sizes`, `test_rejects_bad_durations`,
`test_rejects_a_timeout_not_longer_than_settle`,
`test_rejects_option_like_applet`, `test_rejects_empty_applet`,
`test_rejects_a_path_carrying_applet`, `test_applet_refusals_name_the_actual_defect`,
and `test_requires_an_output_path`. Give the new class the existing
`applet_problem` patch in `setUp`; leave the original class's patch for its
remaining dialog tests.

The local `assert_usage_error` is also used by the three-mode refusal test
that stays behind. Move its implementation to
`tests/support/render_cli_cases.py::assert_usage_error(case, *argv)` and keep
thin class wrappers in both classes, so neither test module imports the other.
Update that support module's routing prose and recheck its helper caller-count
docstrings across the new and existing modules. Remove unused imports from
the original module and update its routing docstring. Update the moved method
anchors in `docs/invariants.md` (CLI delegation and applet refusal rows).
Search `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py` and
`tests/support/validation_gaps/*.py` for additional moved anchors and update
matches. Production tools, dialog-mode cases and session-script cases are
outside this plan.

**Acceptance criteria.**

- Unittest discovery finds the named general argument cases under the new
  class, without duplicate definitions in the original class. Their existing
  inputs and expected outcomes survive the move.
- Valid default and custom dimensions, settle and timeout values still reach
  the mocked workflow with the asserted parsed values. Invalid dimensions,
  durations, applet ids and missing output still return usage status 2 with
  the existing diagnostic checks. These tests launch no render session.
- The original dialog argument tests, including the three-mode diagnostic
  case, still run; the two modules can be selected independently. Published
  file/class/method anchors resolve to the moved cases.
- Focused checks for both argument modules and the invariant register pass,
  followed by `make check`. No GUI probe is needed for this extraction.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

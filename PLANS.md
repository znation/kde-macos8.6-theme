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

### Render-session readiness: the client writes RENDER_SESSION_READY_FILE once its window is shown (planned 2026-11-16 by the bugfix role)

**Needs review 2026-11-17 by feature: plan defect — the approach is superseded by QUESTIONS.md (answered 2026-11-17, "Let's go with your recommendation"). The answered design is a KWin-side settle script that reports the mapped window over D-Bus to a listener the session shell starts, and the listener touches the ready file; the "Remaining work" below still says each client touches the file, and the answer requires a probe on this host before any code. The entry has no files-touched list or acceptance criteria for the listener design. Plan role: rewrite this entry to the answered design, with the probe as its first step.**

**Goal.** Make the render settle end on a real client readiness signal, as the user chose
(option 2, QUESTIONS.md 2026-11-16). The session side is in place: `tools/render_session.py::session_script`
exports `RENDER_SESSION_READY_FILE` (`<capture>.ready`) before the client starts and ends the settle
early once the file exists, with the settle budget as the ceiling. Nothing writes the file yet, so
every session still waits its full settle.

**Remaining work (client side, one launch path per change).** Each client that a render starts must
touch `$RENDER_SESSION_READY_FILE` once its window is shown: the ksplashqml `--test` client (splash
mode), the plasmashell applet/desktop path, and the inactive-dialog wrapper. Each path needs a test
that stubs the readiness write, and a bounded real-session run to confirm the signal fires. Sibling of
the BUGS.md entry "Render-session tests rely on fixed wall-clock budgets" (which stays open until
these land).

### Render dialog gates suite extraction: isolate the slider dialog gate (planned 2026-11-17 by the plan role)

**Goal.** `tests/test_render_dialog_gates.py` is still over 1000 lines. Its `TestSliderDialogRender`
gate (about 40 lines) and the two `SLIDER_DIALOG_*` constants with their measurement comments (about
20 lines) pin one surface: the Kvantum slider that `--slider-dialog` renders. Move them into their own
module, as the text-box and progressbar extractions did (PLANS-DONE.md, "isolate the text-box scrollbar
gate"; the progressbar extraction is feature commit 2fc36e0, waiting to merge). This plan moves a
different class but edits the same gate tuple, docstring list, `_GATE_FILES` tuples and doc rows as
that change, so implement it against main after 2fc36e0 has merged, and keep its edits to those lines.

**Approach.**
- Create `tests/test_render_slider_dialog.py`, shaped like `tests/test_render_textbox_dialog.py`. Its
  module docstring says it holds the `--slider-dialog` thumb and trough gate, that the shared capture
  plumbing lives in `tests/support/render_gates.py`, and that the other kdialog widget gates live in
  `tests/test_render_dialog_gates.py`. Move these verbatim: the comment block that starts "The rendered
  Kvantum slider thumb in the slider dialog", `SLIDER_DIALOG_THUMB_CROP`, the trough comment,
  `SLIDER_DIALOG_TROUGH`, and the `@dialog_gate_guard()` class `TestSliderDialogRender`. At the base
  commit, the class body uses only `DialogGate` (its `assert_cell_matches` and `assert_band`),
  `dialog_gate_guard` and `unittest`. Re-check that list against the moved text before you write the
  imports.
- Add `TestSliderDialogGateSkipGuards`, modeled on `TestTextboxDialogGateSkipGuards`, with the method
  `test_the_slider_dialog_gate_skips_only_when_a_tool_is_absent`. It asserts that
  `TestSliderDialogRender.__unittest_skip__` equals the expected skip state: a software renderer is
  detected, or a `DIALOG_REAL_TOOLS` tool is missing from `PATH`. It then re-runs
  `probe_gate_skip(dialog_gate_guard, missing)` for `None` and for each tool. So the module also
  imports `shutil`, `DIALOG_REAL_TOOLS`, `probe_gate_skip` and `software_renderer_skip_reason`. End
  the module with the `if __name__ == "__main__": unittest.main()` footer.
- In `tests/test_render_dialog_gates.py`, delete the moved block and class. Drop
  `TestSliderDialogRender` from the gate tuple in
  `TestDialogGateSkipGuards.test_the_widget_dialog_gates_skip_only_when_a_tool_is_absent`, and extend
  that tuple's trailing comment to name the new module. Add the new module to the module docstring's
  list of sibling modules. Delete any import that no remaining code uses (check each with `grep -w`).
- Add `"tests/test_render_slider_dialog.py"` to `_GATE_FILES` in both
  `tests/test_dialog_gate_count_prose.py` and `tests/test_readme_render_gates.py`.
- Update the anchors:
  - `docs/invariants.md`: in the slider dialog row, which today cites
    `tests/test_render_dialog_gates.py::TestSliderDialogRender`, cite
    `tests/test_render_slider_dialog.py::TestSliderDialogRender` and keep the method names. The
    "fifteen dialog render gates" skip-guard row and the software-renderer skip row both cite the
    per-module skip-guard tests. Append
    `tests/test_render_slider_dialog.py::TestSliderDialogGateSkipGuards::test_the_slider_dialog_gate_skips_only_when_a_tool_is_absent`
    to each. Leave the gate counts alone, because the gate set does not change.
  - `docs/rendering.md`: in the `--slider-dialog` paragraph, point the gate cite at the new path.
  - `docs/fidelity.md`: in the dialog-gate list, take `::TestSliderDialogRender` out of the
    `tests/test_render_dialog_gates.py` chain. Give it as a full
    `tests/test_render_slider_dialog.py::TestSliderDialogRender` token, as the text-box entry is.
  - `tests/test_ci_workflow.py` names the gate only by class in a comment, so leave it. Grep
    `docs tests tools README.md BUGS.md QUESTIONS.md` again, including
    `tests/support/validation_gaps/*.py`, for `test_render_dialog_gates.py::TestSliderDialogRender`,
    and rewrite any other anchor that turns up. Do not rewrite PLANS-DONE.md or BUGS-FIXED.md.

**Files touched.** `tests/test_render_slider_dialog.py` (new), `tests/test_render_dialog_gates.py`,
`tests/test_dialog_gate_count_prose.py`, `tests/test_readme_render_gates.py`, `docs/invariants.md`,
`docs/rendering.md`, `docs/fidelity.md`.

**Acceptance criteria.**
- Unittest discovery lists both `TestSliderDialogRender` methods exactly once each, under
  `test_render_slider_dialog.TestSliderDialogRender`. Neither appears under `test_render_dialog_gates`.
  Every other class in `tests/test_render_dialog_gates.py` keeps its methods.
- During the run, the moved class's `ast.dump` matches the original's at this plan's base commit, and
  the two constants' values match. This is a one-time check, not a committed test.
- On a host without `kdialog`, or under `LIBGL_ALWAYS_SOFTWARE=1`, the new guard test passes and both
  `TestSliderDialogRender` methods report as skipped. With every tool present, the guard test passes
  and the gate runs. The guard test fails if the `@dialog_gate_guard()` decorator is removed from the
  moved class.
- `grep -rn "test_render_dialog_gates.py::TestSliderDialogRender" docs tests tools README.md` prints
  nothing. `grep -n "SLIDER_DIALOG\|TestSliderDialogRender" tests/test_render_dialog_gates.py` prints
  only the comment that points to the new module. The invariants anchor check, the dialog-gate count
  prose test and the README render-gate test pass in `make check`.
- `tests/test_render_dialog_gates.py` shrinks by at least 55 lines, and the new module stays under
  about 130 lines. `make check` passes after the final edit.

### Render units suite extraction: isolate the desktop and splash argument checks (planned 2026-11-17 by the plan role)

**Goal.** `tests/test_render_surface_units.py` is still over 1100 lines, and its `TestArguments` class
is about 500 of them. `TestArguments` has 14 methods covering the two modes whose client is a fixed
plain command instead of `kdialog`: `--desktop` (`plasmashell`) and `--splash` (`ksplashqml`). They
run from `test_cli_delegates_the_desktop_capture_size` through `test_the_help_text_names_the_splash`
and are about 108 lines. Move them into their own module. This follows the earlier units extractions
(PLANS-DONE.md, "isolate the CLI applet preflight checks"). The module-level helpers they call are
shared with the dialog-mode methods that stay, so move those helpers into a support module instead of
importing from one test module into another. This plan does not touch `tests/test_render_dialog_gates.py`
or any file the waiting slider extraction edits, so the two can merge in either order.

**Approach.**
- Create `tests/support/render_cli_cases.py`. Give it a docstring saying it holds the shared
  `render_surface.main` argument assertions for the per-mode CLI tests. Move these module-level
  functions into it verbatim, docstrings included: `delegated_render_args`,
  `assert_delegated_capture_size`, `assert_rejects_applet_with_fixed_client`,
  `assert_rejects_capture_size_with_fixed_client`, `assert_two_mode_refusal_names_both`,
  `assert_dialog_requires_kdialog` and `assert_help_lists_flag`. Their bodies use `mock`,
  `render_surface`, `call_main`, `_call_capturing` and `assert_missing_tool_named`. Import those from
  `unittest`, `tools` and `support.cli_fixtures`, and re-check that list against the moved text. Each
  docstring's call-site count ("Seven call sites", "Thirteen tests", …) counts callers across both
  test modules. After the move, recount with `grep -c` over both modules and correct any count that
  no longer holds.
- Create `tests/test_render_fixed_client_modes.py` with a docstring. It says the module holds the
  `--desktop` and `--splash` argument and preflight checks, that it was moved out of
  `tests/test_render_surface_units.py`, that the dialog-mode argument checks stay there, and that the
  splash client argv is pinned in `tests/test_render_splash_client.py`. Add the class
  `TestFixedClientModeArguments(unittest.TestCase)` with a copy of `TestArguments.setUp`, which pins
  `render_surface.applet_problem` off. Move the 14 desktop and splash methods into it verbatim, with
  their comments. Import the helpers from `support.render_cli_cases`, along with
  `assert_missing_tool_named` and `render_surface`, plus whatever else the moved bodies use. Add the
  `from support import repo_root` path setup and the `unittest.main()` footer. These tests patch
  `render` and start no session, so the class needs no skip guard.
- In `tests/test_render_surface_units.py`, delete the moved helpers and methods. Import the helpers
  the remaining `TestArguments` methods use from `support.render_cli_cases`. Delete any import that
  no remaining code uses, checking each with `grep -nw`. Extend the module docstring's sibling list
  to name `tests/test_render_fixed_client_modes.py` for the desktop and splash argument checks.
- Update the anchors in `docs/invariants.md`. In the `--desktop` row, cite
  `tests/test_render_fixed_client_modes.py::TestFixedClientModeArguments::test_cli_delegates_the_desktop_capture_size`
  in place of the `test_render_surface_units.py::TestArguments` one. In the `--splash` row, cite
  `...::test_cli_delegates_the_splash_capture_size` the same way. Leave the `render_surface keeps
  parsing and preflight` row alone, because its method stays. Then grep `docs tests tools README.md
  BUGS.md QUESTIONS.md`, including `tests/support/validation_gaps/*.py` and
  `tests/test_ci_workflow.py`, for each of the 14 moved method names and the 7 helper names, and
  rewrite any other anchor that turns up. Do not rewrite PLANS-DONE.md or BUGS-FIXED.md.

**Files touched.** `tests/support/render_cli_cases.py` (new), `tests/test_render_fixed_client_modes.py`
(new), `tests/test_render_surface_units.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Unittest discovery lists each of the 14 desktop and splash methods exactly once, under
  `test_render_fixed_client_modes.TestFixedClientModeArguments`, and none under
  `test_render_surface_units`. Every other `TestArguments` method, plus `TestCapturePaintCheck` and
  `TestSessionScript`, is still listed under `test_render_surface_units`.
- During the run, each moved method's `ast.dump` and each moved helper's `ast.dump` with its
  docstring removed match the originals at this plan's base commit. This is a one-time check, not a
  committed test.
- Running `python3 -m unittest test_render_fixed_client_modes` from `tests/` passes on its own, with
  no display and with `plasmashell` and `ksplashqml` absent from the host. Breaking the desktop mode's
  default settle (30 s) or the splash mode's 640x400 capture size in `tools/render_surface.py` makes
  that module fail.
- `grep -n "desktop\|splash" tests/test_render_surface_units.py` finds no `def test_` line, and
  `grep -rn "test_render_surface_units.py::TestArguments::test_cli_delegates_the_\(desktop\|splash\)" docs tests tools`
  prints nothing. The invariants anchor check passes in `make check`.
- Each helper docstring's call-site count equals the number of call sites a `grep` over the two
  modules finds.
- `tests/test_render_surface_units.py` shrinks by at least 190 lines, and each new file stays under
  about 160 lines. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

# Plans

Planned features, written by the plan role and implemented by the feature role.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Render CLI tests: move the environment-isolation cases into their own module (planned 2026-11-19 by the plan role)

**Goal.** `tests/test_render_failure_paths.py` is 1011 lines, and PRINCIPLES.md asks for files
small enough to read in one sitting. Its module docstring says it covers the render CLI's failure
paths, but `TestFailurePaths` also holds seven tests that check what the render session takes
from the caller's environment and what it drops. They are not failure paths. This plan moves them
unchanged into a new `tests/test_render_environment.py`. No tool behavior and no test body
changes. It is independent of the Firefox test move, the stylesheet series and the GTK parser
brace-pairing move, and touches none of their files.

The seven tests to move, keeping their names and order:
`test_session_receives_the_geometry_and_the_themed_configs`,
`test_session_ignores_a_config_search_path_from_the_environment`,
`test_session_pins_the_nested_bus_to_a_display_free_qt_platform`,
`test_session_script_keeps_the_clients_on_the_nested_compositor_platform`,
`test_install_ignores_a_destdir_from_the_environment`,
`test_install_ignores_makefiles_from_the_environment`,
`test_install_ignores_a_destdir_from_the_outer_make_command_line`. The test just before them,
`test_make_render_passes_a_dash_leading_output_as_a_path`, covers argument passing and stays.

**Approach and files touched.**

- New `tests/support/render_stub_tools.py`:
  - Move `class StubTools` verbatim from `tests/test_render_failure_paths.py`, with its
    `setUp`, `stub`, `assert_scratch_removed` and `assert_failed_run`.
  - Move `TestFailurePaths.run_main` up onto `StubTools` verbatim. Both suites call it, and per
    L4 shared helpers go to `tests/support/` rather than one test module importing another.
  - Write a module docstring naming both suites as its users.
  - Import only what the moved code uses: `os`, `shutil`, `stat`, `tempfile`, `unittest`,
    `Path`, `mock`, `repo_root` (the sys.path side-effect import), `call_main` from
    `support.cli_fixtures`, and `render_surface` from `tools`. Confirm each with grep.
  - `assert_failed_run`'s docstring says "Shared by the 18 failure-path tails in
    :class:`TestFailurePaths`". None of the moved tests call it. Recount the
    `self.assert_failed_run(` call sites in `tests/test_render_failure_paths.py` with grep and
    write that count, naming the module. As of this plan grep finds 22 call lines, so the 18 is
    already stale. Do not keep a number grep does not confirm.
  - The module is not a `test_*.py` file, so the runner does not collect `StubTools` on its own.
- New `tests/test_render_environment.py`:
  - Module docstring: it pins what the render session inherits from and drops from the caller's
    environment (display sockets, `XDG_CONFIG_DIRS`, `QT_QPA_PLATFORM`, `DESTDIR`,
    `MAKEFILES`, `MAKEFLAGS`) against the same shell stubs. The failure paths stay in
    `tests/test_render_failure_paths.py`.
  - `class TestRenderEnvironment(StubTools)` holds the seven methods verbatim, in their current
    order.
  - Give it the `if __name__ == "__main__": unittest.main()` footer.
  - Import only what the bodies use. As of this plan that is `os`, `unittest`, `Path`, `mock`,
    `repo_root`, `render_session` from `tools`, and `StubTools`. Confirm each with grep.
- `tests/test_render_failure_paths.py`:
  - Delete `StubTools`, `run_main` and the seven methods.
  - Import `StubTools` from `support.render_stub_tools`. `TestFailurePaths(StubTools)` and its
    remaining bodies stay unchanged.
  - Drop the imports nothing left uses. As of this plan that includes `render_session`, and
    probably `tempfile`. Check each import with grep, and keep anything still referenced
    (for example by `TestMissingTool`).
  - In the module docstring, add one sentence pointing the environment-isolation cases at
    `tests/test_render_environment.py`.
- `docs/invariants.md`: rewrite each of these anchors from
  `tests/test_render_failure_paths.py::TestFailurePaths::<name>` to
  `tests/test_render_environment.py::TestRenderEnvironment::<name>`:
  - the `XDG_CONFIG_DIRS` row ("The render session resolves configuration only from its
    scratch data and config homes");
  - the `MAKEFILES` row ("The render session drops caller `MAKEFILES`");
  - the both-anchors row that begins "The render session pins its whole nested
    `dbus-run-session` bus subtree".

  Leave the other `TestFailurePaths` anchors alone.
- `tests/support/validation_gaps/unclear_invariant.py` (`render-config-search-path`) and
  `tests/support/validation_gaps/real_run_needed.py` (`nested-session-portal-crash-loop`):
  rewrite their `TestFailurePaths` anchors for the moved methods to the new module and class.
  The `crashed-applet-setup-wait` entries in `slow_check.py` and `real_run_needed.py` and the
  class-level `TestFailurePaths` anchors in `no_repro.py`, `unclear_invariant.py` and
  `real_run_needed.py` name tests that stay, so leave them unchanged.
- Per L1/L3, also grep `docs/rendering.md`, `docs/fidelity.md`, `tests/test_ci_workflow.py`
  and `tests/support/validation_gaps/*.py` for the seven moved method names. As of this plan,
  the only hits outside the test file are the invariants rows and the two validation-gap entries
  above. None of the moved tests is a `Test*DialogRender` gate, so the `_GATE_FILES` lists do not
  apply. Archives (PLANS-DONE.md, BUGS-FIXED.md) keep their historical anchors.

**Acceptance criteria.**

- `tests/test_render_environment.py::TestRenderEnvironment` defines the seven listed tests with
  the bodies they had in `TestFailurePaths`. None of the seven names is still defined in
  `tests/test_render_failure_paths.py`.
- The union of `test_*` method names across the two modules equals the set the original
  `tests/test_render_failure_paths.py` defined, with nothing lost or duplicated.
  `tests/test_render_failure_paths.py` is under 860 lines (`wc -l`).
- `grep -n '^class StubTools' tests/test_render_failure_paths.py` prints nothing, and
  `tests/test_apply_theme.py`'s own `StubTools` is unchanged.
- No anchor for any of the seven moved names still points at `tests/test_render_failure_paths.py`
  in `docs/` or `tests/support/validation_gaps/`, and the invariants-anchor and
  validation-gap tests pass.
- `assert_failed_run`'s docstring count matches the number of call sites grep finds in the
  module it names.
- No file under `theme/` or `tools/` changes, and the `Makefile` does not change.
- `make check` passes after the final edit, and its run includes the new module's tests.

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

**Size drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; merged-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role; merged-series narration trimmed 2026-11-11 by the
steward role; measurements refreshed 2026-11-18 by the steward role; stylesheet-source status
refreshed 2026-11-19 by the steward role):** PRINCIPLES.md asks
each file to stay small enough to read in one sitting. Current `wc -l` measurements include
`theme/gtk/.../gtk-3.0/gtk.css` (7111), `gtk-4.0/gtk.css` (6523), Firefox
`userChrome.css` (1581) and `userContent.css` (941). Among the tests,
`test_render_file_dialog.py` is 1336 lines and `test_gtk_theme_views.py` is 1142;
the two queued GTK 3 extractions split declarations out of the views module.
`test_render_surface_units.py` is 527 lines after its dialog-argument and capture-paint
extractions, and `test_gtk_theme.py` is 331 lines. Those two render extractions and the
measured list-row fixture extraction are archived in PLANS-DONE.md; they no longer queue
render-suite work here. The GTK sheets and Firefox stylesheets remain single-file theme
artifacts, now built from source partials concatenated into one shipped sheet as chosen
(QUESTIONS.md, answered 2026-11-14; GTK 3, GTK 4 and Firefox source splits are archived in
PLANS-DONE.md). This note queues no stylesheet work and changes no behavior.

### Render CLI: separate option construction and mode resolution (planned 2026-11-19 by the organize role)

**Goal.** Reduce the mode-policy responsibilities concentrated in
`tools/render_surface.py::main`. The 351-line CLI module is more than twice the current
161-line production Python median, and `main` currently builds the parser, applies
mode-specific defaults and conflicts, chooses capture dimensions, and resolves required
tools before dispatching the existing render workflow.

**Approach and files.** Add `tools/render_surface_options.py` for the parser-facing
responsibilities: move `_seconds`, `_applet`, the capture/default constants, and the
mode-option handlers that construct the parser, resolve mode combinations and sizing,
and derive the mode's required client tools. Expose a small public entry point that
returns the validated namespace (with `parser.error` retaining the CLI's usage behavior)
and its requirements. Keep `main` in `tools/render_surface.py` as orchestration: obtain
validated options, perform missing-tool, applet-package and output checks, then call
`render`. Keep execution and session lifecycle in `tools/render_workflow.py` and its
existing collaborators. Update the CLI tests and any live module references in
`docs/`, `tests/`, and `README.md`; keep direct-script and package imports working.

**Acceptance criteria.**

- Existing CLI tests pass unchanged in behavior for defaults, each render mode, mode
  conflicts, invalid sizes and timing, missing tools, missing applet, and output errors.
- Direct invocation and package imports preserve the same usage diagnostics and exit
  codes; `render_surface.py` remains the documented executable path.
- The new options module owns parser and mode-resolution policy, while render lifecycle
  code remains in the existing workflow module; no rendering behavior or theme files
  change.
- Grep finds no stale references to moved private names, and `make check` passes after
  the final edit.

### Cursor artifact tests: isolate vector text and hand pins (planned 2026-11-19 by the plan role)

**Goal.** Make the vector I-beam and pointing-hand artifact contract readable in a
focused module instead of inside `tests/test_cursors_theme.py`. This is independent
of the waiting GTK extractions and changes test organization only.

**Approach and files.** Move `TestVectorPointerArtifacts`, including its design-point
docstring, `EXPECTATIONS`, helper methods and test bodies, to
`tests/test_cursors_vector_artifacts.py`. Keep its class and method names. Extract
the shared `PACKAGE`, `CURSORS`, `SIZES`, `HOTSPOTS`, `BLACK`, `WHITE`, `TRANSPARENT`,
`_pixel` and `_read_cursor` definitions into a new
`tests/support/cursor_artifact_cases.py`; both test modules import what they use.
Keep the full literal hotspot table together, preserving its independent expected
values rather than deriving them from production art. Move the `xcursor_reader`
import with `_read_cursor`; the independent reader remains `support.xcursor`.
Keep `_scaled`, `_repo_bytes` and the remaining cursor-set fixtures in the original
module. The new test module also imports `unittest` and `tools.png.decode_rgba`.
Update the original module's opening docstring to locate the vector-pointer pins.
Update the cursor-set row in `docs/invariants.md` to point its
`TestVectorPointerArtifacts` anchor at the new module. Search `tests/`, `docs/`
and `README.md` for other live references to the moved class and methods, including
comments in `TestCursorSet`; historical plan records stay historical. No test module
imports another test module. Leave `support/cursor_theme_fixtures.py` focused on
staging installed themes.

**Acceptance criteria.**

- Normal discovery and a focused run of `test_cursors_vector_artifacts` execute the
  moved class; `test_cursors_theme` no longer defines it.
- The retained fixtures check xterm hotspots `(7,7)`, `(11,11)`, `(15,15)` and hand2
  hotspots `(7,2)`, `(10,3)`, `(14,4)` at sizes 16/24/32. They still pin the existing
  black and white design points, opaque hotspots, transparent corners and partly
  covered edge pixels. Opaque intermediate grey remains required for xterm at 24
  and hand2 at each nominal size.
- The moved assertion bodies and fixture values survive relocation without semantic
  edits; the remaining arrow and cursor-set tests still discover and pass. Production
  tools and shipped cursor files have no diff.
- The invariant register resolves the moved anchor, and `make check` passes after
  the final edit.

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

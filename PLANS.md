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
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
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
Charcoal-style body face and selected by the global theme for the general, menu, toolbar,
smallest-readable and window-title fonts, and monospaced text keeps the user's fixed font;
a Chicago-style menu face (part 2/3 of the font series) remains unplanned because its
redistribution licence is unresolved, and Lato is the only family the package installs.
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

### Platinum GTK 4 slider: pin the rendered trough band, transparent fill and raised thumb with an offscreen pixel probe (planned 2026-11-11 by the plan role; independent of the waiting GTK 4 push-button entry — that entry adds its `test_button_faces_render` probe beside `tests/test_gtk4_theme.py`'s landed rendered probes and appends one end-of-table `## gtk` row to `docs/invariants.md`, while this entry adds its own probe beside the same landed probes and appends one end-of-table `## gtk` row to the same table — the two share no test method, no pinned widget and no README sentence, though both touch `tests/test_gtk4_theme.py`'s rendered-probe region and `docs/invariants.md`'s `## gtk` table tail, so whichever merges later re-reads the file's probe region and the table tail before writing; at implementation re-grep every anchor this entry names)

**Goal.** The GTK 4 sheet's slider recipe — `scale > trough` (the `#EEEEEE` band, `background-image: none`, 1px `#000000` border, `border-radius: 0`, the `inset 1px 1px #999999` inset shadow, `min-height: 6px`/`min-width: 6px`), `scale > trough > fill, scale > trough > highlight` (the transparent fill and highlight faces, `border: 0`, no shadow), and `scale > trough > slider` (the `#DDDDDD` thumb face, 1px `#000000` border, zero radius, the raised `inset 1px 1px #FFFFFF, inset -1px -1px #999999` bevel, the `-5px` thumb margin that overhangs the band, `min-width: 12px`/`min-height: 16px` horizontal) — is pinned today only by declaration checks (`tests/test_gtk4_theme.py::TestGtk4Theme::test_scale` and the neighbouring scale declaration tests; the `support.gtk_theme_spec` constants `SCALE_TROUGH`, `SCALE_EMPTY_FILL`, `SCALE_THUMB` and `SCALE_SLIDER` spell the groups). A GTK-side regression — a trough rule that never matches the rendered node tree, a thumb that never paints or loses its bevel, stock's accent-coloured highlight leaking through the landed transparent fill — would ship green, unlike the GTK 4 progress meter whose rendered probe (`test_progressbar_faces_render`) already pins pixels. The suite's landed GTK 4 rendered probes (`test_mixed_indicators_draw_black_dashes`, `test_spin_field_renders_the_mirrored_etch_in_rtl`, `test_notebook_tab_faces_render`, `test_progressbar_faces_render` in `tests/test_gtk4_theme.py`) prove the child-interpreter route works, and no rendered probe of a `Gtk.Scale` exists (a grep over the file finds no scale construction in any child program), and a grep of PLANS.md and PLANS-DONE.md finds no entry carrying one — the landed scale records cover marks allocation, value ink and selected-row rims only, all by declaration.

**Approach and files.**

1. `tests/test_gtk4_theme.py`: add `TestGtk4Theme::test_scale_faces_render` beside `test_progressbar_faces_render`, the landed meter probe's shape: `require_gui_opt_in()` first (`tests/support/gui_tests.py`), then a child interpreter subprocess with `GDK_BACKEND=x11` and `GSK_RENDERER=cairo` that imports `gi` with `Gtk` 4.0 (exit 77 when introspection or an X11 display is missing, mapped by the parent to a skip naming what is missing), loads the shipped sheet's bytes into a `Gtk.CssProvider` at priority 801 with the `'../assets/'` URL rewrite the landed probes use, sets the stock theme name to Adwaita the way the mixed-indicator probe does, then builds a `Gtk.Window` holding two horizontal `Gtk.Scale`s built from a `Gtk.Adjustment` (lower 0, upper 100, value 50) with `set_draw_value(False)` and `set_size_request(120, -1)` — one resting, the second wrapped in a `set_sensitive(False)` holder so the `:disabled` state propagates the way the meter probe's disabled bar does — pumps the main context until both are allocated, snapshots each scale with `Gtk.WidgetPaintable` at the widget's own allocation, renders it through `renderer.render_texture` into a pixbuf with the same deadline loop and failure reporting as the meter probe, and asserts each pinned pixel as a literal tuple at positions derived from the fresh allocations (the child program reads the trough's and slider's `get_allocated_width()/get_allocated_height()` plus their `get_allocation()` origins and computes every coordinate from those, exactly as the meter probe derives its pins; assert the node tree's `trough`/`slider` css names the way the meter probe asserts its own). The plan states no absolute coordinates. Pin, per resting scale, the discriminating positions each clear of antialiasing edges: the thumb interior centre expecting the `#DDDDDD` face, the thumb's top border row expecting `#000000`, the thumb's top interior row expecting the `#FFFFFF` bevel arm, the thumb's bottom interior row expecting the `#999999` bevel arm, a trough interior row left of the thumb and one right of the thumb each expecting `#EEEEEE` (the landed fill and highlight are transparent, so a stock accent-coloured fill or highlight leaking through fails either side), the trough's top border row expecting `#000000`, and the trough's top interior row right of the thumb expecting the `#999999` inset-shadow arm. The disabled scale repeats the shared trough band/border pins and pins the thumb's flat disabled twin (`scale > trough > slider:disabled`: the `#DDDDDD` face with the 1px `#999999` border and no bevel): the thumb's top border row expecting `#999999` — not `#000000` — and the thumb's former bevel-arm rows expecting `#DDDDDD`, so a disabled twin that kept the raised bevel or the black rim fails. Every expectation comes from the landed recipe and the palette constants already imported in `tests/test_gtk4_theme.py` (`FACE`, `BLACK`, `WHITE`, `GREY`, `TROUGH` — re-grep the import list before writing and add only what is missing), never from a capture's own pixels. The pressed state stays out: the landed `scale > trough > slider:hover, scale > trough > slider:active` group repaints the same face, border and raised bevel as the resting thumb, so pressed pins would be byte-identical and add nothing discriminating — the declaration test holds the spelling. The probe imports no GTK in the suite process (the `tests/test_no_gtk_introspection.py` guard pins that) and mentions no brand or toolkit name.
2. `docs/invariants.md`: append one dated (2026-11-11) end-of-table `## gtk` row naming the new probe: a plain horizontal GTK 4 slider paints the landed `#EEEEEE` trough band with its `#000000` border and `#999999` inset arm, keeps the landed transparent fill and highlight, and paints the raised `#DDDDDD` thumb with its black rim and white/`#999999` bevel, the disabled thumb keeping the landed `#999999` flat rim and no bevel; recording the missing reference surface (no collected screenshot in `macos8.6-screenshots/` shows a GTK slider — the GTK scope's standing adaptation premise), the value sources (the sheet's landed `scale > trough`, fill/highlight, slider and disabled-thumb groups and the platinum palette constants), and that the probe runs under the opt-in guard through the child interpreter, establishing rendered pixels only where GTK 4 introspection and an X display are present, as the landed declaration rows never have.

**Files.** `tests/test_gtk4_theme.py` (one probe beside the landed rendered probes), `docs/invariants.md` (one appended end-of-table `## gtk` row). No sheet change, no production tool change, no render-harness change, and no other GTK 4 widget is touched.

**Acceptance criteria.**

- `make check` stays green where GTK 4 probes are not runnable: without `PLATINUM_RUN_GUI_TESTS=1` the new probe raises the same skip as the landed probes, and where GTK 4 introspection or a display is missing despite the opt-in, the child exits 77 and the probe skips with its own reason — the hosted job keeps today's behavior.
- Where GTK 4 introspection and an X display are present with `PLATINUM_RUN_GUI_TESTS=1`, the child completes and every pinned pixel reads its literal tuple: the resting scale's `#DDDDDD` thumb face, `#000000` thumb rim, `#FFFFFF` and `#999999` thumb bevel arms, `#EEEEEE` trough band on both sides of the thumb, `#000000` trough rim and `#999999` trough inset arm; the disabled scale's `#999999` thumb rim, `#DDDDDD` flat thumb arms and unchanged trough band and rim. Deleting or weakening any landed scale rule — the trough band, a trough arm, the fill/highlight transparency, the thumb face, the thumb rim or a raised bevel arm, or the disabled thumb's flat grey rim — changes at least one pinned pixel and fails the probe.
- The landed neighbouring probes (`test_progressbar_faces_render`, `test_notebook_tab_faces_render`, `test_spin_field_renders_the_mirrored_etch_in_rtl`, `test_mixed_indicators_draw_black_dashes`) and the scale declaration tests (`test_scale`, `test_scale_focus_outline_color`, `test_scale_focus_transition`) pass unchanged, the no-GTK-in-suite guard passes, and `make check` passes after the final edit.

## Done

### Reference-pixel sampler: select named colors in scanline runs (planned 2026-11-03 by the plan role) — done 2026-11-03 by the feature role

**Goal.** Isolate known border and stripe shades in a reference crop while retaining their separate equal-color runs. The current run report filters lengths, while named inclusion is limited to histograms; source and related finished-plan searches found no named run selection. This feature is independent of the waiting histogram plan.

**Approach and files.** Add repeatable `--run-color RRGGBB` in `tools/sample_arguments.py::build_parser`, destination `run_colors`, default None, using `tools/sample_validators.py::rgb_argument`. In `option_error`, immediately after the maximum-run-length dependency check, require `--runs` with diagnostic `--run-color requires --runs`. In `tools/sample_report_runs.py::_runs_result`, build a set of requested RGB tuples once and intersect membership with the existing length predicates on completed `_color_runs` records. Selection ignores opacity, but segmentation still uses RGB or RGBA according to `--alpha`; retain separate adjacent runs of different selected colors. Preserve the report schema, traversal order and absolute coordinates. Add `tests/test_sample_runs_colors.py` using `CliTestCase` and fixture patterns from `tests/test_sample_runs_max_length.py::TestSampleRunsMaximumLength`; extend `tests/test_sample_option_validation.py::TestSampleOptionValidation`. Document the flag beside the run length filters in README.md and amend the scanline-run row in docs/invariants.md. These six files form one bounded change of a few hundred lines including tests; decoding and search-mode diagnostics remain outside scope.

**Acceptance criteria.**
- For a crop at (2,1) containing successive pixels A,A,B,B,B,A,C,C, where A=`010203`, B=`090807`, C=`040506`, selecting A emits starts (2,1) and (7,1) with lengths 2 and 1. Selecting A and C also emits (8,1) with length 2, in scan order. Adding minimum length 2 removes the singleton A; maximum length 1 retains only that singleton. Omitted B never joins the A runs. Selecting adjacent distinct colors retains their individual run records.
- Repetition, lowercase and optional `#` give the same selection. An absent color yields JSON `runs: []` and text with image, region and axis lines but no run lines or added metadata. Selecting the complete crop palette matches the unfiltered report. Literal expected records cover an offset nonsquare rectangle in both axes, inferred single-column traversal, an explicit vertical singleton, crop-edge runs and equal colors on adjacent scanlines that remain separate. Text and JSON agree; direct-script and package invocations agree; omitting the flag retains existing fixtures.
- For adjacent RGBA pixels (1,2,3,0), (1,2,3,128), (4,5,6,255), selecting `010203` yields one length-2 run in RGB mode and two length-1 runs with their original alpha bytes in alpha mode. Minimum length 2 in alpha mode yields an empty list, proving segmentation precedes selection and length filtering. An RGB-only fixture reports alpha 255 when requested.
- Missing and malformed values exit 2 with empty stdout. Valid use outside runs mode, including ordinary samples, histogram and find-color modes, exits 2 with `--run-color requires --runs` before image access; guard `os.open`, `read_png_size` and `read_png` in validation tests. Earlier incompatible-option diagnostics retain precedence. Help lists the repeatable option and the absent parser default is None. Run `make check` after final edits.

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

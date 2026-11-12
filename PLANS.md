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

### README render-gate prose: align the menu-dialog sentence with the landed TestMenuDialogRender gate (planned 2026-11-03 by the plan role; eligible — nothing else in ## Planned is implementable, all three entries above carry Refused notes, so this entry needs no queue comment; it touches no GTK, Kvantum, Firefox or tool file the archive's recent entries touch)

**Goal.** The README's `make render` paragraph still describes the dialog-gate family as it stood before the 2026-11-03 item-view pin landed: the `--menu-dialog` sentence claims "no gate compares its rendered border runs yet (BUGS.md tracks adding that pin alongside the dialog-gate coverage work)", but that exact pin was fixed 2026-11-03 (the item-view record in `BUGS-FIXED.md`) and the landed gate is `tests/test_render_surface.py::TestMenuDialogRender` with `test_item_view_frame_matches_its_measured_border_runs`, `test_current_item_focus_ring_is_pinned_inside_the_field` and `test_draws_the_item_view_frame_and_white_interior` (pinned in `docs/invariants.md`'s dialog rows). The later "Validating the reference set" paragraph likewise names only `TestCheckboxDialogRender` and `TestComboboxDialogRender` as the suite's dialog runs, and the `tests/test_ci_workflow.py` comment block above `test_workflow_installs_and_verifies_the_plasma_render_tools` says "the two dialog gates (TestCheckboxDialogRender and TestComboboxDialogRender)" where three dialog gates now depend on the `kdialog` client. A reader following the README instead of the code is told the gate is missing, so the documentation asserts a state that landed three work-logs ago.

**Approach and files.**
1. In `README.md`'s `make render` paragraph, replace the `--menu-dialog` sentence's trailing "no gate compares its rendered border runs yet (BUGS.md tracks adding that pin alongside the dialog-gate coverage work)" with a clause naming the menu-dialog gate `tests/test_render_surface.py::TestMenuDialogRender` and stating, in README's own prose style, that it pins the engine-drawn item-view frame's measured border runs (`#999999` outer top/left against `#000000` inner and `#FFFFFF` outer bottom/right), the white interior and the current-item focus ring at the same 480x360 capture, and that the measured provenance is `docs/invariants.md`'s dialog row ("no direct reference crop; pixels measured in the fixed 480x360 KWin capture").
2. In `README.md`'s "Validating the reference set" paragraph, extend the parenthetical suite list to `(`tests/test_render_surface.py::TestCheckboxDialogRender` and `::TestComboboxDialogRender` and `::TestMenuDialogRender`)` and widen the widget summary from "the engine-drawn check box cell ... and the engine-drawn combo arrow ..." to cover the menu item-view frame and focus ring as well.
3. In `tests/test_ci_workflow.py`, in the comment block above `test_workflow_installs_and_verifies_the_plasma_render_tools`, change "the two dialog gates (TestCheckboxDialogRender and TestComboboxDialogRender)" to name all three dialog gates, leaving the six-tool verification list and assertions untouched (the menu client `tools/render_clients.py::menu_dialog_client` already opens that same `kdialog`).
4. Add `tests/test_readme_render_gates.py`: a stdlib `unittest` module that reads `README.md` through `support.containment.read_text`, extracts every token matching `tests/[A-Za-z0-9_]+\.py::[A-Za-z_]+`, and asserts for each that the named module file exists under `tests/` and that the class name appears in that module's text — so a README gate reference can never again name landed work that is not there. Add one direct assertion that the README's dialog-gate sentence names `TestMenuDialogRender`, so this specific stale claim is pinned, not just guarded in general. (No README test exists for these backtick references today: `tests/test_readme_commands.py` covers `make` targets and `tools/*.py` scripts, `tests/test_readme_references.py` covers the screenshot table — this closes the `tests/…::TestClass` reference gap the staleness slipped through.)

**Acceptance criteria.** Reading README's `make render` paragraph shows the menu dialog named as gated by `TestMenuDialogRender`, and neither README paragraph nor any prose a reader follows from it still asserts the gate is missing or points at the cleared item-view bug record as open — that is verified by the new `tests/test_readme_render_gates.py`, which also fails when a README `tests/<module>.py::Test<Name>` token names a module absent from `tests/` or a class not in that module's text, including a version of the old stale sentence any future edit reintroduces. The existing README suites (`tests/test_readme_commands.py`, `tests/test_readme_theme_files.py`, `tests/test_make_help.py`) stay green because the edit changes no target, tool path, shipped-asset name or command output. Run `make check` after the final edit.

### Split the 6622-line tests/test_gtk4_theme.py into per-surface suites (planned 2026-11-11 by the organize role; ordering clause — this entry queues behind the three waiting GTK 4 rendered-probe entries (push button, slider, scrollbar) and must land after all three, since each appends a probe to `tests/test_gtk4_theme.py`'s rendered-probe region and an end-of-table `## gtk` row to `docs/invariants.md`, and writing their anchors into the per-surface suites once beats churning them twice; at implementation re-grep every anchor this entry names)

Needs review 2026-11-11 by feature: too large for one run

**Goal and cost.** `tests/test_gtk4_theme.py` is the repository's largest file by a wide margin — 6622 lines, ~6400 of them the single `TestGtk4Theme` class holding 249 test methods over every GTK 4 surface (header bar, OSD, notebook, scrollbar, calendar, spin field, …), with the inline child-interpreter probe programs (the `subprocess.run([sys.executable, "-c", '''…'''])` blocks near lines 164–780) embedding whole GTK programs as string literals inside one method. Every new GTK 4 probe appends to this one file: the three queued probe entries all target its rendered-probe region, `docs/invariants.md` pins ~217 references to the file, and the queued entries' independence clauses already coordinate merge order around "the file's probe region and the table tail" — evidence that one file is now a shared edit point where merges queue on each other. A 249-method grab-bag class also hides which surface a method covers. The split is not a one-run move: the reference updates alone (invariants table, queued-entry anchors) are large, so it is planned rather than started.

**Target structure.** Designed up front; no assertion, expected value, probe pixel or child-program byte changes — only module placement, class composition and imports move.

1. `tests/support/gtk4_sheet.py` (new): the file's shared GTK 4 fixture state — the parsed shipped-sheet handle, `DEFINED_COLOURS` (the palette-derived defined-colour map at lines 86–117), `SCALE_FOCUS`/`SCALE_SLIDER`, `_rgb` — and one base class `Gtk4SheetRuleCases` (subclassing `support.gtk_rule_cases.GtkSharedControlCases`) whose `setUpClass` parses the shipped `gtk-4.0/gtk.css` once, exactly as `TestGtk4Theme` does today.
2. `tests/test_gtk4_rendered_probes.py` (new): the rendered-probe methods (`test_mixed_indicators_draw_black_dashes`, `test_spin_field_renders_the_mirrored_etch_in_rtl`, `test_notebook_tab_faces_render`, `test_progressbar_faces_render`, and the queued entries' three probes as they land) move whole, each child program kept as it is written today. The identical child-program prelude each probe repeats (the gi/Gtk 4.0 import block, exit-77 guard, provider load at priority 801 with the `'../assets/'` URL rewrite, Adwaita switch) moves once into `tests/support/gtk4_probe.py` as a helper the probe methods call to assemble their child source; only the byte-identical prelude lines are extracted, never a per-widget pin.
3. Per-surface declaration suites: `tests/test_gtk4_<surface>.py`, each `class TestGtk4<Surface>(Gtk4SheetRuleCases, unittest.TestCase)`, partitioning `TestGtk4Theme`'s remaining 243 declaration methods by the surface each asserts (the leading widget token of the test name: headerbar, osd, notebook, scrollbar, calendar, scale, spin, button, check, radio, …), grouped so no module exceeds roughly one sitting (~800 lines); a method names exactly one module, moves unchanged, and keeps its method name. `TestGtk4Theme` disappears — no half-moved state: every method lands in a suite, and `tests/test_gtk4_theme.py` is deleted at the end.
4. The file's three trailing classes move into the matching surface suites: `TestScrollbarBreadthRules` and `TestScrollbarBreadthReference` into the scrollbar suite, `TestCalendarDisabledGreyReference` into the calendar suite.
5. Reference updates in the same change: every `tests/test_gtk4_theme.py` reference in `docs/invariants.md` (~217), `PLANS.md`, `PLANS-DONE.md`, `README.md`, `tests/test_no_gtk_introspection.py`, `tests/support/gtk_theme_spec.py` and `tests/support/gtk_child_probe.py` is repointed at the module and class the named test landed in; `tests/test_no_gtk_introspection.py`'s no-GTK-in-suite guard is extended to cover every new `tests/test_gtk4_*.py` module.

**Files.** New: `tests/support/gtk4_sheet.py`, `tests/support/gtk4_probe.py`, `tests/test_gtk4_rendered_probes.py`, the per-surface `tests/test_gtk4_*.py` suites. Deleted: `tests/test_gtk4_theme.py`. Updated: `docs/invariants.md`, `PLANS.md`, `PLANS-DONE.md`, `README.md`, `tests/test_no_gtk_introspection.py`, `tests/support/gtk_theme_spec.py`, `tests/support/gtk_child_probe.py`. No production tool, sheet, render-harness or GTK 3 change.

**Acceptance criteria.**

- The split changes no behavior: the full test-set union before and after is identical (same method names, same assertions, same skips; the GUI-guarded probes skip identically without `PLATINUM_RUN_GUI_TESTS=1`), and `make check` passes after the final edit.
- A grep over the repository (source, tests, docs) finds no remaining `tests/test_gtk4_theme.py` reference: the file is gone and every invariants-table row names the module the test landed in.
- Each per-surface suite is under roughly one sitting and imports its parse only from `tests/support/gtk4_sheet.py`; the probe suite's child programs carry the extracted prelude and no duplicated prelude line remains across the seven probe methods (a diff of the extracted prelude against each original block shows only the moved lines).
- The queued probe entries' independence clauses and the invariants table tail read true after the split; if one of the three probe entries is still unlanded at implementation time, this entry is behind it and waits.

### README sampler option reference: add direct navigation by output family (planned 2026-11-11 by the plan role)

**Goal and grounding.** Make the long `### Sampling options` reference navigable when a contributor already knows which output family they need. It currently spans pixel output, histograms, color searches and scanline runs without intervening headings. The finished sampling recipe-table entries cover choosing a command; the finished navigation entries cover README workflows. Neither supplies destinations within this option reference. This documentation task is independent of the pending quiet fidelity option and GTK suite split.

**Approach and files.** Edit README.md only, adding a compact four-link list immediately under `### Sampling options` and four level-four headings: `Pixel and rectangle samples` before the ordinary pixel introduction, `Histogram options` before the paragraph beginning `Pass --histogram` (the flag is backticked in the source), `Color search options` before the paragraph beginning `Pass --find-color`, and `Scanline run options` before the paragraph introducing `--runs` after the longest-match-column-run explanation. Link the list to those four headings using same-document fragments. Keep each family's existing paragraphs and examples in their present order, retaining the `#sampling-options` destination and the earlier Choosing a sampling mode table. Limit the diff to navigation links, headings and whitespace, roughly twenty added lines. No runtime code, new test, dependency or invariant change is needed; existing `tests/test_readme_links.py::TestReadmeLinks.test_local_links_resolve` checks fragment destinations and `tests/test_readme_commands.py::TestReadmeCommands` checks referenced commands. `tools/sample_arguments.py::build_parser` is the CLI evidence anchor, not an implementation target.

**Acceptance criteria.**

- From Sampling options, a reader can jump directly to pixel/rectangle, histogram, color-search or scanline-run documentation; each link lands immediately before that family's introductory paragraph, outside code fences.
- Existing `#sampling-options` links still resolve, the task-selection table remains available, and a diff shows no changed commands, example outputs or option semantics.
- Run `make check` after the final edit; the README fragment and command checks pass. Review heading placement manually because a resolvable fragment alone does not establish that it precedes the correct family.

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

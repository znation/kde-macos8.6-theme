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
2026-10-29 by the steward role):** The
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

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows). The
`userContent.css` sheet now styles surfaces within six internal pages:
about:downloads, about:config, about:preferences, about:support, about:networking
and about:telemetry. These include preferences navigation and controls, support
tables and buttons, and telemetry navigation, tables and histograms; this is
surface coverage, not a claim of complete page theming. The opt-in profile install
copies this sheet alongside `userChrome.css`. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._ (Only the standing scope-drift note above; the entries below wait in the queue.)

### Kvantum scrollbar dialog render gate: pin a captured kdialog text box's scrollbar handle and trough on the shipped art recipe (planned 2026-11-10 by the plan role; the same CLI-plumbing files as the waiting progressbar-dialog entry ahead of it, a further widget surface — the two entries share no assertion region and may merge in either order, so at implementation re-read the landed mode lists and re-grep every anchor this entry names)

**Goal.** No render gate captures the Kvantum engine's rendered `QScrollBar`: a change to the shipped `scrollbarslider` frame tiles, the `[Scrollbar]`/`[ScrollbarSlider]`/`[ScrollbarGroove]` sections of `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` (`scroll_width=16`, `scroll_arrows=true`, `frame.element=scrollbarslider` with 2px margins, `indicator.element=grip` at size 13, a `slider`-element groove) or Kvantum's scrollbar drawing would ship green. A `kdialog --textbox <file>` dialog (the flag exists; verified on this host, and a probe capture in this session's scratch shows the scrollbar rendering) opens a real themed text view with a vertical `QScrollBar` in the isolated headless session, giving the missing surface. No collected reference screenshot shows a dialog with a scrollbar, so the comparison surfaces are the shipped art recipe: the raised 16x16 `scrollbarslider` arrangement `tests/test_kvantum_svg.py` pins by element id (flat #DDDDDD face, #FFFFFF top/left arms, #999999 bottom/right arms, 1px #000000 outline), the `slider` element interior `[ScrollbarGroove]` draws as the trough (flat #EEEEEE face with its 1px #000000 outline), the `grip` element's three #000000 bars the handle's 13px indicator paints, and the `arrow` element faces the `scroll_arrows=true` buttons paint. The dialog is byte-deterministic at rest: the client reads a plain scratch text file, the scrollbar rests at value zero, so value zero disables the up arrow (its triangle paints the disabled #999999 `arrow` state, the same disabled tint the pinned `comboarrow-*` families use) while the bottom arrow stays enabled in the normal #000000 state, and no hover, press or focus byte enters any crop. The reference screenshots stay out of the gate code, exactly as the landed menu-dialog gate does.

**Approach and files.** In `tools/render_clients.py` add `textbox_dialog_client(session)` beside `slider_dialog_client`: it writes a fresh plain-text scratch file (enough numbered lines, count chosen on the implementation host so the resting handle is tall enough to carry the full grip indicator and still leaves a visible trough band below it) under a path inside the session the context manager already removes, and returns `kdialog --title Test --textbox <that path>`; its docstring records the at-rest reasoning above. In `tools/render_surface.py` add a mutually exclusive `--textbox-dialog` flag into the existing `dialog_flags` tuple and the `kdialog_flags` tuple, rejecting `--width`, `--height` and a non-default `--applet` and fixed at 480x360 like the other dialog modes; include the flag in the help text. In `tools/render_workflow.py` import the new client in both the package and the direct-run import blocks and extend the `dialog` OR-chain and the client dispatch beside `slider_dialog`. In the `Makefile` `RENDER_MODE` case add `textbox-dialog) set -- --textbox-dialog ;;` beside the `slider-dialog` branch and extend both enumeration error strings. In `tests/test_render_surface.py` add unit cases beside the landed dialog-mode cases (mutually exclusive with the other dialog flags and the calculator surface, missing-tool naming names kdialog, `--help` names the mode, `test_only_dialog_renders_add_kdeglobals_to_the_session_configs` reads unchanged) and extend `TestDialogGateSkipGuards`' gate tuple in `test_all_dialog_gates_skip_only_when_a_tool_is_absent` with the new class, aligning its docstring's mode counts. Model the gate class `TestTextboxDialogRender` on `TestSliderDialogRender` (same `_DialogGate` base, prerequisite and software-renderer-guard skips): measure the window origin and crops from two consecutive full `--textbox-dialog` captures on the implementation host that agree byte for byte under `cmp`, and record both measured-crop dates in the class comment the way the landed crops' comments do. Pin six bands: (a) one trough-interior crop below the handle, clear of the handle's bevel and the trough's outline rows, expecting the flat #EEEEEE `slider` interior face with no outline byte inside; (b) one top-edge band and one left-edge band over the resting handle's border, each expecting the 1px #000000 outline with the #FFFFFF raised arm inside it; (c) one bottom-edge band over the handle expecting the #999999 arm inside the #000000 outline, so swapping the bevel arms' highlight and shadow fails; (d) one grip band across the handle's middle expecting the `grip` element's three #000000 bars on the #DDDDDD face, so a dropped `grip` indicator fails; (e) one band over the top arrow button expecting the disabled #999999 up-triangle rows on the button's raised #DDDDDD face, so an always-enabled arrow fails; and one band over the bottom arrow button expecting the enabled #000000 down-triangle rows on the same raised face, so a one-tint arrow pair fails. README's dialog-mode enumeration sentences (the command list, the `RENDER_MODE` list, the dialog descriptions and the capture table's dialog rows) collect the new mode to whatever count and wording the landed state shows at implementation (the waiting progressbar entry also extends those sentences); docs/invariants.md's `## tooling` table gains one dated (2026-11-10) end-of-table row naming the gate's tests, the missing dialog-scrollbar reference surface and the shipped-art value sources above.

**Acceptance criteria.**

- `python3 tools/render_surface.py --textbox-dialog out.png` and `make render RENDER_MODE=textbox-dialog out.png` reach the same argv; using the new flag with any other dialog flag or the calculator surface, or with `--width`/`--height`/a non-default `--applet`, exits 2 before installing; a missing kdialog is named as the first missing tool; `--help` and the Makefile's RENDER_MODE enumeration name the new mode.
- When the documented render prerequisites are present and the software-renderer guard is quiet, two consecutive full `--textbox-dialog` captures agree byte for byte under `cmp`, and the gate's six pinned bands match the expected pixels: the trough below the handle paints the flat #EEEEEE arrangement with no outline byte inside, the handle's top-edge and left-edge bands paint the #000000 outline with the #FFFFFF raised arm, the handle's bottom-edge band paints the #999999 arm inside the #000000 outline, the grip band paints the three #000000 bars over the #DDDDDD face, the top-arrow band paints the disabled #999999 triangle rows and the bottom-arrow band paints the enabled #000000 triangle rows, each over its raised #DDDDDD button face. The gate skips cleanly when its tools are missing or the software-renderer guard triggers, so `make check` passes with today's skip behavior on the hosted job.
- The gate code reads no reference screenshot and mentions no brand or library name (the landed sheet-level conventions); the invariants row records the measured-capture provenance and the value sources. `make check` passes after the final edit.

## Done

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

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


### Inactive-window gate, part 2/2: pin the rendered unfocused window's decoration pixels in `TestInactiveDialogRender` (planned 2026-11-11 by the plan role; completes the two-part series whose part 1/2 landed 2026-11-11, so no allocator dependency clause remains — the landed part 1/2 plumbed the two-window `--inactive-dialog` capture and its `kwinrulesrc` rules and recorded the regions for this gate in `tests/test_render_window_rules.py` and the `## tooling` invariants row; independent of the waiting applet-preflight entry — that entry edits `tools/render_surface.py`'s preflight and `_applet`, `tools/render_applet.py` (new), `tests/test_render_applet.py` (new), `tests/test_render_surface_units.py`, README's prerequisites/`### Rendering a candidate`/troubleshooting rows and a `## tooling` table-tail row, while this entry edits `tests/test_render_surface.py`'s gate scaffolding (`_Renders.KINDS`, a new gate class, the count-bearing docstrings), `tests/test_dialog_gate_count_prose.py`'s number map, `tests/test_ci_workflow.py`'s count comment, README's dialog-gate enumeration and `docs/invariants.md`'s two count-bearing rows plus one new row appended directly after the landed 2026-11-11 part 1/2 row, deliberately not at the `## tooling` table tail so the two entries' table appends cannot collide — the two share no production file, no test module and no assertion and either merge order leaves all working; at implementation re-grep every anchor this entry names)

**Goal.** The landed two-window `--inactive-dialog` render has plumbing and a measured capture but no pixel gate: no assertion holds a running KWin to the shipped inactive decoration art — the flat buttonless `#DDDDDD` bar with its 1px `#555555` outline that `tests/test_aurorae_frame.py::TestDecorationSvg::test_inactive_frame_matches_reference` derives from `desktop_fandom.png`'s four unfocused windows and the `#777777` title ink `tests/test_aurorae_rc.py` pins against `org.macos8.desktoprc`'s `InactiveTextColor=119,119,119`. A regression that, say, resurrects flattened box art in the inactive bar, recolours the outline, resamples the field or paints the title in the active ink would pass every landed test. This part adds the gate the landed part 1/2 record promised.

**Grounding (measured fresh 2026-11-11 by the plan role, one full `python3 tools/render_surface.py <scratch>/dialog.png --inactive-dialog` run on this host, exit 0, 480x360 PNG).** The left (unfocused) window's frame occupies exactly `(4,8)`–`(227,351)` — position `(4,8)`, size `(224,344)`, matching `tests/test_render_window_rules.py::INACTIVE_GEOMETRY` — and its decoration structure on the capture is exactly: a 1px `#555555` outer ring around the whole rect (every border pixel measured `#555555`); a 1px `#555555` inner rectangle ring — the active frame's black client edge recoloured — with its top row y=29 and bottom row y=346 spanning x=9..222 and left column x=9 and right column x=222 spanning y=29..346; every pixel strictly between the two rings flat `#DDDDDD`; and the only non-`#DDDDDD` pixels in that between-rings region the centered title "Inactive window"'s glyph band, ink `#777777` spanning x=60..128 at y=14..23 (antialiasing bleeds one pixel around it; band x=58..130, y=13..24 contained all of it in the measured run), with the leftmost stem column x=60 fully `#777777` down y=14..23 — no box or button art anywhere in the bar. The right (focused) window's frame ring at `(252,8)`–`(475,351)` is 1px `#000000` with non-field pixels in its title bar, proving the capture really holds two states. These are session-measured platform values (KWin 6.3.6, Lato title font, kdialog 25.04.x) no reference screenshot shows; `tests/test_aurorae_frame.py` and `tests/test_aurorae_rc.py` are the art-side re-derivation the gate's constants point at.

**Approach.**

1. First re-verify the measurement: run two consecutive full `--inactive-dialog` renders on this host and `cmp` the two captures; only pin once they agree byte for byte (the landed color- and gtk-gate pattern). If the pair disagrees, or any region differs from the values above, stop and re-derive every region from the fresh capture — never pin an unstable value — and record the re-derivation in the test comments.
2. `tests/test_render_surface.py`: append `("inactive", ("--inactive-dialog",), "dialog.png")` to `_Renders.KINDS` after the `"gtk"` entry, and add `class TestInactiveDialogRender(_DialogGate, unittest.TestCase)` beside the landed gate classes with `KIND = "inactive"` and a docstring stating it pins the shipped inactive Aurorae decoration as KWin draws it on the unfocused left window, complements the landed art-side pins, and holds no client-widget pin (the message-box contents stay unpinned; the other dialog gates own widget pins). Its tests, reading the capture through the inherited `candidate_image`:
   - `test_left_window_outline_is_the_inactive_outline`: every pixel of `(4,8)`–`(227,351)`'s border ring equals `INACTIVE_OUTLINE` (`#555555`, `tests/support/platinum_palette.py`). The ring test also pins the forced placement: a moved or resized window no longer puts the ring on these coordinates.
   - `test_left_window_client_edge_is_the_recoloured_inner_rectangle`: the ring of the rect with corners `(9,29)` and `(222,346)` equals `INACTIVE_OUTLINE` — the active frame's black client edge recoloured, the same derivation `test_inactive_frame_matches_reference` pins in the art.
   - `test_left_window_field_is_the_flat_buttonless_bar`: every pixel of the frame rect that lies neither on the outer ring, nor on the inner-rectangle ring, nor strictly inside the inner rectangle, nor in the glyph band x=58..130 × y=13..24, equals `INACTIVE_FRAME_GREY` (`#DDDDDD`, `tests/support/aurorae_fixtures.py`). This kills flattened box art, a stray active bevel row and any resampling bleed in the bar; the glyph-band bounds sit in the test comments with the measured-run provenance.
   - `test_title_ink_is_the_inactive_text_colour`: the pixels `(60,14)`..`(60,23)` all equal `#777777`, quoted with its source — `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`'s `InactiveTextColor=119,119,119`, which `tests/test_aurorae_rc.py` already pins against the reference title-core samples. Do not byte-compare the full antialiased glyph set; the stem column is the ink's deterministic core.
   - `test_right_window_keeps_its_active_frame`: every pixel of `(252,8)`–`(475,351)`'s border ring equals `BLACK` (`#000000`), and the right window's title-bar band (rows y=9..28, x=253..474) holds at least one non-`#DDDDDD` pixel — the capture must carry two different states or the left-window pins prove nothing.
3. Count prose: `tests/test_render_surface.py`'s gate scaffolding docstrings and comments spell counts the prose test derives — update them for thirteen dialog gates and twelve kdialog modes (the `TestDialogGateSkipGuards` docstring and the `_dialog_gate_guard` docstring's tool lists, the `_DialogGate` docstring, and the `kdialog for the eleven kdialog modes` comment above the missing-client test); `tests/test_ci_workflow.py`'s install comment near its `kdialog` mention likewise; `docs/invariants.md`'s skip-guard row and software-renderer row move twelve→thirteen and eleven→twelve kdialog modes, and the skip-guard row's gate-class enumeration gains `TestInactiveDialogRender`; `tests/test_dialog_gate_count_prose.py`'s `_WORDS` gains `"thirteen": 13` (its counts derive from the live classes, so it fails until every count word moves).
4. `README.md`: extend the `make render` paragraph's dialog-gate enumeration with `::TestInactiveDialogRender` and one clause naming the two-window inactive capture (the `tests/test_readme_render_gates.py` completeness pin fails until the token lands).
5. `docs/invariants.md` `## tooling`: append one dated (2026-11-11) row directly after the landed part 1/2 inactive-window row, recording the gate's pinned structure (outer ring, inner recoloured client-edge rectangle, flat field, glyph-band ink), the two-run `cmp` identity, the region provenance (measured on this host's session, KWin 6.3.6), the constants the assertions re-derive from (`tests/test_aurorae_frame.py`, `tests/test_aurorae_rc.py`), and that the message-box client contents stay unpinned.
6. Optionally extend `tests/test_render_surface.py::TestRenderBudgets` with one test that the `inactive` kind's `_Renders.KINDS` flags carry no `--settle` (the dialog default budget governs), mirroring the landed applet-settle test.

**Files.** `tests/test_render_surface.py`, `tests/test_dialog_gate_count_prose.py`, `tests/test_ci_workflow.py`, `tests/test_render_window_rules.py` (only if a region re-derivation must update the recorded comment values), `README.md`, `docs/invariants.md`. No production tool changes: `tools/render_surface.py`, `tools/render_dialogs.py`, `tools/render_clients.py`, `tools/render_workflow.py` and the `Makefile` stay untouched.

**Acceptance criteria.**

- On this host the thirteen dialog render gates (the twelve landed ones plus `TestInactiveDialogRender`) all run under `make check`'s gate pass: `TestInactiveDialogRender` renders `--inactive-dialog` at the 480x360 dialog defaults, exits 0, and its five region tests pass against the pinned values; the two-run `cmp` identity recorded in the row's provenance holds at implementation time.
- A host missing any of the five Plasma tools or `kdialog` skips all thirteen dialog gates with the shared skip-guard reason (the landed skip-guard tests pass unchanged in shape), and the count-prose test passes with every count word at thirteen dialog gates and twelve kdialog modes.
- Every landed gate class, the applet render gate and their unit tests compare unchanged; `_Renders.KINDS` gains exactly one entry; README's enumeration and the two invariants rows name the new gate; `make check` passes after the final edit.

## Done

### Fidelity CLI: extract parser construction from comparison orchestration (planned 2026-11-02 by the plan role) — done 2026-11-11 by the feature role

**Goal and grounding.** Make the fidelity entry point readable as a comparison workflow. `tools/fidelity.py::main` currently starts with parser construction and a nested `worst_pixel_limit` validator before it reads images. `tools/fidelity_arguments.py` already owns the other argument validators. The finished report-extraction plan deliberately retained parser setup in the entry point; heading searches found no separate parser-extraction plan. This maintenance task is independent of the queued sampler work.

**Approach and files.** Create `tools/fidelity_cli_parser.py::build_parser`, moving the existing `EscapingArgumentParser` construction and option declarations there without changing their order, help strings, defaults, destinations or types. Move `worst_pixel_limit` to `tools/fidelity_arguments.py` and import the validators into the new parser module. In `tools/fidelity.py::main`, replace the construction block with `build_parser().parse_args(argv)` and remove imports made unused by the move. Support package imports and direct-script execution using the existing conditional import pattern. Keep image reads, crop application, optional diagnostic scans and reporting in their current owners. Inspect repository references to validators imported through `tools.fidelity` before removing those imports; preserve an existing consumer's import path if needed. Bound the change to those three production files and a new `tests/test_fidelity_cli_parser.py`; adjust ownership docstrings in the touched files. No CLI behavior change or new dependency is intended.

**Acceptance criteria.** Before moving declarations, capture characterization fixtures in the new test module for normalized help text and parsed default/explicit namespaces, including both crops, diagnostic switches and combined budgets. The same fixtures pass after extraction. Use the existing unittest framework to verify two independently constructed parsers work, malformed crop/budget/worst-pixel arguments retain status 2 and escaped diagnostics, and help and invalid arguments do not call `tools/fidelity.py::_read_source`. Existing fidelity CLI, JSON, crop and direct-script tests continue to pass. Run `make check` after final edits. This structural change adds no guarantee to docs/invariants.md; its existing tooling contracts remain the acceptance boundary.

### Reference-pixel sampler: cap the vertical color-match interval report (planned 2026-11-04 by the plan role) — done 2026-11-04 by the feature role

**Goal.** Bound noisy `--find-color --match-column-runs` output while retaining full-region measurements. Source and archive-heading searches found vertical length filters and counts, and horizontal output caps, but no vertical color-match interval cap. This complements the preceding horizontal-cap entry and can merge independently: the vertical filter and report blocks already exist.

**Approach and files.** In `tools/sample_arguments.py::build_parser`, add optional `--max-match-column-runs N`, default None, using `positive_int`; `option_error` requires `--match-column-runs`. In `tools/sample_report_search.py::_search_match`, slice the completed column-major list after both inclusive vertical length filters and add `match.omitted_column_runs` (eligible count minus emitted count) when the cap is explicit, including zero. In `report_search`, print `omitted matching column runs: N` immediately after the vertical list. Keep `tools/sample_match_runs.py::_MatchRuns` unchanged: its count and longest summary precede report filtering, and `finish` sorts by `(x,y)`. This bounds output, not segmentation memory. Add `tests/test_sample_match_column_runs_limit.py` using `CliTestCase` and the generated PNG pattern in `TestSampleMatchColumnRunsMaxLength`; document the flag beside vertical filters in README.md and extend the vertical-filter tooling row in docs/invariants.md. These five changed files constitute one run; pagination and collector optimization are outside this plan.

**Acceptance criteria.**

- For a 2x9 crop at absolute origin (2,1), column zero matches relative rows {0,2,3,5,6,7} and column one matches {8}. Cap 2 emits exactly `(2,1,1)` and `(2,3,2)` as `{x,y,length}` records with 2 omitted. Cap 3 adds `(2,6,3)` with 1 omitted, detecting a cap restarted per column. Maximum length 2 plus cap 2 emits the leading pair with 1 omitted; minimum length 2 plus cap 1 emits `(2,3,2)` with 1 omitted. Contradictory length cutoffs yield an empty list with zero omitted. Cap 4 or larger includes the bottom-flushed `(3,9,1)` and reports zero omitted; no matches produce an empty list with zero omitted.
- With summaries requested, count remains 7, column-run count remains 4 and longest column run remains `(2,6,3)` despite capping. Bounds, fraction, centroid, horizontal intervals, row/column diagnostics and coordinate paging match uncapped results. Include adjacent unequal RGB values accepted by tolerance and an exact-alpha rejection that splits an interval, checking literal capped records; stored RGB beneath alpha zero remains searchable. JSON and text expose the same prefix and omitted count. Without the option, neither the new member nor text line appears.
- Zero, negative, fractional, malformed, non-ASCII and missing caps exit 2 with empty stdout. A valid cap with `--find-color` but without `--match-column-runs` fails before reading a missing image and names the required flag. Help describes the dependency; direct-script and package output agree. README distinguishes interval count from pixel length and states filtering precedes capping; the invariant row names the new tests. `make check` passes after the final edit.

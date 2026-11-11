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

_None yet._

### Platinum GTK 3 menu scroll arrows: restate the stock arrow face family with the landed flat-button recipe and square the landed scroll-arrow glyph groups (planned 2026-11-11 by the plan role; independent of the waiting GTK 3 notebook-arrow entry — that entry appends ten `notebook > header > tabs > arrow` groups at the GTK 3 sheet tail, adds one test beside `test_notebook_tab_close_button_arms` in `tests/test_gtk_theme.py` and appends an end-of-table `docs/invariants.md` row while amending the flat-family row's stay-stock clause, while this entry adds four `menu > arrow` face groups at the sheet tail, extends the two landed glyph groups mid-sheet, adds one test beside `test_menu_scroll_arrows` in `tests/test_gtk_theme_views.py` and appends its own end-of-table row without touching any landed row — the two share no selector, no test file and no assertion, and whichever entry lands second re-reads the sheet tail and sits after the first's block; at implementation re-grep every anchor this entry names)

**Goal.** When a GTK 3 menu is too short to show all its items, its ends show scroll arrows whose CSS nodes spell `menu > arrow`, `.menu > arrow` and `.context-menu > arrow`. The landed glyph series redirected only `-gtk-icon-source` on the two top/bottom arms; every face and state claim stock makes on these nodes is still live. Probed fresh this run 2026-11-11 with `gresource extract /usr/lib/x86_64-linux-gnu/libgtk-3.so.0 /org/gtk/libgtk/theme/Adwaita/gtk-contained.css` (libgtk-3 3.24.49, the 2055-line extract): resource line 808 `menu > arrow, .menu > arrow, .context-menu > arrow` clears border, background-image, box-shadow, text-shadow and `-gtk-icon-shadow`, sets 16px minimums and 4px padding — and then closes with `background-color: #ffffff` after its own transparent face declaration, so the effective rest face is white; line 814 hovers to `background-color: #eaebeb`; line 816 backdrops to `background-color: #fcfcfc`; line 818 disables with `color: transparent` and transparent face and border; and the top/bottom arms (lines 810/812) add scroll-geometry margins, a 1px `#eaebeb` edge hairline and 5px top or bottom radii. A scrolling menu over the landed `#DDDDDD` paper therefore shows a white 5px-rounded tile per arrow, a grey hover wash and a near-white backdrop tile. The landed glyph groups cannot fix this (they declare only `-gtk-icon-source`), no archived record restates the arrow faces (the landed CSD-corners record names the `.context-menu > arrow` spellings only as a sweep exclusion), and no queued entry touches them. No collected reference screenshot in `macos8.6-screenshots/` shows a GTK scrolling menu — the standing GTK-scope adaptation premise — so the arrows take the landed flat-button recipe, introducing no new palette value; the GTK 4 sheet needs nothing (its header comment already records that GTK 4 scrolls menus inside a popover through no arrow node).

**Approach.**

1. `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: at implementation re-probe the resource with `gresource` under a scratch dir and quote the four face arms verbatim with their resource lines in one dated (2026-11-11) comment appended directly after whatever the sheet tail then ends with (today the landed `list row.activatable:disabled:selected …` block whose last declaration is `color: #888888`; re-read the tail before writing — if the waiting GTK 3 notebook-arrow entry has landed first, sit after whatever block it appended). Keep the landed sheet-comment vocabulary: name the resource as `gtk-contained.css in libgtk-3 3.24.49` (the sheet carries no `adwaita` substring — `tests/test_gtk4_theme.py::TestGtk4Theme::test_stands_alone`'s lowercase scan is the family precedent) and allow hex literals only inside the comment. Then four new groups, each the byte-equal stock comma spelling at equal specificity winning by later source order, each carrying exactly the declarations of the corresponding landed same-sheet flat-button group (the ten-group family beginning `button.flat {` and ending at `button.flat:disabled:active, button.flat:disabled:checked` — re-read that block before writing and copy its dictionaries byte-equal):
   - `menu > arrow, .menu > arrow, .context-menu > arrow` — the landed `button.flat` dictionary; no radius addition, because stock's base arm already squares itself (resource line 808 closes `border-radius: 0`);
   - `menu > arrow:hover, .menu > arrow:hover, .context-menu > arrow:hover` — the landed `button.flat:hover` dictionary; no `-gtk-icon-effect` addition, because stock's hover arm carries only the background colour (line 814);
   - `menu > arrow:backdrop, .menu > arrow:backdrop, .context-menu > arrow:backdrop` — the landed `button.flat:backdrop` dictionary (stock line 816);
   - `menu > arrow:disabled, .menu > arrow:disabled, .context-menu > arrow:disabled` — the landed `button.flat:disabled` dictionary (stock line 818).
   The dated comment records the exclusions with their reasons: stock's 16px minimums and 4px padding (line 808) and the top/bottom margins and `#eaebeb` edge hairlines (lines 810/812) stay inherited per-property as platform scroll geometry and kept-toolkit ink; stock's own `-gtk-icontheme("pan-up-symbolic")`/`pan-down` glyph claims on the top/bottom arms are already beaten by the landed groups' asset URLs, which stay where they are; and GTK 3 stock declares no checked, active or drop arm for menu arrows. Record too the one state-dependent consequence of the byte-equal dictionaries: in the disabled state the restated `border-color` wins the equal-specificity tie over the stock hairline's colour, while the hairline's width and style stay stock. Then extend the two landed glyph groups in place (the `menu > arrow.top, .menu > arrow.top, .context-menu > arrow.top` group and its bottom twin, at the sheet's menu block) with exactly one added declaration each, `border-radius: 0;`, squaring the 5px radii stock rounds at resource lines 810/812 per the landed square-corner policy; the icon URL declarations stay first in each dictionary and the radius joins the same dictionaries.
2. `tests/test_gtk_theme_views.py`: before writing, re-grep that no landed test sweeps the bare `menu > arrow` token. Then extend `TestGtkThemeViews::test_menu_scroll_arrows`'s two `assert_rule` dictionaries with `"border-radius": "0"`, and add `TestGtkThemeViews::test_menu_scroll_arrow_faces` beside it: for each of the four new triple spellings `self.assert_rule` with whole-dict equality over the exact declarations above and `self.selectors.count(selector) == 1`; a token sweep in the landed corner-bearing shape asserting the parsed selectors carrying the `menu > arrow` substring equal exactly the landed top triple, the bottom triple and the four new triples (nothing else in the sheet carries the substring); and one order pin that each of the four new base selectors parses after `self.selectors.index("menu > arrow.top")`, so a block inserted before the landed glyph block could not claim the tail's source-order wins. Extend no other landed assertion: the landed `test_menu_check_and_radio_are_boxless`, `test_icon_sources_resolve_to_shipped_files`, `test_icon_sources_point_at_shipped_assets` and the landed `menu` pins name their own selectors and never read these spellings.
3. `docs/invariants.md`: append one dated (2026-11-11) end-of-table `## gtk` row naming both tests and recording: the missing reference surface (no collected screenshot shows a GTK scrolling menu); the value sources (the landed flat-button dictionaries and the square-corner policy); the probed stock arms with resource lines, including the within-block declaration order that makes stock's effective rest face white; the kept-toolkit geometry and ink exclusions; and that declaration and source-order checks do not establish rendered pixels. No landed row is amended — menu arrows are not flat-family co-members.

**Files.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/test_gtk_theme_views.py`, `docs/invariants.md`.

**Acceptance criteria.**

- The GTK 3 sheet declares exactly the four new arrow groups appended at the sheet tail behind the dated comment, each with exactly its landed dictionary's declarations byte-equal and nothing more, and exactly one added `border-radius: 0` declaration in each of the two landed glyph groups; every other landed sheet rule is unchanged, and `test_stands_alone`, `test_only_palette_hex_literals` and `test_no_universal_selector` pass unchanged.
- `tests/test_gtk_theme_views.py::TestGtkThemeViews::test_menu_scroll_arrow_faces` passes and fails on a dropped group, a foreign value, a lost placement or a stray extra declaration; the extended `test_menu_scroll_arrows` pins the squared glyph dictionaries; `test_menu_check_and_radio_are_boxless`, `test_icon_sources_resolve_to_shipped_files`, `test_icon_sources_point_at_shipped_assets` and the landed menu face tests pass unchanged.
- `docs/invariants.md` carries the appended row with no landed row amended, and `make check` passes after the final edit.

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

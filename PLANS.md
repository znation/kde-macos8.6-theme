# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
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
Firefox's `tests/test_firefox_theme_*.py` modules check stylesheet declarations;
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
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows), and it now
reaches a content page: the `userContent.css` sheet paints the about:downloads
list (part 1/2), and its opt-in profile install as part 2/2 has also landed. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._

### Firefox Platinum content: paint about:telemetry's data payloads — the sections' tables, the histogram boxes and their bars and the copy and JSON-viewer buttons — with the landed table and push-button recipes (planned 2026-10-27 by the plan role; part 1/2, the about:telemetry furniture plan, is landed in PLANS-DONE.md, so its body, register and test class exist to extend; independent of the queued GTK places-sidebar plan — that one touches the GTK sheets and their suites, this one `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py` and `docs/invariants.md`)

**Goal.** The landed `about:telemetry` body paints only the page's furniture — the sidebar rows, the `#search` field, the `#stores` menu and the `#ping-picker` panel — so the sections' data payloads still paint stock: the JS-built tables keep Firefox's grey `--border-color` cell rules, the `.histogram` boxes keep the stock rounded grey-bordered box, each bar's `.bar-inner` keeps Firefox's accent-blue fill with its rounded rgba border, and the histogram `.copy-node` button and the raw payload's `#payload-json-viewer` button keep the stock in-content button paint. This plan appends the payload rules to the landed `about:telemetry` body — no new `@-moz-document` body, so the sheet's body-count assertion stays at six — reusing only values the sheet and test module already pin, so no new constant and no new hex is introduced and no landed rule changes. The home-section chrome stays Firefox's, as the landed part-1 grounding recorded.

**Verified facts (checked 2026-10-27 against the installed Firefox ESR 153.5.1's omnijar contents, scratch at `/tmp/tum-scratch-omz/omni`).** `aboutTelemetry.xhtml` builds every section inside `div#main.main-content`, each data section holding a JS-filled `div.data` (`#general-data`, `#environment-data`, `#session-info`, `#scalars`, `#keyed-scalars`, `#histograms`, `#keyed-histograms`, `#events`, `#simple-measurements`, `#slow-sql-tables`, `#addon-details`); `#raw-payload-section` holds `button#payload-json-viewer` and `pre#raw-payload-data`. `aboutTelemetry.js` builds the tables as bare `table` > `caption`/`tr`/`th`/`td` (`renderTable`, `renderAddonDetails`, `renderSlowSQL`) and each histogram as `div.histogram` (id = the probe name) wrapping `div.histogram-title`, `div.histogram-stats`, the bars and `button.copy-node`; each bar is `div.bar` (inline padding-top/height) wrapping `div.bar-inner`. `aboutTelemetry.css` paints the stock the plan must replace: `.histogram { border: 1px solid var(--border-color); background-color: var(--background-color-box); border-radius: 2px }`, `.bar-inner { background-color: var(--color-accent-primary); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 2px }`, `td { border-bottom: 1px solid var(--border-color) }` and `tr:not(:first-child):hover { background-color: rgba(0, 0, 0, 0.05) }`; `.copy-node`'s visibility/position and `.histogram:hover .copy-node { visibility: visible }` are geometry that stays stock, as do `.histogram`'s float/padding/min-height, `.bar`'s width/float/font, the caption/table font sizes and `.keyed-histogram`/`.sub-section` margins. `grep -c histogram` and `grep -c copy-node` return 0 for the sheet and the test module: nothing landed or planned covers the payloads, and the landed part-1 plan recorded exactly this scope as the later plan's subject.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot shows Firefox's about:telemetry (the same missing surface the landed telemetry row of `docs/invariants.md` records): the tables reuse the landed about:support/about:networking table arms byte-for-byte (the sunken white table field of `FIELD_RULE`, the `#EEEEEE` zebra of `TROUGH`, the raised `#DDDDDD` `th` band of `SUPPORT_TH_RULE`, the cleared cell borders of `SUPPORT_CELL_RULE`, the flat `#CCCCFF` `th:hover` of `BUTTON_HOVER_RULE`); the `.histogram` box reuses the landed `#ping-picker` panel values byte-for-byte (the sheet's white face and square `1px solid #000000` outline, no shadow); `.bar-inner` reuses the reference-grounded Platinum progress-bar fill — the flat `#CCCCFF` selection fill with `border: 0` and `border-radius: 0`, pinned by `tests/test_desktoptheme_progressbar.py::TestProgressBar` from `widgets/bar_meter_horizontal.svg` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the `.copy-node` and `#payload-json-viewer` buttons reuse the landed push-button recipe `BUTTON_RULE`/`BUTTON_HOVER_RULE` (grounded in `widgets/button.svg` and `aboutsystem_betawiki.png`, pinned by `tests/test_desktoptheme_button.py::TestButton` and `TestButtonReference`). The `.selected`-free class hooks (`histogram`, `bar-inner`, `copy-node`), the `#payload-json-viewer` id, the stock row hover (`rgba(0,0,0,.05)` left standing, as the networking landing leaves its own stock row hover standing) and `#raw-payload-data`'s stock black-on-white text (aboutTelemetry.css paints no `pre` colour and the page face is white) are Firefox-required; `#raw-payload-data` gets no rule.

**Sheet change.** Inside the landed `@-moz-document url("about:telemetry")` body, append after the landed `#ping-picker` rule, in this selector order (the comma-list cell arms restated before the header rule, as the landed bodies do):
- `.main-content table` = `FIELD_RULE`; `.main-content table tr:nth-child(2n)` = the zebra arm; `.main-content table th, .main-content table td` = the cleared cell arms; `.main-content table th` = `SUPPORT_TH_RULE`; `.main-content table th:hover` = `BUTTON_HOVER_RULE`.
- `.histogram` = the landed `#ping-picker` values (`background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #000000 !important; border-radius: 0 !important; box-shadow: none !important`).
- `.bar-inner` = `background-color: #CCCCFF !important; border: 0 !important; border-radius: 0 !important`.
- `.copy-node` = `BUTTON_RULE` and `.copy-node:hover` = `BUTTON_HOVER_RULE`; `#payload-json-viewer` = `BUTTON_RULE` and `#payload-json-viewer:hover` = `BUTTON_HOVER_RULE`.

Every rule carries `!important` like its landed siblings. In the sheet's header comment, append one provenance paragraph after the landed telemetry paragraph naming the payload provenance (no reference shows the page; the tables reuse the landed support/networking arms; the `.histogram` box reuses the `#ping-picker` panel; `.bar-inner` reuses the reference-grounded progress fill of `widgets/bar_meter_horizontal.svg` pinned by `TestProgressBar`; the buttons reuse `BUTTON_RULE`; the stock row hover, `#raw-payload-data`'s text and the copy button's reveal stay Firefox's).

**Test change.** In `tests/test_firefox_content_theme.py`, extend the telemetry register with the new selector constants (`TELEMETRY_TABLE = ".main-content table"` plus its zebra/th/td/hover arms, `TELEMETRY_HISTOGRAM = ".histogram"`, `TELEMETRY_BAR_INNER = ".bar-inner"`, `TELEMETRY_COPY`/`TELEMETRY_COPY_HOVER`, `TELEMETRY_JSON_BUTTON`/`TELEMETRY_JSON_BUTTON_HOVER`), extend `REQUIRED_TELEMETRY_RULES` and `TELEMETRY_SELECTORS` in the sheet order above, and then in `TestFirefoxTelemetryTheme`:
- `test_telemetry_rules_match_the_required_rules` and `test_parsed_rules_are_exactly_the_telemetry_rules` read the extended register unchanged.
- Extend `test_telemetry_rules_scope_to_page_furniture` with payload scope assertions: a `table` under `element("div", None, classes=("data",), parent=element("div", "main", classes=("main-content",)))` matches `TELEMETRY_TABLE` and its zebra/th/td/hover arms, a plain `table` outside `.main-content` matches none; `element("div", None, classes=("histogram",))` matches `TELEMETRY_HISTOGRAM` and its child `element("div", None, classes=("bar",))` matches none of them; a `bar-inner` child matches `TELEMETRY_BAR_INNER` and a bare `.bar` does not; `element("button", None, classes=("copy-node",))` matches `TELEMETRY_COPY` only with hover for the hover arm; `element("button", "payload-json-viewer")` matches `TELEMETRY_JSON_BUTTON` while `element("button", "other")` matches neither button arm.
- Extend `test_header_names_telemetry_provenance`'s token tuple with the payload tokens (".main-content table", ".histogram", ".bar-inner", ".copy-node", "#payload-json-viewer", "widgets/bar_meter_horizontal.svg", "TestProgressBar", "BUTTON_RULE").

`test_palette_is_exact`, `test_no_rule_paints_page_chrome` and `test_sheet_has_the_downloads_config_preferences_support_networking_and_telemetry_at_rules` stay unedited — the new rules use only the module-level palette set (`#FFFFFF`, `#000000`, `#DDDDDD`, `#CCCCFF`, `#EEEEEE`, `#999999`, `#AAAAAA`, `#888888`) and avoid every `FORBIDDEN_PAGE_CHROME` token.

In `docs/invariants.md`, in the `## firefox` table, append one row after the landed telemetry row before the trailing validation notes: the guarantee in one sentence — the about:telemetry body also paints the JS-built payload tables as the landed sunken white table field with the `#EEEEEE` zebra, the raised `#DDDDDD` header band, the flat `#CCCCFF` header hover and the cleared cell borders, the `.histogram` boxes as the white square black-outlined panel, each bar's `.bar-inner` as the flat `#CCCCFF` progress fill, and the histogram `.copy-node` and `#payload-json-viewer` buttons as the landed push buttons — with the test column naming `tests/test_firefox_content_theme.py::TestFirefoxTelemetryTheme`, `...::TestFirefoxContentTheme::test_palette_is_exact` and `...::test_no_rule_paints_page_chrome`, and the provenance cell naming the missing reference surface (no reference screenshot shows Firefox's about:telemetry), the reused byte-recipes and their pinned tests as the grounding paragraph names them, the omnijar probe and the rule that declaration checks establish no rendered pixels. Trim no landed row; `tests/test_invariants.py` (part of the check) parses the register.

**Acceptance criteria.**
- The landed `about:telemetry` body carries exactly the payload rules spelled above after the furniture rules; no landed rule's text changes; the sheet holds six `@-moz-document` bodies still.
- `TestFirefoxTelemetryTheme` (including the extended scope and provenance tests) passes, every landed content test keeps passing with no edits outside the named additions, and `TestFirefoxContentTheme::test_palette_is_exact`, `test_no_rule_paints_page_chrome` and the body-count test stay green unedited.
- The `## firefox` invariants table grows exactly one row and trims none; the full `make check` passes.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

## Done

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

### Firefox Platinum preferences radio groups: paint the panes' XUL radio buttons as the Platinum circle face with the shipped black dot (planned 2026-10-27 by the plan role; independent of the waiting Firefox Library toolbar-search plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite `tests/test_firefox_content_theme.py` versus `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py` and `tests/test_firefox_theme_library.py`), so either order merges; it is part 7 of the about:preferences series, whose parts 1 (category navigation rows), 2 (sidebar separators), 3 (page background and heading bands), 4 (search field), 5 (pane push buttons) and 6 (checkboxes) landed 2026-10-27 — the panes' entry fields and menulists are later parts that share this sheet and wait behind this one)

**Goal.** Part 6 left every XUL `radio` in the panes painting from `chrome://global/skin/classic/global/radio.css` (read 2026-10-27 from the installed `/usr/lib/firefox-esr/omni.ja`): `.radio-check` carries `appearance: auto; -moz-default-appearance: radio;`, so the disc renders as Firefox's modern non-native widget art, not this theme's circle. The square's size is already theme-agnostic: `chrome/toolkit/skin/classic/global/in-content/common-shared.css` puts `xul|*.radio-check` in the same rule as `.checkbox-check`, sizing it from `--checkbox-size` (16px through `design-system/tokens-shared.css` `--size-item-small`), while `radio.css`'s `@media (-moz-platform: linux)` sets `width/height: 1.3em` — the plan touches neither, so the box geometry stays Firefox's whichever sizer wins. `chrome/toolkit/content/global/elements/radio.js` appends a real light-DOM fragment (`image.radio-check` + `hbox.radio-label-box` holding `image.radio-icon` + `label.radio-label`), so an author sheet matches `.radio-check` directly. `chrome/browser/content/browser/preferences/preferences.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`) authors 11 XUL `<radio>` elements in 4 `radiogroup`s inside `#mainPrefPane` (the applications `saveForNewTypes`/`askBeforeHandling` pair, the ETP `standardRadio`/`strictRadio`/`customRadio` triple, the privacy-data recommendation pair and the three DoH radios) and 0 `<html:moz-radio>` shadow elements, so the paint reaches the whole radio population through the panes' light DOM. Paint the enabled radio as this theme's radio art — the Kvantum interior element `radio-normal` in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` (a 1px `#000000` circular ring over a `#FFFFFF` face — an unflat square: the art has no bevel, unlike `checkbox-normal`) — and, when the radio is selected, overlay the checked dot of `theme/desktoptheme/org.macos8.desktop/widgets/checkmarks.svg`'s `radiobutton` element, the black `r=3` circle centred in its 16x16 cell (pinned by `tests/test_desktoptheme_checkmarks.py::TestCheckmarks`), drawn centred because the dot SVG is 16x16. No reference screenshot shows Firefox's about:preferences; the ring/face/dot adapt the theme's own Kvantum and desktoptheme assets (a platform colour adaptation), with the 14x14 Kvantum cell scaled onto the 16px box and the dot taken 1:1 from the desktoptheme element. No hover rule: the reference's radio face does not change on hover and the Kvantum art ships no radio hover state. Disabled radios keep Firefox's whole paint (the `:not([disabled])` choice parts 5 and 6 made). The dot is inlined as a data-URI SVG whose black is written `rgb(0, 0, 0)` so the sheet gains no new hex literal and `TestFirefoxContentTheme::test_palette_is_exact` stays exact untouched.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the existing `@-moz-document url("about:preferences")` block, after the part-6 `#mainPrefPane checkbox:not([disabled])[checked] .checkbox-check` rule (which stays byte-unchanged), append two rules and nothing else — the block-end append point keeps the entry independently mergeable with the later parts of this series:

    #mainPrefPane radio:not([disabled]) .radio-check {
      appearance: none !important;
      background-color: #FFFFFF !important;
      border: 1px solid #000000 !important;
      border-radius: 50% !important;
    }

    #mainPrefPane radio:not([disabled])[selected] .radio-check {
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'%3E%3Ccircle cx='8' cy='8' r='3' fill='rgb(0, 0, 0)'/%3E%3C/svg%3E") !important;
      background-repeat: no-repeat !important;
      background-position: center !important;
    }

The selected-state predicate is `[selected]`, not `[checked]`: `radio.js`'s `inheritedAttributes` maps `"disabled,selected"` onto `.radio-check`, the attribute the `radiogroup` sets on the chosen item. The `#mainPrefPane radio` prefix scopes both rules to the panes (the `#dialogTemplate` overlay's radios stay Firefox's); the sheet ships no `@namespace` declaration, so the bare `radio` type selector matches the XUL-namespace elements exactly as the landed bare `checkbox` rule does, and the `.radio-check` descendant matches the light-DOM image `radio.js` appends. The dot URI is byte-pinned as written: single quotes inside the quoted `url()`, `%3C`/`%3E` for the angle brackets, `rgb(0, 0, 0)` for the pinned black, and `width='16' height='16'` with `background-position: center` so the dot centres whatever box Firefox sizes. The second rule adds only background longhands because the first rule also matches a selected enabled radio (it carries no `[selected]` predicate), so face, ring and `appearance: none` come from it. Geometry (the `--checkbox-size`/`1.3em` box, `radio.css`'s `radio` margins and the `.radio-label-box` offset), the label anatomy, the disabled `GrayText` colour and the `radiogroup:focus-visible radio[focused] > .radio-check` focus outline stay Firefox's; the shadow-DOM `html:moz-radio` elements (0 in the panes, verified 2026-10-27) and the dialog radios match neither selector and stay Firefox's.

Extend the header comment's about:preferences provenance with a radios paragraph inserted after the checkboxes paragraph and before the closing `*/`, naming: the two selectors and their declarations; the paint chain `chrome/toolkit/skin/classic/global/radio.css` (`appearance: auto`, `-moz-default-appearance: radio`, the linux `1.3em` media sizer), `chrome/toolkit/skin/classic/global/in-content/common-shared.css` (sizing the disc from `--checkbox-size` alongside `.checkbox-check`), `chrome/toolkit/content/global/elements/radio.js` (the light-DOM fragment that gives `.radio-check`, and the `[selected]` inherited attribute) and `chrome/browser/content/browser/preferences/preferences.xhtml` (11 XUL `radio` elements in 4 `radiogroup`s inside `#mainPrefPane`, 0 `html:moz-radio`; all read 2026-10-27 from the installed Firefox ESR 153.5.1); the adapted anchors — the ring/face from the Kvantum `radio-normal` interior element (the checked `radio-checked-normal` element shares the arrangement with its dot) and the dot from `theme/desktoptheme/org.macos8.desktop/widgets/checkmarks.svg`'s `radiobutton` circle drawn centred, pinned by `tests/test_desktoptheme_checkmarks.py::TestCheckmarks` (a platform colour adaptation with the 14x14 Kvantum cell scaled onto the 16px box and the dot taken 1:1); the `rgb(0, 0, 0)` encoding choice and the data-URI route; the `:not([disabled])` disabled choice (the parts-5/6 precedent), the absence of a hover rule and the absence of a bevel (the Kvantum radio art has none); the out-of-scope surfaces (`html:moz-radio`, the dialog radios — and the panes' entry fields and menulists, later parts); and that geometry, anatomy, the disabled colour and the focus outline stay Firefox's, with only `#FFFFFF` and `#000000` plus the dot's `rgb(0, 0, 0)` appearing, every hex already a member of the pinned palette (`test_palette_is_exact`); declaration checks do not establish rendered radio pixels.

In `tests/test_firefox_content_theme.py`: add module constants `RADIO_FACE = "#mainPrefPane radio:not([disabled]) .radio-check"` and `RADIO_DOT = "#mainPrefPane radio:not([disabled])[selected] .radio-check"` beside `CHECKBOX_FACE`/`CHECKBOX_GLYPH`, and extend `REQUIRED_PREFERENCES_RULES` with the two selectors mapped to their exactly pinned declaration dicts (the dot rule's `background-image` value being the byte-exact `url("data:…")` string above), so `TestFirefoxPreferencesNavTheme::test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` hold for the now twelve-rule `about:preferences` body in order (`moz-page-nav-button`, `moz-page-nav`, `#nav-separator`, `:root`, `.subcategory`, `moz-input-search#searchInput`, the button face rule, the button hover rule, the checkbox face rule, the checkbox glyph rule, the radio face rule, the radio dot rule). Add `TestFirefoxPreferencesRadioTheme(SheetCase)` with `AT_RULE_URL = "about:preferences"` holding: `test_radio_rules_are_the_sheet_recipe` — both rules equal the pinned dicts byte-for-byte (which also proves `support.gtk_css.parse_css` round-trips the data-URI value); `test_radio_rules_scope_to_the_pane` — both selectors start with `#mainPrefPane radio` and carry `:not([disabled])`, the face rule is the one without `[selected]`, and neither selector names `checkbox`, `moz-radio` or `#dialogTemplate`; `test_radio_rules_use_the_pinned_palette` — every hex literal in the two rules lies in `{WHITE, BLACK}` imported from `tests/support/platinum_palette.py` and every colour-setting declaration carries `!important`; `test_selected_dot_uri_pins_the_radiobutton_dot` — decoding the dot rule's `background-image` URI (urllib.parse.unquote) yields an SVG whose `cx`, `cy`, `r` and `fill` attribute values equal the pinned `8`, `8`, `3` and `rgb(0, 0, 0)` (the same dot `tests/test_desktoptheme_checkmarks.py::TestCheckmarks` pins, in the bottom 16x16 cell), whose width and height are `16`, and which contains no `#`-prefixed hex literal; and `test_header_names_radio_provenance` — the header names `radio.css`, `radio.js`, `common-shared.css`, `--checkbox-size`, `radio-normal`, `radio-checked-normal`, `org.macos8.desktop.svg`, `widgets/checkmarks.svg`, `tests/test_desktoptheme_checkmarks.py::TestCheckmarks`, `rgb(0, 0, 0)`, `:not([disabled])`, `[selected]`, `moz-radio` and `platform colour adaptation 2026-10-27` (pattern: `TestFirefoxPreferencesCheckboxTheme::test_header_names_checkbox_provenance`).

In `docs/invariants.md`, append a row of its own after the checkbox row in the `## firefox` table (the register keeps one row per landed part): the enabled XUL radios in the panes are the Platinum circle face — a `#FFFFFF` face with a 1px `#000000` circular ring, no bevel, no native appearance — and a selected one overlays the black centred dot inlined as a data-URI SVG, while disabled radios, the shadow-DOM `html:moz-radio` elements, the `#dialogTemplate` dialog radios, the box geometry, the label anatomy and the focus outline stay Firefox's; the row's provenance records the radio sentences above (the `radio.css` paint chain, the sizing, the Kvantum and checkmarks anchors, the rgb encoding choice) with `TestFirefoxPreferencesRadioTheme` in the test column. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block holds exactly twelve rules in order — the ten byte-unchanged rules from parts 1–6 followed by the two radio rules above — and the two new rules introduce no colour outside `#FFFFFF` and `#000000` plus the dot's `rgb(0, 0, 0)`; the sheet's hex set stays exactly the pinned palette and `TestFirefoxContentTheme::test_palette_is_exact` passes untouched.
- `TestFirefoxPreferencesRadioTheme`'s five tests pass; `test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` hold against the extended `REQUIRED_PREFERENCES_RULES`; `TestFirefoxPreferencesCheckboxTheme`'s tests keep green against the byte-unchanged checkbox rules; the sheet's other hygiene tests (`test_no_rule_paints_page_chrome`, `test_selectors_are_not_universal`, `test_sheet_does_not_import_or_name_adwaita`) keep green over the extended sheet.
- The header's radios paragraph names the required strings above; `test_header_names_radio_provenance` pins them.
- `docs/invariants.md`'s new row records the radio paint, the stay-Firefox surfaces and the platform adaptation, with `TestFirefoxPreferencesRadioTheme` in its test column; `tests/invariants.py` stays green.
- `make check` passes.

## Done

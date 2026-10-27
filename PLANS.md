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

### Firefox Platinum preferences, part 8: paint the panes' entry fields as the Platinum sunken line edit and their menulists as the Platinum raised push buttons (planned 2026-10-27 by the plan role; independent of the waiting Firefox Library column-headers plan — the two touch disjoint sheet and test files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py` versus `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py` and `tests/test_firefox_theme_library.py`), and their `docs/invariants.md` edits touch different rows (the Library plan trims the landed places-trees row and appends its own; this plan only appends its own row), so either order merges; it is part 8 of the about:preferences series, whose parts 1 (category navigation rows), 2 (sidebar separators), 3 (page background and heading bands), 4 (search field), 5 (pane push buttons), 6 (checkboxes) and 7 (radio groups) landed 2026-10-27) — this entry covers the panes' entry fields and menulists together because the two append inside the same `@-moz-document url("about:preferences")` block and extend the same `REQUIRED_PREFERENCES_RULES` dict and its ordered-rule assertions, so the two halves cannot merge independently (the pane push-buttons part recorded the same coupling against the search field); no further pane control waits beyond it — the panes' sub-dialogs are separate documents this sheet does not reach)

**Goal.** The landed parts left about:preferences' text entry fields and dropdown menulists Firefox's. `chrome/browser/content/browser/preferences/preferences.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`; `vbox#mainPrefPane` opens ~line 243) authors both surfaces as ordinary light-DOM elements inside the pane: four `html:input[type="text"]` fields (`#homePageUrl` ~line 512, `#dohEnabledInputField` ~1352, `#dohStrictInputField` ~1389, and `#fxaSyncComputerName` ~1563 which starts `disabled="true"`) and eight XUL `menulist` elements (`#primaryBrowserLocale` ~335, `#homeMode` ~500, `#newTabMode` ~551, `#blockCookiesMenu` ~940, `#trackingProtectionMenu` ~967, `#fingerprintingProtectionMenu` ~995, `#dohEnabledResolverChoices` ~1349, `#dohStrictResolverChoices` ~1386) — no `html:textarea` exists in the pane. `chrome/toolkit/skin/classic/global/in-content/common-shared.css` (root `omni.ja`, read 2026-10-27) paints the fields `border: 1px solid var(--border-color)`, `border-radius: var(--border-radius-medium)`, `background-color: var(--background-color-box)`, `color: inherit` — rounded grey boxes reading as nothing Platinum on the white page part 3 painted — and paints the menulists like buttons (`button, …, xul|menulist` sharing the token `--button-*` pill recipe from `tokens-shared.css`/`tokens-brand.css`) with `:hover`/`[open="true"]`/disabled recolours; `chrome/toolkit/skin/classic/global/menulist.css` gives the menulist's shadow-tree `dropmarker` element its `content: url(chrome://global/skin/icons/arrow-down-12.svg)` drawn `currentColor` and owns the non-native focus outline. Paint the four enabled fields as the sheet's Platinum sunken line edit — white face, black text, square 1px black outline, `inset 1px 1px #999999` sunken shadow, the byte-recipe the landed about:config `#about-config-search` rule carries in this same sheet — and the eight enabled menulists as the landed `#mainPrefPane button` push-button recipe with the landed `#mainPrefPane button:hover` flat `#CCCCFF` no-bevel recipe extended to the open state. No reference screenshot shows Firefox's about:preferences; the field adapts this theme's `widgets/lineedit.svg` and the menulist face the reference-grounded `widgets/button.svg` (platform colour adaptations). The disabled `#fxaSyncComputerName` keeps Firefox's whole disabled paint (the push buttons' and radios' `:not([disabled])` choice). Geometry (`min-height`, `padding`, `margin`, font), the field focus outline, the `:user-invalid` error ring, the menulists' `dropmarker` arrow (it already follows `currentColor` black), the dropdown `menupopup` lists and their stock styling stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the existing `@-moz-document url("about:preferences")` block after the landed `radio:not([disabled])[selected] .radio-check` rule (currently the block's last rule), append three rules and nothing else:

    /* The panes' entry fields and menulists: the Platinum sunken line
       edit and raised push button (see the header's provenance
       paragraph). */
    #mainPrefPane input[type="text"]:not([disabled]) {
      background-color: #FFFFFF !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #999999 !important;
    }

    #mainPrefPane menulist:not([disabled]) {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border: 1px solid #000000 !important;
      border-radius: 0 !important;
      box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA !important;
    }

    #mainPrefPane menulist:not([disabled]):hover,
    #mainPrefPane menulist[open="true"]:not([disabled]) {
      background-color: #CCCCFF !important;
      color: #000000 !important;
      box-shadow: none !important;
    }

The field rule carries `[type="text"]` step so it can never widen to the element name `input` beyond the authored population, and the plain `input`/`menulist` type selectors match without an `@namespace` because the sheet declares none (the landed `button`/`checkbox`/`radio` rules rely on the same). The menulist face rule out-specifies the stock `xul|menulist` token rules through the `#mainPrefPane` prefix, and the hover rule's two arms cover the stock `:hover` recolour and the `[open="true"]` active recolour `common-shared.css` applies. `parse_css` splits the comma list into one key per arm. The rules introduce no hex literal outside the pinned set `{#FFFFFF, #000000, #999999, #DDDDDD, #AAAAAA, #CCCCFF}` — every value already a sheet member — so `TestFirefoxContentTheme::test_palette_is_exact` passes untouched.

Extend the header comment's provenance block with an entry-fields-and-menulists paragraph inserted immediately after the landed radios paragraph and before the header's closing `*/`, and edit the radios paragraph's stay-Firefox sentence from "as do the panes' entry fields and menulists (later parts);" to "(the panes' entry fields and menulists have their own paragraph below);" keeping the rest of that sentence unchanged. The new paragraph names: no reference screenshot shows Firefox's about:preferences; the field is the sheet's Platinum sunken line edit, the byte-recipe of the landed about:config `#about-config-search` rule, adapting `widgets/lineedit.svg`, pinned by `tests/test_desktoptheme_lineedit.py::TestLineEdit` and `TestLineEditReference`; the menulist face is the landed `#mainPrefPane button` recipe adapting `widgets/button.svg`, pinned by `tests/test_desktoptheme_button.py::TestButton` and `tests/test_desktoptheme_button_reference.py::TestButtonReference`, and the flat `#CCCCFF` hover/open fill adapts `widgets/viewitem.svg`, pinned by `tests/test_desktoptheme_viewitem.py::TestViewItem` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background` (platform colour adaptations 2026-10-27); the anatomy read 2026-10-27 from the installed Firefox ESR 153.5.1 — `preferences.xhtml`'s four `html:input[type="text"]` fields (`#homePageUrl`, `#dohEnabledInputField`, `#dohStrictInputField`, `#fxaSyncComputerName`) and eight `menulist` elements (`#primaryBrowserLocale`, `#homeMode`, `#newTabMode`, `#blockCookiesMenu`, `#trackingProtectionMenu`, `#fingerprintingProtectionMenu`, `#dohEnabledResolverChoices`, `#dohStrictResolverChoices`) inside `#mainPrefPane` as authored light-DOM elements, `common-shared.css`'s stock field paint (`--border-color`, `--border-radius-medium`, `--background-color-box`, `color: inherit`, focus outline, `user-invalid` ring, disabled opacity 0.4) and token pill menu paint (`tokens-shared.css`/`tokens-brand.css`), and `menulist.css`'s shadow `dropmarker` with `arrow-down-12.svg` drawn `currentColor` — all packages `omni.ja` reads marked for the toolkit file and `browser/omni.ja` for `preferences.xhtml`; the intentionally unscoped surfaces — the disabled `#fxaSyncComputerName` (`:not([disabled])`), the menus' `menupopup` dropdown lists, the field focus outline and error ring, the dropmarker geometry and the panes' sub-dialogs (separate documents); and that there is no field hover rule because `widgets/lineedit.svg` ships no hover state; declaration checks do not establish rendered pixels.

In `tests/test_firefox_content_theme.py`: add module constants after `RADIO_FACE`/`RADIO_DOT` — `PANEFIELD = "#mainPrefPane input[type=\"text\"]:not([disabled])"`, `PANE_MENULIST = "#mainPrefPane menulist:not([disabled])"` and `PANE_MENULIST_HOVER = "#mainPrefPane menulist:not([disabled]):hover"` plus `PANE_MENULIST_OPEN = "#mainPrefPane menulist[open=\"true\"]:not([disabled])"` — pinned dicts `PANEFIELD_RULE` (the byte-recipe of this module's `FIELD_RULE`, spelled explicitly rather than aliased) and `PANE_MENULIST_RULE`/`PANE_MENULIST_HOVER_RULE` (the byte-recipes of `PANE_BUTTON_RULE`/`BUTTON_HOVER_RULE` above, spelled explicitly), extend `REQUIRED_PREFERENCES_RULES` with `PANEFIELD`, `PANE_MENULIST` and `PANE_MENULIST_HOVER` mapped to `PANEFIELD_RULE`, `PANE_MENULIST_RULE` and the `PANE_MENULIST_HOVER_RULE` shared by both hover arms, and add `class TestFirefoxPreferencesFieldsTheme(SheetCase)` with `AT_RULE_URL = "about:preferences"` after `TestFirefoxPreferencesRadioTheme`, holding: `test_field_and_menulist_rules_are_the_sheet_recipe` — each of the five `#mainPrefPane` field/menulist arms equals its pinned dict byte-for-byte, the dict entries and the `REQUIRED_PREFERENCES_RULES` entries being the same mapping; `test_field_and_menulist_rules_extend_the_ordered_rule_register` — `TestFirefoxPreferencesNavTheme::test_required_rules` (which asserts `set(self.rules) == set(REQUIRED_PREFERENCES_RULES)` and `self.selectors == list(REQUIRED_PREFERENCES_RULES)`) passes over the extended dict, proving the three rules are the block's last in sheet order so no earlier rule moved; `test_field_and_menulist_rules_scope_to_the_pane` — every arm starts `#mainPrefPane`, the field arm carries `[type="text"]` and `:not([disabled])` and no `moz-input-search`, the menulist face arm carries `:not([disabled])`, one hover arm carries `:hover` and the other `[open="true"]`, and no selector names `menupopup`, `#dialogTemplate` or `subdialog`; and `test_field_and_menulist_rules_use_the_pinned_palette` — every declaration carries `!important` and each arm's hex set is `input`: `{WHITE, BLACK, GREY}`, `menulist face`: `{WHITE, BLACK, FACE, BUTTON_SHADOW}`, `hover arms`: `{SELECTION, BLACK}`; matching through `support.selector_matching.matches` — the field arm matches `element("input", "homePageUrl", attrs={"type": "text"}, parent=element("html", None, parent=element("vbox", "mainPrefPane")))` and never the same fixture with `attrs={"type": "text", "disabled": "true"}` or `attrs={"type": "range"}`, the menulist face arm matches `element("menulist", "homeMode", parent=element("vbox", "mainPrefPane"))` and never a `menulist` under an element("vbox", "dialogTemplate") parent, and the two hover arms match their fixtures with `hover=True` and `attrs={"open": "true"}` respectively (matcher text gives attribute support); and `test_header_names_field_provenance` — the header names the strings above (pattern: `TestFirefoxPreferencesRadioTheme::test_header_names_radio_provenance`). No incumbent test edits beyond the extended dict: the palette, custom-property and other per-selector tests keep to their own selectors, and nothing in `FORBIDDEN_PAGE_CHROME`, `CONFIG_*` or the downloads/`about:config` case classes names `input`/`menulist`.

In `docs/invariants.md`, in the `## firefox` table, append a row of its own immediately after the landed radios row (the register keeps one row per landed part; the new plan only appends — no existing row's word changes): the about:preferences enabled entry fields (the four `html:input[type="text"]` inside `#mainPrefPane`) are the Platinum sunken line edit — white face, black text, square 1px black outline, the `inset 1px 1px #999999` shadow — and the enabled menulists (the eight `menulist` inside `#mainPrefPane`) are square `#DDDDDD` push buttons with a black outline and the white/`#AAAAAA` raised bevel, a hovered (or `[open="true"]`) one flat `#CCCCFF` with black text and no bevel, while the disabled `#fxaSyncComputerName`, dropdown `menupopup` lists, dropmarker arrow, field focus outline, error ring and geometry stay Firefox's; the row's provenance records the `widgets/lineedit.svg`/`widgets/button.svg`/`widgets/viewitem.svg` adaptations and the `preferences.xhtml`/`common-shared.css`/`menulist.css`/`tokens-shared.css` paint chain read 2026-10-27 with `TestFirefoxPreferencesFieldsTheme` plus `TestFirefoxContentTheme::test_palette_is_exact` in the test column, and declaration checks do not establish rendered pixels. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block gains exactly the three rules above after the radio-selected rule (five selector arms), introducing no hex outside `{#FFFFFF, #000000, #999999, #DDDDDD, #AAAAAA, #CCCCFF}` (all pre-existing sheet members); `TestFirefoxContentTheme::test_palette_is_exact` passes untouched.
- `TestFirefoxPreferencesFieldsTheme`'s tests pass; `TestFirefoxPreferencesNavTheme::test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` hold over the extended `REQUIRED_PREFERENCES_RULES` with the five new arms last in sheet order; every other `tests/test_firefox_content_theme.py` class (downloads, `about:config`, sidebar/search, buttons, checkboxes, radios) keeps green against unchanged text.
- The header comment drops the radios paragraph's later-parts clause (the replacement sentence above) and carries the new provenance paragraph naming the strings above; `test_header_names_field_provenance` pins them.
- `docs/invariants.md` gains the entry-fields-and-menulists row after the radios row with `TestFirefoxPreferencesFieldsTheme` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

## Done

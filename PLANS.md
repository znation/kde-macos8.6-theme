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

### Firefox Platinum chrome, part 4 of a Library window series: paint the Library toolbar band as the Platinum toolbar and its Organize/View/Maintenance menu titles as the Platinum menu titles (planned 2026-10-27 by the plan role; independent of the waiting about:preferences part 8 plan — the two touch disjoint sheet and test files (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme_library.py` and `tests/support/firefox_chrome_cases.py` versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`), and their `docs/invariants.md` edits touch different rows (the prefs plan only appends its own new row; this plan trims the landed places-trees row's stay-Firefox list and appends its own new row), so either order merges; it is part 4 of the Firefox Library window series, whose parts 1 (the two places trees as the Platinum sunken list field), 2 (the toolbar search box as the Platinum line edit) and 3 (the content tree's column headers as the Platinum raised header buttons) landed 2026-10-27 and whose base recipes this part reuses without touching their rules — the `richlistbox#downloadsListBox` downloads view and the `#detailsPane` bookmark-details fields are later parts that wait behind this one)

**Goal.** The landed parts left the Library window's toolbar band Firefox's and its three dropdown menu titles Firefox's. In `chrome/browser/content/browser/places/places.xhtml` (read 2026-10-27 from the installed Firefox ESR 153.5.1's `browser/omni.ja`), `toolbox#placesToolbox` holds `toolbar#placesToolbar.chromeclass-toolbar` with `toolbarbutton#back-button` and `toolbarbutton#forward-button` (both starting `disabled="true"`) and `menubar#placesMenu nonnative="true"` with the three `menu.menu-iconic` titles `#organizeButton`, `#viewMenu` and `#maintenanceButton`, each opening a `menupopup` (`#organizeButtonPopup`, `#viewMenuPopup`, plus the maintenance popup). `chrome/toolkit/skin/classic/global/toolbar.css` (root `omni.ja`, read 2026-10-27) paints the Linux `toolbar` band `background-color: -moz-headerbar` with `-moz-headerbartext` text (and `-moz-headerbarinactive`/`-moz-headerbarinactivetext` when the window is inactive) — a grey-blue band reading as nothing Platinum under the sheet's white trees. `chrome/browser/skin/classic/browser/places/organizer.css` gives `#placesMenu > menu` `appearance: auto` with `-moz-default-appearance: toolbarbutton`, `min-height: var(--button-min-height)`, `:hover`/`:hover:active`/`[open]` `-moz-buttonhovertext`/`-moz-buttonactivetext` colour changes and the `::after` `arrow-down-12.svg` dropmarker drawn `currentColor`, and `chrome/toolkit/skin/classic/global/menu.css`'s Linux `menubar > menu` block paints the titles transparent with `0.25em 0.5em` padding, a 1px bottom pad and a 3px transparent bottom border, `[open]` boxing an `AccentColor` underline — so at rest the titles hover as unanchored text with no fill, and an open one underlines in the platform accent, nothing Platinum. The two toolbarbuttons need no new rule: at rest their native toolbarbutton paint is transparent over the band and the sheet's landed generic `toolbarbutton:hover:not([disabled="true"])` and `toolbarbutton:hover:active:not([disabled="true"])` bevel rules (the app-toolbar recipe appended when the main-toolbox plan landed) already shape their hover and press, in this same sheet, in the Library window too. Paint the toolbar band as the Platinum toolbar — `#DDDDDD` face, black text, the `1px solid #888888` bottom rule with the `inset 0 -1px #FFFFFF` etched highlight, the byte-recipe the landed `#toolbar-menubar` band rule carries in this same sheet — and the three menu titles as the landed `#toolbar-menubar` menu-title recipe: the `3px 7px 0` padding over Firefox's retained 3px transparent stock bottom border, and `[open]` flat `#CCCCFF` with the border-bottom filled `#CCCCFF`. No reference screenshot shows the Firefox Library window; the band reuses this sheet's reference-grounded toolbar recipe and the menu titles adapt `widgets/menubaritem.svg`'s flat-pressed title (platform colour adaptations). The two back/forward toolbarbuttons' icons, enabled/disabled states and the sheet-generic hover/active bevels, organizer.css's `--button-min-height` and native `toolbarbutton` appearance on the menus, the `::after` dropmarker arrow drawn `currentColor` black, the three `--menuitem-icon` icons, the menu popups (already token-painted by the sheet's landed `menupopup` rule), the window body and the two later surfaces (downloads rich list, details pane) keep their paint.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, after the landed `treecols#placeContentColumns` header rules (currently the sheet's last rules), with a short comment naming the adaptation, append three rules and nothing else:

    /* The Library window's toolbar band and menu titles adapt the sheet's
       toolbar and menubar-title recipes (see the header's provenance
       paragraph). */
    toolbar#placesToolbar {
      background-color: #DDDDDD !important;
      color: #000000 !important;
      border-bottom: 1px solid #888888 !important;
      box-shadow: inset 0 -1px #FFFFFF !important;
    }

    menubar#placesMenu > menu {
      padding: 3px 7px 0 !important;
    }

    menubar#placesMenu > menu[open] {
      background-color: #CCCCFF !important;
      border-bottom-color: #CCCCFF !important;
    }

In `tests/support/firefox_chrome_cases.py`: extend the shared `REQUIRED_RULES` dict after the `"menubar#placesMenu > menu[open]"`-sibling phrase with three new entries placed after the `"treecols#placeContentColumns"` group the current dict ends with (keep the dict's footer comment accurate) — `"toolbar#placesToolbar"`, `"menubar#placesMenu > menu"` and `"menubar#placesMenu > menu[open]"` — each the byte-recipe of the landed `"#toolbar-menubar"`, `"#toolbar-menubar menubar > menu"` and `"#toolbar-menubar menubar > menu[open]"` entries respectively, spelled explicitly with the shared palette constants rather than aliased (yes, the first entry is the same mapping as `"#toolbar-menubar"`).

In `tests/test_firefox_theme_library.py`: add a module constant after `HEADER_HOVER_ARMS` — `TOOLBAR_RULES = ("toolbar#placesToolbar", "menubar#placesMenu > menu", "menubar#placesMenu > menu[open]")` — and add `class TestFirefoxLibraryToolbarChrome(FirefoxChromeTestCase)` after `TestFirefoxLibraryHeaderChrome`, holding: `test_toolbar_and_menubar_rules_match_the_required_rules` — each of the three arms equals its `REQUIRED_RULES` entry byte-for-byte and every declaration ends `!important`; `test_toolbar_band_is_scoped_to_the_library_toolbar` — via `support.selector_matching`'s `element`/`matches`, `toolbar#placesToolbar` matches `element("toolbar", "placesToolbar")` and never `element("toolbar", "nav-bar")`, and `menubar#placesMenu > menu` matches `element("menu", "organizeButton", parent=element("menubar", "placesMenu", parent=element("toolbar", "placesToolbar")))` (and the same with the other two ids, one with `attrs={"open": "true"}` matching the open arm and without matching only the padding arm) but never a `menu` whose parent `menubar` lacks the `placesMenu` id (the `#toolbar-menubar` menubar's titles included), and `test_header_names_toolbar_provenance` (pattern: `TestFirefoxLibraryHeaderChrome`'s final test) asserting the header names the strings below. Extend the assertions of `TestFirefoxLibraryChrome::test_library_tree_provenance` and `TestFirefoxLibrarySearchChrome::test_header_names_search_provenance` for the two narrowed sentences below.

The header comment gains exactly one paragraph, between the column-headers paragraph and the closing `*/`, naming: no reference screenshot shows the Firefox Library window; the toolbar band reuses this sheet's landed `#toolbar-menubar` recipe (`#DDDDDD` face, black text, the `#888888` bottom rule and the `inset 0 -1px #FFFFFF` etched highlight), grounded in the reference toolbars and pinned by `tests/test_firefox_theme_shell.py::TestFirefoxChromeShell::test_required_rules`; the open menu title's flat `#CCCCFF` fill comes from `widgets/menubaritem.svg`'s pressed slices with no hover highlight (platform colour adaptation 2026-10-27), pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem.test_menubaritem_pressed_is_flat_selection_colour` and `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`; the anatomy is read 2026-10-27 from the installed Firefox ESR 153.5.1 — `places.xhtml`'s `toolbox#placesToolbox` with `toolbar#placesToolbar.chromeclass-toolbar` holding `toolbarbutton#back-button` and `toolbarbutton#forward-button` (both starting `disabled="true"`) and `menubar#placesMenu nonnative="true"` with the three `menu.menu-iconic` titles `#organizeButton`, `#viewMenu` and `#maintenanceButton`; `chrome/toolkit/skin/classic/global/toolbar.css` paints the Linux `toolbar` band `-moz-headerbar`/`-moz-headerbartext` with the `-moz-headerbarinactive` inactive pair; `organizer.css` gives `#placesMenu > menu` `appearance: auto` with `-moz-default-appearance: toolbarbutton`, `min-height: var(--button-min-height)`, the `-moz-buttonhovertext`/`-moz-buttonactivetext` hover/open colour changes and the `::after` `arrow-down-12.svg` dropmarker drawn `currentColor`; `menu.css`'s Linux `menubar > menu` block owns the transparent rest paint, the `0.25em 0.5em`/1px bottom padding the rules override and the 3px transparent bottom border they keep, with the `[open]` `AccentColor` underline they replace; and the intentionally unscoped surfaces — the two back/forward toolbarbuttons (already shaped by the sheet's generic `toolbarbutton:hover`/`:hover:active` bevel rules, rest state Firefox's), organizer.css's `--button-min-height` and native appearance on the menus, the `::after` dropmarker, the three `--menuitem-icon` icons, the popup lists (the landed `menupopup` token rule), the window body, the downloads rich list and the details pane; plus that only the padding is overridden on the titles, with a zero bottom pad, so the retained stock border completes the 3px bottom margin and stays the open title's `#CCCCFF` underline; and that declaration checks do not establish rendered pixels.

In the header's two earlier paragraphs, narrow the stay-Firefox sentences: the trees paragraph's sentence becomes "The toolbar's back and forward buttons, downloads rich list and details pane stay Firefox's for the later parts of this series (the content-tree column headers, the toolbar's search filter and the toolbar's menu titles have their own paragraphs below)." and the search paragraph's sentence becomes "The toolbar's back and forward buttons, the downloads rich list and the details pane stay Firefox's for the later parts of this series." — keeping the asserted substrings `The toolbar's back and forward buttons` and `downloads rich list and details pane stay Firefox's` contiguous, and refreshing `test_library_tree_provenance`'s corresponding assertions.

In `docs/invariants.md`, in the `## firefox` table: trim the landed places-trees row's stay-Firefox list from "the row icons, twisties, toolbar buttons and the Organize/View/Maintenance menus, downloads rich list and details pane stay Firefox's" to "the row icons, twisties, the toolbar's back and forward buttons, downloads rich list and details pane stay Firefox's" (the series precedent when a part takes over a surface), and append a new row immediately after the column-headers row: the Library window's toolbar band `toolbar#placesToolbar` is the Platinum toolbar — `#DDDDDD` face with black text, a `1px solid #888888` bottom rule and the `inset 0 -1px #FFFFFF` etched highlight — and its Organize/View/Maintenance titles (`menubar#placesMenu > menu`) take the Platinum menu-title padding with an open title flat `#CCCCFF` and the stock bottom border filled the same, while the back/forward toolbarbuttons' icons and sheet-generic hover bevels, the menus' `min-height` and native appearance, the `::after` dropmarker, the three icons, the popup lists, the window body, the downloads rich list and the details pane stay Firefox's; the row's provenance records the `#toolbar-menubar`/`menubaritem.svg` reuse and the `places.xhtml`/`toolbar.css`/`organizer.css`/`menu.css` chain read 2026-10-27 with `TestFirefoxLibraryToolbarChrome` plus `TestFirefoxChromeShell::test_palette_is_exact` in the test column. `tests/invariants.py` is structural and stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_library.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet gains exactly the three rules above after the `treecols#placeContentColumns` header rules, introducing no hex outside `{#DDDDDD, #000000, #888888, #FFFFFF, #CCCCFF}` (all pre-existing sheet members); `TestFirefoxChromeShell::test_palette_is_exact` passes untouched, and no landed rule's text changes other than the narrowed header sentences.
- `TestFirefoxLibraryToolbarChrome`'s tests pass; the three new `REQUIRED_RULES` entries make `TestFirefoxChromeShell::test_required_rules` and every other chrome suite's per-selector tests pass without edits (no incumbent test asserts the sheet rule count, and `TestFirefoxLibraryChrome`'s named-places-tree filter excludes all three new selectors); every other `tests/test_firefox_theme_library.py` class (trees, search, headers) keeps green against unchanged rule text.
- The header gains exactly one paragraph between the column-headers paragraph and `*/` carrying the provenance strings above (pinned by `test_header_names_toolbar_provenance`); the two earlier paragraphs' sentences are narrowed exactly as specified, with the asserted substrings contiguous.
- `docs/invariants.md` trims the places-trees row's stay-Firefox list as specified and gains the toolbar-and-menu-titles row after the column-headers row, with `TestFirefoxLibraryToolbarChrome` named in its test column and no other row's wording changed; `tests/invariants.py` stays green.
- `make check` passes.

## Done

# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-nine widget SVGs under
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

### Platinum desktoptheme analog clock face: ship `widgets/clock.svg` for the analog clock plasmoid (planned 2026-10-27 by the plan role; independent of the waiting timer-digits plan — the two touch disjoint art files (`theme/desktoptheme/org.macos8.desktop/widgets/clock.svg` versus `widgets/timer.svg`) plus append-only rows in the same three shared files, so either order merges; it follows the same pattern the landed notes-paper plan set)

**Goal.** The desktop theme ships twenty-nine `widgets/` SVGs but not `clock.svg`, so the optional analog clock plasmoid (`org.kde.plasma.analogclock`) draws Breeze's gradient face instead of Platinum art. The installed plasmoid (read 2026-10-27 from `/usr/share/plasma/plasmoids/org.kde.plasma.analogclock/contents/ui/`) draws the face and every hand as `KSvg.SvgItem` with `imagePath: "widgets/clock"` (`main.qml`): the required element ids are `ClockFace`, `HourHand`, `HourHandShadow`, `MinuteHand`, `MinuteHandShadow`, `SecondHand`, `SecondHandShadow`, `HandCenterScrew` and `Glass` — nine in all; its rotations are `180 + hours*30 + minutes/2`, `180 + minutes*6` and `180 + seconds*6`, so every hand's neutral art points toward 6 o'clock (at 12:00, rotation 180 must stand the hand up to 12). `Hand.qml` also queries `rotationCenterHintId: "hint-<hand>[shadow]-rotation-center-offset"` — none of these nine ids — and `main.qml` probes `hint-hands-shadow-offset-to-west`/`to-east`/`to-north`/`to-south` with `hasElement`; when absent both fallbacks are harmless (`naturalHorizontalHandShadowOffset`/`naturalVerticalHandShadowOffset` become 0, the rotation centres become the hand rect's centre), which the plasmoid handles itself, so this theme ships none of the hint ids and leans on the fallbacks.

**Grounding.** No reference screenshot shows an analog clock (Mac OS 8.6's Clock applet is absent from the set), so this is the platform-required adaptation: the nine element ids, the six optional hint ids and the point-down neutral orientation are KDE-required and read from the installed plasmoid; the face geometry and art are this theme's own, in the theme's established flat black-glyph recipe (`widgets/checkmarks.svg`). The two colours reuse already-pinned tokens — hands and ticks `#000000` (`[Colors:Tooltip] ForegroundNormal=0,0,0` in `theme/color-schemes/MacOS8.colors`, the checkmarks black), the second hand `#CC0000` (`ForegroundNegative=204,0,0`, the timer plan's alert red precedent) — and the face reuses the etched-ring pair `#888888`/`#FFFFFF` (`tests/test_desktoptheme_line.py` `DARK`/`LIGHT`) over the white field face (`#FFFFFF`, `tests/test_desktoptheme_lineedit.py`). Provenance for these platform-required values goes in the file header and both tests' comments.

**Approach.** Add `theme/desktoptheme/org.macos8.desktop/widgets/clock.svg` on one 528x96 root canvas. Columns, left to right, each an element group plus one invisible full-bounds `fill="none"` rect pinning it, so no element rect overlaps another and every `elementRect` is exact:

- `ClockFace` (0,0,96,96): the bounds rect; a white circle `cx="48" cy="48" r="47"` `fill="#FFFFFF"` with `stroke="#888888" stroke-width="1"` as the face's dark ring (the light half of the etch is noise at 1px on a curve — record the choice in the header); and twelve hour ticks, each a `stroke="#000000" stroke-width="2"` `path d="M 48,5 L 48,12"` filling the 12-o'clock direction, eleven of them inside `<g transform="rotate(θ 48 48)">` for θ = 30…330 in steps of 30 and the twelfth bare (`rotate(0)` written nowhere — the test accepts the bare path as the 0 tick).
- `HandCenterScrew` (104,0,12,12): a black filled `circle cx="110" cy="6" r="5"` (`main.qml` anchors it `centerIn` the clock, sizing by natural size — the rect just pins 12x12 natural).
- `HourHandShadow` (124,0,8,8), `MinuteHandShadow` (204,0,8,8), `SecondHandShadow` (316,0,8,8): bounds rects only, nothing visible — the shadow items draw nothing, keeping the flat look, and the missing shadow-offset hint elements make both shadow offsets 0.
- `HourHand` (140,0,56,56): a stroke-only 4px `path d="M 168,54 L 168,16"` `#000000` — the pivot is the rect's centre (that is the QML fallback), the tip is the path's lower end reaching y=54 so the square cap lands exactly on the rect edge, and the 12px tail above the pivot is the path's upper end; the lower tip is the hand's pointing direction, matching the point-down neutral.
- `MinuteHand` (220,0,88,88): the same recipe, 3px `path d="M 264,86 L 264,32"` `#000000`.
- `SecondHand` (332,0,88,88): same recipe, 2px `path d="M 376,86 L 376,32"` `#CC0000`.
- `Glass` (432,0,96,96): bounds rect only — the plasmoid fills the face with it (`anchors.fill: face`); flat theme means no glass.

Every hand rect is square, so the `Hand.qml` vertical fallback (its `verticalRotationCenter` otherwise falls back to `width/2`) keeps it vertically centred on the clock like the horizontal fallback. The leading XML comment names the consumer (`org.kde.plasma.analogclock` `main.qml` `imagePath: "widgets/clock"`), the nine KDE-required ids, the point-down neutral (why every tip is at the rect's lower edge and the `180 +` rotations stand the hands up at 12), the absent hint ids and their fallback consequences, the missing reference surface, and the four colour provenances above.

In `tests/support/desktoptheme_paths.py`, add `CLOCK_SVG = os.path.join(PACKAGE, "widgets", "clock.svg")` beside `NOTES_SVG` (line ~31). In `tests/test_desktoptheme.py`, import `CLOCK_SVG` and append `("clock.svg", CLOCK_SVG, 528, 96)` to `SVG_CANVASES` (back-tick the comment above it with one clause for the clock's wide nine-column row); `TestSvgRootCanvas::test_registry_covers_every_shipped_svg` fails until the row lands, so the file cannot ship unregistered.

Add `tests/test_desktoptheme_clock.py` (pattern: `tests/test_desktoptheme_notes.py` — structural assertions via `svg_assertions`' `elements_by_id`/`attribute_values`, no rendering) with `TestClock` holding: `test_clock_declares_exactly_the_nine_kde_required_ids` — the `id` attributes are exactly the nine element ids above (no `hint-` ids — assert the prefix is absent, pinning the fallback path `main.qml` already handles), plus the XML root and metadata boilerplate the registry test tolerates; `test_face_is_white_ring_and_twelve_hour_ticks` — `ClockFace` holds the bounds rect, the pinned circle attributes (fill `#FFFFFF`, stroke `#888888`, stroke-width 1) and exactly twelve tick paths whose parent `g` transforms rotate `48 48` by exactly the twelve angle set 0…330 step 30 (unordered, angles compared as integers), each path `d="M 48,5 L 48,12"`, stroke `#000000`, width 2; `test_hands_are_single_point_down_shafts` — each of the three hands holds its pinned square bounds rect plus exactly one stroke-only path whose `d` is the pinned endpoints above (which also pins that the tip — the lower `y` — is at the rect's lower edge and the tail is 12 above the pivot at the rect centre), `stroke-width` and `stroke-linecap="square"`; `test_second_hand_publishes_the_negative_red` — the second hand strokes `#CC0000` and the hour and minute hands `#000000`, with a comment naming the `ForegroundNegative`/`ForegroundNormal` provenance so a future edit re-grounds it deliberately; and `test_shadows_and_glass_draw_nothing` — the three shadow groups and `Glass` hold only an invisible `fill="none"` bounds rect at their pinned rects, so the flat theme cannot silently grow drop shadows or a glass sheen.

In `docs/invariants.md`, append a row to the `## desktoptheme` table: `widgets/clock.svg` draws the analog clock plasmoid's flat face, hands, screw and invisible overlays at the plasmoid's fallback rotation centres. Test column: `tests/test_desktoptheme_clock.py::TestClock`. Provenance exception: no reference screenshot shows an analog clock; the nine ids, the six rejected hint ids and the point-down hand orientation are KDE-required (read from the installed plasmoid's `main.qml`/`Hand.qml`), the face, hand and tick geometry are this theme's own, and the colours reuse the scheme's `ForegroundNormal`/`ForegroundNegative` and the line.svg/lineedit palette anchors; `tests/support/invariants.py` stays green.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/clock.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `tests/test_desktoptheme_clock.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `widgets/clock.svg` holds exactly nine element groups in the pinned canvas order with their pinned rects — white ringed face, black screw, three invisible shadow columns, three hands (black hour/minute, red second, each one square-capped shaft with tip at the rect's lower edge) and an invisible glass — with the header comment naming the consumer, the KDE-required ids and neutral orientation, the absent hint ids' fallback consequences, the missing reference surface and the colour provenances.
- `TestClock`'s five tests pass and pin the id set (and the hint-id absence), the face's circle and twelve ticks, each hand's re-pinned `d` attribute and stroke, the colour split, and the empty shadow/glass groups; `TestSvgRootCanvas`'s registry and root-canvas tests pass with the new `SVG_CANVASES` row; every other desktop-theme test stays green over the unchanged SVGs.
- `docs/invariants.md`'s new row cites `TestClock` and records the provenance exception; `tests/support/invariants.py` stays green.
- `make check` passes.

### Firefox Platinum preferences search field: paint about:preferences' search box as the Platinum line edit through the `moz-input-search` tokens (planned 2026-10-27 by the plan role; independent of the waiting analog-clock plan — the two touch disjoint files (`theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite versus `theme/desktoptheme/org.macos8.desktop/widgets/clock.svg` and its suites), so either order merges; it is part 4 of the about:preferences series, whose parts 1 (category navigation rows), 2 (sidebar separators) and 3 (page background and heading bands) landed 2026-10-27 — the panes' remaining controls (the group cards, push buttons and checkboxes) stay Firefox's for later parts)

**Goal.** The landed parts left every control inside `#mainPrefPane` Firefox's, and the panes' most visible one is the search field: `preferences.xhtml` builds it as `html:moz-input-search#searchInput` (in the installed Firefox ESR 153.5.1, `chrome/browser/content/browser/preferences/preferences.xhtml` line ~237), a shadow-DOM custom element whose inner `#input` is styled by `chrome/toolkit/content/global/elements/moz-input-text.css` exclusively through tokens — `border: var(--input-text-border)`, `border-radius: var(--input-text-border-radius)`, `background-color: var(--input-text-background-color)`, `color: var(--input-text-color)` — with the magnifier icon filled by `var(--icon-color)` through `-moz-context-properties` and no `::part()` exposed. Its token defaults come from `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` (read 2026-10-27): a 1px rounded grey border (`--input-text-border: var(--border-width) solid var(--input-text-border-color)`, `--input-text-border-radius: var(--border-radius-medium)`), a box face and grey `--icon-color`, so the field reads as a rounded Adwaita pill on the white page part 3 painted. Paint it as the Platinum line edit — white face, 1px black square border, black text, black icon — by overriding the tokens on the host element, the exact route part 1's headless run of 2026-10-27 verified (outer-sheet custom properties override the shadow `:host`/inherited defaults). No reference screenshot shows Firefox's about:preferences; the field adapts this theme's `widgets/lineedit.svg` recipe — a platform colour adaptation. One deliberate limitation: the line edit's sunken bevel (`inset 1px 1px #999999`, the sheet's `FIELD_RULE`) cannot be delivered here, because `moz-input-text.css` reads no shadow token — the field ships as the outline, face, text and icon only, and the sheet's provenance records that as this theme's own choice. Geometry (`min-height`, padding), the disabled state and any focus indicator stay Firefox's.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, inside the existing `@-moz-document url("about:preferences")` block, immediately after the `.subcategory` rule, add one rule:

    moz-input-search#searchInput {
      --input-text-border: 1px solid #000000 !important;
      --input-text-border-radius: 0 !important;
      --input-text-background-color: #FFFFFF !important;
      --input-text-color: #000000 !important;
      --icon-color: #000000 !important;
    }

Overriding the composed `--input-text-border` (not just `--input-text-border-color`) pins width, style and colour in one declaration instead of leaving the width tied to `--border-width`; the rule touches only custom properties on the light-DOM host, so the shadow `#input` keeps its single box (no double border from host background/border paint) and the search icon's fill turns black while its own `--input-background-icon` image stays. Extend the leading comment's about:preferences paragraph to name the field, the three files above (read 2026-10-27), the five overridden tokens, the token route reusing part 1's headless verification, the absent shadow token as the reason there is no sunken bevel, the missing reference surface, and that only `#FFFFFF` and `#000000` are used (`tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_palette_is_exact` already pins the sheet's exact set — it must not gain a new literal).

In `tests/test_firefox_content_theme.py`: rename the module constant `REQUIRED_PREFERENCES_NAV_RULES` to `REQUIRED_PREFERENCES_RULES` and add the `SEARCH = "moz-input-search#searchInput"` entry with the exact declarations above, so `TestFirefoxPreferencesNavTheme::test_required_rules` and `test_parsed_rules_are_exactly_the_nav_rules` keep holding for the now six-rule `about:preferences` body; keep `TestFirefoxPreferencesNavTheme::test_host_rule_sets_only_custom_properties` and `test_nav_rule_sets_only_custom_properties` scoped to their own two selectors (the search rule's property names must not be forced through the `--page-nav-` check). Add `TestFirefoxPreferencesSearchTheme(SheetCase)` with `AT_RULE_URL = "about:preferences"` holding: `test_search_field_rule_sets_only_custom_properties` — every property of the `SEARCH` rule starts `--input-text-` or equals `--icon-color`, and every value ends `!important`; `test_search_field_is_the_line_edit` — the rule equals the pinned dict above (border `1px solid #000000 !important`, radius `0 !important`, background `#FFFFFF !important`, text `#000000 !important`, icon `#000000 !important`) and the rule's values contain no hex beyond `WHITE` and `BLACK`; `test_search_field_selector_avoids_page_chrome` — the selector avoids every `FORBIDDEN_PAGE_CHROME` token and names the element and the id (`moz-input-search#searchInput`) so it cannot leak to other pages' `moz-input-search` hosts; and `test_header_names_search_provenance` — the header names `moz-input-search#searchInput`, `moz-input-text.css`, `tokens-shared.css`, `--icon-color`, the no-`::part()` route, the absent sunken bevel, `preferences.xhtml`, `2026-10-27` and `platform colour adaptation 2026-10-27` (pattern: `TestFirefoxPreferencesNavTheme::test_header_names_preferences_provenance`).

In `docs/invariants.md`, append a row to the `## firefox` table: the about:preferences search field (`moz-input-search#searchInput`) is a white face with a square 1px black outline, black text and a black magnifier icon, delivered through the five `--input-text-*`/`--icon-color` tokens on the host element, with the sunken bevel, geometry, disabled and focus states Firefox's. Test column: `tests/test_firefox_content_theme.py::TestFirefoxPreferencesSearchTheme` (all four tests) plus `TestFirefoxContentTheme::test_palette_is_exact`. Provenance: no reference screenshot shows the page; the token names and defaults are read 2026-10-27 from `moz-input-text.css` and `tokens-shared.css`; the token route reuses part 1's headless verification of the sheet's reach; the missing sunken bevel follows from the shadow stylesheet reading no shadow token (this theme's own choice); declaration checks do not establish rendered pixels. `tests/support/invariants.py` stays green.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_content_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The `about:preferences` block gains exactly one rule, `moz-input-search#searchInput`, setting exactly the five pinned custom properties with `!important`; no other rule, selector or colour changes anywhere in the sheet, and the sheet's palette stays exactly the pinned set (`#FFFFFF`/`#000000` were already members).
- `TestFirefoxPreferencesSearchTheme`'s four tests pass; `TestFirefoxPreferencesNavTheme`'s exact-set, custom-property and provenance tests pass against the renamed `REQUIRED_PREFERENCES_RULES`; `TestFirefoxContentTheme` stays green over the unchanged downloads and config bodies.
- `docs/invariants.md`'s new `## firefox` row cites the new test class and records the provenance exception and the bevel limitation; `tests/support/invariants.py` stays green.
- `make check` passes.

## Done

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

### Platinum desktoptheme timer digits: ship `widgets/timer.svg` for the Timer plasmoid's LCD numerals (planned 2026-10-27 by the plan role; the notes-paper plan, planned the same day, landed 2026-10-27 and set the pattern this plan follows — a separate `theme/desktoptheme/org.macos8.desktop/widgets/timer.svg` file, its own test suite, and append-only rows in the shared `tests/test_desktoptheme.py::SVG_CANVASES`, `tests/support/desktoptheme_paths.py` and `docs/invariants.md`)

**Goal.** The desktop theme ships twenty-nine `widgets/` SVGs but not `timer.svg`, so the optional Timer plasmoid (`org.kde.plasma.timer`, the countdown timer) draws its edit digits from Breeze's gradient LCD art. The installed plasmoid's `contents/ui/TimerEdit.qml` (read 2026-10-27 from the installed plasma-workspace) draws every digit as `KSvg.SvgItem` with `imagePath: "widgets/timer"` and `elementId: num + internal.digitSuffix` plus `elementId: "separator" + internal.digitSuffix`, where `digitSuffix` is `""` normally and `"_1"` in alert mode (`alertMode` = running with under a minute left, `main.qml`), and `num` scans the six `hh:mm:ss` characters `0`–`9`: the two suffix states double each of the ten digits, so the file needs exactly the twenty-two elements `0`–`9`, `0_1`–`9_1`, `separator`, `separator_1` (the installed default theme's extra `separatorB*`/`separatorC*` ids are legacy this plasmoid never requests). Until the file ships, both displays — and the alert recolour — fall back to Breeze.

**Grounding.** No reference screenshot shows a KDE timer (nor Mac OS 8.6's countdown equivalent), so the digits are platform-required adaptations. The `imagePath` and the twenty-two element ids are KDE-required, read from the installed plasmoid's `TimerEdit.qml` (`elementId: num + internal.digitSuffix` / `"separator" + internal.digitSuffix`, 2026-10-27). The recipe is the theme's flat black-glyph art (`widgets/checkmarks.svg`: stroke-only glyphs pinned by an invisible bounds rect). A seven-segment numeral has no Mac OS 8.6 retail surface, so the segment geometry is this theme's own choice; the two colours are the colour scheme's own semantic tokens — normal digits `#000000` reuse `[Colors:Tooltip] ForegroundNormal=0,0,0`, alert digits `#CC0000` reuse `ForegroundNegative=204,0,0` (`theme/color-schemes/MacOS8.colors`) — with the alert recolour's existence already grounded in the element-suffix split the plasmoid itself makes. Both the geometry and the colour provenance go in the file header and the test comments.

**Approach.** Add `theme/desktoptheme/org.macos8.desktop/widgets/timer.svg`: a tight 168x64 canvas — two stacked rows of ten 16x32 digit cells (the SvgItem renders each digit at a 1:2 wide:tall aspect, `digitW = digitH / 2`), plus one extra 8-wide column at `x=160` holding the two 8x32 separator cells (the separator renders at `digitW / 2` wide). Top row and top separator = normal state; bottom row = the `_1` alert states. Each `<g id="<n>">` digit group holds an invisible full-cell bounds rect (`fill="none"`, pinning the element bounds, the `checkmarks.svg` convention) plus one stroke-only `<path>` that draws the digit's lit seven-segment set in the 2px-stroke cell recipe: segment endpoints `a` top `(3,5)-(13,5)`, `b` upper-right `(13,5)-(13,15)`, `c` lower-right `(13,17)-(13,27)`, `d` bottom `(3,27)-(13,27)`, `e` lower-left `(3,17)-(3,27)`, `f` upper-left `(3,5)-(3,15)`, `g` middle `(3,16)-(13,16)`, with `stroke-width="2"` and square caps so segments meet without gaps, and `stroke="#000000"` on the normal row / `#CC0000` on the alert row. The per-digit lit sets: `0`=abcdef, `1`=bc, `2`=abged, `3`=abgcd, `4`=fgbc, `5`=afgcd, `6`=afgedc, `7`=abc, `8`=abcdefg, `9`=abfgcd (recorded verbatim so the implementer derives each `d` attribute mechanically). Each separator group holds an 8x32 bounds rect plus two filled `<circle>`s at `cx="4"`, `cy="10"` and `cy="22"`, `r="1.5"` — the colon dots — black normally, `#CC0000` in `separator_1`. The leading XML comment names the consumer (`org.kde.plasma.timer` `TimerEdit.qml` `imagePath: "widgets/timer"`), the alert `"_1"` suffix and its condition, the twenty-two KDE-required ids (noting the default theme's unused legacy separator ids), the missing reference surface (no screenshot shows a KDE timer), and the two colour provenances as above.

In `tests/support/desktoptheme_paths.py`, add `TIMER_SVG = os.path.join(PACKAGE, "widgets", "timer.svg")` beside `PAGER_SVG`. In `tests/test_desktoptheme.py`, import `TIMER_SVG` and append `("timer.svg", TIMER_SVG, 168, 64)` to `SVG_CANVASES`, extending the comment above it with one clause for the two-and-a-half-cell-tall timer rows; `TestSvgRootCanvas::test_registry_covers_every_shipped_svg` fails until the row lands, so the file cannot ship unregistered.

Add `tests/test_desktoptheme_timer.py` (pattern: `tests/test_desktoptheme_checkmarks.py` — attribute-level assertions via `svg_assertions.elements_by_id`/`attribute_values`, no rendering needed for stroke paths) with: `test_timer_declares_exactly_the_kde_required_ids` — the SVG's `id` attributes are exactly the twenty-two values above, in canvas order; `test_digits_are_seven_segment_paths` — a `DIGIT_SEGMENTS` mapping in the test pins the per-digit lit-set table above, and for every digit element the test re-derives the expected stroke-only `d` attribute from the pinned segment endpoints (a,b,c,d,e,f,g) and compares it verbatim, also pinning `stroke-width="2"`, `stroke-linecap="square"` and the bounds rect at (0,0)/(0,32) sized 16x32 with `fill="none"`; `test_normal_digits_are_black_and_alert_digits_are_the_negative_red` — row order pins that the ten normal digits stroke `#000000` and the ten `_1` digits plus `separator_1` stroke `#CC0000`, with the test's comment naming the `ForegroundNegative`/`ForegroundNormal` provenance so a future edit re-grounds it deliberately; and `test_separators_are_black_colon_dots` — `separator` holds exactly two black filled circles at the pinned coordinates and `separator_1` the same two in `#CC0000`, each with the 8x32 invisible bounds rect, so an element can silently gain or lose a dot only by failing the test.

In `docs/invariants.md`, append a row to the `## desktoptheme` table: `widgets/timer.svg` draws the Timer plasmoid's 22 LCD digits as seven-segment black-stroke numerals with red-alert `_1` variants. Test column: `tests/test_desktoptheme_timer.py::TestTimer`. Provenance exception: no reference screenshot shows a KDE timer; the twenty-two ids and the alert `_1` suffix are KDE-required (read from the installed plasmoid's `TimerEdit.qml`), the seven-segment geometry is this theme's own, and the two colours reuse the scheme's `ForegroundNormal`/`ForegroundNegative` tokens; `tests/support/invariants.py` stays green.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/timer.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `tests/test_desktoptheme_timer.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `widgets/timer.svg` holds exactly twenty-two elements — the ten digits, their ten `_1` variants and the two separators — on one 168x64 canvas, each digit a stroke-only seven-segment path using the pinned segment table and 2px square-capped stroke, each separator the two pinned colon dots, with the header comment naming the consumer, the KDE-required ids, the missing reference surface and the two colour provenances as above.
- `TestTimer`'s four tests pass and pin the id set, the digit geometry via the re-derived `d` attributes, the normal/alert colour split and the separator dots; `TestSvgRootCanvas`'s registry and root-canvas tests pass with the new `SVG_CANVASES` row; every other desktop-theme test stays green over the unchanged SVGs.
- `docs/invariants.md`'s new row cites `TestTimer` and records the provenance exception; `tests/support/invariants.py` stays green.
- `make check` passes.

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

## Done

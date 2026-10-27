# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
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
sheet under `theme/firefox/` (its `userChrome.css` copied and its profile preference written
only by the opt-in `install-firefox` target); and the render and fidelity tooling.
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

### Platinum desktoptheme notes paper: ship `widgets/notes.svg` for the Notes plasmoid's sticky-note papers (planned 2026-10-27 by the plan role; independent of the waiting Firefox preferences-panes plan — the two touch disjoint files (`theme/desktoptheme/org.macos8.desktop/*` and its suites versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and its suite), so either order merges; the theme's other unshipped plasmoid elements (the analog clock face, the timer digits, dragger, monitor, plot-background and the rest of the installed default theme's set) stay unplanned)

**Goal.** The desktop theme ships twenty-eight `widgets/` SVGs but not `notes.svg`, so the optional Notes plasmoid (`org.kde.plasma.notes`, KDE's Stickies analog — a yellow paper pinned to the desktop) falls back to Breeze's gradient papers. The installed plasmoid draws its full representation and its config thumbnails as `KSvg.SvgItem` with `imagePath: "widgets/notes"` and `elementId: Plasmoid.configuration.color + "-notes"` (`contents/ui/main.qml`, read 2026-10-27 from the installed plasma-workspace), over the ten note colours its config offers — `view.model: ["white", "black", "red", "orange", "yellow", "green", "blue", "pink", "translucent", "translucent-light"]` in `contents/ui/configAppearance.qml`, default `yellow` (`contents/config/main.xml`). Ship all ten papers as flat Platinum-style sticky notes, so every note colour draws this theme's art. The installed default theme is no help for two of them: it spells its element `transluscent-notes` (a typo this plasmoid never requests) and has no `translucent-light-notes` at all, so today those two colours draw nothing.

**Grounding.** No reference screenshot shows a sticky note (nor Mac OS 8.6's Stickies), so the papers are platform-required adaptations. The `imagePath` and the ten `<color>-notes` element ids are KDE-required, read from the installed plasmoid's `main.qml`, `configAppearance.qml` and `config/main.xml` (2026-10-27). The paper recipe is the theme's flat, black-outlined art: each paper is a flat fill inside a 1px `#000000` outline, the outline being the same black the checkmarks and arrows glyphs pin. The fills: `white` `#FFFFFF` and `black` `#000000` reuse the grounded view/label anchors; `yellow` `#FFFFCC` reuses the colour scheme's `[Colors:Tooltip]` role, `255,255,204` — the classic Platinum pale-yellow the scheme already ships as a KDE-required semantic role (QUESTIONS.md decision of 2026-10-08: recorded as not sampled, no retail balloon reference exists) — so the default note echoes the scheme's own pale-yellow rather than introducing a new value; the six remaining chromatic fills (`red` `#FF6666`, `orange` `#FFCC99`, `green` `#99FF99`, `blue` `#99CCFF`, `pink` `#FF99CC`) and the two translucent opacities (`translucent` = `#FFFFFF` at 0.5, `translucent-light` = `#FFFFFF` at 0.35) have no reference ground and are this theme's own choices, recorded in the file's header and pinned by the test so they cannot drift.

**Approach.** Add `theme/desktoptheme/org.macos8.desktop/widgets/notes.svg`: a tight 320x32 canvas holding ten 32x32 cells side by side (the convention `widgets/radiobutton.svg` uses for side-by-side elements, `widgets/checkmarks.svg` for the invisible bounds rect). Each element is a `<g id="<color>-notes">` holding an invisible full-cell bounds rect (`fill="none"`, pinning the element bounds KSvg scales to the note) plus one paper rect — `x="0.5" y="0.5" width="31" height="31"`, `fill` per the mapping above, `stroke="#000000"` `stroke-width="1"` — with the translucent papers' rect adding `fill-opacity` in place of a solid colour. The leading XML comment names the consumer (`org.kde.plasma.notes` `main.qml` `imagePath: "widgets/notes"`), the ten ids as KDE-required, the missing reference surface (no screenshot shows a sticky note), the yellow fill's `[Colors:Tooltip]` reuse with its not-sampled caveat, and the own-choice chromatic fills and translucent opacities. No nine-slice: the plasmoid's SvgItem scales the element, it does not read margins.

In `tests/support/desktoptheme_paths.py`, add `NOTES_SVG = os.path.join(PACKAGE, "widgets", "notes.svg")` beside `PAGER_SVG`. In `tests/test_desktoptheme.py`, import `NOTES_SVG` and append `("notes.svg", NOTES_SVG, 320, 32)` to `SVG_CANVASES`, extending the comment above it with one clause for the ten side-by-side 32x32 note cells; `TestSvgRootCanvas::test_registry_covers_every_shipped_svg` fails until the row lands, so the file cannot ship unregistered.

Add `tests/test_desktoptheme_notes.py` (pattern: `tests/test_desktoptheme_checkmarks.py` — attribute-level assertions via `svg_assertions.elements_by_id`/`attribute_values`, no rendering needed for flat rects) with: `test_notes_declares_exactly_the_kde_required_ids` — the SVG's `id` attributes are exactly the ten `<color>-notes` values the plasmoid's `view.model` names, in canvas order; `test_each_paper_is_a_flat_fill_with_a_black_outline` — a `NOTES_PAPERS` mapping pins all ten `(fill, fill-opacity, stroke)` triples (opacity `None` on the eight solid papers, `0.5` and `0.35` on the two translucent ones), and each element's paper rect is 31x31 at (0.5, 0.5) with `stroke="#000000"` and `stroke-width="1"`; `test_translucent_papers_are_the_only_opacity_carriers` — no element outside the two translucent papers carries a `fill-opacity`, so an opaque paper cannot silently turn translucent; and `test_yellow_paper_reuses_the_tooltip_role` — `yellow-notes`' fill is `#FFFFCC`, with the test's comment naming the `[Colors:Tooltip]` provenance so a future edit re-grounds it deliberately.

In `docs/invariants.md`, append a row to the `## desktoptheme` table: `widgets/notes.svg` draws the Notes plasmoid's ten sticky-note papers as flat fills inside a 1px black outline on ten side-by-side 32x32 cells. Test column: `tests/test_desktoptheme_notes.py::TestNotes`. Provenance exception: no reference screenshot shows a sticky note; the ten ids are KDE-required (read from the installed plasmoid's `main.qml`/`configAppearance.qml`/`config/main.xml`), the yellow fill reuses the scheme's not-sampled `[Colors:Tooltip]` pale-yellow, and the other chromatic fills and translucent opacities are this theme's own; `tests/support/invariants.py` stays green.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/notes.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `tests/test_desktoptheme_notes.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `widgets/notes.svg` holds exactly ten `<color>-notes` elements — `white`, `black`, `red`, `orange`, `yellow`, `green`, `blue`, `pink`, `translucent`, `translucent-light` — on one 320x32 canvas, each paper the flat-fill/1px-black-outline recipe with the pinned fills, and the header comment names the consumer, the KDE-required ids, the missing reference surface, the tooltip-role reuse and the own-choice values as above.
- `TestNotes`'s four tests pass and pin the ids, the fill/opacity/outline mapping, the opacity carriers and the yellow provenance; `TestSvgRootCanvas`'s registry and root-canvas tests pass with the new `SVG_CANVASES` row; every other desktop-theme test stays green over the unchanged SVGs.
- `docs/invariants.md`'s new row cites `TestNotes` and records the provenance exception; `tests/support/invariants.py` stays green.
- `make check` passes.

## Done

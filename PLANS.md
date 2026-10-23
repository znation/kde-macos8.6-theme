# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
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
NW-SE and NE-SW diagonal resize arrows, crosshair and circle-slash, not traced from Apple's
artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; drag-and-drop (`dnd-*`), grab, help, progress, zoom and the separate
`forbidden`/`no-drop` pointers still come from the fallback cursor theme; **system sounds** are out
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
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Platinum panel edit-mode chrome, part 1/2: ship the panel margin highlight (planned 2026-10-23 by the plan role; independent of the waiting cursor series)

**Goal.** The desktop theme ships no `widgets/margins-highlight.svg`, so while a panel is in
edit mode Plasma falls back to the default theme's blue translucent margin band. Ship our own
4x4 highlight tile: the flat `fill` and four corner wedges the panel's `SideMargin` reads, tinted
the reference selection lavender instead of Breeze blue. The panel's resize/slider handles
(`widgets/containment-controls.svg`) stay on the fallback theme in this part; part 2/2 covers
them. No reference screenshot shows panel edit mode, so the tile is our own art: the lavender is
the grounded selection colour `#CCCCFF`, and the 0.3 translucency is the default theme's
margin-highlight opacity.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg`, a 4x4 canvas with the
five ids the installed `org.kde.panel` `main.qml` `SideMargin` resolves: `fill` for the flat band
and `topleft`, `topright`, `bottomleft`, `bottomright` for the corner wedges (the component builds
`side + 'left'`/`'right'`, or `'top'`/`'bottom'` + side, so those four names are the only ones it
asks for).
  - `fill` is `<rect id="fill" x="0" y="0" width="4" height="4" fill="#CCCCFF"
fill-opacity="0.3"/>`.
  - The four corner ids are quarter-canvas triangles, each `fill="#CCCCFF"` and
`fill-opacity="0.3"`: `topleft` `M 0,0 H 4 L 0,4 Z`, `topright` `M 0,0 H 4 V 4 Z`, `bottomleft`
`M 0,0 V 4 H 4 Z`, `bottomright` `M 4,0 V 4 H 0 Z`.
  - Open the SVG with a comment naming the consumer, the five ids, and the provenance: the
consumer stretches each element over the margin band, `#CCCCFF` is the reference selection colour,
and 0.3 is the default theme's margin-highlight opacity.
- `tests/support/desktoptheme_paths.py`: add `MARGINS_HIGHLIGHT_SVG` pointing at
`widgets/margins-highlight.svg`.
- `tests/test_desktoptheme.py`: add `("margins-highlight.svg", MARGINS_HIGHLIGHT_SVG, 4, 4)` to
`SVG_CANVASES`, so `TestSvgRootCanvas`'s canvas, unique-id and self-contained loops cover it.
- New `tests/test_desktoptheme_marginshighlight.py`: pin the five ids, the flat `fill` rect at
`(0,0,4,4)`, each corner path's exact `d` and the four corner orientations, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and the absence of scripts, styles and external references.
- `README.md`: after the `widgets/action-overlays.svg` sentence, record
`widgets/margins-highlight.svg` as the translucent lavender panel-margin highlight shown in edit
mode, and note that the panel resize/slider handles still come from the fallback theme.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the margin highlight's flat fill
and four corner wedges share the grounded selection lavender at KDE's 0.3 highlight opacity, pinned
by `tests/test_desktoptheme_marginshighlight.py`; the provenance exception records that no
reference screenshot shows panel edit mode, so the five ids and 0.3 opacity are KDE-required while
the colour reuses the reference selection anchor.
- `PLANS.md`: in the scope-drift paragraph, change the desktop-theme count from twenty-four to
twenty-five widget SVGs, name the new margin highlight, and state that
`widgets/containment-controls.svg` still falls back.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg` (new),
`tests/test_desktoptheme_marginshighlight.py` (new), `tests/support/desktoptheme_paths.py`,
`tests/test_desktoptheme.py`, `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 4x4 square with the five ids present and unique, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and no script, style or external reference.
- `fill` is the full 4x4 rect and each corner id is its pinned quarter-canvas triangle; dropping
an id, nudging a path, changing a fill or changing the opacity fails a test.
- `TestSvgRootCanvas`'s registry covers the new file, and the README and `docs/invariants.md`
name it; `tests/invariants.py` accepts the new row and the scope-drift count is twenty-five.
- `make check` is green.

## Done

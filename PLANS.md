# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._


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

_None yet._


### Platinum GTK infobar: paint `Gtk.InfoBar` as the menu-bar band with the etched bottom rule (planned 2026-10-27 by the plan role; independent of the waiting Firefox Page Info groupbox plan — the two touch disjoint files (`theme/firefox/…/userChrome.css` and its suite versus `theme/gtk/…/gtk.css` and its suites), so either order merges)

**Goal.** Under both standalone GTK sheets a `Gtk.InfoBar` draws nothing of its own: the bar's content box keeps its transparent background over the window face, its labels take the toolkit's default black, and the `info`, `question`, `warning` and `error` message-type classes distinguish nothing — GTK 3 replaces the toolkit's compiled-in Adwaita rules entirely when `GTK_THEME` names this theme, and GTK 4's embedded `Default` theme defines no infobar rule at all. Give the bar the menu-bar band's recipe — the reference-grounded `#DDDDDD` face, black text and the bottom edge's `#888888`/`#FFFFFF` etch (`border-bottom: 1px solid #888888` with `box-shadow: inset 0 -1px #FFFFFF`, the exact declarations the GTK 4 sheet's `.toolbar, menubar` rule and the GTK 3 sheet's `toolbar, menubar` rule already draw) — so a message band reads as a Platinum band separated from the pane below it. All four message types take the same band: Platinum has no per-type message colour, and the type class names are GTK-required. The bar's close and action buttons keep the sheets' existing `button` paint, `:backdrop` stays out of scope as in the calendar plan, and GTK CSS needs no `appearance` reset — the paint is plain declarations.

**Grounding.** No reference screenshot shows a GTK infobar, so this is a platform-required adaptation; the recipe reuses only values the reference set already pins — the menu-bar face `#DDDDDD` (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_menu_bar_face`) and the etched pair (`tests/test_desktoptheme_line.py::TestLineReference`) — through the sheets' own menubar band rules, adding no new colour or metric. Measured live with PyGObject (GTK 3.24.49 and GTK 4.18.6, `GTK_THEME=org.macos8.desktop` with the sheet symlinked under a temp `XDG_DATA_HOME/themes`, on the session display): both toolkits build `infobar > revealer > box` — the infobar node carries the message-type style class (GTK 3 showed `horizontal, error`; GTK 4 showed `warning` with the node tree `infobar > revealer > box > [box, box, button.close > image]`; GTK 3's adds the message box holding the label and an action-area box beside it) — and the infobar node resolves `background-color` transparent with black text under this theme, so today the band is invisible and the type classes change nothing; the one `infobar > revealer > box` selector reaches both toolkits' band box, its `color` inherits to the message label, and the close and action buttons keep their own paint.

**Approach.** Append at the very end of `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, after each sheet's calendar rules, one comment and one rule (the same text in both sheets):

```css
/* An infobar draws the menu-bar band: the #DDDDDD face, black text and the
   etched bottom rule. The info, question, warning and error type classes all
   take this band; no reference screenshot shows a GTK infobar, and the type
   class names are GTK-required. */
infobar > revealer > box {
  background-color: #DDDDDD;
  color: #000000;
  border-bottom: 1px solid #888888;
  box-shadow: inset 0 -1px #FFFFFF;
}
```

Add one sentence to each sheet's header comment block, before its closing `*/` (after the spinner sentence): "An infobar band reuses the menu-bar band's face and etched bottom rule with black text; no reference screenshot shows a GTK infobar, and the four message-type class names are GTK-required, so all types take the same band." In `tests/support/gtk_theme_spec.py`, add beside `RUBBERBAND`:

```python
# An infobar draws the menu-bar band's face and etched bottom rule. No
# reference screenshot shows a GTK infobar; the GTK-required type class names
# take no per-type colour, so all four message types use this one band.
INFOBAR = {
    "background-color": FACE,
    "color": BLACK,
    "border-bottom": f"1px solid {ETCH_DARK}",
    "box-shadow": f"inset 0 -1px {WHITE}",
}
```

In `tests/support/gtk_rule_cases.py`, add `assert_infobar(self, selectors)` to `GtkSheetRuleCases` next to `assert_rubberband`, asserting each of the suite's own selectors against `INFOBAR`, and add infobar to the two docstring lists of assertions that take the suites' own selectors.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/support/gtk_rule_cases.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Each sheet ends with exactly the rule above (the same selector and the same four declarations, after its calendar rules), and each header comment gains the infobar sentence. Both sheets' `test_only_palette_hex_literals` tests stay green: the rule adds no hex literal outside each suite's pinned palette (`#DDDDDD`, `#000000`, `#888888` and `#FFFFFF` are already in it).
- `tests/test_gtk_theme.py::TestGtkTheme` gains `test_infobar` calling `self.assert_infobar(("infobar > revealer > box",))`, and `tests/test_gtk4_theme.py::TestGtk4Theme` gains the same test, both placed immediately after their `test_calendar`; each also asserts the sheets name no message type — no rule selector contains `.info`, `.question`, `.warning` or `.error` — and `assert_rule` pins each of the four declarations against `INFOBAR`.
- `docs/invariants.md` gains a row appended at the end of the `## gtk` table: both GTK sheets draw an infobar (`infobar > revealer > box`) as the menu-bar band — the `#DDDDDD` face, black text and the `#888888`/`#FFFFFF` etched bottom rule — with all four message types (`info`, `question`, `warning`, `error`) taking the same band, the close and action buttons keeping the `button` paint and `:backdrop` out of scope. Its test column names the two new `test_infobar` tests; its provenance records the missing reference surface (no screenshot shows a GTK infobar), the live-measured node tree and current transparent background (GTK 3.24.49 / GTK 4.18.6, 2026-10-27), the re-used reference-grounded values (`TestReferenceAnchors::test_menu_bar_face`, `TestLineReference`, the sheets' own menubar band rules), and the GTK-required class names. `tests/invariants.py` stays green.
- `make check` passes, and every existing rule in both sheets keeps its declarations and selector, including the menubar bands the infobar reuses.

### Platinum Kvantum dock titles: pin the `QDockWidget` title band and dock area (planned 2026-10-27 by the plan role; independent of the waiting GTK infobar plan — the two touch disjoint files (`theme/kvantum/org.macos8.desktop/*` and its suites versus `theme/gtk/…/gtk.css` and its suites), so either order merges)

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig` defines no `[Dock]` or `[DockTitle]` section, while the installed engine's themes define both (`/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig` and `/usr/share/Kvantum/KvAdapta/KvAdapta.kvconfig`, read 2026-10-27): `[Dock]` is the area a `QDockWidget` occupies inside a main window and `[DockTitle]` is the header band Qt's `CE_DockWidgetTitle` paints at the top of every dock panel — the panel headers Qt Creator, Krita and similar Qt applications show. With both sections absent, Kvantum resolves the two surfaces from its compiled-in defaults, so a Qt dock's header band and dock area are the engine's, not the theme's. Write both sections so the surfaces are this theme's own: the docking area draws nothing (`frame=false`, `interior=false`, as KvantumAlt pins it, so the panel body keeps the `#DDDDDD` window face), and the header band becomes the menu-bar band read in Kvantum terms — the `#DDDDDD` window face with a plain black label and the bottom edge's etched rule (a `#FFFFFF` row above a 1px `#888888` row at the band's very bottom), the same pair `widgets/line.svg` and the GTK sheets' menubar bands pin. Neither Kvantum-requirement colour nor metric is new to the pinned palette.

**Grounding.** No reference screenshot shows a Qt dock panel, palette or its header band, so this is a Kvantum-required adaptation recorded as such: the section and key names (`[Dock]`, `[DockTitle]`, `inherits`, `frame.*`, `interior.*`, `text.*`) are Kvantum's, read from the two installed themes above (KvAdapta ships an unused `dock-normal`/`dock-focused-*` element set and also sets `text.bold=true`, showing the state ids the engine requests are `normal` and `focused`; responsibility for the paint is ours). The `#DDDDDD` face and `#000000` label reuse the `[GeneralColors]` `window.color` and `text.color` roles pinned by `tests/test_kvantum_config.py::TestGeneralColors`, themselves grounded; the etched pair reuses the reference-grounded `#888888`/`#FFFFFF` rule that `tests/test_desktoptheme_line.py::TestLineReference` re-derives and the GTK menubar bands draw. Chosen values with no reference ground: the band's 0/2/0/0 frame margins (top/left/right/bottom), the 2/3 text margins and the plain (non-bold) label — the reference set shows no dock header to sample a spacing or a weight from, KvantumAlt's bold white-on-default header is clearly not Platinum, and these three are recorded as this theme's own choice.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, after `[StatusBar]` (the file's last section), append two commented sections:

```
[Dock]
inherits=PanelButtonCommand
frame=false
interior=false

[DockTitle]
inherits=PanelButtonCommand
frame=true
frame.element=dock
frame.top=0
frame.bottom=2
frame.left=0
frame.right=0
interior=false
text.normal.color=#000000
text.focus.color=#000000
text.margin.top=2
text.margin.bottom=2
text.margin.left=3
text.margin.right=3
```

`[Dock]` mirrors `[StatusBar]` (flat window face, no bevel). `[DockTitle]` draws through one nine-sliced frame element `dock` with `interior=false`, so the label sits on the bare `#DDDDDD` window background and the band's only art is the bottom 2px etched rule: the `frame.bottom=2` margin holds the two rule rows fixed while everything above stretches freely. Treating the band this way reuses exactly the established machinery: `[Splitter]` already ships zero-height slices with frame margins 0.

In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, after the `toolbar` frame groups, append the `dock` element groups for the two states (`dock-normal`, `dock-focused`, centre ids plus all eight `-top`/`-bottom`/`-left`/`-right`/`-topleft`/`-topright`/`-bottomleft`/`-bottomright` slice ids each, in the file's nine-slice layout): each centre group is a flat `#DDDDDD` rect (20x18), each `-bottom` group is two 20x1 rows (`#FFFFFF` at y=0, `#888888` at y=1), and the six margin-degenerate slices (top/left/right and all four corners, x-height or width 0 under the 0 margins) are `fill="none"` one-px rects documented as invisible degenerate slices, the way the size-grip bounds rects read. Extend the SVG header comment's surface-controls enumeration with the dock band. No fill outside the existing set appears: `#DDDDDD` and `#FFFFFF` are in `PLATINUM_FILLS`, `#888888` is the named `CHECKBOX_SHADOW` extra and `"none"` is already accepted.

Pin the sections in `tests/support/kvantum_config_spec.py`: add `"Dock": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false"}` to `FRAMELESS_SECTIONS` (pinning the `inherits` target like `[StatusBar]`), `"DockTitle": {"frame.element": "dock"}` to `SURFACE_CONTROL_CONFIG`, and `"DockTitle": {"frame": "true", "frame.top": "0", "frame.bottom": "2", "frame.left": "0", "frame.right": "0", "interior": "false", "text.normal.color": "#000000", "text.focus.color": "#000000", "text.margin.top": "2", "text.margin.bottom": "2", "text.margin.left": "3", "text.margin.right": "3"}` to `VALUE_KEYS`, so `TestSectionCoverage`, `TestValueKeys` and `test_every_key_is_pinned` stay exhaustive.

In `tests/test_kvantum_svg.py`: add `"dock": ("normal", "focused")` to `FRAME_STATES`; add a `test_dock_band_draws_the_window_face_and_the_etched_rule` method to `TestSvg` asserting, for both states, that `dock-normal-centre` (and `dock-focused-centre`) equals `(_rect("0", "0", "20", "18", "#DDDDDD"),)` and each `-bottom` slice equals `(_rect("0", "0", "20", "1", "#FFFFFF"), _rect("0", "1", "20", "1", "#888888"))` via `_drawing_elements`, reusing the check-state pin style of `INTERIOR_GROUP_SHAPES` — so a rule row deleted, reordered, rescaled or repainted (all its colours are palette members the fill-set test cannot see) fails.

In `tests/test_kvantum_config_elements.py`, add a `TestDockSurface` class beside `TestToolboxTabSurface` pinning: `Dock`'s `frame` and `interior` are `"false"` and its `inherits` is `"PanelButtonCommand"`; and `[DockTitle]`'s `frame.element` resolves to `"dock"` and differs from KvantumAlt's unpinned default by asserting `frame.bottom` is `"2"` while `frame.top`, `frame.left` and `frame.right` are `"0"`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_svg.py`, `tests/test_kvantum_config_elements.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- Both sections exist at the end of the `.kvconfig` with exactly the keys above, each preceded by a comment naming the section and recording the no-reference-surface provenance sentence: no reference screenshot shows a Qt dock panel; `[Dock]`/`[DockTitle]` are Kvantum-required (read from the installed KvantumAlt and KvAdapta themes); the face and label reuse the grounded `[GeneralColors]` window/text colours; the etched pair reuses the reference-grounded rule pinned by `TestLineReference`; the 0/2/0/0 margins, 2/3 text margins and plain label are this theme's own choices.
- The SVG ships both `dock` states' nine ids; `TestSvg::test_every_frame_element_ships_its_centre_and_eight_slices`, `test_every_element_the_config_names_has_art` and `test_uses_exactly_the_platinum_palette` stay green, and the new band/rule shape test holds for both states.
- `tests/test_kvantum_config.py::TestSectionCoverage`, `TestFrameMargins` and `TestValueKeys`, `tests/test_kvantum_config_elements.py` (including the new `TestDockSurface`), and every existing Kvantum test pass with no other section, key or element changed.
- `docs/invariants.md` gains a row at the end of the `## kvantum` table: the `QDockWidget` docking area draws nothing (`frame=false`/`interior=false`, flat window face) and its `CE_DockWidgetTitle` header band is the `#DDDDDD` window face with a plain black label and the etched `#FFFFFF`-over-`#888888` bottom rule, with no hover or pressed state. Its test column cites `TestDockSurface` and the new `TestSvg` band test; its provenance exception records the missing reference surface, the Kvantum-required names read from the installed themes, the grounding reuse, `TestGeneralColors` and `TestLineReference`, and that config and SVG checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`'s Kvantum sentence that names the toolbar buttons, toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders, toolbox tabs and the status bar names the dock header band among the surfaces the style maps to the Platinum art.
- `make check` passes.

## Done

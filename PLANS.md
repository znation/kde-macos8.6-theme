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
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Platinum GTK menu bars: give GTK 4 the etched menu-bar face and space both toolkits' titles like the reference (planned 2026-10-24 by the plan role; independent of the waiting GTK disclosure-arrow plan)

**Goal.** Both standalone GTK sheets load no stock rules, so a GTK menu bar gets only what we write. The GTK 3 sheet's `toolbar, menubar` rule gives the bar the `#DDDDDD` face with the etched `#888888`/`#FFFFFF` bottom rule. Its `menuitem:hover, .menuitem:hover` rule paints a hovered or open title `#CCCCFF`. The titles themselves get no padding, so they sit edge to edge. The GTK 4 sheet's `.toolbar` rule does not match a `GtkPopoverMenuBar` (CSS node `menubar > item`), so a GTK 4 menu bar has no Platinum face and its open title gets no highlight. Stock rules, which we never load, are GTK 4 `Default-light.css` `menubar > item { min-height: 16px; padding: 4px 8px; }` with `menubar > item:selected { box-shadow: inset 0 -3px …; }`, and GTK 3 Adwaita `gtk-contained.css` `menubar > menuitem { min-height: 16px; padding: 4px 8px; }`. Give both toolkits the Platinum menu-bar title geometry that the desktop theme already re-derives from the reference: `widgets/menubaritem.svg`'s 7px left/right margins (pinned to the reference title gaps by `tests/test_desktoptheme_menubaritem.py::TestMenuTitleSpacingMatchesReference::test_horizontal_margin_is_half_the_mean_gap`) and its 3px top/bottom margins. Give GTK 4 the face and the flat `#CCCCFF` open title (the colour the menubaritem `pressed` slices are pinned to).

**Design (decided; do not widen).**
- GTK 4: change the selector `.toolbar {` to `.toolbar, menubar {`, keeping its three declarations. Add `menubar > item { padding: 3px 7px; }` and `menubar > item:selected { background-color: #CCCCFF; }` right after it. GTK 4 marks an open menu-bar title `:selected`; stock uses that state too.
- GTK 3: add `menubar > menuitem { padding: 3px 7px; }` right after the `toolbar, menubar` rule. The open/hovered title colour already comes from `menuitem:hover`, so add no colour rule.
- Out of scope: `:disabled` title colours (no reference shows one), `:backdrop`, `min-height`, the menus' own popover bodies (already styled), and `-GtkWidget-window-dragging`.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the selector change and the two new rules. In the header comment, add one sentence: menu-bar titles take `widgets/menubaritem.svg`'s 3px/7px margins, re-derived from the reference title gaps, and an open title takes the `#CCCCFF` selection; the `menubar > item` node and `:selected` state are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the one new rule, plus the matching header sentence (naming `menubar > menuitem`, and saying the open title's colour comes from the existing `menuitem:hover` rule).
- `tests/support/gtk_theme_spec.py`: add `assert_menubar_titles(self, selector)` at the end of `GtkSheetRuleCases`. It parses `MENUBARITEM_SVG` (from `support.desktoptheme_paths`) with `support.svg_case.parse_svg`, reads `normal-hint-top-margin` height and `normal-hint-left-margin` width through `svg_assertions.rect_geometry` (as `test_horizontal_margin_is_half_the_mean_gap` does), and calls `assert_rule(selector, {"padding": f"{top}px {left}px"})`. The padding is then derived from the pinned SVG rather than restated. Import them at module top the way `tests/test_desktoptheme_menubaritem.py` does (`svg_assertions` is the `tests/svg_assertions/` package).
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_menubar_titles`, calling `self.assert_menubar_titles("menubar > menuitem")`. (The open-title `#CCCCFF` from `menuitem:hover` is already pinned in that module; add nothing for it.)
- `tests/test_gtk4_theme.py`: rename `test_toolbar` to `test_toolbar_and_menubar`, looping over `(".toolbar", "menubar")` like the GTK 3 test of the same name. Add `test_menubar_titles`, calling `self.assert_menubar_titles("menubar > item")`, then `self.assert_rule("menubar > item:selected", {"background-color": SELECTION})`, importing `SELECTION` from `support.platinum_palette` if the module does not already.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets pad menu-bar titles with `widgets/menubaritem.svg`'s 3px/7px margins, and GTK 4 paints the menu bar with the etched Platinum face and an open title `#CCCCFF`. Tests: both `test_menubar_titles` cases and `tests/test_gtk4_theme.py::TestGtk4Theme::test_toolbar_and_menubar`. Provenance: the 7px is re-derived from the reference title gaps by `TestMenuTitleSpacingMatchesReference`, and the `#CCCCFF` by `TestReferenceAnchors.test_selection_background`. The 3px vertical margin is the desktop theme's menubaritem contract, not measured on a GTK widget, since no reference screenshot shows one. The node names and the `:selected` state are GTK-required.

**Acceptance criteria.**
- The GTK 4 sheet matches `menubar` with the toolbar's face, border and inset shadow, pads `menubar > item` `3px 7px`, and paints `menubar > item:selected` `#CCCCFF`. The GTK 3 sheet pads `menubar > menuitem` `3px 7px`.
- Changing either sheet's title padding, or the menubaritem margins without updating the sheets, fails a `test_menubar_titles` case. Dropping `menubar` from the GTK 4 face rule fails `test_toolbar_and_menubar`.
- The sheets' existing hex-literal allow-list tests still pass, since no new colour is introduced. The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

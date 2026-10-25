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

### Platinum GTK 4 menu-button arrows: draw the shipped down and up triangles on GTK 4 menu buttons (planned 2026-10-24 by the plan role; independent of the waiting GTK submenu-arrow plan)

**Goal.** The GTK 4 sheet does not style a `Gtk.MenuButton`'s arrow. The stock rules that give it an icon are in `Default-light.css`, which our standalone sheet never loads, so a menu button with no icon or label of its own shows an empty face. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): a bare `Gtk.MenuButton()` parented in a presented `Gtk.Window` maps `menubutton > button > arrow.down` at 16x16, but snapshotting that arrow through `Gtk.WidgetPaintable` gives no render node, so nothing is drawn. Under `GTK_THEME=Adwaita` the same arrow renders a dark triangle. Stock `Default-light.css` (`gresource extract /usr/lib/x86_64-linux-gnu/libgtk-4.so.1 /org/gtk/libgtk/theme/Default/Default-light.css`) has `menubutton arrow { min-height: 16px; min-width: 16px; }` and one `-gtk-icon-source: -gtk-icontheme(...)` rule per direction class: `.none` uses `open-menu-symbolic`, `.down` `pan-down-symbolic`, `.up` `pan-up-symbolic`, `.left` `pan-start-symbolic` and `.right` `pan-end-symbolic`.

I appended the two rules below to a `cp -rL` copy of the theme and re-ran the snapshot. The arrow then renders a 16x16 texture, with dark opaque pixels (every channel below 170) filling the shipped triangles. For the default direction (down), they fill x=4..11, y=5..9, widest at the top. After `set_direction(Gtk.ArrowType.UP)` they fill x=4..11, y=6..10, widest at the bottom. The arrow stayed 16x16 without a `min-width`/`min-height` rule, so the plan adds none.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after the `combobox arrow, dropdown arrow` rule, add
  - `menubutton arrow.down { -gtk-icon-source: url("../assets/arrow-down.svg"); }`
  - `menubutton arrow.up { -gtk-icon-source: url("../assets/arrow-up.svg"); }`
- Both assets already ship, and their triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes, as the combo box arrow's does. So this plan adds no asset, Makefile, fixture or README-count change.
- Out of scope:
  - `arrow.none` (the hamburger `open-menu-symbolic` glyph) and `arrow.left`/`arrow.right`: no shipped asset fits, and the down direction is GTK's default.
  - The GTK 3 menu button: GTK 3 builds its arrow as a `GtkImage` from the icon theme, not a CSS `arrow` node.
  - Hover and disabled glyph colours, and the menu button's face.
- No reference screenshot shows a GTK menu button. The reference's pop-up menus show a double arrow (`TestComboBoxReference`). So the single triangle is the same KDE-required shape the combo box and dropdown arrows already use. Say so in the provenance.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the two rules above. The header comment's sentence "The combo box and dropdown arrows load from the shared assets/arrow-down.svg ..." also names the menu button's down arrow, plus its up arrow from `assets/arrow-up.svg`.
- `tests/support/gtk_theme_spec.py`: next to `COMBO_ARROW`, add `MENUBUTTON_ARROWS = {"menubutton arrow.down": {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}, "menubutton arrow.up": {"-gtk-icon-source": 'url("../assets/arrow-up.svg")'}}`, with a one-line comment.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_menubutton_arrows`, which imports `MENUBUTTON_ARROWS` and calls `self.assert_rule(selector, expected)` for each entry. Both URLs are already in the `test_stands_alone` URL set, so that set stays unchanged.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section.
  - Guarantee: the GTK 4 sheet draws a menu button's down and up arrows from the shipped `arrow-down.svg` and `arrow-up.svg` triangles.
  - Test: `tests/test_gtk4_theme.py::TestGtk4Theme::test_menubutton_arrows`.
  - Provenance: no reference screenshot shows a GTK menu button. The triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes, as the combo box arrow does. The node and direction-class names are GTK-required.

**Acceptance criteria.**
- Both rules exist exactly as described, and the GTK 3 sheet is unchanged.
- Each of these fails `test_menubutton_arrows`: removing either rule, renaming either selector, or swapping either URL.
- `test_only_palette_hex_literals`, `test_no_universal_selector` and `test_stands_alone` still pass in the GTK 4 suite, `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

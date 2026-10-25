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

### Platinum GTK 3 popover menus: draw a popover menu row's check and radio without the box, as GTK 3 menus and GTK 4 popovers do (planned 2026-10-24 by the plan role; independent of the waiting GTK spinner plan)

**Goal.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the boxless rule (`menu menuitem check, menu menuitem radio`) covers only `GtkMenu` rows. A check or radio row in a GTK 3 popover menu (`GtkModelButton`, CSS node `modelbutton` with a `check` or `radio` child) still matches the generic `check, radio` rule, so it draws the raised button face inside a menu. The GTK 4 sheet already strips that face with `popover modelbutton check, popover modelbutton radio, popover.background modelbutton check, popover.background modelbutton radio`. `docs/invariants.md`'s GTK 3 sheet row already promises faces that are "boxless in menus".

I measured this live with PyGObject and GTK 3 under `GTK_THEME=org.macos8.desktop`, through a `Gtk.StyleContext` set to a `Gtk.WidgetPath` of named nodes:
- `window > menu > menuitem > check` has a transparent background and a 0 margin.
- `window > popover > modelbutton > check` has background `rgb(221,221,221)` (the raised face) and a 4px left margin.
- `window > popover > modelbutton > radio` has background `rgb(255,255,255)` (the radio face) and a 4px left margin.

**Design (decided; do not widen).**
- In `gtk-3.0/gtk.css`, extend the selector list of the existing `menu menuitem check, menu menuitem radio` rule with `popover modelbutton check, popover modelbutton radio`. Leave its four declarations unchanged (`margin: 0; background-color: transparent; border-color: transparent; box-shadow: none;`).
- `check:checked` and `radio:checked` keep supplying the shipped `assets/checkmark.svg` and `assets/bullet.svg` glyphs, so a checked row shows the bare glyph. GTK 3's popover node is `popover.background`, which `popover` already matches, so no `.background` selector is needed.
- In the header comment's popover sentence ("A popover menu row (modelbutton) takes the same #CCCCFF highlight …"), add that a popover row's check and radio show the bare glyph, as a menu row's do.
- Out of scope:
  - GTK 3 popover row padding and min-height. The only open-menu reference, `desktop_archiveorg8.6hd.png`, is scaled: its Apple-menu rows are 14px apart and its text is antialiased, so it cannot ground a row metric.
  - GTK 3 popover submenu arrows (`modelbutton arrow.right`/`.left`).
  - Any GTK 4 change.
- No new asset, colour or metric is added, so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README counts do not change.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: the selector list and the header sentence.
- `tests/test_gtk_theme.py`: in `TestGtkTheme.test_menu_check_and_radio_are_boxless`, add `"popover modelbutton check"` and `"popover modelbutton radio"` to the selector tuple. Each is checked against the existing `MENU_CHECK` from `tests/support/gtk_theme_spec.py`.
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 sheet draws a popover menu row's (`popover modelbutton`) check and radio without the raised face, margin or bevel, as it does for a `menu menuitem` row.
  - Test: `tests/test_gtk_theme.py::TestGtkTheme::test_menu_check_and_radio_are_boxless`.
  - Provenance: no reference screenshot shows a GTK popover. The rule reuses the existing boxless menu-check declarations and adds no colour or metric.

**Acceptance criteria.**
- The GTK 3 sheet's boxless rule names both popover selectors with the unchanged `MENU_CHECK` declarations.
- Removing either popover selector, or changing any of the four declarations, fails `test_menu_check_and_radio_are_boxless`.
- A live `Gtk.StyleContext` probe of `window > popover > modelbutton > check` reports a transparent background and a 0 margin.
- `test_icon_sources_point_at_shipped_assets`, `test_only_palette_hex_literals` and the rest of `tests/test_gtk_theme.py` still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

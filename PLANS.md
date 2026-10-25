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

### Platinum GTK submenu arrows: draw the reference's solid black submenu triangle on GTK 3 and GTK 4 menu rows that open a submenu (planned 2026-10-24 by the plan role; independent of the waiting GTK calendar plan)

**Goal.** Neither standalone GTK sheet styles a menu row's submenu arrow, and the stock rules that give it an icon and a size are in sheets we never load. So a menu row that opens a submenu shows no arrow. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`):
- GTK 3: a style context on the path `menu > menuitem > arrow` resolves `min-width` and `min-height` to `0`, so the arrow has no size. Under `GTK_THEME=Adwaita` both are `16`. Stock `gtk-contained.css` has `menu menuitem arrow { min-height: 16px; min-width: 16px; }` and `-gtk-icon-source: -gtk-icontheme("pan-end-symbolic")` for `:dir(ltr)`.
- GTK 4: a `Gtk.PopoverMenu` built from a `Gio.Menu` with one `append_submenu` row maps that row's `modelbutton > arrow.right` at 16x16. But snapshotting it through `Gtk.WidgetPaintable` gives no render node at all, so nothing is drawn. Stock `Default-light.css` has `modelbutton.flat arrow.right { -gtk-icon-source: -gtk-icontheme("go-next-symbolic"); }`.
- The reference's open Apple menu (`desktop_archiveorg8.6hd.png`) draws a solid black 5x9 right triangle on each submenu row. The icon theme already ships that triangle as `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (path `M 6,3 L 6,11 L 10,7 Z`, fill `#000000`), and `tests/test_icon_arrow_reference.py::TestSubmenuArrowReference` pins it to the reference. The GTK assets' `arrow-right.svg` (`M 5,4 L 5,12 L 11,8 Z`, the disclosure arrow) is a different shape, so do not reuse it here.

With the rules below and a scratch `assets/submenu-arrow.svg` (that same path) appended to a `cp -rL` copy of the theme:
- GTK 3: the `menu > menuitem > arrow` context resolves `min-width` and `min-height` to `16`.
- GTK 4: the arrow snapshot renders a 16x16 texture with opaque dark pixels (every channel below 170) inside x=6..9, y=3..9.

**Design (decided; do not widen).**
- New asset `theme/gtk/org.macos8.desktop/assets/submenu-arrow.svg`: a 16x16 root (`width="16" height="16" viewBox="0 0 16 16"`, root element first, no `<?xml` prolog needed) holding one `<path d="M 6,3 L 6,11 L 10,7 Z" fill="#000000"/>`. Put its comment inside the root, as `arrow-right.svg` does. The comment says the path copies the icon theme's reference-pinned `16x16/actions/go-next-symbolic.svg` triangle (the open Apple menu's 5x9 submenu arrow) and names the test that pins the copy. GTK loads it directly, so it does not depend on which icon theme the user selected.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `menu menuitem check, menu menuitem radio` rule, add `menu menuitem arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/submenu-arrow.svg"); }`.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after the `popover modelbutton check, popover modelbutton radio, popover.background modelbutton check, popover.background modelbutton radio` rule, add `popover.menu modelbutton > arrow.right { -gtk-icon-source: url("../assets/submenu-arrow.svg"); }`. GTK 4 already gives the node its 16px size.
- Out of scope: margins between label and arrow, the GTK 4 sliding-submenu back arrow (`arrow.left`, which the reference never shows), right-to-left mirroring, `menubutton arrow`, and hover or disabled arrow colours. The arrow stays black on the `#CCCCFF` hover fill, as in the reference.

**Files touched.**
- The new asset, and both sheets' rules above. Add one sentence to each sheet's header comment: the submenu arrow loads the shared `assets/submenu-arrow.svg`, the icon theme's reference-grounded submenu triangle.
- `tests/support/gtk_theme_spec.py`:
  - Add `SUBMENU_ARROW = {"-gtk-icon-source": 'url("../assets/submenu-arrow.svg")'}` next to `EXPANDER_EXPANDED`.
  - Add `assert_submenu_arrow(self, selectors, sized)` to `GtkSheetRuleCases`, next to `assert_expander_arrows`. Each selector must match `SUBMENU_ARROW`. When `sized` is true, it must also match `min-width: 16px` and `min-height: 16px`.
  - Add the submenu arrow to the docstrings' list of assertions that take the suites' own selectors.
- `tests/test_gtk_theme.py`:
  - Add `TestGtkTheme.test_submenu_arrow`, calling `self.assert_submenu_arrow(("menu menuitem arrow",), sized=True)`.
  - Add `'"../assets/submenu-arrow.svg"'` to `test_icon_sources_point_at_shipped_assets`.
  - Add `SUBMENU_ARROW_SVG = THEME_DIR / "assets" / "submenu-arrow.svg"` beside `ARROW_RIGHT`, and include it in the `TestArrowGlyphs` stand-alone, root-first, 16px-canvas and black-fill checks.
  - Add `TestArrowGlyphs.test_submenu_arrow_copies_the_icon_theme_triangle`. It parses the new asset and `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg`, and asserts that each has exactly one `path`, with equal `d` and `fill`.
- `tests/test_gtk4_theme.py`:
  - Add `TestGtk4Theme.test_submenu_arrow`, calling `self.assert_submenu_arrow(("popover.menu modelbutton > arrow.right",), sized=False)`.
  - Add the new URL to the `test_stands_alone` URL set.
- Install wiring for the twelfth GTK file:
  - `Makefile` `install_gtk`: add the staging `install` line, the commit `mv` line and the trap's staging path for `assets/submenu-arrow.svg`, written the same way as `arrow-right.svg`.
  - `Makefile` `_uninstall`: add the file and its `.submenu-arrow.svg.staging` to the GTK `rm -f`.
  - `tests/support/gtk_fixtures.py`: add the file to `SHIPPED_FILES`.
  - `tests/test_gtk_install.py`: add `"assets/submenu-arrow.svg": "assets/.submenu-arrow.svg.staging"` to `STAGING_PATHS`.
- `README.md`:
  - "the eight shared check, radio, combo box, menu arrow, disclosure arrow and title-button box assets" becomes nine, naming the submenu arrow.
  - Both "eleven" GTK file counts become "twelve".
- `docs/invariants.md`:
  - The GTK install row's "eleven GTK theme files" becomes "twelve".
  - Add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets draw a submenu row's arrow from the shipped `submenu-arrow.svg`, whose path is the icon theme's reference-pinned submenu triangle, and GTK 3 sizes it 16x16. Tests: the two `test_submenu_arrow` tests and `TestArrowGlyphs.test_submenu_arrow_copies_the_icon_theme_triangle`. Provenance: the 16px canvas and the node names are GTK-required, and the triangle comes from `TestSubmenuArrowReference`.

**Acceptance criteria.**
- The asset and both rules exist exactly as described, and `make install-gtk` installs the asset beside the other assets, which `make uninstall` removes.
- Each of these fails a test: removing either rule, renaming its selector or its URL, dropping either GTK 3 min size, or changing the asset's path or fill (or the icon theme's 16x16 `go-next-symbolic.svg` path alone).
- `test_only_palette_hex_literals` and `test_no_universal_selector` still pass in both suites, the GTK install tests pass with the new file, `tests/invariants.py` accepts the edited rows, and `make check` is green.

## Done

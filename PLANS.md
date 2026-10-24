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

### Platinum GTK view backgrounds: paint tree, list, icon and text views on the white content field (planned 2026-10-24 by the plan role; independent of the waiting GTK spin-button plan)

**Goal.** Both opt-in GTK sheets are standalone (they import nothing), and neither gives a view its base fill: no rule names `.view`, `list` or `textview text`, so a `GtkTreeView`, `GtkTextView`, `GtkIconView`, `GtkListBox` (and in GTK 4 `GtkListView`, `GtkColumnView`, `GtkGridView`) paints transparently over the `#DDDDDD` window face. Stock GTK paints them in sheets we never load: GTK 3 Adwaita's `gtk-contained.css` (`libgtk-3.so.0` gresource) has `.view, iconview, .view text, iconview text, textview text { color: black; background-color: #ffffff; }` and `list { … background-color: #ffffff; }`; GTK 4's `Default/Default-light.css` has `.view, iconview, textview > text { … background-color: #ffffff; }` and `listview, list { … background-color: #ffffff; }`. The row rules already assume this base: their comment says "a hovered row stays the view background". Mac OS 8.6's window content area is white: the `[Colors:View] BackgroundNormal` anchor `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_window_view_background` re-derives `#FFFFFF` from the reference, already `WHITE` in `tests/support/platinum_palette.py` and the sheets' `theme_base_color`. Paint views white with black text. No new colours are needed.

**Design (decided; do not widen).** Checked with PyGObject on this machine: GTK 3 `TextView`, `TreeView` and `IconView` carry the `view` class and `ListBox` is the class-less `list` node (GTK 3's text view also has a `text` child node, which stock paints too); GTK 4 `TextView`, `ListView`, `ColumnView`, `TreeView`, `IconView` and `GridView` all carry `view` and `ListBox` is `list`. So the selector lists are GTK 3 `.view, textview text, list` and GTK 4 `.view, list`. Declarations: `background-color: #FFFFFF; color: #000000;` only — no border, padding or `:backdrop`/`:disabled` variant (out of scope). Specificity keeps existing rules on top: `.view` and `list` are weaker than `treeview.view:hover`, `treeview.view:selected` and the `list row.activatable…` / `listview > row.activatable…` rules, and the header buttons are not `view` nodes, so their `#DDDDDD` face is untouched.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: add `.view, textview text, list { background-color: #FFFFFF; color: #000000; }` immediately before the `treeview.view:hover, list row.activatable:hover` rule. In the header comment, say views paint the reference-grounded white content field (the colour scheme's View background) with black text, that no reference screenshot shows a GTK widget, and that the `view` class and node names are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `.view, list { background-color: #FFFFFF; color: #000000; }` immediately before the `listview > row.activatable:hover` rule, with the matching header-comment sentence.
- `tests/support/gtk_theme_spec.py`: beside `ROW_HOVER`, add `VIEW_BACKGROUND = {"background-color": WHITE, "color": BLACK}` with a comment naming the `test_window_view_background` anchor; add `assert_view_background(self, selectors)` to `GtkSheetRuleCases` after `assert_text_selection`, asserting `VIEW_BACKGROUND` on each selector; mention view-background in the class docstring's list of selector-taking assertions.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_view_background` calls `self.assert_view_background((".view", "textview text", "list"))`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_view_background` calls `self.assert_view_background((".view", "list"))`.
- `docs/invariants.md`: a new `## gtk` row at the end of the gtk section: both GTK sheets paint views (`.view`, `list`, and GTK 3's `textview text`) white with black text; tests are the two `test_view_background` cases; provenance: the white is re-derived by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_window_view_background`, no reference screenshot shows a GTK widget, and the class and node names are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet carries `.view`, `textview text` and `list` with `background-color: #FFFFFF` and `color: #000000`; the GTK 4 sheet carries `.view` and `list` with the same declarations; both `test_view_background` cases pin them through `assert_view_background`.
- The existing row-hover, row-selection, tree-header and text-selection tests still pass unchanged, and no new hex literal appears in either sheet (`#FFFFFF` and `#000000` are already used).
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK disclosure arrows: point tree-view and expander arrows at the Platinum right and down triangles (planned 2026-10-24 by the plan role; independent of the waiting GTK view-background plan)

**Goal.** Neither standalone GTK sheet names an expander, so a tree view's row expander and a `GtkExpander`'s arrow get no `-gtk-icon-source` from us. Stock GTK sets them only in sheets we never load: GTK 3 Adwaita's `gtk-contained.css` (`libgtk-3.so.0` gresource) has `treeview.view.expander { -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); … }`, `treeview.view.expander:checked { … "pan-down-symbolic" }` and `expander title > arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); }` with a matching `:checked` rule; GTK 4's `Default/Default-light.css` has `columnview.view.expander, treeview.view.expander { min-width: 16px; min-height: 16px; -gtk-icon-source: … }` and bare `expander { min-width: 16px; min-height: 16px; -gtk-icon-source: -gtk-icontheme("pan-end-symbolic"); }`, with `:checked` switching to `pan-down-symbolic`. Without our own rules, these arrows get the toolkit's unstyled default instead of a Platinum triangle. The Kvantum style already draws `[TreeExpander]` with the desktop theme's pinned right and down triangles (the `## kvantum` secondary-controls invariant row). Give GTK the same disclosure triangles: right when collapsed, down when expanded. Both shapes already exist in `theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg` (`right-arrow` `M 5,4 L 5,12 L 11,8 Z`, `down-arrow` `M 4,5 L 12,5 L 8,11 Z`). The down triangle already ships as `assets/arrow-down.svg`, so only a right-triangle asset is new.

**Design (decided; do not widen).** Checked with PyGObject on this machine: a GTK 3 `Gtk.Expander` is `expander > title > arrow.horizontal` (bare `expander` is the widget itself, so GTK 3 must use `expander title > arrow`), and a GTK 4 `Gtk.Expander` is `expander-widget > box > title > expander`. GTK 4's `GtkTreeExpander` arrow is also an `expander` node, so bare `expander` covers both, as stock does. In both toolkits, `GtkTreeView` draws its expander with the `expander` class on `treeview.view`. Expanded is `:checked` everywhere. Rules:
- GTK 3: `treeview.view.expander, expander title > arrow { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/arrow-right.svg"); }` and `treeview.view.expander:checked, expander title > arrow:checked { -gtk-icon-source: url("../assets/arrow-down.svg"); }`.
- GTK 4: `treeview.view.expander, expander { min-width: 16px; min-height: 16px; -gtk-icon-source: url("../assets/arrow-right.svg"); }` and `treeview.view.expander:checked, expander:checked { -gtk-icon-source: url("../assets/arrow-down.svg"); }`.
- Out of scope: `:dir(rtl)` mirroring (an RTL tree keeps the right-pointing triangle), `:hover`/`:selected`/`:disabled`/`:backdrop` colours (the url() SVG paints its own black fill), `columnview.view.expander` (GTK 4 column views draw expanders through `treeexpander`, which bare `expander` already covers), and indent sizes.

**Files touched.**
- `theme/gtk/org.macos8.desktop/assets/arrow-right.svg` (new): a 16x16 canvas holding one `<path d="M 5,4 L 5,12 L 11,8 Z" fill="#000000"/>`, laid out like `assets/arrow-down.svg`, with its provenance comment *inside* the root (naming `widgets/arrows.svg` `right-arrow` and `TestArrowGlyphs`), because GTK's CSS icon loader rejects a comment before the root.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: put the two GTK 3 rules immediately after the row-selection rule (`treeview.view:selected, … list row.activatable:selected:hover`). In the header comment, add a sentence: tree-view and expander disclosure arrows load the shared `assets/arrow-right.svg` (collapsed) and `assets/arrow-down.svg` (expanded), whose triangles reuse the desktop theme's pinned `widgets/arrows.svg` shapes; no reference screenshot shows a GTK widget; the node names are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: put the two GTK 4 rules immediately after its row-selection rule (the one ending `listview > row.activatable:selected:hover`), and add the matching header sentence.
- `tests/support/gtk_theme_spec.py`: add `EXPANDER_COLLAPSED = {"min-width": "16px", "min-height": "16px", "-gtk-icon-source": 'url("../assets/arrow-right.svg")'}` and `EXPANDER_EXPANDED = {"-gtk-icon-source": 'url("../assets/arrow-down.svg")'}`. Add `assert_expander_arrows(self, collapsed, expanded)` to `GtkSheetRuleCases`, after `assert_tree_header`: it asserts `EXPANDER_COLLAPSED` on each collapsed selector and `EXPANDER_EXPANDED` on each expanded selector through `assert_rule`. Mention it in the class docstring's list of selector-taking assertions, if that list exists.
- `tests/test_gtk_theme.py`: add `ARROW_RIGHT = THEME_DIR / "assets" / "arrow-right.svg"` beside `ARROW_UP`. Extend `TestArrowGlyphs` (setUpClass, stand-alone, root-first, 16px canvas, black-only fill, and `test_arrow_geometry` with `M 5,4 L 5,12 L 11,8 Z`) to cover the right arrow, and update its docstring to mention disclosure arrows. Add `TestGtkTheme.test_expander_arrows`, calling `self.assert_expander_arrows(("treeview.view.expander", "expander title > arrow"), ("treeview.view.expander:checked", "expander title > arrow:checked"))`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_expander_arrows`, calling `self.assert_expander_arrows(("treeview.view.expander", "expander"), ("treeview.view.expander:checked", "expander:checked"))`.
- `Makefile` `install_gtk`: add `assets/arrow-right.svg` to the `trap` cleanup list, the `install -Dm644 … .arrow-right.svg.staging` chain and the `mv` chain, beside `arrow-up.svg`. In the uninstall recipe, add the file and its `.arrow-right.svg.staging` to the GTK `rm -f` line.
- `tests/support/gtk_fixtures.py` `SHIPPED_FILES` and `tests/test_gtk_install.py` `STAGING_PATHS`: add `assets/arrow-right.svg` (staging `assets/.arrow-right.svg.staging`) after `arrow-up.svg`.
- `README.md` (outside the brief markers): "the seven shared check, radio, combo box, menu arrow and title-button box assets" becomes "the eight shared check, radio, combo box, menu arrow, disclosure arrow and title-button box assets", and "removes the ten GTK files" becomes "eleven". Update `docs/invariants.md`'s GTK install row from "ten GTK theme files" to "eleven". Grep both files for any other GTK file count and fix it too.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both sheets point tree-view and expander disclosure arrows at the shipped right (collapsed) and down (`:checked`) triangles in a 16px box. Tests: the two `test_expander_arrows` cases and `tests/test_gtk_theme.py::TestArrowGlyphs`. Provenance: no reference screenshot shows a GTK widget or a disclosure triangle; the triangles reuse the desktop theme's pinned `widgets/arrows.svg` `right-arrow`/`down-arrow` shapes; the node names, the `:checked` state and the 16px size are GTK-required; RTL mirroring is not done.

**Acceptance criteria.**
- `assets/arrow-right.svg` ships with the right-arrow path, a 16x16 canvas, only `#000000` fill and the root first. `TestArrowGlyphs` fails if the path, canvas or fill changes.
- The GTK 3 sheet carries `treeview.view.expander` and `expander title > arrow` with the 16px minimum and the right-arrow source, plus their `:checked` forms with the down-arrow source. The GTK 4 sheet carries the same for `treeview.view.expander` and `expander`. Both `test_expander_arrows` cases pin them.
- `make install-gtk` installs `assets/arrow-right.svg` byte-for-byte, and `make uninstall` removes it and its staging file. The existing `tests/test_gtk_install.py` cases pass with the extended `STAGING_PATHS`/`SHIPPED_FILES`.
- The new invariant row is accepted by `tests/invariants.py`, the other GTK tests still pass, and `make check` is green.

## Done

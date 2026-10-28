# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
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

### Platinum GTK file chooser: paint the places sidebar band and its rows as the menu-bar face with the landed list-row selection in GTK 3 and GTK 4 (planned 2026-10-27 by the plan role; independent of the queued about:telemetry furniture plan — that one touches `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`, this one the GTK sheets and their suites, and their `docs/invariants.md` edits only append one new row each, so either order merges; the chooser's path bar landed in PLANS-DONE.md and its file list, column headers, entries, buttons, action bar and paned handle are already covered by the landed generic rules, so the places sidebar is the chooser's remaining surface)

**Goal.** After the landed path-bar plan, a GTK file chooser's places sidebar — the left column `GtkFileChooserWidget` shows in both toolkits — still paints stock: the band keeps Adwaita's near-white `#fbfafa` face (GTK 3 with a `#f9f9f8` backdrop face; GTK 4 with a grey `#cdc7c2` right border), GTK 3 greys the rows in backdrop (`placessidebar row:backdrop { color: #929595 }` and `placessidebar row:backdrop:selected { color: #fcfcfc }`), a selected row in an inactive GTK 3 window turns Adwaita blue (`row.activatable:selected:backdrop { background-color: #3584e4 }`, outranking the landed selection rule, which has no backdrop arm), and the sidebar's "New bookmark" row keeps Adwaita's link-blue text in both toolkits. This plan paints the sidebar band as the landed flat menu-bar face — `#DDDDDD`, black text, flat backdrop, no border — and pins the chooser-specific row arms, introducing no new hex and editing no landed rule.

**Verified facts (checked 2026-10-27, PyGObject probes with GTK 3.24.49 and GTK 4.18.6 plus the stock sheets extracted from the installed libraries' gresources).** A GTK 3 `Gtk.FileChooserDialog` builds `paned.horizontal > placessidebar[frame, sidebar] > viewport.frame > list > row[activatable, sidebar-row]` rows (one carries `sidebar-new-bookmark-row`); the chooser's header strip holds the `path-bar` (landed) beside a `search` entry (landed), the file list is `treeview.view` (landed) and the bottom bar an `actionbar` (landed). A GTK 4 `Gtk.FileChooserWidget` builds `paned.horizontal > placessidebar[sidebar] > scrolledwindow > viewport > list[navigation-sidebar] > row[activatable, sidebar-row]` rows (plus one `sidebar-new-bookmark-row`); its root `filechooser` node's other paint — the `pathbar` (landed), the `columnview.view` file list (landed), the search `entry` (landed) and the root `actionbar` band (landed) — is covered by landed rules. Stock paint, from the GTK 3 gresource `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` and the GTK 4 gresource `/org/gtk/libgtk/theme/Default/Default-light.css`: GTK 3 paints `.sidebar { border-style: none; background-color: #fbfafa }` with `.sidebar:backdrop { background-color: #f9f9f8 }`; GTK 4 paints `.sidebar { background-color: #fbfafa }` with `.sidebar:not(separator):dir(ltr) { border-right: 1px solid #cdc7c2 }`; GTK 3 paints `placessidebar row:backdrop { color: #929595 }`, `placessidebar row:backdrop:selected { color: #fcfcfc }`, `row.activatable:selected:backdrop { background-color: #3584e4 }` and `placessidebar row.sidebar-new-bookmark-row { color: #3584e4 }`; GTK 4 paints `placessidebar .navigation-sidebar > row.sidebar-new-bookmark-row { color: #3584e4 }`. The landed generic arms already paint rest, hover (transparent) and selection (`#CCCCFF`, black text, square): `list row.activatable:hover` and `list row.activatable:selected[:hover]` outrank stock's `row.activatable:hover` and GTK 4's `.navigation-sidebar > row:hover/:selected/:selected:hover`, so only the band face, the backdrop arms, the GTK 4 right border and the new-bookmark text remain stock. The sidebar's inner `list` already stays transparent because stock's `.sidebar list { background-color: transparent }` (0,1,1) beats our landed white `list` rule (0,1,0); stock's `placessidebar > viewport.frame { border-style: none }` likewise already clears the inner viewport's frame against our landed `.frame` rule in GTK 3. `tests/test_gtk_theme.py::TestGtkTheme::test_disabled_text_follows_the_entry_text_rule` already establishes that our theme sheet loads after the stock base and wins equal-specificity ties by order, so tie-overrides need no `!important`.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows a GTK widget, and Mac OS 8.6's Finder has no sidebar at all, so the band reuses the reference-grounded flat menu-bar/window face `#DDDDDD` with black text (the landed `window, .background` face) and a flat `#DDDDDD` backdrop mirroring the landed headerbar's inactive face; the rows reuse the landed `list row` recipe whose `#CCCCFF` selection is the pinned `[Colors:Selection]` of `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background` and whose squareness extends the landed `border-radius: 0` selection. The `placessidebar` node name, the `sidebar`, `frame`, `navigation-sidebar` and `sidebar-new-bookmark-row` classes, the stock row geometry (the 36px min-height, stock paddings and margins) and the drag-over indicator (`:drop(active)` arms, painted green by stock) are GTK-required; the rows' geometry and the drag indicator stay stock. Recorded, not planned here: the same GTK 3 `:backdrop` arms grey or blue every generic list row in an inactive window (our landed row rule has no backdrop arm outside the sidebar) — a natural subject of a later plan deciding whether the landed row recipe grows backdrop arms generally.

**Approach.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append after the landed `.path-bar > button` block at the sheet's end:

```css
/* A file chooser's places sidebar takes the flat menu-bar face with black
   text in backdrop, and its rows keep the landed selection and drop
   Adwaita's link blue. */
.sidebar {
  background-color: #DDDDDD;
  color: #000000;
}

.sidebar:backdrop {
  background-color: #DDDDDD;
  color: #000000;
}

placessidebar row:backdrop {
  color: #000000;
}

placessidebar row.activatable:selected:backdrop {
  background-color: #CCCCFF;
  color: #000000;
}

placessidebar row.sidebar-new-bookmark-row {
  color: #000000;
}
```

`.sidebar` ties stock's `.sidebar` face on specificity and wins by coming later; `placessidebar row:backdrop` (0,1,2) and `placessidebar row.sidebar-new-bookmark-row` (0,1,2) tie and win the same way; `placessidebar row.activatable:selected:backdrop` (0,2,2) beats stock's `row.activatable:selected:backdrop` (0,2,1). GTK 3 keeps the landed `.frame` sunken black box around the chooser's sidebar (the `frame` class is on the `placessidebar` itself) and stock's `placessidebar > viewport.frame` clear.

In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, append at the sheet's end after the landed `pathbar` block:

```css
/* A file chooser's places sidebar takes the flat menu-bar face and drops
   the stock grey right border; its new-bookmark row drops Adwaita's link
   blue. */
.sidebar {
  background-color: #DDDDDD;
  color: #000000;
  border: none;
}

.sidebar:backdrop {
  background-color: #DDDDDD;
  color: #000000;
}

placessidebar.sidebar:not(separator):dir(ltr),
placessidebar.sidebar:not(separator):dir(rtl) {
  border: none;
}

placessidebar .navigation-sidebar > row.sidebar-new-bookmark-row {
  color: #000000;
}
```

The border-clearing rule spells the stock arms `.sidebar:not(separator):dir(ltr)`/`:dir(rtl)` through the `placessidebar.sidebar` node so it ties (0,3,0) with stock's border-right rule and wins by coming later; plain `placessidebar.sidebar { border: none }` (0,1,1) would lose to (0,3,0) and is spelled only as part of that rule. GTK 4 needs no row backdrop arms: stock's `.navigation-sidebar > row` has none, so the landed selection and transparent hover hold in backdrop too.

In `tests/test_gtk_theme.py`, add `TestGtkTheme.test_places_sidebar` mirroring `test_path_bar_tabs`'s `assert_rule` idiom with the spec-module constants (`FACE`, `BLACK`, `SELECTION` from `tests/support/gtk_theme_spec.py`, which re-exports the pinned `platinum_palette.py` values):

- `assert_rule(".sidebar", {"background-color": FACE, "color": BLACK})` and `assert_rule(".sidebar:backdrop", {"background-color": FACE, "color": BLACK})`.
- `assert_rule("placessidebar row:backdrop", {"color": BLACK})`.
- `assert_rule("placessidebar row.activatable:selected:backdrop", {"background-color": SELECTION, "color": BLACK})`.
- `assert_rule("placessidebar row.sidebar-new-bookmark-row", {"color": BLACK})`.

In `tests/test_gtk4_theme.py`, add `TestGtk4Theme.test_places_sidebar` with the same first two band assertions plus:

- `assert_rule("placessidebar.sidebar:not(separator):dir(ltr)", {"border": "none"})` and the same for the `:dir(rtl)` selector.
- `assert_rule("placessidebar .navigation-sidebar > row.sidebar-new-bookmark-row", {"color": BLACK})`.

Both suites' existing exact-set and palette tests (the sheets' `@define-color` register and hex checks in `tests/test_gtk_theme.py`/`tests/test_gtk4_theme.py`) must stay green without edits — the new rules reuse only `#DDDDDD`, `#CCCCFF` and `#000000`.

In `docs/invariants.md`, in the `## gtk` table, append one row after the current last row (the tree-header row) before the trailing validation notes: the guarantee in one sentence — both GTK sheets paint the file chooser's places sidebar band (`placessidebar`, the `sidebar` class) as the flat `#DDDDDD` menu-bar face with black text and a flat `#DDDDDD` backdrop, clear GTK 4's stock grey right border, keep GTK 3's rows black-texted in backdrop with the landed `#CCCCFF` square selection in backdrop, and paint the `sidebar-new-bookmark-row` black while the rows' geometry and drag-over indicator stay stock — with the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_places_sidebar` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_places_sidebar`, and the provenance cell naming the missing reference surface (no reference screenshot shows a GTK widget; the Finder has no sidebar), the reused face (the landed `window, .background` band) and row selection (`widgets/listitem.svg`'s flat fill, `test_selection_background`), the gresource and PyGObject probes above, the GTK-required node and class names, and that declaration checks establish no rendered pixels. Trim no landed row; `tests/test_invariants.py` (part of the check) parses the register.

**Acceptance criteria.**
- Both sheets carry exactly the rules spelled above; no landed rule's text changes; the only hex values introduced are the already-pinned `#DDDDDD`, `#CCCCFF` and `#000000`.
- `TestGtkTheme.test_places_sidebar` and `TestGtk4Theme.test_places_sidebar` pass against the sheets, and every landed GTK test keeps passing with no edits outside the additions.
- The `## gtk` invariants table grows exactly one row and trims none; the full `make check` passes.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

## Done

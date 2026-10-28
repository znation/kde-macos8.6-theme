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

### Platinum GTK search bar and action bar: paint `GtkSearchBar` and `GtkActionBar` as the menu-bar band in GTK 3 and GTK 4 (planned 2026-10-27 by the plan role; independent of the waiting Firefox about:support content plan — the two touch disjoint files (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py` versus `theme/firefox/org.macos8.desktop/chrome/userContent.css` and `tests/test_firefox_content_theme.py`), and their `docs/invariants.md` edits only append one new row each, so either order merges; no other GTK plan waits behind it)

**Goal.** The landed GTK sheets paint the menu bar, toolbar and infobar as the Platinum band (`#DDDDDD` face, black text, `#888888`/`#FFFFFF` etched bottom rule) but a `GtkSearchBar` and a `GtkActionBar` keep stock paint: a plain background under the sheet's `window` colours with no etched rule, so a window's bottom action bar and top search bar read as unbounded strips. This plan paints both bands as the landed menu-bar band — the same recipe byte-for-byte, in both toolkits.

**Verified facts (checked 2026-10-27).** `grep -c 'actionbar\|searchbar\|search-bar'` returns 0 for both `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` — no landed rule covers either surface, and no PLANS.md `## Planned` entry nor PLANS-DONE.md finished plan names a GTK search bar or action bar (the landed GTK infobar plan's heading names only `Gtk.InfoBar`). Live-measured with PyGObject (GTK 3.24.49 and GTK 4.18.6, the toolkits the landed infobar row also names): GTK 3 builds `searchbar > revealer > box` (the search entry under it has the `entry` node with the `.search` class) and `actionbar > revealer > box` (the buttons under it are plain `button` nodes); GTK 4's widget probes report the identical css names `searchbar > revealer > box` (a `box`-named `GtkCenterBox` under the revealer) and `actionbar > revealer > box` — so the two landed toolkits share the one selector pair, exactly as the landed infobar rule shares `infobar > revealer > box`.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows a GTK search bar or action bar, so the bands sample no reference pixel: they reuse only reference-grounded values the sheets already pin — the `#DDDDDD` face and black text from the menu-bar band (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_menu_bar_face`) and the etched pair from `tests/test_desktoptheme_line.py::TestLineReference`, through the sheets' own `toolbar, menubar` and landed infobar rules. The band geometry, the revealer/box node names and the `:disabled`-free scope are GTK-required. `:backdrop` stays out of scope, as the landed infobar and headerbar backdrop decisions scoped it out. Both surfaces take the one band recipe — the action bar's etched rule stays the menu-bar band's bottom rule rather than a mirrored top rule, because the sheets ship exactly one band recipe (menu bar, toolbar and infobar all use it) and a second mirrored variant would add an unpinned orientation choice; this is decided here so no design question is left open.

**Approach.** In both `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`, directly after the landed `infobar > revealer > box` rule (the last rule of the GTK 3 sheet; the GTK 4 sheet ends the same way), add:

```css
/* A search bar and an action bar draw the menu-bar band: the #DDDDDD face,
   black text and the etched bottom rule. The search entry keeps the entry
   field and the close and action buttons keep the button paint; :backdrop
   stays out of scope. */
searchbar > revealer > box,
actionbar > revealer > box {
  background-color: #DDDDDD;
  color: #000000;
  border-bottom: 1px solid #888888;
  box-shadow: inset 0 -1px #FFFFFF;
}
```

In both sheets' provenance header comment, append one sentence after the infobar sentence and before the closing `*/`: "A search bar and an action bar band reuse the same menu-bar band with the same etched bottom rule; no reference screenshot shows a GTK search bar or action bar, and the revealer and box node names are GTK-required."

In `tests/test_gtk_theme.py::TestGtkTheme`, after the landed `test_infobar`, add:
- `test_search_bar` and `test_action_bar`, each calling `self.assert_infobar((selector,))` with `"searchbar > revealer > box"` and `"actionbar > revealer > box"` respectively — reusing the shared `INFOBAR` spec in `tests/support/gtk_rule_cases.py` so both bands stay byte-identical to the infobar band, with no new constant and no edit to any landed rule.

In `tests/test_gtk4_theme.py::TestGtk4Theme`, after the landed `test_infobar`, add the same two tests with the same selectors calling `self.assert_infobar`.

Extend no landed assertion: the shared `assert_rule` machinery already parses both sheets, so the only change is the two tests per sheet.

In `docs/invariants.md`, in the `## gtk` table: append exactly one row after the last gtk row (the landed infobar row) with the guarantee in one sentence (both sheets paint `searchbar > revealer > box` and `actionbar > revealer > box` as the menu-bar band — the `#DDDDDD` face, black text and the `#888888`/`#FFFFFF` etched bottom rule — while the search entry keeps the entry field and the close and action buttons keep the `button` paint, and `:backdrop` stays out of scope) and the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_search_bar`/`test_action_bar` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_search_bar`/`test_action_bar`; trim no landed row.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets gain exactly the one rule block above after the infobar rule, introducing no hex outside `{#DDDDDD, #888888, #FFFFFF, #000000}` and changing no landed rule's text.
- Both sheets' headers gain exactly the one sentence after the infobar sentence and before `*/`.
- The four new tests pass with the shared `assert_infobar`/`INFOBAR` path, and no landed test or support constant changes.
- `docs/invariants.md` gains exactly one appended row after the last `## gtk` row naming the four new tests, with no landed row's wording changed; `tests/support/invariants.py`'s register stays in step.
- `make check` passes.

## Done

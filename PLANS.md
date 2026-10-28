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

### Platinum GTK path bar: paint the file chooser's breadcrumb buttons as the Platinum tabs in GTK 3 and GTK 4 (planned 2026-10-27 by the plan role; independent of the queued stack-switcher plan above — it touches the same three landed files, so all anchors below are rule texts and symbol names, not line numbers)

**Goal.** The landed GTK sheets give the generic `button` the raised Platinum push-button paint and `button:active, button:checked` a sunken bevel, and a file chooser's path bar — the breadcrumb strip `GtkFileChooserWidget` shows above the file list — falls through to exactly those rules: every unpressed breadcrumb gets the generic raised face, and the current folder's `GtkToggleButton` sits `:checked` for the chooser's whole lifetime, so the breadcrumb strip paints its home entry *permanently sunken* while a queued stack window's own header strip would paint the same strip's active entry as the raised, flat-merged `tab:checked` face. This plan paints the path bar's buttons with the landed tab recipe byte-for-byte in both toolkits — the same decision the queued stack-switcher plan makes for that widget — so the unpressed breadcrumbs read as raised tabs, the current folder as the flat checked tab, and no new constant, no new hex and no edit to any landed rule is introduced.

**Verified facts (checked 2026-10-27).** `grep -c "pathbar\|path-bar"` returns 0 for `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `tests/support/gtk_theme_spec.py`, `tests/support/gtk_rule_cases.py` and `docs/invariants.md`, and no `## Planned` entry nor PLANS-DONE.md or BUGS-FIXED.md finished record names a GTK path bar. Live-probed with PyGObject (GTK 3.24.49 and GTK 4.18.6, the toolkits the landed status-bar row names), a `Gtk.FileChooserWidget` opened on `/usr/local/share` builds: GTK 3 — a `GtkPathBar` having `get_style_context().list_classes() == ["linked", "path-bar"]` whose direct `get_children()` are the folder `GtkToggleButton`s with classes `text-button, toggle` (`image-button, toggle` for the leading icon button), two `GtkButton`s with class `slider-button` (the scroll arrows) and one `GtkMenuButton` with classes `popup, toggle` (the "Other Locations" button the chooser root shows); GTK 4 — a root `get_css_name() == "pathbar"` widget whose only `button` descendants sit at `pathbar > scrolledwindow > viewport > box[linked,horizontal] > button` (the folder toggles with classes `text-button, toggle` / `image-button, toggle`), the scrolledwindow's overlay `scrollbar` siblings carrying no `button` node. In GTK 3 the `GtkPathBar` widget-path's own node name resolves `None`, so the widget-set `path-bar` and `linked` classes are the reachable handle; in GTK 4 the root's `pathbar` css node is the handle and no `path-bar` class exists. The current folder's toggle carries `:checked` in both toolkits. The landed rules these selectors must outrank in both sheets are `button { ... box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA; }` and `button:active, button:checked { box-shadow: inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF; }` — the checked arm is what paints the sunken face this plan clears. The landed tab recipe the sheets already ship is the `tab`/`tab.reorderable-page` arm block (`tab`, `tab:hover`, `tab:checked`, `tab:checked:hover` plus the same `tab:backdrop[:checked]` arms, each rule also naming the `notebook > header > tabs > tab[:...][:...]` spellings), and the suite shares it through `TAB_STATES` in `tests/support/gtk_theme_spec.py` (states `base`, `hover`, `checked`, `checked+hover`, `backdrop`, `backdrop+checked`) with `RAISED_BEVEL` (`inset 1px 1px #FFFFFF, inset -1px -1px #999999`), while `GtkSheetRuleCases.test_tab_states` in `tests/support/gtk_rule_cases.py` builds each state's expected dict from `FACE`, `BLACK` and `RAISED_BEVEL` via the landed `assert_rule`; the landed tests that drive `test_tab_states` live in the suites' `TestGtkTheme`/`TestGtk4Theme` inheritance of that shared class.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows a GTK path bar, and Mac OS 8.6 has no breadcrumb surface at all — a Finder window navigates through a pop-up folder menu, not a button strip — so the plan samples no new reference pixel: it reuses only the landed tab recipe's values, whose own provenance the landed `test_tab_states` path already records (the raised tab bevel and the `#DDDDDD` face, pinned by the desktop theme's `widgets/tabbar.svg` case and the notebook tab rules). The `path-bar`/`linked` classes, the `pathbar`, `scrolledwindow`, `viewport` and `box` node names and the checked folder button's `:checked` state are GTK-required (probe above). The kept `border-bottom-color: #DDDDDD` on the checked arm — meaningful where a notebook tab merges into its header groove — is included byte-for-byte against this plan's decided reopening: below a path bar sits the chooser's black-outlined sunken file field, so the checked folder's bottom border paints `#DDDDDD` over one pixel of that outline; this is recorded here as the decided adaptation so no design question is left open. `:backdrop` stays out of scope, as the landed infobar, search-bar, action-bar and status-bar decisions and the queued stack-switcher plan scoped it out, and the landed tab `:backdrop` arms stay untouched.

**Approach.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, directly after the landed `statusbar > frame > border` rule (the sheet's last rule), add

```css
/* A file chooser's path bar draws its breadcrumb buttons — the folder toggles,
   the slider arrows and the Other Locations button alike — as the landed tab
   recipe, the current folder's checked tab included; :backdrop stays out of
   scope. */
.path-bar > button {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999;
}

.path-bar > button:hover {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999;
}

.path-bar > button:checked,
.path-bar > button:checked:hover {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-bottom-color: #DDDDDD;
  border-radius: 0;
  box-shadow: none;
}
```

Verification that the three blocks' declaration lines match the landed tab arms' text byte-for-byte is part of the edit; so is laying the comment out before the first arm and nothing between the arms.

In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, directly after the landed final `statusbar` rule (the sheet's last rule), add the same three blocks under the same comment text with `pathbar > scrolledwindow > viewport > box > button`, `pathbar > scrolledwindow > viewport > box > button:hover` and `pathbar > scrolledwindow > viewport > box > button:checked, pathbar > scrolledwindow > viewport > box > button:checked:hover` as the selectors.

In both sheets' provenance header comments, append one sentence immediately before the closing `*/`: "A file chooser's path bar paints its buttons as the landed tab recipe byte-for-byte; no reference screenshot shows a GTK path bar, and the path-bar and linked classes and the pathbar, scrolledwindow, viewport and box node names are GTK-required."

In `tests/test_gtk_theme.py::TestGtkTheme`, after the landed `test_status_bar_frame_border_is_flat`, add `test_path_bar_tabs`: build the local dict `forms = {"base": ".path-bar > button", "hover": ".path-bar > button:hover", "checked": ".path-bar > button:checked", "checked+hover": ".path-bar > button:checked:hover"}` and iterate `TAB_STATES`, skipping every state whose name is not in the dict (the two `:backdrop` states stay out of scope), building for the state iterated the same expected dict `test_tab_states` builds — `FACE` face, `background-image: none`, `border: 1px solid BLACK`, `border-radius: 0`, and `box-shadow: RAISED_BEVEL` when unchecked, `border-bottom-color: FACE` and `box-shadow: none` when checked — and calling `self.assert_rule(selector, expected)` inside a `subTest(state=..., selector=...)` per selector, with no change to `test_status_bar`, `test_status_bar_frame_border_is_flat` or the shared `GtkSheetRuleCases`.

In `tests/test_gtk4_theme.py::TestGtk4Theme`, after the landed `test_status_bar`, add the same `test_path_bar_tabs` body with the four `pathbar > scrolledwindow > viewport > box > button` selector spellings. Each suite's existing `from support.gtk_theme_spec import (...)` list gains `TAB_STATES` only if it is not already there (the queued stack-switcher plan adds it to both suites; whichever lands first, after both merges the list carries it exactly once).

Extend no landed assertion: the shared `assert_rule` machinery already parses both sheets, `test_tab_states` changes no text and runs unchanged, and the only shared-file touch is the one added `TAB_STATES` name per suite's already existing import list.

In `docs/invariants.md`, in the `## gtk` table: append exactly one row after the landed status-bar row (the table's current last row before the trailing validation notes) with the guarantee in one sentence (both sheets paint a file chooser's path bar as the landed tab recipe — the raised bevel for the unpressed states and the flat checked face with the face-coloured bottom border — while the landed notebook tab and generic button rules stay byte-identical and an unfocused chooser keeps them) and the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_path_bar_tabs` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_path_bar_tabs`; its exception sentence names the missing reference surface (no reference screenshot shows a GTK path bar, and Mac OS 8.6 has no breadcrumb to adapt), the re-used landed values through `test_tab_states`, and the probed GTK 3 class / GTK 4 node handles. Trim no landed row; `tests/support/invariants.py`'s register stays in step.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

## Done

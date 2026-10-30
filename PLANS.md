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
2026-10-27 by the feature role; Firefox content scope refreshed
2026-10-29 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
the 2026-10-29 user decision supersedes its final-art status and queues placeholder tracking
below); the `org.macos8.desktop` Kvantum widget
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
Firefox's `tests/test_firefox_theme_*.py` and `tests/test_firefox_content_*.py` modules
check stylesheet declarations and selector behavior;
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
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows). The
`userContent.css` sheet now styles surfaces within six internal pages:
about:downloads, about:config, about:preferences, about:support, about:networking
and about:telemetry. These include preferences navigation and controls, support
tables and buttons, and telemetry navigation, tables and histograms; this is
surface coverage, not a claim of complete page theming. The opt-in profile install
copies this sheet alongside `userChrome.css`. This content work extends the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._

### Platinum GTK 4 drag-and-drop feedback: repaint the drop states with the selection fill (planned 2026-10-30 by the plan role; independent of the waiting GTK 3 scrollbar-corner-junction plan — it edits the GTK 4 sheet and `tests/test_gtk4_theme.py` while that plan edits the GTK 3 sheet and `tests/test_gtk_theme.py`, and it covers the drag-drop states the landed GTK 4 row, header and rubberband rules left untouched, so no existing selector it names is changed)

**Goal.** During a GTK 4 drag, the sheet's styled rows and headers leak stock paint: the
carries-no-rule inventory is the drag-and-drop state set — a drop hovered over an icon view
strokes the stock accent border, a row-drop indicator over a tree or column view strokes
the stock accent top/bottom lines, and dragging a column onto a header button floods that
button in the stock accent fill with white text — none of it Platinum. The sheet styles
rows, headers and the rubberband but declares no `dnd-target` or `.dnd` rule, so the stock
accent colour renders on every drop surface. The drop states must read as the theme's
selection: repaint them with the reference-grounded `#CCCCFF`.

**Verified facts, method and values (checked 2026-10-30).** The sheet carries no dnd rule
or test (grep over `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` and
`tests/test_gtk4_theme.py` for `dnd` returns only rubberband commentary lines), and no
Planned or finished plan covers GTK drag-and-drop. The stock resources re-derived by
gresource extraction on 2026-10-30 carry these arms. In
`/org/gnome/Adwaita/styles/base.css` inside `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`:
`iconview > dndtarget:drop(active)` declares `border-style: solid; border-width: 1px;
border-color: var(--accent-bg-color);`; `treeview.view > dndtarget:drop(active),
window.print:not(.ssd-frame) treeview.dialog-action-box > dndtarget:drop(active)` declares
`border-style: solid none; border-width: 1px; border-color: var(--accent-bg-color);`; the
same tree gains `.after` (`border-top-style: none`) and `.before`
(`border-bottom-style: none`) arms that hide one line, and a long header arm covering
`columnview button.dnd` and `treeview.view button.dnd` (with `:active`, `:selected` and
`:hover` variants, the legacy `header.button.dnd` spelling and print variants) declaring
the accent fill (`background-color: var(--accent-bg-color)`, white text, and an inset
white ring on the GTK 4 sheet below). In `/org/gtk/libgtk/theme/Default/Default-light.css`
inside `/usr/lib/x86_64-linux-gnu/libgtk-4.so.1` the same surface is painted with fixed
values: `#185fb4` on both `dndtarget` rules and, on the header drag arm, `background-color:
#3584e4; color: #ffffff; background-image: none; border-style: none; border-radius: 0;
box-shadow: inset 0 0 0 1px #ffffff; text-shadow: none; padding: 0 6px; transition: none;`
covering `columnview.view > header`'s `header.button.dnd` and `button.dnd` spellings. No
reference screenshot shows any drag-and-drop feedback, so every value here is a platform
adaptation: the adaptation reuses the pinned `SELECTION` constant `#CCCCFF` from
`tests/support/platinum_palette.py` — the same value the sheet already applies to selected
rows, text selections, calendar day, progress bar and level bar — so the elevated drop
state answers the toolkit's accent-family semantics with the theme's selection family, and
no new palette value, artwork or dependency is needed. The stock `padding: 0 6px` on the
header drag arm stays undeclared, so that transient state keeps the stock's own geometry
choice; the stock `.after`/`.before` arms are left undeclared too, because they hide one
of the two row lines and neither carries a colour the adaptation must replace.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, insert directly
after the `selected:backdrop` row rule (the rule ending before the `treeview.view.expander`
rule) a dated adaptation comment and three rules. Comment convention follows the landed
overshoot clearance: name the absent reference surface, that the stock GTK 4 paints these
states with its accent family, and that `SELECTION` `#CCCCFF` replaces it — keeping the
stock scheme's name and library names out of the comment text, as
`tests/test_gtk4_theme.py`'s `test_stands_alone` and palette-content assertions require.
The rules: one, `iconview > dndtarget:drop(active)` declaring exactly `border: 1px solid
#CCCCFF;`; two, one grouped rule over `columnview.view > dndtarget:drop(active)`,
`treeview.view > dndtarget:drop(active)` and
`window.print:not(.ssd-frame) treeview.dialog-action-box > dndtarget:drop(active)`
declaring exactly `border-style: solid none;` `border-width: 1px;`
`border-color: #CCCCFF;`; three, one grouped header-drag rule over the native header
tree the landed header rules style — `columnview.view > header > button.dnd`,
`columnview.view > header > button.dnd:hover`, `columnview.view > header >
button.dnd:active`, `columnview.view > header > button.dnd:selected`,
`treeview.view > header > button.dnd`, `treeview.view > header >
button.dnd:hover`, `treeview.view > header > button.dnd:active`,
`treeview.view > header > button.dnd:selected`, and the print variant
`window.print:not(.ssd-frame) treeview.dialog-action-box > header > button.dnd` —
declaring exactly `background-color: #CCCCFF;` `background-image: none;`
`color: #000000;` `text-shadow: none;` `box-shadow: none;` `border-style: none;`
`border-radius: 0;`. The state variants mirror the stock arm list, otherwise the stock `:hover` variants
outrank a plain `.dnd` rule and re-leak the accent under the cursor. In
`tests/test_gtk4_theme.py`, add `TestGtk4Theme` tests beside `test_rubberband`, using the
shared `assert_rule` helper and the imported `SELECTION` constant:
`test_iconview_drop_border` asserting the icon view rule's `border` equals
`f"1px solid {SELECTION}"`; `test_row_drop_borders` asserting all three row selectors
carry `{'border-style': 'solid none', 'border-width': '1px', 'border-color':
SELECTION}`; `test_header_drop_indicator` asserting the native tree and column
selectors (each state) carry the seven declarations above and that the print variant
carries them too; and `test_row_drop_directional_arms_undeclared` asserting
`"drop(active).after"` is absent from the sheet text, pinning the undeclared
directional arms. In `docs/invariants.md`, append one row under `## gtk`: no collected screenshot
shows GTK drag-and-drop feedback; the stock inventory (the two `dndtarget` shapes plus
the header button arm, the `.after`/`.before` directional arms and the `dnd` node and
`dnd tab` out of scope) comes from the libadwaita `base.css` and GTK 4 `Default-light.css`
resources in `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` and
`/usr/lib/x86_64-linux-gnu/libgtk-4.so.1`, extracted with gresource on 2026-10-30; the
drop states reuse the pinned `#CCCCFF` selection instead of the stock accent values, a
platform adaptation grounded in the landed selection recipes; the header drag arm names
only the native `> header > button` tree the landed header rules style; the declaration
checks do not establish rendered pixels.

**Acceptance criteria.** The three dnd rule groups exist in the GTK 4 sheet with exactly
the pinned declarations, so a rendered drop over an icon view runs line to line, a row
drop shows the top and bottom `#CCCCFF` border band with the stock directional hide
intact, and a column dragged over a header button paints the flat `#CCCCFF` selection
with black text and no white ring or accent leak in any drag state; deleting any pinned
declaration, changing any pinned value, or claiming the undeclared `.after`/`.before` or
stock-drag padding fails one of the new tests or the absence pin. Every landed assertion
in `tests/test_gtk4_theme.py` passes unchanged — the rules sit beside the row block, so
no existing selector or declaration shifts; `test_stands_alone`, `test_only_palette_hex_literals` and
`test_no_universal_selector` pass because the change adds no import, url,
selector star and only already-pinned hex values. Scope is the two named files plus
`docs/invariants.md`; the GTK 3 sheet and its single `treeview button.dnd` header arm stay
outside this plan (they belong to the sheet the waiting GTK 3 junction plan edits, and
may join a later GTK 3 plan); the stock `dnd` node colour and `dnd tab` drag-tab arm also
stay out (no Platinum drop surface is drawn by either, and the drag icon follows the
already-themed window text); overlay-scrollbar geometry stays out. `make check` passes.

## Done

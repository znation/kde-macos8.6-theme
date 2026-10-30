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

### Platinum GTK 3 drag-and-drop feedback: repaint the header drop arm with the selection fill (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 drag-and-drop plan — it edits the GTK 3 sheet and `tests/test_gtk_theme.py` while that plan edits the GTK 4 sheet and `tests/test_gtk4_theme.py`, and it answers the single stock GTK 3 drag arm that the sheet's landed row, header and rubberband rules leave untouched, so no existing selector it names is changed)

**Goal.** During a GTK 3 drag onto a tree view, the sheet's styled header leaks stock paint:
dragging a column over a header button floods that button in the stock accent fill with
white text and a white inset ring — none of it Platinum, and the state variants re-leak it
under the cursor. The sheet styles `treeview.view header button` rows and selection and the
rubberband but declares no `.dnd` rule, so the stock arm colours every tree-header drop
surface. The drop state must read as the theme's selection: repaint it with the
reference-grounded `#CCCCFF`.

**Verified facts, method and values (checked 2026-10-30).** The sheet carries no dnd rule
or test (grep over `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and
`tests/test_gtk_theme.py` for `dnd` returns nothing), and the GTK drag-and-drop planning in
`PLANS.md` covers only the GTK 4 sheet. The stock inventory re-derived by gresource
extraction on 2026-10-30 —
`gresource extract /usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` — is a single arm, one grouped rule
covering `treeview.view button.dnd` and the legacy `treeview.view header.button.dnd`
spelling, each with `:active`, `:selected`, `:hover` and plain variants, declaring exactly
`padding: 0 6px; color: #ffffff; background-image: none; background-color: #3584e4;
border-style: none; border-radius: 0; box-shadow: inset 0 0 0 1px #ffffff; text-shadow:
none; transition: none;` (grep confirms no other `dnd` selector in that resource: GTK 3 has
no `dndtarget` node and no `dnd tab` arm, so no other surface is covered here). No
reference screenshot shows any drag-and-drop feedback, so every value here is a platform
adaptation: the adaptation reuses the pinned `SELECTION` constant `#CCCCFF` from
`tests/support/platinum_palette.py` — the same value the sheet already applies to selected
rows (`treeview.view:selected`, `list row.activatable:selected`) and text selections — so
the elevated drop state answers the toolkit's accent-family semantics with the theme's
selection family, and no new palette value, artwork or dependency is needed. The stock
`padding: 0 6px` and `transition: none` on the arm stay undeclared, so that transient state
keeps the stock's own geometry and transition choices, mirroring the waiting GTK 4 plan.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, insert directly
after the `treeview.view:selected:backdrop, list row.activatable:selected:backdrop` rule
(the rule ending before the `list row:focus` comment block) a dated adaptation comment and
one grouped rule. Comment convention follows the landed row-selection commentary: name the
absent reference surface, that the stock GTK 3 paints this state with its accent family,
and that the selection `#CCCCFF` replaces it — keeping the stock scheme's name and library
names out of the comment text, as `tests/test_gtk_theme.py`'s
`test_imports_nothing_and_does_not_mention_adwaita` and palette-content assertions require.
The rule covers twelve selectors: `treeview.view button.dnd`, `treeview.view
button.dnd:hover`, `treeview.view button.dnd:active`, `treeview.view button.dnd:selected`,
`treeview.view header.button.dnd`, `treeview.view header.button.dnd:hover`, `treeview.view
header.button.dnd:active`, `treeview.view header.button.dnd:selected`, `treeview.view
header button.dnd`, `treeview.view header button.dnd:hover`, `treeview.view header
button.dnd:active` and `treeview.view header button.dnd:selected` — the stock pair of
spellings plus the sheet's own landed header chain — declaring exactly `background-color:
#CCCCFF;` `background-image: none;` `color: #000000;` `text-shadow: none;` `box-shadow:
none;` `border-style: none;` `border-radius: 0;`. The state variants mirror the stock arm
list, otherwise the stock `:hover` variants outrank a plain `.dnd` rule and re-leak the
accent under the cursor. In `tests/test_gtk_theme.py`, add `TestGtkTheme` tests beside
`test_row_selection_backdrop`, using the shared `assert_rule` helper and the imported
`SELECTION` and `BLACK` constants: `test_header_drop_indicator` asserting every one of the
twelve selectors carries exactly `{"background-color": SELECTION, "background-image":
"none", "color": BLACK, "text-shadow": "none", "box-shadow": "none", "border-style":
"none", "border-radius": "0"}`; `test_header_drop_arm_carries_no_padding` asserting
`"padding" not in self.rules[<a plain representative selector>]`; and
`test_no_dndtarget_node_declared` asserting the sheet text contains no `dndtarget` match,
pinning that the GTK 3 inventory stays the single header/button arm. In
`docs/invariants.md`, append one row under `## gtk`: no collected screenshot shows GTK
drag-and-drop feedback; the stock inventory (the one grouped `button.dnd`/
`header.button.dnd` arm; GTK 3 declares no `dndtarget` node or `dnd tab` arm) comes from
the `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in
`/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, extracted with gresource on 2026-10-30; the drop
state reuses the pinned `#CCCCFF` selection instead of the stock accent values, a platform
adaptation grounded in the landed selection recipes; the declaration checks do not
establish rendered pixels.

**Acceptance criteria.** The dnd rule exists in the GTK 3 sheet with exactly the pinned
declarations, so dragging a column over a header button paints the flat `#CCCCFF`
selection with black text and no white ring or accent leak in any drag state (body buttons
dragged over inside the tree view get the same flat fill); deleting any pinned declaration,
changing any pinned value, re-adding padding to the arm, or declaring a `dndtarget` rule
fails one of the new tests or the absence pin. Every landed assertion in
`tests/test_gtk_theme.py` passes unchanged — the rule sits beside the row block, so no
existing selector or declaration shifts; `test_imports_nothing_and_does_not_mention_adwaita`,
`test_only_palette_hex_literals` and `test_no_universal_selector` pass because the change
adds no import, selector star and only already-pinned hex values. Scope is the two named
files plus `docs/invariants.md`; the GTK 4 sheet's `dndtarget`, `.after`/`.before` and
header arms stay outside this plan (they belong to the waiting GTK 4 drag-and-drop plan);
overlay-scrollbar geometry stays out. `make check` passes.

## Done

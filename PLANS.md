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

### Platinum GTK 4 scroll areas: clear the stock overshoot and undershoot edge bands (planned 2026-10-29 by the plan role; independent of the waiting linked-group plan — it changes different selectors and properties beside the scrollbar section, so no rule text overlaps)

**Goal.** In libadwaita applications using the supported `make apply-gtk` GTK 4 user
stylesheet import, the stock theme still paints two families of scroll-edge effects that
no reference screenshot of Mac OS 8.6 shows: translucent shade-coloured fade bands
("undershoot", the `undershoot.top`/`.bottom`/`.left`/`.right` child nodes of a scrolled
window, drawn with an inset box-shadow plus a 4px linear gradient) and radial over-scroll
glows ("overshoot", the `overshoot.top`/`.bottom`/`.left`/`.right` child nodes, drawn with
two radial gradients as a background image). Platinum scroll areas are flat: the white field
runs to the frame with nothing at the edge, so both families must render nothing.

**Verified facts, method and values (checked 2026-10-29).** The stock theme resource
`/org/gnome/Adwaita/styles/base.css` inside `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`
(extracted with `gresource`) declares every arm by selector; an inventory of the extract
gives these painting arms and only these: (a) six generic direction arms,
`scrolledwindow.undershoot-top > undershoot.top`, `scrolledwindow.undershoot-bottom >
undershoot.bottom`, and the four `scrolledwindow.undershoot-start`/`-end` `:dir(ltr)`/`:dir(rtl)`
left/right arms, each with an inset `box-shadow` and a linear-gradient `background`;
(b) `columnview ~ undershoot.top, treeview.view ~ undershoot.top, window.print:not(.ssd-frame)
treeview.dialog-action-box ~ undershoot.top`; (c) the dropdown and combobox popover search
arms `dropdown popover.menu .dropdown-searchbar + scrolledwindow:not(.undershoot-top) >
undershoot.top` and its `combobox popover.menu` sibling; (d) the two `popover.emoji-picker
scrolledwindow.view:not(.undershoot-top) > undershoot.top` and `-bottom` arms; (e) the
`filechooser gridview ~ undershoot.top` and `filechooser placesview > stack > scrolledwindow
> undershoot.bottom` arms; (f) `row.combo popover > contents .combo-searchbar + scrolledwindow
> undershoot.top`; (g) the toolbar-view scrolledwindow arms `toolbarview.undershoot-top
scrolledwindow > undershoot.top` and its `-bottom` sibling; and (h) four flat
`scrolledwindow > overshoot.top`/`.bottom`/`.left`/`.right` rules whose radial gradients sit
on `background-image` (their `background-color` is already transparent and
`border`/`box-shadow` are already none). All node and class names are GTK or widget-runtime
node names, not library branding. The extract contains two reset arms — the
`window.print:not(.ssd-frame) treeview.dialog-action-box ~ undershoot.top` reset that clears
the box-shadow for its contexts and the toolbar-view popover scrolledwindow reset — which
stay working because this plan copies selector text verbatim and leaves them unregenerated.
The mechanism this project uses for every GTK 4 stock override is the one the landed plans
record: the user stylesheet imported by `make apply-gtk` supplies the later override at the
stock selector's specificity, so each neutralizer mirrors its stock arm's selector text
verbatim. No palette value is new: every declaration is `background: none; box-shadow: none;`
(undershoot) or `background-image: none;` (overshoot). No collected reference screenshot
(`macos8.6-screenshots/`) shows a GTK scroll-edge band of either family, so this is a
platform adaptation whose grounding is the absence of any Platinum edge band — the same
absence the landed flat statusbar, infobar and scrollbar recipes assert.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, directly after the
scrollbar trough-margin adaptation block that begins with the "no reference shows GTK trough
spacing" comment: (1) add a dated comment naming the missing reference surface (a GTK
scroll-edge band of either family) and the clearance policy; it must not contain the library
string the sheet test rejects (`tests/test_gtk4_theme.py::TestGtk4Theme::test_stands_alone`
asserts no "adwaita" in the sheet). (2) Add one grouped rule listing arms (a)–(g) verbatim,
separated by commas, declaring exactly `background: none; box-shadow: none;`. (3) Add four
rules `scrolledwindow > overshoot.top`, `.bottom`, `.left` and `.right`, each declaring
exactly `background-image: none;` (the stock rules already leave their other paint
properties neutral). In `tests/test_gtk4_theme.py`, add two `TestGtk4Theme` tests using the
cases' `assert_rule` helper: `test_undershoot_bands_cleared` (asserts the grouped rule with
the mirror arm selectors declares `background: none` and `box-shadow: none`) and
`test_overshoot_fades_cleared` (asserts each of the four overshoot selectors declares
`background-image: none`). The new rules sit beside the landed scrollbar adaptations, so the
existing `test_scrollbar`, overlay and trough-margin assertions stay untouched. In
`docs/invariants.md`, append one row under `## gtk`: no collected screenshot shows a GTK
overshoot or undershoot band; the arm inventory (all node and class-name selector spellings,
including the print, emoji-picker, filechooser and toolbar-view contexts) comes from the
stock `/org/gnome/Adwaita/styles/base.css` in `/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`,
inspected 2026-10-29; the clearance values are plain `none`/transparent declarations, not
measured pixels; the user stylesheet import supplies the override at mirrored specificity;
and the declaration checks do not establish rendered pixels.

**Acceptance criteria.** Every stock undershoot painting arm listed above is matched by a
verbatim user-sheet arm declaring `background: none; box-shadow: none;`, and every stock
overshoot arm is matched at equal specificity declaring `background-image: none;`, so a
rendered scroll area keeps its field flush to the frame with no band or glow at the edge;
deleting a mirror arm, adding a wrong property, or widening the strip to an arm the stock
does not paint fails one of the two new tests. The existing scrollbar, trough and overlay
assertions pass unchanged. Scope is the three named files; GTK 3 undershoot and overshoot
arms (a separate future plan — the GTK 3 stock theme spells arms differently), the
overshoot/undershoot node geometry and the linked-group plan are outside this plan. No new
palette value, artwork or dependency. `make check` passes.

## Done

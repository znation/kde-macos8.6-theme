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

_None yet._

### Platinum GTK 3 OSD overlay surfaces: repaint the stock dark container bands with the landed infobar band (planned 2026-10-30 by the plan role; independent of the waiting Firefox scrollbar plan — it appends rules at the end of the GTK 3 sheet, one test beside the landed `.app-notification` band in `tests/test_gtk_theme.py` and a row in the `## gtk` invariants table, while that waiting entry edits the two Firefox sheets, their suites and the `## firefox` table; neither entry names a file, selector or test the other changes)

**Goal.** GTK 3's overlay surfaces — a fullscreen video toolbar, a scale button's
value bubble, a touch-selection or magnifier popover — still draw stock Adwaita's
translucent dark bubble: the theme's GTK 3 sheet declares nothing for the `.osd`
family (grep over `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` returns no `osd`
rule), while the theme already replaces the identical stock bubble on GTK 3's
`.app-notification` with the landed light infobar band and keeps GTK 4's OSD
machinery on its own landed arms (`video image.osd`, `progressbar.osd`,
`.osd switch:checked`). Give the GTK 3 sheet one container-band guarantee: every
stock OSD container the toolkit names takes the landed infobar band instead of
the dark bubble.

**Verified facts (probed 2026-10-30, libgtk-3 3.24.49).** `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` shows the stock container
claims the plan must beat: the grouped rule naming `.osd .scale-popup`,
`.app-notification`, `.app-notification.frame`, `.csd popover.background.osd`,
`popover.background.osd`, `.csd popover.background.touch-selection`,
`.csd popover.background.magnifier`, `popover.background.touch-selection`,
`popover.background.magnifier` and `.osd` paints
`background-color: rgba(53,53,53,0.9)` with `color: #eeeeec`, white text and
icon shadows, and its `:backdrop` sibling clears only those shadows;
`toolbar.osd` paints the same bubble with `padding: 13px` and a 5px radius (its
`.left/.right/.top/.bottom` arms already set `border-radius: 0`). The landed
`.app-notification` band (appended after the statusbar block) beats this stock
group only for its own two widget pairs; the other eight selectors stay
unrestated, so those overlay containers keep the dark bubble. No collected
reference screenshot shows an OSD overlay, so this is a platform adaptation
reusing the landed infobar band values — pinned by `INFOBAR` in
`tests/support/gtk_theme_spec.py`, asserted by
`tests/test_gtk_theme.py::TestGtkTheme::test_infobar`/`test_app_notification_band`,
with the `#DDDDDD` face grounded by
`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face`
and the etched pair by `tests/test_desktoptheme_line.py::TestLineReference`.
The `.osd`, `popover.background`, `.scale-popup` and `toolbar.osd` class and
node names and the stock `padding: 13px` are GTK-required. The stock's
five `.osd`-family `:backdrop` selectors carry the same node paints, so the
plan reuses the landed restatement's shape: include the `:backdrop` arms in the
one grouped rule.

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`,
append at the sheet's end, after the landed file-chooser places-sidebar block,
a dated provenance comment naming the missing reference surface, the gresource
probe above and the reuse of the landed `.app-notification` recipe, followed by
exactly one grouped rule naming the fourteen stock selectors
`.osd .scale-popup`, `.csd popover.background.osd`, `popover.background.osd`,
`.csd popover.background.touch-selection`, `.csd popover.background.magnifier`,
`popover.background.touch-selection`, `popover.background.magnifier`, `.osd`,
`.osd .scale-popup:backdrop`, `popover.background.osd:backdrop`,
`popover.background.touch-selection:backdrop`,
`popover.background.magnifier:backdrop`, `.osd:backdrop` and `toolbar.osd`,
declaring exactly `background-color: #DDDDDD; background-image: none;
color: #000000; border: 0; border-bottom: 1px solid #888888;
border-radius: 0; box-shadow: inset 0 -1px #FFFFFF; text-shadow: none;` and
`-gtk-icon-shadow: none;` — the landed `.app-notification` declaration set
verbatim, with `border: 0` before `border-bottom`. Keep stock's
`toolbar.osd` padding; the edge-class arms already square it. (2) In
`tests/test_gtk_theme.py`, add `TestGtkTheme.test_osd_overlay_bands` beside
`test_app_notification_band`: assert each of the fourteen selectors against the
same nine-declaration expected dictionary the app-notification test builds
(that module's local `expected` literal, keyed on `FACE`, `BLACK`, `ETCH_DARK`
and `WHITE`), and assert that the set of parsed sheet selectors matching
`.osd`, `magnifier`, `touch-selection` or `scale-popup` equals the expected
fourteen, so no untested OSD arm can appear. Do not reuse `assert_infobar`
alone: the exact-dictionary equality distinguishes the full restatement from a
partial `INFOBAR` subset. (3) In `docs/invariants.md`, in the `## gtk` table,
append one row: the guarantee — every stock OSD overlay container named above
draws the infobar band with black text and no shadows, backdrop included — with
the test column naming
`tests/test_gtk_theme.py::TestGtkTheme::test_osd_overlay_bands` and the test it
mirrors, `...::test_app_notification_band`; the provenance cell records the
missing reference surface, the `gresource` probe (libgtk-3 3.24.49,
`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, inspected 2026-10-30), the
reused landed band and its grounding tests, the GTK-required names, stock
padding, and the close-out note that declaration checks do not establish
rendered pixels. Trim no landed row; `tests/test_invariants.py` parses the
register.

**Scope notes for later plan runs.** The stock OSD families this entry leaves
unrestated are recorded here so a later planner need not re-probe: the dark
`entry`/`spinbutton:not(.vertical)` container fields and their focus, backdrop
and disabled arms; `button.osd` and the grouped `.osd button`/flat families
including the suggested-action and destructive-action arms; `.osd check`
and `.osd radio`; the `.osd` progress and scale trough, fill, highlight and
slider arms; `progressbar.osd`'s more specific transparent-trough override
(the GTK 3 mirror of the landed GTK 4 `progressbar.osd` arms), plus the
`.scale-popup button.flat` and `colorchooser .popover.osd` corners. Each is a
surface-specific GTK 3 plan of its own; this entry claims only the containers.

**Acceptance criteria.** The GTK 3 sheet ends with the one grouped fourteen-
selector rule whose complete declaration dictionary is the landed
app-notification band's nine declarations; changing any of the fourteen
selectors or deleting the rule fails `test_osd_overlay_bands`; the existing
`test_app_notification_band`, `test_status_bar`, `test_infobar` and palette
assertions stay green, and the `.app-notification` selectors keep their own
landed rule untouched. Scope is the GTK 3 sheet, `tests/test_gtk_theme.py`,
`docs/invariants.md` and nothing else: no GTK 4 rule, no Firefox sheet, no new
asset, colour literal beyond the landed hex values, dependency or
`!important`. `make check` passes.

## Done

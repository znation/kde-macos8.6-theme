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


_None yet._

### Platinum GTK 3 OSD entry and spin-button fields: restate the stock dark field arms with the landed entry recipe (planned 2026-10-30 by the plan role; independent of the waiting Firefox toolbar-fields plan — it appends four field rules to the GTK 3 sheet, adds one test beside `test_osd_overlay_bands` in `tests/test_gtk_theme.py` and a row in the `## gtk` invariants table, while that entry edits the Firefox chrome sheet, `tests/support/firefox_chrome_cases.py`, `tests/test_firefox_theme_shell.py` and the `## firefox` table; no shared file, selector or test)

**Goal.** The landed GTK 3 OSD container plan repainted every stock OSD overlay
container with the light infobar band, but the fields inside them are still
stock dark: the theme's GTK 3 sheet declares nothing for the `.osd` entry arms
(grep: the sheet's only `osd` rules are the landed container block), so the
toolkit's installed resource supplies them — four grouped arms painting
`entry` and horizontal `spinbutton` fields translucent dark with white text
and black text-shadows inside a container the theme now draws `#DDDDDD`.
Restate all four arms to the landed entry recipe, so an OSD field is a
Platinum field like every other entry.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, libgtk-3 3.24.49).** The
resource's four `entry`-overriding OSD field arms, each a grouped
spinbutton/entry rule: `.osd spinbutton:not(.vertical), .osd entry` (`color:
white`, `rgba(0,0,0,0.7)` border, `rgba(0,0,0,0.5)` background (a field the
landed light container band contradicts), `background-clip: padding-box`,
both text and icon shadows `0 1px black`); its `:focus` sibling (same field,
`#3584e4` border-colour and an `inset 0 0 0 1px #3584e4` ring); its
`:backdrop` sibling (same dark field, shadows cleared); its `:disabled`
sibling (`rgba(71,71,71,0.5)` field, `#919190` text). No collected reference
screenshot shows a GTK OSD overlay or a field inside one, so this is a
platform adaptation reusing the landed entry recipe — pinned by `ENTRY_FIELD`
in `tests/support/gtk_theme_spec.py` (`WHITE` face, `BLACK` square border,
inset `GREY` etch, `BLACK` text), the landed focus outline pinned by
`tests/test_gtk_theme.py::TestGtkTheme::test_entry_focus_outline` and
`...::test_horizontal_spinbutton_focus_outline` (the dotted-outline trio
`outline: 1px dotted #000000; outline-offset: 0; -gtk-outline-radius: 0;`,
reused from `button:focus` per the landed header comment), and the disabled
text grey pinned by `...::test_disabled_text`, whose `DISABLED_TEXT["color"]`
(`tests/support/gtk_theme_spec.py`, the `ETCH_DARK` value `#888888`) is
re-derived from the colour scheme's `[Colors:Button] ForegroundInactive`. The
arm selector sets and state names are GTK-required (they mirror the toolkit
resource's own grouped rules).

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`,
append after the landed OSD container block (the `toolbar.osd` grouped rule
that currently closes the sheet) a dated provenance comment naming the
missing reference surface, the gresource probe above and the reuse of the
landed entry recipe, followed by exactly four grouped rules: `.osd
spinbutton:not(.vertical), .osd entry` declaring `background-color: #FFFFFF;
background-image: none; border: 1px solid #000000; border-radius: 0;
box-shadow: inset 1px 1px #999999; color: #000000; text-shadow: none;
-gtk-icon-shadow: none;` (the landed `ENTRY_FIELD` five declarations verbatim
plus the stock-normal arm's own `text-shadow` and `-gtk-icon-shadow` shadow
claims cleared); the same seven declarations on `.osd
spinbutton:focus:not(.vertical), .osd entry:focus` plus the landed focus trio
(the border shorthand replaces stock's `#3584e4` border-colour and the
box-shadow declaration replaces stock's blue inset ring); the same seven on
`.osd spinbutton:backdrop:not(.vertical), .osd entry:backdrop` (stock's
backdrop arm repaints the dark field, so it needs the full restatement, not
just shadow clears); the same seven on `.osd spinbutton:disabled:not(.vertical),
.osd entry:disabled` with `color: #888888`. Do not touch the landed
`entry`/`spinbutton:not(.vertical)` rules, their focus rules, the landed
disabled-text rule or the landed OSD container block — each restated arm is
the same selector stock declares at higher specificity, so the landed
base-field rules keep governing outside `.osd`. From the same probe, scope
notes for later surface plans (recorded here, not this change): the
spin-button's inner transparent text node `.osd spinbutton:not(.vertical)
entry`, its button row `.osd spinbutton:not(.vertical) button(:hover/:
backdrop/:disabled)` and its dir/last-child radius arms, and the vertical
`.osd spinbutton.vertical button:first-child` family. (2) In
`tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_entry_fields` beside
`test_osd_overlay_bands`: build two expected dictionaries by extending the
landed `ENTRY_FIELD` spec with `background-image: none`, `text-shadow: none`
and `-gtk-icon-shadow: none` (so the reuse is visible in the code, not a
coincidence of literals), the focus dictionary further adding the outline
trio and the disabled dictionary replacing `color` with the value
`DISABLED_TEXT["color"]` shares (`#888888`); assert each of the eight
per-selector keys `tests/support/gtk_css.parse_css` splits out of the four
grouped rules against the expected dictionary of its arm, and add a scope
assertion that the set of parsed sheet selectors containing `.osd entry` or
`.osd spinbutton` equals exactly those eight, so no other OSD entry arm can
appear untested. (3) In `docs/invariants.md`, in the `## gtk` table, append
one row: the guarantee — inside a stock OSD container, horizontal entries and
spin-button fields carry the landed entry field (opaque white face, black
square border, inset grey etch, black text; disabled text the Inactive grey;
focus the landed dotted outline) through all four stock state arms instead of
the toolkit's dark translucent field — with the test column naming
`tests/test_gtk_theme.py::TestGtkTheme::test_osd_entry_fields` and the tests
it mirrors (`...::test_entry`, `...::test_entry_focus_outline`,
`...::test_disabled_text`); the provenance cell records the missing reference
surface, the gresource probe (libgtk-3 3.24.49,
`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, inspected 2026-10-30), the
reused `ENTRY_FIELD` spec, the GTK-required arm selectors and states, and the
close-out that declaration checks do not establish rendered pixels. Trim no
landed row; `tests/test_invariants.py` parses the register.

**Acceptance criteria.** The GTK 3 sheet ends with the four grouped arms whose
complete parsed dictionaries are exactly the ones above; changing any of the
eight selectors, deleting an arm, dropping a shadow-clear declaration or
reintroducing stock's blue focus ring or dark field fails
`test_osd_entry_fields`; `test_entry`, `test_disabled_text`,
`test_entry_focus_outline`, `test_horizontal_spinbutton_focus_outline`,
`test_osd_overlay_bands`, `test_app_notification_band` and the palette
assertions stay green, and the landed container block keeps its landed text.
Scope is the GTK 3 sheet, `tests/test_gtk_theme.py`, `docs/invariants.md` and
nothing else: no GTK 4 rule, no Firefox sheet, no new asset, dependency or
`!important`; the only colour literals are the landed `#FFFFFF`, `#000000`,
`#999999` and `#888888`. `make check` passes.

## Done

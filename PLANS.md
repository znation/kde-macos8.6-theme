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

### Platinum GTK 3 scrolled windows: paint the scrollbar-corner junction with the scrollbar band (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 linked-group extension plan — it edits the GTK 3 sheet and `tests/test_gtk_theme.py` while that plan edits the GTK 4 sheet and `tests/test_gtk4_theme.py`, and it extends the landed GTK 3 overshoot plan with the corner node that landing explicitly left out, per PLANS-DONE.md's sentence "the scrollbar-corner junction and overlay-scrollbar geometry are outside this plan")

**Goal.** When a GTK 3 scrolled window shows both of its scrollbars at once, the corner node
between them is unpainted on the Platinum theme: the sheet carries no
`scrolledwindow junction` rule, so the corner square behind the two scrollbar ends renders as a hole in the
band while the stock theme paints it to blend the troughs together. The junction must read
as the flat Platinum scrollbar band in normal and backdrop state, like the rest of the
band this sheet already declares.

**Verified facts, method and values (checked 2026-10-30).** The stock resource
`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` inside
`/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (extracted with `gresource` on 2026-10-30) carries exactly
three junction arms: `scrolledwindow junction` declaring `border-color: transparent;`
`border-image: linear-gradient(to bottom, #cdc7c2 1px, transparent 1px) 0 0 0 1/0 1px
stretch;` and `background-color: #cecece;`; `scrolledwindow junction:dir(rtl)` declaring
only `border-image-slice: 0 1 0 0;`; and `scrolledwindow junction:backdrop` declaring a
lighter `#d5d0cc` gradient and `background-color: #efedec; transition: 200ms
ease-out;`. The stock resource carries no undershoot arm, as the landed overshoot plan
already recorded. The resource `/org/gnome/Adwaita/styles/base.css` inside
`/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0` (extracted 2026-10-30) carries no junction
arm at all, so the GTK 4 sheet is untouched — GTK 4 shows no stock junction paint to
answer. No collected screenshot in `macos8.6-screenshots/` shows the GTK scrollbar corner,
so every value here is a platform adaptation: the adaptation reuses the landed scrollbar
band `#EEEEEE` (pinned by the sheet's `scrollbar` rule and the `TROUGH` constant in
`tests/support/platinum_palette.py`) instead of the stock `#cecece`/`#efedec` paints, and
clears the stock border-image trough line the same way the landed overshoot clearance
declares plain `none`. Because the replacement declares `border-image: none`, the stock
`:dir(rtl)` slice arm has no border-image to slice and holds no visual value — the sheet
leaves it undeclared and the comment says so; the `:backdrop` arm must be replaced because
without a rule it keeps the stock backdrop colours and the 200ms transition.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, insert
directly after the landed overshoot group rules (the block ending in the
`background-image: none;` group under the `/* Adaptation 2026-10-30: …over-scroll glow… */`
comment) a dated adaptation comment and two rules: `scrolledwindow junction` and
`scrolledwindow junction:backdrop`, each declaring exactly `background-color: #EEEEEE;`
`border-color: transparent;` `border-image: none;`. The comment names what the stock GTK 3
resource paints on the junction, that no collected reference screenshot shows the corner,
that the band value is the landed scrollbar band, and that the stock `:dir(rtl)` slice arm
is left undeclared as inert under a none border-image — keeping library names out of the
sheet's comments as `tests/test_gtk_theme.py`'s content assertions require. In
`tests/test_gtk_theme.py`, add two `TestGtkTheme` tests beside the two overshoot tests,
using the shared `assert_rule` helper (and `TROUGH` from
`tests/support/platinum_palette.py`): `test_junction_shares_the_scrollbar_band` asserting
`scrolledwindow junction` carries exactly the three declarations above, and
`test_junction_backdrop_shares_the_scrollbar_band` asserting the same for
`scrolledwindow junction:backdrop`; the first test additionally asserts the sheet stops
at the two-declaration shape by asserting `"junction:dir"` is absent from the sheet text,
pinning the undeclared RTL arm. Leave every landed assertion unchanged; the rules sit
beside the overshoot block, so no existing scrollbar, thumb or overlay assertion shifts.
In `docs/invariants.md`, append one row under `## gtk`: no collected screenshot shows a
GTK scrollbar corner junction; the three-arm stock inventory (the normal rule, the
`:dir(rtl)` slice arm and the `:backdrop` rule) comes from the stock
`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in
`/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, extracted with `gresource` and headless-probed
over broadway on 2026-10-30; the corner reuses the landed `#EEEEEE` scrollbar band
instead of the stock `#cecece`/`#efedec` paints, a platform adaptation grounded in the
flat Platinum field the landed scrollbar and overshoot recipes assert; the RTL slice arm stays undeclared because its slice has no
border-image to apply to; the declaration checks do not establish rendered pixels.

**Acceptance criteria.** Both junction selectors exist in the GTK 3 sheet with exactly the
three pinned declarations each, so a rendered scrolled window with both scrollbars shows
the corner as the flat `#EEEEEE` band with no stock trough line or colour change in normal
or backdrop state; deleting either rule, changing any pinned value, or widening the
junction block to any further selector (including a `:dir(rtl)` arm) fails one of the two
new tests or the pinned absence check. The landed scrollbar, overshoot and overlay
assertions pass byte-for-byte unchanged. Scope is the three named files; overflow-scroll
overlay geometry, stepper art and GTK 4 (no stock junction arm there) stay outside this
plan; no new palette value, artwork or dependency. `make check` passes.

## Done

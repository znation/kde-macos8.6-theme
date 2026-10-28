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

### Platinum GTK status bar: paint `GtkStatusbar` as the menu-bar band in GTK 3 and GTK 4 (planned 2026-10-27 by the plan role; the `## Planned` queue holds no other entry, so nothing waits beside or behind this plan, which touches `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py` and appends exactly one row to `docs/invariants.md`; no other GTK plan waits behind it)

**Goal.** The landed GTK sheets paint the menu bar, toolbar, infobar, search bar and action bar as the Platinum band (`#DDDDDD` face, black text, `#888888`/`#FFFFFF` etched bottom rule) but a `GtkStatusbar` — the long-lived bottom strip that GTK 4 still ships to GTK 3-era status-window applications — keeps stock paint: no background of its own under the sheet's `window` colours and no etched rule, so a window's bottom status strip reads as an unbounded area. This plan paints the status bar as the landed menu-bar band, the same recipe byte-for-byte, in both toolkits, and clears one accidental paint the landed `frame > border` rule draws inside it on GTK 3.

**Verified facts (checked 2026-10-27).** `grep -c statusbar` returns 0 for `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `gtk-4.0/gtk.css`, `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py`, and no PLANS.md `## Planned` entry nor PLANS-DONE.md or BUGS-FIXED.md finished record names a GTK status bar. Live-probed with PyGObject (GTK 3.24.49 and GTK 4.18.6, the toolkits the landed infobar row names): `Gtk.Statusbar.new()` builds a GTK 3 tree `Statusbar > Frame > Box > Label` (the `Frame`'s shadow type reads `GTK_SHADOW_NONE`) and a GTK 4 tree `statusbar > box > label` (no frame node; `Gtk.Statusbar.new()` in 4.18.6 emits a `DeprecationWarning` but the class still ships and instantiates, and libadwaita applications draw no `GtkStatusbar` at all). docs.gtk.org states on both the GtkStatusbar pages: "GtkStatusbar has a single CSS node with name `statusbar`" — so the root `statusbar` node is the one guaranteed handle in both toolkits. GTK 4.18.6's built-in css (embedded in `libgtk-4.so`) only sets `statusbar { padding: 6px 10px 6px 10px; }` — no face or border of its own, so the band's background and the etched rule are the only strip paint and the GTK-required padding stays untouched. GTK 3 consequence verified against the 3.24.49 source (`gtk/gtkframe.c`, fetched from the 3.24.49 tag): a `GtkFrame` always owns the documented `frame > border` subnode and `GTK_SHADOW_NONE` only toggles the `.flat` class on it — the landed `frame > border, .frame` rule matches `frame > border.flat` and paints its sunken field border unconditionally, so today's GTK 3 statusbar carries a sunken `#000000` box inside itself that no test pins; this plan clears that border with a scoped arm rather than leaving the band to sit around a sunken field.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows a GTK status bar, so the strip samples no new reference pixel: it reuses only reference-grounded values the sheets already pin — the `#DDDDDD` face and black text via the menu-bar band (`tests/test_colorscheme_reference.py::TestReferenceAnchors::test_menu_bar_face`) and the etched pair (`tests/test_desktoptheme_line.py::TestLineReference`), through the sheets' landed `toolbar, menubar` and infobar rules and the shared `INFOBAR` spec. The band geometry and the `statusbar` node name are GTK-required, as is the GTK 3 `statusbar > frame > border` clearing arm's `frame`/`border` node pair. `:backdrop` stays out of scope, as the landed infobar, search-bar and action-bar decisions scoped it out, and the etched rule stays the menu-bar band's bottom rule rather than a mirrored top rule because the landed search/action bar plan decided the sheets ship exactly one band recipe and the bottom-standing action bar already took that bottom rule; this is decided here so no design question is left open.

**Approach.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, directly after the landed `searchbar > revealer > box, actionbar > revealer > box` rule (the GTK 3 sheet's last rule), add:

```css
/* A status bar draws the menu-bar band: the #DDDDDD face, black text and the
   etched bottom rule. The statusbar's internal shadowless GtkFrame border
   stays flat, so the landed frame rule does not draw the sunken field
   inside the band; :backdrop stays out of scope. */
statusbar {
  background-color: #DDDDDD;
  color: #000000;
  border-bottom: 1px solid #888888;
  box-shadow: inset 0 -1px #FFFFFF;
}

statusbar > frame > border {
  border-style: none;
  box-shadow: none;
}
```

In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, directly after the landed `searchbar > revealer > box, actionbar > revealer > box` rule (the GTK 4 sheet's last rule), add the same band rule under a comment that drops the GtkFrame sentence and records that the GTK 4 statusbar builds `statusbar > box > label` with no frame node (verified above), so the sheet gains no clearing arm.

In both sheets' provenance header comments, append one sentence after the search-bar/action-bar sentence and before the closing `*/`: "A status bar band reuses the same menu-bar band with the same etched bottom rule, and on GTK 3 its shadowless internal frame border stays flat; no reference screenshot shows a GTK status bar, and the statusbar node name is GTK-required."

In `tests/test_gtk_theme.py::TestGtkTheme`, after the landed `test_action_bar`, add `test_status_bar` calling `self.assert_infobar(("statusbar",))` — reusing the shared `INFOBAR` spec in `tests/support/gtk_theme_spec.py` and `tests/support/gtk_rule_cases.py` so the band stays byte-identical to the landed band rules, with no new constant and no edit to any landed rule — and `test_status_bar_frame_border_is_flat` calling `self.assert_rule("statusbar > frame > border", {"border-style": "none", "box-shadow": "none"})`.

In `tests/test_gtk4_theme.py::TestGtk4Theme`, after the landed `test_action_bar`, add the same `test_status_bar` with the same `assert_infobar` call.

Extend no landed assertion: the shared `assert_rule` machinery already parses both sheets, so the only change is two tests in the GTK 3 suite and one in the GTK 4 suite.

In `docs/invariants.md`, in the `## gtk` table: append exactly one row after the last gtk row with the guarantee in one sentence (both sheets paint the `statusbar` node as the menu-bar band — the `#DDDDDD` face, black text and the `#888888`/`#FFFFFF` etched bottom rule — while the GTK 3 sheet keeps the statusbar's shadowless internal `frame > border` flat and the GTK 4 sheet leaves the built-in `6px 10px` statusbar padding untouched) and the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_status_bar`, `test_status_bar_frame_border_is_flat` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_status_bar`; trim no landed row (this plan closes no other surface).

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The GTK 3 sheet gains exactly the two rule blocks above and the GTK 4 sheet exactly the one band rule directly after each sheet's landed search-bar/action-bar rule, introducing no hex outside `{#DDDDDD, #888888, #FFFFFF, #000000}`, changing no landed rule's text and adding no `!important`.
- Both sheets' headers gain exactly one appended sentence after the search-bar/action-bar sentence and before `*/`.
- The three new tests pass through the shared `assert_infobar`/`assert_rule` path against the landed `INFOBAR` spec, and no landed test or support constant changes.
- `docs/invariants.md` gains exactly one appended row after the last `## gtk` row naming the three new tests, with no landed row's wording changed; `tests/support/invariants.py`'s register stays in step.
- `make check` passes.

## Done

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

### Platinum Firefox scrollbars: recolour the chrome and page scrollbars with the scrollbar band and thumb (planned 2026-10-30 by the plan role; independent of the waiting GTK 3 drag-and-drop plan — it edits the two Firefox sheets, their suites and the `## firefox` invariants table while that plan edits the GTK 3 sheet, `tests/test_gtk_theme.py` and the `## gtk` table, and neither entry names a selector or test the other changes)

**Goal.** Every scrollable Firefox surface still draws a non-Platinum scrollbar: the
browser chrome paints the toolkit's platform scrollbars (GTK's overlay bars on this
host) and web pages paint their theme's own trough and thumb, neither of which is
the theme's flat `#EEEEEE` band under a `#DDDDDD` thumb. The GTK sheets already
carry that scrollbar recipe; the landed Firefox sheets style tabs, menus, panels,
tooltips, the find bar and five about-pages but declare nothing about scrollbars,
so the Firefox look is inconsistent with the GTK one on the most common surface
of all. Give both Firefox sheets one scrollbar guarantee: `scrollbar-color` on the
chrome `:root` block recolours the UI scrollbars, and a top-level `:root` rule in
`userContent.css` recolours page scrollbars, both thumb `#DDDDDD` over trough
`#EEEEEE`.

**Verified facts (checked 2026-10-30, Firefox ESR 153.6.0esr).** Grep over
`theme/firefox/`, `tests/`, `PLANS-DONE.md`, `BUGS.md` and `docs/invariants.md`
returns no `scrollbar-color` match: no landed, planned or fixed entry covers
Firefox scrollbars. `unzip -p /usr/lib/firefox-esr/omni.ja
chrome/toolkit/res/scrollbars.css` shows the toolkit's `scrollbar`, `thumb`,
`scrollbarbutton` and `scrollcorner` parts are native anonymous nodes carrying
only `-moz-default-appearance: scrollbar*` declarations (no class or id to
brand), plus `@media (-moz-overlay-scrollbars)` arms that fade inactive chrome
bars: the colour sweep is the standard `scrollbar-color` two-tone property
(CSS Scrollbars Styling Level 1, supported since Firefox 64; geometry, band
width, fade and stepper visibility stay the toolkit's). No collected reference
screenshot in `macos8.6-screenshots/` shows a Firefox scrollbar, so both values
are a platform adaptation reusing the reference-grounded desktop-theme scrollbar
art: the flat `#EEEEEE` trough pinned by
`tests/test_desktoptheme_scrollbar.py::TestScrollbarReference` and grounded in
`setup_emaculation.png` by
`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_view_background_alternate`,
and the `#DDDDDD` thumb face of the same artwork pinned by the same module (the
palette constants `TROUGH` and `FACE` in `tests/support/platinum_palette.py`).
The adaptation's limit must be recorded: `scrollbar-color` carries exactly two
colours, so the thumb's raised `#FFFFFF`/`#999999` bevel, the 1px black trough
and thumb outlines and the step boxes have no property equivalent and
stay unpainted — the painted scrollbar keeps the toolkit's geometry and gains
only the two faces. Page-anonymous scrollbars on sites that set their own
`scrollbar-color` keep that author paint; the origin order puts user-origin
`!important` values ahead of normal author styles.

**Approach and files.** (1) In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`,
append to the landed `:root` block (the variable-rule ending before the
`#navigator-toolbox` rule) one declaration `scrollbar-color: #DDDDDD #EEEEEE
!important;` inside it, and one dated provenance comment paragraph naming the
absent reference surface, the toolkit probe above and the adaptation's limit
(two faces only; the thumb bevel, the outlines and the steppers are out of
reach), both faces defined by the desktop-theme pins. (2) In
`tests/support/firefox_chrome_cases.py`, extend the `REQUIRED_RULES[":root"]`
table with `"scrollbar-color": f"{FACE} {TROUGH} !important"` — the shell suite
parses the whole chrome sheet and byte-asserts that table, so the landing is
pinned. (3) In `tests/test_firefox_theme_shell.py`, add
`TestFirefoxChromeShell.test_root_colors_every_chrome_scrollbar` beside
`test_required_rules` asserting `self.rules[":root"]["scrollbar-color"] ==
f"{FACE} {TROUGH} !important"`. (4) In
`theme/firefox/org.macos8.desktop/chrome/userContent.css`, after the telemetry
body's closing brace append a dated provenance comment and the sheet's one
top-level rule

```
:root {
  scrollbar-color: #DDDDDD #EEEEEE !important;
}
```

byte-exact. (5) In `tests/test_firefox_content_theme.py`, add
`TestFirefoxContentTheme.test_root_colors_the_page_scrollbars` that asserts
`self.text.count(":root {") == 1`, that the top-level block is present as the
exact three-line form above, and that no `self.bodies` value contains
`scrollbar-color` (the paint stays one top-level sweep; the per-body suites and
`test_no_rule_paints_page_chrome` parse only their own bodies and see none of
it). (6) In `docs/invariants.md`, in the `## firefox` table, append two rows
(one per sheet side, the chrome row first, before the trailing validation
notes): the chrome-side row's guarantee — the chrome UI scrollbars take the
Platinum `scrollbar-color` on the sheet's `:root` block — with the test column
naming `tests/test_firefox_theme_shell.py::TestFirefoxChromeShell::test_required_rules`
and `...::test_root_colors_every_chrome_scrollbar`; the content-side row's
guarantee — every page scrollbar's thumb and trough take the two Platinum faces
through the sheet's one top-level `:root` rule — with the test column naming
`tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_root_colors_the_page_scrollbars`
and `...::test_palette_is_exact`. Each row's provenance cell names the missing
reference surface (no collected screenshot shows a Firefox scrollbar), the
probe (`unzip -p /usr/lib/firefox-esr/omni.ja chrome/toolkit/res/scrollbars.css`
on 2026-10-30, plus the Firefox-64-supported standard property), the desktop
theme scrollbar pins that ground the two values, and the limitation note (bevel,
outlines and steppers out of the property's reach; geometry stays the toolkit's;
author-origin scrollbar styles on a page keep their paint). Trim no landed row;
`tests/test_invariants.py` parses the register.

**Acceptance criteria.** Both sheets carry the two-face `scrollbar-color` pin:
the chrome `:root` block declares it inside the landed variable set (so
`test_required_rules`, `test_root_colors_every_chrome_scrollbar`,
`test_palette_is_exact` — whose hex set already contains `#DDDDDD` and
`#EEEEEE` — and `test_sheet_has_no_at_rule_or_import` all hold), and the content
sheet carries exactly one top-level `:root` rule whose body is exactly the
pinned declaration while every at-rule body and every at-rule count stays as
landed (`stripped.count("@") == 6` and the body set unchanged). Because
`scrollbar-color` is an inherited property set on the root, every scrollable
box in each document picks it up unless it or a page sets its own style, so
browser popups, sidebars, the library and content scrollbars render a `#DDDDDD`
thumb on a flat `#EEEEEE` trough. Deleting any pinned declaration or changing
either face fails a pinned test; adding a second top-level `:root` rule or a
`scrollbar-color` inside any body fails the content test. Scope is the two named
sheets, the two suites plus `tests/support/firefox_chrome_cases.py` and
`tests/support/firefox_content_cases.py` registers, and `docs/invariants.md`;
no geometry, width, stepper or PDF-viewer-specific rule ships here, the GTK
sheets stay untouched, and `make check` passes.

## Done

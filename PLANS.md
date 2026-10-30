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

### Platinum GTK 3 scroll areas: clear the stock overshoot edge glows (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 scroll-edge plan — it edits the GTK 3 sheet and `tests/test_gtk_theme.py` while that plan edits the GTK 4 sheet and `tests/test_gtk4_theme.py`, so no file or rule text overlaps)

**Goal.** In GTK 3 applications using the installed Platinum theme (`make apply-gtk` sets `gtk-theme-name=org.macos8.desktop`), the stock theme paints radial over-scroll glows: translucent shade-coloured corner fades ("overshoot", the `overshoot.top`/`.bottom`/`.left`/`.right` child nodes of a scrolled window, drawn with two radial `-gtk-gradient` background images). No collected reference screenshot of Mac OS 8.6 shows any such band; Platinum scroll fields are flat, running to the frame, so the glows must render nothing.

**Verified facts, method and values (checked 2026-10-30).** The stock resource
`/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` inside
`/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (extracted with `gresource`) declares scroll-edge
painting in exactly eight arms: `scrolledwindow overshoot.top`, `scrolledwindow
overshoot.bottom`, `scrolledwindow overshoot.left` and `scrolledwindow overshoot.right`
and the same four with `:backdrop`. Each paints radial gradients on `background-image` and
is otherwise neutral (`background-color: transparent; border: none; box-shadow: none;`);
the dark and inverse variants compiled into the same library spell identical selectors with
different palettes, so the arm set is theme-variant independent. A grep of the extract shows
no `undershoot` rule anywhere in the GTK 3 stock theme, and a headless runtime probe
(`broadwayd :21` plus `BROADWAY_DISPLAY=:21`, then a `GtkScrolledWindow` containing a
`GtkTextView`, 2026-10-30) shows GTK 3 creates no undershoot child windows or nodes — the
only `undershoot` string in the library binary is the entry-icon name in the `gtkentry`
rodata — so, unlike the GTK 4 sheet work, there is no undershoot family to neutralize. The
cascade differs from GTK 4: this GTK 3 sheet is a standalone named theme that imports
nothing (`tests/test_gtk_theme.py::TestGtkTheme::test_imports_nothing_and_does_not_mention_adwaita`),
so it is the only theme stylesheet GTK 3 loads and its rules replace the stock arms rather
than racing them; the arm selectors are still copied verbatim so each rule reads beside the
stock text it replaces. No palette value is new: every declaration is
`background-image: none;`. In-sheet comments must not contain the stock library's name —
`test_imports_nothing_and_does_not_mention_adwaita` rejects it — so the provenance comment
names "the stock GTK 3 resource in libgtk-3" and the library path, and
`docs/invariants.md` carries the full provenance.

**Approach and files.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, directly after
the `scrollbar.horizontal button.down` rule that ends the scrollbar button block and before
the `progressbar trough` rule whose rule begins the next section: (1) add a dated comment
naming the missing reference surface (no collected screenshot in `macos8.6-screenshots/`
shows a GTK over-scroll glow) and the clearance policy. (2) Add one grouped rule listing
the eight arm selectors verbatim, comma-separated, declaring exactly `background-image:
none;` — the sheet-rule parser (`tests/support/gtk_css.py::parse_css` with
`_split_selector_list`) keys grouped rules per selector, and the GTK 3 built-in defaults
leave background colour, border and box-shadow neutral, so no further declaration is
needed. In `tests/test_gtk_theme.py`, add two `TestGtkTheme` tests using the cases'
`assert_rule` helper: `test_overshoot_glows_cleared` (asserts each of the four direction
selectors maps to a rule declaring `background-image: none`) and
`test_overshoot_backdrop_glows_cleared` (asserts the same for the four `:backdrop`
selectors). The new rules sit beside the landed scrollbar adaptations, so the existing
scrollbar, thumb-minimum and overlay assertions pass untouched. In `docs/invariants.md`,
append one row under `## gtk`: no collected screenshot shows a GTK over-scroll glow; the
eight-arm inventory (including the four `:backdrop` versions and the absence of any
undershoot arm) comes from the stock `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`
resource in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, extracted with `gresource`, and the
no-undershoot runtime probe ran headless over broadway on 2026-10-30; the clearance values
are plain `none` declarations, not measured pixels; the named theme's rules replace the
stock arms rather than override them; and the declaration checks do not establish rendered
pixels.

**Acceptance criteria.** All eight stock overshoot arms listed above are matched by
same-selector rules in the GTK 3 sheet declaring exactly `background-image: none;`, so a
rendered scrolled window keeps its field flush to the frame with no glow at any edge in
normal or backdrop state; deleting an arm selector, adding an undeclared property, or
widening the group to any unsupported selector fails one of the two new tests, and the new
sheet gains no undershoot rule (GTK 3 paints none). The existing scrollbar, trough and
overlay assertions pass unchanged. Scope is the three named files; the GTK 4 scroll-edge
plan, the scrollbar-corner junction and overlay-scrollbar geometry are outside this plan.
No new palette value, artwork or dependency. `make check` passes.

## Done

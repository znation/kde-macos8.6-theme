# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
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
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Platinum GTK 4 scroll bars: give the GTK 4 scroll bar the reference's 16px breadth (planned 2026-10-24 by the plan role; independent of the waiting GTK menu-bar plan)

**Goal.** The GTK 4 sheet is standalone: it loads no stock rules. Its `scrollbar > range > trough` rule (1px black border, no padding) and `scrollbar > range > trough > slider` rule (1px black border, `margin: 0`) set no minimum size. GTK 4 also has no stepper buttons, so nothing else gives the bar any breadth. Measured live with PyGObject (`Gtk.Scrollbar().measure(...)` under `GTK_THEME=org.macos8.desktop` with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`), a GTK 4 scroll bar is 4px across and 4px long in both orientations. That is only the four border pixels, so the thumb is a sliver. The GTK 3 bar measures 16px across, and stock Adwaita GTK 4 measures 14px. The reference installer CD window (`setup_emaculation.png`) shows a 16px horizontal bar: black rules at y=462 and y=477 around a flat `#EEEEEE` band, which `tests/test_desktoptheme_scrollbar.py::TestScrollbarReference` already samples. The fix is to give the GTK 4 slider a 12px minimum in both axes: 16px = 1px trough border + 1px slider border + 12px + 1px slider border + 1px trough border. Measured live with that rule added through a display CSS provider, the bar is 16px across in both orientations.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: in `scrollbar > range > trough > slider`, add `min-width: 12px;` and `min-height: 12px;`. The equal minimum length makes the smallest thumb square. Change no other rule.
- Out of scope: overlay-scrolling behaviour (`.overlay-indicator`/`.hovering`, and the `gtk-overlay-scrolling` setting), GTK 3 (already 16px), the thumb's grip, and `:disabled`.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the two declarations. Add one sentence to the header comment: the scroll-bar thumb's 12px minimum fills the reference's 16px bar inside the trough's and thumb's 1px borders, because GTK 4 has no steppers to size the bar.
- `tests/test_gtk4_theme.py`:
  - Extend `TestGtk4Theme.test_scrollbar`'s slider expectation with `"min-width": "12px"` and `"min-height": "12px"`.
  - Add `TestScrollbarBreadthReference(ReferenceScreenshotMixin, unittest.TestCase)` with `REFERENCE = SETUP_REFERENCE` and `MAX_ROWS = SETUP_MAX_ROWS`. Import these from `support.desktoptheme_paths` and `support.reference_image`, as `tests/test_gtk_theme.py::TestScrollbarStepperReference` does.
  - Its test asserts that pixels (200, 462) and (200, 477) are `BLACK` and that every row in between at x=200 is `TROUGH`. It derives `band = 477 - 462 + 1` and asserts `band == 16`.
  - It then parses `CSS` with `parse_css` and asserts the slider's `min-width` and `min-height` both equal `f"{band - 4}px"`. The 4 is the trough's and slider's 1px borders, so the test should also assert that both rules' `border` is `1px solid #000000` (spelled through `BLACK`).
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: the GTK 4 sheet gives the scroll-bar thumb a 12px minimum in both axes, so a GTK 4 scroll bar is the reference's 16px across. Tests: `tests/test_gtk4_theme.py::TestGtk4Theme::test_scrollbar` and `tests/test_gtk4_theme.py::TestScrollbarBreadthReference`. Provenance: none (the 16px is re-derived from `setup_emaculation.png`).

**Acceptance criteria.**
- The GTK 4 sheet's `scrollbar > range > trough > slider` carries `min-width: 12px` and `min-height: 12px`, and no other rule changes.
- Removing either declaration, or changing it to a value other than the reference band minus the two 1px borders, fails `TestScrollbarBreadthReference`. Removing either one also fails `test_scrollbar`.
- The sheet's hex-literal allow-list tests still pass, since no colour is added. The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

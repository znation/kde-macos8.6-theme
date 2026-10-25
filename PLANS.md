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

### Platinum GTK entry progress: draw an entry's progress fraction as a 2px selection-lavender strip in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover check/radio plan)

**Goal.** Both GTK sheets are standalone (no `@import` of Adwaita), and neither names an entry's progress node, so `gtk_entry_set_progress_fraction()` / `set_progress_pulse_step()` draw nothing. Download fields, location bars and similar entries show no progress at all. Adwaita draws it as a 2px blue underline: GTK 3 `entry progress`, GTK 4 `entry > progress > trough > progress`. Neither sheet has any rule that matches those nodes: `progressbar progress` and `progressbar > trough > progress` need a `progressbar` ancestor.

I measured this live under `GTK_THEME=org.macos8.desktop`:
- GTK 3, `Gtk.StyleContext` on the `Gtk.WidgetPath` `window > entry > progress`: background `rgba(0,0,0,0)`, `min-height` 0, border 0, margin 0. The node has no height and no paint.
- GTK 4, rendering a `Gtk.WidgetPaintable` of a 120px `Gtk.Entry` with `set_progress_fraction(0.5)` (texture 150x19): the rows above the bottom border stay `#FFFFFF` across the field.
- With the candidate GTK 4 rules below appended to a copy of the sheet, a `#CCCCFF` strip covers about the left half of the field, just above the black bottom border. Without `margin-bottom: 1px` it spills into the border row.

**Design (decided; do not widen).**
- `tests/support/gtk_theme_spec.py`: add `ENTRY_PROGRESS = {**PROGRESSBAR_PROGRESS, "min-height": "2px"}` beside `PROGRESSBAR_PROGRESS`. Comment: an entry's progress reuses the progress-bar selection fill as a 2px strip, Adwaita's stock thickness.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: directly after the `progressbar progress:disabled` rule, add `entry progress` with `background-color: #CCCCFF; background-image: none; border: 0; border-radius: 0; box-shadow: none; margin: 0; min-height: 2px;`.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: directly after `progressbar > trough > progress:disabled`, add three rules:
  - `entry > progress { margin-bottom: 1px; }`
  - `entry > progress > trough { min-height: 2px; }`
  - `entry > progress > trough > progress` with the same seven declarations as the GTK 3 rule.
- In each sheet's header comment, extend the sentence about the level bar reusing the progress-bar trough and selection fill: an entry's progress fraction is a 2px strip of the same selection fill. The 2px thickness is Adwaita's stock value, because no reference screenshot shows an entry progress, and the node names are GTK-required.
- Out of scope:
  - Spin-button progress (`spinbutton progress`).
  - A `:disabled` or `:backdrop` variant.
  - Any change to the progress bar or level bar rules.
- No new asset or colour is added (`#CCCCFF` is already in both sheets), so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README counts do not change.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the rules and the header sentence.
- `tests/support/gtk_theme_spec.py`: `ENTRY_PROGRESS`.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_entry_progress`, which calls `self.assert_rule("entry progress", ENTRY_PROGRESS)`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_entry_progress`, which asserts three things:
  - `self.assert_rule("entry > progress > trough > progress", ENTRY_PROGRESS)`
  - `{"min-height": "2px"}` on `entry > progress > trough`
  - `{"margin-bottom": "1px"}` on `entry > progress`
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 and GTK 4 sheets draw an entry's progress fraction as a 2px strip of the `#CCCCFF` selection fill.
  - Tests: both `test_entry_progress` tests.
  - Provenance: no reference screenshot shows an entry progress. The fill reuses the reference-grounded progress-bar selection. The 2px thickness and the node names come from the toolkits' stock sheets.

**Acceptance criteria.**
- Removing any of the four new rules, or changing any declaration in them, fails the matching `test_entry_progress`.
- A live GTK 3 `Gtk.StyleContext` probe of `window > entry > progress` reports background `rgb(204,204,255)` and `min-height` 2.
- A live GTK 4 render of a `Gtk.Entry` with `set_progress_fraction(0.5)` shows `#CCCCFF` on the strip at a quarter of the field width and `#FFFFFF` at three quarters. Its bottom border row matches the same entry without progress.
- `test_only_palette_hex_literals`, `test_progressbar`, `test_levelbar` and the rest of `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py` still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

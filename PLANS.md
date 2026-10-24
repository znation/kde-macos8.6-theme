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

### Platinum GTK separators: etch standalone horizontal and vertical separators like the reference's rule (planned 2026-10-24 by the plan role; independent of the waiting GTK text-selection plan)

**Goal.** Both opt-in GTK sheets are standalone and etch only menu separators (`menu separator, .menu separator` in GTK 3, `popover separator, popover.background separator` in GTK 4). A `GtkSeparator` anywhere else, such as a dialog's divider, a toolbar's or a settings pane's, matches no rule, so GTK draws nothing. Stock GTK's own `separator` rule is in sheets we never load. Mac OS 8.6 draws a separator as an etched pair, a 1px `#888888` line beside a 1px `#FFFFFF` line. `tests/test_desktoptheme_line.py::TestLineReference` re-derives that pair from the reference in both orientations: `test_horizontal_rule_matches_reference` has dark above light, and `test_vertical_rule_matches_reference` has dark left of light. Paint each orientable `GtkSeparator` with that pair. No new colours are needed: `ETCH_DARK` and `WHITE` are already pinned in `tests/support/gtk_theme_spec.py`.

**Selector scoping (decided; do not widen).** Use `separator.horizontal` and `separator.vertical`, not a bare `separator`. GTK puts the orientation class only on orientable `GtkSeparator` widgets. That keeps the rule off the unclassed nodes that share the `separator` name: paned handles (`paned > separator`), GTK 3's `GtkSeparatorMenuItem` (already etched by the menu rule) and tree-view row separators. GTK 4's popover menu separators are horizontal `GtkSeparator` widgets, so `separator.horizontal` (specificity 0,1,1) outranks `popover separator` (0,0,2) there. For that reason the horizontal rule repeats the menu rule's declarations exactly and **declares no `margin`**, which keeps the menu's `margin: 2px 0` in force. Stock Adwaita hides GTK 3's headerbar title-button separator (`headerbar separator.titlebutton { opacity: 0; }`), and our new vertical etch would otherwise make it visible. So the GTK 3 sheet adds that hide rule too: `headerbar separator.titlebutton` at (0,1,2) outranks `separator.vertical`. GTK 4's `windowcontrols` has no such separator.

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `MENU_SEPARATOR` add `SEPARATOR_HORIZONTAL = {"background-color": ETCH_DARK, "border": "0", "border-bottom": f"1px solid {WHITE}", "min-height": "1px", "padding": "0"}` and `SEPARATOR_VERTICAL = {"background-color": ETCH_DARK, "border": "0", "border-right": f"1px solid {WHITE}", "min-width": "1px", "padding": "0"}`, with a comment that they are the reference's etched rule from `widgets/line.svg`. Add `GtkSheetRuleCases.test_separator`, a shared case that both suites inherit because the two sheets spell these selectors the same way. It asserts both specs on `separator.horizontal` and `separator.vertical` and runs `assertNotIn("margin", ...)` on each rule. Mention the separator in the class docstring.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `menu separator, .menu separator` rule add `separator.horizontal { background-color: #888888; border: 0; border-bottom: 1px solid #FFFFFF; min-height: 1px; padding: 0; }`, `separator.vertical { background-color: #888888; border: 0; border-right: 1px solid #FFFFFF; min-width: 1px; padding: 0; }` and `headerbar separator.titlebutton, .titlebar separator.titlebutton { opacity: 0; }`. In the header comment, say that the standalone separators reuse the reference-grounded etched pair in both orientations and that the orientation classes are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `popover separator, popover.background separator` rule add the same two orientation rules (no title-button rule), plus the same header-comment sentence.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_titlebutton_separator_hidden`, which asserts `{"opacity": "0"}` on both title-button selectors.
- `docs/invariants.md`: add one `## gtk` row after the newest per-feature row. It reads "Both GTK sheets etch each horizontal and vertical `GtkSeparator` with a 1px `#888888` line and a 1px `#FFFFFF` line on its bottom or right, without overriding the menu separator's margin, and GTK 3 hides the headerbar title-button separator". It is tested by `test_separator` in both suites and `test_titlebutton_separator_hidden`. Its provenance exception: the etched pair is re-derived from the reference by `TestLineReference`, no reference screenshot shows a GTK widget, and the orientation classes and the title-button hide are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry `separator.horizontal` and `separator.vertical` with exactly the declarations above, and neither rule sets `margin`. `test_separator` runs in both `TestGtkTheme` and `TestGtk4Theme`, and removing any declaration, or adding a `margin`, fails it.
- The existing `test_menu_separator` cases still pass unchanged in both suites.
- The GTK 3 sheet hides `headerbar separator.titlebutton` and `.titlebar separator.titlebutton` with `opacity: 0`, which `test_titlebutton_separator_hidden` pins.
- `test_only_palette_hex_literals` passes in both suites with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

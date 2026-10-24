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

### Platinum GTK paned handles: etch the `paned > separator` split handle like the reference rule (planned 2026-10-24 by the plan role; independent of the waiting GTK level-bar plan)

**Goal.** A `GtkPaned`'s draggable split handle is a `separator` node with no orientation class (`paned > separator`, `.wide` when the paned's `wide-handle` is set). The standalone separator rules (`separator.horizontal`, `separator.vertical`) skip it on purpose: see the done separator plan's "Selector scoping" in PLANS-DONE.md. No other rule in either sheet names it either (`grep -n paned theme/gtk` finds nothing). Stock GTK sizes and paints this handle only in its own sheets, which we never load. GTK 3 Adwaita `gtk-contained.css` and GTK 4 `Default-light.css` both have `paned > separator { min-width: 1px; min-height: 1px; -gtk-icon-source: none; … background-image: image(#cdc7c2); }`. So in our theme the split between, say, a file manager's sidebar and its view most likely has zero size and draws nothing (from reading the sheets; not checked in a running app). Etch it with the same reference-grounded `#888888`/`#FFFFFF` pair the standalone separators use (`ETCH_DARK`, re-derived by `tests/test_desktoptheme_line.py::TestLineReference`). No new colour or spec value is introduced.

**Design (decided; do not widen).**
- A horizontal paned (`paned.horizontal`, side-by-side children) has a vertical handle, so it gets `SEPARATOR_VERTICAL` from `tests/support/gtk_theme_spec.py`: `background-color: #888888; border: 0; border-right: 1px solid #FFFFFF; min-width: 1px; padding: 0`. A vertical paned (`paned.vertical`) gets `SEPARATOR_HORIZONTAL` (`border-bottom` and `min-height` instead). Each rule also sets `-gtk-icon-source: none`, as stock does, so GTK 3's builtin pane-handle image never draws, and `margin: 0`.
- Both sheets use the child selectors `paned.horizontal > separator` and `paned.vertical > separator`. That is stock's spelling in both GTK 3 and GTK 4, because the handle is always a direct child. The rules' specificity is (0,1,2), and they cannot match a classed `GtkSeparator`, since that is never a paned's direct `separator` child.
- `.wide` handles, `:selected`, `:backdrop` and `:dir()` get no rule. Stock's negative-margin grab-area extension (`margin: 0 -8px 0 0; padding: 0 8px 0 0`) is not copied: it would move our `border-right` 8px away from the dark line. All of these are out of scope.

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `SEPARATOR_VERTICAL`, add `PANED_HANDLE_HORIZONTAL = {**SEPARATOR_VERTICAL, "-gtk-icon-source": "none", "margin": "0"}` and `PANED_HANDLE_VERTICAL = {**SEPARATOR_HORIZONTAL, "-gtk-icon-source": "none", "margin": "0"}`. Give them a comment saying a horizontal paned's handle is a vertical rule and that both reuse the reference etch. After `assert_separators`, add `GtkSheetRuleCases.assert_paned_handles(self)`. It takes no selectors, because both sheets spell them alike. It asserts `PANED_HANDLE_HORIZONTAL` on `paned.horizontal > separator` and `PANED_HANDLE_VERTICAL` on `paned.vertical > separator`. Add "paned-handle" to the module docstring's list of named assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: after each sheet's `separator.vertical` rule, add the two rules with exactly those declarations. Extend the header comment's "The standalone separators reuse …" sentence to say that the paned split handles reuse the same etch, and that the `paned` orientation classes are GTK-required.
- `tests/test_gtk_theme.py` (`TestGtkTheme`) and `tests/test_gtk4_theme.py` (`TestGtk4Theme`): add `test_paned_handle` after `test_separator`. It calls `self.assert_paned_handles()`.
- `docs/invariants.md`: add one `## gtk` row as the last row of the section. It reads "Both GTK sheets etch a `GtkPaned` split handle with a 1px `#888888` line and a 1px `#FFFFFF` line on its right (side-by-side panes) or bottom (stacked panes), with no builtin handle image". It is tested by `tests/test_gtk_theme.py::TestGtkTheme::test_paned_handle` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_paned_handle`. Its exception: the etched pair is re-derived from the reference by `tests/test_desktoptheme_line.py::TestLineReference`, no reference screenshot shows a split pane, and the `paned` node and orientation classes are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry `paned.horizontal > separator` and `paned.vertical > separator` with the declarations above. `test_paned_handle` runs in `TestGtkTheme` and `TestGtk4Theme`. Dropping any asserted declaration, or swapping the two orientations' specs, fails it.
- `test_separator` and `test_titlebutton_separator_hidden` still pass unchanged, and `test_only_palette_hex_literals` passes with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

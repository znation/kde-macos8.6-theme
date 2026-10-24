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

### Platinum GTK level bars: paint `levelbar` as the Platinum progress bar's trough and fill (planned 2026-10-24 by the plan role; independent of the waiting GTK separator plan)

**Goal.** Neither standalone GTK sheet has a `levelbar` rule (`grep -n levelbar theme/gtk` finds nothing). Stock GTK sizes and paints a `GtkLevelBar`'s blocks only in its own Adwaita/Default sheets, which we never load: GTK 3 `levelbar.horizontal block { min-height: 1px; }` plus `levelbar trough`/`levelbar block.*` colours, and GTK 4 `levelbar.horizontal trough > block { min-height: 9px; }` plus `levelbar > trough > block.*`. So a level bar in our theme, such as a password-strength meter or a disk-usage gauge, has no styled trough, and its zero-height blocks most likely draw nothing (from reading the sheets; not checked in a running app). Mac OS 8.6 has no separate level meter. Its gauge is the progress bar, which both sheets already paint from the reference-grounded spec pinned in `tests/support/gtk_theme_spec.py` (`PROGRESSBAR_TROUGH`, `PROGRESSBAR_PROGRESS`, which `test_progressbar` pins in both suites). Paint the level bar with that same trough and fill. No new colour or spec value is introduced.

**Design (decided; do not widen).**
- Nodes: in both GTK 3 and 4 a level bar is `levelbar[.horizontal|.vertical][.discrete] > trough > block`, where each filled block carries `.filled` (plus the `low`/`high`/`full` offset class) and each unfilled block carries `.empty`. Style `.filled` and `.empty` only. Platinum has one fill colour, so the offset classes get no rule.
- The trough is `PROGRESSBAR_TROUGH` without its `min-height`/`min-width`, plus `padding: 0`. The blocks set the size instead: `min-height: 10px` on horizontal blocks and `min-width: 10px` on vertical blocks, so the content box matches the progress trough's 10px.
- A filled block is `PROGRESSBAR_PROGRESS` (flat `#CCCCFF`, no border, bevel or margin). A disabled filled block is `#999999`, like `progressbar progress:disabled`. An empty block is `SCALE_EMPTY_FILL` (transparent, so the `#EEEEEE` trough shows).
- Discrete mode gets no rule: its blocks abut like one continuous progress fill. Out of scope.
- Spell selectors the way each sheet already spells the progress bar: GTK 3 uses descendants (`levelbar trough`, `levelbar block.filled`, `levelbar block.empty`, `levelbar block.filled:disabled`, `levelbar.horizontal block`, `levelbar.vertical block`). GTK 4 uses children (`levelbar > trough`, `levelbar > trough > block.filled`, `levelbar > trough > block.empty`, `levelbar > trough > block.filled:disabled`, `levelbar.horizontal > trough > block`, `levelbar.vertical > trough > block`).

**Approach.**
- `tests/support/gtk_theme_spec.py`: after `SCALE_EMPTY_FILL` add `LEVELBAR_TROUGH`, built from `PROGRESSBAR_TROUGH` minus `min-height`/`min-width` plus `"padding": "0"`, with a comment saying it reuses the progress trough. Add `GtkSheetRuleCases.assert_levelbar(self, trough, filled, empty, disabled, horizontal, vertical)` beside `assert_progressbar`. It asserts `LEVELBAR_TROUGH` on *trough* and `assertNotIn` for `min-height` and `min-width` there; `PROGRESSBAR_PROGRESS` on *filled*; `SCALE_EMPTY_FILL` on *empty*; `{"background-color": GREY}` on *disabled*; `{"min-height": "10px"}` on *horizontal*; and `{"min-width": "10px"}` on *vertical*. Add "level-bar" to the module docstring's list of named assertions.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: after each sheet's `progressbar … progress:disabled` rule, add the six rules above with exactly those declarations. Add one header-comment sentence: the level bar reuses the reference-grounded progress-bar trough and selection fill, and its node and class names are GTK-required.
- `tests/test_gtk_theme.py` (`TestGtkTheme`) and `tests/test_gtk4_theme.py` (`TestGtk4Theme`): add `test_levelbar` after `test_progressbar`, calling `assert_levelbar` with that sheet's selectors.
- `docs/invariants.md`: add one `## gtk` row after the text-selection row. It reads "Both GTK sheets paint a level bar as the Platinum progress bar: the `#EEEEEE` black-bordered inset trough with no padding, flat `#CCCCFF` filled blocks (`#999999` when disabled), transparent empty blocks and a 10px block cross-size in each orientation". It is tested by `test_levelbar` in both suites. Its exception: the trough and fill reuse the reference-grounded progress-bar spec, no reference screenshot shows a level meter, and the node and class names are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the six level-bar rules with the declarations above. `test_levelbar` runs in `TestGtkTheme` and `TestGtk4Theme`. Dropping any asserted declaration, or adding `min-height` to the trough, fails it.
- `test_progressbar` and `test_scale` still pass unchanged in both suites, and `test_only_palette_hex_literals` passes with its expected set unchanged.
- The new invariant row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

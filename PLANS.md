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
(startup splash, desktop layout, defaults); the desktop theme (twenty-six widget SVGs under
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
open and closed hands, and the drag-and-drop/forbidden aliases, not traced from Apple's
artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; help, progress, pencil, `zoom-in` and `zoom-out` still come from the fallback
cursor theme; **system sounds** are out
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

### Platinum cursor set, part 4: ship the help, progress, pencil and zoom pointers (planned 2026-10-23 by the plan role; completes the cursor set after the landed parts 1-3)

**Goal.** The icon theme's `cursors/` covers fourteen pointers; README records that `help`,
`progress`, `pencil`, `zoom-in` and `zoom-out` still come from the fallback cursor theme, so the
busy, help, drawing and zoom pointer roles change shape when the Platinum theme is selected. Add
the five remaining pointers and their aliases: `help` (the landed arrow plus a question mark),
`progress` (the arrow plus a small hourglass), `pencil` (a diagonal pencil), and `zoom-in` /
`zoom-out` (a magnifier with a plus or minus). No reference screenshot shows a pointer, so the art
stays our own `#000000`-face/`#FFFFFF`-outline drawing. The canonical names are X/KDE-required and
taken from the installed Breeze set (`/usr/share/icons/breeze_cursors/cursors`): `help`,
`left_ptr_help`, `question_arrow` and `whats_this` are one byte group there; `progress`,
`half-busy` and `left_ptr_watch` are another; `pencil`, `zoom-in` and `zoom-out` have no aliases
there (checked with `md5sum` over that directory).

**Approach.**
- `tools/make_cursors.py`: add five 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and append them to `CURSORS`; `cursor_bytes`, `NOMINAL_SIZES` and `main`
need no change.
  - `HELP_HOTSPOT = (1, 1)`; `HELP_GRID`: `ARROW_GRID` with a question mark stamped in the free
    right-hand area -- a white plate at columns 9-14, rows 2-8 carrying a black top bar
    `(10,3)-(13,3)`, a right stem `(13,4)-(13,5)`, a curve at `(12,5)` and a black dot `(12,7)`,
    with white at `(12,6)` separating the hook from the dot.
  - `PROGRESS_HOTSPOT = (1, 1)`; `PROGRESS_GRID`: `ARROW_GRID` with a white plate at columns
    9-14, rows 8-14 carrying a black hourglass -- a top bar `(10,9)-(13,9)`, a waist `(12,11)`
    and a bottom bar `(10,13)-(13,13)`, with white rows at 8 and 14.
  - `PENCIL_HOTSPOT = (2, 14)`; `PENCIL_GRID`: a two-pixel black shaft on the anti-diagonal
    `x+y = 15`/`16` from the writing tip `(2,14)` to the eraser `(13,2)`, each black edge bounded
    by one white cell; black at `(2,14)`, `(8,7)` and `(12,3)`, white at `(1,14)` and `(13,1)`.
  - `ZOOM_IN_HOTSPOT = (7, 7)` and `ZOOM_OUT_HOTSPOT = (7, 7)`; the two grids share a
    white-outlined black lens ring centred on `(7,7)` (black at `(7,3)`, `(3,7)`, `(11,7)`,
    `(7,11)` and white at `(7,2)`), a black handle along `(11,11)-(13,13)` (black at `(13,13)`),
    and a black plus in the lens at `(7,5)`, `(5,7)`, `(9,7)`, `(7,9)` and `(7,7)`; `ZOOM_OUT_GRID`
    keeps only the horizontal bar of the plus, leaving `(7,5)` and `(7,9)` transparent.
  - Append `("help", HELP_GRID, HELP_HOTSPOT, ("left_ptr_help", "question_arrow", "whats_this"))`,
    `("progress", PROGRESS_GRID, PROGRESS_HOTSPOT, ("half-busy", "left_ptr_watch"))`,
    `("pencil", PENCIL_GRID, PENCIL_HOTSPOT, ())`,
    `("zoom-in", ZOOM_IN_GRID, ZOOM_IN_HOTSPOT, ())` and
    `("zoom-out", ZOOM_OUT_GRID, ZOOM_OUT_HOTSPOT, ())` to `CURSORS`.
  - Update the module docstring: the package ships nineteen canonical cursors, not fourteen, and
    list the new names and their aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with the five names and `ALIASES` with their
  alias tuples (empty for `pencil`, `zoom-in` and `zoom-out`). Add the five names to `HOTSPOTS` --
  `help`/`progress`: `(1,1)` at 16, `(2,2)` at 24, `(2,2)` at 32; `pencil`: `(2,14)`, `(3,21)`,
  `(4,28)`; `zoom-in`/`zoom-out`: `(7,7)`, `(11,11)`, `(14,14)` -- and to `PINNED_PIXELS` (face
  `(1,1)` / outline `(0,0)` for `help` and `progress`; face `(2,14)` / outline `(1,14)` for
  `pencil`; face `(7,7)` / outline `(7,2)` for `zoom-in` and `zoom-out`). Add `pencil`, `zoom-in`
  and `zoom-out` to `TRANSPARENT_CORNER_CURSORS`; `help` and `progress` keep the arrow's white
  top-left corner, so they stay out. The existing `TestCursorSet` loops then cover the new files,
  aliases, hotspots, face/outline pixels and determinism. Add focused tests:
  - `test_help_pins_the_arrow_and_question_mark`: at 16px black at `(1,1)`, `(10,3)`, `(13,5)` and
    `(12,7)`; white at `(0,0)` and `(12,6)`.
  - `test_progress_pins_the_arrow_and_hourglass`: at 16px black at `(1,1)`, `(10,9)`, `(12,11)`
    and `(10,13)`; white at `(12,8)` and `(12,14)`.
  - `test_pencil_draws_a_diagonal_shaft_to_its_writing_tip`: at 16px black at `(2,14)`, `(8,7)`
    and `(12,3)`; white at `(1,14)` and `(13,1)`; all four corners transparent.
  - `test_zoom_in_and_out_differ_only_at_the_plus_arms`: at 16px both have black at `(7,3)`,
    `(3,7)`, `(7,11)` and the handle tip `(13,13)`, and white at `(7,2)`; `zoom-in` is black at
    `(7,5)`, `(5,7)`, `(9,7)` and `(7,9)`, while `zoom-out` is black only at `(5,7)` and `(9,7)`
    and transparent at `(7,5)` and `(7,9)`.
  - `test_help_and_progress_alias_names_reuse_their_canonical`: `left_ptr_help`, `question_arrow`
    and `whats_this` are byte-identical to `help`; `half-busy` and `left_ptr_watch` to `progress`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the ten new X names (`help`, `left_ptr_help`, `question_arrow`,
  `whats_this`, `progress`, `half-busy`, `left_ptr_watch`, `pencil`, `zoom-in`, `zoom-out`) to
  `SHIPPED_CURSORS`, so the shipped-file registry and the shared install-lifecycle list cover them.
- `README.md`: name the five new pointers and their aliases in the cursor sentence, and replace the
  fallback sentence with "Xcursor roles the theme does not name still come from the fallback cursor
  theme".
- `docs/invariants.md`: extend the `## icons` cursor row to name all nineteen canonical files and
  every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`;
  extend the provenance exception: no reference screenshot shows the pointer, the help, progress
  and zoom names are X/KDE-required and taken from the installed Breeze set, and the help/progress
  alias groups follow Breeze's byte groups while `pencil`, `zoom-in` and `zoom-out` have no alias.
- `PLANS.md`: in the scope-drift paragraph, add the help, progress, pencil and zoom pointers to the
  shipped cursor clause, and say Xcursor roles the theme does not name still fall back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(five canonical names and five alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the five new canonical files and the five aliases; running
  it twice leaves every committed cursor byte-identical, and each new canonical parses to three
  chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel and white outline
  pixel, and the pencil and zoom files keep transparent corners.
- The focused tests pin the arrow-plus-question-mark, the arrow-plus-hourglass, the diagonal
  pencil and the plus/minus magnifiers; deleting a grid, dropping a size, moving a hotspot,
  drawing `zoom-out` as a copy of `zoom-in`, or losing the pencil's white outline fails a test.
- `left_ptr_help`, `question_arrow`, `whats_this`, `half-busy` and `left_ptr_watch` are
  byte-identical to their canonical files; the generator writes exactly the ten new names into a
  temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all ten new
  names; README and `docs/invariants.md` name them; `tests/invariants.py` accepts the updated
  `## icons` row; the scope-drift clause no longer lists help, progress, pencil or zoom as
  fallback.
- `make check` is green.

## Done

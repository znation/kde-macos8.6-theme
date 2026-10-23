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
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
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
queued it anyway as the theme's own Platinum-style art (a black-face, white-outline arrow not
traced from Apple's artwork), it has landed inside the icon theme package with its provenance
exception recorded in `docs/invariants.md`, and `make apply-cursor`/`make remove-cursor`
link it into the Xcursor path and select it; **system sounds** are out
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

### Platinum cursor set: ship the text, hand, busy and move pointers (planned 2026-10-23 by the plan role; follows the landed arrow artifact)

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, so after
`make apply-cursor` selects the theme every pointer except the arrow still comes from the user's
fallback theme: typing in a field, hovering a link, waiting for a task and dragging a window all
draw the fallback cursor. Add the four other pointer roles a desktop uses constantly -- the text
I-beam (`xterm`), the pointing hand (`hand2`), the busy hourglass (`watch`) and the move cross
(`fleur`) -- with the X-name aliases applications use, generated by the same tool. All art is our
own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline, not traced from
Apple's artwork; no reference screenshot shows a pointer, so the existing `## icons` provenance
exception covers the new names. This entry does not change the arrow's bytes; the landed
"Platinum cursor selection" entry's `make apply-cursor` selects the set. Resize, diagonal, drag
and not-allowed pointers stay on the fallback theme and are recorded as such; a later entry can
complete them.

**Approach.**
- `tools/make_cursors.py`: replace the one-glyph constants' use with a fixed `CURSORS` table whose
  entries are `(canonical_name, rows, hotspot, aliases)`, in this order: `left_ptr` (the existing
  `ARROW_GRID`/`HOTSPOT`, aliases `arrow`, `default`, `top_left_arrow`), `xterm` (I-beam, aliases
  `text`, `ibeam`), `hand2` (pointing hand, aliases `hand1`, `pointer`, `pointing_hand`), `watch`
  (hourglass, alias `wait`) and `fleur` (move cross, aliases `move`, `all-scroll`, `size_all`).
  Keep `ARROW_GRID`, `HOTSPOT`, `NOMINAL_SIZES` and `cursor_bytes(rows=ARROW_GRID, sizes=
  NOMINAL_SIZES, hotspot=HOTSPOT)` so the landed artifact and its tests stay valid. Add a
  `*_GRID` and `*_HOTSPOT` constant per glyph and generalize `_checked_rows` to take the glyph
  name so a bad cell reports `"xterm grid cell (x, y) ..."` (the arrow keeps its `"arrow grid"`
  messages). `main` walks `CURSORS` in order and writes each canonical file then its aliases with
  the same containment guard, atomic write and stop-on-first-failure behavior.
- The new 16x16 grids use the existing `PIXELS` map (`#` black face, `.` white outline, space
  transparent) and keep the arrow's 1px black face fully inside a 1px white outline, transparent
  elsewhere: `xterm` is a vertical I-beam with top and bottom serifs, hotspot at its centre;
  `hand2` is a pointing hand with the index finger up and the thumb to the right, hotspot at the
  fingertip; `watch` is a top and bottom triangle joined at a narrow waist, hotspot at the
  centre; `fleur` is a four-way arrow cross, hotspot at the centre. Each grid must differ from
  `ARROW_GRID` so a copy-paste fails the set test.
- `tests/test_cursors_theme.py`: keep `TestCursorArtifact` for the arrow and add `TestCursorSet`
  covering every canonical name and alias: each file parses to 16/24/32 chunks, its hotspot is
  the glyph's pinned scaled hotspot, the four corners are transparent, the face is black and the
  outline white at pinned pixels, and every alias is byte-identical to its canonical file. Extend
  the determinism and `main` error cases to all files, including a corrupted grid, dropped size
  and moved hotspot per new glyph; keep the failed-write case failing on `arrow` so the write
  order is pinned. `HOTSPOTS` becomes a per-glyph mapping.
- `README.md`: the cursor sentence in the installed-theme paragraph names the arrow plus the
  `xterm`, `hand2`, `watch` and `fleur` pointers and their aliases, and says resize/drag pointers
  still come from the fallback theme. Keep the landed `make apply-cursor`/`make remove-cursor`
  selection sentences as they are.
- `docs/invariants.md`: extend the existing `## icons` cursor row to name every canonical file and
  alias and cite both `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`; the
  provenance exception keeps "no reference screenshot shows the pointer; our own Platinum-style
  art on the pinned face and outline; the nominal sizes, Xcursor layout and X names are KDE/X
  required".
- `PLANS.md`: the scope-drift paragraph's artifact list names the cursor set instead of only the
  arrow; its selection sentence already names the landed `make apply-cursor`/`make remove-cursor`
  commands.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`, the new files under
`theme/icons/org.macos8.desktop/cursors/` (canonical names and aliases listed above), `README.md`,
`docs/invariants.md` and `PLANS.md` (this entry and the scope-drift artifact list). Do not edit
`tools/xcursor.py`, `tools/apply_cursor.py`, `PLANS-DONE.md`, or the arrow's committed bytes.

**Acceptance criteria.**
- `git diff --name-status` does not list `cursors/left_ptr`, `cursors/arrow`, `cursors/default` or
  `cursors/top_left_arrow`; running `python3 tools/make_cursors.py` twice leaves every committed
  cursor file byte-identical.
- Every alias is byte-identical to its canonical file, each canonical file holds three chunks at
  nominal sizes 16, 24 and 32, and each glyph's scaled hotspot is pinned at all three sizes
  (the arrow's are (1,1), (2,2) and (2,2)).
- Tests prove each new grid differs from the arrow, a corrupted grid, dropped size or moved
  hotspot changes that glyph's bytes, and an unknown cell names the glyph (`xterm grid cell ...`).
  A missing alias, a copied arrow grid, or swapping two glyphs' hotspots fails a test.
- The generator still refuses a `cursors/` symlink that escapes the repository, reports a failed
  write by path and stops, and writes nothing outside the icon theme package.
- `make check CHECK_TESTS=test_cursors_theme` passes, then `make check` is green (fixing the
  separately recorded stale `_write_atomic` test reference first if it is still open);
  `tests/invariants.py` accepts the updated `## icons` row.

## Done

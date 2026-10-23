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
exception recorded in `docs/invariants.md`, and nothing selects it yet; **system sounds** are out
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

### Platinum cursor selection: link the shipped cursor into the Xcursor user path and apply it (planned 2026-10-23 by the plan role; follows the landed cursor artifact)

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, but nothing
selects them. Xcursor searches `~/.icons`, `/usr/share/icons` and `/usr/share/pixmaps` (its
`XcursorLibraryPath()` default), not `$XDG_DATA_HOME/icons`: `plasma-apply-cursortheme --list-themes`
and `XcursorLibraryPath()` both ignore a theme copied under `$XDG_DATA_HOME/icons`, and list it when
the same theme is under `~/.icons`. This part adds an opt-in `make apply-cursor` that exposes the
installed icon theme at `$HOME/.icons/org.macos8.desktop` as a symlink and selects it with
`plasma-apply-cursortheme org.macos8.desktop`; `make remove-cursor` removes only that link. `make
install` and `make apply` stay unchanged and select no cursor.

**Approach.**
- `tools/apply_cursor.py` (new CLI, `TOOL = "apply_cursor"`, `CURSOR_THEME =
  "org.macos8.desktop"`, `SELECT_TOOL = "plasma-apply-cursortheme"`, `COMMAND_TIMEOUT = 60.0`).
  It uses `tools.argument_parsing.EscapingArgumentParser` (`--remove`), reports through
  `tools.diagnostics.report_error`/`report_failure`/`report_missing_tool`, runs the selector with
  `tools.process_group.run_logged` into a temporary log, escapes path text with
  `tools.terminal.escape_controls`, and imports `tools.repo_root.ROOT`.
- `resolve_homes(env)` returns `(home, data_home, config_home)`: `$HOME` must be absolute; data home
  is an absolute `$XDG_DATA_HOME` else `$HOME/.local/share`; config home is an absolute
  `$XDG_CONFIG_HOME` else `$HOME/.config` (only for the removal note). A missing or relative `HOME`
  exits 2 naming it.
- `installed_theme(data_home)` is `$XDG_DATA_HOME/icons/org.macos8.desktop`; it must contain a
  regular `index.theme` and a regular `cursors/left_ptr`, else exit 2 naming the path. That file is
  the icon theme's own `index.theme`, so the symlinked directory is also a valid cursor theme (the
  KDE cursor model lists it by the directory name `org.macos8.desktop`).
- Install: the target path is `$HOME/.icons/org.macos8.desktop`. A missing `~/.icons` is created; an
  existing symlink to the installed theme is success (a repeat install changes nothing); any other
  existing path (a foreign symlink, a real directory or a file) is refused with exit 2 naming it and
  is not touched; a `~/.icons` that exists but is not a directory is refused the same way. A new link
  is created with `os.symlink(str(installed_theme), str(target))`.
  Then `plasma-apply-cursortheme org.macos8.desktop` runs with the inherited environment; a missing
  tool exits 2 through `report_missing_tool`, a timeout or non-zero exit returns `report_failure`
  (status 1) with the log tail.
- Remove (`--remove`): unlink the target only when it is a symlink whose link text is the installed
  theme path (a dangling link to a since-uninstalled theme counts as ours); a real directory, a file
  or a symlink elsewhere is left alone with a note and exit 0, like `remove-gtk` leaving a foreign
  file. Do not edit `kcminputrc`; if its `[Mouse] cursorTheme` still names `org.macos8.desktop`,
  print a note naming `plasma-apply-cursortheme breeze_cursors` as the reset. Leave `~/.icons`
  itself in place.
- `Makefile`: add `apply-cursor` and `remove-cursor` to `.PHONY` and `make help`. `apply-cursor`
  refuses a non-empty `DESTDIR` (like `apply`/`apply-gtk`), then runs
  `$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme` followed by
  `$(PYTHON) tools/apply_cursor.py`, behind `require_python`/`require_python_version`.
  `remove-cursor` runs `$(PYTHON) tools/apply_cursor.py --remove` behind the same Python guards.
- `README.md`: replace the cursor paragraph's "Nothing selects it yet." with the opt-in commands,
  the `$HOME/.icons/org.macos8.desktop` symlink, the selection name, the restart note (the selector
  says a restart is needed for the new pointer to display correctly), and the removal note. Add no
  new `?=` variable.
- `docs/invariants.md`: add one row under `## icons`: the opt-in link/selection exposes the shipped
  arrow at the Xcursor path and selects it, refuses a foreign path, and removal reverses only our
  link, leaving a foreign path and `kcminputrc` untouched; pinned to
  `tests/test_apply_cursor.py::TestInstall`, `::TestRemove` and `::TestSelection`. The provenance
  exception records that no reference screenshot shows a pointer, and that the `~/.icons` path, the
  theme name and the selector are Xcursor/KDE-required values.
- `PLANS.md`'s scope-drift paragraph changes its "nothing selects it yet" phrase to name `make
  apply-cursor`/`make remove-cursor` once this lands; the historical "not planned yet" wording in
  `PLANS-DONE.md` is left alone.

**Files touched.** `tools/apply_cursor.py` (new), `tests/test_apply_cursor.py` (new), `Makefile`,
`README.md`, `docs/invariants.md` and `PLANS.md` (this entry and the scope-drift sentences). Do not
edit `PLANS-DONE.md`, the cursor generator, any `theme/` file, or the installed-theme layout.

**Acceptance criteria.**
- `tests/test_apply_cursor.py` pins: an absolute `HOME` is required (unset and relative refused by
  name); the data-home fallback; a missing installed theme, `index.theme` or `cursors/left_ptr` is
  refused by name; install creates `$HOME/.icons/org.macos8.desktop` as a symlink to the installed
  icon theme, a repeat install succeeds, and a foreign symlink, real directory or file is refused
  without being changed; the selector is invoked as `plasma-apply-cursortheme org.macos8.desktop`,
  a missing selector exits 2 naming it, and a non-zero selector exits 1 with its log tail; removal
  unlinks only our symlink (including a dangling one), leaves a foreign path and `.icons` in place,
  succeeds when repeated, and prints the `kcminputrc` note only when the selection still names
  `org.macos8.desktop`. Changing the link target, deleting the installed-theme check or dropping
  the foreign-path guard makes the matching test fail.
- The Makefile tests pin `apply-cursor`'s dry run (`INSTALL_PACKAGES=icon-theme` before
  `tools/apply_cursor.py`), its `DESTDIR` refusal, and the Python-version refusal; `make help` lists
  both targets and README names `make apply-cursor` and `make remove-cursor`.
- `make check CHECK_TESTS=test_apply_cursor` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## icons` row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

### Platinum cursor set: ship the text, hand, busy and move pointers (planned 2026-10-23 by the plan role; follows the landed arrow artifact)

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, so after
`make apply-cursor` selects the theme every pointer except the arrow still comes from the user's
fallback theme: typing in a field, hovering a link, waiting for a task and dragging a window all
draw the fallback cursor. Add the four other pointer roles a desktop uses constantly -- the text
I-beam (`xterm`), the pointing hand (`hand2`), the busy hourglass (`watch`) and the move cross
(`fleur`) -- with the X-name aliases applications use, generated by the same tool. All art is our
own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline, not traced from
Apple's artwork; no reference screenshot shows a pointer, so the existing `## icons` provenance
exception covers the new names. This entry does not change the arrow's bytes or select the theme
(that is the waiting "Platinum cursor selection" entry). Resize, diagonal, drag and not-allowed
pointers stay on the fallback theme and are recorded as such; a later entry can complete them.

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
  still come from the fallback theme. Do not mention selection here; the waiting entry owns the
  "Nothing selects it yet" sentence.
- `docs/invariants.md`: extend the existing `## icons` cursor row to name every canonical file and
  alias and cite both `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`; the
  provenance exception keeps "no reference screenshot shows the pointer; our own Platinum-style
  art on the pinned face and outline; the nominal sizes, Xcursor layout and X names are KDE/X
  required".
- `PLANS.md`: the scope-drift paragraph's artifact list names the cursor set instead of only the
  arrow; leave its "nothing selects it yet" words to the selection entry.

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

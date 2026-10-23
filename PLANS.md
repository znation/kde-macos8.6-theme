# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
the `org.macos8.desktop` Kvantum widget style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`
but not yet selected); the GTK 3 and GTK 4 Platinum stylesheets under `theme/gtk/` (not yet
installable; part 3/4 is planned below); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style art (a black-face, white-outline arrow not
traced from Apple's artwork) with its provenance exception recorded in its entry and
`docs/invariants.md`; **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them); and a **lock screen** is out of scope
unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered 2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both now have plan entries in the queue.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed; part 3/4 is queued as three entries — the opt-in install (parts 1/3 and 2/3) and,
blocked on them, the selection (part 3/3) — and part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) is not planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed but not yet selected); part 2/3 (a
Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) is queued as one entry,
the Lato body face only, because Lato is the only family the package installs. Until part
3/3 lands, KDE, Plasma and Qt applications keep the user's own font; GTK and Firefox
applications keep their own chrome regardless (the queued GTK entries cover GTK, and
Firefox chrome is part 1/2, which has landed).

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 2/3 landed")

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** The theme ships eight artifacts but no cursor, so a themed Plasma session still shows the
Breeze arrow. Mac OS 8.6 draws a black arrow with a white outline; this part builds that cursor as
a KDE/Xcursor theme artifact — `theme/icons/org.macos8.desktop/cursors/{left_ptr,arrow,default,top_left_arrow}`
(the last three byte-identical X-name copies of `left_ptr`, images at nominal sizes 16, 24 and 32
in one Xcursor file) — with a deterministic generator, and ships it inside the
`org.macos8.desktop` icon theme package, whose `make install` family already installs that whole
tree (so install and uninstall need no Makefile change) and whose directory is one of the paths the
XDG icon-spec lookup searches for `cursors/`. It touches no install or selection path: `make
uninstall` already removes the tree with its family, and the selection (`cursorTheme` in the global
terminal's `contents/defaults`) is not planned yet and is not part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows the mouse pointer, so no
reference pixel is sampled and the arrow is our own Platinum-style art drawn from a pixel grid in
the generator, not traced from Apple's artwork (the icon theme's standing rule). Its two colours
are `#000000` face and `#FFFFFF` outline, both already pinned in the colour scheme; the nominal
sizes 16/24/32, the Xcursor binary format, the file name `left_ptr` and the X-name aliases are
X/KDE-required values the reference set does not show. Record that provenance exception in the
`## icons` row of `docs/invariants.md` (the artifact ships inside the icon theme package). Xcursor
files have no image extension, so Git LFS (`.gitattributes`) is
untouched. The files ride the icon theme artifact, so README's artifact count stays at eight
(status wording untouched); part 3/3 only extends their reader-facing description in the
"Installing" section.

**Approach.**
- `tools/make_cursors.py` (new): follow `tools/make_wallpaper.py`'s direct-or-package import block,
  `require_within_repo` containment guard and `report_error` diagnostics. It holds the 16x16 arrow
  pixel grid as ASCII rows (`#` black face, `.` white outline, space transparent) with the tip at
  (1,1), scales it nearest-neighbour to 16, 24 and 32 (hotspot scaled by the same mapping), encodes
  each frame with `encode_rgba_png` and assembles each file with `write_cursor`, writing `left_ptr`
  and the three aliases as byte-identical copies (not symlinks) into the repository's
  `theme/icons/org.macos8.desktop/cursors/`. The output is deterministic, so re-running it
  rewrites identical bytes; it refuses an output directory that resolves outside the repository,
  naming the path.
- Committed artifacts: the four generated files under
  `theme/icons/org.macos8.desktop/cursors/` (small binaries, regular git blobs, no LFS filter).
- `tests/test_cursors_theme.py` (new): run the generator into a temp directory twice, asserting
  byte-identical output; parse the committed `left_ptr` with `tests/support/xcursor.py` (part 2/3)
  and pin: exactly one image chunk per nominal size in {16, 24, 32}; each chunk's PNG payload
  decodes with `decode_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its expected
  set and `TestInstall.INSTALLED_FILES` extends its registry, so both equal the package tree with
  the four cursor files added (the inherited `test_installed_files_registry_covers_the_package`
  compares that registry against `shipped_files(self.PACKAGE_DIR)`). The SVG-level assertions
  iterate the explicit `SHIPPED_ICONS` tuple, not `shipped_files`, so they need no change; the
  placeholder register stays untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add one row to the existing `## icons` section — the icon theme's
  `cursors/left_ptr` draws the black face and white outline at nominal sizes 16/24/32 with the
  hotspot at the tip, and its `arrow`, `default` and `top_left_arrow` aliases are byte-identical to
  it — pinned to `tests/test_cursors_theme.py::TestCursorArtifact`, carrying the provenance
  exception above (no screenshot shows a pointer). Do not add a `## cursors` section:
  `tests/invariants.py` accepts only `theme/` subsystem sections plus
  `EXTRA_SECTIONS = ("tooling",)`, so an unregistered section fails `make check`.

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `tools/xcursor.py` (only its module docstring's forward
reference to a `## cursors` section becomes the `## icons` row), `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). The
`Makefile`, `.gitattributes` and `tests/invariants.py` are untouched; do not edit
`PLANS-DONE.md` (this replan already annotated its part 2/3 entry).

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; each chunk's
  PNG payload decodes with `tools.png.decode_rgba`, and its width/height equal the nominal size;
  the pinned pixels and hotspots hold for all three nominal sizes (scaled accordingly); the
  aliases are byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size
  from the generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin and `TestInstall.INSTALLED_FILES` hold with the four
  cursor files (removing one, or editing the committed grid's colours, fails the matching test),
  while the SVG-level assertions still iterate only `SHIPPED_ICONS`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## icons` row; `grep -n '^## cursors' docs/invariants.md` prints nothing; `git diff
  --name-status` names only the files listed under "Files touched" (besides the backlog move) and
  none of `Makefile`, `.gitattributes`, `tests/invariants.py` or `PLANS-DONE.md`.
- The entry moves from `## Planned` under `## Done` with its Done stamp, verified on the pre-merge
  working diff: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
  `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. No acceptance criterion
  refers to `PLANS.md` or `PLANS-DONE.md` after the merge.

### Retire the `unclear-invariant` validation gap with an invariant-register ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: unclear-invariant` tag, 17 Fixed entries)

**Goal.** Seventeen Fixed entries in BUGS-FIXED.md carry `gap: unclear-invariant` — each bug
could be confirmed only after reconstructing what the code was supposed to guarantee first.
`docs/invariants.md` already has rows for the KDE INI rules, the PNG IDAT trailer, the
`INSTALL_PACKAGES` guard, the icon theme, the palette anchors and the fidelity gate, but it has
no row for `tools/url_check.py`'s RFC 3986 rules, the render session's config-search-path
isolation or the lineedit corner tiles, and nothing ties an archived record to its register row.
Retire the tag with a ledger that maps each record to the register row and the test that pins
it, and a count cap so a new `unclear-invariant` tag fails the suite until its invariant is
recorded.

**Cited entries.** BUGS-FIXED.md lines recording `gap: unclear-invariant` (17 entries): the PNG
IDAT-trailer invariant, three KDE config-reader rules, the render session's `XDG_CONFIG_DIRS`
isolation, the lineedit corner geometry, the eight `tools/url_check.py` RFC 3986 cases, and the
three older one-line records (icon-theme placeholder naming, the selection palette anchor and
the objective fidelity check).

**Approach.**
- `tests/support/validation_gaps.py`: add `UNCLEAR_INVARIANT_BASELINE = 17` and one
  `UNCLEAR_INVARIANT_REPRODUCTIONS` entry per mechanism, matching both the prose and the older
  one-line record forms. Give each entry the register row's guarantee text in addition to its
  test reference, and add an `unclear_invariant(records)` selector plus a tag-aware lookup that
  returns `None` for an unmatched record, mirroring the `no-observability` ledger without
  changing its entries.
- `tests/test_validation_gaps.py`: add `TestUnclearInvariantLedger` asserting that every
  archived `unclear-invariant` record maps to an entry; that each entry's test reference passes
  `tests/invariants.check_reference`; that each entry's guarantee text occurs in a row
  `tests/invariants.parse_rows` returns from `docs/invariants.md`; that each entry covers a
  shipped record; and that the record count does not exceed 17.
- `docs/invariants.md`: add the three missing tooling rows — `tools/url_check.py`'s RFC 3986
  well-formedness pinned to `tests/test_url_check.py`, the render session's
  `XDG_CONFIG_DIRS` isolation pinned to
  `tests/test_render_surface.py::TestFailurePaths::test_session_ignores_a_config_search_path_from_the_environment`,
  and the lineedit corner tiles pinned to
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference`
  — and extend the existing validation-gap ledger row to name both tags.
- `PLANS.md`: this entry moves under `## Done` when the work is done.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`,
`docs/invariants.md` and `PLANS.md` (this entry). Do not edit `PLANS-DONE.md` or any `theme/`
path; the invariants are already recorded, so no shipped artwork or config changes.

**Acceptance criteria.**
- `tests/test_validation_gaps.py::TestUnclearInvariantLedger` passes, and deleting a ledger
  entry, pointing one at an absent register row or a non-existent test, or adding an
  `unclear-invariant` record without an entry makes the matching assertion fail.
- `make check` is green; `tests/invariants.py` accepts the new and extended `## tooling` rows.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`.

## Done

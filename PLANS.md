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
blocked on them, the selection (part 3/3) — and part 4/4 (Firefox `userChrome.css` plus profile
preference) is not planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed but not yet selected); part 2/3 (a
Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) is queued as one entry,
the Lato body face only, because Lato is the only family the package installs. Until part
3/3 lands, KDE, Plasma and Qt applications keep the user's own font; GTK and Firefox
applications keep their own chrome regardless (the queued GTK entries cover GTK, and
Firefox is GTK series part 4/4, not planned).

### Platinum cursor theme, part 2/3: Xcursor binary writer and test-side parser (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 1/3 landed")

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** Part 1/3 added the RGBA PNG codec (`tools/png/write.py::encode_rgba_png`,
`tools/png/read.py::decode_rgba`). This part adds the Xcursor container the cursor artifact needs:
a standard-library writer that turns PNG frames into one Xcursor file, and an independent
test-side parser that reads that file back and cross-checks the writer's framing. Nothing else:
no generator, no committed cursor files, no Makefile, no README, no `theme/` change, no selection.
The generator, the shipped artifact and its registration are part 3/3 ("requires part 2/3
landed").

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a pointer, so no reference
pixel is sampled here; the Xcursor binary layout is an X/KDE-required value the reference set does
not show. Its facts: a 16-byte file header (`b"Xcur"`, header size 16, file version 0x00010000,
TOC count), one 12-byte TOC entry per chunk (type, subtype, byte offset), and the 36-byte image
chunk header (header size 36, type 0xfffd0002, subtype = nominal size, chunk version 1, width,
height, hotspot x, hotspot y, delay 0). The image payload is `width * height` little-endian
**premultiplied ARGB** words, not PNG bytes: the writer decodes each PNG frame with `decode_rgba`
and premultiplies each colour channel with `(channel * alpha + 127) // 255`, and the parser
converts the stored words back to RGBA and re-encodes them with `encode_rgba_png`. An opaque frame
(alpha 255) therefore round-trips byte for byte; a translucent frame does not, because
premultiplication loses colour precision — the tests pin the stored premultiplied word instead.
Record that provenance first here and carry it into the `## cursors` section part 3/3 adds.

**Approach.**
- `tools/xcursor.py` (new): module constants `MAGIC = b"Xcur"`, `FILE_VERSION = 0x00010000`,
  `FILE_HEADER_SIZE = 16`, `TOC_ENTRY_SIZE = 12`, `IMAGE_TYPE = 0xFFFD0002`,
  `CHUNK_VERSION = 1`, `IMAGE_HEADER_SIZE = 36` and `MAX_IMAGE_SIZE = 0x7FFF`; follow
  `tools/make_wallpaper.py`'s direct-or-package import block and use
  `tools/ints.py::is_plain_int`. `write_cursor(images)` takes one `(nominal_size, width, height,
  hotspot_x, hotspot_y, png_bytes)` record per frame; it rejects a dimension outside 1..0x7FFF, a
  hotspot outside its image, a non-integer (including a bool) numeric field, a PNG field that is
  not `bytes`/`bytearray` and a PNG whose size disagrees with `width`/`height`, each with a
  `ValueError` naming the argument; it decodes with `decode_rgba`, premultiplies, writes the file
  header, one TOC entry per image and each image chunk at its declared offset, so the same records
  always produce byte-identical output. The public surface is `write_cursor` plus those constants;
  no comment chunks.
- `tests/support/xcursor.py` (new): the test-side parser, written independently of the writer and
  importing no symbol from `tools/xcursor.py`. `read_cursor(path)` validates the file header
  (magic, header size 16, version 0x00010000, `ntoc`), reads the TOC, skips a TOC entry whose type
  is not `0xfffd0002` (tolerating, for example, a comment chunk), rejects a chunk offset or length
  outside the file, validates the 36-byte image header (type, chunk version 1, nominal size, width,
  height, hotspot), slices the ARGB payload, converts it back to RGBA and returns a `CursorFile`
  NamedTuple of `CursorImage(nominal_size, width, height, hotspot_x, hotspot_y, png)` records whose
  `png` is `encode_rgba_png(width, height, rgba)`. Errors are `ValueError` naming the path and the
  field or offset that failed.
- `tests/test_xcursor.py` (new): round-trip synthetic opaque frames at 1x1, 2x2, 3x3 and 4x4 whose
  hotspot is the bottom-right tip and whose pixels vary by position: `write_cursor` → `read_cursor`
  reproduces every field and returns the original `encode_rgba_png` bytes exactly. Pin the
  container layout by unpacking the bytes: magic, header size, version, `ntoc`, each TOC entry's
  type/subtype/offset, each chunk's 36-byte header (delay 0) and one known translucent pixel's
  premultiplied ARGB word. Two runs with the same records are byte-identical. Rejections, using
  `tests/support/rejection_assertions.py`'s `assert_rejection_names`: a truncated file header, a
  truncated image payload, a bad magic, a wrong header size, a wrong version, a corrupt `ntoc`
  whose TOC overruns the file, a hotspot outside its image, a zero dimension, a bool dimension, a
  PNG sized differently from its record and a non-`bytes` PNG, each message naming the argument or
  offset. One test builds a valid file plus a hand-appended unknown TOC entry and shows the parser
  skips it while still returning the image.
- `docs/invariants.md`: untouched. This part ships no artifact, so the `## cursors` row belongs to
  part 3/3, which pins the committed file; this part's guarantees are pinned by
  `tests/test_xcursor.py` alone.

**Files touched.** `tools/xcursor.py` (new), `tests/support/xcursor.py` (new),
`tests/test_xcursor.py` (new) and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not
edit `PLANS-DONE.md`, `Makefile`, `README.md`, `docs/invariants.md` or any `theme/` path.

**Acceptance criteria.**
- `tests/test_xcursor.py`'s round-trip case shows `write_cursor` → `read_cursor` agreeing on every
  field and on the exact PNG bytes for all four opaque synthetic sizes; two runs with the same
  records produce byte-identical files; the layout pin finds the constants above at their stated
  offsets with delay 0 and the expected premultiplied translucent word; each malformed input above
  raises `ValueError` whose message names the offending argument or offset; the hand-appended
  unknown TOC entry is skipped and the remaining image still parses.
- The test-side parser is independent of the writer:
  `grep -n 'from tools import xcursor\|from tools\.xcursor' tests/support/xcursor.py` prints no
  line.
- `make check CHECK_TESTS=test_xcursor` passes, then `make check` is green; removing a guard,
  offsetting a chunk or changing a constant makes the matching test fail.
- `git diff --name-status` names only the files listed under "Files touched" (including the
  `PLANS.md` move) and does not name `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`. No acceptance criterion refers to `PLANS.md` or `PLANS-DONE.md` after
  the merge; tumwater archives the `## Done` entry into `PLANS-DONE.md`.

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; "requires part 2/3 landed")

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -n '^### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor
artifact' PLANS.md` must print exactly one line whose number is greater than the `## Done` line's.
The final report quotes the actual output of `grep -l "Generate and ship the Xcursor arrow cursor
artifact" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`; never claim
a file the diff does not name.

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
X/KDE-required values the reference set does not show. Record that provenance exception in
`docs/invariants.md`. Xcursor files have no image extension, so Git LFS (`.gitattributes`) is
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
  decodes with `read_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its tracked
  set so the tree holds exactly with the four cursor files added; the SVG-level assertions
  (`test_each_icon_is_a_square_svg_of_its_declared_size`, the palette and pins and
  `test_the_geometry_registry_covers_every_shipped_icon`) take the `suffix=".svg"` filter of
  `tests/support/shipped_files.py`'s `shipped_files(root, suffix=None)` so they keep iterating only
  the icons and do not mistake a binary cursor for an icon. The placeholder register and
  `tests/support/package_metadata.py` stay untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add a `## cursors` section with one row — the arrow draws the black face
  and white outline at nominal sizes 16/24/32 with the hotspot at the tip, and the four files are
  byte-identical apart from their names — pinned to `tests/test_cursors_theme.py`, carrying the
  provenance exception above (this is the standing exception window the cursor series uses; no
  screenshot shows a pointer).

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry
moves to `## Done`; see Plan record). The `Makefile` and `.gitattributes` are untouched; do not
edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; the pinned
  pixels and hotspots hold for all three nominal sizes (scaled accordingly); the aliases are
  byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size from the
  generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin holds with the four cursor files (removing one, or
  editing the committed grid's colours, fails the matching test), and every SVG-level icon
  assertion keeps iterating only the icons because of its `suffix=".svg"` filter from
  `tests/support/shipped_files.py`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## cursors` row; `git diff --name-status` names only the files listed under "Files touched"
  (besides the backlog move) and neither the `Makefile` nor `PLANS-DONE.md`.
- When the work lands, `grep -n '^### Platinum cursor theme, part 3/3: Generate and ship the Xcursor
  arrow cursor artifact' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's, and `grep -F 'Generate and ship the Xcursor arrow cursor artifact'
  PLANS-DONE.md` exits 1 with no output.

## Done

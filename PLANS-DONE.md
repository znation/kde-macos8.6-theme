# Done plans

Finished plans, newest first, moved here by tumwater from PLANS.md's `## Done`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Done

### Correct the shared sunken-outside field's bottom corners to the reference field's true bottom (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `sunken_outside_face_corners()` in `tests/svg_assertions/faces.py` derives its
bottom-left and bottom-right corners from the internal separator at y=350-351 inside the Setup
Assistant's sunken content field in `firstboot_betawiki.png`, not from the field's true bottom.
Correct the shared table and every artifact that paints from it, then re-anchor the two reference
tests on the field's true bottom.

**Approach.** The field in `firstboot_betawiki.png` runs (28,58)-(431,377): left shadow x=28
`y=58..376`, outline x=29, top shadow y=58, bottom highlight y=377 `x=29..431`, right highlight
x=431 `y=59..377`. Its bottom-left outer pixel (28,377)=#CCCCCC is unpainted (the window face) and
the highlight starts one pixel in at (29,377)=#FFFFFF; its bottom-right corner block is
(430,376)=#000000, (431,376)=#FFFFFF, (430,377)=#FFFFFF, (431,377)=#FFFFFF. The item view's
bottom-left in `setup_emaculation.png` ((22,478)=#CCCCCC, (23,478)=#FFFFFF) shows the same corner;
its bottom-right sits under the scrollbar corner (#CCCCCC), so the corrected shared geometry is
the only grounded arrangement. The field's bottom interior is the #DDDDDD footer, so the bottom
border run checks only the outline and highlight.

**Files touched.**
- `tests/svg_assertions/faces.py`: in `sunken_outside_face_corners`'s `bottomleft` table set
  `(0,2)` to `None` and `(1,2)` to `"#FFFFFF"`; in `bottomright` set `(1,2)` to `"#FFFFFF"`.
- `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`: redraw `base-bottomleft` and
  `base-bottomright` to the corrected 3x3 tables; reword the header comment's bottom-anchor
  sentence.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: redraw `lineedit-normal-bottomleft`,
  `lineedit-normal-bottomright`, `lineedit-focused-bottomleft`, `lineedit-focused-bottomright` and
  `itemview-normal-bottomright`, `itemview-focused-bottomright` to the corrected 2x2 outer blocks;
  update the header comment's bottom anchors.
- `tests/test_kvantum_lineedit_reference.py`: `FIELD_BOTTOM=377`; bottom run `((100,376),
  "#000000"), ((100,377), "#FFFFFF")`; replace the bottom four `FIELD_CORNER_PIXELS` with the true
  (28,376)/(29,376)/(28,377)/(29,377) and (430,376)/(431,376)/(430,377)/(431,377) pixels.
- `tests/test_desktoptheme_lineedit.py`: the same bottom run and corner pixels; update comments.
- `tests/support/desktoptheme_paths.py`: `FIRSTBOOT_MAX_ROWS = 378`.
- `tests/test_svg_assertions_faces.py`: update the pinned `sunken_outside_face_corners("#DDDDDD")`
  table's `bottomleft`/`bottomright` rows.
- `tests/test_kvantum_itemview_reference.py`: drop the now-redundant `corners["bottomleft"]`
  override; update its comment.
- `tests/test_kvantum_bevel_pixels.py`: `_ITEMVIEW_BOTTOMLEFT` now equals the helper's block;
  remove the override if it is redundant.
- `macos8.6-screenshots/sources.txt`: extend the `firstboot_betawiki.png` note to record the
  field's true bottom and the shared bottom-left corner.
- `docs/invariants.md`: extend the item view row's provenance-exception cell to record that its
  bottom-right corner sits under the scrollbar and follows the line edit's grounded corner.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 28 377` prints #CCCCCC and
  `... 29 377` prints #FFFFFF; `... 30 375` prints #FFFFFF, `... 30 376` #000000, `... 30 377`
  #FFFFFF; `... 430 377` and `... 431 377` print #FFFFFF.
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 478` prints #CCCCCC and
  `... 23 478` prints #FFFFFF.
- `tests/test_kvantum_lineedit_reference.py::TestLineEditReference` and
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference` pass when the Git-LFS reference is
  materialized, and the corrected helper's bottom-left block is `("#999999", "#000000", None,
  "#FFFFFF")`.
- `tests/test_svg_assertions_faces.py::TestSunkenOutsideFaceCorners`,
  `tests/test_desktoptheme_lineedit.py::TestLineEdit` and
  `tests/test_kvantum_bevel_pixels.py::TestLineEditBevelPixels`/`TestItemViewBevelPixels` pass
  against the redrawn art.
- `make check` is green.

### Ground the Kvantum item view's sunken field in the reference Finder content area (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws the
`itemview-normal` and `itemview-focused` frames with the #000000 outline on the outer edge and
the bevel inside it (`itemview-normal-top` is #000000 then #999999, `itemview-normal-left` the
same) -- the same inversion the line edit had before its fix. The reference item view puts the
sunken bevel *outside* the outline -- `macos8.6-screenshots/setup_emaculation.png` (retail Mac
OS 8.6 installer CD Finder window, item view): left (22,250)=#999999, (23,250)=#000000,
(24,250)=#FFFFFF; top (200,118)=#999999, (200,119)=#000000, (200,120)=#FFFFFF; right
(452,200)=#000000, (453,200)=#FFFFFF; bottom (100,477)=#000000, (100,478)=#FFFFFF. Redraw the
Kvantum item view's tiles as that bevel-outside ring so a KDE application's list/tree view
matches the reference, exactly as the landed line-edit fix did for text fields.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of the `itemview-normal-*`
  and `itemview-focused-*` frames, rewrite the four edge slices so the outer pixel is the bevel
  (#999999 top/left, #FFFFFF bottom/right) and the inner pixel is the #000000 outline, leaving
  the #FFFFFF centre face unchanged (the same pixels as the landed `lineedit-normal-*`/
  `lineedit-focused-*` art, except the bottom-left corner below). Rewrite each 2x2 corner as the
  outer 2x2 of `sunken_outside_face_corners("#FFFFFF")` in `tests/svg_assertions/faces.py`,
  except the bottom-left: the reference's bottom highlight starts one pixel in from the left
  ((22,478)=#CCCCCC, the window face), so its outer bottom pixel is left unpainted and the
  #FFFFFF highlight sits at the inner bottom pixel. The top-right outer pixel stays unpainted
  (reference (453,118)=#CCCCCC, the window face). Leave `itemview-pressed-*` and
  `itemview-toggled-*` flat #CCCCFF, and add a comment above the two groups naming the
  reference and its sampled pixels.
- Update the file-header comment (the sentence "the line edit is the white sunken field") to
  name the item view as sharing that field.
- `tests/test_kvantum_bevel_pixels.py`: keep `"itemview"`'s flat `pressed`/`toggled` states in
  `SURFACE_STATES` (so the flat #CCCCFF art stays pinned) and add a `TestItemViewBevelPixels`
  case mirroring `TestLineEditBevelPixels` (reusing `LINEEDIT_EDGES`, `_lineedit_edge_map` and
  `_lineedit_corners`, with an item-view bottom-left override) for prefixes `itemview-normal`
  and `itemview-focused`, so a state repeating the old outline-outside art fails there.
- New `tests/test_kvantum_itemview_reference.py`: a `ReferenceScreenshotMixin` case over
  `setup_emaculation.png` (`MAX_ROWS = 479`) that re-derives the field's four border runs, its
  top-left 2x2 corner and its bottom-left 2x2 corner and asserts the rendered Kvantum
  `itemview-normal` tiles paint the same sunken-outside arrangement; skips when the image is
  not materialized. The reference field's top-right and bottom-right corners sit under the
  status header and the scrollbars, so the test derives only the clean left/top/right/bottom
  runs and the two clean corners (the bottom-left's outer bottom pixel is the window face, so
  the shipped tile leaves it unpainted).
- `docs/invariants.md`: add a `kvantum` row `| The item view is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_itemview_reference.py::TestItemViewReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_itemview_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `itemview-normal-*` and `itemview-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline, except the
  bottom-left, whose outer bottom pixel the reference leaves to the window face (the shipped
  tile leaves it unpainted and paints the #FFFFFF highlight one pixel in).
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 250` prints
  `153,153,153 #999999`, `... 23 250` prints `0,0,0 #000000`, `... 24 250` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and the other three runs and
  passes, skipping when the image is not materialized.
- `TestItemViewBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Checker unreadable-input mutations: manufacture a register, asset or reference that cannot be read so the checker's own diagnostic is observable (planned 2026-10-19 by the steward role; from the recurring `no-fake` validation gap in four Fixed entries) — done 2026-10-19

**Goal.** Four Fixed entries share one shape: a record checker reads an input that cannot be read
-- a register path that is a directory, a text asset under `theme/` that is a dangling symlink
resolving inside the root, a register reference containing a NUL byte, or a reference to a test
file that cannot be decoded -- and the read raises a bare `OSError`/`ValueError` that names
neither the checker nor the offending row, aborting the check with an unrelated traceback. Each
was confirmed only by hand-building a shim the suite did not have (its `no-fake` gap).
`tests/support/checker_mutations.py` already manufactures the malformed register and theme inputs
the shipped data never holds; extend it with the four unreadable-input shapes so confirming the
next bug of this kind reuses the scratch fixture instead of a one-off.

**From (the `no-fake` Fixed entries).**
- `tests/placeholders.py` lets an unreadable register escape as a bare `OSError`.
- `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare
  `FileNotFoundError`.
- `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception.
- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated
  exception.

**Approach.**
- `tests/support/checker_mutations.py`: teach `Scratch` to clean up a directory it wrote (its
  `reset` only unlinks files today), then add four `Mutation` entries: `unreadable-register`
  (replace the register path with a directory so `register_entries`' `OSError` arm fires;
  diagnostic `cannot be read`), `dangling-symlink-inside-theme` (a text asset under `theme/`
  symlinked to a missing path inside the root; diagnostic `cannot be read`),
  `reference-with-nul-byte` (`_replace_first_reference` with a `\x00` in the path; diagnostic
  `NUL byte`), and `unreadable-test-file` (point the first row's reference at a scratch file
  written as undecodable bytes; diagnostic `cannot be read as Python`).
- `tests/placeholders.py` and `tests/invariants.py`: add each new name to `REJECTION_SHAPES` in
  the same commit, so `test_checker_mutations.py`'s two set-equality guards keep each checker's
  boundary list and the mutation table in step.

**Implementation note.** `unreadable-test-file` overwrites the scratch copy of the existing
`MUTANT_MODULE` with undecodable bytes (and `Scratch.reset` now restores an overwritten file)
rather than adding a new scratch path, so the stage self-check's added-nonexistent-path guard
keeps seeing a repository path that exists.

**Files touched.** `tests/support/checker_mutations.py`, `tests/placeholders.py`,
`tests/invariants.py`.

**Acceptance criteria.**
- `tests/test_checker_mutations.py` drives each of the four new mutations, and each makes its
  checker raise the named `AssertionError`; the two unreadable-read mutations fail if the
  checker's `OSError` arm is removed.
- The two `REJECTION_SHAPES` set-equality guards pass with the four new names.
- `make check` is green.

### Ground the Kvantum line edit's sunken bevel in the reference text field (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws the
`lineedit-normal` and `lineedit-focused` frames with the #000000 outline on the outer edge and
the bevel inside it (`lineedit-normal-top` is #000000 then #999999, `lineedit-normal-left` the
same). The reference text field puts the sunken bevel *outside* the outline --
`macos8.6-screenshots/firstboot_betawiki.png` (28,95)=#999999, (29,95)=#000000,
(30,95)=#FFFFFF -- the structure `theme/desktop-themes/org.macos8.desktop/widgets/lineedit.svg`
already paints and `tests/test_desktoptheme_lineedit.py` already pins. Redraw the Kvantum line
edit's tiles as that bevel-outside ring so a KDE application's text field matches the reference.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of the `lineedit-normal-*`
  and `lineedit-focused-*` frames, rewrite the four edge slices so the outer pixel is the bevel
  (#999999 top/left, #FFFFFF bottom/right) and the inner pixel is the #000000 outline, leaving
  the #FFFFFF centre face unchanged: the top/left slices read #999999 then #000000 from the
  outer edge inward, and the bottom/right slices read #FFFFFF then #000000 the same way (in
  slice coordinates the bottom/right slices are #000000 then #FFFFFF, their outer edge being
  the last row/column). Rewrite each 2x2 corner as the outer 2x2 of the `sunken-outside`
  corner table in `tests/svg_assertions/faces.py` (`sunken_outside_face_corners("#FFFFFF")`), scaled to the 2px
  border: the #999999/#FFFFFF bevel wraps the #000000 outline, which meets at the inner corner,
  and the top-right outer pixel stays unpainted because the reference field's top shadow stops
  one pixel short of the outer highlight (reference (431,58)=#CCCCCC, the window face). Add a
  comment above the two line-edit groups naming the reference and its sampled pixels; leave the
  file header comment untouched.
- `tests/test_kvantum_bevel_pixels.py`: add a `TestLineEditBevelPixels` case that renders both
  states with `render_slices` and pins every slice and corner pixel, so a state repeating the
  old outline-outside art fails here.
- New `tests/test_kvantum_lineedit_reference.py`: a `ReferenceScreenshotMixin` case over
  `firstboot_betawiki.png` that re-derives the field's left/top/right/bottom border runs and its
  corner pixels (the same coordinates `tests/test_desktoptheme_lineedit.py` samples) and asserts
  the rendered Kvantum `lineedit-normal` tiles paint the same sunken-outside arrangement; skips
  when the image is not materialized.
- `docs/invariants.md`: add a `kvantum` row `| The line edit is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_lineedit_reference.py::TestLineEditReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_lineedit_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `lineedit-normal-*` and `lineedit-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline.
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 28 95` prints
  `153,153,153 #999999`, `... 29 95` prints `0,0,0 #000000`, `... 30 95` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and passes, skipping when the
  image is not materialized.
- `TestLineEditBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Ground the Kvantum check box face in the reference's raised Platinum check box (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws each `checkbox-*`
interior as a flat `#FFFFFF` square inside a 1px `#000000` outline (pinned as `_CHECKBOX_FACE`
in `tests/test_kvantum_svg.py`), so a KDE application's check box is a flat white square. The
reference set's check box — the Get Info window's "Locked" / "ロック" check box at
`macos8.6-screenshots/aboutsystem_betawiki.png` x=38..49, y=382..393 (the same face in
`systeminfo_betawiki.png` at the same pixels) — is a raised Platinum square: a 1px `#000000`
outline, a 1px `#FFFFFF` top/left highlight, a `#DDDDDD` face, and a 1px `#888888` bottom/right
shadow. Redraw the four `checkbox-*` faces as that raised square so the Kvantum check box matches
the reference, and pin it against the reference pixels.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of `checkbox-normal`,
  `checkbox-focused`, `checkbox-checked-normal` and `checkbox-checked-focused`, replace the two
  face rects (the 14x14 `#000000` outline and the 12x12 `#FFFFFF` face) with the reference's
  raised structure on the same 14x14 canvas: the 14x14 `#000000` outline, a `#FFFFFF` top row and
  left column, the `#DDDDDD` face, and an `#888888` bottom row and right column, with the
  reference's bottom-left corner left `#DDDDDD`. Keep each checked state's five glyph rects
  unchanged (no reference shows a checked box, so the check stays KDE-required).
- `tests/test_kvantum_svg.py`: update `_CHECKBOX_FACE` to the new rect tuple, and add the
  check-box shadow `#888888` as a named extra in `test_uses_exactly_the_platinum_palette`'s
  `extra` set (the reference's check-box shadow), so the exact-palette assertion still holds.
- New `tests/test_kvantum_checkbox_reference.py`: a `ReferenceScreenshotMixin` case over
  `aboutsystem_betawiki.png` that re-derives the check box at x=38..49, y=382..393 — the outer
  ring `#000000`, the row and column inside it `#FFFFFF`, the interior `#DDDDDD`, and the inner
  bottom row and right column `#888888` — and asserts the shipped `checkbox-normal` interior
  paints those same four colours in a raised arrangement. Skips when the image is not
  materialized.
- `docs/invariants.md`: add a `kvantum` row `| The check box face is the reference's raised
  Platinum square. | tests/test_kvantum_checkbox_reference.py::TestCheckBoxReference | The
  reference's check box is a beta build (`aboutsystem_betawiki.png`, `systeminfo_betawiki.png`);
  no retail screenshot shows a check box. |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_svg.py`, `tests/test_kvantum_checkbox_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Each `checkbox-*` interior draws the reference's raised face (`#000000` outline, `#FFFFFF`
  top/left highlight, `#DDDDDD` face, `#888888` bottom/right shadow), and each checked state's
  glyph is unchanged.
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 38 382` prints
  `0,0,0 #000000`, `... 39 383` prints `255,255,255 #FFFFFF`, `... 40 385` prints
  `221,221,221 #DDDDDD`, and `... 48 385` prints `136,136,136 #888888`; the new test re-derives
  those pixels and passes, skipping when the image is not materialized.
- `test_kvantum_svg`'s `_CHECKBOX_FACE` matches the new art, and
  `test_uses_exactly_the_platinum_palette` passes with the named `#888888` extra.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Ship the Platinum menu submenu arrow (`go-next-symbolic`) grounded in the open Apple menu (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** KDE draws a menu's submenu indicator as a `Kirigami.Icon` with
`source: "go-next-symbolic"` — `PlasmaComponents` `MenuItem.qml`'s `arrow` and the kicker's
`ItemListDelegate.qml` both name that icon — and the icon theme declares `Inherits=breeze`, so
the indicator is Breeze's thin chevron. The reference's open Apple menu
(`macos8.6-screenshots/desktop_archiveorg8.6hd.png`, retail 8.6, already the anchor for the menu
body and the view item) draws a solid black right triangle on each submenu row: at the
"Automated Tasks" row the dark pixels (every channel < #AA) are a 5x9 right triangle with a
full-height left edge, bounding box x=151..155, y=91..99, and the triangle is pure `#000000` at
(152, 93). Ship that triangle as the theme's `go-next-symbolic` so the submenu indicator matches
the reference instead of falling back to Breeze's chevron.

**Approach.**
- Add `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (16x16) and
  `theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (22x22), each a single
  solid `#000000` right-triangle path — 16x16 `M 6,3 L 6,11 L 10,7 Z` (a 5x9 triangle whose left
  edge is full-height and whose tip is at the vertical middle), the 22x22 path the same shape at
  the 22/16 scale — with a header comment naming the `desktop_archiveorg8.6hd.png` anchor and
  recording that the 16px canvas is KDE-required (the reference menu row is ~17px). Draw the
  triangle alone: the reference's 1px lighter left edge (x=150 is #E8E8E8 against the #DDDDDD
  body) is a bevel a `-symbolic` icon cannot keep, because KDE recolours the icon to the menu
  text colour.
- `theme/icons/org.macos8.desktop/index.theme`: add `16x16/actions` and `22x22/actions` to
  `Directories` and add the matching `[16x16/actions]` / `[22x22/actions]` sections (`Size=16`
  and `22`, `Context=Actions`, `Type=Fixed`), so a 16px or 22px lookup resolves to the theme's
  triangle before Breeze's chevron.
- `tests/test_icon_theme.py`: add both icons to `SHIPPED_ICONS` and to `ICON_SHAPES` (one
  `path` element with its `d` and `fill`); `INSTALLED_FILES` derives from `SHIPPED_ICONS`.
- New `tests/test_icon_arrow_reference.py`: a `ReferenceScreenshotMixin` case over
  `desktop_archiveorg8.6hd.png` that re-derives the "Automated Tasks" submenu triangle — the
  dark pixels (every channel < 170) in x=146..159, y=86..104 — asserts it is a right triangle
  (its left column spans the full 9-row height, its widest row is the vertical middle) with a
  5x9 bounding box, and asserts the shipped 16x16 path's bounding box is the same 5x9; it skips
  when the reference is not materialized.
- `docs/invariants.md`: add an icons row naming the new test.
- `README.md`: extend the icon-theme sentence to name the menu submenu arrow alongside the
  kicker logo.

**Files touched.** `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/index.theme`, `tests/test_icon_theme.py`,
`tests/test_icon_arrow_reference.py` (new), `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- Both icons ship, are square SVGs of their declared size (16x16, 22x22), and each one's only
  drawing element is a solid `#000000` right-triangle `path`; `TestIcons` and `TestIconGeometry`
  pass.
- `index.theme` declares both `actions` directories, so
  `test_every_shipped_icon_lives_in_a_declared_size_directory` passes.
- The new reference test re-derives the 5x9 right triangle from `desktop_archiveorg8.6hd.png`
  (`python3 tools/sample.py macos8.6-screenshots/desktop_archiveorg8.6hd.png 152 93` prints
  `0,0,0 #000000`) and passes; it skips (not fails) when the reference is not materialized.
- `make check` is green.

Recorded scope: the RTL names (`go-next-rtl-symbolic`, `go-next-symbolic-rtl`) are not shipped;
the theme targets the reference's LTR English UI, so a right-to-left layout keeps Breeze's
chevron.

### Ground the Aurorae inactive frame in the reference's inactive windows (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The `decoration-inactive` nine-slice and its header comment claim "the reference set has
no inactive window" and therefore paint KDE-required greys: the active tile's
`#FFFFFF`/`#777777` pinstripes and `#CCCCCC` field flattened to `#CCCCCC`, keeping the `#000000`
outlines and the `#999999` shadow. The reference set does show inactive windows:
`macos8.6-screenshots/desktop_fandom.png` (retail 8.6, the image the tabbar and progressbar
already sample) shows four unfocused windows (the "Mac OS 8.6", "Utilities", "Applications" and
"Apple System Profiler" windows), and the lossless beta `macos8.6-screenshots/
systeminfo_betawiki.png` shows a fifth behind the active "System Info" window. Their frame is a
flat `#DDDDDD` field with a 1px `#555555` outline on both the outer and inner edges of the
border (the outer edge and the inner edge that meets the client), with no pinstripes, no
white highlight and no `#999999` shadow (verified with `tools/sample.py`; the scheme's own
`[WM] inactiveBackground=221,221,221` agrees). Correct the art and the provenance, and pin the
inactive frame to the reference pixels.

**Approach.**
- `theme/aurorae/themes/org.macos8.desktop/decoration.svg`: rewrite every `decoration-inactive-*`
  tile to the reference's flat inactive frame — the 1px `#555555` outer and inner outlines
  (the top and bottom rows of `decoration-inactive-top`, the outer and inner columns of the
  side tiles, the outer and inner rows of the bottom tiles, and the corner pixels where they
  meet) and `#DDDDDD` everywhere between; recolor the `#000000` outlines to `#555555` and drop
  the `#999999` shadow and the `#FFFFFF`/`#777777`/`#CCCCCC` bevel fills. Keep the active
  geometry (18x34 canvas, 6px side/bottom border, 22px top border, 6x6 centre). Recompress
  `decoration.svgz` (`gzip -9 -n`) so `test_svgz_is_the_compressed_svg` still passes.
- Reword the `decoration.svg` header comment: name `desktop_fandom.png` (2 image px per logical
  px) as the inactive anchor and `systeminfo_betawiki.png` as lossless corroboration, state the
  flat `#DDDDDD` field with the 1px `#555555` outer and inner outlines, and delete the "the
  reference set has no inactive window" clause.
- `tests/support/aurorae_fixtures.py`: add `INACTIVE_REFERENCE` (`desktop_fandom.png`, with a row
  bound covering y=900), `INACTIVE_FRAME_GREY = "#DDDDDD"` and `INACTIVE_OUTLINE = "#555555"`;
  keep `INACTIVE_GREY = "#CCCCCC"` for the button boxes. Load `INACTIVE_REFERENCE` in
  `ReferenceImageCase.setUpClass` (skip when unmaterialized, like `REFERENCE`) and add an
  `inactive_pixel(x, y)` accessor.
- `tests/test_aurorae_frame.py`: replace `_assert_flattened_inactive_tile` and its callers with
  reference-derived checks; add `TestDecorationSvg.test_inactive_frame_matches_reference`, which
  derives each inactive tile from its active tile (pinned to the reference) with the `#000000`
  outlines recolored `#555555` and every other fill flattened to `#DDDDDD`, so no `#FFFFFF`,
  `#777777`, `#999999` or `#CCCCCC` pixel survives, and cross-checks the field and outline
  against `inactive_pixel(300, 75)`, `(1000, 130)`, `(1500, 80)`, `(300, 880)` (`#DDDDDD`) and
  `(300, 57)`, `(25, 75)` (`#555555`). Reword the module docstring and the inactive tests so they
  name the reference instead of claiming none exists.
- `theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`
  and `tests/test_aurorae_buttons.py`: replace each "the reference set has no inactive window"
  clause with the accurate one — the reference's inactive windows draw no close/collapse boxes in
  their title bars, so the greyed inactive box stays KDE-required. No art change; `INACTIVE_GREY`
  and the button tests are unchanged.
- `macos8.6-screenshots/sources.txt`: extend the `desktop_fandom.png` note to record that it
  grounds the inactive window frame (the flat `#DDDDDD` title bar and 1px `#555555` outline of its
  four unfocused windows).
- `docs/invariants.md`: update the aurorae frame row to name the inactive reference, and the
  title-bar-box row so its inactive grey is recorded as KDE-required rather than re-derived.

**Files touched.** `theme/aurorae/themes/org.macos8.desktop/decoration.svg` (+ `.svgz`),
`theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`,
`tests/support/aurorae_fixtures.py`, `tests/test_aurorae_frame.py`,
`tests/test_aurorae_buttons.py`, `macos8.6-screenshots/sources.txt`, `docs/invariants.md`.

**Acceptance criteria.**
- The `decoration-inactive-*` tiles paint only `#DDDDDD` and `#555555`, with `#555555` on the
  outer edge; no `#FFFFFF`, `#777777`, `#999999` or `#CCCCCC` pixel remains in them.
- `python3 tools/sample.py macos8.6-screenshots/desktop_fandom.png 300 75` (and `1000 130`,
  `1500 80`, `300 880`) prints `221,221,221 #DDDDDD`; `... 300 57` and `... 25 75` print
  `85,85,85 #555555`.
- `TestDecorationSvg.test_inactive_frame_matches_reference` passes when `desktop_fandom.png` is
  materialized and skips (not fails) when it is not, through the `skip_unless_materialized` path.
- No Aurorae SVG header or Aurorae test docstring still claims the reference set has no inactive
  window.
- `decoration.svgz` decompresses to the edited `decoration.svg`.
- `make check` is green.

### Correct the desktop theme's false "no menu-open / no combo-box" reference claims (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** Three desktop-theme SVG header comments justify a palette-only value by claiming the
reference set shows no such surface, but the set does show it, so the stated reason is false and
the real reason the value has no per-pixel sample is hidden.

- `theme/desktop-themes/org.macos8.desktop/widgets/viewitem.svg` says "the reference set has no
  open-menu screenshot, so the menu-item highlight has no per-pixel menu sample". The set's open
  Apple menu is `macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the image the
  `widgets/background.svg` plan already sampled its grey menu body from. That menu shows no
  highlighted item (a scan of the image finds no `#CCCCFF` pixel, the highlight fill), so the
  conclusion holds but the stated reason is wrong.
- `theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg` repeats the claim as "the
  reference set has no menu-open screenshot". The same open Apple menu is a menu-open screenshot;
  its open title is the Apple-logo kicker (a text title is never shown open), so the pressed
  text-title fill has no per-pixel sample for that different reason.
- `theme/desktop-themes/org.macos8.desktop/widgets/arrows.svg` says "no reference screenshot
  shows a combo box or menu button". The set does: the beta `macos8.6-screenshots/
  systeminfo_betawiki.png` Get Info window's "General Information" and "None" popups, and the
  JPEG `macos8.6-screenshots/opendialog_macrumors86.jpg` Open dialog's "ROM-new" popup. Their Mac
  OS indicator is a double (up+down) arrow, not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle is still a KDE-required shape — but the
  comment must give that reason instead of the false one.

Correct all three comments to state what the reference actually shows, and pin the corrected
provenance so the false claim cannot return.

**Approach.**
- `viewitem.svg`: replace the "the reference set has no open-menu screenshot, so the menu-item
  highlight has no per-pixel menu sample" clause with one naming the reference: the reference
  set's open Apple menu (`desktop_archiveorg8.6hd.png`) shows no highlighted item, so the
  menu-item highlight has no per-pixel sample. Keep the `[Colors:Selection]
  BackgroundNormal=204,204,255` token sentence and the `normal`-slices paragraph unchanged.
- `menubaritem.svg`: replace "the reference set has no menu-open screenshot, so the pressed fill
  has no per-pixel menu sample" with: the reference set's open Apple menu
  (`desktop_archiveorg8.6hd.png`) opens the Apple-logo kicker's title, not a text title, so the
  pressed text-title fill has no per-pixel sample. Keep the `[Colors:Selection]` token sentence
  and the side-padding grounding paragraph unchanged.
- `arrows.svg`: replace the "Provenance: no reference screenshot shows a combo box or menu
  button" sentence with one naming the beta Get Info's and the Open dialog's popup buttons and
  stating that their double-arrow indicator is not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle stays a KDE-required shape and the fill
  reuses the grounded Platinum black (`#000000`) `widgets/checkmarks.svg` pins. Keep the
  literal-attribute sentence.
- `tests/test_desktoptheme_provenance.py` (new): a `TestProvenance` case reading each SVG's
  leading XML comment with a small `header_comment(path)` helper (the SVGs open with a single
  `<!-- ... -->` after the XML declaration) and, per `(path, required, forbidden)` case, asserting
  the comment contains the reference filename it must cite and does not contain the false phrase.
  Import the three paths from `support.desktoptheme_paths` (`VIEWITEM_SVG`, `MENUBARITEM_SVG`,
  `ARROWS_SVG`). Cases:
  - `viewitem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no open-menu screenshot`.
  - `menubaritem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no menu-open screenshot`.
  - `arrows.svg`: requires `systeminfo_betawiki.png`; forbids `no reference screenshot shows a
    combo box`.
- `docs/invariants.md`: add a `desktop-themes` row `| The `viewitem.svg`, `menubaritem.svg` and
  `arrows.svg` provenance comments name the reference screenshot their claim rests on and do not
  claim the set shows no such surface. | tests/test_desktoptheme_provenance.py::TestProvenance |
  none |`.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/viewitem.svg`,
`theme/desktop-themes/org.macos8.desktop/widgets/menubaritem.svg`,
`theme/desktop-themes/org.macos8.desktop/widgets/arrows.svg`,
`tests/test_desktoptheme_provenance.py` (new), `docs/invariants.md`.

**Acceptance criteria.**
- `viewitem.svg`'s and `menubaritem.svg`'s headers name `desktop_archiveorg8.6hd.png` and no
  longer contain "no open-menu screenshot" / "no menu-open screenshot" respectively;
  `arrows.svg`'s header names `systeminfo_betawiki.png` and no longer contains "no reference
  screenshot shows a combo box".
- `tests/test_desktoptheme_provenance.py::TestProvenance` passes, and fails when any of the three
  comments is reverted to its false phrase or loses its reference filename.
- The new `docs/invariants.md` row resolves through `tests/invariants.py` (its named test case
  exists), and no existing widget assertion changes: the three SVGs' parsed elements and fills are
  untouched.
- `make check` is green.

### Correct the `[Colors:Selection]` anchor's provenance: the reference region is the Setup Assistant's Introduction banner, not a list selection (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`
grounds `[Colors:Selection] BackgroundNormal=204,204,255` in `firstboot_betawiki.png`, but its
comment calls the sampled region "the Setup Assistant's list selection ... a full-width
highlighted row". The region is the Setup Assistant window's "Introduction" title banner: a flat
`#CCCCFF` band spanning roughly x=31..428, y=61..85, under the `#000000` rule at y=59 and the
`#FFFFFF` highlight at y=60 (verified with `tools/sample.py`). `tests/support/platinum_palette.py`
compounds the error, calling the selection fill one of the "KDE-required `[Colors:Tooltip]` and
`[Colors:Selection]` roles no screenshot shows" — a claim `test_selection_background` itself
contradicts. Correct both to state what the reference shows, and widen the anchor so it pins the
banner's flat extent rather than a single pixel.

**Approach.**
- `tests/test_colorscheme_reference.py`:
  - Reword the `REFERENCE_FIRSTBOOT` comment: the sampled region is the Setup Assistant's flat
    `#CCCCFF` "Introduction" banner, not a list selection, and note that it is the reference
    set's flat `#CCCCFF` region.
  - In `test_selection_background`, reword the comment and assert the fill is flat across the
    banner by calling
    `assert_anchor_at("Colors:Selection", "BackgroundNormal", ..., path=REFERENCE_FIRSTBOOT)` at
    `(100, 63)`, `(200, 63)`, `(300, 63)` and `(200, 80)` (all inside the band, clear of its
    text), and one call for the same point with key `BackgroundAlternate`, which the scheme sets
    to the same `204,204,255`.
  - Reword the class docstring's "``firstboot_betawiki.png`` for the selection anchor" clause to
    name the Introduction banner.
- `tests/support/platinum_palette.py`: rewrite the module docstring so the selection fill is
  grounded by `test_colorscheme_reference.TestReferenceAnchors.test_selection_background` in the
  Setup Assistant's Introduction banner (`firstboot_betawiki.png`) and only the tooltip face is
  the KDE-required role no screenshot shows; update the `SELECTION` comment to name that
  reference.
- `macos8.6-screenshots/sources.txt`: extend the `firstboot_betawiki.png` entry with a grounding
  note (the Setup Assistant's Introduction banner is the flat `#CCCCFF` band at y=61..85 that
  grounds `[Colors:Selection] BackgroundNormal`), mirroring the `setup_emaculation.png` entry.

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/support/platinum_palette.py`,
`macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 100 63` (and `300 63`,
  `200 80`) prints `204,204,255 #CCCCFF`, and
  `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 200 59` prints
  `0,0,0 #000000`.
- `TestReferenceAnchors.test_selection_background` asserts the scheme's `BackgroundNormal` and
  `BackgroundAlternate` at all four banner points and still skips (not fails) when the Git-LFS
  reference is not materialized, through the existing `pixel`/`skip_unless_materialized` path.
- `tests/test_colorscheme_reference.py` and `tests/support/platinum_palette.py` no longer call
  the sampled region a "list selection" or claim `[Colors:Selection]` is a role "no screenshot
  shows".
- `macos8.6-screenshots/sources.txt`'s `firstboot_betawiki.png` entry names the selection anchor
  and `python3 tools/check_references.py` still accepts the record.
- `make check` is green.

### Ground the `[Colors:View] BackgroundAlternate` scroll-bar trough anchor in `setup_emaculation.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The color scheme's `[Colors:View] BackgroundAlternate=238,238,238` is the flat
`#EEEEEE` trough that `theme/desktop-themes/org.macos8.desktop/widgets/scrollbar.svg`,
`slider.svg` and `switch.svg` paint. It is the trough that `tests/support/platinum_palette.py`
records as "pinned only by the widget tests that draw it", unlike the face, view, chrome and
selection anchors that `tests/test_colorscheme_reference.py::TestReferenceAnchors` re-derives from
a retail screenshot. The retail installer window in `setup_emaculation.png` shows the trough, so
add an anchor there and tie the scroll bar's own slices to the same pixels.

**Approach.**
- `tests/test_colorscheme_reference.py`: add
  `REFERENCE_SCROLLBAR = os.path.join(ROOT, "macos8.6-screenshots", "setup_emaculation.png")`
  and `SCROLLBAR_ANCHOR_ROWS = 471` (the anchor is at y=470, so the bound must cover row 470),
  load it in `TestReferenceAnchors.setUpClass` next to `REFERENCE_DESKTOP` and
  `REFERENCE_FIRSTBOOT`, and add `test_view_background_alternate` calling
  `assert_anchor_at("Colors:View", "BackgroundAlternate", 200, 470, path=REFERENCE_SCROLLBAR)`.
  The pixel is inside the installer CD window's horizontal scroll bar: the 16px band has a
  `#000000` outline at y=462 and y=477 with a flat `#EEEEEE` trough between them, so (200, 470)
  is clear of both outlines and of the arrow boxes.
- `tests/test_desktoptheme_scrollbar.py`: add a `TestScrollbarReference(ReferenceScreenshotMixin)`
  class, following `tests/test_desktoptheme_line.py::TestLineReference`, with
  `REFERENCE = REFERENCE_SCROLLBAR` (import the path from `support.theme_install`/`ROOT` and
  `TROUGH`/`BLACK` from `support.platinum_palette`). Its `test_trough_matches_reference` asserts
  `self.pixel(200, 470)` is `TROUGH`, `self.pixel(200, 462)` and `self.pixel(200, 477)` are
  `BLACK`, and the trough is flat at `(50, 470)`, `(300, 470)` and `(400, 470)`, so the
  `background-vertical`/`background-horizontal` slices' pinned fills are tied to the screenshot
  and not only to `platinum_palette`.
- `tests/support/platinum_palette.py`: reword the module docstring, which says the trough "is
  pinned only by the widget tests that draw it", to name the new anchor and reference test.
- `macos8.6-screenshots/sources.txt`: extend the `setup_emaculation.png` note to record that it
  grounds the `[Colors:View] BackgroundAlternate` trough anchor (the flat scroll-bar band at
  y=462..477).

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/test_desktoptheme_scrollbar.py`,
`tests/support/platinum_palette.py`, `macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 200 470` prints
  `238,238,238 #EEEEEE`, and the outlines at `(200, 462)` and `(200, 477)` are `#000000`.
- `TestReferenceAnchors.test_view_background_alternate` passes when the Git-LFS reference is
  materialized and skips (not fails) when it is not, through the existing
  `pixel`/`skip_unless_materialized` path; `SCROLLBAR_ANCHOR_ROWS` covers row 470 so the read
  stays in bounds.
- `TestScrollbarReference.test_trough_matches_reference` passes/skips the same way and pins the
  trough fill and both outlines.
- `tests/support/platinum_palette.py` no longer claims the trough is ungrounded.
- `make check` is green.

### Prove the beta `aboutsystem_betawiki.png` window chrome matches the retail `systemprofiler_betawiki.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `macos8.6-screenshots/sources.txt` labels `aboutsystem_betawiki.png` "Mac OS 8.6b2c4LB
beta", and the README's reference policy says beta builds "must not be used as retail
reference" — yet `tests/test_render_surface.py` (the render fidelity gate) and
`tests/support/aurorae_fixtures.py` (the Aurorae decoration tests) read that file. The retail
`systemprofiler_betawiki.png` shows the same window chrome, and this run verified the title-bar
strip, the left and right frame borders, and the close and collapse boxes are byte-identical
between the two (0 differing pixels over 1760, 1272, 1272, 169 and 169 pixels). Add a test that
pins that equality, so the beta is an evidence-backed proxy instead of an unrecorded policy
exception, and record the exception in the docs.

**Approach.**
- New `tests/test_aurorae_reference_equivalence.py`: a `unittest.TestCase` that loads both PNGs
  with `tools.png.read_png`/`pixel_at` and asserts these five regions are pixel-for-pixel equal,
  skipping when either Git-LFS image is not materialized (use
  `support.reference_image.skip_unless_materialized`, the way `ReferenceImageCase` does):
  - title bar: aboutsystem `(30, 25, 80, 22)` vs profiler `(232, 22, 80, 22)`;
  - left border: `(7, 47, 6, 212)` vs `(209, 44, 6, 212)`;
  - right border: `(354, 47, 6, 212)` vs `(808, 44, 6, 212)`;
  - close box: `(11, 29, 13, 13)` vs `(213, 26, 13, 13)`;
  - collapse box: `(343, 29, 13, 13)` vs `(797, 26, 13, 13)`.
  Each region is a window-relative crop (`aboutsystem`'s window origin is `(7, 25)`, the
  profiler's `(209, 22)`, a `(+202, -3)` shift), so the test also records why those two origins
  differ.
- `docs/invariants.md`: add a row to the aurorae section naming the new test as the one that
  pins the beta reference's chrome against the retail screenshot.
- `macos8.6-screenshots/sources.txt` and the README "Reference screenshots" section: record that
  `aboutsystem_betawiki.png` is a beta used as a window-chrome proxy, backed by this test, and
  that the render gate's bottom-border crop (aboutsystem `(13, 419, 308, 6)`) stays on the beta
  because the System Profiler window's bottom differs (its sunken content field and bottom
  scrollbar) and the set has no other lossless retail window-bottom crop.

**Files touched.** `tests/test_aurorae_reference_equivalence.py` (new), `docs/invariants.md`,
`macos8.6-screenshots/sources.txt`, `README.md`.

**Acceptance criteria.**
- The new test passes with both LFS images materialized and skips cleanly when they are not.
- A one-pixel change in any of the five regions of either image makes the test fail (prove it by
  mutating a copy in the test itself, never the reference file).
- `docs/invariants.md`'s aurorae section names the test, and `tests/test_invariants.py` stays
  green.
- `make check` passes.

### Mac OS 8.6 Platinum text field: draw the sunken bevel outside the black outline in `widgets/lineedit.svg` (planned 2026-10-18 by the plan role) — done 2026-10-19

**Goal.** `theme/desktop-themes/org.macos8.desktop/widgets/lineedit.svg` paints the sunken
white field `PlasmaComponents.TextField`/`TextArea`/`SpinBox` and the editable `ComboBox` draw.
It puts the 1px `#000000` outline on the *outer* edge and the `#999999`/`#FFFFFF` bevel *inside*
it. The retail 8.6 reference draws the opposite: the bevel is *outside* the `#000000` outline,
which sits next to the white face. Correct the artwork so a text field matches the reference,
and ground it in reference pixels (the file cites none today). Independent of every other entry:
one artwork file plus its test and a shared assertion convention.

**Reference.** `macos8.6-screenshots/firstboot_betawiki.png` (retail Mac OS 8.6 Setup
Assistant, 1024x768 lossless PNG; `sources.txt` labels it "Mac OS 8.6"). Its body text field:
left border at (28, 95)=`#999999`, (29, 95)=`#000000`, (30, 95)=`#FFFFFF` (face); right border at
(429, 150)=`#FFFFFF` (face), (430, 150)=`#000000`, (431, 150)=`#FFFFFF`; bottom border at
(100, 349)=`#FFFFFF` (face), (100, 350)=`#000000`, (100, 351)=`#FFFFFF`. So the outer 1px ring is
the bevel (`#999999` top/left, `#FFFFFF` bottom/right), the inner 1px ring is `#000000`, and the
face is `#FFFFFF`. `systeminfo_betawiki.png` (8.6a3c2 alpha) and `aboutsystem_betawiki.png`
(8.6b2c4L8 beta) show the same order but are not retail and must not be cited.

**Approach.**
- `widgets/lineedit.svg`: rewrite the eight `base-*` tiles as the ring-swap of the current
  geometry -- the outer 1px ring becomes the bevel (`#999999` top/left, `#FFFFFF` bottom/right),
  the inner 1px ring becomes `#000000`, the face stays `#FFFFFF`. Edges: `base-top` rows
  `#999999`/`#000000`/`#FFFFFF`; `base-bottom` rows `#FFFFFF` (face)/`#000000`/`#FFFFFF` (outer);
  `base-left` columns `#999999`/`#000000`/`#FFFFFF`; `base-right` columns `#FFFFFF`
  (face)/`#000000`/`#FFFFFF` (outer). Corners (row-major 3x3): `base-topleft`
  `#999999 #999999 #999999 / #999999 #000000 #000000 / #999999 #000000 #FFFFFF`; `base-topright`
  `#999999 #999999 #999999 / #000000 #000000 #FFFFFF / #FFFFFF #000000 #FFFFFF`;
  `base-bottomleft` `#999999 #000000 #FFFFFF / #999999 #000000 #000000 / #999999 #FFFFFF #FFFFFF`;
  `base-bottomright` `#FFFFFF #000000 #FFFFFF / #000000 #000000 #FFFFFF / #FFFFFF #FFFFFF #FFFFFF`.
  Keep the 12x12 canvas, the 3px border around the 6px centre, and every hint id.
- Rewrite the header: the sunken bevel sits outside the `#000000` outline, sampled from
  `firstboot_betawiki.png` at the pixels above; drop "the frame's sunken bevel inside it".
- `tests/svg_assertions/faces.py`: add a `"sunken-outside"` bevel to `_require_known_bevel`, to
  `face_edge_bands` (`("#999999", "#000000", face)` outward, `(face, "#000000", "#FFFFFF")`
  mirrored) and to `face_corners` via a new `sunken_outside_face_corners(face)` table holding the
  four corners above. Leave the existing `"sunken"` convention for `frame.svg`.
- `tests/test_desktoptheme_lineedit.py`: switch `test_lineedit_edge_bevels_are_sunken` and
  `test_lineedit_corner_bevels_turn_the_corner` to `"sunken-outside"`; add
  `TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase)` with `REFERENCE` =
  `firstboot_betawiki.png`, `MAX_ROWS = 352`, asserting `hex_colour(self.pixel(x, y))` equals
  `#999999`/`#000000`/`#FFFFFF` for the three border runs above.
- `tests/test_svg_assertions_faces.py`: add the new convention's edge and corner expectations
  beside the existing sunken ones.
- `docs/invariants.md`: the `widgets/lineedit.svg` row's guarantee and its `none` provenance
  exception are unchanged.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/lineedit.svg`,
`tests/test_desktoptheme_lineedit.py`, `tests/svg_assertions/faces.py`,
`tests/svg_assertions/__init__.py` (re-export the new corner table),
`tests/svg_assertions/pixels.py` (docstring only: `assert_face_bevel`'s bevel vocabulary), and
`tests/test_svg_assertions_faces.py`.

**Acceptance criteria.**
- The `base-*` tiles' outer ring is `#999999` (top/left) / `#FFFFFF` (bottom/right) and the inner
  ring `#000000`, with the `#FFFFFF` face; the parsed `fill` set is still
  {`#FFFFFF`, `#999999`, `#000000`}.
- A reference test re-derives the field's left, right and bottom border runs from
  `firstboot_betawiki.png` and skips when the Git LFS image is not materialized.
- The header names `firstboot_betawiki.png` and the sampled pixels and no longer says the bevel is
  inside the outline.
- `frame.svg`'s sunken test and artwork are unchanged.
- `make check` is green.

### Mac OS 8.6 Platinum dialog body: ground `dialogs/background.svg`'s face in the lossless window body (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktop-themes/org.macos8.desktop/dialogs/background.svg` paints the raised
Platinum body that a `PlasmaCore.Dialog` and a `PlasmaCore.AppletPopup` resolve to (the applet and
clock popups). Its header comment says the reference set shows the same grey window bodies but
they are dithered 8-bit captures, so "no single pixel is screenshot-anchored: the values are
palette-derived and recorded as such". Two retail 8.6 references do show an undithered `#DDDDDD`
window body, so the face can be pinned to a pixel and the palette-derived claim dropped.
Independent of every other entry: one reference test class plus one comment rewrite, touching no
artwork.

**Reference.** `macos8.6-screenshots/desktop_archiveorg8.6hd.png` (800x600, lossless PNG): the
About This Computer window body below its title bar, (583..586, 95..100) a solid 4x6 `#DDDDDD`
block ((584, 97) is `#DDDDDD`). Cross-check `macos8.6-screenshots/desktop_fandom.png` (2x,
WebP re-encoded but flat faces exact): the same window body at (1750..1757, 1100..1105) is a solid
8x6 `#DDDDDD` block and (1792, 1126) is `#DDDDDD`. `about_betawiki.png` and
`setup_emaculation.png` are dithered and must not be sampled. `test_colorscheme_reference`
already anchors `[Colors:Window] BackgroundNormal` at (400, 5) of `desktop_archiveorg8.6hd.png`
-- that pixel is the menu bar; this plan anchors the *window body* at a second location, which is
the pixel the header comment says does not exist.

**Approach.**
- `tests/test_desktoptheme_dialog.py`: add `import os`, `from support.platinum_palette import FACE,
  hex_colour`, `from support.reference_image import ReferenceScreenshotMixin` and
  `from support.repo_root import ROOT` (the import pattern `tests/test_desktoptheme_tabbar.py`
  uses); add `TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png")` and
  `MAX_ROWS = 101` (the deepest sampled row is 100), asserting
  `hex_colour(self.pixel(x, y)) == FACE` for the 4x6 block. The mixin skips the class when the Git
  LFS image is not materialized. Leave `TestDialogBackground(RaisedFaceCase, unittest.TestCase)`
  unchanged.
- `theme/desktop-themes/org.macos8.desktop/dialogs/background.svg`: rewrite the provenance
  paragraph -- the `#DDDDDD` face is the window body sampled from `desktop_archiveorg8.6hd.png` at
  (584, 97) and cross-checked at (1792, 1126) of `desktop_fandom.png`; the 1px `#000000` outline
  and the `#FFFFFF`/`#999999` bevel are the shared raised-face rule (the reference window body
  itself is flat, so no window-body pixel grounds them); delete "no single pixel is
  screenshot-anchored: the values are palette-derived and recorded as such".
- `docs/invariants.md`: the `dialogs/background.svg` row's guarantee and its `none` provenance
  exception are unchanged, now that the face is reference-sampled.

**Files touched.** `tests/test_desktoptheme_dialog.py`,
`theme/desktop-themes/org.macos8.desktop/dialogs/background.svg`.

**Acceptance criteria.**
- `TestDialogBackgroundReference` re-derives `#DDDDDD` from `desktop_archiveorg8.6hd.png`'s window
  body and skips when the Git LFS image is not materialized.
- `dialogs/background.svg`'s parsed `fill` set is unchanged (the Platinum four `#DDDDDD`,
  `#000000`, `#FFFFFF`, `#999999`; the hints are painted with `style` and so are not in the parsed
  `fill` set), so `RaisedFaceCase`'s `test_hint_geometry`, `test_frame_bevel` and `test_colours`
  still pass.
- The header comment names `desktop_archiveorg8.6hd.png` (and the `desktop_fandom.png`
  cross-check) with the sampled pixels and no longer calls the face palette-derived or unanchored.
- `make check` is green.

### Mac OS 8.6 Platinum progress bar: paint the reference's vertical gradient in `bar_meter_horizontal.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktop-themes/org.macos8.desktop/widgets/bar_meter_horizontal.svg` paints its
`bar-active` fill as a flat `#9B9BEA` face with a `#9A9A9A`/`#7878D1` bevel, sampled from the
low-resolution boot thumbnail `boot2_betawiki.png`. Mac OS 8.6's progress-bar fill is a vertical
gradient — dark at the top and bottom, `#CBCCFF` at the centre — and the lossless 2x reference
`macos8.6-screenshots/desktop_fandom.png` resolves all ten rows of it. Paint that gradient so the
Plasma progress bar matches the reference instead of a flat fill.

**Reference.** `desktop_fandom.png` (2 image px per logical px), the "Mac OS 30.4 MB" memory meter
of the About This Computer window. The fill spans x=1458..1817, y=1230..1249. Its interior column
x=1600 has, at image rows 1230, 1232, 1234, 1236, 1238, 1240, 1242, 1244, 1246, 1248:
`#515372`, `#666799`, `#8484BB`, `#B0B0EB`, `#CBCCFF`, `#B2B2E8`, `#8586BC`, `#66679B`, `#50527F`,
`#24244D`. The fill's 1px left edge column is `#68688D` ((1458, 1238)) and its 1px right edge
column `#50527F` ((1816, 1238)). The boot2 fill rows at x=102, y=99..102 (`#7D7D9A`, `#9B9BEA`,
`#7878D1`, `#83839D`) are the same gradient downscaled, so the two references agree.

**Approach.**
- `widgets/bar_meter_horizontal.svg`: leave `bar-inactive` (the track) unchanged. Replace the
  `bar-active` flat face and its `#9A9A9A`/`#7878D1` bevel with the ten sampled rows: in the
  `bar-active-top` (rows 0-2), `bar-active-center` (rows 3-6) and `bar-active-bottom` (rows 7-9)
  tiles one 4x1 rect per row carrying that row's colour, and in each of the four corner tiles and
  the `bar-active-left`/`bar-active-right` tiles the same per-row rects (3px wide) plus one 1x3 or
  1x4 rect on the outer column carrying `#68688D` (left) or `#50527F` (right). Keep the 3px border
  around a 4px centre tile, the 10x10 canvas and the `hint-bar-size` 10x10 hint.
- Rewrite the header comment's fill paragraph: the fill is the reference's vertical gradient
  sampled from `desktop_fandom.png` at the ten pixels above, with the two edge columns sampled at
  (1458, 1238) and (1816, 1238); the boot2 pixels are the downscaled evidence. Record the
  deviations: the reference's 1px `#000000` outline and its ~12px total height are not drawn (the
  bar keeps the 10px canvas), and the edge columns are painted flat rather than row by row.
- `tests/test_desktoptheme_progressbar.py`: replace `FILL_FACE`/`FILL_LIGHT` with a ten-colour
  `FILL_ROWS` table and the two edge constants; `_assert_bar_pixels` builds the top/centre/bottom
  bands and the corner expectations from the table; `test_progressbar_colours` expects the parsed
  fill set of the track's three colours plus the eleven distinct fill colours. Keep the existing
  `TestProgressBarReference` (the boot2 track) for the three track colours and drop its two fill
  pixels; add a second reference class whose `REFERENCE` is `desktop_fandom.png`,
  `MAX_ROWS = 1250`, sampling the ten interior rows and the two edge columns and comparing each to
  the artwork's own parsed fill.
- `README.md`: the `widgets/bar_meter_horizontal.svg` sentence says a lavender-to-white vertical
  gradient fill instead of "a lavender fill".
- `docs/invariants.md`: the `widgets/bar_meter_horizontal.svg` guarantee ("draws the Platinum
  progress bar") is unchanged; no provenance exception is needed because every fill colour is
  reference-sampled.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/bar_meter_horizontal.svg`,
`tests/test_desktoptheme_progressbar.py`, `README.md`.

**Acceptance criteria.**
- The `bar-active` fill's ten rows are exactly the ten sampled `desktop_fandom.png` colours and the
  left/right edge columns are `#68688D`/`#50527F`, asserted slice by slice.
- A reference test re-derives all ten row colours and the two edge colours from
  `desktop_fandom.png` and skips when the Git LFS image is not materialized.
- `bar-inactive`'s track pixels and the 10x10 nine-slice contract (`hint-tile-center`,
  `hint-bar-size`) are unchanged.
- The header comment names `desktop_fandom.png` and the sampled pixels and no longer calls the
  fill a flat `#9B9BEA` face.
- `make check` is green.

### Mac OS 8.6 Platinum tab face: ground `widgets/tabbar.svg` in the System Profiler tabs (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktop-themes/org.macos8.desktop/widgets/tabbar.svg` paints every tab face
`#DDDDDD`, the same grey as the menu bar and the dialog body, so a Plasma tab (`TabBar`,
`TabButton`, the kickoff footer, the system-tray current-item and panel expanded applets) reads
as a bare outline on an identical background. The high-resolution lossless reference
`macos8.6-screenshots/desktop_fandom.png` (English retail 8.6, the "Apple System Profiler"
window) shows the Platinum tab face is one grey darker, `#CCCCCC`, with a `#DDDDDD` highlight
inside the `#000000` outline rather than the `#FFFFFF` the artwork paints. The SVG's provenance
comment claims "No screenshot reference exists for tabs", which this reference contradicts.

**Grounding.** In `desktop_fandom.png` the four System Profiler tabs run y=124..157 (a 2x
upscale of a 1280x721 screen, so 2 image pixels per logical pixel). Each tab's interior is
uniformly `#CCCCCC`: the 12x5 rectangles x=2056..2068 y=149..154 (inside "Applications"),
x=2200..2212 y=149..154 ("System Folders") and x=1920..1932 y=149..154 ("Extensions") are each
60/60 `#CCCCCC` (`tools/sample.py`). The 1px band just inside the top black outline is
`#DDDDDD` (rows 128..129 at x=2064), the outline `#000000` (rows 124..125), the tab-bar
background between tabs `#DDDDDD` (221,221,221). Only the solid face, highlight and outline
colours are taken from the reference; the 2x scale leaves the exact 1px bevel placement
unresolved, so the bevel keeps its current black/highlight/face geometry.

**Approach.**
- `theme/desktop-themes/org.macos8.desktop/widgets/tabbar.svg`: in all four `*-active-tab`
  prefixes change the face fill `#DDDDDD` to `#CCCCCC` and the raised-bevel highlight
  `#FFFFFF` to `#DDDDDD`; keep the `#000000` outline, the `#999999` shadow and the face-only
  open edge. Update the header comment to name `desktop_fandom.png` and the sampled rectangles
  and to drop the "No screenshot reference exists for tabs" claim.
- `tests/test_desktoptheme_tabbar.py`: set `FACE = "#CCCCCC"`, add `HIGHLIGHT = "#DDDDDD"`,
  and build `TOP_LEFT_BAND`/`BOTTOM_RIGHT_BAND` and the two fully-raised corners in
  `tab_corners` from `HIGHLIGHT`/`FACE` (the shared `svg_assertions.face_corners` table is
  hard-coded for the `#DDDDDD`/`#FFFFFF` button face, so the tab gets its own raised corner
  table, as the file's `band_rows`/`band_columns` helpers already do for the mixed corners).
  Replace `test_tabbar_colours`'s `assert_fill_palette(self, self.tree)` with an explicit
  `attribute_values(self.tree, "fill") == {"#000000", "#CCCCCC", "#DDDDDD", "#999999"}`,
  and update `test_tabbar_palette`'s expected raw strings to `#CCCCCC`, `#DDDDDD`, `#999999`,
  `#000000`. Add `TestTabBarReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE` = `desktop_fandom.png` and `MAX_ROWS = 160`, asserting `hex_colour(self.pixel(x, y))`
  is `FACE` for each of the three rectangles above.
- `tests/support/reference_image.py`: give `ReferenceScreenshotMixin` a `MAX_ROWS = None` class
  attribute and pass `max_rows=cls.MAX_ROWS` to `read_reference` in `setUpClass`, so the
  2560x1442 reference decodes only its first 160 rows (0.4s) instead of all of it (3.4s).
- `docs/invariants.md`: the desktop-themes row already names
  `tests/test_desktoptheme_tabbar.py::TestTabBar`; its guarantee ("draws the Platinum tab bar")
  is unchanged.

**Acceptance criteria.**
- Every `*-active-tab` centre and the face part of every slice is `#CCCCCC`, and every
  raised-bevel highlight is `#DDDDDD`; `test_tabbar_centres_are_the_face`,
  `test_tabbar_closed_edges_are_raised` and `test_tabbar_corners` pass.
- The new reference test re-derives `#CCCCCC` from the three `desktop_fandom.png` rectangles and
  passes; a face painted `#DDDDDD` fails it. The test skips, not fails, when the reference is
  not materialized (`skip_unless_materialized`).
- `tabbar.svg`'s comment no longer claims no screenshot reference exists and names the
  reference and the rectangles.
- `make check` exits 0.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/tabbar.svg`,
`tests/test_desktoptheme_tabbar.py`, `tests/support/reference_image.py`.

**Recorded deviation.** The reference tab is a trapezoid whose sides slant outward over the
full tab height; a KSvg nine-slice draws a fixed-corner rectangle, so the shape stays
rectangular. The Kvantum `tab` element (`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`)
keeps its own `#DDDDDD`/`#FFFFFF` raised face: it is a separate Qt-widget surface, not part of
this desktop-theme change.

### Mac OS 8.6 Platinum translucent applet background: ship `widgets/translucentbackground.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `BasicAppletContainer.qml` — the Plasma applet container the desktop containment uses for
applets placed on the desktop — picks its background from the applet's
`effectiveBackgroundHints`: the `TranslucentBackground` bit resolves to
`imagePath: "widgets/translucentbackground"`. The desktop theme ships no such file, so KSvg falls
back to the default theme's Breeze `translucentbackground.svgz`, a rounded translucent rectangle
that clashes with Platinum. Ship the Platinum body so those applet containers are Platinum too.

**Grounding.** `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/private/containmentlayoutmanager/BasicAppletContainer.qml`
chooses the path in `background.imagePath`: `effectiveBackgroundHints & TranslucentBackground` →
`widgets/translucentbackground`, else `& StandardBackground` → `widgets/background` (already
shipped), else `""`. The same item sets `prefix: blurEnabled ? "blurred" : ""`; `blurEnabled`
requires the `StandardBackground` bit, so a translucent-hint container reads the **unprefixed**
elements. The installed applets that set the bit are those with `PlasmaCore.Types.DefaultBackground`
(`= StandardBackground | TranslucentBackground`) — `org.kde.plasma.weather`, `org.kde.plasma.comic`
and `org.kde.plasma.systemmonitor` each set `Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground
| PlasmaCore.Types.ConfigurableBackground`, and `BasicAppletContainer` tests `TranslucentBackground`
first, so they take the translucent path. Mac OS 8.6 has no translucent applet surface: no reference
screenshot shows one and every Platinum body is opaque, so the KDE-required translucent-hint surface
takes the same opaque Platinum body as the standard hint. No new palette value: the file is a
byte-identical copy of `widgets/background.svg` (the Platinum body the standard hint already draws),
exactly as `solid/widgets/tooltip.svg` copies `widgets/tooltip.svg`.

**Approach.**
- Add `theme/desktop-themes/org.macos8.desktop/widgets/translucentbackground.svg`, byte-identical to
`theme/desktop-themes/org.macos8.desktop/widgets/background.svg` (no header change, so the copy test
compares bytes).
- `tests/support/desktoptheme_paths.py`: add `TRANSLUCENT_BACKGROUND_SVG = os.path.join(PACKAGE,
"widgets", "translucentbackground.svg")` beside `BACKGROUND_SVG`.
- `tests/test_desktoptheme.py`: import `TRANSLUCENT_BACKGROUND_SVG`, add
`("translucentbackground.svg", TRANSLUCENT_BACKGROUND_SVG, 16, 16)` to `SVG_CANVASES` (so the
registry, canvas, id and self-containment tests cover it) and
`os.path.join("widgets", "translucentbackground.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_background.py`: import `TRANSLUCENT_BACKGROUND_SVG` and add
`test_translucent_copy_is_identical` to `TestBackground`, opening `BACKGROUND_SVG` and
`TRANSLUCENT_BACKGROUND_SVG` in binary and asserting equal bytes (mirroring
`TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktop-themes `widgets/background.svg` row's guarantee to "…and
its `widgets/translucentbackground.svg` copy is byte-identical." The row already names
`TestBackground`, which holds the new test.
- `README.md`: in the `widgets/background.svg` sentence, add that a byte-identical copy ships at
`widgets/translucentbackground.svg`, where `BasicAppletContainer.qml` looks for a translucent-hint
applet container's background.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/translucentbackground.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_background.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `widgets/translucentbackground.svg` is byte-identical to `widgets/background.svg`, asserted by
`TestBackground::test_translucent_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 16x16 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (the README prose names the
file) and `tests/test_invariants.py`.
- Removing `widgets/translucentbackground.svg` makes `test_translucent_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer equals
the registry).

### Mac OS 8.6 grey menu body: ground `widgets/background.svg` in the open Apple menu (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktop-themes/org.macos8.desktop/widgets/background.svg` paints the body of every
`PlasmaComponents.Menu` (context menus and combo-box dropdowns), `Drawer`, `Popup` and planar
applet container as a flat `#FFFFFF` face, and its comment justifies that with
`[Colors:View] BackgroundNormal`. But the open Apple menu in the retail screenshot
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the same image
`tests/test_colorscheme_reference.py::TestReferenceAnchors` samples the menu-bar face from — has a
flat `#DDDDDD` body, the Platinum face, not white. Ship the reference's grey menu body and pin it
to the reference pixels.

**Reference.** The Apple menu is open in `desktop_archiveorg8.6hd.png`, dropping from the top-left
(its body spans roughly x=6..160, y=16..355). The menu's empty right margin, clear of item text and
icons, is flat `#DDDDDD`: (150, 60) = (221, 221, 221) and (150, 200) = (221, 221, 221). The Finder
window's content in the same image is white at (470, 300) — already the `[Colors:View]` anchor —
so the menu body is a distinct grey, not the View background. (The image is stored with Git LFS,
so a clone without it must skip this test, as `test_colorscheme_reference` does.)

**Approach.**
- `widgets/background.svg`: change the face — the centre tile and the interiors of the four edge
tiles — from `#FFFFFF` to `#DDDDDD`, keeping the 1px `#000000` outline and the 3px/10px nine-slice
contract. Rewrite the header comment's face paragraph: the body is the Platinum grey `#DDDDDD`
sampled from the open Apple menu in `desktop_archiveorg8.6hd.png`, not `[Colors:View]`; drop the
"flat white" wording.
- `tests/test_desktoptheme_background.py`: `test_background_pixels` passes `FACE` instead of
`WHITE` to `assert_face_bevel`; `test_background_colours` expects `{BLACK, FACE}`; import `FACE`
from `support.platinum_palette` (it is already `#DDDDDD`). Add a reference case, mirroring the
`ReferenceScreenshotMixin` use in `tests/test_desktoptheme_panel.py` and
`tests/test_desktoptheme_menubaritem.py`, whose `REFERENCE` is
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` and which compares `pixel(150, 60)` and
`pixel(150, 200)` to the artwork's own rendered face, skipping when the LFS image is not
materialized.
- `README.md`: the `widgets/background.svg` sentence at the desktop-theme paragraph says the
Platinum grey menu body instead of "the flat white Platinum body".
- `docs/invariants.md`: the desktop-themes `background.svg` row's guarantee ("draws the Platinum
menu body") still holds; no provenance exception is needed now that the face is reference-sampled.

**Acceptance criteria.**
- `background.svg`'s parsed fill set is exactly `{#000000, #DDDDDD}`, its 10x10 centre and four
edge tiles are `#DDDDDD`, and its outline is 1px `#000000` with no bevel.
- The new reference test compares the artwork's own rendered face to the two `#DDDDDD` pixels
from `desktop_archiveorg8.6hd.png` and skips when the image is missing, exactly as the other
reference-screenshot cases do.
- `background.svg`'s comment names the reference and the sampled pixels and no longer derives the
face from `[Colors:View]`.
- README.md no longer calls the menu body white.
- `make check` is green.

### Fidelity gate for the rendered window's title-bar boxes (close, zoom, collapse) (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate byte-compares the title-bar's middle strip and the
side and bottom borders, but not the three Platinum title-bar boxes, so a regression in how
Aurorae places or sizes them renders unnoticed. Extend `tests/test_render_surface.py::TestRender`
to byte-compare the close, zoom and collapse box regions of the render against the reference
screenshots.

**Grounding (verified 2026-10-18 with `tools/render_surface.py --settle 3` on this tree and
`tools/png`).** The 320x240 render puts the window at the capture's origin, and each box region is
byte-identical to the reference (0 differing pixels):
- close box: render `(4,4,13,13)` vs `aboutsystem_betawiki.png` `(11,29,13,13)`;
- collapse box: render `(303,4,13,13)` vs `aboutsystem_betawiki.png` `(343,29,13,13)`;
- zoom box: render `(282,4,21,13)` vs `systemprofiler_betawiki.png` `(776,26,21,13)`.
The close and collapse boxes use `aboutsystem_betawiki.png` (its collapse box at x=343); the zoom
box uses `systemprofiler_betawiki.png`, the only reference whose window shows a zoom box
(`aboutsystem`'s window cannot be zoomed, as `tests/support/aurorae_fixtures.py` records), with
`ZOOM_BOX_X = 5` matching the 21px gap-plus-box canvas. The title-bar strip gate deliberately
starts at x=30 to clear the close box, so these three regions are currently ungated at render
time.

**Approach.**
- `tests/test_render_surface.py`: beside the existing border crops, add
  `PROFILER_REFERENCE = str(repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png")`
  and the six crop tuples `CLOSE_CANDIDATE`/`CLOSE_REFERENCE`,
  `COLLAPSE_CANDIDATE`/`COLLAPSE_REFERENCE`, `ZOOM_CANDIDATE`/`ZOOM_REFERENCE` with the values
  above.
- Generalize `TestRender.assert_strip_pixels_match` to take a `reference_path=REFERENCE`
  argument and load that image with `support.reference_image.read_reference` +
  `skip_unless_materialized` (so the zoom test skips when the profiler LFS image is absent), then
  add `test_title_bar_boxes_match_the_reference` iterating the three
  `(candidate_crop, reference_crop, reference_path)` triples. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row `| The rendered window's title-bar boxes are
  byte-identical to the same regions of the reference screenshots. |
  tests/test_render_surface.py::TestRender::test_title_bar_boxes_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph, name the box regions beside the title-bar and
  border strips.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `TestRender.test_title_bar_boxes_match_the_reference` passes where the render tools and both
  references are materialized, and skips when either reference is an unmaterialized LFS pointer.
- Each region is pinned to zero differing pixels: shifting any crop by one pixel, or changing the
  box art or the Aurorae box geometry in `org.macos8.desktoprc`, makes the test fail.
- `docs/invariants.md` resolves the new `tooling` row, and `make check` is green.

### Mac OS 8.6 opaque menu bar: ship the `solid/widgets/panel-background.svg` copy (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `Panel.qml` draws an opaque panel from `solid/widgets/panel-background`, but the
desktop theme ships only `widgets/panel-background.svg`, so the menu bar loses its Platinum bevel
whenever the panel is opaque. Ship the solid copy so the opaque menu bar is Platinum too.

**Grounding.** `/usr/share/plasma/shells/org.kde.plasma.desktop/contents/views/Panel.qml` gives
its two opaque items (`opaqueItem`, `floatingOpaqueItem`) `imagePath:
"solid/widgets/panel-background"`, while the two translucent items use
`widgets/panel-background`. Plasma 6's default panel opacity mode is Adaptive
(`PanelConfiguration.qml`'s opacity combo defaults to index 0), and in Adaptive mode a window
touching the panel (`screenCovered`) drives `panelOpacity` to 1, which hides the translucent item
and shows the opaque one; choosing the Opaque mode does the same always. KSvg does not map
`solid/widgets/panel-background` onto `widgets/panel-background` — the same behaviour
`tests/test_desktoptheme_tooltip.py::TestTooltip::test_solid_copy_is_identical` records for
`PlasmaComponents.ToolTip`'s hardcoded `solid/widgets/tooltip` — so today the opaque menu bar
resolves to the default theme's Breeze `solid/widgets/panel-background.svgz` (the default theme
ships a solid copy; ours ships only `solid/widgets/tooltip.svg`). `widgets/panel-background.svg`
is already fully opaque (its fills are the solid `#FFFFFF`/`#DDDDDD`/`#999999`/`#000000` with no
alpha), so a byte-identical copy is the correct solid variant. Out of scope: a
`solid/widgets/background.svg` (the default theme ships one, but no installed QML requests it —
`DialogBackground.qml` hardcodes `widgets/background` and `libPlasmaQuick` carries no `solid/`
path), so it is not shipped here.

**Approach.**
- Add `theme/desktop-themes/org.macos8.desktop/solid/widgets/panel-background.svg`, byte-identical
to `widgets/panel-background.svg` (no header change, so the copy test compares bytes), matching
the existing `solid/widgets/tooltip.svg`.
- `tests/support/desktoptheme_paths.py`: add `SOLID_PANEL_SVG = os.path.join(PACKAGE, "solid",
"widgets", "panel-background.svg")` beside `SOLID_TOOLTIP_SVG`.
- `tests/test_desktoptheme.py`: import `SOLID_PANEL_SVG`, add `("solid/widgets/panel-background.svg",
SOLID_PANEL_SVG, 12, 22)` to `SVG_CANVASES` (so the registry, canvas, id and self-containment
tests cover it), add `"solid/widgets/panel-background.svg": ("",)` to `ORIGIN_STATES` (its
unprefixed margin rects sit at the origin of the canvas grown to hold the 22px-tall `north-`
state, like `panel-background.svg`), and add
`os.path.join("solid", "widgets", "panel-background.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_panel.py`: import `SOLID_PANEL_SVG` and add
`test_solid_copy_is_identical` to `TestPanelBackground`, opening `PANEL_SVG` and `SOLID_PANEL_SVG`
in binary and asserting equal bytes (mirroring `TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktop-themes `widgets/panel-background.svg` row's guarantee
to "`widgets/panel-background.svg` draws the menu bar, including its top-panel north state, and
its `solid/` copy is byte-identical." The row already names `TestPanelBackground`, which holds
the new test.
- `README.md`: in the `widgets/panel-background.svg` sentence, add that a byte-identical copy
ships at `solid/widgets/panel-background.svg`, where `Panel.qml` looks for an opaque panel's
background.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/solid/widgets/panel-background.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_panel.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `solid/widgets/panel-background.svg` is byte-identical to `widgets/panel-background.svg`,
asserted by `TestPanelBackground::test_solid_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 12x22 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (its `*/*.svg` glob does not
reach the two-level `solid/` path, and the README prose names the file) and
`tests/test_invariants.py`.
- Removing `solid/widgets/panel-background.svg` makes `test_solid_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer
equals the registry).

### Mac OS 8.6 splash: draw the reference's full "Mac OS 8.6" wordmark (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The startup splash's wordmark draws the truncated label `Mac OS`;
`macos8.6-screenshots/boot2_betawiki.png` shows the full `Mac OS 8.6`. Draw the full label so the
login splash matches the reference.

**Grounding.** In `macos8.6-screenshots/boot2_betawiki.png` (240x180, the retail 8.6 boot screen
whose `8.6` is legible) the wordmark's black glyphs occupy `x=89..150, y=71..83` — 62 of the 80
columns of the panel's white face (`x=80..159, y=39..88`, re-derived by
`tests/test_splash_reference.py::TestSplashGeometry::test_grid_geometry`). `Splash.qml`'s
`wordmark` Text draws `text: "Mac OS"`, roughly 38 columns centred on the panel, leaving the
reference's leftmost (`x=89..~100`) and rightmost (`x=~140..150`) glyph columns blank. The
original splash plan (PLANS.md `## Done`, "Mac OS 8.6 Platinum startup splash") and
`tests/test_splash_qml.py::test_wordmark_shows_the_reference_label_at_its_grid_size` both call
`Mac OS` the reference label, which the thumbnail does not support.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`: change the `wordmark`
  `Text`'s `text` from `"Mac OS"` to `"Mac OS 8.6"`. Leave its `y: 71 * root.unit`,
  `anchors.horizontalCenter: panel.horizontalCenter` and `font.pixelSize: 12 * root.unit`
  unchanged: the 12-row band and the panel centring already match the reference.
- `tests/test_splash_qml.py`: change `test_wordmark_shows_the_reference_label_at_its_grid_size`
  to require `text: "Mac OS 8.6"` and correct its comment, which calls `Mac OS` the reference
  label.
- `tests/test_splash_reference.py`: add `test_wordmark_spans_the_reference_band` to
  `TestSplashGeometry`. Derive the wordmark's black-pixel bounding box from the thumbnail (dark
  pixels with all three channels below a fixed threshold in the band `y=68..86`, `x=84..156`,
  which excludes the logo stem above `y=68`) and assert its width is at least 55 of the face's 80
  columns, so a reference whose label is no wider than `Mac OS` fails instead of silently passing.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`,
`tests/test_splash_qml.py`, `tests/test_splash_reference.py`.

**Acceptance criteria.**
- The `wordmark` Text's `text` is exactly `"Mac OS 8.6"`; any other string fails
  `test_wordmark_shows_the_reference_label_at_its_grid_size`.
- `test_wordmark_spans_the_reference_band` re-derives the reference wordmark bbox on
  `boot2_betawiki.png` and passes; a label that spans fewer than 55 face columns fails it.
- `make check` exits 0.
- Recorded deviation (not fixed here): the reference wordmark is a high-contrast serif (Apple's
  Garamond-family wordmark) while the QML draws the system UI font, so glyph shapes still differ;
  shipping a typeface is out of scope and the reference set has no larger boot capture to ground
  one.

### Mac OS 8.6 Platinum full-Trash icon (`32x32/places/user-trash-full.svg`) for the icon theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** KDE asks for the icon name `user-trash-full` whenever the Trash holds something
(`/usr/share/plasma/plasmoids/org.kde.plasma.trash/contents/ui/main.qml`:
`hasContents ? "user-trash-full" : "user-trash"`; Dolphin's Places panel and the desktop do the
same). The icon theme ships only `theme/icons/org.macos8.desktop/32x32/places/user-trash.svg`, so
the non-empty state falls through `Inherits=breeze` to Breeze's flat modern `user-trash-full.svg`
— the desktop's Trash visibly stops being Platinum the moment it holds a file. Ship our own
full-Trash art so the non-empty state stays Platinum.

**Approach.**
- Add `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg`: our own 32x32 Platinum
drawing, the same can as `user-trash.svg` (lid, body outline/face, the two grey/white rib pairs),
with the handle replaced by a `#FFFFFF` paper sheet outlined in `#000000` rising above the lid, so
the can reads as full. Recommended drawing, in document order (the implementer may adjust the
paper shape, but the constraints below hold):
  ```xml
  <path d="M12 2 l3 2 l3 -2 l1 7 h-8 Z" fill="#000000"/>
  <path d="M13 3 l2 1 l2 -1 l1 5 h-6 Z" fill="#FFFFFF"/>
  <rect x="6" y="8" width="20" height="5" fill="#000000"/>
  <rect x="7" y="9" width="18" height="4" fill="#DDDDDD"/>
  <rect x="7" y="9" width="18" height="1" fill="#FFFFFF"/>
  <rect x="7" y="12" width="18" height="1" fill="#999999"/>
  <path d="M9 13 h14 l-2 16 H11 Z" fill="#000000"/>
  <path d="M10 14 h12 l-2 14 H12 Z" fill="#DDDDDD"/>
  <rect x="13" y="16" width="1" height="10" fill="#999999"/>
  <rect x="14" y="16" width="1" height="10" fill="#FFFFFF"/>
  <rect x="17" y="16" width="1" height="10" fill="#999999"/>
  <rect x="18" y="16" width="1" height="10" fill="#FFFFFF"/>
  ```
- Register the file in `tests/test_icon_theme.py`: add its package-relative path to `SHIPPED_ICONS`
and its exact drawing-element tuple (via the module's `_shape` helper) to `ICON_SHAPES`. The
existing `TestIndex`/`TestIcons`/`TestIconGeometry` tests then cover the new icon: it must be a
32x32 square SVG whose fills are a subset of `PLATINUM_FILLS`, with no scripts, `<style>`,
external references or duplicate ids, and every drawing element must match the pinned tuple.
`TestInstall.INSTALLED_FILES` is derived from `SHIPPED_ICONS`, so the install lifecycle covers it
with no further edit.
- `32x32/places` is already a declared directory in `theme/icons/org.macos8.desktop/index.theme`,
so the metadata does not change and no new size directory is added.
- `README.md`: in the icon-theme sentence, change "the desktop's hard-disk, folder, document and
Trash icons" to name the full-Trash art as well (e.g. "…document, Trash and full-Trash icons").
- `docs/invariants.md`: the `icons` section's "ships exactly the tracked icons" row already names
`tests/test_icon_theme.py::TestIndex`, which covers the new file; no text change.

**Files touched.** `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg` (new),
`tests/test_icon_theme.py`, `README.md`.

**Acceptance criteria.**
- `tests/test_icon_theme.py`'s `SHIPPED_ICONS` and `ICON_SHAPES` both list the new icon, and
`test_the_geometry_registry_covers_every_shipped_icon` passes; changing one drawing element in the
SVG fails `TestIconGeometry::test_each_icon_draws_its_pinned_artwork`.
- Deleting the SVG, or removing it from either registry, fails `make check`.
- `make check` is green, and `make install XDG_DATA_HOME=<tmp>` installs the new icon
(`TestInstall` covers the installed file set).

### Record-checker mutation harness: manufacture the malformed inputs from the shipped registers so a silent accept or drop is observable (planned 2026-10-18 by the steward role; from the recurring `no-observability` validation gap in thirteen Fixed entries) — done 2026-10-18

**Goal.** Twelve Fixed entries share one mechanism: a record checker (`tests/invariants.py`'s
register parser and reference resolver, `tests/placeholders.py`'s marker scanner) accepted or
silently dropped malformed input that the shipped records never contain, so no test or real run
could surface the bug — each was found by reading the checker and fixed with one hand-written case.
Add a mutation harness that manufactures each malformed shape from the shipped registers
(`docs/invariants.md`, `PLACEHOLDERS.md` and the shipped placeholder markers) and asserts the
checker reports it, so the acceptance boundary is exercised by data and the next silent accept or
drop fails a test instead of waiting for a reader.

**From (the `no-observability` Fixed entries).**
- `tests/invariants.py` register checker, ten entries (all fixed 2026-10-18): accepts a class whose
locally defined base only looks like a test case; accepts a register reference that escapes the
repository; accepts a method reference into a class that is not a test case; accepts a register
reference to a class with no tests; accepts a register reference to a non-test method; accepts a
register reference with a segment after the method; accepts a register reference ending in `::`,
pinning a guarantee to no test; drops a row that does not split into three cells; drops a row whose
Test cell has no backticked reference; drops a row whose cell contains an escaped pipe.
- `tests/placeholders.py` marker scanner, two entries (both fixed 2026-10-18): ignores
`PLACEHOLDER:` markers in the theme's `.kvconfig` file; ignores them in the theme's `.js` and
`.desktoprc` files.
- The thirteenth `no-observability` entry, "Palette anchors are not re-derivable from the reference
screenshots" (fixed 2026-10-08), is a different mechanism — a hard-coded anchor assertion — and is
retired by the register's provenance-exception row and `TestProvenanceNote`, not by this harness.

**Approach.**
- Add `tests/support/checker_mutations.py`: one named mutation per rejection shape the two checkers
must catch, each a transform of a copy of the real register or of a scratch theme root plus the
diagnostic substring the checker must raise. Seed the table with the twelve shapes above. The
reference mutations point the register's first row at `tests/support/mutant_module.py`, a shipped
fixture holding the class shapes the shipped tests never define, and at a real test case in
`tests/test_checker_mutations.py`; the placeholder mutations name real shipped theme files, so
every path they cite exists in the tree.
- Add `tests/test_checker_mutations.py`: copy `docs/invariants.md` and the placeholder register into
a scratch root, apply each mutation, run the checker, and assert the named diagnostic; a mutation
the checker does not reject fails. Exercise the `.js`/`.desktoprc`/`.kvconfig` cases by writing one
marked file per text format the theme ships into the scratch theme root.
- Give each checker a `REJECTION_SHAPES` list naming the boundaries it must reject (the shapes its
`cross_check` docstring already enumerates), and add a test asserting the list and the mutation
table name the same rejection boundaries, so a boundary named in one without the other fails.

**Files touched.** `tests/support/checker_mutations.py` (new), `tests/test_checker_mutations.py`
(new), `tests/support/mutant_module.py` (new), `tests/invariants.py`, `tests/placeholders.py`
(the `REJECTION_SHAPES` lists).

**Acceptance criteria.**
- Every shape above is a mutation entry, and applying it makes the matching checker raise the named
diagnostic; a scratch run with one mutation's expected diagnostic removed demonstrates the harness
fails.
- `REJECTION_SHAPES` for both checkers is covered by the mutation table; removing a table row fails
the guard test.
- `make check` is green, with the existing hand-written rejection tests still passing.

**Implementation note (2026-10-18).** The escaped-pipe and the three placeholder-format
shapes are acceptance boundaries, not rejections: the checker must keep the row or find the
marker, so the harness pins them with an `observe` assertion instead of a diagnostic. The
`REJECTION_SHAPES` lists hold the nine invariant rejections and the three placeholder
rejections; the guard test asserts each list equals the rejection mutation names, so a name
or a mutation added without the other fails. It is a sync check between two hand-maintained
lists, not a detector of a new rejection branch added to a checker on its own.

### Fidelity gate for the rendered window frame's side and bottom borders (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate compares only the title-bar strip
(`TestRender::test_title_bar_matches_the_reference`). The frame's six-pixel left, right and
bottom borders are still pinned only by the SVG unit tests (`tests/test_aurorae_frame.py`) and the
rc test (`tests/test_aurorae_rc.py`), so nothing checks that KWin paints them at the reference
geometry. Extend the same render-and-byte-compare gate to those three border strips. It reuses
the one render `TestRender.setUpClass` already makes; no second render runs.

**Grounding (sampled 2026-10-18 with `tools/png.read_png` + `pixel_at` on a render from
`tools/render_surface.py --settle 3`).** The 320x240 render puts the window at (0,0): a 6px left
border at x=0..5, a 6px right border at x=314..319 and a 6px bottom border at y=234..239.
`aboutsystem_betawiki.png`'s window has its left outline at x=7 and top outline at y=25, so its
left border is x=7..12, its right border x=354..359 and its bottom border y=419..424. The
reference window is taller than the render, so the side strips compare only the straight part
between the title bar and the bottom border (212 rows), and the bottom strip the horizontal
border between the two corners (308 columns). Byte-exact comparisons:
- left: candidate `(0, 22, 6, 212)` vs reference `(7, 47, 6, 212)` — 0 differing of 1272;
- right: candidate `(314, 22, 6, 212)` vs reference `(354, 47, 6, 212)` — 0 differing of 1272;
- bottom: candidate `(6, 234, 308, 6)` vs reference `(13, 419, 308, 6)` — 0 differing of 1848.

**Approach.**
- `tests/test_render_surface.py`: keep `CANDIDATE_CROP`/`REFERENCE_CROP` for the title bar and add
  six module constants beside them — `LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)`,
  `LEFT_BORDER_REFERENCE = (7, 47, 6, 212)`, `RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)`,
  `RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)`, `BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)`,
  `BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)`, each with its grounding row above as its comment.
  Extract the body of `test_title_bar_matches_the_reference` (the `read_reference` +
  `skip_unless_materialized` guard and the `process_runner.run` of the real `FIDELITY` CLI with
  `--candidate-crop`/`--crop`) into a helper method
  `assert_strip_matches(self, candidate_crop, reference_crop)`; the title-bar test keeps its name
  and calls the helper with its two constants. Add
  `test_frame_borders_match_the_reference`, which loops the three `(candidate, reference)` border
  pairs and calls the helper under `self.subTest`, so a failure names the strip.
- `docs/invariants.md`: add a second `tooling` row
  `| The rendered window's side and bottom border strips are byte-identical to the same strips of
  the reference screenshot. | tests/test_render_surface.py::TestRender::test_frame_borders_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph's `make check` sentence, extend the compared
  region from the title-bar strip to the title bar and the side and bottom borders.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `make check` passes. `test_frame_borders_match_the_reference` runs (does not skip) where the
  render tools are on `PATH` and the LFS reference is materialized, and skips when the reference
  is an unmaterialized pointer; the existing title-bar test still passes.
- Each strip reports `differing pixels: 0 / 1272` (left and right) and `0 / 1848` (bottom).
- Changing `BorderLeft`, `BorderRight` or `BorderBottom` in
  `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`, or the border colours in
  `decoration.svg`, makes a named test fail.
- `tests/test_invariants.py` still resolves every register row against the repository.

### Fidelity gate for the rendered window decoration: byte-compare the title-bar strip to `aboutsystem_betawiki.png` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `tools/render_surface.py` renders the themed window in a headless KWin session and
`tools/fidelity.py` compares a rendered PNG against a reference screenshot, but no reference crop
or threshold for a rendered surface is chosen, so nothing checks that the assembled theme renders
like the reference. This is the later plan the render entry's "Out of scope" names. Choose the
first such crop — the window title bar — add a `--candidate-crop` option so the candidate can be
cropped to the reference crop's size, and pin the whole pipeline (install, KWin, Aurorae, render)
with a `make check` test that byte-compares the strip.

**Grounding (sampled 2026-10-18 with `tools/png.read_png` + `pixel_at`).** A 320x240 render
(`tools/render_surface.py --settle 3`, `org.kde.plasma.calculator`) puts the window's title bar at
the top of the capture: row 0 is the `#000000` top outline, rows 1..20 are the Platinum pinstripes,
row 21 is the `#000000` title-bar bottom outline. `aboutsystem_betawiki.png` (retail) has the same
window chrome one row per row at `y=25..46`: row 25 the top outline, rows 26..45 the pinstripes,
row 46 the bottom outline. So the render's rows `0..21` map to the reference's rows `25..46`.
The pinstripes are horizontal, so the x offset does not matter as long as both crops stay clear of
the close box and the centred title text: the reference's close box face is x=11..22 with its
`#FFFFFF` highlight at x=23, and the title text is centred near x=180. The strip `x=30..109,
y=0..21` of the render is byte-identical to `x=30..109, y=25..46` of the reference (0 differing
pixels of 1760, max channel delta 0); the same render compared to `y=24..45` or `y=26..47` fails,
so the one-row alignment is pinned by the test.

**Approach.**
- `tools/fidelity.py`: add `--candidate-crop X,Y,W,H` (`type=_parse_crop`,
  `metavar="X,Y,W,H"`, help "crop the candidate to this region before comparing"), apply it as
  `candidate = crop(candidate, *args.candidate_crop)` before `compare` (beside the existing
  `reference = crop(reference, *args.crop)`), and print `candidate crop: X,Y,W,H` when set,
  beside the existing `reference crop:` line. Update the module docstring's usage line to
  `[--candidate-crop X,Y,W,H]`. A run without the option is byte-for-byte unchanged in
  behaviour and output.
- `tests/test_fidelity_cli.py`: cover the option in `TestCli`, mirroring the existing `--crop`
  tests: `_write_padded_surface_pair` returns a 2x2 surface and a 4x4 padded image that embeds it
  at (1,1), so pass the padded image as candidate and the surface as reference with
  `--candidate-crop 1,1,2,2` and assert it passes; the `candidate crop:` rectangle is echoed
  only when the option is given; a malformed rectangle (`1,2,3`) is a usage error naming
  `--candidate-crop`; and a rectangle outside the candidate is a read error from `crop()`.
- `tests/test_render_surface.py`: add module constants beside `SCRIPT` — `FIDELITY =
  str(repo_root.ROOT / "tools" / "fidelity.py")`, `REFERENCE =
  str(repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png")`,
  `CANDIDATE_CROP = (30, 0, 80, 22)` and `REFERENCE_CROP = (30, 25, 80, 22)` — and a
  `test_title_bar_matches_the_reference` method to `TestRender`. It loads `REFERENCE` with
  `support.reference_image.read_reference` + `skip_unless_materialized` (imported beside the
  other `support` imports, so it skips where the LFS image is absent, like the other reference
  tests), then runs the real CLI `[sys.executable, FIDELITY, cls.output, REFERENCE,
  "--candidate-crop", "30,0,80,22", "--crop", "30,25,80,22"]` through `process_runner` and
  asserts exit 0 and `differing pixels: 0 / 1760` in stdout. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row
  `| The rendered window's title-bar strip is byte-identical to the same strip of the reference
  screenshot. | tests/test_render_surface.py::TestRender::test_title_bar_matches_the_reference |
  none |`.
- `README.md`: in the Fidelity checking paragraph, replace the closing sentence "no reference
  crop or threshold for a rendered surface is chosen yet" with the chosen crop: `make check`
  renders the window (`make render`) and byte-compares its title-bar strip at candidate
  `30,0,80,22` against reference `30,25,80,22` of `aboutsystem_betawiki.png`, naming
  `--candidate-crop`.

**Files touched.** `tools/fidelity.py`, `tests/test_fidelity_cli.py`, `tests/test_render_surface.py`,
`docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `python3 tools/fidelity.py <render.png> macos8.6-screenshots/aboutsystem_betawiki.png
  --candidate-crop 30,0,80,22 --crop 30,25,80,22` exits 0 and prints `differing pixels: 0 /
  1760`; without `--candidate-crop` the run still fails on the size mismatch, and a run with
  neither option is unchanged.
- `TestRender.test_title_bar_matches_the_reference` passes where the render tools and the
  materialized reference are present, and skips when the reference is an unmaterialized LFS
  pointer. Changing the Aurorae pinstripe colours, the title-bar height, or the close-box width
  (so the close box reaches x=30) makes it fail.
- The new `--candidate-crop` tests in `tests/test_fidelity_cli.py` pass, and the existing
  `--crop` tests still pass unchanged.
- `docs/invariants.md` resolves the new tooling row, and `make check` is green.

### Mac OS 8.6 Platinum desktop icon action buttons (`widgets/action-overlays.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/action-overlays.svg` so the desktop containment's folder-icon action buttons draw Platinum add/open/remove buttons instead of inheriting Breeze's. The theme ships no `widgets/action-overlays`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last widget name the default session's applets reference and the theme does not ship: the layout's kicker, appmenu, systemtray, digitalclock, windowlist and desktopcontainment reference every other widget name the theme ships. Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README/register lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemActionButton.qml` is an `SvgItem` whose `svg` is `KSvg.Svg { imagePath: "widgets/action-overlays"; multipleImages: true; size: "16x16" }`; it sets `elementId: element + "-normal"`, switching to `element + "-hover"` while the pointer is over it and `element + "-pressed"` while down. Its width and height are `Kirigami.Units.iconSizes` chosen from `Plasmoid.configuration.iconSize` (small 16, smallMedium 22, medium 32, large 48), so the 16x16 art scales.
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemDelegate.qml` instantiates it with `element: model.selected ? "remove" : "add"` (the selection toggle) and `element: "open"` (the folder-popup button); both appear on hover over a desktop icon in the layout the global theme applies. The default theme's `widgets/action-overlays.svg` ships the plain ids `add-`/`open-`/`remove-` plus `base`, and no size-prefixed ids, so the consumer resolves the plain ids.
- `main.qml` sets `imagePath: "widgets/toolbox"` on an `Svg` it never draws, and no installed desktop theme ships a `toolbox.svgz`; the toolbox is dead code, not a surface to style.

**Provenance.** No Mac OS 8.6 screenshot in the reference set shows a hover action button, so the shape and its three states are KDE-required; the fills reuse the grounded Platinum faces the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face). No new palette constant is introduced.

**Approach.**
- New `theme/desktop-themes/org.macos8.desktop/widgets/action-overlays.svg`, a 16x16 canvas with nine groups, ids `add-normal`, `add-hover`, `add-pressed`, `open-normal`, `open-hover`, `open-pressed`, `remove-normal`, `remove-hover`, `remove-pressed` (the plain ids the consumer resolves):
  - each group opens with the invisible `0,0,16,16` `fill="none"` bounding rect, then the `actionbutton.svg` circle recipe at (8,8): a `#000000` r=7 outline circle, the two bevel half-discs of radius 6 split on the top-right to bottom-left diagonal, and the `#DDDDDD` r=5 face circle;
  - `normal` and `hover` keep the raised bevel (`#FFFFFF` top-left half, `#999999` bottom-right half) and `pressed` swaps it; the `hover` face is `#FFFFFF` (a lit Platinum button), the `normal` and `pressed` face `#DDDDDD`;
  - a `#000000` glyph over the face: `add` a plus, `remove` a minus (each a stroked path with `fill="none"`), `open` a right-pointing filled triangle, sized to fit inside the r=5 face.
- `tests/support/desktoptheme_paths.py`: add `ACTION_OVERLAYS_SVG = os.path.join(PACKAGE, "widgets", "action-overlays.svg")`.
- New `tests/test_desktoptheme_actionoverlays.py`, modelled on `tests/test_desktoptheme_actionbutton.py` (extends `SvgCase`): `TestActionOverlays` pins the nine ids (`assert_ids_present`), the parsed fill set (`PLATINUM_FILLS | {"none"}`), the stroke set (`{"#000000"}`), `assert_no_script_elements`, each group's bounds rect, each state's circle geometry and bevel order, and each kind's glyph path (`d`, `fill`, `stroke`, `stroke-width`).
- `tests/test_desktoptheme.py`: add `("action-overlays.svg", ACTION_OVERLAYS_SVG, 16, 16)` to `SVG_CANVASES` (and a clause about it to the canvas comment) and `os.path.join("widgets", "action-overlays.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-themes row `widgets/action-overlays.svg` draws the Platinum desktop icon action buttons. | `tests/test_desktoptheme_actionoverlays.py::TestActionOverlays` | none.
- `README.md`: add `widgets/action-overlays.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/action-overlays.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionoverlays.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `action-overlays.svg` parses with a 16x16 root canvas; the nine element ids are present and unique; every fill is in `PLATINUM_FILLS | {"none"}` and every stroke `#000000`.
- Every group carries the `0,0,16,16` invisible bounds rect; `normal`/`hover` paint the white-top-left/grey-bottom-right bevel and `pressed` the swapped one; the `hover` face is `#FFFFFF`, the `normal`/`pressed` face `#DDDDDD`; each kind's glyph is pinned by its `d` and its stroke/fill attributes.
- `make install` copies the SVG into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), `test_registry_covers_every_shipped_svg` and the README backtick test pass, and `docs/invariants.md` resolves the new row's test.
- `make check` is green.

### Mac OS 8.6 Platinum round action button (`widgets/actionbutton.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/actionbutton.svg` so `PlasmaComponents.RoundButton` and `PlasmaComponents.Dial` draw a Platinum circle instead of inheriting Breeze's blue one. The theme ships no `widgets/actionbutton`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last of the `actionbutton`/`busy`/`switch` surfaces the done plans name (`busy` and `switch` are done). Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RoundButton.qml` reads `imagePath: "widgets/actionbutton"` in one `KSvg.Svg`, draws element `pressed` while down/checked else `normal` (`buttonItem`), and overlays `Private.RoundShadow` with states `hidden`/`hover`/`focus`/`shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Dial.qml` reads `imagePath: "widgets/actionbutton"`, element `pressed` while pressed else `normal`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/private/RoundShadow.qml` reads `imagePath: "widgets/actionbutton"` and draws element `hover`, `focus` and (default state) `shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RadioIndicator.qml` uses the older combination: `imagePath: "widgets/actionbutton"`, element `normal`, over `widgets/checkmarks`.
- Breeze's `actionbutton.svg` (the default theme) ships elements `normal`, `pressed`, `hover`, `focus` and no `shadow` element (verified by decoding `/usr/share/plasma/desktoptheme/default/widgets/actionbutton.svgz`); a missing `shadow` draws nothing, so the theme keeps Breeze's behaviour there. No shipped plasmoid uses `RoundButton`/`Dial`/`RoundShadow`, so this surface is not visible in the default session; it completes the widget set for third-party Plasma widgets.

**Provenance.** Mac OS 8.6 draws no round button, so the shape and its hover/focus rings are KDE-required; the fills reuse the grounded Platinum face and bevel the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face), and the focus ring reuses `button.svg`'s 1px `#000000` ring treatment. State this in the file's header comment.

**Approach.**
- New `theme/desktop-themes/org.macos8.desktop/widgets/actionbutton.svg`, a 36x36 canvas with four `<g>` elements, each opening with an invisible 36x36 bounding rect, so `KSvg` scales all four by the same bounds:
  - `normal` (raised): a filled `#000000` circle r=17 (outline), then a `#FFFFFF` half-disc path (top-left half, r=16) and a `#999999` half-disc path (bottom-right half, r=16) painting the 1px bevel, then a filled `#DDDDDD` circle r=15 (face). Each half-disc is one `M`/`A`/`Z` path, so `path_arcs` reads one 180-degree arc.
  - `pressed` (sunken): the same circles with the bevel halves swapped — `#999999` top-left, `#FFFFFF` bottom-right.
  - `hover` and `focus`: a 1px `#000000` ring in the outermost pixel, just outside the r=17 outline, drawn as one donut path — a full r=18 circle and a full r=17 circle wound the other way, so the nonzero fill rule leaves the interior transparent and the underlying `normal` art shows through.
  - no `shadow` element (Breeze ships none).
- `tests/support/desktoptheme_paths.py`: add `ACTIONBUTTON_SVG = os.path.join(PACKAGE, "widgets", "actionbutton.svg")`.
- New `tests/test_desktoptheme_actionbutton.py`, modelled on `tests/test_desktoptheme_radiobutton.py` (circles) and `tests/test_desktoptheme_busywidget.py` (arcs):
  - `TestActionButton(SvgCase, unittest.TestCase)` with `SVG_PATH = ACTIONBUTTON_SVG`.
  - `test_actionbutton_contract`: `assert_ids_present(self, self.tree, ("normal", "pressed", "hover", "focus"))`, the parsed fill set is exactly `PLATINUM_FILLS | {"none"}`, and `assert_no_script_elements`.
  - `test_actionbutton_geometry`: for `normal`, the circles are `(18, 18, 17, "#000000")` then `(18, 18, 15, "#DDDDDD")`, and the two half-disc paths' arcs reconstruct (18,18) at r=16; their fills in document order are `#FFFFFF` then `#999999`, so the paint order pins the top-left highlight. For `pressed`, the same geometry with the two fills swapped. For `hover` and `focus`, the group holds no circle but one `#000000` donut path whose four 180-degree arcs reconstruct (18,18) at radii 18, 18, 17, 17 with the inner pair wound the other way, so a filled disc, a same-winding path or a swapped inner/outer radius fails. Every group must also hold one invisible 36x36 bounding rect, so all four scale identically.
- `tests/test_desktoptheme.py`: add `("actionbutton.svg", ACTIONBUTTON_SVG, 36, 36)` to `SVG_CANVASES` and `os.path.join("widgets", "actionbutton.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-theme row `| widgets/actionbutton.svg draws the Platinum round action button. | tests/test_desktoptheme_actionbutton.py::TestActionButton | none |`.
- `README.md`: add `widgets/actionbutton.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktop-themes/org.macos8.desktop/widgets/actionbutton.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionbutton.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `actionbutton.svg` parses with a 36x36 root canvas and the four named groups; its parsed fills are exactly the Platinum four plus `none` (the bounding rects).
- `normal`/`pressed` are concentric circles at (18,18) with r=17/16/15 and opposite bevel orders; `hover`/`focus` are a r=17..18 `#000000` donut path with a transparent r=17 interior, all pinned by name.
- `make install` copies the file into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), the SVG registry covers it (through `TestSvgRootCanvas.test_registry_covers_every_shipped_svg`), and the README and `docs/invariants.md` list it.
- `make check` is green.

- Mac OS 8.6 Platinum busy indicator (`widgets/busywidget.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit b42c20a)
- Invariants register: `docs/invariants.md` pinning each subsystem's guarantee to its test (planned 2026-10-18, done 2026-10-18; commit 6dfe56b)
- Mac OS 8.6 Platinum switch widget (`widgets/switch.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit 448301a)
- Mac OS 8.6 Kvantum widget style, part 4/4: select the Kvantum style from the global theme (planned 2026-10-18, done 2026-10-18; commit 1ce5330)
- Mac OS 8.6 Kvantum widget style, part 3/4: the Platinum surface controls (planned 2026-10-18, done 2026-10-18; commit d16dec4)
- Mac OS 8.6 Kvantum widget style, part 2/4: the Platinum track and value controls (planned 2026-10-18, done 2026-10-18; commit c8220b9)
- Mac OS 8.6 kicker logo: our own non-infringing `start-here-kde-symbolic` icon (planned 2026-10-18, done 2026-10-18; commit 397f190)
- Mac OS 8.6 Kvantum widget style, part 1/4: ship the `org.macos8.desktop` Kvantum theme with the Platinum palette and the core-control art (planned 2026-10-18, done 2026-10-18; commit 1e9762f)
- Mac OS 8.6 Platinum icon theme: replace the placeholder art with final non-infringing art (planned 2026-10-18, done 2026-10-18; commit ca89e96)
- Own icon art: `PLACEHOLDER:` markers and a test that keeps `PLACEHOLDERS.md` complete (planned 2026-10-18, done 2026-10-18; commit 58830a3)
- Mac OS 8.6 Platinum desktop icon theme: a minimal `org.macos8.desktop` icon package for the icons the desktop shows (planned 2026-10-18, done 2026-10-18; commit 364335d)
- Local theme apply, part 2/2: `make install-local-hook` writes an uncommitted `post-commit` hook that runs `make apply` (planned 2026-10-18, done 2026-10-18; commit e897ef0)
- Local theme apply, part 1/2: `make apply` installs and re-applies the theme to the running Plasma session (planned 2026-10-18, done 2026-10-18; commit c7c2d14)
- Mac OS 8.6 menu-bar top highlight: a `north-` panel-background state whose centre carries the white row 0 (planned 2026-10-18, done 2026-10-18; commit cdc6e60)
- Mac OS 8.6 Qt widget style: select Qt's built-in square-bevel `Windows` style from the global theme (planned 2026-10-18, done 2026-10-18; commit a318999)
- Mac OS 8.6 menu-title spacing: 7px horizontal padding in `widgets/menubaritem.svg` (planned 2026-10-18, done 2026-10-18; commit 31208c2)
- Mac OS 8.6 desktop icon labels: one line of text under each icon (planned 2026-10-18, done 2026-10-18; commit 727cde4)
- Mac OS 8.6 desktop icon arrangement: one right-aligned column of 32px icons (planned 2026-10-18, done 2026-10-18; commit aacf578)
- Mac OS 8.6 Platinum tooltip (`widgets/tooltip.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 84cdbbb)
- Mac OS 8.6 menu-bar clock format: 12-hour time with AM/PM, no date, no seconds (planned 2026-10-17, done 2026-10-17; commit dc4dfce)
- Clear the title-bar pinstripes around the zoom box, as Mac OS 8.6 does (planned 2026-10-17, done 2026-10-17; commit d59e398)
- Grow the Aurorae title-bar boxes to 13x13 with their white highlight (planned 2026-10-17, done 2026-10-17; commit 73bd870)
- Mac OS 8.6 zoom box glyph and collapse (windowshade) box for the Aurorae decoration (planned 2026-10-17, done 2026-10-17; commit ffa77e7)
- Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 262f2d9)
- Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 0446a33)
- Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17, done 2026-10-17; commit 76ba0c4)
- Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17, done 2026-10-17; commit 4422d20)
- Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17, done 2026-10-17; commit 884c659)
- Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17, done 2026-10-17; commit d46c4eb)
- Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit a683b57)
- Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17; commit 1b5c020)
- Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17; commit ff71c62)
- Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17; commit c8d132b)
- Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09; commit 370205e)

- Mac OS 8.6 Platinum view item widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 1e1a455)
- Mac OS 8.6 Platinum slider widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 698e2b2)
- Wire the Mac OS 8.6 window decoration into the global theme defaults (planned 2026-10-09, done 2026-10-09; commit 0063255)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (planned 2026-10-08, done 2026-10-09; commit 91189a7)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (planned 2026-10-08, done 2026-10-08; commit 15bee80)
- Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08, done 2026-10-08; commit 395994f)
- Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 27b7439)
- Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 8df5661)
- Mac OS 8.6 Platinum scroll bar widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 9f51d5b)
- Mac OS 8.6 Platinum list item widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7fe6ddc)
- Mac OS 8.6 Platinum text field widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 0fe5213)
- Mac OS 8.6 Platinum checkmarks widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7313acd)
- Mac OS 8.6 Platinum radio button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit a73c322)
- Mac OS 8.6 Platinum frame widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit ebb65ca)
- Mac OS 8.6 Platinum button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit e553908)
- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)

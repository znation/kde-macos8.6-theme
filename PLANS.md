# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-18 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-three widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document and
Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic`, our own mark rather than
Apple's; `PLACEHOLDERS.md` is empty); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-18 by the plan
role): a **Qt widget style** for KDE applications (the desktop theme styles only Plasma shell
widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

### Ground the Kvantum item view's sunken field in the reference Finder content area (planned 2026-10-19 by the plan role)

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
  `lineedit-focused-*` art). Rewrite each 2x2 corner as the outer 2x2 of
  `sunken_outside_face_corners("#FFFFFF")` in `tests/svg_assertions/faces.py`; the top-right
  outer pixel stays unpainted (reference (453,118)=#CCCCCC, the window face). Leave
  `itemview-pressed-*` and `itemview-toggled-*` flat #CCCCFF, and add a comment above the two
  groups naming the reference and its sampled pixels.
- Update the file-header comment (the sentence "the line edit is the white sunken field") to
  name the item view as sharing that field.
- `tests/test_kvantum_bevel_pixels.py`: remove `"itemview"` from `SURFACE_STATES` and add a
  `TestItemViewBevelPixels` case mirroring `TestLineEditBevelPixels` (reusing `LINEEDIT_EDGES`,
  `_lineedit_edge_map` and `_lineedit_corners`) for prefixes `itemview-normal` and
  `itemview-focused`, so a state repeating the old outline-outside art fails there.
- New `tests/test_kvantum_itemview_reference.py`: a `ReferenceScreenshotMixin` case over
  `setup_emaculation.png` (`MAX_ROWS = 479`) that re-derives the field's four border runs and
  its top-left 2x2 corner and asserts the rendered Kvantum `itemview-normal` tiles paint the
  same sunken-outside arrangement; skips when the image is not materialized. The reference
  field's top-right and bottom corners sit under the status header and the scrollbars, so the
  test derives only the clean left/top/right/bottom runs and the top-left corner.
- `docs/invariants.md`: add a `kvantum` row `| The item view is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_itemview_reference.py::TestItemViewReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_itemview_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `itemview-normal-*` and `itemview-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline.
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 250` prints
  `153,153,153 #999999`, `... 23 250` prints `0,0,0 #000000`, `... 24 250` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and the other three runs and
  passes, skipping when the image is not materialized.
- `TestItemViewBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

## Done

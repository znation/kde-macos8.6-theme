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

### Correct the shared sunken-outside field's bottom corners to the reference field's true bottom (planned 2026-10-19 by the plan role)

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

## Done

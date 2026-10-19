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

_None yet._

### Ground the Kvantum line edit's sunken bevel in the reference text field (planned 2026-10-19 by the plan role)

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
  the #FFFFFF centre face unchanged: `-top` becomes #999999 then #000000, `-bottom` stays
  #FFFFFF then #000000, `-left` becomes #999999 then #000000, `-right` stays #FFFFFF then
  #000000. Rewrite each 2x2 corner as the outer 2x2 of the `sunken-outside` corner table in
  `tests/svg_assertions/faces.py` (`sunken_outside_face_corners("#FFFFFF")`), scaled to the 2px
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

## Done

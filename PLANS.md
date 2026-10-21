# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-19 by the clean role):** The initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
and the render and fidelity tooling
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

### Ground the desktop theme dialog body's raised bevel shadow in the reference Get Info window body (planned 2026-10-19 by the plan role)

**Goal.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg` paints the raised
window body's bevel shadow `#999999`, and its header claims "the reference window body itself is
flat, so no window-body pixel grounds those two". But the Get Info window body in
`macos8.6-screenshots/aboutsystem_betawiki.png` is a clean lossless raised Platinum body: a 1px
`#000000` outline, a 1px `#FFFFFF` highlight on the top/left, a 1px `#AAAAAA` shadow on the
bottom/right, and a `#DDDDDD` face. Correct the shadow to `#AAAAAA` and pin it to those pixels.
This is the same raised shadow the Kvantum `button` element and the desktop theme `button.svg`
already use (`PLANS-DONE.md`; PLANS.md), while the reference's sunken field keeps `#999999`, so
only the raised bevel moves. The other desktop-theme raised faces (`widgets/frame.svg`'s raised
state, `widgets/scrollbar.svg`'s thumb, `widgets/toolbar.svg`, `widgets/actionbutton.svg`) are
separate surfaces that the reference's window body does not directly ground; they keep `#999999`
and are out of scope.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4L8`, the same image
the Kvantum button/check-box groundings use). The Get Info window body: top `(200,46)=#000000`,
`(200,47)=#FFFFFF`; left `(12,200)=#000000`, `(13,200)=#FFFFFF`; face `(200,100)=#DDDDDD`; bottom
`(200,418)=#AAAAAA` (uniform across x=40..339) then `(200,419)=#000000`; right `(353,200)=#AAAAAA`
then `(354,200)=#000000`. The window's 6px Aurorae border (pinned by the render gate) sits outside
those pixels, so `#AAAAAA` is the body's bevel shadow, not the frame's. The retail `#999999`
sunken-field shadow (`firstboot_betawiki.png`) is unchanged.

**Approach.**
- `dialogs/background.svg`: in `bottom`, `right` and the four shadow corners, change the bevel
  shadow `#999999` to `#AAAAAA`; leave the `#000000` outline, `#FFFFFF` highlight and `#DDDDDD`
  face. Correct the header: the reference window body is a raised bevel, name
  `aboutsystem_betawiki.png` and the sampled pixels, and drop the "flat" claim and the "same bevel
  rule as scrollbar.svg's thumb" cross-reference (the thumb keeps `#999999`).
- `tests/svg_assertions/faces.py`: give the raised branch of `face_corners`/`RAISED_FACE_CORNERS`
  and `face_edge_bands` a `shadow="#999999"` keyword so the raised table can be rebuilt with
  `#AAAAAA`; the waiting button plan adds the same keyword to `face_edge_bands`, so reuse it when
  it is already present.
- `tests/svg_assertions/pixels.py`: thread the same `shadow="#999999"` keyword through
  `assert_face_bevel` into `face_edge_bands`/`face_corners`.
- `tests/support/platinum_palette.py`: give `assert_fill_palette` a `shadow=GREY` keyword that
  swaps `GREY` for the caller's shadow (the button plan adds the same keyword; whichever lands
  second reuses it).
- `tests/support/raised_face_case.py`: add a `SHADOW = GREY` class attribute and pass it to
  `assert_face_bevel` and `assert_fill_palette`.
- `tests/test_desktoptheme_dialog.py`: set `SHADOW = "#AAAAAA"` on `TestDialogBackground`; add a
  `TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE`/`MAX_ROWS` from `support.aurorae_fixtures` that re-derives the four colours from the
  anchors above and asserts the rendered `bottom`/`right` slices paint `#AAAAAA` and the
  `top`/`left` slices `#FFFFFF`, skipping when the Git LFS image is not materialized.
- `docs/invariants.md`: extend the `dialogs/background.svg` row's guarantee to name the
  reference's raised bevel shadow.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`,
`tests/svg_assertions/faces.py`, `tests/svg_assertions/pixels.py`,
`tests/support/platinum_palette.py`, `tests/support/raised_face_case.py`,
`tests/test_desktoptheme_dialog.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 200 418` prints
  `170,170,170 #AAAAAA`, `... 200 47` prints `#FFFFFF`, `... 12 200` prints `#000000`, and
  `... 200 100` prints `#DDDDDD`.
- `dialogs/background.svg`'s parsed fill set is exactly `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`
  and `test_desktoptheme_dialog.py` passes.
- `TestToolBar` and the frame/scrollbar/actionbutton raised tests still pin `#999999`; the
  line-edit's and Kvantum item-view's sunken `#999999` shadow is unchanged.
- The new reference test re-derives the four colours from `aboutsystem_betawiki.png` and passes
  when the image is materialized, skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- `make check` is green.

### Ground the Kvantum combo box indicator in the reference's double up/down arrow (planned 2026-10-20 by the plan role)

**Goal.** `[ComboBox]` in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`
inherits `PanelButtonCommand`, so its popup currently draws the shared `arrow` indicator: a single
9x9 down triangle (`arrow-down-*`). The reference's popup button draws a double up/down arrow --
two 7px-wide triangles separated by two face rows -- in a #DDDDDD cell. Ship a dedicated
`comboarrow` indicator for `[ComboBox]` and leave `arrow` (still used by `IndicatorArrow`, the
spin box and the splitter) unchanged.

**Reference grounding.** `macos8.6-screenshots/systeminfo_betawiki.png` (labelled in
`sources.txt` as the 8.6a3c2 beta build, About This Computer), the System Info window's "Show:"
popup. Its 12x12 arrow region `(233,106)..(244,117)` is exactly `#000000` and `#DDDDDD`: 32 black
pixels in eight one-row bands of widths 1/3/5/7 at y107..110 and 7/5/3/1 at y113..116, centred on
x238, with face rows y106, y111..112 and y117. The popup's arrow-cell face is 16x14
(x231..246, y105..118), so a 12x12 element centred in it lands on exactly that region (2px side
and 1px top/bottom face margins). The cell's divider (`x228` `#AAAAAA`), white highlight (`x230`
`#FFFFFF`) and right bevel (`x247` `#AAAAAA`, `x248` `#777777`) are frame art, not indicator art;
this plan does not ship them.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: add five single-element indicator
  groups `comboarrow-normal`, `comboarrow-focused`, `comboarrow-pressed`, `comboarrow-toggled`
  and `comboarrow-disabled` after the last existing `menubaritem` group. Each group holds a full
  12x12 `#DDDDDD` rect (which fixes the element's 12x12 bounds, so Kvantum scales it 1:1 at
  `indicator.size=12`), then eight arrow rects at cell-relative y=1 x=5 w=1, y=2 x=4 w=3, y=3
  x=3 w=5, y=4 x=2 w=7, y=7 x=2 w=7, y=8 x=3 w=5, y=9 x=4 w=3 and y=10 x=5 w=1; the disabled
  group paints the arrow rects `#999999`. Rects, not paths, so `render_slices` can paint and
  compare the element. Place the five groups at translate y positions 22870, 22930, 22990, 23050 and
  23110 and raise the root `height`/`viewBox` from 22920 to 23140. Extend the leading SVG comment
  to name the reference, the 12x12 cell and the frame-art exclusion.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`: under `[ComboBox]`, add
  `indicator.element=comboarrow` and `indicator.size=12`, with a short comment naming the
  reference popup's double arrow.
- `tests/support/kvantum_config_spec.py`: set
  `CORE_CONTROL_CONFIG["ComboBox"]["indicator.element"]` to `"comboarrow"`; add
  `VALUE_KEYS["ComboBox"] = {"indicator.size": "12"}`.
- `tests/test_kvantum_svg.py`: add
  `"comboarrow": ("normal", "focused", "pressed", "toggled", "disabled")` to
  `INTERIOR_STATES`; add `_COMBOARROW` and `_COMBOARROW_DISABLED` draw lists to
  `INTERIOR_GROUP_SHAPES` for the five state ids; add `"comboarrow"` to the `elements` tuple in
  `test_remaining_interiors_draw_the_pinned_shapes`; update the table comments that enumerate
  single interior/indicator elements.
- `tests/support/kvantum_fixtures.py`: add
  `SYSTEMINFO_REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "systeminfo_betawiki.png")`
  and `SYSTEMINFO_MAX_ROWS = 118`, commented as the About This Computer screenshot and the
  deepest row the combo arrow samples (y117).
- `tests/test_kvantum_combobox_reference.py` (new): define
  `TestComboBoxReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = SYSTEMINFO_REFERENCE`, `MAX_ROWS = SYSTEMINFO_MAX_ROWS`, `COMBO_X = 233`,
  `COMBO_Y = 106`, `COMBO_SIZE = 12` and the black-row table. One test samples all 144 pixels,
  asserts the colour set is exactly `{BLACK, FACE}` and asserts the black pixels are the row
  table, so the reference itself is pinned; another renders the SVG once with
  `render_slices(parse_svg(SVG))`, compares `comboarrow-normal` exactly to the sampled map,
  asserts `comboarrow-focused`, `comboarrow-pressed` and `comboarrow-toggled` equal it, and
  asserts `comboarrow-disabled` equals it with every `#000000` replaced by `GREY`.
- `docs/invariants.md`: add a kvantum row -- "The combo box indicator is the reference's double
  up/down arrow in a 12x12 `#DDDDDD` cell." -- naming
  `tests/test_kvantum_combobox_reference.py::TestComboBoxReference`, with the provenance
  exception that the popup is an 8.6a3c2 beta build and that the cell's divider and right bevel
  are frame art, not indicator art.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`tests/support/kvantum_config_spec.py`, `tests/support/kvantum_fixtures.py`,
`tests/test_kvantum_svg.py`, `tests/test_kvantum_combobox_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/systeminfo_betawiki.png 238 107` prints
  `0,0,0 #000000`; `... 238 111` prints `221,221,221 #DDDDDD`; `... 238 113` prints
  `0,0,0 #000000`; `... 233 106` and `... 244 117` print `221,221,221 #DDDDDD`.
- `make check CHECK_TESTS=test_kvantum_combobox_reference` passes when the Git LFS image is
  materialized and skips (does not fail) when it is not; changing any arrow or gap pixel in the
  12x12 cell makes it fail.
- `make check CHECK_TESTS=test_kvantum_svg` passes: the five `comboarrow-*` ids exist, each
  state's rects match the pinned shape, and the fill set stays the Platinum palette.
- `make check CHECK_TESTS=test_kvantum_config_elements` and `test_kvantum_config` pass:
  `[ComboBox]` resolves to `comboarrow` at size 12, and every config key remains pinned.
- The existing `arrow-*` ids, path `d` values and fills are unchanged; the four direction tests
  and the `IndicatorArrow`, spin box and splitter mappings still pass.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`, and `make check` is
  green.


## Done

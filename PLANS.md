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

### Ground the Kvantum button bevel's shadow in the reference's popup buttons (planned 2026-10-19 by the plan role)

**Goal.** The four `button-*` state groups in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` paint their bevel shadow `#999999`
(the raised states' bottom/right bands and their two shadow corners, the sunken states' top/left
bands and their two shadow corners). The Get Info window in
`macos8.6-screenshots/aboutsystem_betawiki.png` draws its two popup buttons with a `#AAAAAA`
shadow, and `[ComboBox]` in the `.kvconfig` renders through that same `button` element
(`[ComboBox] inherits=PanelButtonCommand`, whose `frame.element` and `interior.element` are both
`button`), so the screenshot directly grounds the element. Correct the shadow to `#AAAAAA` and
pin it to the reference; the `#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face already
match.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4`, the same image
the Kvantum check box grounding uses). The "表示" popup button spans x=80..249, y=103..122: top
outline (150,103)=`#000000`, top highlight (150,104)=`#FFFFFF`, left outline (80,108)=`#000000`,
left highlight (81,108)=`#FFFFFF`, face (150,108)=`#DDDDDD`, bottom shadow (150,121)=`#AAAAAA`,
bottom outline (150,122)=`#000000`. The "ラベル" popup button repeats it at y=275..292:
(150,275)=`#000000`, (150,276)=`#FFFFFF`, (150,291)=`#AAAAAA`, (150,292)=`#000000`. The
reference shadow is `#AAAAAA`, six levels lighter than the theme's `#999999`.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: in the four `button-*` state groups
  (`normal`, `focused`, `pressed`, `toggled`) change every bevel shadow `#999999` to `#AAAAAA` --
  the raised states' `-bottom`/`-right` bands and their `-topright`/`-bottomright` corners, and the
  sunken states' `-top`/`-left` bands and their `-topleft`/`-bottomleft` corners. Leave the
  `#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face. Reword the header comment's bevel
  sentence so it names the reference-grounded button shadow (the popup buttons in
  `aboutsystem_betawiki.png`) rather than stating `#999999` as the shared raised shadow; the other
  raised-frame elements (tab, menu, group, toolbar, ...) keep `#999999`, because the reference
  set's only lossless raised-button bevel is these popup buttons.
- `tests/test_kvantum_bevel_pixels.py`: add `BUTTON_SHADOW = "#AAAAAA"` and
  `SURFACE_SHADOW = "#999999"`; give `_button_edge_maps` a `shadow` parameter and turn the
  `BUTTON_CORNERS` literal into a `_button_corners(shadow)` helper; `TestButtonBevelPixels` passes
  `BUTTON_SHADOW` and `TestSurfaceBevelPixels` passes `SURFACE_SHADOW`, so the button states are
  pinned to `#AAAAAA` while the tab/menu/group/toolbar states keep `#999999`.
- New `tests/test_kvantum_button_reference.py`, modelled on
  `tests/test_kvantum_checkbox_reference.py`: a
  `TestButtonReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = aboutsystem_betawiki.png` that derives the four bevel colours from the anchors above
  and asserts the shipped `button-normal` slices paint the raised arrangement with `#AAAAAA` and
  that `button-pressed` paints the sunken arrangement with the same `#AAAAAA` shadow, skipping when
  the Git LFS image is not materialized. `render_slices(parse_svg(SVG))` reads the nine
  `button-normal-*`/`button-pressed-*` slices.
- `docs/invariants.md`: add the kvantum row `| The button bevel is the reference's raised
  popup-button bevel. | tests/test_kvantum_button_reference.py::TestButtonReference | The
  reference's popup button is a beta build (aboutsystem_betawiki.png); it is the set's only
  lossless raised-button bevel. |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_button_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 150 121` prints
  `170,170,170 #AAAAAA`, and `(150,291)` likewise; `(150,104)` and `(81,108)` are `#FFFFFF`,
  `(150,108)` is `#DDDDDD`, and `(150,103)`, `(150,122)` and `(80,108)` are `#000000`.
- Every `button-*` raised state's bottom and right bands are `#AAAAAA`, every sunken state's top
  and left bands are `#AAAAAA`, and the four `button-*` state groups' fill set is exactly
  `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`; `TestButtonBevelPixels` passes.
- `TestSurfaceBevelPixels` still pins the tab/menu/group/toolbar `#999999` shadow, and the line
  edit's and item view's `#999999` sunken-field shadow (the shared `sunken_outside_face_corners`
  table) is unchanged.
- The new reference test re-derives the four colours from `aboutsystem_betawiki.png` and passes
  when the image is materialized, skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- `make check` is green.


## Done

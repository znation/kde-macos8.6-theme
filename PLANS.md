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

### Ground the desktop theme push button's raised bevel shadow in the reference's raised buttons (planned 2026-10-19 by the plan role)

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/button.svg` paints the raised
bevel's shadow `#999999`: the `normal` state's bottom and right bands and its three shadow
corners, and the inverted `pressed` state's top and left bands and corners. The reference
set's lossless raised button bevels -- the Get Info window's two popup buttons in
`macos8.6-screenshots/aboutsystem_betawiki.png` -- use `#AAAAAA`, and the lossy Open dialog's
rounded push buttons (`opendialog_macrumors86.jpg`) show the same lighter shadow. The Kvantum
`button` element was already corrected from `#999999` to `#AAAAAA` against those popup buttons
(`PLANS-DONE.md`, "Ground the Kvantum button bevel's shadow"), so the desktop theme's push
button is now the odd one out. Correct its shadow to `#AAAAAA` and pin it to the reference. The
`#000000` outline, `#FFFFFF` highlight and `#DDDDDD` face already match; the rounded corner
stays, because the reference's push buttons are rounded while its popup buttons are square --
only the shadow colour is grounded.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4`, the same image
the Kvantum button and check-box groundings use). The "表示" popup button spans x=80..249,
y=103..122: `(150,103)=#000000`, `(150,104)=#FFFFFF`, `(150,108)=#DDDDDD`, `(150,121)=#AAAAAA`,
`(150,122)=#000000`; the "ラベル" popup button repeats it at y=275..292 (`(150,275)=#000000`,
`(150,276)=#FFFFFF`, `(150,291)=#AAAAAA`, `(150,292)=#000000`). The Open dialog's rounded push
buttons (`opendialog_macrumors86.jpg`, JPEG, corroboration only) show a ~`#ADADAD` shadow.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/button.svg`: change every bevel shadow
  `#999999` to `#AAAAAA` -- `normal-bottom`, `normal-right`, `normal-topright`,
  `normal-bottomleft`, `normal-bottomright`, and the inverted `pressed-top`, `pressed-left`,
  `pressed-topleft`, `pressed-topright`, `pressed-bottomleft`. Leave the `#000000` outline,
  `#FFFFFF` highlight and `#DDDDDD` face; the `focus` state has no shadow.
- `tests/support/platinum_palette.py`: add `BUTTON_SHADOW = "#AAAAAA"`, documented as the
  reference's raised-button shadow, and give `assert_fill_palette` a `shadow=GREY` keyword that
  swaps `GREY` for the caller's shadow in the expected set (the default keeps the current
  behaviour for every other widget test).
- `tests/svg_assertions/faces.py`: give `face_edge_bands(face, bevel)` a `shadow="#999999"`
  keyword and use it in place of the three `#999999` literals (the raised, sunken and
  sunken-outside bands), so the button test can pass `BUTTON_SHADOW` while
  `frame`/`lineedit`/`toolbar`/`scrollbar` keep the default.
- `tests/test_desktoptheme_button.py`: call `assert_fill_palette(self, self.tree,
  shadow=BUTTON_SHADOW)`; replace the `#999999` literals in `test_button_bevel_direction`'s
  `outward` and `corners` tables with `#AAAAAA`; pass `shadow=BUTTON_SHADOW` in
  `test_button_edge_pixels`.
- New `tests/test_desktoptheme_button_reference.py`, modelled on
  `tests/test_kvantum_button_reference.py`: a `TestButtonReference(ReferenceScreenshotMixin,
  unittest.TestCase)` with `REFERENCE`/`REFERENCE_ROWS` from `support.aurorae_fixtures` that
  re-derives the four colours from the popup-button anchors above and asserts the shipped
  `normal` slices paint the raised arrangement with `#AAAAAA` and the `pressed` slices the
  sunken one with the same shadow; skips when the Git LFS image is not materialized.
- `docs/invariants.md`: add a `desktoptheme` row `| widgets/button.svg's raised bevel shadow is
  the reference's #AAAAAA. | tests/test_desktoptheme_button_reference.py::TestButtonReference |
  The reference's raised button bevel is the Get Info popup button (aboutsystem_betawiki.png), a
  beta build; the reference's rounded push buttons are only in the lossy
  opendialog_macrumors86.jpg. |`.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/button.svg`,
`tests/support/platinum_palette.py`, `tests/svg_assertions/faces.py`,
`tests/test_desktoptheme_button.py`, `tests/test_desktoptheme_button_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 150 121` prints
  `170,170,170 #AAAAAA` and `... 150 291` likewise; `(150,104)` is `#FFFFFF`, `(150,108)` is
  `#DDDDDD`, and `(150,103)`/`(150,122)` are `#000000`.
- Every `button.svg` `#999999` is now `#AAAAAA`, the file's fill set is exactly
  `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`, and `test_desktoptheme_button.py` passes.
- `face_edge_bands` with its default still returns the `#999999` shadow, so
  `test_desktoptheme_frame.py`, `test_desktoptheme_lineedit.py` and the
  `test_svg_assertions_faces.py` self-test are unchanged.
- The new reference test re-derives the four colours from `aboutsystem_betawiki.png` and passes
  when the image is materialized, skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.


## Done

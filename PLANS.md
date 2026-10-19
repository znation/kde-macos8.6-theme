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

### Ground the Kvantum check box face in the reference's raised Platinum check box (planned 2026-10-19 by the plan role)

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

## Done

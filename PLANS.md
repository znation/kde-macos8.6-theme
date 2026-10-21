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
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-20 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** is out of scope (no reference screenshot shows a
cursor, so no pixel ground truth exists to match); and **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them). The shipped work should not be treated
as the whole of the prompt.

Two answers on 2026-10-19 expand the scope again, and neither has a plan yet.
**GTK applications and Firefox** are now in scope (QUESTIONS.md, answered 2026-10-19): a
KDE/Qt global theme cannot reach them, so this needs a GTK 4 CSS theme and a Firefox
`userChrome.css` plus profile preference, installed by separate opt-in `make` targets — a
multi-part series of its own. **The UI font** is now to be vendored (QUESTIONS.md, answered
2026-10-19): the theme should ship a Chicago/Charcoal-style font with a checked redistribution
licence and recorded provenance, select it for KDE, Plasma and Qt applications, and the answer
leaves open whether one face serves both Chicago and Charcoal. The plan queue carries neither
surface yet; until it does, the menu bar and dialog text keep the user's desktop font, and GTK
and Firefox applications keep their own chrome.

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

### Ship a GTK 3 Platinum theme for GTK applications (planned 2026-10-21 by the plan role; part 1/4)

**Goal.** No GTK theme exists in the repository (no `theme/gtk` directory), so GTK 3
applications -- including Firefox's GTK chrome -- keep the desktop's Breeze GTK theme. Ship a
user-installable `org.macos8.desktop` GTK 3 theme whose windows, header bars, buttons, entries,
notebook tabs, menus, scroll bars and toolbars paint the Platinum palette and square bevels.
This is part 1/4 of the GTK and Firefox application-chrome series; it ships the artwork only.
Part 2/4 will ship the GTK 4/libadwaita CSS, part 3/4 installs and selects both, and part 4/4
adds the opt-in Firefox chrome. Those sibling plans are not in this queue yet and will be added
as separate entries.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. Take every
colour from the already reference-grounded Platinum palette in
`tests/support/platinum_palette.py`: `FACE` `#DDDDDD`, `WHITE`, `GREY` `#999999`, `BLACK`,
`BUTTON_SHADOW` `#AAAAAA` (the raised push button's shadow), `TROUGH` `#EEEEEE` and `SELECTION`
`#CCCCFF`. The `#888888` etched-separator dark half is the value
`tests/test_desktoptheme_line.py` pins to the reference. Record in the CSS header and in
`docs/invariants.md` that the palette is reference-grounded while the GTK-specific geometry is
this theme's adaptation; do not claim a GTK reference crop.

**Approach.**
- `theme/gtk/org.macos8.desktop/index.theme`: `[Desktop Entry]` with `Type=X-GNOME-Metatheme`,
  `Name=Mac OS 8.6 Platinum`, `Encoding=UTF-8` and a short `Comment=`, plus an
  `[X-GNOME-Metatheme]` group naming the same theme.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: import Adwaita first with
  `@import url("resource:///org/gtk/libgtk/theme/Adwaita/gtk-contained.css");`, then redefine the
  theme colours with `@define-color theme_bg_color #DDDDDD;`, `theme_fg_color #000000`,
  `theme_base_color #FFFFFF`, `theme_text_color #000000`, `theme_selected_bg_color #CCCCFF`,
  `theme_selected_fg_color #000000`, `borders #000000` and `unfocused_borders #999999`.
  Override exactly these scoped rules (no `*` selector):
  - `window, .background`: `#DDDDDD` background, `#000000` text.
  - `headerbar, .titlebar`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, no box shadow; `headerbar` keeps only its 1px black bottom rule.
  - `button`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`;
    `button:hover` keeps the same face; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF`.
  - `entry`: white face, `1px solid #000000` border, `border-radius: 0`, sunken
    `box-shadow: inset 1px 1px #999999`, black text.
  - `notebook > header`: `#DDDDDD` background, black border; each
    `notebook > header > tabs > tab` is a raised `#DDDDDD` face with `1px solid #000000`,
    `border-radius: 0` and `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`; the
    `:checked` tab drops the bottom border to `#DDDDDD` and the bevel shadow.
  - `menu, .menu, popover, .popover`: `#DDDDDD` face, `1px solid #000000` border,
    `border-radius: 0`; `menuitem:hover, .menuitem:hover` paints `#CCCCFF`.
  - `scrollbar`: `#EEEEEE` trough with a `1px solid #000000` border; `scrollbar slider` is the
    raised `#DDDDDD` thumb with a `1px solid #000000` border, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`.
  - `toolbar, menubar`: `#DDDDDD` face with the reference's etched rule,
    `border-bottom: 1px solid #888888` and `box-shadow: inset 0 -1px #FFFFFF`.
- `tests/test_gtk_theme.py` (new): `TestGtkTheme` reads the two files as text. Pin the
  `index.theme` keys above; pin the Adwaita import string, every `@define-color` name/value, and
  every selector/property above (a parser over brace blocks or explicit substring checks is
  fine). Assert the only six-digit hex literals in the CSS are exactly
  `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`, importing the
  palette constants from `support.platinum_palette` and defining `ETCH_DARK = "#888888"` beside
  the existing line-test value, so a stray Breeze colour fails. Assert the rules for
  `headerbar, .titlebar`, `button`, `entry`, `notebook > header > tabs > tab`,
  `menu, .menu, popover, .popover` and `scrollbar slider` each carry `border-radius: 0`, and
  that no rule uses the universal `*` selector.
- `docs/invariants.md`: add a `## gtk` section (a `theme/gtk` subsystem needs its own section;
  do not fold this into `tooling`) with one row: "The GTK 3 Platinum theme imports
  libgtk/Adwaita, redefines the Platinum palette and paints the scoped Platinum control rules."
  pinned to `tests/test_gtk_theme.py::TestGtkTheme`, provenance exception: no reference
  screenshot shows a GTK widget, so the palette comes from the pinned Platinum values and the
  geometry is this theme's adaptation.

**Files touched.** `theme/gtk/org.macos8.desktop/index.theme` (new),
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (new), `tests/test_gtk_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The two new files exist under `theme/gtk/org.macos8.desktop/`; the CSS imports Adwaita,
  defines the eight theme colours with the values above, and carries every scoped control rule.
- `make check CHECK_TESTS=test_gtk_theme` passes, and removing the import, any `@define-color`,
  any listed selector, a bevel shadow or the scoped `border-radius: 0` makes it fail.
- The parsed CSS hex set is exactly the eight pinned colours; no Breeze or other colour is
  introduced.
- `tests/invariants.py`'s cross-check accepts the new `## gtk` section and
  `tests/test_gtk_theme.py::TestGtkTheme`.
- No install target, GTK selection, `kdeglobals` write or Firefox change is added in this part;
  `make check` is green.


## Done

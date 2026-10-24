# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-eight widget SVGs under
`widgets/`, including the `widgets/margins-highlight.svg` panel edit-mode margin highlight and the
`widgets/containment-controls.svg` panel resize and slider handles, plus
`dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's;
`PLACEHOLDERS.md` records no remaining placeholders); the `org.macos8.desktop` Kvantum widget
style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`,
and the global theme selects its `Lato` family for the general, menu, toolbar, smallest-readable
and window-title fonts, while monospaced text keeps the user's fixed font); the GTK 3 and GTK 4
Platinum stylesheets under `theme/gtk/` (installed by the opt-in `install-gtk` target and
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces and their status are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style pointer set (black-face, white-outline arrow,
text I-beam, pointing hand, busy hourglass, move cross, horizontal and vertical resize arrows,
NW-SE and NE-SW diagonal resize arrows, crosshair, circle-slash, drag-and-drop copy plus,
open and closed hands, the help question-mark arrow, the progress arrow with a small hourglass,
a pencil, the `zoom-in`/`zoom-out` magnifiers, and the drag-and-drop/forbidden aliases, not
traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; Xcursor roles the theme does not name still come from the fallback cursor
theme; **system sounds** are out
of scope (not a visual surface, so the reference set cannot ground them); and a **lock screen** is
out of scope unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered
2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both are being implemented in series.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed, and part 3/4 has landed as three entries — the opt-in install (parts 1/3 and 2/3) and
the selection (part 3/3) — while part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) has landed and part 2/2 (the profile install plus the
preference) has landed. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed and selected by the global theme); part 2/3
(a Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) has landed for the Lato
body face only, because Lato is the only family the package installs. KDE, Plasma and Qt
applications now use Lato for the general, menu, toolbar, smallest-readable and window-title
fonts, and monospaced text keeps the user's fixed font; GTK and Firefox
applications keep their own chrome unless the opt-in GTK targets or the Firefox userChrome
install are used (the GTK entries have landed, and Firefox chrome is part 1/2, which has
landed, while its profile install is part 2/2, which has landed).

_None yet._

### Platinum GTK window controls: paint the title-bar buttons as Platinum boxes (planned 2026-10-23 by the plan role; independent of the waiting GTK header plan)

**Goal.** Both opt-in GTK sheets name no `button.titlebutton` or `windowcontrols` rule. GTK 3's default sheet paints `button.titlebutton` transparent and draws the close, maximize and minimize glyphs from the icon theme; GTK 4's `Default-light.css` gives `windowcontrols button > image` a 30px circular background and tints it on hover. A client-side-decorated GTK window therefore keeps Adwaita's title-bar controls beside the Platinum header bar. Paint them with the reference-grounded Aurorae box art: the blank close box, the zoom (maximize) box whose inner square is the same in GTK's restore state, and the collapse (minimize) box with its two bars. The 16px square hit area and centre placement are this theme's GTK adaptation; every box pixel comes from the Aurorae SVGs that `tests/test_aurorae_buttons.py` re-derives from `aboutsystem_betawiki.png` and `systemprofiler_betawiki.png`. This plan paints the controls in the order GTK and KDE already lay them out; it does not change `gtk-decoration-layout`.

**Approach.**
- Add three assets under `theme/gtk/org.macos8.desktop/assets/`, each a 13x13 canvas carrying only the `active-center` group and a comment naming its Aurorae source, reference coordinates and `tests/test_gtk_title_buttons.py`. `window-close.svg` copies the rects of the Aurorae `close.svg` active group; `window-minimize.svg` copies the Aurorae `shade.svg` active group; `window-maximize.svg` copies the Aurorae `maximize.svg` active group with canvas x=5..17 (the box plus its highlight) translated to x=0..12, dropping its pinstripe, gap and spacing columns. Do not copy the Aurorae files whole: a plain SVG renderer draws both their `active-center` and later `inactive-center` groups, so the inactive art would cover the active box. GTK's restore state keeps the `.maximize` class and gets the zoom art, matching the Aurorae `restore.svg` decision, so it ships no fourth asset.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `headerbar` rule and before the generic `button` rule, add one rule group per control for both scoped selectors `headerbar button.titlebutton.close` and `.titlebar button.titlebutton.close` (and `.maximize` / `.minimize`), each with `background-color: transparent`, `background-image: url("../assets/window-close.svg")` (or the matching asset), `background-position: center`, `background-repeat: no-repeat`, `background-size: 13px 13px`, `border: 0`, `border-radius: 0`, `box-shadow: none`, `margin: 0`, `min-height: 16px`, `min-width: 16px`, `padding: 0` and `-gtk-icon-source: none`; add `headerbar button.titlebutton image, .titlebar button.titlebutton image` with `color: transparent`, `min-height: 16px` and `min-width: 16px`. The scoped selectors outrank the default sheet's `button.titlebutton`, `button.titlebutton:not(.appmenu)` and `button.titlebutton:backdrop` rules, so the box survives hover, active and backdrop instead of reverting to a transparent circular button.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: after the `headerbar` rule and before the generic `button` rule, add the same three rule groups for `headerbar windowcontrols button.close` and `.titlebar windowcontrols button.close` (and `.maximize` / `.minimize`) with the same declarations; add `headerbar windowcontrols button image, .titlebar windowcontrols button image` with `color: transparent`, `min-height: 16px` and `min-width: 16px`, which also overrides the default sheet's 30px image circle. Extend both sheets' provenance comments to name the title-bar boxes, their Aurorae source and the no-restore-asset decision.
- `tests/support/gtk_theme_spec.py`: add `TITLE_BUTTON` (the base declarations above without `background-image`) and `TITLE_BUTTON_IMAGE` beside `FRAME`, plus `assert_title_button(self, selector, asset)` after `assert_scale`, which asserts the base declarations and the `url("../assets/<asset>")` background image on one selector.
- `tests/test_gtk_theme.py`: add `test_title_buttons` asserting the three controls on both `headerbar` and `.titlebar` selectors and the image rule on both image selectors, and add the three new URLs to `test_icon_sources_point_at_shipped_assets`.
- `tests/test_gtk4_theme.py`: add `test_title_buttons` with the `windowcontrols` selectors and the same image assertion, and add the three new URLs to `test_stands_alone`.
- Add `tests/test_gtk_title_buttons.py`: parse the three assets with `support.svg_case.parse_svg`, assert each is a 13x13, script-free, style-free SVG holding only an `active-center` group, assert `window-close.svg` and `window-minimize.svg` render the same `active-center` pixels as their Aurorae sources, and assert `window-maximize.svg` renders exactly the Aurorae maximize group's x=5..17 pixels shifted by `-ZOOM_BOX_X`. The test needs no reference image, so it does not skip when the LFS set is absent.
- Install plumbing: add the three assets to the `install_gtk` staging trap, install and rename steps and to the `make uninstall` removal list in `Makefile`; add them to `SHIPPED_FILES` in `tests/support/gtk_fixtures.py` and to `STAGING_PATHS` in `tests/test_gtk_install.py`; move that suite's shadowed failing staging path to the new last asset (`*/assets/.window-minimize.svg.staging`) so its "last staging step fails" check still exercises the last step. Update `README.md`'s "four shared ... glyph assets" phrase and both "seven GTK files" counts to the new seven assets and ten files, and update the `## gtk` install invariant row in `docs/invariants.md` to the ten files and seven assets. Add one new `## gtk` invariant row at the end of the table naming the title-button rules and the Aurorae-derived assets.

**Files touched.** `theme/gtk/org.macos8.desktop/assets/window-close.svg`, `theme/gtk/org.macos8.desktop/assets/window-maximize.svg`, `theme/gtk/org.macos8.desktop/assets/window-minimize.svg`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `tests/test_gtk_title_buttons.py`, `tests/support/gtk_fixtures.py`, `tests/test_gtk_install.py`, `Makefile`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- The three assets are 13x13 SVGs with one `active-center` group and no inactive group; close and minimize are pixel-identical to their Aurorae active groups, and maximize is the Aurorae zoom box's 13x13 crop.
- Both sheets carry the close, maximize and minimize rule groups on both `headerbar` and `.titlebar` selectors with the base declarations, the matching asset URL, `-gtk-icon-source: none`, and the image rule that hides the toolkit icon; no new hex literal appears in either sheet.
- The new asset test and both suites' title-button tests pass, and both sheets' URL allowlists accept exactly the shipped assets they name.
- The opt-in install copies the now ten files byte-for-byte, a failed staging step still leaves every previous file intact, `make uninstall` removes all ten and the emptied directories, and the README and `docs/invariants.md` counts and rows match.
- `make check` is green.

## Done

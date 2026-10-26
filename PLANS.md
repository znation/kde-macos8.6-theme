# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role):** The
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
selected by `apply-gtk`; `make install` copies no GTK files); and the render and fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme.py::TestFirefoxChrome` checks stylesheet declarations;
those checks do not establish rendered Firefox pixels. Keep this distinction when assessing
progress toward pixel-perfect application chrome. README.md describes the reference set as the
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

### Firefox Platinum chrome: frame the sidebar with the Platinum face (planned 2026-10-26 by the plan role; independent of the waiting multi-selected tab face)

**Goal.** Give Firefox's sidebar the Platinum frame the toolbars already wear: the sidebar box takes the shared `#DDDDDD` face and black text, and the header band above the sidebar content gets the theme's etched `#888888`/`#FFFFFF` bottom rule, so an open sidebar reads as a Platinum panel rather than a band with no face of its own. The sidebar's inner document (bookmarks, history and other panel rows) stays Firefox's: `userChrome.css` does not style that document, and this plan claims no paint there.

**Grounding.** No reference screenshot shows Firefox chrome or a sidebar. Firefox's `chrome/browser/skin/classic/browser/sidebar.css` paints `#sidebar-container, #sidebar-box` with `--sidebar-background-color` and `--sidebar-text-color` and gives `#sidebar-header` a 1px `--sidebar-border-color` bottom border; those are lightweight-theme sidebar keys mapped from `sidebar`, `sidebar_text` and `sidebar_border` in `modules/ThemeVariableMap.sys.mjs`, and this userChrome-only sheet sets none of them, so it gives the header band no Platinum face or rule. `chrome/browser/content/browser/browser.xhtml` puts `#sidebar-header` inside `#sidebar-box`, with the `<browser id="sidebar">` panel document below it; the installed ESR's `defaults/preferences/firefox.js` leaves `sidebar.revamp` off, so that is the sidebar markup in use, and the revamped launcher is a different document outside this plan. The face `#DDDDDD` is the reference-grounded menu-bar face (`tests/test_colorscheme_reference.py::TestReferenceAnchors.test_menu_bar_face`) and the etched pair is the desktop theme's separator rule (`tests/test_desktoptheme_line.py::TestLineReference`), already used by this sheet's `#nav-bar`, `#PersonalToolbar` and `#toolbar-menubar`; no new colour literal is added. Record the missing reference surface and the dated platform adaptation (2026-10-26) in the sheet header.

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#nav-bar, #PersonalToolbar, #toolbar-menubar` rule and before the open menu-bar title comment, add
  `#sidebar-box { background-color: #DDDDDD !important; color: #000000 !important; }`
  and
  `#sidebar-header { border-bottom: 1px solid #888888 !important; box-shadow: inset 0 -1px #FFFFFF !important; }`.
  Replace no existing rule and add no hover, geometry, font or inner-document rule: `#sidebar-switcher-target` already takes `#EEEEEE` hover and `#CCCCFF` pressed/active fills from the sheet's `:root` toolbar-button tokens. In the header, insert a provenance paragraph between the tab-hover note (ending "`tests/test_desktoptheme_scrollbar.py::TestScrollbarReference.`") and the install-instructions paragraph (starting "Install it opt-in"): no reference shows a Firefox sidebar; its face reuses the reference-grounded `#DDDDDD` menu-bar face and its header rule the pinned etched pair rather than a screenshot sample; Firefox's `chrome/browser/skin/classic/browser/sidebar.css` consumes `--sidebar-background-color`, `--sidebar-text-color` and `--sidebar-border-color`, lightweight-theme sidebar keys mapped in `modules/ThemeVariableMap.sys.mjs`; the sidebar's inner document is not userChrome territory.
- `tests/test_firefox_theme.py`: add `#sidebar-box` and `#sidebar-header` entries to `REQUIRED_RULES` after the `#toolbar-menubar menubar > menu[open]` entry, with the declarations above. Add `TestFirefoxChrome.test_sidebar_frame_is_scoped_to_the_box_and_header`: the selectors naming `sidebar` are exactly `#sidebar-box` and `#sidebar-header`; each declaration set equals its `REQUIRED_RULES` entry; the box's face is `FACE`, its text `BLACK`, the header's border `1px solid ETCH_DARK` and its inset highlight `WHITE`. Append `"No reference shows a Firefox sidebar"`, `"chrome/browser/skin/classic/browser/sidebar.css"`, `"--sidebar-background-color"`, `"modules/ThemeVariableMap.sys.mjs"` and `"the sidebar's inner document is not userChrome territory"` at the end of the provenance tuple in `test_header_names_provenance_and_preference`, after the menu-bar entries.
- `docs/invariants.md`: add a new row at the end of `## firefox` (after the open-menu-bar-title row) whose guarantee is "The legacy Firefox sidebar frame (`#sidebar-box` above `#sidebar-header`) is the `#DDDDDD` Platinum face with black text and an etched `#888888`/`#FFFFFF` bottom rule on the header band, while the sidebar's inner document stays Firefox's", whose test is the new scope test, and whose provenance exception names the missing Firefox-sidebar reference, the reference-grounded menu-bar face and separator pair, Firefox's `sidebar.css` consumers and `ThemeVariableMap.sys.mjs` keys, the inner-document boundary, and that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when either sidebar rule is missing, the box face or text is not `#DDDDDD`/`#000000`, the header rule is not `#888888` with a `#FFFFFF` inset highlight, or any of them loses `!important`.
- The scope test fails when any selector other than `#sidebar-box` and `#sidebar-header` names a sidebar element, when either declaration set differs from `REQUIRED_RULES`, or when the header gains a declaration beyond the etched pair.
- The sidebar header's switcher keeps `#EEEEEE` hover and `#CCCCFF` pressed/active fills from the existing `:root` tokens; the tab strip, menu-bar titles, find bar, tooltip, search field, menus, arrow panels, results rows and status panel keep their current paints.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

### Firefox Platinum chrome: space the menu-bar titles with the Platinum menu-bar margins (planned 2026-10-26 by the plan role; independent of the waiting sidebar frame)

**Goal.** Give Firefox's menu-bar titles the same 3px/7px title box the desktop theme and the GTK sheets use, so an idle or open title sits with the reference menu bar's spacing instead of Firefox's font-relative, bottom-heavy stock padding. Change the title box's padding only; the open title's `#CCCCFF` fill and the menubar's face and etched rule stay as they are.

**Grounding.** No reference screenshot shows Firefox chrome or a Firefox menu bar. The geometry is `widgets/menubaritem.svg`'s `normal-hint-top-margin`/`normal-hint-bottom-margin` height (3px) and `normal-hint-left-margin`/`normal-hint-right-margin` width (7px), pinned by `tests/test_desktoptheme_menubaritem.py::TestMenuBarItem::test_menubaritem_hint_geometry`, and the 7px is re-derived from the reference title gaps by `TestMenuTitleSpacingMatchesReference::test_horizontal_margin_is_half_the_mean_gap`. Both GTK sheets already apply it as `padding: 3px 7px` (`menubar > item` in `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `menubar > menuitem` in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`). Firefox's installed `chrome/toolkit/skin/classic/global/menu.css` gives `menubar > menu` on Linux `padding: 0.25em 0.5em; padding-bottom: 1px; border-bottom: 3px solid transparent`, so its title box is font-relative and bottom-heavy; nothing in the sheet overrides it. Record the missing Firefox menu-bar reference and the dated geometry adaptation (2026-10-26).

**Approach and files touched.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: immediately after the `#toolbar-menubar` face rule and before the open-title rule, add `#toolbar-menubar menubar > menu { padding: 3px 7px !important; }`. Add nothing else: no fill, text colour, border, margin or hover declaration. In the header, insert a provenance paragraph after the open-menu-bar paragraph (ending "`chrome/toolkit/skin/classic/global/menu.css` on Linux.") and before the find-field paragraph (starting "No reference shows Firefox's find field"): no reference shows a Firefox menu bar; the title box takes `widgets/menubaritem.svg`'s 3px/7px margins, re-derived from the reference title gaps; Firefox's stock Linux rule is font-relative and bottom-heavy; only the padding is overridden, so the open title's landed `#CCCCFF` fill and bottom border stay.
- `tests/test_firefox_theme.py`: add `"#toolbar-menubar menubar > menu": {"padding": "3px 7px !important"}` to `REQUIRED_RULES` directly before the `[open]` entry. Add `TestFirefoxChrome.test_menubar_title_geometry_matches_the_menubaritem_margins`, which derives the top/bottom and left/right hint sizes with `MENUBARITEM_SVG` from `support.desktoptheme_paths`, `parse_svg` from `support.svg_case` and `rect_geometry` from `svg_assertions` (as `tests/test_desktoptheme_menubaritem.py` does) and asserts the sheet's padding, so the SVG is the source and a sheet/SVG drift fails. Extend `test_menubar_open_title_paint_is_scoped_to_the_open_title`: its title-rule set becomes exactly `#toolbar-menubar`, the new base title rule and the `[open]` rule; the base rule's declaration names are exactly `{"padding"}`; the open rule keeps its two declarations. Add provenance entries after `"not-found and flash states stay"` and before `"No reference shows Firefox multi-selected tabs"`: `"No reference shows Firefox's menu bar titles"`, `"TestMenuBarItem.test_menubaritem_hint_geometry"`, `"TestMenuTitleSpacingMatchesReference"`, `"padding: 0.25em 0.5em"`, `"chrome/toolkit/skin/classic/global/menu.css"` and `"platform geometry adaptation 2026-10-26"`.
- `docs/invariants.md`: extend the existing open-menu-bar-title row under `## firefox` so its guarantee also covers the title box's 3px/7px padding, its test list adds the new geometry test, and its provenance names the `menubaritem.svg` hint geometry and reference title gaps, the stock Firefox Linux padding and the missing Firefox menu-bar reference; keep its statement that declaration checks do not establish rendered pixels.

**Acceptance criteria.**
- `REQUIRED_RULES` validation fails when the base title rule is missing, its padding is not `3px 7px !important`, or it gains another declaration.
- The geometry test fails when the sheet's padding differs from the menubaritem SVG's normal-hint top/bottom and left/right margins.
- The scope test fails when any selector other than `#toolbar-menubar`, the base title rule and the open-title rule targets a menu-bar title.
- An idle, hovered or open title keeps its inherited black text; the open title keeps its `#CCCCFF` fill and `#CCCCFF` bottom border; the `#toolbar-menubar` face and etched bottom rule, the toolbar buttons, tabs, sidebar, menus, find bar, search field, tooltips, results rows and status panel keep their current paints.
- `make check` passes without Firefox or a new dependency, the palette hex set is unchanged, and implementation stays within these three files. Report declaration validation separately from live browser rendering.

## Done

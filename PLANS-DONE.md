# Done plans

Finished plans, newest first, moved here by tumwater from PLANS.md's `## Done`. This file
only grows: search it with grep, or read one entry by its line range. Never read it whole.

## Done

### Retire the `real-run-needed` validation gap with a bounded-run ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: real-run-needed` tag, 5 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Five Fixed entries in BUGS-FIXED.md carry `gap: real-run-needed` — confirming the failure needed a real bounded run because no offline test covered it. Three are prose records from 2026-10-23: each MemoryError on an oversize Firefox INI, GTK config or Firefox profile file now has a sparse-file cap test pinning the same bound offline. Two are older one-line bullets whose fixes now have offline install tests: the still-selected color-scheme warning and the scheme filename that KDE must be able to resolve on restart. Add the fourth validation-gap ledger, mirroring the `no-observability`, `unclear-invariant` and `no-fake` ones, so every record names the test that now confirms it offline and the suite refuses a new uncovered `real-run-needed` record instead of letting the tag grow.

**Cited entries.** The five `gap: real-run-needed` records in BUGS-FIXED.md:
- "An oversize Firefox profile-discovery INI file crashes with a MemoryError", reproduced by `tests/test_firefox_install.py::TestProfileResolution::test_an_oversize_ini_file_is_refused_by_name`.
- "An oversize GTK settings or user-CSS file crashes the GTK selection with a MemoryError", reproduced by `tests/test_gtk_apply.py::TestUnreadableConfig::test_apply_refuses_an_oversize_settings_file_before_writing_anything` and `tests/test_gtk_apply.py::TestUnreadableConfig::test_remove_refuses_an_oversize_user_css_before_clearing_anything`.
- "An oversize Firefox profile file crashes the installer with a MemoryError", reproduced by `tests/test_firefox_install.py::TestInstall::test_an_oversize_user_chrome_is_refused_by_name` and `tests/test_firefox_install.py::TestInstall::test_an_oversize_user_js_is_refused_by_name`.
- "Uninstalling the scheme while it is selected leaves KDE warning `Could not find color scheme \"MacOS8\"`", reproduced by `tests/test_colorscheme_install.py::TestInstall::test_make_uninstall_warns_when_the_removed_scheme_is_still_selected`.
- "`plasma-apply-colorscheme` writes a scheme ID that does not survive a restart", reproduced offline by `tests/test_colorscheme_install.py::TestInstall::test_make_install_names_the_scheme_after_its_source_basename` (the basename is what KDE resolves on restart); the live `TestRestartRoundTrip` test stays skipped when the Plasma CLI is absent.

**Approach.**
- `tests/support/validation_gaps.py`: add `REAL_RUN_NEEDED_BASELINE = 5`, a `REAL_RUN_NEEDED_REPRODUCTIONS` tuple reusing `Reproduction` with one entry per cited record (markers match the prose heading or the older bullet), a `real_run_needed(records)` filter and a `real_run_needed_reproduction(record)` lookup, and extend `reproduction_for` to dispatch the tag; update the module docstring to four ledgers.
- `tests/test_validation_gaps.py`: update the module docstring to four ledgers; add `TestRealRunNeededLedger` mirroring `TestNoFakeLedger`, with `test_every_record_names_a_reproduction`, `test_every_entry_names_a_real_test`, `test_every_ledger_entry_covers_a_shipped_record`, `test_the_record_count_does_not_grow` and `test_an_unmatched_mechanism_has_no_reproduction`.
- `docs/invariants.md`: extend the tooling row that names the three existing ledgers to name the `real-run-needed` ledger and `tests/test_validation_gaps.py::TestRealRunNeededLedger`.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 5 `real-run-needed` records; each maps to a `REAL_RUN_NEEDED_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every cited test resolves through `check_reference`; a new `real-run-needed` record without an entry, or a count above 5, fails the suite.
- `tests/invariants.py` accepts the extended tooling row and `make check` is green.

### Platinum GTK secondary chrome: paint the tooltip, menu separator and frame (planned 2026-10-23 by the plan role; independent of the waiting Firefox chrome plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets paint windows, header bars, buttons, entries, tabs, menus, scroll bars, progress bars, scales and toolbars, but they leave `GtkTooltip`, `GtkSeparatorMenuItem` and `GtkFrame` to GTK's generic rendering, so a tooltip, a menu separator and a group box still draw the toolkit's own rounded greys. Paint them from the Platinum art the theme already ships: the flat `#FFFFCC` tooltip face with a 1px `#000000` outline (matching `widgets/tooltip.svg`), the etched `#888888` over `#FFFFFF` menu separator (matching `widgets/line.svg`), and the sunken 1px `#000000` frame with the `#999999` inner shadow the entry and trough rules already use. No reference screenshot shows a GTK widget, so the geometry is this theme's adaptation; the only palette value the sheets do not already carry is the already-pinned `TOOLTIP_FACE` from `tests/support/platinum_palette.py`, and every other declaration reuses a token the sheet already names.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the `menuitem:hover` rules and before `scrollbar`, add:
  - `tooltip` with `background-color: #FFFFCC`, `color: #000000`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: none` and `padding: 2px 4px`; `tooltip.background` with `background-color: #FFFFCC` and `background-clip: padding-box`.
  - `menu separator, .menu separator` with `background-color: #888888`, `border: 0`, `border-bottom: 1px solid #FFFFFF`, `margin: 2px 0`, `min-height: 1px` and `padding: 0`.
  - `frame > border, .frame` with `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: inset 1px 1px #999999`, `margin: 0` and `padding: 0`.
  - Extend the header provenance paragraph to name the `#FFFFCC` tooltip face pinned by `tests/support/platinum_palette.py` beside the existing `#888888` separator sentence.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add the same tooltip and frame rules, and the GTK 4 menu selector `popover separator, popover.background separator` (the selector the installed Breeze GTK 4 sheet uses for menu separators) with the same separator declarations, after the `popover.menu modelbutton` rules and before the scrollbar rules. Extend its header provenance paragraph the same way.
- `tests/test_gtk_theme.py`: import `TOOLTIP_FACE` from `support.platinum_palette`, add it to the expected set in `test_only_palette_hex_literals`, and add `test_tooltip`, `test_menu_separator` and `test_frame` pinning every declaration above for both menu selector forms (`menu separator`, `.menu separator`) and both frame selector forms (`frame > border`, `.frame`).
- `tests/test_gtk4_theme.py`: import `TOOLTIP_FACE`, add it to `test_only_palette_hex_literals`, and add matching `test_tooltip`, `test_menu_separator` (for `popover separator` and `popover.background separator`) and `test_frame` methods.
- `docs/invariants.md`: extend both `## gtk` guarantee sentences (GTK 3 and GTK 4) to name the tooltip, menu-separator and frame rules; keep their no-reference-screenshot provenance exception and add that the tooltip face is the classic Platinum `[Colors:Tooltip]` role no screenshot shows.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the tooltip, menu-separator and frame rules, and the new test methods fail if any selector or declaration changes.
- `test_only_palette_hex_literals` in both suites accepts the sheets with `TOOLTIP_FACE` added and rejects any other new hex literal; the GTK 4 `test_stands_alone` still finds no `@import` and no `url(`, and no selector is universal.
- `tests/invariants.py` accepts the updated `## gtk` rows and `make check` is green.

### Firefox Platinum chrome: paint the toolbar button states, bookmark items, menu separators and the find bar (planned 2026-10-23 by the plan role; independent of the waiting GTK meters plan) — done 2026-10-23 by the feature role

**Goal.** The Firefox sheet paints the tab strip, navigation bar, bookmarks-bar background, menus and status panel, but it leaves Firefox's own rounded hover and pressed washes on the toolbar buttons, rounded highlights on bookmarks-bar items, the stock grey menu separator, and the default find bar. Paint those surfaces with the pinned Platinum values the sheet already uses: the #EEEEEE trough as the hover wash, the #CCCCFF selection as the pressed/open fill, the raised bevel (`inset 1px 1px #FFFFFF, inset -1px -1px #999999`) on the hovered button, the etched #888888/#FFFFFF rule from `widgets/line.svg`, the #DDDDDD face for the find bar and the white sunken field with its #999999 shadow for its text box. No reference screenshot shows Firefox chrome, so the geometry is this theme's adaptation of the Platinum controls; the new rules introduce no new hex literal.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`:
  - Extend the `:root` block with Firefox's toolbarbutton variables: `--toolbarbutton-border-radius: 0 !important`, `--toolbarbutton-background-color-hover: #EEEEEE !important` and `--toolbarbutton-background-color-active: #CCCCFF !important`.
  - Add `toolbarbutton:hover:not([disabled="true"])` with the raised bevel box-shadow and `toolbarbutton:hover:active:not([disabled="true"])` with `box-shadow: inset 1px 1px #999999 !important`.
  - Add one rule `#PersonalToolbar .bookmark-item:hover, #PersonalToolbar .bookmark-item[open]` with `background-color: #CCCCFF !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #FFFFFF !important`.
  - Add `menupopup > menuseparator` with `padding: 0 !important` and `margin: 2px 0 !important`, and `menupopup > menuseparator::before` with `border-top: 1px solid #888888 !important` and `border-bottom: 1px solid #FFFFFF !important` (the etched separator, matching `widgets/line.svg`).
  - Add `findbar` with `background-color: #DDDDDD !important` and `border-top: 1px solid #000000 !important`, and `findbar .findbar-textbox:not([status="notfound"]):not([flash="true"]):not(:focus)` with `background-color: #FFFFFF !important`, `border: 1px solid #000000 !important`, `border-radius: 0 !important` and `box-shadow: inset 1px 1px #999999 !important`; the guards leave Firefox's own red not-found wash, yellow flash and focus ring in place.
  - Extend the header's provenance paragraph to name the toolbar button states, bookmark items, menu separators and find bar among the sheet's adapted surfaces.
- `tests/test_firefox_theme.py`: add the three `:root` variables to `REQUIRED_RULES[":root"]` and add `REQUIRED_RULES` entries for the toolbar button states, bookmark-item, menuseparator and `::before`, findbar and findbar-textbox selectors, reusing the imported `BLACK`, `FACE`, `GREY`, `SELECTION`, `TROUGH` and `WHITE` values and importing `RAISED_BEVEL` from `support.gtk_theme_spec`; leave `test_palette_is_exact`'s expected set unchanged (every new declaration uses a value it already accepts).
- `docs/invariants.md`: extend the `## firefox` standalone-sheet guarantee sentence to name the toolbar button states, bookmark items, menu separators and find bar; keep its no-reference-screenshot provenance exception.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The sheet carries the pinned `:root` variables and the bookmark-item, menuseparator and findbar rules, and `test_required_rules` fails if any selector or declaration changes.
- `test_palette_is_exact` still passes with the same hex set, the sheet still contains no at-rule or import, and no selector is universal.
- `tests/invariants.py` accepts the updated `## firefox` row and `make check` is green.

### Platinum GTK meters and sliders: paint the progress-bar track and fill and the scale trough and thumb (planned 2026-10-23 by the plan role; independent of the waiting pointer plan) — done 2026-10-23 by the feature role

**Goal.** Both opt-in GTK sheets cover windows, buttons, entries, tabs, menus, scroll bars and toolbars, but they leave `GtkProgressBar` and `GtkScale` to the Adwaita fallback, so a file-copy meter or a volume slider still draws Adwaita's rounded blue track and thumb. Paint them from the Platinum art the theme already ships: the flat #EEEEEE trough with its 1px #000000 outline that `widgets/scrollbar.svg` and `widgets/slider.svg` ship, the #999999 sunken shadow `widgets/lineedit.svg` uses, the flat #CCCCFF selection for the progress fill (the reference progress gradient's middle row is `#CBCCFF`), and the desktop theme's raised #DDDDDD slider thumb from `widgets/slider.svg`. No reference screenshot shows a GTK widget, so the geometry stays this theme's adaptation, but every colour is an existing pinned Platinum palette value and the sheets stay standalone (no `@import`, no `url()`).

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after the scrollbar rules, add these rules. Do not introduce a new hex literal anywhere in the file, including the header comment: `test_only_palette_hex_literals` scans the raw GTK 3 sheet text.
  - `progressbar trough`: `background-color: #EEEEEE; background-image: none; border: 1px solid #000000; border-radius: 0; box-shadow: inset 1px 1px #999999; min-height: 10px; min-width: 10px;`
  - `progressbar progress`: `background-color: #CCCCFF; background-image: none; border: 0; border-radius: 0; box-shadow: none; margin: 0;`
  - `progressbar progress:disabled`: `background-color: #999999;`
  - `scale trough`: the same declaration block as `progressbar trough` but `min-height: 6px; min-width: 6px;` (the desktop slider's 6px track).
  - `scale fill, scale highlight`: `background-color: transparent; background-image: none; border: 0; border-radius: 0; box-shadow: none; margin: 0;` (the desktop slider deliberately omits its `groove-highlight`, so the trough stays one uniform Platinum bar and the thumb marks the value).
  - `scale slider`: `background-color: #DDDDDD; background-image: none; border: 1px solid #000000; border-radius: 0; box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999; margin: -5px;`
  - `scale.horizontal slider`: `min-width: 12px; min-height: 16px;` and `scale.vertical slider`: `min-width: 16px; min-height: 12px;` (the desktop theme's two handle shapes).
  - `scale slider:hover, scale slider:active`: the same face, outline, square corners and bevel as the base `scale slider`, so no fallback hover colour shows through.
  - `scale slider:disabled`: `background-color: #DDDDDD; border: 1px solid #999999; box-shadow: none;`
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add the same declarations with the GTK 4 node paths, immediately after the scrollbar rules:
  - `progressbar > trough` and `progressbar > trough > progress` (plus `progressbar > trough > progress:disabled`).
  - `scale > trough`, `scale > trough > fill, scale > trough > highlight`, `scale > trough > slider` (with `margin: -5px`), `scale.horizontal > trough > slider`, `scale.vertical > trough > slider`, `scale > trough > slider:hover, scale > trough > slider:active`, and `scale > trough > slider:disabled`, with the same values as the GTK 3 rules.
- `tests/test_gtk_theme.py`: add `test_progressbar` pinning the trough, fill and disabled-fill rules, and `test_scale` pinning the trough, the transparent fill/highlight, the base/hover/active/disabled thumb, and the 12x16 and 16x12 orientation sizes. Reuse the already-imported `BLACK`, `FACE`, `GREY`, `SELECTION`, `TROUGH` and `WHITE` values and `RAISED_BEVEL` from `support.gtk_theme_spec`.
- `tests/test_gtk4_theme.py`: add the matching `test_progressbar` and `test_scale` against the GTK 4 selectors and the same values; `DEFINED_COLOURS` is unchanged.
- `docs/invariants.md`: in the `## gtk` section, extend the GTK 3 and GTK 4 guarantee sentences to name the progress-bar and scale rules (and keep their existing no-reference-screenshot provenance exception).

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the pinned progress-bar and scale rules, and `test_only_palette_hex_literals` still passes unchanged in both suites (every hex in either sheet remains a value that test already accepts; the new declarations use only `#000000`, `#999999`, `#DDDDDD`, `#EEEEEE`, `#FFFFFF` and `#CCCCFF`).
- The new tests fail if a track, fill, thumb face, outline, bevel, square corner, orientation size or state rule changes, and the GTK 4 sheet still passes `test_stands_alone` (no `@import`, no `url()`).
- `tests/invariants.py` accepts the updated `## gtk` rows and `make check` is green.

### Platinum pointer roles: ship the context-menu pointer and alias the resize, hand and cell roles (planned 2026-10-23 by the plan role; independent of the landed pager plan) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` names the Platinum pointers for the arrow, text, hand, busy, move, resize, crosshair, forbidden, drag-and-drop, help, progress, pencil and zoom roles, but several common Xcursor names still come from the fallback Breeze set: right-click uses `context-menu`, table and splitter borders use `col-resize`/`split_h` and `row-resize`/`split_v`, panning uses `openhand`/`closedhand`, and cell selection uses `cell`/`plus`. Add one new Platinum pointer for `context-menu` (the arrow beside a small menu panel) and alias the role-equivalent names to the already-shipped resize, grab and copy-plus art, so those roles stop changing shape when the Platinum cursor theme is selected. No reference screenshot shows a pointer, so the art stays our own `#000000`-face/`#FFFFFF`-outline drawing; the names and their Breeze byte groups are X/KDE-required values read from `/usr/share/icons/breeze_cursors/cursors` (`alias` and `link` share one file there, as do `cell` and `plus`, `col-resize` and `split_h`, `row-resize` and `split_v`, `openhand` and `grab`, and `closedhand` and `grabbing`).

**Approach.**
- `tools/cursor_art.py`: add `CONTEXT_MENU_HOTSPOT = (1, 1)` and `CONTEXT_MENU_GRID`, the arrow with a white-faced, black-bordered menu panel at x=8..14, y=9..14 carrying two black text bars:

  ```python
  CONTEXT_MENU_GRID = (
      "...             ",
      ".#..            ",
      ".##..           ",
      ".###..          ",
      ".####..         ",
      ".#####..        ",
      ".######..       ",
      ".#######..      ",
      ".########.      ",
      "....##..#######.",
      "   .##..#.....#.",
      "   .##..#.###.#.",
      "   .##..#.....#.",
      "   .##..#.##..#.",
      "   .##..#######.",
      "   ....         ",
  )
  ```

  Append `("context-menu", CONTEXT_MENU_GRID, CONTEXT_MENU_HOTSPOT, ())` to `CURSORS`, and extend the existing alias tuples: `size_hor` gains `col-resize` and `split_h`; `size_ver` gains `row-resize` and `split_v`; `dnd-copy` gains `cell` and `plus`; `grab` gains `openhand`; `grabbing` gains `closedhand`. Update the module docstring: the package ships twenty canonical pointers, and list `context-menu` and the new aliases.
- Run `python3 tools/make_cursors.py` to write `theme/icons/org.macos8.desktop/cursors/context-menu` and the eight new alias files. The alias files must be byte-identical to their canonical cursor, and the existing files must keep their bytes.
- `tests/test_cursors_theme.py`: add `context-menu` to `CANONICAL`, `ALIASES` (empty), `HOTSPOTS` (16 `(1, 1)`, 24 `(2, 2)`, 32 `(2, 2)`) and `PINNED_PIXELS` (face `(1, 1)`, outline `(0, 0)`); add the new aliases to the matching `ALIASES` tuples. Leave `TRANSPARENT_CORNER_CURSORS` unchanged: like `help` and `progress`, the context-menu pointer keeps the arrow's white top-left corner. Add `test_context_menu_pins_the_menu_panel`: at 16px black at `(1, 1)`, `(8, 9)`, `(8, 10)`, `(14, 10)`, `(10, 11)`, `(10, 13)`, `(11, 13)` and `(8, 14)`; white at `(0, 0)`, `(1, 9)`, `(2, 9)`, `(3, 9)`, `(7, 10)`, `(9, 10)` and `(15, 10)`. Extend `test_dnd_aliases_reuse_the_landed_glyphs` with `cell`/`plus` -> `dnd-copy`, `col-resize`/`split_h` -> `size_hor`, `row-resize`/`split_v` -> `size_ver`, `openhand` -> `grab` and `closedhand` -> `grabbing`.
- `tests/test_icon_theme.py`: add `context-menu` and the eight new alias names to `SHIPPED_CURSORS`, so the installed-package inventory test sees them.
- `README.md`: in the cursor sentence, name the new `context-menu` pointer and add each new alias to its existing group (`cell`, `plus` with `dnd-copy`; `col-resize`, `split_h` with `size_hor`; `row-resize`, `split_v` with `size_ver`; `openhand` with `grab`; `closedhand` with `grabbing`), and narrow the fallback sentence to the roles the theme still does not name.
- `docs/invariants.md`: extend the `icons` cursor row's canonical and alias lists with the new names; keep the provenance exception that no reference screenshot shows a pointer and that the names and byte groups are X/KDE-required.

**Files touched.** `tools/cursor_art.py`, `theme/icons/org.macos8.desktop/cursors/context-menu` and eight new alias files (generated), `tests/test_cursors_theme.py`, `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `cursors/context-menu` exists at nominal sizes 16, 24 and 32, with the hotspot at the arrow tip and a fresh-generator result; the focused pixel test fails if the menu panel or its text bars move.
- `cell`, `plus`, `col-resize`, `split_h`, `row-resize`, `split_v`, `openhand` and `closedhand` are byte-identical to `dnd-copy`, `size_hor`, `size_ver`, `grab` and `grabbing` as mapped above, and `tests/test_icon_theme.py` sees every new file.
- The README and the `icons` invariant row name the new pointer and aliases, `tests/invariants.py` accepts the row, and `make check` is green.

### Platinum virtual-desktop pager: ship `widgets/pager.svg` for the optional Pager applet (planned 2026-10-23 by the plan role) — done 2026-10-23 by the feature role

**Goal.** The optional Pager (`org.kde.plasma.pager`; `org.kde.plasma.activitypager` shares its QML through `X-Plasma-RootPath`) draws every virtual-desktop cell with `KSvg.FrameSvgItem imagePath: "widgets/pager"` in `contents/ui/main.qml`, one frame per prefix `normal`, `hover` and `active`. The theme ships no `widgets/pager.svg`, so KSvg falls back to Breeze's pager frames and a Pager added to the Platinum menu bar draws Breeze's cells. Add a Platinum pager frame: an idle desktop as a thin grey outline, a hovered desktop as the translucent pale grey view trough, and the current desktop as the translucent lavender selection fill. The reference set shows no virtual-desktop pager, so this is our own Platinum art; the three prefixes are KDE-required and the colours reuse grounded palette tokens.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg` on a 12x9 canvas: a 1px border around a 10x7 centre tile. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover` and `active`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups (39 ids besides `hint-tile-center`).
- Hints: `hint-tile-center` at (1,1,10,7); top/bottom margins at (1,0,10,1)/(1,8,10,1); left/right margins at (0,1,1,7)/(11,1,1,7). Slice groups translate to (1,0), (1,8), (0,1), (11,1), (1,1), (0,0), (11,0), (0,8) and (11,8).
- Paint the states as follows: `normal` is a 1px `#999999` border on its eight edge and corner tiles with a transparent 0.01-opacity `#FFFFFF` placeholder for the centre (an idle desktop is an outlined cell on the panel face); `hover` is the same `#999999` border around an `#EEEEEE` centre at `fill-opacity="0.2"`; `active` is a 1px `#000000` border around a `#CCCCFF` centre at `fill-opacity="0.6"`. Each colour is a `fill` attribute; the centre placeholder uses `style` plus `fill-opacity="0.01"`, the menubaritem convention, so the parsed fill set stays the art colours. The Pager draws each desktop's window previews in `clipRect` at z:1 with the frames above at z:2-4, so opaque hover and active centres would hide them; 0.2 and 0.6 are the installed default theme's centre opacities.
- `tests/support/desktoptheme_paths.py`: add `PAGER_SVG = os.path.join(PACKAGE, "widgets", "pager.svg")`.
- `tests/test_desktoptheme.py`: import `PAGER_SVG` and add `("pager.svg", PAGER_SVG, 12, 9)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_pager.py` with `TestPager(NineSliceCase)`: set `SVG_PATH = PAGER_SVG` and `PREFIXES = ("normal", "hover", "active")`; pin the exact 40-id set and the exact hint map with `rect_geometry`; pin `normal`'s eight `#999999` edge tiles plus its fill-less centre; pin every `hover` tile to `#999999` on the border and `#EEEEEE` in the centre; pin every `active` tile to `#000000` on the border and `#CCCCFF` in the centre; pin each centre's fill and `fill-opacity` (`normal` has no `fill` attribute, only the `style` `#FFFFFF` placeholder at `0.01`, while `hover` pins `#EEEEEE`/`0.2` and `active` pins `#CCCCFF`/`0.6`) and the whole file's `fill-opacity` set to exactly `{"0.01", "0.2", "0.6"}`; pin the parsed `fill` set to exactly `{"#000000", "#999999", "#CCCCFF", "#EEEEEE"}`. Use `nine_slice_tile_sizes(12, 9, 1, 1, 1, 1)` and `assert_slice_pixels` so a one-pixel-short rect or a recoloured tile fails.
- `README.md`: after the `widgets/menubaritem.svg` sentence, add that `widgets/pager.svg` draws the optional Pager's virtual-desktop cells: an idle `#999999` outline, a translucent `#EEEEEE` hover wash and the current desktop's translucent `#CCCCFF` selection, as one 1px-border nine-slice shared by such a panel applet.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/pager.svg`, citing `tests/test_desktoptheme_pager.py::TestPager`; its provenance exception records that no reference screenshot shows a virtual-desktop pager, the `normal`/`hover`/`active` prefixes are KDE-required (read from the installed Pager's `contents/ui/main.qml`), the 12x9 tile is this theme's own, the 0.2 and 0.6 hover/active centre opacities are the installed default theme's (its frames sit above the window previews, so opaque centres would hide them), and the colours reuse the grounded bevel, trough, outline and selection anchors.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/pager.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_pager.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `pager.svg` exists on a 12x9 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the geometry above; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders eight `#999999` border tiles around a fill-less centre, `hover` renders `#999999` borders around an `#EEEEEE` centre at 0.2 opacity, and `active` renders `#000000` borders around an `#CCCCFF` centre at 0.6 opacity; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The README names the new widget and its three states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum task-manager buttons: ship `widgets/tasks.svg` for the optional Task Manager applet (planned 2026-10-23 by the plan role; independent of the waiting icon series) — done 2026-10-23 by the feature role

**Goal.** The default layout draws the window list with `widgets/menubaritem.svg`, but the optional Task Manager (`org.kde.plasma.taskmanager`) draws every task through `KSvg.FrameSvgItem imagePath: "widgets/tasks"` (`Task.qml`, `main.qml`, `TaskProgressOverlay.qml`, `GroupExpanderOverlay.qml`). The theme ships no `widgets/tasks.svg`, so KSvg falls back to Breeze's task backgrounds and a Task Manager added to the Platinum menu bar draws Breeze task items instead of Platinum ones. Add the missing nine-slice and its four group-expander arrows. The reference set shows no KDE task manager, so this is our own Platinum art; the element names are KDE-required and the colours reuse the already-grounded tokens (#CCCCFF selection, #FFFFCC tooltip, #999999 bevel, #FFFFFF placeholder).

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg` on the same 20x12 canvas and 7px left/right, 3px top/bottom, 6x6-centre contract as `widgets/menubaritem.svg`. It declares exactly these ids: `hint-tile-center`; for each prefix `normal`, `hover`, `focus`, `attention`, `minimized` and `progress`, the four `-hint-{top,bottom,left,right}-margin` rects and the nine `-{top,bottom,left,right,center,topleft,topright,bottomleft,bottomright}` slice groups; and `group-expander-{top,bottom,left,right}`.
- Every prefix's hints and slices use the menubaritem geometry: `hint-tile-center` at (7,3,6,6); top/bottom hints at (7,0,6,3)/(7,9,6,3); left/right hints at (0,3,7,6)/(13,3,7,6); slice groups translated to (7,0), (7,9), (0,3), (13,3), (7,3), (0,0), (13,0), (0,9) and (13,9).
- Paint the states as follows: `normal` is the transparent 0.01-opacity #FFFFFF placeholder in all nine tiles (an idle task shows the menu-bar face); `hover` and `focus` are flat #CCCCFF in every tile; `attention` is flat #FFFFCC in every tile; `minimized` is the placeholder in six tiles, but `minimized-bottom`, `minimized-bottomleft` and `minimized-bottomright` each paint a 2px #999999 rule at the bottom of their 3px band (local y=1, height 2; the bottom tile is 6px wide, the corner tiles 7px wide); `progress` is the same six placeholders with a 2px #CCCCFF bottom rule. The transparent states keep the `fill-opacity="0.01"` placeholder convention so the existing no-fill helpers read them as empty.
- Ship only the bare state prefixes. `TaskTools.taskPrefix` in the installed task manager's `code/tools.js` returns `[edge-prefixed, bare]` for every state, and `taskPrefixHovered` appends `hover` before the base state, so the bare `normal`/`hover`/`focus`/`attention`/`minimized`/`progress` elements resolve on a top, bottom, left or right panel without duplicating the art four ways. The group overlay is the exception: it names `elementId: "group-expander-<edge>"` directly, so ship all four arrows.
- Draw each group expander as an 8x8 black triangle: top `M1 6 L4 3 L7 6 Z`, bottom `M1 2 L4 5 L7 2 Z`, left `M6 1 L3 4 L6 7 Z`, right `M2 1 L5 4 L2 7 Z`.
- `tests/support/desktoptheme_paths.py`: add `TASKS_SVG = os.path.join(PACKAGE, "widgets", "tasks.svg")`.
- `tests/test_desktoptheme.py`: import `TASKS_SVG` and add `("tasks.svg", TASKS_SVG, 20, 12)` to `SVG_CANVASES`, so the shared root-canvas, unique-id, self-containment and registry tests cover the new file.
- Add `tests/test_desktoptheme_tasks.py` with `TestTasks(NineSliceCase)`: set `SVG_PATH = TASKS_SVG`, `PREFIXES = ("normal", "hover", "focus", "attention", "minimized", "progress")` and `EXTRA_GROUPS` mapping the four expander ids to (0,0); pin the exact hint map, the exact id set, the flat fills (`hover`/`focus` #CCCCFF, `attention` #FFFFCC), the `normal` placeholders, the minimized/progress bottom rules pixel by pixel, and each expander's path and fill.
- `README.md`: in the desktop-theme widget list, after the `widgets/menubaritem.svg` sentence, add that `widgets/tasks.svg` draws an optional Task Manager's idle (transparent), hover/focus (#CCCCFF), attention (#FFFFCC), minimized (#999999 rule) and progress (#CCCCFF rule) task faces as one 7px/3px nine-slice shared by every panel edge, plus the four group-expander arrows.
- `docs/invariants.md`: add a `## desktoptheme` row for `widgets/tasks.svg`, citing `tests/test_desktoptheme_tasks.py::TestTasks`; its provenance exception records that no reference screenshot shows a KDE task manager, the six state prefixes and four expander ids are KDE-required (read from the installed task manager's `Task.qml`, `TaskProgressOverlay.qml` and `GroupExpanderOverlay.qml`), and the colours reuse the grounded selection, tooltip and bevel tokens.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tasks.svg`, `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, new `tests/test_desktoptheme_tasks.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- `tasks.svg` exists on a 20x12 canvas and declares exactly the id set above; `tests/test_desktoptheme.py`'s registry sees it, and a missing or extra prefix, hint or slice id fails the id-set test.
- Every prefix's four hints and nine slice groups sit at the menubaritem geometry; moving a group or hint off its tile fails `NineSliceCase.test_tiles_placed_by_margins` or the hint-map test.
- `normal` renders no fill (0.01-opacity #FFFFFF placeholders), `hover` and `focus` render flat #CCCCFF, `attention` flat #FFFFCC, and `minimized`/`progress` render a 2px #999999/#CCCCFF rule across the bottom band with transparent tiles above it; changing one pixel, dropping a state or recolouring a slice fails the pixel tests.
- The four `group-expander-*` elements are 8x8 black triangles with the paths above; removing or repointing one fails.
- The README names the new widget and its five states, and `tests/invariants.py` accepts the new `## desktoptheme` row.
- `make check` is green.

### Platinum icon theme, part 2/2: ship 16x16 and 22x22 renditions of the hard-disk and document icons (planned 2026-10-23 by the plan role; "requires part 1/2 landed") — done 2026-10-23 by the feature role

**Goal.** After part 1/2 the places icons have small-size renditions, but `drive-harddisk` and `text-x-generic` still ship only at 32x32, and `index.theme` declares no 16x16 or 22x22 devices or mimetypes directory. Add four renditions and the four directory declarations so the hard disk and document icons also have purpose-drawn art at menu, tree-view and small desktop sizes. The art is our own drawing on the same four-fill Platinum palette as the places art; the reference set has no pixel ground truth for the icon theme, as `docs/invariants.md`'s `## icons` row records.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the declared size:
  - `theme/icons/org.macos8.desktop/16x16/devices/drive-harddisk.svg` (nine elements): rect `x=1 y=3 width=14 height=10` `#000000`; rect `x=2 y=4 width=12 height=8` `#DDDDDD`; rect `x=2 y=4 width=12 height=1` `#FFFFFF`; rect `x=2 y=4 width=1 height=8` `#FFFFFF`; rect `x=2 y=11 width=12 height=1` `#999999`; rect `x=13 y=4 width=1 height=8` `#999999`; rect `x=3 y=7 width=7 height=3` `#000000`; rect `x=4 y=8 width=5 height=1` `#FFFFFF`; circle `cx=12 cy=9 r=1` `#000000`.
  - `theme/icons/org.macos8.desktop/22x22/devices/drive-harddisk.svg` (nine elements): rect `x=2 y=4 width=18 height=15` `#000000`; rect `x=3 y=5 width=16 height=13` `#DDDDDD`; rect `x=3 y=5 width=16 height=2` `#FFFFFF`; rect `x=3 y=5 width=1 height=13` `#FFFFFF`; rect `x=3 y=17 width=16 height=1` `#999999`; rect `x=18 y=5 width=1 height=13` `#999999`; rect `x=4 y=10 width=8 height=4` `#000000`; rect `x=5 y=11 width=6 height=2` `#FFFFFF`; circle `cx=15 cy=12 r=2` `#000000`.
  - `theme/icons/org.macos8.desktop/16x16/mimetypes/text-x-generic.svg` (six elements): path `M3 1 h7 l3 3 v10 H3 Z` `#000000`; path `M4 2 h5 l3 3 v8 H4 Z` `#FFFFFF`; path `M9 2 L12 2 L12 5 Z` `#DDDDDD`; rect `x=5 y=7 width=6 height=1` `#999999`; rect `x=5 y=9 width=6 height=1` `#999999`; rect `x=5 y=11 width=4 height=1` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/mimetypes/text-x-generic.svg` (six elements): path `M4 1 h10 l4 4 v15 H4 Z` `#000000`; path `M5 2 h8 l4 4 v13 H5 Z` `#FFFFFF`; path `M13 2 L17 2 L17 6 Z` `#DDDDDD`; rect `x=7 y=10 width=8 height=1` `#999999`; rect `x=7 y=13 width=8 height=1` `#999999`; rect `x=7 y=16 width=5 height=1` `#999999`.
- `theme/icons/org.macos8.desktop/index.theme`: append `16x16/devices,16x16/mimetypes,22x22/devices,22x22/mimetypes` to `Directories`, and add four sections with `Size=16`/`Size=22`, `Context=Devices`/`Context=MimeTypes` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the four new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple above, using the existing `_shape` helper and document order. `TestIndex.test_every_shipped_icon_lives_in_a_declared_size_directory` then proves the four new directories are declared.
- `README.md`: in the icon-theme sentence (the lines that currently read `ships our own Platinum-style art for the desktop's hard-disk, folder, document, Trash and full-Trash icons`), add that the package draws these at 32x32 with 16x16 and 22x22 renditions. Do not touch the cursor sentence on the following line.

**Files touched.** `tests/test_icon_theme.py`, `theme/icons/org.macos8.desktop/index.theme`, `README.md`, and four new SVGs under `theme/icons/org.macos8.desktop/16x16/{devices,mimetypes}/` and `22x22/{devices,mimetypes}/`.

**Acceptance criteria.**
- The four files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `index.theme` declares `16x16/devices`, `16x16/mimetypes`, `22x22/devices` and `22x22/mimetypes` in `Directories`, with the matching `Size`, `Context` and `Type` sections; `TestIndex` passes for every shipped icon.
- `ICON_SHAPES` equals `SHIPPED_ICONS`, and each new file's drawing elements equal the tuple above in document order. Deleting an element, changing a coordinate or fill, moving an element or dropping a size fails a test.
- The 32x32 art and the part 1/2 places renditions keep their pinned elements unchanged.
- `README.md` names the 16x16 and 22x22 renditions without claiming a size for the cursor set, and the cursor sentence is untouched.
- `make check` is green.

### Platinum icon theme, part 1/2: ship 16x16 and 22x22 renditions of the folder, directory and Trash icons (planned 2026-10-23 by the plan role; part 2/2 adds the hard-disk and document renditions) — done 2026-10-23 by the feature role

**Goal.** `theme/icons/org.macos8.desktop/index.theme` declares `16x16/places` and `22x22/places`, but those directories hold no `folder`, `inode-directory`, `user-trash` or `user-trash-full` file: the package ships those four names only at 32x32. Add eight pixel-aligned renditions so a menu, tree view or small desktop icon can draw a dedicated Platinum shape at its own size instead of relying on the 32x32 art. The 32x32 art is our own drawing, and `docs/invariants.md`'s `## icons` row records that the reference set has no pixel ground truth for the icon theme; these renditions are our own simplified redraws using only the four pinned palette fills (`#000000` outline, `#DDDDDD` face, `#FFFFFF` top/left bevel, `#999999` bottom/right bevel), not traced from Apple's artwork.

**Approach.**
- Add these files, each an `<svg>` whose `width`, `height` and `viewBox` are the directory's declared size:
  - `theme/icons/org.macos8.desktop/16x16/places/folder.svg` (six elements, in order): path `M1 4 h5 l2 2 h6 v7 H1 Z` `#000000`; path `M2 5 h4 l2 2 h5 v4 H2 Z` `#DDDDDD`; path `M2 5 h4 l2 2 h5 v1 h-5 l-2 -2 h-4 Z` `#FFFFFF`; rect `x=2 y=5 width=1 height=6` `#FFFFFF`; rect `x=2 y=11 width=11 height=1` `#999999`; rect `x=12 y=8 width=1 height=3` `#999999`.
  - `theme/icons/org.macos8.desktop/22x22/places/folder.svg` (six elements): path `M2 6 h7 l3 3 h8 v8 H2 Z` `#000000`; path `M3 7 h6 l3 3 h7 v6 H3 Z` `#DDDDDD`; path `M3 7 h6 l3 3 h7 v1 h-7 l-3 -3 h-6 Z` `#FFFFFF`; rect `x=3 y=7 width=1 height=8` `#FFFFFF`; rect `x=3 y=15 width=16 height=1` `#999999`; rect `x=18 y=10 width=1 height=5` `#999999`.
  - `theme/icons/org.macos8.desktop/16x16/places/inode-directory.svg` and `22x22/places/inode-directory.svg`: the same drawing elements as the matching `folder.svg`, in the same order; only the comment differs, saying the alias shares the folder geometry because Mac OS 8.6 draws one folder shape for both names.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash.svg` (ten elements): rect `x=6 y=1 width=4 height=2` `#000000`; rect `x=7 y=2 width=2 height=1` `#DDDDDD`; rect `x=3 y=3 width=10 height=3` `#000000`; rect `x=4 y=4 width=8 height=2` `#DDDDDD`; rect `x=4 y=4 width=8 height=1` `#FFFFFF`; rect `x=4 y=5 width=8 height=1` `#999999`; path `M5 6 h6 l-1 9 H6 Z` `#000000`; path `M6 7 h4 l-1 7 H7 Z` `#DDDDDD`; rect `x=7 y=8 width=1 height=5` `#999999`; rect `x=8 y=8 width=1 height=5` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash.svg` (twelve elements): rect `x=8 y=1 width=6 height=3` `#000000`; rect `x=9 y=2 width=4 height=2` `#DDDDDD`; rect `x=4 y=4 width=14 height=4` `#000000`; rect `x=5 y=5 width=12 height=3` `#DDDDDD`; rect `x=5 y=5 width=12 height=1` `#FFFFFF`; rect `x=5 y=7 width=12 height=1` `#999999`; path `M6 8 h10 l-1 12 H7 Z` `#000000`; path `M7 9 h8 l-1 10 H8 Z` `#DDDDDD`; rect `x=9 y=11 width=1 height=8` `#999999`; rect `x=10 y=11 width=1 height=8` `#FFFFFF`; rect `x=12 y=11 width=1 height=8` `#999999`; rect `x=13 y=11 width=1 height=8` `#FFFFFF`.
  - `theme/icons/org.macos8.desktop/16x16/places/user-trash-full.svg` (ten elements): the two paper paths path `M6 0 l2 1 l2 -1 l1 4 h-6 Z` `#000000` and path `M7 1 l1 1 l1 -1 l1 3 h-4 Z` `#FFFFFF`, then the `user-trash.svg` elements from its rim outline through its white rib (elements 3-10 above), in the same order.
  - `theme/icons/org.macos8.desktop/22x22/places/user-trash-full.svg` (twelve elements): the two paper paths path `M8 0 l3 2 l3 -2 l1 6 h-8 Z` `#000000` and path `M9 1 l2 1 l2 -1 l1 4 h-6 Z` `#FFFFFF`, then the `22x22/places/user-trash.svg` elements from its rim outline through its last white rib (elements 3-12 above), in the same order.
- `theme/icons/org.macos8.desktop/index.theme`: no change; `16x16/places` and `22x22/places` are already declared with `Size=16`/`Size=22`, `Context=Places` and `Type=Fixed`.
- `tests/test_icon_theme.py`: add the eight new paths to `SHIPPED_ICONS`; add each file to `ICON_SHAPES` with the exact element tuple listed above, using the existing `_shape` helper and the same document order. Extend `TestIconGeometry.test_the_folder_alias_shares_the_folder_art` to compare the `folder.svg` and `inode-directory.svg` drawings at 16x16, 22x22 and 32x32, so the alias cannot drift at a new size.
- `README.md` and `docs/invariants.md`: no change here. The existing README sentence names the icon art without claiming a size, and the existing `## icons` guarantee (`Every shipped icon draws its pinned drawing elements in document order`) already covers these files because `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` requires `ICON_SHAPES` to equal `SHIPPED_ICONS`. Part 2/2 updates the README sentence once the complete set of renditions ships.

**Files touched.** `tests/test_icon_theme.py` and eight new SVGs under `theme/icons/org.macos8.desktop/16x16/places/` and `22x22/places/`.

**Acceptance criteria.**
- The eight files exist; each parses as an SVG whose width, height and viewBox equal 16 or 22, each fill is one of the four `PLATINUM_FILLS`, and each has no script, style, external reference or duplicate id.
- `TestIndex` sees the eight files in its declared directories, `TestIconGeometry.test_the_geometry_registry_covers_every_shipped_icon` sees `ICON_SHAPES` equal to the shipped set, and every new file's drawing elements equal the tuple above in document order.
- The `inode-directory` drawing elements equal the matching `folder` elements at 16x16, 22x22 and 32x32.
- Deleting an element, changing a coordinate or fill, moving an element, dropping a size, or drawing an alias differently from its folder fails a test.
- `make check` is green.

### Platinum cursor set, part 4: ship the help, progress, pencil and zoom pointers (planned 2026-10-23 by the plan role; completes the cursor set after the landed parts 1-3) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers fourteen pointers; README records that `help`,
`progress`, `pencil`, `zoom-in` and `zoom-out` still come from the fallback cursor theme, so the
busy, help, drawing and zoom pointer roles change shape when the Platinum theme is selected. Add
the five remaining pointers and their aliases: `help` (the landed arrow plus a question mark),
`progress` (the arrow plus a small hourglass), `pencil` (a diagonal pencil), and `zoom-in` /
`zoom-out` (a magnifier with a plus or minus). No reference screenshot shows a pointer, so the art
stays our own `#000000`-face/`#FFFFFF`-outline drawing. The canonical names are X/KDE-required and
taken from the installed Breeze set (`/usr/share/icons/breeze_cursors/cursors`): `help`,
`left_ptr_help`, `question_arrow` and `whats_this` share one byte group there with the hash
aliases `5c6cd98b3f3ebcb1f9c7f1c204630408` and `d9ce0ab605698f320427677b458ad60b`; `progress`,
`half-busy` and `left_ptr_watch` share another with the hash aliases
`00000000000000020006000e7e9ffc3f`, `08e8e1c95fe2fc01f976f1e063a24ccd` and
`3ecb610c1bf2410f44200f48c40d3599`; `pencil`, `zoom-in` and `zoom-out` have no aliases there
(checked with `md5sum` over that directory).

**Approach.**
- `tools/cursor_art.py`: add five 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and append them to `CURSORS`; `tools/make_cursors.py` needs no change.
  - `HELP_HOTSPOT = (1, 1)`; `HELP_GRID`: `ARROW_GRID` with a question mark stamped in the free
    right-hand area -- a white plate at columns 9-14, rows 2-8 carrying a black top bar
    `(10,3)-(13,3)`, a right stem `(13,4)-(13,5)`, a curve at `(12,5)` and a black dot `(12,7)`,
    with white at `(12,6)` separating the hook from the dot.
  - `PROGRESS_HOTSPOT = (1, 1)`; `PROGRESS_GRID`: `ARROW_GRID` with a white plate at columns
    9-14, rows 8-14 carrying a black hourglass -- a top bar `(10,9)-(13,9)`, a two-pixel-wide
    neck `(11,10)-(12,12)` and a bottom bar `(10,13)-(13,13)`, with white rows at 8 and 14.
  - `PENCIL_HOTSPOT = (2, 14)`; `PENCIL_GRID`: a two-pixel black shaft on the anti-diagonal
    `x+y = 15`/`16` from the writing tip `(2,14)` to the eraser `(13,2)`, each black edge bounded
    by one white cell; black at `(2,14)`, `(8,7)` and `(12,3)`, white at `(1,14)` and `(13,1)`.
  - `ZOOM_IN_HOTSPOT = (7, 7)` and `ZOOM_OUT_HOTSPOT = (7, 7)`; the two grids share a
    white-outlined black lens ring centred on `(7,7)` (black at `(7,3)`, `(3,7)`, `(11,7)`,
    `(7,11)` and white at `(7,2)`), a black handle along `(11,11)-(13,13)` (black at `(13,13)`),
    and a black plus in the lens at `(7,5)`, `(5,7)`, `(9,7)`, `(7,9)` and `(7,7)`; `ZOOM_OUT_GRID`
    keeps only the horizontal bar of the plus, leaving `(7,5)` and `(7,9)` transparent.
  - Append `("help", HELP_GRID, HELP_HOTSPOT, ("left_ptr_help", "question_arrow", "whats_this",
    "5c6cd98b3f3ebcb1f9c7f1c204630408", "d9ce0ab605698f320427677b458ad60b"))`,
    `("progress", PROGRESS_GRID, PROGRESS_HOTSPOT, ("half-busy", "left_ptr_watch",
    "00000000000000020006000e7e9ffc3f", "08e8e1c95fe2fc01f976f1e063a24ccd",
    "3ecb610c1bf2410f44200f48c40d3599"))`,
    `("pencil", PENCIL_GRID, PENCIL_HOTSPOT, ())`,
    `("zoom-in", ZOOM_IN_GRID, ZOOM_IN_HOTSPOT, ())` and
    `("zoom-out", ZOOM_OUT_GRID, ZOOM_OUT_HOTSPOT, ())` to `CURSORS`.
  - Update `tools/cursor_art.py`'s module docstring: the package ships nineteen canonical cursors, not fourteen, and
    list the new names and their aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with the five names and `ALIASES` with their
  alias tuples (empty for `pencil`, `zoom-in` and `zoom-out`). Add the five names to `HOTSPOTS` --
  `help`/`progress`: `(1,1)` at 16, `(2,2)` at 24, `(2,2)` at 32; `pencil`: `(2,14)`, `(3,21)`,
  `(4,28)`; `zoom-in`/`zoom-out`: `(7,7)`, `(11,11)`, `(14,14)` -- and to `PINNED_PIXELS` (face
  `(1,1)` / outline `(0,0)` for `help` and `progress`; face `(2,14)` / outline `(1,14)` for
  `pencil`; face `(7,7)` / outline `(7,2)` for `zoom-in` and `zoom-out`). Add `pencil`, `zoom-in`
  and `zoom-out` to `TRANSPARENT_CORNER_CURSORS`; `help` and `progress` keep the arrow's white
  top-left corner, so they stay out. The existing `TestCursorSet` loops then cover the new files,
  aliases, hotspots, face/outline pixels and determinism. Add focused tests:
  - `test_help_pins_the_arrow_and_question_mark`: at 16px black at `(1,1)`, `(10,3)`, `(13,5)` and
    `(12,7)`; white at `(0,0)` and `(12,6)`.
  - `test_progress_pins_the_arrow_and_hourglass`: at 16px black at `(1,1)`, `(10,9)`, `(11,10)`,
    `(11,11)`, `(11,12)`, `(12,11)` and `(10,13)`; white at `(12,8)` and `(12,14)`.
  - `test_pencil_draws_a_diagonal_shaft_to_its_writing_tip`: at 16px black at `(2,14)`, `(8,7)`
    and `(12,3)`; white at `(1,14)` and `(13,1)`; all four corners transparent.
  - `test_zoom_in_and_out_differ_only_at_the_plus_arms`: at 16px both have black at `(7,3)`,
    `(3,7)`, `(7,11)` and the handle tip `(13,13)`, and white at `(7,2)`; `zoom-in` is black at
    `(7,5)`, `(5,7)`, `(9,7)` and `(7,9)`, while `zoom-out` is black only at `(5,7)` and `(9,7)`
    and transparent at `(7,5)` and `(7,9)`.
  - `test_help_and_progress_alias_names_reuse_their_canonical`: `left_ptr_help`, `question_arrow`,
    `whats_this` and the two `help` hash names are byte-identical to `help`; `half-busy`,
    `left_ptr_watch` and the three `progress` hash names to `progress`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the fifteen new X names (`help`, `left_ptr_help`, `question_arrow`,
  `whats_this`, `5c6cd98b3f3ebcb1f9c7f1c204630408`, `d9ce0ab605698f320427677b458ad60b`, `progress`,
  `half-busy`, `left_ptr_watch`, `00000000000000020006000e7e9ffc3f`,
  `08e8e1c95fe2fc01f976f1e063a24ccd`, `3ecb610c1bf2410f44200f48c40d3599`, `pencil`, `zoom-in`,
  `zoom-out`) to `SHIPPED_CURSORS`, so the shipped-file registry and the shared install-lifecycle
  list cover them.
- `README.md`: name the five new pointers and their aliases in the cursor sentence, and replace the
  fallback sentence with "Xcursor roles the theme does not name still come from the fallback cursor
  theme".
- `docs/invariants.md`: extend the `## icons` cursor row to name all nineteen canonical files and
  every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`;
  extend the provenance exception: no reference screenshot shows the pointer, the help, progress
  and zoom names are X/KDE-required and taken from the installed Breeze set, and the help/progress
  alias groups follow Breeze's byte groups while `pencil`, `zoom-in` and `zoom-out` have no alias.
- `PLANS.md`: in the scope-drift paragraph, add the help, progress, pencil and zoom pointers to the
  shipped cursor clause, and say Xcursor roles the theme does not name still fall back.

**Files touched.** `tools/cursor_art.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(five canonical names and ten alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the five new canonical files and the ten aliases; running
  it twice leaves every committed cursor byte-identical, and each new canonical parses to three
  chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel and white outline
  pixel, and the pencil and zoom files keep transparent corners.
- The focused tests pin the arrow-plus-question-mark, the arrow-plus-hourglass, the diagonal
  pencil and the plus/minus magnifiers; deleting a grid, dropping a size, moving a hotspot,
  drawing `zoom-out` as a copy of `zoom-in`, or losing the pencil's white outline fails a test.
- `left_ptr_help`, `question_arrow`, `whats_this`, the two `help` hash names, `half-busy`,
  `left_ptr_watch` and the three `progress` hash names are byte-identical to their canonical
  files; the generator writes exactly the fifteen new names into a temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all fifteen new
  names; README and `docs/invariants.md` name them; `tests/invariants.py` accepts the updated
  `## icons` row; the scope-drift clause no longer lists help, progress, pencil or zoom as
  fallback.
- `make check` is green.

### Retire the `no-fake` validation gap with a fixture ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-fake` tag, 16 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Sixteen Fixed entries in BUGS-FIXED.md carry `gap: no-fake` — confirming the failure
needed a fake, shim or manufactured fixture the shipped suite did not have. The shared fixture kit
those records needed now exists (`symlinked_repo` in `tests/support/symlink_fixtures.py`, the
scratch/mutation helpers in `tests/support/checker_scratch.py`, `tests/support/invariants_mutations.py`
and `tests/support/placeholders_mutations.py`, and the chunk builders in
`tests/support/png_fixtures.py`), and the fixes have reproducing tests, but no ledger maps the
records to those fixtures and nothing stops a new `no-fake` record landing uncovered. Add the third
validation-gap ledger, mirroring the `no-observability` and `unclear-invariant` ones, and give the
one hand-assembled PNG stream a named builder, so a future no-fake failure lands with a fixture and
a test instead of growing the tag.

**Cited entries.** The sixteen `gap: no-fake` records in BUGS-FIXED.md:
- Symlink-escape fixtures (7): `tests/placeholders.py`'s `cross_check` reads a symlinked
  `PLACEHOLDERS.md` bare; `tests/invariants.py`'s `cross_check` reads a symlinked register bare;
  `tests/support/checker_mutations.py`'s register reads follow a symlinked register outside the
  repository; The color-scheme provenance test reads `MacOS8.colors` unguarded; The desktop-theme
  copy-identity tests read the secondary SVG copy unguarded; `tests/support/splash_fixtures.py`'s
  `read_qml` follows a symlinked `Splash.qml` outside the repository;
  `tests/support/package_metadata.py`'s `load_metadata` follows a symlinked `metadata.json`
  outside the repository.
- Unreadable / non-UTF-8 / dangling-path fixtures (4): `tests/invariants.py`'s `cross_check` lets
  an unreadable register escape as a bare `OSError`; `tests/support/package_metadata.py` lets an
  unreadable `metadata.json` escape as a bare `OSError`; `tests/placeholders.py` lets an unreadable
  register escape as a bare `OSError`; `tests/placeholders.py` lets a dangling symlink inside
  `theme/` escape as a bare `FileNotFoundError`.
- Process fixtures (2): A FIFO at either Firefox profile-discovery INI file blocks the install;
  A FIFO at a Firefox profile file blocks the install forever.
- Manufactured inputs (3): A palette image with `tRNS` before `PLTE` is accepted;
  `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception; `tests/invariants.py` lets a reference to an unreadable test file escape as an
  unrelated exception.

**Approach.**
- `tests/support/png_fixtures.py`: add `palette_trns_before_plte()`, returning the record's stream
  (`png_stream(ihdr_chunk(1, 1, 3), _chunk(b"tRNS", bytes([0, 128])), _chunk(b"PLTE", bytes([255,
  0, 0, 0, 255, 0])), _chunk(b"IDAT", zlib.compress(bytes([0, 0]))), _chunk(b"IEND", b""))`), so
  the malformed-order case has a named fixture rather than a hand-assembled chunk list.
  `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`
  calls the builder and keeps its two-decoder assertion and its `tRNS chunk before` / `PLTE chunk` /
  `follow` needles.
- `tests/support/validation_gaps.py`: name the third tag in the module docstring; add
  `NO_FAKE_BASELINE = 16`; add `NO_FAKE_REPRODUCTIONS`, reusing the `Reproduction` namedtuple
  (name, markers, reference), with one entry per record — markers name the module and the failure,
  and the reference is the reproducing test:
  - `firefox-ini-fifo` → `tests/test_firefox_install.py::TestProfileResolution::test_a_fifo_at_either_ini_file_is_refused_without_blocking`.
  - `firefox-profile-file-fifo` → `tests/test_firefox_install.py::TestRemove::test_a_fifo_at_either_profile_file_is_refused_without_blocking`.
  - `png-trns-before-plte` → `tests/test_png_malformed.py::TestTrnsColorTypeValidation::test_palette_trns_before_plte_is_refused`.
  - `placeholders-symlinked-register` → `tests/test_placeholders.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `invariants-symlinked-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_refuses_a_symlinked_register_that_escapes`.
  - `checker-mutations-symlinked-register` → `tests/test_checker_mutations.py::TestCheckerMutations::test_register_reads_refuse_a_symlink_escape`.
  - `colorscheme-provenance-symlink` → `tests/test_containment.py::TestReadText::test_rejects_a_symlink_that_escapes_the_root`.
  - `desktoptheme-copy-symlink` → `tests/test_containment.py::TestReadBytes::test_rejects_a_symlink_that_escapes_the_root`.
  - `splash-symlink` → `tests/test_splash_qml.py::TestSplashQmlContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `metadata-symlink` → `tests/test_package_metadata.py::TestLoadMetadataContainment::test_rejects_a_symlink_that_escapes_the_repository`.
  - `invariants-unreadable-register` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_an_unreadable_register`.
  - `metadata-unreadable` → `tests/test_package_metadata.py::TestLoadMetadata::test_unreadable_file_names_the_path`.
  - `placeholders-unreadable-register` → `tests/test_placeholders.py::TestHelpers::test_register_entries_rejects_an_unreadable_register`.
  - `placeholders-dangling-symlink` → `tests/test_placeholders.py::TestHelpers::test_markers_rejects_a_dangling_symlink_within_the_theme_root`.
  - `invariants-nul-row` → `tests/test_invariants.py::TestHelpers::test_cross_check_rejects_a_reference_with_a_nul_byte`.
  - `invariants-unreadable-test-file` → `tests/test_checker_mutations.py::TestCheckerMutations::test_invariants_mutations` (which drives the `unreadable-test-file` mutation).
  Add `no_fake(records)` filtering the tag, `no_fake_reproduction(record)` using the existing
  `_lookup`, and extend `reproduction_for` to dispatch `no-fake` and say so in its docstring.
- `tests/test_validation_gaps.py`: update the module docstring to three ledgers; add
  `TestNoFakeLedger` mirroring `TestNoObservabilityLedger`: every `no-fake` record names a
  reproduction, every reproduction reference is a real test via `check_reference`, every entry
  covers a shipped record, the record count is at most `NO_FAKE_BASELINE` (message tells the next
  author to add an entry and raise the baseline by one), and an unmatched mechanism returns `None`.
- `docs/invariants.md`: extend the tooling row that names the two existing ledgers to name the
  `no-fake` ledger and `tests/test_validation_gaps.py::TestNoFakeLedger`.

**Files touched.** `tests/support/png_fixtures.py`, `tests/support/validation_gaps.py`,
`tests/test_png_malformed.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 16 `no-fake` records; each
  resolves to exactly one `NO_FAKE_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every reproduction reference names a real test, so a deleted or misspelled reference fails
  `check_reference`; a new `no-fake` record without an entry, or a count above 16, fails the suite.
- The palette `tRNS`-before-`PLTE` test still refuses on both decode paths through the named
  builder; reversing the builder's chunk order or changing its payload fails the test.
- `tests/invariants.py` accepts the updated tooling row, and `make check` is green.

### Platinum panel edit-mode chrome, part 2/2: ship the panel resize and slider handles (planned 2026-10-23 by the plan role; follows the landed part 1/2 margin highlight) — done 2026-10-23 by the feature role

**Goal.** The desktop theme ships no `widgets/containment-controls.svg`, so while a panel is in
edit mode its offset, minimum and maximum drag handles and its centre indicators come from the
default theme's blue-grey artwork. Ship our own `widgets/containment-controls.svg` for the
twenty-six element ids the installed panel configuration and its ruler resolve, drawn as raised
Platinum thumbs, a black-edged face band and lavender centre lines. No reference screenshot
shows panel edit mode, so the art is our own: the element ids are KDE-required (its consumers
name them), the frame slice and indicator geometry plus the indicator opacity are the installed
default theme's, and the 9x9 slider size is this theme's own. The colours reuse the grounded
Platinum face/bevel palette and the `#CCCCFF` selection anchor.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg`: a `<svg
width="42" height="42" viewBox="0 0 42 42">` whose twenty-six consumers are id-bearing `<g>`
elements at the origin, each holding rects with 0-based coordinates so KSvg reads that group's
bounding box as its natural size. Open with a comment naming the consumers
(`PanelConfiguration.qml` sets the north/south/east/west prefix, `Ruler.qml` is a
`KSvg.FrameSvgItem` for that prefix and asks for the two centre indicators, and
`SliderHandle.qml` builds `prefix + '-' + graphicElementName`), the ids,
and the provenance exception.
  - The twelve ruler frame groups are `north-center`, `north-top`, `north-bottom` and the
same three for `south`, plus `east-center`, `east-left`, `east-right` and the same three for
`west`. A horizontal ruler's top/bottom strips are 10x1 black and its centre 10x12 #DDDDDD; a
vertical ruler's left/right strips are 1x10 black and its centre 12x10 #DDDDDD, so the band is
14px thick. The geometry is the installed default theme's.
  - The twelve slider groups are `north-offsetslider`, `north-minslider`, `north-maxslider`,
`north` repeated for `south`, `east` and `west`. Each is a 9x9 raised Platinum thumb painted in
this document order (later rects override earlier ones, the slider.svg rule):
`<rect width="9" height="9" fill="#DDDDDD"/>`; `<rect y="1" width="9" height="1"
fill="#FFFFFF"/>`; `<rect y="7" width="9" height="1" fill="#999999"/>`; `<rect x="1"
width="1" height="9" fill="#FFFFFF"/>`; `<rect x="7" width="1" height="9"
fill="#999999"/>`; then the four outline rects `<rect width="9" height="1"
fill="#000000"/>`, `<rect y="8" width="9" height="1" fill="#000000"/>`, `<rect width="1"
height="9" fill="#000000"/>` and `<rect x="8" width="1" height="9" fill="#000000"/>`.
  - The grip is the last rect of each slider group: the four offset sliders carry a 3x3 black
centre dot `<rect x="3" y="3" width="3" height="3" fill="#000000"/>`; the north/south
min/max sliders carry a vertical 1x5 black bar `<rect x="4" y="2" width="1" height="5"
fill="#000000"/>`; the east/west min/max sliders carry the horizontal 5x1 bar `<rect x="2"
y="4" width="5" height="1" fill="#000000"/>`.
  - The two centre indicators are `vertical-centerindicator` (a vertical panel stretches it
across the panel width) with one `<rect width="42" height="1" fill="#CCCCFF"
fill-opacity="0.4"/>`, and `horizontal-centerindicator` (a horizontal panel stretches it down
the panel height) with one `<rect width="1" height="42" fill="#CCCCFF"
fill-opacity="0.4"/>`. The 42x1/1x42 natural geometry and the 0.4 opacity are the installed
default theme's; the colour is the grounded selection lavender.
- `tests/support/desktoptheme_paths.py`: add `CONTAINMENT_CONTROLS_SVG` pointing at
`widgets/containment-controls.svg`.
- `tests/test_desktoptheme.py`: add `("containment-controls.svg", CONTAINMENT_CONTROLS_SVG,
42, 42)` to `SVG_CANVASES` and `os.path.join("widgets", "containment-controls.svg")` to
`TestInstall.INSTALLED_FILES`, so the canvas, unique-id, self-containment, registry-completeness
and install-lifecycle checks cover the new file.
- New `tests/test_desktoptheme_containmentcontrols.py` (`SvgCase`, `SVG_PATH =
CONTAINMENT_CONTROLS_SVG`):
  - `test_containment_controls_contract`: all twenty-six ids are present, ids are unique, and
the file has no script, style or external reference.
  - `test_groups_sit_at_the_origin`: `tile_origins` finds every id-bearing group at (0, 0), so a
future transform cannot move a slice off its canvas region while the pixel tests still pass.
  - `test_ruler_frame_slices_are_black_edges_on_a_face_band`: each of the twelve frame groups
holds one rect at its pinned natural size and fill, and `render_slices` paints exactly that
pixel map.
  - `test_sliders_are_raised_platinum_thumbs_with_grips`: render each of the twelve slider
groups with `render_slices` and compare its full pixel map to `raised_thumb_pixels(9, 9)` from
`support.thumb_fixtures` with the pinned grip pixels overwritten to `BLACK` -- the 3x3 dot for
the offset sliders, the vertical 1x5 bar for north/south min/max, the horizontal 5x1 bar for
east/west min/max. This pins every pixel, the 9x9 natural size and the grip orientation, so a
shifted bevel, a resized group or a swapped grip fails.
  - `test_center_indicators_are_lavender_lines`: each indicator group renders exactly 42
`SELECTION` pixels in the pinned 42x1 or 1x42 shape, and each of its rects carries
`fill-opacity="0.4"`.
  - `test_containment_controls_colours`: `assert_fill_palette(self, self.tree,
extra={SELECTION})`, so the parsed fill set is exactly the Platinum face/bevel palette plus the
selection lavender.
- `README.md`: replace the sentence that says the panel resize and slider handles still come from
the fallback theme with one naming `widgets/containment-controls.svg`, its black-edged ruler
frame, its twelve offset/min/max sliders and its two centre indicators.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the panel edit-mode ruler frame
is black-edged Platinum face slices, the sliders are raised Platinum thumbs and the centre
indicators lavender lines, pinned by
`tests/test_desktoptheme_containmentcontrols.py::TestContainmentControls`; the provenance
exception records that no reference screenshot shows panel edit mode; the twenty-six ids are
KDE-required (the consumers name them), the frame slice and 42x1/1x42 indicator geometry plus
0.4 opacity are the installed default theme's, and the 9x9 slider size and artwork are this
theme's own; the colours reuse the grounded Platinum and selection anchors.
- `PLANS.md`: in the scope-drift paragraph, change the widget-SVG count from twenty-five to
twenty-six, name the new containment-controls file, and drop the claim that its handles still
come from the default theme.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/containment-controls.svg` (new),
`tests/test_desktoptheme_containmentcontrols.py` (new),
`tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`, `README.md`,
`docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 42x42 canvas with the twenty-six pinned ids present and unique, every
ruler frame group rendering its pinned 10x1/10x12 or 1x10/12x10 slice, every slider group
rendering as the pinned 9x9 raised thumb plus its orientation's grip, the two indicator groups
rendering as the pinned 42x1 or 1x42 lavender line at 0.4 opacity, and every id-bearing group at
the origin.
- The parsed fill set is exactly `#000000`, `#FFFFFF`, `#999999`, `#DDDDDD` and `#CCCCFF`;
dropping an id, resizing a group, swapping a bevel colour or turning a grip the wrong way fails
a test.
- `TestSvgRootCanvas`'s registry and `TestInstall.INSTALLED_FILES` cover the new file,
`tests/invariants.py` accepts the new `## desktoptheme` row, and README and the scope-drift
paragraph name it with the scope-drift count at twenty-six.
- `make check` is green.

### Platinum cursor set, part 3: ship the drag-and-drop, grab and forbidden pointers (planned 2026-10-23 by the plan role; follows the landed resize/diagonal/crosshair/not-allowed set) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers the arrow, text I-beam, pointing hand, busy
hourglass, move cross, the four resize arrows, the crosshair and the circle-slash, and README
records that drag-and-drop (`dnd-*`), grab, the separate `forbidden`/`no-drop` pointers, help,
progress, zoom and pencil still come from the fallback cursor theme. Add the drag-and-drop and
grab pointers: a new `dnd-copy` (white-outlined black copy plus), the landed four-way cross as
`dnd-move`, the landed arrow as `dnd-none`, the landed circle-slash as
`dnd-no-drop`/`no-drop`/`forbidden`, and the new `grab` (open hand) and `grabbing` (closed fist)
cursors. `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` stay on the fallback theme and
are a later entry. No reference screenshot shows a pointer, so the art stays our own
`#000000`-face/`#FFFFFF`-outline drawing; the canonical names are X/KDE-required, taken from the
installed Breeze cursor set (`/usr/share/icons/breeze_cursors/cursors` ships exactly the four
`dnd-copy`/`dnd-move`/`dnd-no-drop`/`dnd-none` drag names, plus `forbidden`, `no-drop`, `grab` and
`grabbing`). The alias grouping is this theme's choice: Breeze's own byte groups are not copied.

**Approach.**
- `tools/make_cursors.py`: add three 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary and wire them into `CURSORS`; `cursor_bytes`, `NOMINAL_SIZES` and `main`
need no change.
  - `DND_COPY_HOTSPOT = (7, 7)`; `DND_COPY_GRID` -- a symmetric black plus whose vertical bar is
column 7 on rows 2-12 and horizontal arms run along row 7 from columns 2-12, split from the bar by
its white outline at columns 6 and 8, with a white outline cell around every black edge and
transparent corners; `(7, 7)` is black and `(6, 7)` is white.
  - `GRAB_HOTSPOT = (7, 12)`; `GRAB_GRID` -- an open hand: four 1px black fingers at columns 3, 6,
9 and 12 on rows 2-9, separated by white outline columns, over a black palm on rows 10-13 with a
white outline along its sides and bottom; the fingertips are black at row 2 and the palm is black
at `(7, 12)`, its left edge white at `(1, 12)`.
  - `GRABBING_HOTSPOT = (7, 12)`; `GRABBING_GRID` -- the same hand closed into a fist: a black block
on rows 5-13 with a white outline around it and the thumb folded across; row 2 is transparent (no
raised fingers) and the palm is black at `(7, 12)`, its left edge white at `(1, 12)`.
  - Append `("dnd-copy", DND_COPY_GRID, DND_COPY_HOTSPOT, ())`, `("grab", GRAB_GRID,
GRAB_HOTSPOT, ())` and `("grabbing", GRABBING_GRID, GRABBING_HOTSPOT, ())` to `CURSORS`; extend the
existing tuples so `fleur` also carries `dnd-move`, `left_ptr` also carries `dnd-none`, and
`not-allowed` also carries `forbidden`, `no-drop` and `dnd-no-drop` (byte-identical aliases).
  - Update the module docstring: the package ships fourteen canonical cursors, not eleven, and
list the new names and aliases.
- `tests/test_cursors_theme.py`: extend `CANONICAL` with `dnd-copy`, `grab` and `grabbing`, and
`ALIASES` with the three new canonical names (no aliases) plus `dnd-move` under `fleur`, `dnd-none`
under `left_ptr`, and `forbidden`/`no-drop`/`dnd-no-drop` under `not-allowed`. Add the three new
names to `HOTSPOTS` (`(7, 7)` at 16, `(11, 11)` at 24, `(14, 14)` at 32 for `dnd-copy`; `(7, 12)`
at 16, `(11, 18)` at 24, `(14, 24)` at 32 for `grab` and `grabbing`) and to `PINNED_PIXELS`
(face `(7, 7)` / outline `(6, 7)` for `dnd-copy`; face `(7, 12)` / outline `(1, 12)` for `grab` and
`grabbing`). Add `dnd-copy`, `grab` and `grabbing` to `TRANSPARENT_CORNER_CURSORS`. The existing
`TestCursorSet` loops then cover the new files, aliases, hotspots, face/outline pixels and
determinism. Add focused tests:
  - `test_dnd_copy_is_a_centred_plus`: at 16px, black at `(7, 2)`, `(7, 12)`, `(2, 7)`, `(12, 7)`
and `(7, 7)`; white at `(6, 7)` and `(7, 1)`; every corner transparent.
  - `test_grab_and_grabbing_pin_open_and_closed_hands`: at 16px both have black `(7, 12)` and white
`(1, 12)`; `grab` is black at the fingertip `(3, 2)` while `grabbing` is transparent there; the two
grids differ.
  - `test_dnd_aliases_reuse_the_landed_glyphs`: `dnd-move` is byte-identical to `fleur`, `dnd-none`
to `left_ptr`, and `forbidden`, `no-drop` and `dnd-no-drop` to `not-allowed`.
- Regenerate the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the eight new X names (`dnd-copy`, `dnd-move`, `dnd-none`,
`dnd-no-drop`, `forbidden`, `no-drop`, `grab`, `grabbing`) to `SHIPPED_CURSORS`, so the shipped-file
registry and the shared install-lifecycle list cover them.
- `README.md`: in the cursor sentence name the new pointers and aliases, and narrow the fallback
sentence to the `help`, `progress`, `pencil`, `zoom-in` and `zoom-out` pointers.
- `docs/invariants.md`: extend the `## icons` cursor row to name all fourteen canonical files and
every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and
`::TestCursorSet`. Extend the provenance exception: no reference screenshot shows the pointer; the
drag-and-drop, grab and forbidden names are X/KDE-required and taken from the installed Breeze set,
while grouping `dnd-move` with `fleur`, `dnd-none` with `left_ptr` and
`dnd-no-drop`/`no-drop`/`forbidden` with `not-allowed` is this theme's own choice.
- `PLANS.md`: in the scope-drift paragraph, add the drag-and-drop, grab and forbidden pointers to
the shipped cursor clause, and state that `help`, `progress`, `pencil`, `zoom-in` and `zoom-out`
still fall back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/`
(three canonical names and five alias names), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the three new canonical files and the five aliases;
running it twice leaves every committed cursor byte-identical, and each new canonical parses to
three chunks at nominal sizes 16/24/32 with its pinned hotspot, black face pixel, white outline
pixel and transparent corners.
- `dnd-copy` draws the pinned centred plus, `grab` draws the open hand with black fingertips and
`grabbing` the closed fist with transparent finger cells; deleting a grid, dropping a size,
moving a hotspot, redrawing the plus off-centre or making `grabbing` a copy of `grab` fails a test.
- `dnd-move`, `dnd-none`, `forbidden`, `no-drop` and `dnd-no-drop` are byte-identical to their
canonical files; the generator writes exactly the eight new names into a temp directory.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all eight new
names, README and `docs/invariants.md` name them, and `tests/invariants.py` accepts the updated
`## icons` row; the scope-drift clause names only help, progress, pencil and zoom as fallback.
- `make check` is green.

### Platinum panel edit-mode chrome, part 1/2: ship the panel margin highlight (planned 2026-10-23 by the plan role; independent of the waiting cursor series) — done 2026-10-23 by the feature role

**Goal.** The desktop theme ships no `widgets/margins-highlight.svg`, so while a panel is in
edit mode Plasma falls back to the default theme's blue translucent margin band. Ship our own
4x4 highlight tile: the flat `fill` and four corner wedges the panel's `SideMargin` reads, tinted
the reference selection lavender instead of Breeze blue. The panel's resize/slider handles
(`widgets/containment-controls.svg`) stay on the fallback theme in this part; part 2/2 covers
them. No reference screenshot shows panel edit mode, so the tile is our own art: the lavender is
the grounded selection colour `#CCCCFF`, and the 0.3 translucency is the default theme's
margin-highlight opacity.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg`, a 4x4 canvas with the
five ids the installed `org.kde.panel` `main.qml` `SideMargin` resolves: `fill` for the flat band
and `topleft`, `topright`, `bottomleft`, `bottomright` for the corner wedges (the component builds
`side + 'left'`/`'right'`, or `'top'`/`'bottom'` + side, so those four names are the only ones it
asks for).
  - `fill` is `<rect id="fill" x="0" y="0" width="4" height="4" fill="#CCCCFF"
fill-opacity="0.3"/>`.
  - The four corner ids are half-canvas triangles, each `fill="#CCCCFF"` and
`fill-opacity="0.3"`: `topleft` `M 0,0 H 4 L 0,4 Z`, `topright` `M 0,0 H 4 V 4 Z`, `bottomleft`
`M 0,0 V 4 H 4 Z`, `bottomright` `M 4,0 V 4 H 0 Z`.
  - Open the SVG with a comment naming the consumer, the five ids, and the provenance: the
consumer stretches each element over the margin band, `#CCCCFF` is the reference selection colour,
and 0.3 is the default theme's margin-highlight opacity.
- `tests/support/desktoptheme_paths.py`: add `MARGINS_HIGHLIGHT_SVG` pointing at
`widgets/margins-highlight.svg`.
- `tests/test_desktoptheme.py`: add `("margins-highlight.svg", MARGINS_HIGHLIGHT_SVG, 4, 4)` to
`SVG_CANVASES`, so `TestSvgRootCanvas`'s canvas, unique-id and self-contained loops cover it.
- New `tests/test_desktoptheme_marginshighlight.py`: pin the five ids, the flat `fill` rect at
`(0,0,4,4)`, each corner path's exact `d` and the four corner orientations, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and the absence of scripts, styles and external references.
- `README.md`: after the `widgets/action-overlays.svg` sentence, record
`widgets/margins-highlight.svg` as the translucent lavender panel-margin highlight shown in edit
mode, and note that the panel resize/slider handles still come from the fallback theme.
- `docs/invariants.md`: add a `## desktoptheme` row stating that the margin highlight's flat fill
and four corner wedges share the grounded selection lavender at KDE's 0.3 highlight opacity, pinned
by `tests/test_desktoptheme_marginshighlight.py`; the provenance exception records that no
reference screenshot shows panel edit mode, so the five ids and 0.3 opacity are KDE-required while
the colour reuses the reference selection anchor.
- `PLANS.md`: in the scope-drift paragraph, change the desktop-theme count from twenty-four to
twenty-five widget SVGs, name the new margin highlight, and state that
`widgets/containment-controls.svg` still falls back.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/margins-highlight.svg` (new),
`tests/test_desktoptheme_marginshighlight.py` (new), `tests/support/desktoptheme_paths.py`,
`tests/test_desktoptheme.py`, `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- The new SVG parses as a 4x4 square with the five ids present and unique, every fill `#CCCCFF`,
every `fill-opacity` `0.3`, and no script, style or external reference.
- `fill` is the full 4x4 rect and each corner id is its pinned half-canvas triangle; dropping
an id, nudging a path, changing a fill or changing the opacity fails a test.
- `TestSvgRootCanvas`'s registry covers the new file, and the README and `docs/invariants.md`
name it; `tests/invariants.py` accepts the new row and the scope-drift count is twenty-five.
- `make check` is green.

### Platinum cursor set, part 2: ship the resize, diagonal, crosshair and not-allowed pointers (planned 2026-10-23 by the plan role; follows the landed cursor set) — done 2026-10-23 by the feature role

**Goal.** The icon theme's `cursors/` covers the arrow, text I-beam, pointing hand, busy hourglass
and move cross, and README records that resize, diagonal, drag and not-allowed pointers still come
from the fallback cursor theme. Add the six pointers that make window resizing, precise pointing
and a forbidden action wear the same Platinum art: `size_hor` (horizontal double arrow),
`size_ver` (vertical double arrow), `size_fdiag` (NW-SE double arrow), `size_bdiag` (NE-SW double
arrow), `crosshair` (precision cross) and `not-allowed` (circle-slash). No reference screenshot
shows a pointer, so the art stays our own black-face/white-outline drawing; the canonical names and
the alias groups are KDE/X-required and are copied from the installed Breeze theme's own
byte-identical groups (verified with `md5sum` in `/usr/share/icons/breeze_cursors/cursors`):
`size_hor` with `e-resize`/`ew-resize`/`w-resize`/`h_double_arrow`/`sb_h_double_arrow`,
`size_ver` with
`n-resize`/`ns-resize`/`s-resize`/`sb_v_double_arrow`/`v_double_arrow`/`00008160000006810000408080010102`,
`size_fdiag` with `nw-resize`/`se-resize`/`nwse-resize`, `size_bdiag` with
`ne-resize`/`sw-resize`/`nesw-resize`, `crosshair` with `cross`/`tcross`, and `not-allowed` with
`circle`/`crossed_circle`/`03b6e0fcb3499374a867c041f52298f0`. Drag-and-drop (`dnd-*`), grab, help,
progress, zoom and the separate `forbidden`/`no-drop` pointers stay on the fallback theme.

**Approach.**
- `tools/make_cursors.py`: add six 16x16 grids in the existing `#` face / `.` white / space
transparent vocabulary, each with hotspot `(7, 7)`, and append their tuples to `CURSORS` (the
`cursor_bytes`, `NOMINAL_SIZES` and `main` paths need no change):
  - `SIZE_HOR_GRID` -- solid black left and right arrowheads joined by a black stem on rows 7-8,
    with a 1px white outline on the outside of every face cell.
  - `SIZE_VER_GRID` -- `SIZE_HOR_GRID` rotated a quarter turn; `SIZE_BDIAG_GRID` --
    `SIZE_FDIAG_GRID` mirrored left to right. Write both grids literally so the art is reviewable,
    and let the tests pin the relationship to their sibling (a wrong orientation fails).
  - `SIZE_FDIAG_GRID` -- the same double-arrow art along the NW-SE axis, arrowheads at the top-left
    and bottom-right, hotspot on the shaft.
  - `CROSSHAIR_GRID` -- a 1px black horizontal arm on row 7 and vertical arm on column 7 crossing at
    the hotspot, 1px white outline alongside each arm, transparent corners.
  - `NOT_ALLOWED_GRID` -- a black ring (1-2px, inset one pixel from the canvas edge) with a black
    NW-SE slash through the centre, a 1px white outline outside the ring and slash, the ring's
    interior transparent except the slash, transparent corners; (7, 7) is black on the slash.
  - Update the module docstring: the package ships eleven cursors, not five, and list the new names.
- `tests/test_cursors_theme.py`: extend `CANONICAL`, `ALIASES`, `HOTSPOTS` (`(7, 7)`, `(11, 11)`,
  `(14, 14)` at 16/24/32), `PINNED_PIXELS` (one black face and one white outline cell per new glyph)
  and `TRANSPARENT_CORNER_CURSORS`; the existing `TestCursorSet` loops then cover the new files,
  aliases and determinism. Add three focused tests:
  - `test_size_ver_is_the_horizontal_glyph_rotated_a_quarter_turn` and
    `test_size_bdiag_is_the_forward_diagonal_mirrored`: compare the 16px `render_rgba`
    results, rotating with destination `(x, y)` read from source `(y, GRID_SIZE - 1 - x)` and
    mirroring with destination `(x, y)` read from source `(GRID_SIZE - 1 - x, y)`.
  - `test_crosshair_black_cells_lie_on_the_centre_row_or_column`.
  - `test_not_allowed_is_a_ring_with_a_slash`: every corner transparent, `(7, 7)` black, and the
    four cardinal exterior cells (`(7, 0)`, `(7, 15)`, `(0, 7)`, `(15, 7)`) white.
- Regenerate and commit the artifacts with `python3 tools/make_cursors.py` (deterministic output).
- `tests/test_icon_theme.py`: add the twenty-eight new X names to `SHIPPED_CURSORS`, so the
  shipped-file registry and the shared install-lifecycle `INSTALLED_FILES` list include them.
- `README.md`: in the cursor sentence name the six new pointers and their aliases, and narrow the
  fallback sentence to drag-and-drop (`dnd-*`), grab, help, progress and zoom pointers.
- `docs/invariants.md`: extend the `## icons` cursor row to name all eleven canonical files and
every alias, still citing `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`;
the provenance exception keeps "no reference screenshot shows the mouse pointer" and adds that the
six new alias groups mirror Breeze's own byte-identical files.
- `PLANS.md`: in the scope-drift paragraph, extend the cursor clause to name the resize, diagonal,
crosshair and not-allowed pointers alongside the five landed ones, and state what still falls back.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`,
`tests/test_icon_theme.py`, the new binaries under `theme/icons/org.macos8.desktop/cursors/` (six
canonical names and twenty-two aliases), `README.md`, `docs/invariants.md`, `PLANS.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the six canonical files and twenty-two aliases; running it
  twice leaves every committed cursor byte-identical, and each new canonical parses to three chunks
  at nominal sizes 16/24/32 with its pinned hotspot, black face pixel, white outline pixel and
  transparent corners.
- Every new alias is byte-identical to its canonical file, and the generator writes exactly the
  twenty-eight new names into a temp directory.
- The rotation, mirror and crosshair-geometry tests pass; dropping a glyph or alias, rotating a
  grid the wrong way or redrawing the crosshair off the centre row/column fails a test.
- `tests/test_icon_theme.py`'s shipped-file registry and install lifecycle include all twenty-eight
  new files, README and `docs/invariants.md` name them, and `tests/invariants.py` accepts the updated
  `## icons` row.
- `make check` is green.

### Platinum Kvantum secondary controls: map toolbars, tree views and status bars onto the Platinum art (planned 2026-10-23 by the plan role; follows the landed four-part Kvantum series) — done 2026-10-23 by the feature role

**Goal.** The Kvantum style defines the core, track/value and surface controls, but the six
sections Kvantum maps common Qt widgets to are left to its compiled-in default: `[ToolbarButton]`
(a `QToolButton` in a `QToolBar`), `[ToolbarComboBox]`, `[ToolbarLineEdit]`, `[DropDownButton]`
(a tool button with a menu popup), `[TreeExpander]` (a `QTreeView`'s branch indicator) and
`[StatusBar]`. `org.macos8.desktop.kvconfig`'s own header records that Kvantum "merges this file
over its compiled-in default.kvconfig and draws an element the theme SVG lacks from its
compiled-in default.svg", so these six sections are not defined by the Platinum style. State
them explicitly so a KDE application's toolbar buttons, toolbar combo boxes and line edits,
split-button dropdowns, tree-view expanders and status bar draw the same grounded Platinum
controls as the rest of the style instead of inheriting Kvantum's default. The button, line-edit,
comboarrow and arrow-down elements already ship; the tree expander needs Kvantum's
`arrow-minus-*`/`arrow-plus-*` branch names added to the SVG, reusing the grounded down and right
arrow paths.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`: after `[Toolbar]`, add these
  sections with a short comment naming the provenance exception (no reference screenshot shows a
  KDE/Qt toolbar, tree view or status bar, so the section and key names are Kvantum-required):
  - `[ToolbarButton]` -- `inherits=PanelButtonCommand`, the 2px raised Platinum push button with
    its black label in every state.
  - `[ToolbarComboBox]` -- `inherits=ComboBox`, the raised face whose `comboarrow` indicator is
    the reference popup's double arrow at size 12.
  - `[ToolbarLineEdit]` -- `inherits=LineEdit`, the white sunken field.
  - `[DropDownButton]` -- `inherits=PanelButtonCommand`, the raised face with Kvantum's
    `arrow-down` indicator at size 9 (its unqualified `arrow` would resolve to the missing
    `arrow-normal` when Kvantum appends only the state).
  - `[TreeExpander]` -- `inherits=PanelButtonCommand`, `indicator.element=arrow`, `frame=false`,
    `interior=false`, so only the branch triangle is drawn (Kvantum names it
    `arrow-minus-<state>`/`arrow-plus-<state>`: black in the normal states, #999999 disabled).
  - `[StatusBar]` -- `inherits=GenericFrame`, `frame=false`, `interior=false`, a flat bar in the
    `[GeneralColors]` window face with no bevel.
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: add the eight branch triangles
  (`arrow-minus-*` pointing down, `arrow-plus-*` pointing right) for the normal, focused, pressed
  and disabled states, reusing the grounded arrow paths and fills; enlarge the canvas height to
  hold them.
- `tests/support/kvantum_config_spec.py`: add the four framed sections to `CORE_FRAME_MARGINS`
  (all 2) and to `CORE_CONTROL_CONFIG` with the element mappings they resolve to -- for
  `ToolbarButton` the frame and interior `button` and the indicator `arrow`, for `DropDownButton`
  the frame and interior `button` and the indicator `arrow-down`, for `ToolbarComboBox` the frame
  and interior `button` and the indicator `comboarrow`, for `ToolbarLineEdit` the frame and
  interior `lineedit`. Add `TreeExpander` and `StatusBar` to `FRAMELESS_SECTIONS` with
  `frame=false`, `interior=false` and their pinned `inherits` targets (plus the expander's
  `indicator.element=arrow`). The existing `test_every_section_is_pinned`,
  `test_every_core_section_mapping_is_pinned`, `test_every_core_section_resolves_to_the_expected_frame_margin`
  and `test_every_frameless_section_resolves_its_pins` then fail if a section, margin, inherited
  element target or frameless pin is dropped or changed.
- `tests/test_kvantum_svg.py`: pin that every branch triangle ships in every state and draws its
  grounded down/right path with the per-state fill.
- `README.md`: in the Kvantum paragraph, change "Its Platinum palette and core-control art live
  in ..." to "Its Platinum palette and control art live in ..." and add that the toolbar buttons,
  toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar
  map to the same Platinum button, line-edit and arrow art.
- `docs/invariants.md`: add one `## kvantum` row -- the four framed secondary sections resolve to
  the grounded Platinum elements and margins above, the tree expander to the pinned branch
  triangles, and the status bar to no frame or interior, with both frameless sections' `inherits`
  targets pinned -- citing `tests/test_kvantum_config_elements.py::TestCoreControlElements`,
  `tests/test_kvantum_config.py::TestFrameMargins`, `tests/test_kvantum_config.py::TestSectionCoverage`
  and `tests/test_kvantum_svg.py::TestSvg`; its provenance exception is the missing reference
  screenshot (the section and key names are Kvantum-required, the art is grounded).

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`, `tests/support/kvantum_config_spec.py`,
`tests/test_kvantum_config.py`, `tests/test_kvantum_svg.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each new section resolves (following `inherits`) to its pinned element mapping and, for the four
  framed sections, the 2px frame margin; `DropDownButton` resolves its indicator to `arrow-down`;
  `TreeExpander` and `StatusBar` resolve `frame` and `interior` to `false` with their `inherits`
  targets pinned.
- `test_every_section_is_pinned` names all six new sections, and deleting one, dropping its frame
  margin, repointing an inherited element target, or removing a branch arrow or one of its states
  fails a test.
- The SVG change is limited to the eight branch triangles and the canvas height they need, and no
  new colour is introduced.
- `make check` is green and `tests/invariants.py` accepts the new `## kvantum` row.

### Platinum cursor set: ship the text, hand, busy and move pointers (planned 2026-10-23 by the plan role; follows the landed arrow artifact) — done 2026-10-23 by the feature role

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, so after
`make apply-cursor` selects the theme every pointer except the arrow still comes from the user's
fallback theme: typing in a field, hovering a link, waiting for a task and dragging a window all
draw the fallback cursor. Add the four other pointer roles a desktop uses constantly -- the text
I-beam (`xterm`), the pointing hand (`hand2`), the busy hourglass (`watch`) and the move cross
(`fleur`) -- with the X-name aliases applications use, generated by the same tool. All art is our
own Platinum-style drawing on the pinned #000000 face and #FFFFFF outline, not traced from
Apple's artwork; no reference screenshot shows a pointer, so the existing `## icons` provenance
exception covers the new names. This entry does not change the arrow's bytes; the landed
"Platinum cursor selection" entry's `make apply-cursor` selects the set. Resize, diagonal, drag
and not-allowed pointers stay on the fallback theme and are recorded as such; a later entry can
complete them.

**Approach.**
- `tools/make_cursors.py`: replace the one-glyph constants' use with a fixed `CURSORS` table whose
  entries are `(canonical_name, rows, hotspot, aliases)`, in this order: `left_ptr` (the existing
  `ARROW_GRID`/`HOTSPOT`, aliases `arrow`, `default`, `top_left_arrow`), `xterm` (I-beam, aliases
  `text`, `ibeam`), `hand2` (pointing hand, aliases `hand1`, `pointer`, `pointing_hand`), `watch`
  (hourglass, alias `wait`) and `fleur` (move cross, aliases `move`, `all-scroll`, `size_all`).
  Keep `ARROW_GRID`, `HOTSPOT`, `NOMINAL_SIZES` and `cursor_bytes(rows=ARROW_GRID, sizes=
  NOMINAL_SIZES, hotspot=HOTSPOT)` so the landed artifact and its tests stay valid. Add a
  `*_GRID` and `*_HOTSPOT` constant per glyph and generalize `_checked_rows` to take the glyph
  name so a bad cell reports `"xterm grid cell (x, y) ..."` (the arrow keeps its `"arrow grid"`
  messages). `main` walks `CURSORS` in order and writes each canonical file then its aliases with
  the same containment guard, atomic write and stop-on-first-failure behavior.
- The new 16x16 grids use the existing `PIXELS` map (`#` black face, `.` white outline, space
  transparent) and keep the arrow's 1px black face fully inside a 1px white outline, transparent
  elsewhere: `xterm` is a vertical I-beam with top and bottom serifs, hotspot at its centre;
  `hand2` is a pointing hand with the index finger up and the thumb to the right, hotspot at the
  fingertip; `watch` is a top and bottom triangle joined at a narrow waist, hotspot at the
  centre; `fleur` is a four-way arrow cross, hotspot at the centre. Each grid must differ from
  `ARROW_GRID` so a copy-paste fails the set test.
- `tests/test_cursors_theme.py`: keep `TestCursorArtifact` for the arrow and add `TestCursorSet`
  covering every canonical name and alias: each file parses to 16/24/32 chunks, its hotspot is
  the glyph's pinned scaled hotspot, the four corners are transparent, the face is black and the
  outline white at pinned pixels, and every alias is byte-identical to its canonical file. Extend
  the determinism and `main` error cases to all files, including a corrupted grid, dropped size
  and moved hotspot per new glyph; keep the failed-write case failing on `arrow` so the write
  order is pinned. `HOTSPOTS` becomes a per-glyph mapping.
- `README.md`: the cursor sentence in the installed-theme paragraph names the arrow plus the
  `xterm`, `hand2`, `watch` and `fleur` pointers and their aliases, and says resize/drag pointers
  still come from the fallback theme. Keep the landed `make apply-cursor`/`make remove-cursor`
  selection sentences as they are.
- `docs/invariants.md`: extend the existing `## icons` cursor row to name every canonical file and
  alias and cite both `tests/test_cursors_theme.py::TestCursorArtifact` and `::TestCursorSet`; the
  provenance exception keeps "no reference screenshot shows the pointer; our own Platinum-style
  art on the pinned face and outline; the nominal sizes, Xcursor layout and X names are KDE/X
  required".
- `PLANS.md`: the scope-drift paragraph's artifact list names the cursor set instead of only the
  arrow; its selection sentence already names the landed `make apply-cursor`/`make remove-cursor`
  commands.

**Files touched.** `tools/make_cursors.py`, `tests/test_cursors_theme.py`, `tests/test_icon_theme.py`
(its shipped-cursor registry and installed-file list must name the new files), the new files under
`theme/icons/org.macos8.desktop/cursors/` (canonical names and aliases listed above), `README.md`,
`docs/invariants.md` and `PLANS.md` (this entry and the scope-drift artifact list). Do not edit
`tools/xcursor.py`, `tools/apply_cursor.py`, `PLANS-DONE.md`, or the arrow's committed bytes.

**Acceptance criteria.**
- `git diff --name-status` does not list `cursors/left_ptr`, `cursors/arrow`, `cursors/default` or
  `cursors/top_left_arrow`; running `python3 tools/make_cursors.py` twice leaves every committed
  cursor file byte-identical.
- Every alias is byte-identical to its canonical file, each canonical file holds three chunks at
  nominal sizes 16, 24 and 32, and each glyph's scaled hotspot is pinned at all three sizes
  (the arrow's are (1,1), (2,2) and (2,2)).
- Tests prove each new grid differs from the arrow, a corrupted grid, dropped size or moved
  hotspot changes that glyph's bytes, and an unknown cell names the glyph (`xterm grid cell ...`).
  A missing alias, a copied arrow grid, or swapping two glyphs' hotspots fails a test.
- The generator still refuses a `cursors/` symlink that escapes the repository, reports a failed
  write by path and stops, and writes nothing outside the icon theme package.
- `make check CHECK_TESTS=test_cursors_theme` passes, then `make check` is green (fixing the
  separately recorded stale `_write_atomic` test reference first if it is still open);
  `tests/invariants.py` accepts the updated `## icons` row.

### Platinum cursor selection: link the shipped cursor into the Xcursor user path and apply it (planned 2026-10-23 by the plan role; follows the landed cursor artifact) — done 2026-10-23 by the feature role

**Goal.** The icon theme package ships `cursors/{left_ptr,arrow,default,top_left_arrow}`, but nothing
selects them. Xcursor searches `~/.icons`, `/usr/share/icons` and `/usr/share/pixmaps` (its
`XcursorLibraryPath()` default), not `$XDG_DATA_HOME/icons`: `plasma-apply-cursortheme --list-themes`
and `XcursorLibraryPath()` both ignore a theme copied under `$XDG_DATA_HOME/icons`, and list it when
the same theme is under `~/.icons`. This part adds an opt-in `make apply-cursor` that exposes the
installed icon theme at `$HOME/.icons/org.macos8.desktop` as a symlink and selects it with
`plasma-apply-cursortheme org.macos8.desktop`; `make remove-cursor` removes only that link. `make
install` and `make apply` stay unchanged and select no cursor.

**Approach.**
- `tools/apply_cursor.py` (new CLI, `TOOL = "apply_cursor"`, `CURSOR_THEME =
  "org.macos8.desktop"`, `SELECT_TOOL = "plasma-apply-cursortheme"`, `COMMAND_TIMEOUT = 60.0`).
  It uses `tools.argument_parsing.EscapingArgumentParser` (`--remove`), reports through
  `tools.diagnostics.report_error`/`report_failure`/`report_missing_tool`, runs the selector with
  `tools.process_group.run_logged` into a temporary log, escapes path text with
  `tools.terminal.escape_controls`, and imports `tools.repo_root.ROOT`.
- `resolve_homes(env)` returns `(home, data_home, config_home)`: `$HOME` must be absolute; data home
  is an absolute `$XDG_DATA_HOME` else `$HOME/.local/share`; config home is an absolute
  `$XDG_CONFIG_HOME` else `$HOME/.config` (only for the removal note). A missing or relative `HOME`
  exits 2 naming it.
- `installed_theme(data_home)` is `$XDG_DATA_HOME/icons/org.macos8.desktop`; it must contain a
  regular `index.theme` and a regular `cursors/left_ptr`, else exit 2 naming the path. That file is
  the icon theme's own `index.theme`, so the symlinked directory is also a valid cursor theme (the
  KDE cursor model lists it by the directory name `org.macos8.desktop`).
- Install: the target path is `$HOME/.icons/org.macos8.desktop`. A missing `~/.icons` is created; an
  existing symlink to the installed theme is success (a repeat install changes nothing); any other
  existing path (a foreign symlink, a real directory or a file) is refused with exit 2 naming it and
  is not touched; a `~/.icons` that exists but is not a directory is refused the same way. A new link
  is created with `os.symlink(str(installed_theme), str(target))`.
  Then `plasma-apply-cursortheme org.macos8.desktop` runs with the inherited environment; a missing
  tool exits 2 through `report_missing_tool`, a timeout or non-zero exit returns `report_failure`
  (status 1) with the log tail.
- Remove (`--remove`): unlink the target only when it is a symlink whose link text is the installed
  theme path (a dangling link to a since-uninstalled theme counts as ours); a real directory, a file
  or a symlink elsewhere is left alone with a note and exit 0, like `remove-gtk` leaving a foreign
  file. Do not edit `kcminputrc`; if its `[Mouse] cursorTheme` still names `org.macos8.desktop`,
  print a note naming `plasma-apply-cursortheme breeze_cursors` as the reset. Leave `~/.icons`
  itself in place.
- `Makefile`: add `apply-cursor` and `remove-cursor` to `.PHONY` and `make help`. `apply-cursor`
  refuses a non-empty `DESTDIR` (like `apply`/`apply-gtk`), then runs
  `$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme` followed by
  `$(PYTHON) tools/apply_cursor.py`, behind `require_python`/`require_python_version`.
  `remove-cursor` runs `$(PYTHON) tools/apply_cursor.py --remove` behind the same Python guards.
- `README.md`: replace the cursor paragraph's "Nothing selects it yet." with the opt-in commands,
  the `$HOME/.icons/org.macos8.desktop` symlink, the selection name, the restart note (the selector
  says a restart is needed for the new pointer to display correctly), and the removal note. Add no
  new `?=` variable.
- `docs/invariants.md`: add one row under `## icons`: the opt-in link/selection exposes the shipped
  arrow at the Xcursor path and selects it, refuses a foreign path, and removal reverses only our
  link, leaving a foreign path and `kcminputrc` untouched; pinned to
  `tests/test_apply_cursor.py::TestInstall`, `::TestRemove` and `::TestSelection`. The provenance
  exception records that no reference screenshot shows a pointer, and that the `~/.icons` path, the
  theme name and the selector are Xcursor/KDE-required values.
- `PLANS.md`'s scope-drift paragraph changes its "nothing selects it yet" phrase to name `make
  apply-cursor`/`make remove-cursor` once this lands; the historical "not planned yet" wording in
  `PLANS-DONE.md` is left alone.

**Files touched.** `tools/apply_cursor.py` (new), `tests/test_apply_cursor.py` (new), `Makefile`,
`README.md`, `docs/invariants.md`, `tests/test_cursors_theme.py` and `PLANS.md` (this entry and
the scope-drift sentences). Do not edit `PLANS-DONE.md`, the cursor generator, any `theme/` file,
or the installed-theme layout.

**Pre-existing test repair.** `tests/test_cursors_theme.py` patched `make_cursors._write_atomic`,
which the landed dedupe change removed in favour of `write_bytes_atomically`; the stale reference
made `make check` fail. This change retargets that one mock to the function the generator now
calls, changing no generator code.

**Acceptance criteria.**
- `tests/test_apply_cursor.py` pins: an absolute `HOME` is required (unset and relative refused by
  name); the data-home fallback; a missing installed theme, `index.theme` or `cursors/left_ptr` is
  refused by name; install creates `$HOME/.icons/org.macos8.desktop` as a symlink to the installed
  icon theme, a repeat install succeeds, and a foreign symlink, real directory or file is refused
  without being changed; the selector is invoked as `plasma-apply-cursortheme org.macos8.desktop`,
  a missing selector exits 2 naming it, and a non-zero selector exits 1 with its log tail; removal
  unlinks only our symlink (including a dangling one), leaves a foreign path and `.icons` in place,
  succeeds when repeated, and prints the `kcminputrc` note only when the selection still names
  `org.macos8.desktop`. Changing the link target, deleting the installed-theme check or dropping
  the foreign-path guard makes the matching test fail.
- The Makefile tests pin `apply-cursor`'s dry run (`INSTALL_PACKAGES=icon-theme` before
  `tools/apply_cursor.py`), its `DESTDIR` refusal, and the Python-version refusal; `make help` lists
  both targets and README names `make apply-cursor` and `make remove-cursor`.
- `make check CHECK_TESTS=test_apply_cursor` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## icons` row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

### Firefox Platinum chrome, part 2/2: Install the stylesheet and preference into a Firefox profile (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the stylesheet; "requires part 1/2 landed") — done 2026-10-23 by the feature role

**Goal.** Part 1/2 landed `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, but no
target puts it where Firefox reads it. This part makes the sheet usable for one opt-in profile:
`make install-firefox` copies the sheet into the profile's `chrome/userChrome.css` and adds the
marker-delimited `toolkit.legacyUserProfileCustomizations.stylesheets=true` preference to its
`user.js`, and `make remove-firefox` removes exactly those two changes. It is opt-in like the GTK
targets: `make install` and `make apply` stay unchanged and install no Firefox files.

**Approach.**
- `tools/install_firefox.py` (new CLI, `TOOL = "install_firefox"`). It takes `--profile PATH` and
  `--remove`, parses with `tools.argument_parsing.EscapingArgumentParser`, reports through
  `tools.diagnostics.report_error`/`report_failure`, and escapes path text with
  `tools.terminal.escape_controls`. Constants name the source
  (`theme/firefox/org.macos8.desktop/chrome/userChrome.css`), the CSS first-line marker
  (`/* org.macos8.desktop Firefox chrome, standalone userChrome.css`), the `user.js` marker
  (`// org.macos8.desktop Firefox Platinum userChrome`) and the exact pref line
  `user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);`.
- `resolve_profile(explicit, env)`: an explicit `--profile` (or `FIREFOX_PROFILE` when the flag is
  absent, which also lets the script run directly) must be an absolute existing directory, else
  exit 2. Otherwise `HOME` must be absolute and the profile root is `$HOME/.mozilla/firefox`.
  Build candidates in this order: the first non-empty `Default=` in any section of
  `installs.ini` (Firefox names the section by install hash, older releases by `Install` plus a
  suffix); the first `[Profile…]` section of `profiles.ini` whose `Default=1`; the first
  `[Profile…]` section with a `Path`. Read the INI files with `configparser` and
  `interpolation=None`, resolve a `Path` relative to the root unless `IsRelative=0`, and take the
  first candidate whose directory exists. When none exists, exit 2 with a diagnostic naming the
  root and the candidates tried.
- Install (`_apply(profile)`): read the shipped sheet through
  `tools.containment.read_bytes(SHEET, ROOT)`, then read an existing
  `<profile>/chrome/userChrome.css` before writing anything. An existing file whose first line is
  not the CSS marker is foreign: report with `report_failure` (status 1) naming its path and write
  nothing. Otherwise create `<profile>/chrome`, publish the sheet with
  `tools.atomic_write.write_atomically` (byte-for-byte), and publish `<profile>/user.js` with the
  same writer.
- `set_user_js(text)` and `remove_user_js(text)` are pure text transforms. They preserve every
  foreign line and that line's own CRLF/CR/LF ending, and a missing final newline. Install removes
  any earlier marker line plus the exact pref line immediately after it, then appends the marker
  and pref at the end, terminating an unterminated last line first and using the file's dominant
  ending (a new file uses `\n`), so a repeat install leaves exactly one block and our line follows
  any foreign setting of the same pref. Removal deletes only that marker-plus-pref pair and leaves
  a foreign `user_pref` for the same name untouched; it leaves an emptied `user.js` and the
  `chrome/` directory in place rather than deleting a file it cannot prove it created.
- Remove (`_remove(profile)`): delete `<profile>/chrome/userChrome.css` only when its first line
  is the CSS marker, then rewrite `user.js` with `remove_user_js`. A foreign file, a foreign pref
  line, and a repeated remove are all no-ops; an unreadable file or failed write exits 2 naming
  the path.
- `Makefile`: add `install-firefox` and `remove-firefox` to `.PHONY` and `make help`, each behind
  `require_python`/`require_python_version`, running
  `$(PYTHON) tools/install_firefox.py $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")`
  (with `--remove` for removal). Add a `FIREFOX_PROFILE=path` help line naming the default
  (the active profile under `$HOME/.mozilla/firefox`); do not add a `?=` variable. No DESTDIR
  guard or data-home lock is needed because neither target writes the installed theme tree.
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css`: replace the header sentence saying no
  Makefile target installs it with the two target names and the profile rule; keep the provenance
  text, the preference name and every rule and hex value unchanged.
- `README.md`: replace the Firefox paragraph with the opt-in install/remove commands, profile
  resolution and `FIREFOX_PROFILE`, the restart note, and the existing
  `browser.tabs.inTitlebar=0` explanation; keep the artifact count and `tumwater:status` text.
  `PLANS.md`'s scope-drift paragraph already named part 2/2 as queued under `## Planned`;
  both mentions now say the profile install has landed.
- `docs/invariants.md`: add one row under `## firefox`: the opt-in install copies the sheet
  byte-for-byte, adds only the marker-delimited pref while preserving foreign lines and endings,
  refuses a foreign `userChrome.css`, and removal reverses only those two changes — pinned to
  `tests/test_firefox_install.py::TestInstall` and `::TestRemove`.

**Files touched.** `tools/install_firefox.py` (new), `tests/test_firefox_install.py` (new),
`Makefile`, `README.md`, `docs/invariants.md`, `theme/firefox/org.macos8.desktop/chrome/userChrome.css`
(header only) and `PLANS.md` (this entry and the scope-drift sentences). Do not edit
`PLANS-DONE.md`, any `theme/gtk/` path or any installed-theme directory layout.

**Acceptance criteria.**
- `tests/test_firefox_install.py` pins: explicit and `FIREFOX_PROFILE` profile resolution, an
  `installs.ini` `[Install…]` default and a hash-named section default, a `profiles.ini`
  `Default=1` and first-profile fallback, relative and
  absolute `Path`, and a named refusal when `HOME` is unusable or no candidate exists; install
  writes a byte-identical sheet and exactly one marker-plus-pref block; a foreign
  `userChrome.css` is refused with nothing written; a repeat install does not duplicate the block;
  foreign `user.js` lines, a foreign pref with the same name, CRLF endings and a missing final
  newline survive install and removal; removal deletes only our sheet and marker block and a
  repeated removal succeeds. Deleting the marker, changing the pref value, or dropping the foreign
  line assertion makes the matching test fail.
- `make check CHECK_TESTS=test_firefox_install` passes, then `make check` is green;
  `tests/invariants.py` accepts the new `## firefox` row. `tests/test_make_help.py` finds both new
  targets in `.PHONY`, `make help` and README, and the `FIREFOX_PROFILE` help line resolves to a
  variable the Makefile expands.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`.

### Retire the `unclear-invariant` validation gap with an invariant-register ledger (planned 2026-10-23 by the steward role; promotes the recurring `gap: unclear-invariant` tag, 22 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Twenty-two Fixed entries in BUGS-FIXED.md carry `gap: unclear-invariant` — each bug
could be confirmed only after reconstructing what the code was supposed to guarantee first.
`docs/invariants.md` already has rows for the KDE INI rules, the PNG chunk framing, PLTE, tRNS
and IDAT trailer, the `INSTALL_PACKAGES` guard, the icon theme, the palette anchors and the
fidelity gate, but it had no row for `tools/url_check.py`'s RFC 3986 rules, the render
session's config-search-path isolation or the lineedit corner tiles, and nothing tied an
archived record to its register row. Retire the tag with a ledger that maps each record to the
register row and the test that pins it, and a count cap so a new `unclear-invariant` tag fails
the suite until its invariant is recorded.

**Cited entries.** BUGS-FIXED.md lines recording `gap: unclear-invariant` (22 entries): the six
PNG rules (PLTE color-type legality, tRNS color-type validation, the empty IEND payload, chunks
after IEND, non-consecutive IDAT with late PLTE/tRNS, and the IDAT trailer), the two KDE
config-reader rules (an indented `[General]` header and last-duplicate-key precedence), the
`INSTALL_PACKAGES` guard, the render session's `XDG_CONFIG_DIRS` isolation, the lineedit corner
geometry, the eight `tools/url_check.py` RFC 3986 cases, and the three older one-line records
(icon-theme placeholder naming, the selection palette anchor and the objective fidelity check).
Corrected at implementation: the archive held 22 records (six PNG, two KDE INI) when this
landed, not the 17 the plan was written with; the tRNS and PLTE records landed after the plan
was written.

**Approach.**
- `tests/support/validation_gaps.py`: add `UNCLEAR_INVARIANT_BASELINE = 22` and one
  `UNCLEAR_INVARIANT_REPRODUCTIONS` entry per mechanism, matching both the prose and the older
  one-line record forms. Give each entry the register row's guarantee text in addition to its
  test reference, and add an `unclear_invariant(records)` selector plus a tag-aware lookup that
  returns `None` for an unmatched record, mirroring the `no-observability` ledger without
  changing its entries.
- `tests/test_validation_gaps.py`: add `TestUnclearInvariantLedger` asserting that every
  archived `unclear-invariant` record maps to an entry; that each entry's test reference passes
  `tests/invariants.check_reference`; that each entry's guarantee text occurs in a row
  `tests/invariants.parse_rows` returns from `docs/invariants.md`; that each entry covers a
  shipped record; and that the record count does not exceed 22.
- `docs/invariants.md`: add the missing register rows — `tools/url_check.py`'s RFC 3986
  well-formedness pinned to `tests/test_url_check.py` and the render session's
  `XDG_CONFIG_DIRS` isolation pinned to
  `tests/test_render_surface.py::TestFailurePaths::test_session_ignores_a_config_search_path_from_the_environment`
  under `## tooling`, and the lineedit corner tiles pinned to
  `tests/test_desktoptheme_lineedit.py::TestLineEditReference::test_corners_match_the_reference`
  under `## desktoptheme` — and extend the existing validation-gap ledger row to name both tags.
- `PLANS.md`: this entry moves under `## Done` when the work is done.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`,
`docs/invariants.md` and `PLANS.md` (this entry). Do not edit `PLANS-DONE.md` or any `theme/`
path; the invariants are already recorded, so no shipped artwork or config changes.

**Acceptance criteria.**
- `tests/test_validation_gaps.py::TestUnclearInvariantLedger` passes, and deleting a ledger
  entry, pointing one at an absent register row or a non-existent test, or adding an
  `unclear-invariant` record without an entry makes the matching assertion fail.
- `make check` is green; `tests/invariants.py` accepts the new `## tooling` and `## desktoptheme`
  rows and the extended ledger row.
- `git diff --name-status` names only the files listed under "Files touched" and does not name
  `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`.

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 2/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** The theme ships eight artifacts but no cursor, so a themed Plasma session still shows the
Breeze arrow. Mac OS 8.6 draws a black arrow with a white outline; this part builds that cursor as
a KDE/Xcursor theme artifact — `theme/icons/org.macos8.desktop/cursors/{left_ptr,arrow,default,top_left_arrow}`
(the last three byte-identical X-name copies of `left_ptr`, images at nominal sizes 16, 24 and 32
in one Xcursor file) — with a deterministic generator, and ships it inside the
`org.macos8.desktop` icon theme package, whose `make install` family already installs that whole
tree (so install and uninstall need no Makefile change) and whose directory is one of the paths the
XDG icon-spec lookup searches for `cursors/`. It touches no install or selection path: `make
uninstall` already removes the tree with its family, and the selection (`cursorTheme` in the global
terminal's `contents/defaults`) is not planned yet and is not part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows the mouse pointer, so no
reference pixel is sampled and the arrow is our own Platinum-style art drawn from a pixel grid in
the generator, not traced from Apple's artwork (the icon theme's standing rule). Its two colours
are `#000000` face and `#FFFFFF` outline, both already pinned in the colour scheme; the nominal
sizes 16/24/32, the Xcursor binary format, the file name `left_ptr` and the X-name aliases are
X/KDE-required values the reference set does not show. Record that provenance exception in the
`## icons` row of `docs/invariants.md` (the artifact ships inside the icon theme package). Xcursor
files have no image extension, so Git LFS (`.gitattributes`) is
untouched. The files ride the icon theme artifact, so README's artifact count stays at eight
(status wording untouched); part 3/3 only extends their reader-facing description in the
"Installing" section.

**Approach.**
- `tools/make_cursors.py` (new): follow `tools/make_wallpaper.py`'s direct-or-package import block,
  `require_within_repo` containment guard and `report_error` diagnostics. It holds the 16x16 arrow
  pixel grid as ASCII rows (`#` black face, `.` white outline, space transparent) with the tip at
  (1,1), scales it nearest-neighbour to 16, 24 and 32 (hotspot scaled by the same mapping), encodes
  each frame with `encode_rgba_png` and assembles each file with `write_cursor`, writing `left_ptr`
  and the three aliases as byte-identical copies (not symlinks) into the repository's
  `theme/icons/org.macos8.desktop/cursors/`. The output is deterministic, so re-running it
  rewrites identical bytes; it refuses an output directory that resolves outside the repository,
  naming the path.
- Committed artifacts: the four generated files under
  `theme/icons/org.macos8.desktop/cursors/` (small binaries, regular git blobs, no LFS filter).
- `tests/test_cursors_theme.py` (new): run the generator into a temp directory twice, asserting
  byte-identical output; parse the committed `left_ptr` with `tests/support/xcursor.py` (part 2/3)
  and pin: exactly one image chunk per nominal size in {16, 24, 32}; each chunk's PNG payload
  decodes with `decode_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its expected
  set and `TestInstall.INSTALLED_FILES` extends its registry, so both equal the package tree with
  the four cursor files added (the inherited `test_installed_files_registry_covers_the_package`
  compares that registry against `shipped_files(self.PACKAGE_DIR)`). The SVG-level assertions
  iterate the explicit `SHIPPED_ICONS` tuple, not `shipped_files`, so they need no change; the
  placeholder register stays untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add one row to the existing `## icons` section — the icon theme's
  `cursors/left_ptr` draws the black face and white outline at nominal sizes 16/24/32 with the
  hotspot at the tip, and its `arrow`, `default` and `top_left_arrow` aliases are byte-identical to
  it — pinned to `tests/test_cursors_theme.py::TestCursorArtifact`, carrying the provenance
  exception above (no screenshot shows a pointer). Do not add a `## cursors` section:
  `tests/invariants.py` accepts only `theme/` subsystem sections plus
  `EXTRA_SECTIONS = ("tooling",)`, so an unregistered section fails `make check`.

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `tools/xcursor.py` (only its module docstring's forward
reference to a `## cursors` section becomes the `## icons` row), `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). The
`Makefile`, `.gitattributes` and `tests/invariants.py` are untouched; do not edit
`PLANS-DONE.md` (this replan already annotated its part 2/3 entry).

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; each chunk's
  PNG payload decodes with `tools.png.decode_rgba`, and its width/height equal the nominal size;
  the pinned pixels and hotspots hold for all three nominal sizes (scaled accordingly); the
  aliases are byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size
  from the generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin and `TestInstall.INSTALLED_FILES` hold with the four
  cursor files (removing one, or editing the committed grid's colours, fails the matching test),
  while the SVG-level assertions still iterate only `SHIPPED_ICONS`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## icons` row; `grep -n '^## cursors' docs/invariants.md` prints nothing; `git diff
  --name-status` names only the files listed under "Files touched" (besides the backlog move) and
  none of `Makefile`, `.gitattributes`, `tests/invariants.py` or `PLANS-DONE.md`.
- The entry moves from `## Planned` under `## Done` with its Done stamp, verified on the pre-merge
  working diff: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
  `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. No acceptance criterion
  refers to `PLANS.md` or `PLANS-DONE.md` after the merge.

### Firefox Platinum chrome, part 1/2: Ship the `userChrome.css` stylesheet (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the profile install) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** GTK series parts 1/4–3/4 landed the GTK 3 and GTK 4 Platinum sheets and their opt-in
install and selection. Part 4/4 is Firefox: `browser.tabs.inTitlebar=0` in a Firefox profile gives
Firefox a KWin-drawn Aurorae frame, but its tab strip, toolbars and menus keep Firefox's own look.
This part ships the stylesheet alone, `theme/firefox/org.macos8.desktop/chrome/userChrome.css`,
written against Firefox's `userChrome.css` chrome selectors and its own chrome theme variables,
with a test module. It adds no Makefile target, no profile write, no preference and no selection:
installing the sheet into a profile's `chrome/` directory and setting
`toolkit.legacyUserProfileCustomizations.stylesheets=true` is part 2/2, which is not queued yet (a
later plan run writes it with "requires part 1/2 landed" in its heading).

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows Firefox's chrome, so no
reference pixel is sampled; the sheet is checked only against the shared palette and its own
rules. Its palette is the reference-grounded values in `tests/support/platinum_palette.py`
(`#DDDDDD` face, `#FFFFFF` white, `#999999` grey, `#000000` black, `#EEEEEE` trough, `#CCCCFF`
selection) plus the GTK sheets' `#888888` etched-separator dark half. Firefox's
chrome custom-property names (`--lwt-accent-color`, `--toolbar-bgcolor`, `--tab-selected-bgcolor`,
`--arrowpanel-background`, …), its XUL selectors (`#TabsToolbar`, `.tab-background`, `#nav-bar`,
`#urlbar-background`, `menupopup`, …) and the `userChrome.css` filename are Firefox-required values
the reference set does not show; the geometry below adapts the desktop theme's Platinum tab,
toolbar and menu faces, not a reference crop. No repository test runs Firefox, so only the rules
and palette are pinned here — whether Firefox draws them is observable only after part 2/2
installs the sheet into a profile. Record that provenance
exception in `docs/invariants.md`. The sheet carries no image, so `.gitattributes` is untouched.

**Approach.**
- `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (new): a comment header naming the
  provenance exception, the palette source and the preference part 2/2 must set; no `@` character
  anywhere (so it has no at-rule and `tests/support/gtk_css.py::parse_css`, which walks plain rule
  blocks, reads it); every declaration that must beat Firefox's own chrome rule carries
  `!important`. The required rules are exactly these (extra palette-only rules are allowed, but
  the test pins these):
  - `:root` sets `--lwt-accent-color: #DDDDDD`, `--lwt-text-color: #000000`,
    `--toolbar-bgcolor: #DDDDDD`, `--toolbar-color: #000000`,
    `--tab-selected-bgcolor: #EEEEEE`, `--tab-selected-textcolor: #000000`,
    `--arrowpanel-background: #DDDDDD`, `--arrowpanel-color: #000000` and
    `--arrowpanel-border-color: #000000`, each `!important`.
  - `#navigator-toolbox`: `background-color: #DDDDDD !important; border-bottom: 1px solid
    #000000 !important;`.
  - `#TabsToolbar`: `background-color: #DDDDDD !important;`.
  - `#nav-bar`, `#PersonalToolbar` and `#toolbar-menubar`: `background-color: #DDDDDD
    !important; border-bottom: 1px solid #888888 !important; box-shadow: inset 0 -1px #FFFFFF
    !important;` (the GTK sheets' etched toolbar separator, light half under the dark line).
  - `.tab-background`: `background-color: #DDDDDD !important; border: 1px solid #000000
    !important; border-radius: 0 !important; box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px
    #999999 !important;` (the desktop theme's raised Platinum tab face).
  - `.tabbrowser-tab[selected] .tab-background`: `background-color: #EEEEEE !important;
    border-bottom-color: #EEEEEE !important;` (the reference selected-tab face, its bottom border
    dropped as the GTK checked tab does).
  - `#urlbar-background`: `background-color: #FFFFFF !important; border: 1px solid #000000
    !important; border-radius: 0 !important; box-shadow: none !important;` (the white sunken
    Platinum text field, squared).
  - `#statuspanel-label`: `background-color: #DDDDDD !important; color: #000000 !important;
    border: 1px solid #000000 !important; border-radius: 0 !important;`.
  - `menupopup`: `--panel-background: #DDDDDD !important; --panel-color: #000000 !important;
    --panel-border-color: #000000 !important;`.
  - `menupopup > menuitem:hover`: `background-color: #CCCCFF !important;` (the menu selection
    fill the desktop theme's `widgets/background.svg` and the GTK sheets paint).
- `tests/test_firefox_theme.py` (new): `TestFirefoxChrome(unittest.TestCase)` reads the sheet with
  `support.containment.read_text(path, ROOT, encoding="utf-8")` (the containment guard, so a
  checked-in symlink escaping the repository is refused instead of leaking a private file), parses
  it with `support.gtk_css.parse_css` and imports the palette from
  `support.platinum_palette`. A local `assert_rule(selector, expected)` helper asserts each
  required selector is present and carries every listed declaration, including the `!important`
  suffix. It also asserts: `set(HEX.findall(text))` is exactly {BLACK, WHITE, GREY, FACE, TROUGH,
  SELECTION, ETCH_DARK}; `"@" in text` is false; the text mentions no
  `adwaita`; no selector contains `*`; the header names the provenance exception and the
  preference (`toolkit.legacyUserProfileCustomizations.stylesheets`) part 2/2 will set; and
  `README.md`, read through the same containment reader, names the sheet's repository path.
- `README.md`: in the "Installing" section after the GTK paragraph, add a Firefox paragraph saying
  the standalone Platinum `userChrome.css` ships at
  `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, that no target installs or selects it
  yet, that part 2/2 will copy it into a Firefox profile's `chrome/` directory and set
  `toolkit.legacyUserProfileCustomizations.stylesheets=true`, and that setting
  `browser.tabs.inTitlebar=0` makes Firefox use the KWin Aurorae frame. Change no artifact count
  and no `tumwater:status` text.
- `docs/invariants.md`: add a `## firefox` section with one row — the standalone sheet paints the
  Platinum palette on Firefox's tab strip, navigation bar, toolbars, menus and status panel with
  no at-rule and no import — pinned to `tests/test_firefox_theme.py::TestFirefoxChrome`, with the
  provenance exception above (no reference screenshot shows Firefox chrome; the geometry is the
  theme's adaptation of the Platinum controls).
- `PLANS.md`: this entry moves under `## Done` (see Plan record) and the scope-drift paragraph's
  part 4/4 sentence now names part 1/2 and part 2/2.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css` (new),
`tests/test_firefox_theme.py` (new), `README.md`, `docs/invariants.md` and `PLANS.md` (this entry
and the scope-drift sentence). Do not edit `PLANS-DONE.md`, `Makefile`, `.gitattributes`, any
`theme/gtk/` path or any `tests/support/` module; no test-side spec module is needed for one sheet.

**Acceptance criteria.**
- `tests/test_firefox_theme.py` finds every required selector with every listed declaration and
  the `!important` suffix, the hex-literal set equal to the seven palette values above, no `@`
  character, no `adwaita`, no universal selector, the header naming the provenance exception and
  the profile preference, and the README path; deleting a rule, dropping `!important` from a
  declaration or writing a non-palette hex makes the matching assertion fail.
- `make check CHECK_TESTS=test_firefox_theme` passes, then `make check` is green; `tests/invariants.py`
  accepts the new `## firefox` row (it names a `theme/firefox` subsystem and a test that exists).
- `git diff --name-status` names only the files listed under "Files touched" (including the
  `PLANS.md` move) and does not name `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`. No acceptance criterion refers to `PLANS.md` or `PLANS-DONE.md` after
  the merge.

### Platinum cursor theme, part 2/3: Xcursor binary writer and test-side parser (planned 2026-10-23 by the plan role; rewritten 2026-10-23 by the plan role; "requires part 1/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD by the feature role` to its `### ` heading. Do not edit `PLANS-DONE.md`:
tumwater archives `## Done` entries into that file after the merge, so neither its content nor
`PLANS.md` after the merge is evidence this change controls. Verify the move on the pre-merge
working diff only: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
`grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. Do not claim any grep output
for this entry's heading after the merge; tumwater may already have moved it out of `PLANS.md`.

**Goal.** Part 1/3 added the RGBA PNG codec (`tools/png/write.py::encode_rgba_png`,
`tools/png/read.py::decode_rgba`). This part adds the Xcursor container the cursor artifact needs:
a standard-library writer that turns PNG frames into one Xcursor file, and an independent
test-side parser that reads that file back and cross-checks the writer's framing. Nothing else:
no generator, no committed cursor files, no Makefile, no README, no `theme/` change, no selection.
The generator, the shipped artifact and its registration are part 3/3 ("requires part 2/3
landed").

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a pointer, so no reference
pixel is sampled here; the Xcursor binary layout is an X/KDE-required value the reference set does
not show. Its facts: a 16-byte file header (`b"Xcur"`, header size 16, file version 0x00010000,
TOC count), one 12-byte TOC entry per chunk (type, subtype, byte offset), and the 36-byte image
chunk header (header size 36, type 0xfffd0002, subtype = nominal size, chunk version 1, width,
height, hotspot x, hotspot y, delay 0). The image payload is `width * height` little-endian
**premultiplied ARGB** words, not PNG bytes: the writer decodes each PNG frame with `decode_rgba`
and premultiplies each colour channel with `(channel * alpha + 127) // 255`, and the parser
converts the stored words back to RGBA and re-encodes them with `encode_rgba_png`. An opaque frame
(alpha 255) therefore round-trips byte for byte; a translucent frame does not, because
premultiplication loses colour precision — the tests pin the stored premultiplied word instead.
Record that provenance first here and carry it into the `## cursors` section part 3/3 adds.

> **Superseded 2026-10-23 by the plan role:** part 3/3 adds the cursor guarantee to the existing
> `## icons` section of `docs/invariants.md`, not a new `## cursors` section, because
> `tests/invariants.py` accepts only `theme/` subsystem sections plus
> `EXTRA_SECTIONS = ("tooling",)`. The rest of this archived entry records what part 2/3 did.

**Approach.**
- `tools/xcursor.py` (new): module constants `MAGIC = b"Xcur"`, `FILE_VERSION = 0x00010000`,
  `FILE_HEADER_SIZE = 16`, `TOC_ENTRY_SIZE = 12`, `IMAGE_TYPE = 0xFFFD0002`,
  `CHUNK_VERSION = 1`, `IMAGE_HEADER_SIZE = 36` and `MAX_IMAGE_SIZE = 0x7FFF`; follow
  `tools/make_wallpaper.py`'s direct-or-package import block and use
  `tools/ints.py::is_plain_int`. `write_cursor(images)` takes one `(nominal_size, width, height,
  hotspot_x, hotspot_y, png_bytes)` record per frame; it rejects a dimension outside 1..0x7FFF, a
  hotspot outside its image, a non-integer (including a bool) numeric field, a PNG field that is
  not `bytes`/`bytearray` and a PNG whose size disagrees with `width`/`height`, each with a
  `ValueError` naming the argument; it decodes with `decode_rgba`, premultiplies, writes the file
  header, one TOC entry per image and each image chunk at its declared offset, so the same records
  always produce byte-identical output. The public surface is `write_cursor` plus those constants;
  no comment chunks.
- `tests/support/xcursor.py` (new): the test-side parser, written independently of the writer and
  importing no symbol from `tools/xcursor.py`. `read_cursor(path)` validates the file header
  (magic, header size 16, version 0x00010000, `ntoc`), reads the TOC, skips a TOC entry whose type
  is not `0xfffd0002` (tolerating, for example, a comment chunk), rejects a chunk offset or length
  outside the file, validates the 36-byte image header (type, chunk version 1, nominal size, width,
  height, hotspot), slices the ARGB payload, converts it back to RGBA and returns a `CursorFile`
  NamedTuple of `CursorImage(nominal_size, width, height, hotspot_x, hotspot_y, png)` records whose
  `png` is `encode_rgba_png(width, height, rgba)`. Errors are `ValueError` naming the path and the
  field or offset that failed.
- `tests/test_xcursor.py` (new): round-trip synthetic opaque frames at 1x1, 2x2, 3x3 and 4x4 whose
  hotspot is the bottom-right tip and whose pixels vary by position: `write_cursor` → `read_cursor`
  reproduces every field and returns the original `encode_rgba_png` bytes exactly. Pin the
  container layout by unpacking the bytes: magic, header size, version, `ntoc`, each TOC entry's
  type/subtype/offset, each chunk's 36-byte header (delay 0) and one known translucent pixel's
  premultiplied ARGB word. Two runs with the same records are byte-identical. Rejections, using
  `tests/support/error_assertions.py`'s `assert_error_names` (the rejections raise `ValueError`, which `assert_rejection_names` does not observe): a truncated file header, a
  truncated image payload, a bad magic, a wrong header size, a wrong version, a corrupt `ntoc`
  whose TOC overruns the file, a hotspot outside its image, a zero dimension, a bool dimension, a
  PNG sized differently from its record and a non-`bytes` PNG, each message naming the argument or
  offset. One test builds a valid file plus a hand-appended unknown TOC entry and shows the parser
  skips it while still returning the image.
- `docs/invariants.md`: untouched. This part ships no artifact, so the `## cursors` row belongs to
  part 3/3, which pins the committed file; this part's guarantees are pinned by
  `tests/test_xcursor.py` alone.

**Files touched.** `tools/xcursor.py` (new), `tests/support/xcursor.py` (new),
`tests/test_xcursor.py` (new) and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not
edit `PLANS-DONE.md`, `Makefile`, `README.md`, `docs/invariants.md` or any `theme/` path.

**Acceptance criteria.**
- `tests/test_xcursor.py`'s round-trip case shows `write_cursor` → `read_cursor` agreeing on every
  field and on the exact PNG bytes for all four opaque synthetic sizes; two runs with the same
  records produce byte-identical files; the layout pin finds the constants above at their stated
  offsets with delay 0 and the expected premultiplied translucent word; each malformed input above
  raises `ValueError` whose message names the offending argument or offset; the hand-appended
  unknown TOC entry is skipped and the remaining image still parses.
- The test-side parser is independent of the writer:
  `grep -n 'from tools import xcursor\|from tools\.xcursor' tests/support/xcursor.py` prints no
  line.
- `make check CHECK_TESTS=test_xcursor` passes, then `make check` is green; removing a guard,
  offsetting a chunk or changing a constant makes the matching test fail.
- `git diff --name-status` names only the files listed under "Files touched" (including the
  `PLANS.md` move) and does not name `PLANS-DONE.md`; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`. No acceptance criterion refers to `PLANS.md` or `PLANS-DONE.md` after
  the merge; tumwater archives the `## Done` entry into `PLANS-DONE.md`.

### Retire the `no-observability` validation gap with test-side observability (planned 2026-10-23 by the steward role; promotes the recurring `gap: no-observability` tag, 21 Fixed entries) — done 2026-10-23 by the feature role

**Goal.** Twenty-one Fixed entries in BUGS-FIXED.md carry `gap: no-observability` — failures that left no trace the suite could see, so the bug could not be confirmed until instrumentation was added. Retire the tag by adding test-side observability helpers (trace capture, structured failure logging) that make such failures reproducible offline, so new bugs in those areas are confirmable without a real run.

**Cited entries.** BUGS-FIXED.md lines recording `gap: no-observability` (21 entries), including the aurorae reader FIFO, containment guard, config-reading quirks, and invariants/placeholders register rows.

**Acceptance criteria.** `make check` is green; the promoted tag's count stops growing.

**Implementation note (2026-10-23).** Twelve of the thirteen one-line records were already retired by the record-checker mutation harness (`tests/test_checker_mutations.py`), the remaining palette-provenance record was retired by `tests/test_colorscheme.py::TestProvenanceNote`, and each of the eight prose records already names the test that reproduces it offline. This change makes the coverage explicit and bounded: `tests/support/validation_gaps.py` parses both record forms into a structured ledger mapping each mechanism to its reproducing test, and `tests/test_validation_gaps.py` asserts every archived record maps to a real test and caps the count at its 21-record baseline, so a new `no-observability` tag fails the suite instead of growing the gap. The invariant register's tooling row records the guarantee.

### GTK opt-in, part 3/3: Select the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-21 by the plan role; rewritten 2026-10-23 by the plan role; parts 1/3 and 2/3 landed) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
3/3: Select the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one line
whose number is greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select the
installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of
`git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 3/4 installs the GTK 3 and GTK 4 sheets under
`$XDG_DATA_HOME/themes/org.macos8.desktop`, but nothing selects them, so GTK applications still
draw their system theme. Add `make apply-gtk` and `make remove-gtk` plus `tools/apply_gtk.py`:
set `gtk-theme-name=org.macos8.desktop` in both GTK settings files and give libadwaita
applications the GTK 4 sheet as user CSS. Parts 1/3 and 2/3 landed the opt-in install family and
the installed file layout; this entry does not reimplement them. It does not add Firefox chrome, which remains
GTK series part 4/4 and is not planned here.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK settings path, the `gtk-theme-name` key and the
libadwaita user-CSS path are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop.

**Approach.**
- `Makefile`: add public targets `apply-gtk` (refuses a non-empty `DESTDIR`, requires Python with
  both `require_python` and `require_python_version`, runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`, then `$(PYTHON) tools/apply_gtk.py`) and `remove-gtk` (requires
  Python the same way, runs `$(PYTHON) tools/apply_gtk.py --remove`). Add them to `.PHONY` and to
  `help`'s target list. Keep `install-gtk` unchanged.
- `tools/apply_gtk.py` (new): follow `tools/apply_theme.py`'s direct-or-package import block,
  `EscapingArgumentParser`, `report_error`, `report_failure` and `escape_controls`. Put the
  fallback in two module-level helpers so both are directly testable: `_config_home(env)` returns
  an absolute `$XDG_CONFIG_HOME`, else an absolute `$HOME/.config`, else `None`; `_data_home(env)`
  returns an absolute `$XDG_DATA_HOME`, else an absolute `$HOME/.local/share`, else `None`. `main`
  passes `os.environ` to both and, when either is `None`, exits 2 through `report_error` naming
  the ineffective variable and saying to set `XDG_DATA_HOME`/`XDG_CONFIG_HOME` or an absolute
  `HOME` -- the same resolution and refusal as the Makefile's `require_data_home`. Resolve both
  homes before requiring the installed sheet, so the refusal is testable without an install.
  Constants: `TOOL = "apply_gtk"`, `GTK_ID = "org.macos8.desktop"`, the marker comment
  `/* org.macos8.desktop GTK 4 user CSS */`, and the installed CSS path built from the resolved
  data home.
- `tools/apply_gtk.py`: for apply, require the installed
  `themes/org.macos8.desktop/gtk-4.0/gtk.css` (exit 1 naming `make install-gtk` when absent); in
  `$XDG_CONFIG_HOME/gtk-3.0/settings.ini` and `gtk-4.0/settings.ini` set
  `gtk-theme-name=org.macos8.desktop` in `[Settings]`, preserving every other line, stripping a
  leading UTF-8 BOM only for matching and writing it back, replacing the last `gtk-theme-name`
  line in the section or inserting one after the `[Settings]` header, and appending `[Settings]`
  when it is absent; write both files through a `.staging` sibling and `os.replace`. Write
  `$XDG_CONFIG_HOME/gtk-4.0/gtk.css` as the marker line followed by
  `@import url("<installed gtk-4.0/gtk.css as a file URI>");` (use `Path.as_uri()`), but leave an
  existing `gtk.css` whose first line is not the marker untouched and print a note. For `--remove`,
  delete the marker `gtk.css`, and delete only `gtk-theme-name` lines in `[Settings]` whose value
  is `org.macos8.desktop`, leaving foreign values and files. Both modes print a note that running
  GTK applications must be restarted.
- `tests/test_gtk_apply.py` (new): drive `tools.apply_gtk.main` with `XDG_CONFIG_HOME` and `HOME`
  pointed at a temp directory. Pin: apply writes both settings files with `[Settings]` and our
  `gtk-theme-name`; it preserves an existing `gtk-font-name` line and a comment; it replaces an
  existing `gtk-theme-name`; it appends `[Settings]` when absent; it creates the marker `gtk.css`
  whose second line imports the installed sheet as a file URI; it exits 1 naming `make install-gtk`
  when the installed sheet is missing; a foreign `gtk.css` is left byte-identical with a note;
  `--remove` removes our key and marker and leaves a foreign key and file. Add `TestHomeResolution`
  that patches the environment for `main` and pins every helper branch: an absolute
  `XDG_DATA_HOME` is used even with `HOME` unset (with `XDG_CONFIG_HOME` absolute); an empty and a
  relative `XDG_DATA_HOME` each fall back to `$HOME/.local/share`; an empty and a relative
  `XDG_CONFIG_HOME` each fall back to `$HOME/.config`; and the diagnostic pins
  `test_missing_data_home_names_xdg_data_home` and
  `test_missing_config_home_names_xdg_config_home` each call `main` with the variable unset or
  relative and `HOME` unusable, then, after `assert_failed` from `support.process_assertions`,
  assert `result.stderr` contains `XDG_DATA_HOME` or `XDG_CONFIG_HOME` respectively -- a bare
  exit-code assertion does not pin the diagnostic. Add `TestMakeApplyGtk` mirroring
  `tests/test_apply_theme.py`'s `TestMakeApply`, with all five pins as named methods, each also
  asserting its exact diagnostic or output substring, never the return code alone:
  `test_dry_run_shows_install_before_the_script` (`run_make(["-n", "apply-gtk"], ...)`) asserts
  `assert_succeeded`, that `result.stdout` contains both `INSTALL_PACKAGES=gtk` and
  `tools/apply_gtk.py`, and that `result.stdout.index("INSTALL_PACKAGES=gtk")` is less than
  `result.stdout.index("tools/apply_gtk.py")`; `test_non_empty_destdir_is_refused` runs
  `run_make(["apply-gtk", "DESTDIR=<temp dir>"], ...)`, asserts `assert_failed`, that
  `result.stderr` contains `DESTDIR must be empty`, and that neither stream names
  `apply_gtk.py`; `test_python_version_is_refused` follows `tests/test_make_check.py`'s
  `TestPythonVersion` (a fake interpreter script written to a temp dir, made executable, passed
  as `PYTHON=<fake>`, that exits non-zero for every invocation) and asserts `result.stderr`
  contains `Python 3.10 or newer` and the fake path; `test_dry_run_shows_remove_script`
  (`run_make(["-n", "remove-gtk"], ...)`) asserts `assert_succeeded` and that `result.stdout`
  contains `tools/apply_gtk.py --remove`; and `test_help_lists_both_targets`
  (`run_make(["help"], ...)`) asserts `assert_succeeded` and that a `result.stdout` line starts
  with ``  apply-gtk `` and a line starts with ``  remove-gtk ``.
  Every refusal assertion on an exit status states its diagnostic substring in the same method:
  `test_missing_sheet_names_make_install_gtk` asserts `result.stderr` contains both
  `make install-gtk` and `gtk-4.0/gtk.css`, and the foreign-`gtk.css` pin asserts the stdout
  note names `gtk.css`. A method that asserts only a return code does not implement its pin.
- `README.md`: extend the GTK paragraph from part 3/4 with `make apply-gtk` and `make remove-gtk`
  (the `test_make_help` README check requires the exact target names), both `gtk-theme-name`
  settings keys, the libadwaita `gtk-4.0/gtk.css` marker/import, the need to restart GTK
  applications, and that KDE users can also choose the theme in System Settings -> Application
  Style -> GNOME/GTK Application Style. State that `make remove-gtk` is what clears the selection.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in selection pinned
  to `tests/test_gtk_apply.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the settings keys and user-CSS path are GTK-required.

**Files touched.** `Makefile`, `tools/apply_gtk.py` (new), `tests/test_gtk_apply.py` (new),
`README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record).
Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make apply-gtk` with `XDG_DATA_HOME`, `XDG_CONFIG_HOME` and `HOME` under a temp root writes
  `[Settings]`/`gtk-theme-name=org.macos8.desktop` to `gtk-3.0/settings.ini` and
  `gtk-4.0/settings.ini`, preserves an unrelated key and comment, and writes a `gtk-4.0/gtk.css`
  whose first line is the marker and whose second line is `@import url("file://<installed
  gtk-4.0/gtk.css>");`; the same command fails and its stderr names `make install-gtk` and
  `gtk-4.0/gtk.css` when the installed sheet is absent.
- `make remove-gtk` removes only our `gtk-theme-name` line and marker `gtk.css`; a foreign value
  in `gtk-3.0/settings.ini` and a foreign `gtk-4.0/gtk.css` survive byte for byte.
- `make check CHECK_TESTS='test_gtk_apply test_make_help'` passes; corrupting the settings edit,
  the marker check or a home helper makes the matching test fail; `tests/invariants.py` accepts
  the new row and `make check` is green.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestHomeResolution`; making either helper skip
  the `HOME` fallback, accept a relative value, or return a path when both candidates are
  unusable makes a case fail.
- `make check CHECK_TESTS=test_gtk_apply` passes `TestMakeApplyGtk`; dropping any of its five
  named pins, or asserting a refusal pin only by return code while its named diagnostic
  substring (`DESTDIR must be empty`, `Python 3.10 or newer`, `tools/apply_gtk.py --remove`)
  goes unasserted, does not implement the pin above: mutating the matched message string in
  `tools/apply_gtk.py` or the Makefile recipes -- dropping `make install-gtk` from the
  missing-sheet error, `XDG_DATA_HOME`/`XDG_CONFIG_HOME` from a home refusal, or renaming an
  `apply-gtk`/`remove-gtk` help line -- makes the matching assertion fail.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 3/3: Select the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Select the installed GTK 3 and GTK 4 Platinum themes' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Select the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the GTK selection tool and Makefile targets,
  and its `RISK` names the GTK settings files and libadwaita user CSS; a report that calls the
  change only backlog bookkeeping contradicts the diff.

### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png (planned 2026-10-23 by the plan role; split from the too-large "Generate and ship the Xcursor arrow cursor artifact" entry) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it directly
under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
After the move `grep -n '^## ' PLANS.md` must print exactly `## Planned` and `## Done`, and
`grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md` must print exactly one line, whose
whose number is greater than the `## Done` line's. The final report quotes the actual output of
`grep -l "RGBA PNG encode, decode and read in tools/png" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** The cursor series needs PNG frames that keep alpha: part 2/3 ("requires part 1/3 landed")
decodes Xcursor image chunks that embed RGBA PNG, and part 3/3 generates them.
`tools/png` today only round-trips opaque pixels (`encode_png`, `decode_png`, `read_png`;
`tools/png/read.py` reduces everything through `_to_rgb`). Add `encode_rgba_png`, `decode_rgba` and
`read_rgba` beside the existing pipeline, in the same one-responsibility style, leaving every
existing function byte-identical and every existing caller untouched. Nothing in the repository
consumes the new names yet — that is deliberate ground-laying, not a finished feature, and the
later parts' headings name them. This part is independent of (and runs alongside) the queued GTK
opt-in parts 1/3–3/3.

**Reference grounding.** Codec plumbing carries no visual value and samples no pixel; the pixels
the later cursor parts pin come from part 3/3's own grid and carry its provenance exception. No
new KDE-required value appears in this part.

**Approach.**
- `tools/png/write.py`: add `encode_rgba_png(width, height, rgba)` beside `encode_png`: the same
  deterministic framing (colour type 6, bit depth 8, every row filter type 0, one IDAT at zlib
  level 9, so identical pixels produce identical bytes) but taking packed RGBA, rejecting anything
  that is not `bytes`/`bytearray` of exactly `width * height * 4` and reusing
  `_validate_dimension` for the bounds, each diagnostic naming the offending argument.
  `encode_png`'s behaviour and output stay byte-identical; nothing else in the module changes.
- `tools/png/read.py`: add `decode_rgba(data, max_rows=None)` that reuses the existing pipeline
  (`_CHANNELS`, `_validate_max_rows`, `_parse_ihdr`, `_check_pixel_limit`, `_collect_chunks` and
  the scanline unfiltering) but keeps four samples per pixel and bypasses `_to_rgb`'s palette
  reduction: it returns `(width, height, rgba)`, and its alpha is 255 wherever the source colour
  type has no alpha channel (every type in `_CHANNELS` — 0, 2, 3, 4 and 6). It touches neither
  `Image` nor `decode_png`.
- `tools/png/loader.py`: add `read_rgba(path)` that runs the existing `_read_png_data` file guards
  (non-blocking open, non-regular refusal, `_MAX_FILE_BYTES`, the LFS-pointer diagnostic) and hands
  the bytes to `decode_rgba`. `read_png` and `read_png_size` are untouched.
- `tools/png/__init__.py`: extend the module docstring's name list, the `__all__` list and the
  `from .…` imports with the three new public names, in the established order.
- `tests/test_png_rgba.py` (new, modelled on the codec tests): `encode_rgba_png` round-trips
  through `read_rgba` and `decode_rgba` byte for byte at every alpha value 0..255 in a small image;
  the encoded IHDR declares colour type 6; two runs with the same pixels produce identical bytes;
  a too-short or too-long RGBA buffer, a rejected dimension and a 3-bytes-per-pixel buffer raise
  `ValueError` naming the argument (reuse `tests/support/rejection_assertions.py`); `decode_rgba`
  on a colour-type-2 and a colour-type-3 fixture built with `tests/support/png_fixtures.py`'s
  `make_png` (the decoder tests' own builder) returns alpha 255 everywhere; and `encode_png`'s
  output for a small sample image is recorded as a literal in the test, so the RGBA work cannot
  disturb it.
- `docs/invariants.md`: in the existing `## tooling` section add one row — the RGBA PNG codec
  round-trips alpha byte for byte and leaves `encode_png`'s output unchanged — pinned to
  `tests/test_png_rgba.py`, column 3 `none`.

**Files touched.** `tools/png/write.py`, `tools/png/read.py`, `tools/png/loader.py`,
`tools/png/__init__.py`, `tests/test_png_rgba.py` (new), `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `encode_rgba_png` followed by `read_rgba` returns the original RGBA bytes, at every alpha 0..255
  in the round-trip test; the encoded IHDR declares colour type 6; two runs with the same pixels
  produce identical bytes; an off-size buffer, a bad dimension or a 3-bytes-per-pixel buffer raises
  `ValueError` naming its argument; a colour-type-2 and a colour-type-3 PNG decode with alpha 255
  everywhere; `encode_png`'s pinned sample output is byte-identical to before this change, and no
  existing test changes its expectations.
- `make check` is green with the new module included; corrupting any of the pins above (encoding a
  wrong alpha row, dropping a guard, changing the framing) fails the matching test,
  `tests/invariants.py` accepts the new row, and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and neither `PLANS-DONE.md` nor any `theme/` path.
- When the work lands, `grep -n '^### Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png' PLANS.md`
  prints exactly one line whose number is greater than the `## Done` line's, and
  `grep -F 'Platinum cursor theme, part 1/3: RGBA PNG encode, decode and read in tools/png'
  PLANS-DONE.md` exits 1 with no output.

### GTK opt-in, part 2/3: Uninstall the installed GTK 3 and GTK 4 Platinum themes (planned 2026-10-23 by the plan role; "requires part 1/3 landed") — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### GTK opt-in, part
2/3: Uninstall the installed GTK 3 and GTK 4 Platinum themes' PLANS.md` must print exactly one
line whose number is greater than the `## Done` line's. The final report quotes the actual output
of `grep -l "Uninstall the installed GTK 3 and GTK 4 Platinum themes" PLANS.md PLANS-DONE.md`
(exactly `PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 adds the opt-in `gtk` install family and the staged copies of the three sheets,
but leaves `make uninstall` alone, so uninstalling would leave an orphaned GTK theme and staging
leftovers in the shared `themes/org.macos8.desktop` directory. This part extends `make uninstall`
to remove exactly what part 1/3 installs — the three files, their three staging siblings and the
emptied `gtk-3.0`/`gtk-4.0` directories — and nothing else: `Kvantum/`, the theme directory itself
and every other theme stay in place. It is a follow-on, not a rewrite: the install half is part
1/3, and the selection that points GTK at the installed theme is part 3/3 (`requires part 2/3
landed`).

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel; the uninstall paths are GTK-required values the
reference set does not show. Part 1/3 already records that provenance exception on the install
row; this part extends that same row with the uninstall guarantee rather than adding a new one.

**Approach.**
- `Makefile`: in `_uninstall`, remove `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`
  relative to the part-1/3 `$(GTK_INSTALL_DIR)` and the three `.staging` siblings, then `rmdir`
  `gtk-3.0` and `gtk-4.0` when empty (`|| true`), leaving `Kvantum/` and every other theme
  directory alone. Extend the shared-parent comment to name the `themes/org.macos8.desktop`
  sharing. Do not touch `_install` or the `install_gtk` define.
- `tests/test_gtk_install.py`: add a `TestUninstall` class (modelled on the uninstall cases in
  `tests/test_kvantum_install.py`): after `make install INSTALL_PACKAGES=gtk`,
  `make uninstall` removes the three files and seeded staging leftovers, leaves a pre-planted
  `Kvantum/` file and a sibling second theme directory byte for byte, and repeats successfully.
- `README.md`: extend the part-1/3 GTK paragraph with one uninstall sentence — `make uninstall`
  removes the three GTK files, their `.staging` leftovers and the emptied `gtk-3.0`/`gtk-4.0`
  directories but leaves `Kvantum/` and the theme directory itself.
- `docs/invariants.md`: extend the part-1/3 `## gtk` row with the uninstall guarantee (remove only
  the three files, the staging siblings and the emptied `gtk-3.0`/`gtk-4.0` directories), still
  pinned to `tests/test_gtk_install.py`.

**Files touched.** `Makefile`, `tests/test_gtk_install.py`, `README.md`, `docs/invariants.md`,
and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- After `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` with a planted `Kvantum/` file and a
  second theme directory under `<tmp>/share/themes/`, `make uninstall DESTDIR=<tmp>` removes
  `index.theme`, both `gtk-*/gtk.css` and any planted `.staging` siblings, removes the emptied
  `gtk-3.0` and `gtk-4.0` directories, and leaves the `Kvantum/` file, the second theme directory
  and the `org.macos8.desktop` directory itself untouched; a repeat uninstall succeeds, and so
  does an uninstall on a tree with no GTK install.
- `make check CHECK_TESTS='test_gtk_install test_make_help'` passes; dropping the staging-sibling
  removal, the empty-`rmdir` guard, or letting the removal touch `Kvantum/` makes the matching
  case fail; `tests/invariants.py` accepts the extended row and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`.
- When the work lands, `grep -n '^### GTK opt-in, part 2/3: Uninstall the installed GTK 3 and
  GTK 4 Platinum themes' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's; `grep -F 'Uninstall the installed GTK 3 and GTK 4 Platinum themes'
  PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md` prints exactly `## Planned`
  and `## Done`; and `git diff --name-status` does not name `PLANS-DONE.md`. The final report
  quotes the actual output of `grep -l "Uninstall the installed GTK 3 and GTK 4 Platinum themes"
  PLANS.md PLANS-DONE.md` (exactly `PLANS.md`). The report's `SUMMARY` names `make uninstall` and
  the three GTK files, and its `RISK` names the shared `themes/org.macos8.desktop` directory
  (`Kvantum/` must survive); a report that calls the change only backlog bookkeeping contradicts
  the diff.

### GTK opt-in, part 1/3: Install the GTK 3 and GTK 4 Platinum themes opt-in (planned 2026-10-23 by the plan role; part 1/3) — done 2026-10-23 by the feature role

**Goal.** Parts 1/4 and 2/4 ship `theme/gtk/org.macos8.desktop/index.theme`,
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and
`theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, but no make target copies them, so a GTK
application cannot use them without a manual copy. Add an opt-in `gtk` install family, staged
copies, and an `install-gtk` target, keeping the default `make install` at the families
`INSTALL_PACKAGES` already names and copying no GTK files. Feature sent the 2026-10-21 entry this
splits back as too large for one run; this part carries the install half only. It installs the
three files but does not remove or select them: the uninstall cleanup is part 2/3
(`requires part 1/3 landed`) and the selection is part 3/3; neither is part of this diff.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget, so this part
adds no visual value and samples no pixel. The GTK theme directory name and its `gtk-3.0/` and
`gtk-4.0/` layout are GTK-required values the reference set does not show; record that in
`docs/invariants.md` rather than claiming a GTK reference crop. The sheets' palette is already
grounded through `tests/support/platinum_palette.py`.

**Approach.**
- `Makefile`: add `GTK_ID := org.macos8.desktop`, `GTK_PACKAGE := theme/gtk/$(GTK_ID)` and
  `GTK_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(GTK_ID)`. This is the directory the
  Kvantum package already uses (`.../themes/org.macos8.desktop/Kvantum/`), so the two artifacts
  share a theme directory; do not use `install_package`, which would replace the whole directory
  and delete `Kvantum/`. Name the part-2/3 uninstall in the new comment so the sharing is
  documented before the removal lands.
- `Makefile`: add `gtk` to `INSTALL_FAMILIES` but not to the default `INSTALL_PACKAGES`; reword
  the comment above them so it says the default installs the families `INSTALL_PACKAGES` names and
  that `gtk` is opt-in. Add a `define install_gtk` after `install_kvantum`: create
  `$(GTK_INSTALL_DIR)/gtk-3.0` and `gtk-4.0`, copy `index.theme`, `gtk-3.0/gtk.css` and
  `gtk-4.0/gtk.css` to the hidden staging siblings `.index.theme.staging`,
  `gtk-3.0/.gtk.css.staging` and `gtk-4.0/.gtk.css.staging` under one EXIT trap that removes all
  three, then rename each into place. A failed copy leaves the previous files untouched and
  removes every staging sibling.
- `Makefile`: gate the `install_gtk` call on `gtk` in `_install`; do not touch `_uninstall` in
  this part.
- `Makefile`: add the public `install-gtk` target (runs the nested `$(MAKE) --no-print-directory
  install INSTALL_PACKAGES=gtk`), add it to `.PHONY` and the `help` target list.
- `tests/support/gtk_fixtures.py` (new): `GTK_ID`, `PACKAGE` and `SHIPPED_FILES` naming
  `index.theme`, `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`, so this part's test and the part-2/3
  uninstall and part-3/3 selection tests can share them.
- `tests/test_gtk_install.py` (new, modelled on `tests/test_kvantum_install.py` because the theme
  shares `themes/org.macos8.desktop`): the source package's `shipped_files` equals
  `SHIPPED_FILES`; `make install INSTALL_PACKAGES=gtk` copies all three byte for byte beside a
  pre-existing `Kvantum/` file and is repeatable; a default `make install` writes no
  `index.theme` or `gtk-*/gtk.css` but still writes `Kvantum/`; a shadowed failing `install`
  leaves the previous three files intact and removes every staging sibling. The uninstall cases
  are part 2/3's additions to this module.
- `tests/support/installed_paths.py`: add `installed_gtk_theme(destdir)` returning
  `themes/org.macos8.desktop` below the module's `XDG_DATA_HOME`, and name the theme in the
  module docstring.
- `tests/support/theme_install.py`: add the GTK suite to the module docstring's artifact list and
  reword `install`'s docstring so it no longer says the default installs every family (the default
  installs every default family; `gtk` is opt-in).
- `README.md`: add a GTK paragraph after the Kvantum section that names `make install-gtk` (the
  `test_make_help` README check requires the exact target name), the installed path
  `$XDG_DATA_HOME/themes/org.macos8.desktop`, the shared `Kvantum/` directory, and that the
  default `make install` copies no GTK files. State that this part installs the files but does not
  select them, and hold the uninstall sentence for part 2/3. Do not add the GTK files to the
  default artifact list or change that list's count.
- `docs/invariants.md`: in the existing `## gtk` section add a row for the opt-in install pinned to
  `tests/test_gtk_install.py`, with the provenance exception that no reference screenshot shows a
  GTK widget and the theme directory layout is GTK-required.

**Files touched.** `Makefile`, `tests/support/gtk_fixtures.py` (new),
`tests/test_gtk_install.py` (new), `tests/support/installed_paths.py`,
`tests/support/theme_install.py`, `README.md`, `docs/invariants.md`, and `PLANS.md`
(the entry moves to `## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=gtk DESTDIR=<tmp>` writes exactly `index.theme`,
  `gtk-3.0/gtk.css` and `gtk-4.0/gtk.css` under `<tmp>/share/themes/org.macos8.desktop/` and
  leaves a pre-existing `Kvantum/` file there untouched; the default `make install DESTDIR=<tmp>`
  still writes the default families and leaves all three GTK files absent.
- A shadowed `install` that fails on a GTK copy leaves the previous three files byte-identical and
  no `.staging` sibling.
- `make check CHECK_TESTS='test_gtk_install test_gtk_theme test_make_help test_theme_install'`
  passes; corrupting a staged copy, removing `gtk` from `INSTALL_FAMILIES`, or adding it to the
  default `INSTALL_PACKAGES` makes the matching test fail; `tests/invariants.py` accepts the new
  row and `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move), does not name `PLANS-DONE.md`, and the README's default artifact list does not gain a GTK
  entry or change its count.
- When the work lands, `grep -n '^### GTK opt-in, part 1/3: Install the GTK 3 and GTK 4
  Platinum themes opt-in' PLANS.md` prints exactly one line whose number is greater than the
  `## Done` line's;
  `grep -F 'Install the GTK 3 and GTK 4 Platinum themes opt-in' PLANS-DONE.md` exits 1 with no
  output; `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`; and
  `git diff --name-status` does not name `PLANS-DONE.md`. The final report quotes the actual output
  of `grep -l "Install the GTK 3 and GTK 4 Platinum themes opt-in" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`). The report's `SUMMARY` names the opt-in GTK install family, the Makefile
  staging and the tests, and its `RISK` names the shared `themes/org.macos8.desktop` directory and
  the opt-in default; a report that calls the change only backlog bookkeeping contradicts the
  diff.

### Select the Lato body face in KDE, Plasma and Qt applications (planned 2026-10-22 by the plan role; UI font series part 3/3, body face only) — done 2026-10-23 by the feature role

**Plan record.** When the work is done, cut this whole entry from `## Planned` and paste it
directly under `PLANS.md`'s existing `## Done` heading, which is the file's last heading, adding
`— done YYYY-MM-DD` to its `### ` heading. Do not add, rename or move a `## ` heading, and do not
edit `PLANS-DONE.md`: tumwater moves the entry from `## Done` into that archive after the merge.
Before editing, record `grep -n '^## Done$' PLANS.md`; after the move, `grep -n '^## ' PLANS.md`
must print exactly two lines (`## Planned` and `## Done`) and `grep -n '^### Select the Lato body
face in KDE, Plasma and Qt applications' PLANS.md` must print exactly one line whose number is
greater than the `## Done` line's. The final report quotes the actual output of `grep -l "Select
the Lato body face in KDE, Plasma and Qt applications" PLANS.md PLANS-DONE.md` (exactly
`PLANS.md`) and of `git diff --name-status`; never claim a file the diff does not name.

**Goal.** Part 1/3 landed the Lato package and `make install` copies it, but the global theme's
`contents/defaults` names no font, so KDE, Plasma and Qt applications keep the user's font
(README's Status line calls the package "installed but not yet selected"). Make the global theme
select the installed `Lato` family for the general, menu, toolbar and smallest-readable fonts and
for window titles, at KDE's default point sizes, by adding those keys to `contents/defaults` —
the same declarative mechanism that already selects the colour scheme, icons, decoration and
Kvantum style. This is the body face of part 3/3 only: part 2/3 (a Chicago-style menu face) has no
confirmed redistribution licence and is not planned, so the menu bar and window titles wear Lato
for now and the part that vendors a Chicago-style face will update `menuFont`/`activeFont` then.
Monospaced text (`fixed`) keeps the user's fixed font because the package ships no monospace
face. No `Makefile`, `tools/` or install behaviour changes: `make install` still only copies the
family, and `make apply` selects it by re-applying the global theme.

**Reference grounding.** No reference pixel is sampled: Lato is this theme's substitute for
Charcoal (`theme/fonts/org.macos8.desktop/PROVENANCE.md`), and the point sizes are KDE's defaults
(10 for `font`, `menuFont`, `toolBarFont` and `activeFont`; 8 for `smallestReadableFont`), not a
metric measured in a screenshot. Record both as provenance exceptions in `docs/invariants.md`;
matching the reference's 12px body text would need a rendered comparison, which this part does
not claim.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/defaults`: in `[kdeglobals][General]`, after
  `ColorScheme=MacOS8`, add `font=Lato,10`, `menuFont=Lato,10`, `toolBarFont=Lato,10` and
  `smallestReadableFont=Lato,8`; add a new `[kdeglobals][WM]` section between it and
  `[kdeglobals][Icons]` holding `activeFont=Lato,10`. Leave every other group, key and byte
  identical.
- `tests/test_lookandfeel.py`: add `WM_SECTION = "kdeglobals][WM"` beside the other section
  constants; in `TestDefaults.test_the_expected_sections_and_keys_are_set` put `WM_SECTION` after
  `DEFAULTS_SECTION`, extend the `DEFAULTS_SECTION` options to `["ColorScheme", "font",
  "menuFont", "toolBarFont", "smallestReadableFont"]` in file order, and expect
  `["activeFont"]` for `WM_SECTION`. Add
  `TestDefaults.test_fonts_name_the_installed_lato_family`: for each of the five
  (section, key) pairs, split the value at the first comma, assert the family is exactly
  `Lato`, assert the remaining point size parses as a positive integer, and assert
  `smallestReadableFont` is not larger than `font`. The test reads the shipped file only; it runs
  no KDE tool.
- `theme/fonts/org.macos8.desktop/PROVENANCE.md`: replace the `## Selection` paragraph's "it does
  not select it ... later part" with the selection this part adds (the five roles, KDE default
  sizes, monospace left alone, the Chicago-style face still pending part 2/3).
- `tests/test_fonts.py`: reword the module docstring's "but does not select it in KDE/Plasma/Qt"
  to say the global theme's defaults select the family; no assertion in the file changes.
- `README.md`: in the Status line change "installed but not yet selected" to "selected by the
  global theme"; in the Installing font sentence replace "this part installs the family but does
  not select it" with the five selected roles and KDE's default sizes, that monospaced text keeps
  the user's fixed font, and that menus and window titles use Lato until a Chicago-style face
  lands; in the `make apply` paragraph replace "(the Lato font package is installed but, like
  `make install`, not selected)" with a statement that `make apply` re-applies the global theme,
  which selects Lato, while a bare `make install` only copies it. Leave the artifact count
  (eight) and the target list unchanged.
- `docs/invariants.md`: extend the `## look-and-feel` row whose guarantee lists what
  `contents/defaults` selects to name the `Lato` font family, and add a `## fonts` row pinned to
  `tests/test_lookandfeel.py::TestDefaults`: the global theme selects the installed Lato family
  for the general, menu, toolbar, smallest-readable and window-title fonts; provenance exception:
  Lato is a Charcoal substitute, the point sizes are KDE defaults, and monospace keeps the user's
  fixed font.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/defaults`,
`tests/test_lookandfeel.py`, `theme/fonts/org.macos8.desktop/PROVENANCE.md`,
`tests/test_fonts.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry moves to
`## Done`; see Plan record). Do not edit `PLANS-DONE.md`.

**Acceptance criteria.**
- The defaults file holds exactly the five keys above with the `Lato` family and those sizes,
  `make check CHECK_TESTS='test_lookandfeel test_fonts'` passes, and changing `Lato` to another
  family, dropping a key, adding a sixth font role, or making a size zero, negative or
  non-numeric makes the matching `TestDefaults` assertion fail.
- `tests/invariants.py` accepts the extended look-and-feel row and the new fonts row, and
  `make check` is green.
- `git diff --name-status` names only the files listed under "Files touched" (besides the backlog
  move) and does not name `PLANS-DONE.md`, `Makefile` or any file under `tools/`; README still
  says eight artifacts and lists no new target.
- When the work lands, `grep -n '^### Select the Lato body face in KDE, Plasma and Qt
  applications' PLANS.md` prints exactly one line whose number is greater than the `## Done`
  line's; `grep -F 'Select the Lato body face in KDE, Plasma and Qt applications' PLANS-DONE.md`
  exits 1 with no output; and `git diff --name-status` does not name `PLANS-DONE.md`. The report's
  `SUMMARY` names the `contents/defaults` font selection and its `RISK` names KDE reading the
  font keys from the theme defaults and the menu/window-title face borrowing Lato until a
  Chicago-style face lands; a report that calls the change only backlog bookkeeping contradicts
  the diff.

### Vendor the Lato body font and install it (planned 2026-10-21 by the plan role; part 1/3) — done 2026-10-22

**Plan record.** The backlog move is part of this entry and must not touch any other file. Before
starting, record `grep -n '^## Done$' PLANS.md` (one line) and `grep -n '^### Vendor the Lato body
font and install it' PLANS.md` (one line). When the work is done, cut the whole entry from
`## Planned` and paste it directly under that `## Done` heading, which stays the file's last
heading, adding `— done YYYY-MM-DD` to its `### ` heading. Do **not** add a third `## ` heading, do
**not** rename or move `## Planned`/`## Done`, and do **not** edit `PLANS-DONE.md`: tumwater moves
the entry from `## Done` into that archive after the merge, so a feature-run diff to
`PLANS-DONE.md` is wrong even when it looks like the finished archive. After the move,
`grep -n '^## ' PLANS.md` must print exactly two lines (`## Planned` and `## Done`);
`grep -n '^### Vendor the Lato body font and install it' PLANS.md` must print exactly one line
whose number is greater than `## Done`'s line number; `grep -F 'Vendor the Lato body font'
PLANS-DONE.md` must exit 1 with no output; and `git diff --name-status` must not name
`PLANS-DONE.md`. The final `VERIFIED` line must quote the actual output of `grep -l "Vendor the Lato
body font" PLANS.md PLANS-DONE.md` (exactly `PLANS.md`) and of `git diff --name-status`; do not make
either claim unless that command printed it. If the entry cannot be moved, leave it under
`## Planned` and say so; never edit `PLANS-DONE.md`.

**Goal.** QUESTIONS.md's font answer (2026-10-19) directs the theme to vendor a Chicago/Charcoal-style
font, but no `theme/fonts` directory exists and `make install` copies no font. Ship Lato Regular and
Bold (SIL OFL 1.1, already installed on this machine, so no network fetch) as the Charcoal-style
body face under a new `theme/fonts/org.macos8.desktop` artifact, installed to
`$XDG_DATA_HOME/fonts/org.macos8.desktop`, so a later selection part can name the `Lato` family.
This is part 1/3 of the UI-font series: it vendors and installs the body face only. Part 2/3 will
vendor a Chicago-style menu face once a redistribution licence is confirmed (the ChicagoFLF
provenance is still unresolved, so it is deliberately not shipped here); part 3/3 will select the
installed families in KDE/Plasma/Qt. Neither sibling is in the queue yet, and this part does not
depend on them.

**Reference grounding.** `aboutsystem_betawiki.png`'s dialog body draws Charcoal's narrower
humanist forms at 12px, but the theme ships no Apple font and samples no font pixel: Lato is this
theme's substitute for Charcoal, and `PROVENANCE.md` records it as an approximation rather than a
reference anchor. The two screenshot crops (the menu bar in `desktop_betawiki.png` and the
`System` dialog body in `aboutsystem_betawiki.png`) are recorded there as context for the later
Chicago/selection parts, not copied.

**Approach.**
- Add `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` and `Lato-Bold.ttf`, copied byte for byte
  from `/usr/share/fonts/truetype/lato/` (657,212 and 657,188 bytes; `.gitattributes` leaves
  `.ttf` out of Git LFS, so they are committed directly). Add `LICENSE-Lato.txt` as an exact
  byte-for-byte copy (`cp`, not an editor, heredoc or `sed`) of
  `/usr/share/doc/fonts-lato/copyright`: 5,157 bytes, SHA-256
  `1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97`, ending in the
  `Files: debian/*` stanza's `... for the text of the GNU General Public License version 2".` with
  **no trailing newline**. Do not append a newline (the prior attempt did, producing 5,158 bytes
  and SHA-256 `6664793a025c96e6bb4f319a8c8d5b929296bf0df229db8b1c19e80a5988eb25`); an editor or
  shell substitution that adds one makes the pinned test fail. The `Files: *` stanza carries the
  upstream copyright line and the complete OFL-1.1 body, while the trailing `Files: debian/*`
  stanza is Debian packaging GPL-2+ text that does not cover the fonts. `PROVENANCE.md` records the
  local source paths, the upstream source (`http://www.latofonts.com`, Debian package `fonts-lato`),
  the SHA-256 digests of all three files, that `LICENSE-Lato.txt` is the source byte for byte
  including its missing final newline (not a newline-appended variant), the internal family name
  `Lato`, the `debian/*` stanza's scope, and why the face is an approximation of Charcoal.
- `Makefile`: add `FONT_ID := org.macos8.desktop`, `FONT_PACKAGE := theme/fonts/$(FONT_ID)` and
  `FONT_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/fonts`; add `fonts` to `INSTALL_FAMILIES` and to
  the default `INSTALL_PACKAGES`; in `_install` create `$(FONT_INSTALL_DIR)` and copy the package
  with the existing `install_package` swap; in `_uninstall` remove
  `$(FONT_INSTALL_DIR)/$(FONT_ID)` together with its `.staging` and `.old` siblings. Update the
  `help` line's default family list (the default is compared against the `?=` value by
  `tests/test_make_help.py`). Update the two family comments: the `INSTALL_FAMILIES` comment's
  `all seven` becomes `all eight`, and `_uninstall`'s shared-parent-directory comment lists
  `fonts` with the other families.
- `tests/support/installed_paths.py`: add `installed_fonts_dir(destdir)` returning the `fonts`
  directory under `$DESTDIR`'s data home, built from the module's `XDG_DATA_HOME` constant like
  the other helpers, and `installed_font_package(destdir, package_id)` returning its `package_id`
  child, matching the Makefile paths; add the font package to the module docstring's list of
  installed artifacts.
- `tests/support/install_lifecycle_cases.py`: add the font suite to the module docstring's family
  list and change the `MAKE_PACKAGES` comment's `instead of all seven` to `instead of all eight`.
  `tests/support/install_failure_cases.py`: change the same `instead of all seven` comment to
  `instead of all eight` (the font package uses the shared staging swap, so the family count it
  describes gains one). `tests/support/theme_install.py`: add the font package to its module
  docstring's list of installable artifact suites.
- `tests/test_fonts.py` (new): `TestFontFiles` parses each TTF's sfnt `name` table (name ID 1 and
  2) with `struct` and asserts the family is `Lato` and the subfamily is `Regular`/`Bold`; pins the
  SHA-256 of both TTFs (`6f6940be0835c3ddec9199e5fc42be4cbc61ebcfd58c623fdf719366253f1780` and
  `bf1b8130069b44b9148eeece35e5423bedac49777ba746615b826b8276574a7b`) and of `LICENSE-Lato.txt`
  (`1e6ccc54aa0b0aa4188cda121174f17cf1c28bac9734749bbe1128bb6dd89a97`), asserts that licence's
  last byte is not a newline, and asserts `PROVENANCE.md` names all three digests; asserts
  `LICENSE-Lato.txt` contains `License: OFL-1.1`, the copyright line
  `(c) 2010-2011, Łukasz Dziedzic` and the OFL clause heading `PERMISSION & CONDITIONS` (the file
  has no `SIL OPEN FONT LICENSE` heading, so do not assert that phrase). `TestFontsInstall`
  subclasses `InstallLifecycleCases` with `MAKE_PACKAGES = "fonts"`,
  `PACKAGE_DIR = "theme/fonts/org.macos8.desktop"`, `INSTALLED_FILES` naming the four files, and
  `installed_parent`/`installed_package_dir` overridden to the new helpers, so it gets the
  byte-for-byte, registry-coverage, repeat-install and uninstall-leftover checks once. Add
  `test_uninstall_leaves_a_sibling_font_family`, which creates `$fonts/other-family` before the
  uninstall and asserts it survives.
- `tests/test_theme_install.py`: in `TestWhitespaceInInstallPaths`, add
  `installed_paths.installed_font_package(destdir, package)` to the `directories` list checked
  before and after the round trip, and change both `seven artifacts` docstrings to eight. In
  `TestInstallPackages.test_one_family_installs_only_that_family`, add
  `installed_paths.installed_fonts_dir(tmp)` to `other_dirs` so installing `color-scheme` leaves
  `fonts/` absent.
- `README.md`: change each of the four `seven artifacts` sentences -- the Status line, the
  Installing paragraph, the uninstall paragraph and the `make apply` paragraph -- to eight, and add
  the `org.macos8.desktop` Lato font package to each list with its
  `$XDG_DATA_HOME/fonts/org.macos8.desktop` path, its OFL-1.1 licence and the note that this part
  installs the family but does not select it. In the uninstall paragraph, add `fonts/` to the
  shared-directory list. Leave the Status paragraph's archive sentence (`... fixed bugs are
  archived in BUGS-FIXED.md.`) byte-identical: it is out of scope for this part, and mentioning
  `PLANS-DONE.md` here would contradict the Plan record above.
- `docs/invariants.md`: add a `## fonts` section between `## desktoptheme` and `## gtk` (every
  `theme/` subsystem needs one) with a row for the shipped Lato family/digests pinned to
  `tests/test_fonts.py::TestFontFiles` and a row for the install/uninstall lifecycle pinned to
  `tests/test_fonts.py::TestFontsInstall`, with the provenance exception stating that Lato is a
  Charcoal substitute, not a sampled reference face.

**Files touched.** `theme/fonts/org.macos8.desktop/Lato-Regular.ttf` (new),
`theme/fonts/org.macos8.desktop/Lato-Bold.ttf` (new),
`theme/fonts/org.macos8.desktop/LICENSE-Lato.txt` (new),
`theme/fonts/org.macos8.desktop/PROVENANCE.md` (new), `Makefile`,
`tests/support/installed_paths.py`, `tests/support/install_lifecycle_cases.py`,
`tests/support/install_failure_cases.py`, `tests/support/theme_install.py`,
`tests/test_fonts.py` (new), `tests/test_theme_install.py`, `README.md`,
`docs/invariants.md`, and `PLANS.md` (the entry moves to `## Done`; see Plan record). Do not edit
`PLANS-DONE.md`.

**Acceptance criteria.**
- `make install INSTALL_PACKAGES=fonts DESTDIR=<tmp>` writes exactly the four files above under
  `$XDG_DATA_HOME/fonts/org.macos8.desktop/`; a default `make install DESTDIR=<tmp>` writes them
  too; `make uninstall` removes that directory and its `.staging`/`.old` leftovers while leaving a
  sibling font family's directory in place (pinned by
  `tests/test_fonts.py::TestFontsInstall.test_uninstall_leaves_a_sibling_font_family`).
- `cmp -s theme/fonts/org.macos8.desktop/LICENSE-Lato.txt
  /usr/share/doc/fonts-lato/copyright` exits 0: the shipped licence is the source's 5,157 bytes
  including its missing final newline, not the 5,158-byte newline-appended variant.
- `make check CHECK_TESTS=test_fonts` passes; removing either TTF, changing a byte, renaming the
  family or subfamily in the font, editing `LICENSE-Lato.txt` (including appending a newline), or
  dropping a digest from `PROVENANCE.md` makes it fail.
- `tests/invariants.py` accepts `theme/fonts` with its `## fonts` section, and
  `make check CHECK_TESTS=test_theme_install test_make_help` passes with the new family.
- `grep -n seven README.md Makefile tests/support/install_lifecycle_cases.py
  tests/support/install_failure_cases.py tests/test_theme_install.py` finds no artifact-count
  text, and the README Status paragraph's archive sentence still reads exactly `Open work is
  tracked in PLANS.md (planned features), BUGS.md (known bugs), and QUESTIONS.md (decisions
  needed); fixed bugs are archived in BUGS-FIXED.md.` (a diff that rewrites it fails this plan).
- `git diff --name-status` names only the files listed under "Files touched"; an edit outside that
  list is out of scope for this part.
- When the work lands, `grep -n '^### Vendor the Lato body font and install it' PLANS.md` prints
  exactly one line whose number is greater than the `## Done` line's; `grep -F 'Vendor the Lato
  body font' PLANS-DONE.md` exits 1 with no output; `grep -n '^## ' PLANS.md` prints exactly
  `## Planned` and `## Done`; and `git diff --name-status` does not name `PLANS-DONE.md`. The final
  report quotes the actual output of `grep -l "Vendor the Lato body font" PLANS.md PLANS-DONE.md`
  (exactly `PLANS.md`) and of `git diff --name-status`; a `VERIFIED` line that says otherwise
  contradicts those commands and fails this plan.
- No `kdeglobals` write, global-theme `contents/defaults` change, `tools/apply_*` change, GTK,
  Firefox or README archive-sentence change is made in this part; `make check` is green.

### Ship a GTK 4/libadwaita Platinum stylesheet (planned 2026-10-21 by the plan role; GTK series part 2/4) — done 2026-10-21

**Goal.** Part 1/4 landed the standalone GTK 3 sheet and its test; GTK 4 applications, including
libadwaita ones such as Ghostty (QUESTIONS.md), still draw the system GTK 4 theme. Add a second
standalone sheet at `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` that redefines the GTK and
libadwaita surface colours from the Platinum palette and paints the same Platinum controls and
bevels in the GTK 4 widget tree. This part ships the stylesheet and its test only: no install
target, no selection mechanism and no README claim. Part 3/4 installs and selects the GTK 3 and
GTK 4 sheets; part 4/4 adds the Firefox chrome. Neither sibling is planned yet, and this part
does not require them. Part 1/4 is finished in `PLANS-DONE.md`; its `index.theme` and
`gtk-3.0/gtk.css` are not changed here.

**Reference grounding.** No screenshot in `macos8.6-screenshots/` shows a GTK widget. Take every
colour from `tests/support/platinum_palette.py` (`FACE` `#DDDDDD`, `WHITE`, `GREY` `#999999`,
`BLACK`, `BUTTON_SHADOW` `#AAAAAA`, `TROUGH` `#EEEEEE`, `SELECTION` `#CCCCFF`) and the etched
separator's dark half `#888888` that `tests/test_desktoptheme_line.py` pins. Record in the CSS
header and in `docs/invariants.md` that the palette is reference-grounded while the GTK 4
geometry is this theme's adaptation. Do not redefine `success_*`, `warning_*`, `error_*`,
`destructive_*` or the translucent `*_shade_color` roles: the reference set gives no Platinum
value for a status colour or a dimming overlay, so those keep the GTK 4 stylesheet's built-in
defaults rather than an invented value.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` (new): a standalone sheet with no `@import`, no
  `url(...)` and no Adwaita mention in its text. Define the GTK named colours with the values
  part 1 uses: `theme_bg_color`/`theme_fg_color`, `theme_base_color`/`theme_text_color`,
  `theme_selected_bg_color`/`theme_selected_fg_color`, `borders` and `unfocused_borders`.
  Define the opaque libadwaita surface names with those same values: `accent_bg_color` =
  `SELECTION`, `accent_fg_color` = `BLACK`, `window_bg_color`/`window_fg_color`,
  `view_bg_color` = `WHITE`/`view_fg_color` = `BLACK`, `headerbar_bg_color` `FACE`,
  `headerbar_fg_color` `BLACK`, `headerbar_border_color` `BLACK`,
  `headerbar_backdrop_color` `FACE`, `popover_bg_color` `FACE`, `popover_fg_color` `BLACK`,
  `card_bg_color` `FACE`, `card_fg_color` `BLACK`, `dialog_bg_color` `FACE`,
  `dialog_fg_color` `BLACK`, `sidebar_bg_color` `FACE`, `sidebar_fg_color` `BLACK`,
  `sidebar_backdrop_color` `FACE`, `sidebar_border_color` `BLACK`,
  `secondary_sidebar_bg_color` `FACE`, `secondary_sidebar_fg_color` `BLACK`,
  `secondary_sidebar_backdrop_color` `FACE`, `secondary_sidebar_border_color` `BLACK`,
  `thumbnail_bg_color` `WHITE`, `thumbnail_fg_color` `BLACK`, and
  `scrollbar_outline_color` `BLACK`.
- Write these scoped rules (no universal `*` selector):
  - `window, .background`: `FACE` background, `BLACK` text.
  - `headerbar, .titlebar`: `FACE` face, `background-image: none`, `1px solid BLACK` border,
    `border-radius: 0`, `box-shadow: none`; `headerbar` with `border-width: 0 0 1px 0`.
  - `button`: `FACE` face, no background image, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: inset 1px 1px WHITE, inset -1px -1px BUTTON_SHADOW`; `button:hover` keeps the
    `FACE`; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px BUTTON_SHADOW, inset -1px -1px WHITE`.
  - `entry`: `WHITE` face, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: inset 1px 1px GREY`, `BLACK` text.
  - `notebook > header`: `FACE` background, `1px solid BLACK` border. Cover the same six tab
    states as part 1, each in plain and `notebook > header > tabs > tab` form: base, hover,
    checked, checked+hover, backdrop and backdrop+checked. Base/hover/backdrop carry the raised
    `FACE` face, `1px solid BLACK`, `border-radius: 0` and
    `box-shadow: inset 1px 1px WHITE, inset -1px -1px GREY`; the checked states use
    `border-bottom-color: FACE` and `box-shadow: none`.
  - `popover > contents, popover > arrow`: `FACE` face, `1px solid BLACK`, `border-radius: 0`,
    `box-shadow: none`.
  - `popover.menu modelbutton:hover, popover.menu modelbutton:selected`: `SELECTION` background.
  - `scrollbar > range > trough`: `TROUGH` background, `1px solid BLACK`, `border-radius: 0`.
  - `scrollbar > range > trough > slider`: `FACE` face, no background image,
    `1px solid BLACK`, `border-radius: 0`, `margin: 0`, and the raised `WHITE`/`GREY` bevel.
  - `.toolbar`: `FACE` face with the etched rule `border-bottom: 1px solid #888888` and
    `box-shadow: inset 0 -1px WHITE`.
- `tests/support/gtk_css.py` (new): move `parse_css` and the `DEFINE_COLOR`, `COMMENT`, `RULE`
  and `HEX` regular expressions out of `tests/test_gtk_theme.py` unchanged, with a short module
  docstring saying the two GTK sheet tests share them. Update `tests/test_gtk_theme.py` to import
  `HEX` and `parse_css` from `support.gtk_css` and delete its local copies, so both tests use one
  parser rather than a second copy of the same rules.
- `tests/test_gtk4_theme.py` (new): mirror `TestGtkTheme`. Pin the exact `@define-color` map,
  every selector/property above, and all six tab-state groups in both selector forms. Assert the
  CSS contains no `@import`, no `url(` and no Adwaita text; assert the only six-digit hex
  literals are exactly `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`;
  assert no universal `*` selector; assert `border-radius: 0` on the window, headerbar, button,
  entry, notebook-header, popover, scrollbar and tab rules.
- `docs/invariants.md`: in the existing `## gtk` section add a second row: "The standalone GTK 4
  stylesheet redefines the Platinum palette and opaque libadwaita surface colours and paints the
  scoped Platinum control rules, including every tab state, without importing another
  stylesheet." pinned to `tests/test_gtk4_theme.py::TestGtk4Theme`, with the same provenance
  exception as part 1.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` (new),
`tests/support/gtk_css.py` (new), `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The new sheet exists at `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css` and carries the exact
  `@define-color` map and the scoped rules above; the original `index.theme` and
  `gtk-3.0/gtk.css` are unchanged.
- `make check CHECK_TESTS='test_gtk_theme test_gtk4_theme'` passes. Adding an `@import` or `url(`,
  removing a `@define-color` or a listed rule/state, replacing a bevel or the scoped
  `border-radius: 0`, or introducing a Breeze/default colour literal makes the GTK 4 test fail;
  the extracted parser leaves every part 1 assertion passing.
- The parsed GTK 4 hex set is exactly the eight pinned colours, and the CSS redefines no
  status or translucent shade role.
- `tests/invariants.py` accepts the second `## gtk` row, and `make check` is green.
- No install target, selection mechanism, `kdeglobals` write, README change or Firefox change is
  made in this part.

### Ship a GTK 3 Platinum theme for GTK applications (planned 2026-10-21 by the plan role; part 1/4) — done 2026-10-21

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
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: write a standalone sheet -- **do not**
  `@import` Adwaita. The rejected implementation imported Adwaita and then tried to out-specify
  its reorderable-tab rules; a standalone theme has no imported sheet whose
  `.reorderable-page` selectors can win, so the tab face cannot fall back to Adwaita's
  translucent or transparent fills. Define the theme colours with
  `@define-color theme_bg_color #DDDDDD;`, `theme_fg_color #000000`,
  `theme_base_color #FFFFFF`, `theme_text_color #000000`, `theme_selected_bg_color #CCCCFF`,
  `theme_selected_fg_color #000000`, `borders #000000` and `unfocused_borders #999999`.
  Write exactly these scoped rules (no `*` selector):
  - `window, .background`: `#DDDDDD` background, `#000000` text.
  - `headerbar, .titlebar`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, no box shadow; `headerbar` keeps only its 1px black bottom rule.
  - `button`: `#DDDDDD` face, no background image, `1px solid #000000` border,
    `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA`;
    `button:hover` keeps the same face; `button:active, button:checked` inverts the bevel to
    `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF`.
  - `entry`: white face, `1px solid #000000` border, `border-radius: 0`, sunken
    `box-shadow: inset 1px 1px #999999`, black text.
  - `notebook > header`: `#DDDDDD` background, black border. Every tab state carries the
    raised `#DDDDDD` face with `1px solid #000000`, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`; the checked states drop the
    bottom border to `#DDDDDD` and the bevel shadow. Cover both the plain and `.reorderable-page`
    forms in each state: base (`tab, tab.reorderable-page`), hover (`tab:hover,
    tab.reorderable-page:hover`), checked (`tab:checked, tab.reorderable-page:checked`),
    checked+hover (`tab:checked:hover, tab.reorderable-page:checked:hover`), backdrop
    (`tab:backdrop, tab.reorderable-page:backdrop`) and backdrop+checked
    (`tab:backdrop:checked, tab.reorderable-page:backdrop:checked`). The checked and backdrop
    states explicitly paint the face rather than leaving it to a default: the rejected diff left
    a non-hovered checked reorderable tab translucent and a backdrop one transparent.
  - `menu, .menu, popover, .popover`: `#DDDDDD` face, `1px solid #000000` border,
    `border-radius: 0`; `menuitem:hover, .menuitem:hover` paints `#CCCCFF`.
  - `scrollbar`: `#EEEEEE` trough with a `1px solid #000000` border; `scrollbar slider` is the
    raised `#DDDDDD` thumb with a `1px solid #000000` border, `border-radius: 0` and
    `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999`.
  - `toolbar, menubar`: `#DDDDDD` face with the reference's etched rule,
    `border-bottom: 1px solid #888888` and `box-shadow: inset 0 -1px #FFFFFF`.
- `tests/test_gtk_theme.py` (new): `TestGtkTheme` reads the two files as text. Pin the
  `index.theme` keys above; pin every `@define-color` name/value, and every selector/property
  above (a parser over brace blocks or explicit substring checks is fine). Assert the CSS
  contains no `@import` and no `Adwaita` text, so a future edit cannot reintroduce the imported
  rules that outranked the tabs. Assert the six tab-state selector groups above each exist with
  the raised face and bevel, and that each checked group also drops the bottom border and bevel,
  so neither a missing state nor a translucent/transparent fallback passes. Assert
  the only six-digit hex literals in the CSS are exactly
  `{BLACK, WHITE, GREY, FACE, BUTTON_SHADOW, TROUGH, SELECTION, ETCH_DARK}`, importing the
  palette constants from `support.platinum_palette` and defining `ETCH_DARK = "#888888"` beside
  the existing line-test value, so a stray Breeze colour fails. Assert the rules for
  `headerbar, .titlebar`, `button`, `entry`, `notebook > header > tabs > tab`,
  `menu, .menu, popover, .popover` and `scrollbar slider` each carry `border-radius: 0`, and
  that no rule uses the universal `*` selector.
- `docs/invariants.md`: add a `## gtk` section (a `theme/gtk` subsystem needs its own section;
  do not fold this into `tooling`) with one row: "The standalone GTK 3 Platinum theme redefines
  the Platinum palette and paints the scoped Platinum control rules, including every plain and
  reorderable tab state, without importing Adwaita." pinned to
  `tests/test_gtk_theme.py::TestGtkTheme`, provenance exception: no reference screenshot shows a
  GTK widget, so the palette comes from the pinned Platinum values and the geometry is this
  theme's adaptation.

**Files touched.** `theme/gtk/org.macos8.desktop/index.theme` (new),
`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` (new), `tests/test_gtk_theme.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- The two new files exist under `theme/gtk/org.macos8.desktop/`; the CSS imports nothing,
  defines the eight theme colours with the values above, and carries every scoped control rule
  and all six plain/reorderable tab-state groups.
- `make check CHECK_TESTS=test_gtk_theme` passes, and adding an `@import`, removing any
  `@define-color`, any listed selector or tab-state group, a bevel shadow or the scoped
  `border-radius: 0` makes it fail.
- The parsed CSS hex set is exactly the eight pinned colours; no Breeze or other colour is
  introduced.
- `tests/invariants.py`'s cross-check accepts the new `## gtk` section and
  `tests/test_gtk_theme.py::TestGtkTheme`.
- No install target, GTK selection, `kdeglobals` write or Firefox change is added in this part;
  `make check` is green.

### Ground the desktop theme dialog body's raised bevel shadow in the reference Get Info window body (planned 2026-10-19 by the plan role) — done 2026-10-21

**Goal.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg` paints the raised
window body's bevel shadow `#999999`, and its header claims "the reference window body itself is
flat, so no window-body pixel grounds those two". But the Get Info window body in
`macos8.6-screenshots/aboutsystem_betawiki.png`, inside its 6px Aurorae frame, is a clean lossless
raised Platinum body: the frame's inner black row/column is the visible outline, a 1px `#FFFFFF`
highlight runs inside the top/left, a 1px `#AAAAAA` shadow inside the bottom/right, the face is
`#DDDDDD`, and the top-right and bottom-left mixed corners leave a `#DDDDDD` face pixel where the
bands would meet. Correct the shadow to `#AAAAAA`, notch those two corners, and pin them to those
pixels.
This is the same raised shadow the Kvantum `button` element and the desktop theme `button.svg`
already use (`PLANS-DONE.md`; PLANS.md), while the reference's sunken field keeps `#999999`, so
only the raised bevel moves. The other desktop-theme raised faces (`widgets/frame.svg`'s raised
state, `widgets/scrollbar.svg`'s thumb, `widgets/toolbar.svg`, `widgets/actionbutton.svg`) are
separate surfaces that the reference's window body does not directly ground; they keep `#999999`
and their shared corner geometry, and are out of scope.

**Reference.** `macos8.6-screenshots/aboutsystem_betawiki.png` (beta `8.6b2c4L8`, the same image
the Kvantum button/check-box groundings use). The Get Info window body: the 6px Aurorae frame's
inner black row/column at top `(200,46)`, left `(12,200)`, bottom `(200,419)` and right
`(354,200)` is `#000000`; the body paints top `(200,47)=#FFFFFF`, left `(13,200)=#FFFFFF`, face
`(200,100)=#DDDDDD`, bottom `(200,418)=#AAAAAA` (uniform across x=40..339) and right
`(353,200)=#AAAAAA`. The four 3x3 corners start at `(12,46)`, `(352,46)`, `(12,417)` and
`(352,417)`; their top-right and bottom-left mixed corners `(353,47)` and `(13,418)` are
`#DDDDDD`, while the shared raised table paints the shadow and highlight there. The retail
`#999999` sunken-field shadow (`firstboot_betawiki.png`) is unchanged.

**Approach.**
- `dialogs/background.svg`: in `bottom`, `right` and the four shadow corners, change the bevel
  shadow `#999999` to `#AAAAAA`; notch the top-right and bottom-left mixed corners to the
  reference's `#DDDDDD` face pixel; leave the `#000000` outline, `#FFFFFF` highlight and
  `#DDDDDD` face elsewhere. Correct the header: the reference window body is a raised bevel, name
  `aboutsystem_betawiki.png` and the sampled pixels (including that the black edge is the Aurorae
  frame's inner row/column), and drop the "flat" claim and the "same bevel rule as
  scrollbar.svg's thumb" cross-reference (the thumb keeps `#999999`).
- `tests/svg_assertions/faces.py`: give `face_corners` a `shadow="#999999"` keyword that rebuilds
  `RAISED_FACE_CORNERS` with the caller's shadow and substitutes it into the sunken tables;
  `face_edge_bands` already takes the keyword from the button plan.
- `tests/svg_assertions/pixels.py`: thread the same `shadow="#999999"` keyword through
  `assert_face_bevel` into `face_edge_bands`/`face_corners`, and add a `corners=None` override for
  a surface whose reference corner geometry differs.
- `tests/support/platinum_palette.py`: no change needed; the button plan already gave
  `assert_fill_palette` its `shadow=GREY` keyword, so this plan reuses it.
- `tests/support/raised_face_case.py`: add a `SHADOW = GREY` class attribute and a `CORNERS =
  None` override, and pass both to `assert_face_bevel`; pass `SHADOW` to `assert_fill_palette`.
- `tests/test_desktoptheme_dialog.py`: set `SHADOW = "#AAAAAA"` and `CORNERS` to the reference's
  four 3x3 corner table on `TestDialogBackground`; add
  `TestDialogBackgroundRaisedReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE`/`MAX_ROWS` from `support.aurorae_fixtures` (the existing
  `TestDialogBackgroundReference` already covers the archiveorg face) that re-derives the four
  colours and four 3x3 corners from the anchors above and asserts the rendered edges and corners,
  skipping when the Git LFS image is not materialized.
- `tests/test_svg_assertions_faces.py` and `tests/test_svg_assertions_pixels.py`: pin the new
  `shadow` keyword in the helper tables and `assert_face_bevel`, and the corner-table override.
- `tests/test_reference_image.py`: add the new reader to the aboutsystem shared-decode-bound
  check.
- `docs/invariants.md`: extend the `dialogs/background.svg` guarantees to name the reference's
  raised bevel shadow and mixed corners.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`,
`tests/svg_assertions/faces.py`, `tests/svg_assertions/pixels.py`,
`tests/support/raised_face_case.py`, `tests/test_desktoptheme_dialog.py`,
`tests/test_svg_assertions_faces.py`, `tests/test_svg_assertions_pixels.py`,
`tests/test_reference_image.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/aboutsystem_betawiki.png 200 418` prints
  `170,170,170 #AAAAAA`, `... 200 47` prints `#FFFFFF`, `... 12 200` prints `#000000`,
  `... 200 100` prints `#DDDDDD`, and `... 353 47` and `... 13 418` print `#DDDDDD`.
- `dialogs/background.svg`'s parsed fill set is exactly `{#000000, #FFFFFF, #AAAAAA, #DDDDDD}`
  and `test_desktoptheme_dialog.py` passes.
- `TestToolBar` and the frame/scrollbar/actionbutton raised tests still pin `#999999` and the
  shared raised corners; the line-edit's and Kvantum item-view's sunken `#999999` shadow is
  unchanged.
- The new reference test re-derives the four colours and four 3x3 corners from
  `aboutsystem_betawiki.png` and asserts both the edges and corners, passing when the image is
  materialized and skipping (not failing) when it is not, through the existing
  `ReferenceScreenshotMixin`/`skip_unless_materialized` path.
- The helper self-tests pin the `shadow` keyword in both the corner tables and
  `assert_face_bevel`, and the reference corner-table override.
- `make check` is green.

### Ground the Kvantum combo box indicator in the reference's double up/down arrow (planned 2026-10-20 by the plan role) — done 2026-10-21

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

### Ground the desktop theme push button's raised bevel shadow in the reference's raised buttons (planned 2026-10-19 by the plan role) — done 2026-10-19

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

### Correct the desktop theme tabbar to the reference's selected System Profiler tab (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` paints every
`*-active-tab` face `#CCCCCC` with a `#DDDDDD` highlight, grounded on the
`desktop_fandom.png` System Profiler tabs -- but that window is inactive and its tabs are
unselected. Plasma 6 requests only the `*-active-tab` ids: `TabButton.qml` uses prefix
`north-active-tab`/`south-active-tab` for every tab and varies only `enabledBorders` by
`checked`, `TabBar.qml` draws that art as the highlight behind the current item, and the
kickoff footer, the system-tray current-item highlight and the panel popups use the same
`*-active-tab` ids. The art is therefore the *selected* tab. The lossless retail
`macos8.6-screenshots/systemprofiler_betawiki.png` shows the selected tab's top and left edge
as three bands -- `#000000` outline, `#CCCCCC` mid-tone, `#FFFFFF` highlight -- over an
`#EEEEEE` face, with an open (face-only) bottom. The shipped 3px nine-slice border has exactly
three rows/columns, so it can paint all three bands; the current art paints only two
(`outline`, `#DDDDDD`) and drops the mid-tone, and its face is the unselected grey.

**Grounding.** At the selected tab's column `x=260` (the first tab, "システム情報"),
`tools/sample.py` reads `y=54 #000000`, `y=55 #CCCCCC`, `y=56 #FFFFFF`, `y=57 #EEEEEE`, and
the open bottom `y=72 #EEEEEE`. Its left edge at `y=60` reads `x=225 #000000`, `x=226 #CCCCCC`,
`x=227 #FFFFFF`, `x=228 #EEEEEE`. The unselected tab at `x=450` reads `y=54 #000000`,
`y=55 #CCCCCC`, `y=56 #DDDDDD`, `y=57 #CCCCCC`, `y=70 #000000`, which is what the current art
matches.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`: in all four `*-active-tab`
  prefixes change the face fill `#CCCCCC` to `#EEEEEE` (centres, open-edge slices and the base
  rect of every closed-edge slice), and change the closed top/left band from `#000000`,
  `#DDDDDD`, face to `#000000`, `#CCCCCC`, `#FFFFFF` (the third row/column becomes the
  highlight). Keep the closed bottom/right band `face, #999999, #000000` and the face-only open
  edge. Update the header comment to name `systemprofiler_betawiki.png` and the selected tab,
  and drop the `desktop_fandom.png` provenance.
- `tests/test_desktoptheme_tabbar.py`: set `FACE = "#EEEEEE"`, add `MIDTONE = "#CCCCCC"` and
  `HIGHLIGHT = "#FFFFFF"`; set `TOP_LEFT_BAND = ("#000000", MIDTONE, HIGHLIGHT)`, keep
  `BOTTOM_RIGHT_BAND = (FACE, "#999999", "#000000")`, and `FLAT_BAND = (FACE,) * 3`. Rewrite
  `raised_tab_corners` for the three-band top/left bevel: `topleft` is
  `("#000000",) * 3 + ("#000000", MIDTONE, MIDTONE) + ("#000000", MIDTONE, HIGHLIGHT)`,
  `topright` is `("#000000",) * 3 + (MIDTONE, "#999999", "#000000") + (HIGHLIGHT, "#999999",
  "#000000")`, `bottomleft` is `("#000000", MIDTONE, HIGHLIGHT) + ("#000000", MIDTONE,
  "#999999") + ("#000000",) * 3`, and `bottomright` is `(FACE, "#999999", "#000000") +
  ("#999999", "#999999", "#000000") + ("#000000",) * 3`. The `tab_corners` mixed tables build
  from `EDGE_BANDS` and adapt to the new bands unchanged. Update `test_tabbar_palette` and
  `test_tabbar_colours`'s expected set to `{#000000, #CCCCCC, #EEEEEE, #FFFFFF, #999999}`.
- Replace `TestTabBarReference`'s `desktop_fandom.png` face rectangles with the selected tab's
  anchors: assert `self.pixel(260, y)` is `#000000`, `#CCCCCC`, `#FFFFFF`, `#EEEEEE` for
  `y = 54, 55, 56, 57`, `#EEEEEE` at `y = 72`, and at `y = 60` assert `self.pixel(x, 60)` is
  `#000000`, `#CCCCCC`, `#FFFFFF`, `#EEEEEE` for `x = 225, 226, 227, 228` (compare each against
  the module constants `MIDTONE`, `HIGHLIGHT`, `FACE` so the art and the reference stay tied).
  Import `PROFILER_REFERENCE`/`PROFILER_ROWS` from `support.aurorae_fixtures` instead of
  `FANDOM_REFERENCE`/`FANDOM_MAX_ROWS` from `support.desktoptheme_paths`.
- `tests/support/desktoptheme_paths.py`: the `FANDOM_MAX_ROWS` comment lists "the dialog,
  fill-gradient and tab-bar anchors" as its readers; drop the tab-bar entry now that
  `test_desktoptheme_tabbar.py` reads the profiler reference.
- `docs/invariants.md`: add a desktoptheme row: "`widgets/tabbar.svg`'s `*-active-tab` face and
  top/left bevel are the reference active-window selected tab's (`#EEEEEE` face, `#CCCCCC`
  mid-tone, `#FFFFFF` highlight)." pinned by
  `tests/test_desktoptheme_tabbar.py::TestTabBarReference`, with the provenance exception "The
  reference tab is a trapezoid; the nine-slice is rectangular (PLANS-DONE.md)."

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`,
`tests/test_desktoptheme_tabbar.py`, `tests/support/desktoptheme_paths.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Every `*-active-tab` centre, open edge and closed-edge base is `#EEEEEE`; the closed top/left
  band is `#000000`, `#CCCCCC`, `#FFFFFF`; the closed bottom/right band is `#EEEEEE`, `#999999`,
  `#000000`; `test_tabbar_centres_are_the_face`, `test_tabbar_closed_edges_are_raised`,
  `test_tabbar_inner_edges_are_open` and `test_tabbar_corners` pass.
- `TestTabBarReference` re-derives the selected tab's `#000000`/`#CCCCCC`/`#FFFFFF`/`#EEEEEE`
  top band and left edge from `systemprofiler_betawiki.png` and passes; a face left `#CCCCCC` or
  a two-band top/left bevel fails it. It skips, not fails, when the reference is not
  materialized (`skip_unless_materialized`).
- `tabbar.svg`'s header names `systemprofiler_betawiki.png` and the selected tab and no longer
  claims `desktop_fandom.png` as the tab's ground truth.
- `make check` exits 0.

### Ground the Kvantum tab face in the reference's System Profiler tabs (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The Kvantum `[Tab]` element (`frame.element=tab`, `interior.element=tab` in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`) paints every state as a raised
`#DDDDDD` face with a `#FFFFFF` top/left highlight: the `tab-normal-*`, `tab-focused-*` and
`tab-toggled-*` groups in `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`. The retail
reference `macos8.6-screenshots/systemprofiler_betawiki.png` shows two Platinum tab palettes: an
unselected tab is a `#CCCCCC` face with a `#DDDDDD` highlight, and the selected tab is an
`#EEEEEE` face with a `#FFFFFF` highlight. `tests/test_kvantum_bevel_pixels.py` currently pins all
three tab states to the button's `#DDDDDD`/`#FFFFFF` palette, so the wrong art passes. Correct the
art and that test, and add a reference test that re-derives both palettes from the screenshot.

**Grounding.** `systemprofiler_betawiki.png` is the retail Japanese 8.6 System Profiler the
`README` names as window-chrome ground truth. Its tab row runs y=54..70: the first tab
"システム情報" is selected, the others unselected. Sampled with `tools/sample.py`:
- unselected "環境とボリューム" at x=450: y=54 `#000000` outline, y=55 `#CCCCCC`, y=56 `#DDDDDD`
  highlight, y=57 and y=60 `#CCCCCC` face; y=70 `#000000` bottom outline. The "コントロールパネル"
  tab repeats it (x=700).
- selected "システム情報" at x=260: y=54 `#000000`, y=55 `#CCCCCC`, y=56 `#FFFFFF` highlight, y=57
  and y=60 `#EEEEEE` face; y=66..72 `#EEEEEE` (open bottom edge, no outline).
Kvantum draws an unselected tab through `tab-normal`/`tab-focused` and the selected tab through
`tab-toggled` (the same on/selected `toggled` state the button and slider use).

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: in every `tab-normal-*` and
  `tab-focused-*` group change the face fill `#DDDDDD` to `#CCCCCC` and the raised top/left
  highlight `#FFFFFF` to `#DDDDDD`; in every `tab-toggled-*` group change the face fill `#DDDDDD`
  to `#EEEEEE` and keep the `#FFFFFF` highlight. Keep the `#999999` shadow and the `#000000`
  outline in all three.
- `tests/test_kvantum_bevel_pixels.py`: add `SURFACE_HIGHLIGHT = "#FFFFFF"`, `TAB_FACE =
  "#CCCCCC"`, `TAB_HIGHLIGHT = "#DDDDDD"` and `TAB_SELECTED_FACE = "#EEEEEE"`; give
  `_button_edge_maps` and `_button_corners` a `highlight` parameter (default `SURFACE_HIGHLIGHT`)
  instead of the hard-coded `#FFFFFF`; set `SURFACE_STATES["tab"]` to `{"normal": ("raised",
  TAB_FACE), "focused": ("raised", TAB_FACE), "toggled": ("raised", TAB_SELECTED_FACE)}` and
  have `TestSurfaceBevelPixels` pass `TAB_HIGHLIGHT` for the tab's normal/focused states and
  `SURFACE_HIGHLIGHT` for every other state.
- Add `tests/test_kvantum_tab_reference.py`: a `ReferenceScreenshotMixin` class with `REFERENCE`
  and `MAX_ROWS` from `support.aurorae_fixtures` (`PROFILER_REFERENCE`, `PROFILER_ROWS`, so the
  decode is shared with the Aurorae readers). It samples the two tabs above, asserts the sampled
  pixels are `#000000`/`#CCCCCC`/`#DDDDDD`/`#CCCCCC` (unselected) and
  `#000000`/`#CCCCCC`/`#FFFFFF`/`#EEEEEE` (selected), and asserts the shipped `tab-normal`,
  `tab-focused` and `tab-toggled` centre tiles and raised top/left bands paint those palettes.
- `tests/test_kvantum_svg.py`: add the unselected tab face `#CCCCCC` as a named `TAB_FACE`
  extra in `test_uses_exactly_the_platinum_palette`, so the exact-palette assertion still holds
  (the plan's files-touched list had missed this test).
- `docs/invariants.md`: add a kvantum row naming
  `tests/test_kvantum_tab_reference.py::TestTabReference` and its guarantee.

**Acceptance criteria.**
- `tab-normal` and `tab-focused` centres are `#CCCCCC` and their raised top/left band is
  `#DDDDDD`; `tab-toggled` centre is `#EEEEEE` and its raised top/left band is `#FFFFFF`; all three
  keep the `#000000` outline and `#999999` shadow.
  `TestSurfaceBevelPixels.test_every_surface_state_paints_its_bevel` passes.
- The new reference test re-derives the unselected `#CCCCCC`/`#DDDDDD` and the selected
  `#EEEEEE`/`#FFFFFF` from `systemprofiler_betawiki.png` and passes; a tab left `#DDDDDD` fails
  it. It skips, not fails, when the reference is not materialized.
- `make check` exits 0.

**Recorded deviation.** The reference tab's top/left bevel is three bands -- the `#000000`
outline, a `#CCCCCC` mid-tone, then the `#DDDDDD`/`#FFFFFF` highlight, because the highlight is
inset one pixel. The Kvantum tab keeps its existing two-band outline+highlight geometry (the
same 2px bevel the button and line edit use), so this plan corrects the palette only; the
selected tab's open bottom edge is likewise not reproduced.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_tab_reference.py`,
`tests/test_kvantum_svg.py`, `docs/invariants.md`.

### Ground the Kvantum button bevel's shadow in the reference's popup buttons (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The four `button-*` state groups in
`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` paint their bevel shadow `#999999`
(the raised states' bottom/right bands and their three shadow corners, the sunken states'
top/left bands and their three shadow corners). The Get Info window in
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
  the raised states' `-bottom`/`-right` bands and their
  `-topright`/`-bottomleft`/`-bottomright` corners, and the sunken states' `-top`/`-left` bands
  and their `-topleft`/`-topright`/`-bottomleft` corners. Leave the
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
- `tests/test_kvantum_svg.py`: add `BUTTON_SHADOW = "#AAAAAA"` and include it in
  `test_uses_exactly_the_platinum_palette`'s `extra` set, so the palette check accepts the
  button's new fill while still rejecting any other stray fill.
- `docs/invariants.md`: add the kvantum row `| The button bevel is the reference's raised
  popup-button bevel. | tests/test_kvantum_button_reference.py::TestButtonReference | The
  reference's popup button is a beta build (aboutsystem_betawiki.png); it is the set's only
  lossless raised-button bevel. |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_button_reference.py` (new),
`tests/test_kvantum_svg.py`, `docs/invariants.md`.

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

### Correct the shared sunken-outside field's bottom corners to the reference field's true bottom (planned 2026-10-19 by the plan role) — done 2026-10-19

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

### Ground the Kvantum item view's sunken field in the reference Finder content area (planned 2026-10-19 by the plan role) — done 2026-10-19

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
  `lineedit-focused-*` art, except the bottom-left corner below). Rewrite each 2x2 corner as the
  outer 2x2 of `sunken_outside_face_corners("#FFFFFF")` in `tests/svg_assertions/faces.py`,
  except the bottom-left: the reference's bottom highlight starts one pixel in from the left
  ((22,478)=#CCCCCC, the window face), so its outer bottom pixel is left unpainted and the
  #FFFFFF highlight sits at the inner bottom pixel. The top-right outer pixel stays unpainted
  (reference (453,118)=#CCCCCC, the window face). Leave `itemview-pressed-*` and
  `itemview-toggled-*` flat #CCCCFF, and add a comment above the two groups naming the
  reference and its sampled pixels.
- Update the file-header comment (the sentence "the line edit is the white sunken field") to
  name the item view as sharing that field.
- `tests/test_kvantum_bevel_pixels.py`: keep `"itemview"`'s flat `pressed`/`toggled` states in
  `SURFACE_STATES` (so the flat #CCCCFF art stays pinned) and add a `TestItemViewBevelPixels`
  case mirroring `TestLineEditBevelPixels` (reusing `LINEEDIT_EDGES`, `_lineedit_edge_map` and
  `_lineedit_corners`, with an item-view bottom-left override) for prefixes `itemview-normal`
  and `itemview-focused`, so a state repeating the old outline-outside art fails there.
- New `tests/test_kvantum_itemview_reference.py`: a `ReferenceScreenshotMixin` case over
  `setup_emaculation.png` (`MAX_ROWS = 479`) that re-derives the field's four border runs, its
  top-left 2x2 corner and its bottom-left 2x2 corner and asserts the rendered Kvantum
  `itemview-normal` tiles paint the same sunken-outside arrangement; skips when the image is
  not materialized. The reference field's top-right and bottom-right corners sit under the
  status header and the scrollbars, so the test derives only the clean left/top/right/bottom
  runs and the two clean corners (the bottom-left's outer bottom pixel is the window face, so
  the shipped tile leaves it unpainted).
- `docs/invariants.md`: add a `kvantum` row `| The item view is the reference's sunken field:
  the bevel outside the #000000 outline. |
  tests/test_kvantum_itemview_reference.py::TestItemViewReference | none |`.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`,
`tests/test_kvantum_bevel_pixels.py`, `tests/test_kvantum_itemview_reference.py` (new),
`docs/invariants.md`.

**Acceptance criteria.**
- Every `itemview-normal-*` and `itemview-focused-*` edge slice paints the bevel on its outer
  pixel (#999999 top/left, #FFFFFF bottom/right) and the #000000 outline inside it, over the
  unchanged #FFFFFF centre face; the corners wrap that bevel around the outline, except the
  bottom-left, whose outer bottom pixel the reference leaves to the window face (the shipped
  tile leaves it unpainted and paints the #FFFFFF highlight one pixel in).
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 22 250` prints
  `153,153,153 #999999`, `... 23 250` prints `0,0,0 #000000`, `... 24 250` prints
  `255,255,255 #FFFFFF`; the new test re-derives those pixels and the other three runs and
  passes, skipping when the image is not materialized.
- `TestItemViewBevelPixels` fails against the old outline-outside artwork and passes against the
  new.
- The new `docs/invariants.md` row resolves through `tests/invariants.py`.
- `make check` is green.

### Checker unreadable-input mutations: manufacture a register, asset or reference that cannot be read so the checker's own diagnostic is observable (planned 2026-10-19 by the steward role; from the recurring `no-fake` validation gap in four Fixed entries) — done 2026-10-19

**Goal.** Four Fixed entries share one shape: a record checker reads an input that cannot be read
-- a register path that is a directory, a text asset under `theme/` that is a dangling symlink
resolving inside the root, a register reference containing a NUL byte, or a reference to a test
file that cannot be decoded -- and the read raises a bare `OSError`/`ValueError` that names
neither the checker nor the offending row, aborting the check with an unrelated traceback. Each
was confirmed only by hand-building a shim the suite did not have (its `no-fake` gap).
The per-checker mutation tables in `tests/support/invariants_mutations.py` and
`tests/support/placeholders_mutations.py`, over the shared `tests/support/checker_scratch.py`,
already manufacture the malformed register and theme inputs the shipped data never holds; extend
them with the four unreadable-input shapes so confirming the next bug of this kind reuses the
scratch fixture instead of a one-off.

**From (the `no-fake` Fixed entries).**
- `tests/placeholders.py` lets an unreadable register escape as a bare `OSError`.
- `tests/placeholders.py` lets a dangling symlink inside `theme/` escape as a bare
  `FileNotFoundError`.
- `tests/invariants.py` lets a register reference with a NUL byte escape as an unrelated
  exception.
- `tests/invariants.py` lets a reference to an unreadable test file escape as an unrelated
  exception.

**Approach.**
- `tests/support/checker_scratch.py`: teach `Scratch` to clean up a directory it wrote (its
  `reset` only unlinks files today), then add four `Mutation` entries to the per-checker tables
  (`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`):
  `unreadable-register` (replace the register path with a directory so `register_entries`'
  `OSError` arm fires; diagnostic `cannot be read`), `dangling-symlink-inside-theme` (a text
  asset under `theme/` symlinked to a missing path inside the root; diagnostic `cannot be read`),
  `reference-with-nul-byte` (`_replace_first_reference` with a `\x00` in the path; diagnostic
  `NUL byte`), and `unreadable-test-file` (point the first row's reference at a scratch file
  written as undecodable bytes; diagnostic `cannot be read as Python`).
- `tests/placeholders.py` and `tests/invariants.py`: add each new name to `REJECTION_SHAPES` in
  the same commit, so `test_checker_mutations.py`'s two set-equality guards keep each checker's
  boundary list and the mutation table in step.

**Implementation note.** `unreadable-test-file` overwrites the scratch copy of the existing
`MUTANT_MODULE` with undecodable bytes (and `Scratch.reset` now restores an overwritten file)
rather than adding a new scratch path, so the stage self-check's added-nonexistent-path guard
keeps seeing a repository path that exists.

**Files touched.** The checker-mutation fixtures (now `tests/support/checker_scratch.py`,
`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`),
`tests/placeholders.py`, `tests/invariants.py`.

**Acceptance criteria.**
- `tests/test_checker_mutations.py` drives each of the four new mutations, and each makes its
  checker raise the named `AssertionError`; the two unreadable-read mutations fail if the
  checker's `OSError` arm is removed.
- The two `REJECTION_SHAPES` set-equality guards pass with the four new names.
- `make check` is green.

### Ground the Kvantum line edit's sunken bevel in the reference text field (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg` draws the
`lineedit-normal` and `lineedit-focused` frames with the #000000 outline on the outer edge and
the bevel inside it (`lineedit-normal-top` is #000000 then #999999, `lineedit-normal-left` the
same). The reference text field puts the sunken bevel *outside* the outline --
`macos8.6-screenshots/firstboot_betawiki.png` (28,95)=#999999, (29,95)=#000000,
(30,95)=#FFFFFF -- the structure `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`
already paints and `tests/test_desktoptheme_lineedit.py` already pins. Redraw the Kvantum line
edit's tiles as that bevel-outside ring so a KDE application's text field matches the reference.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`: for each of the `lineedit-normal-*`
  and `lineedit-focused-*` frames, rewrite the four edge slices so the outer pixel is the bevel
  (#999999 top/left, #FFFFFF bottom/right) and the inner pixel is the #000000 outline, leaving
  the #FFFFFF centre face unchanged: the top/left slices read #999999 then #000000 from the
  outer edge inward, and the bottom/right slices read #FFFFFF then #000000 the same way (in
  slice coordinates the bottom/right slices are #000000 then #FFFFFF, their outer edge being
  the last row/column). Rewrite each 2x2 corner as the outer 2x2 of the `sunken-outside`
  corner table in `tests/svg_assertions/faces.py` (`sunken_outside_face_corners("#FFFFFF")`), scaled to the 2px
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

### Ground the Kvantum check box face in the reference's raised Platinum check box (planned 2026-10-19 by the plan role) — done 2026-10-19

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

### Ship the Platinum menu submenu arrow (`go-next-symbolic`) grounded in the open Apple menu (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** KDE draws a menu's submenu indicator as a `Kirigami.Icon` with
`source: "go-next-symbolic"` — `PlasmaComponents` `MenuItem.qml`'s `arrow` and the kicker's
`ItemListDelegate.qml` both name that icon — and the icon theme declares `Inherits=breeze`, so
the indicator is Breeze's thin chevron. The reference's open Apple menu
(`macos8.6-screenshots/desktop_archiveorg8.6hd.png`, retail 8.6, already the anchor for the menu
body and the view item) draws a solid black right triangle on each submenu row: at the
"Automated Tasks" row the dark pixels (every channel < #AA) are a 5x9 right triangle with a
full-height left edge, bounding box x=151..155, y=91..99, and the triangle is pure `#000000` at
(152, 93). Ship that triangle as the theme's `go-next-symbolic` so the submenu indicator matches
the reference instead of falling back to Breeze's chevron.

**Approach.**
- Add `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (16x16) and
  `theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (22x22), each a single
  solid `#000000` right-triangle path — 16x16 `M 6,3 L 6,11 L 10,7 Z` (a 5x9 triangle whose left
  edge is full-height and whose tip is at the vertical middle), the 22x22 path the same shape at
  the 22/16 scale — with a header comment naming the `desktop_archiveorg8.6hd.png` anchor and
  recording that the 16px canvas is KDE-required (the reference menu row is ~17px). Draw the
  triangle alone: the reference's 1px lighter left edge (x=150 is #E8E8E8 against the #DDDDDD
  body) is a bevel a `-symbolic` icon cannot keep, because KDE recolours the icon to the menu
  text colour.
- `theme/icons/org.macos8.desktop/index.theme`: add `16x16/actions` and `22x22/actions` to
  `Directories` and add the matching `[16x16/actions]` / `[22x22/actions]` sections (`Size=16`
  and `22`, `Context=Actions`, `Type=Fixed`), so a 16px or 22px lookup resolves to the theme's
  triangle before Breeze's chevron.
- `tests/test_icon_theme.py`: add both icons to `SHIPPED_ICONS` and to `ICON_SHAPES` (one
  `path` element with its `d` and `fill`); `INSTALLED_FILES` derives from `SHIPPED_ICONS`.
- New `tests/test_icon_arrow_reference.py`: a `ReferenceScreenshotMixin` case over
  `desktop_archiveorg8.6hd.png` that re-derives the "Automated Tasks" submenu triangle — the
  dark pixels (every channel < 170) in x=146..159, y=86..104 — asserts it is a right triangle
  (its left column spans the full 9-row height, its widest row is the vertical middle) with a
  5x9 bounding box, and asserts the shipped 16x16 path's bounding box is the same 5x9; it skips
  when the reference is not materialized.
- `docs/invariants.md`: add an icons row naming the new test.
- `README.md`: extend the icon-theme sentence to name the menu submenu arrow alongside the
  kicker logo.

**Files touched.** `theme/icons/org.macos8.desktop/16x16/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/22x22/actions/go-next-symbolic.svg` (new),
`theme/icons/org.macos8.desktop/index.theme`, `tests/test_icon_theme.py`,
`tests/test_icon_arrow_reference.py` (new), `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- Both icons ship, are square SVGs of their declared size (16x16, 22x22), and each one's only
  drawing element is a solid `#000000` right-triangle `path`; `TestIcons` and `TestIconGeometry`
  pass.
- `index.theme` declares both `actions` directories, so
  `test_every_shipped_icon_lives_in_a_declared_size_directory` passes.
- The new reference test re-derives the 5x9 right triangle from `desktop_archiveorg8.6hd.png`
  (`python3 tools/sample.py macos8.6-screenshots/desktop_archiveorg8.6hd.png 152 93` prints
  `0,0,0 #000000`) and passes; it skips (not fails) when the reference is not materialized.
- `make check` is green.

Recorded scope: the RTL names (`go-next-rtl-symbolic`, `go-next-symbolic-rtl`) are not shipped;
the theme targets the reference's LTR English UI, so a right-to-left layout keeps Breeze's
chevron.

### Ground the Aurorae inactive frame in the reference's inactive windows (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The `decoration-inactive` nine-slice and its header comment claim "the reference set has
no inactive window" and therefore paint KDE-required greys: the active tile's
`#FFFFFF`/`#777777` pinstripes and `#CCCCCC` field flattened to `#CCCCCC`, keeping the `#000000`
outlines and the `#999999` shadow. The reference set does show inactive windows:
`macos8.6-screenshots/desktop_fandom.png` (retail 8.6, the image the tabbar and progressbar
already sample) shows four unfocused windows (the "Mac OS 8.6", "Utilities", "Applications" and
"Apple System Profiler" windows), and the lossless beta `macos8.6-screenshots/
systeminfo_betawiki.png` shows a fifth behind the active "System Info" window. Their frame is a
flat `#DDDDDD` field with a 1px `#555555` outline on both the outer and inner edges of the
border (the outer edge and the inner edge that meets the client), with no pinstripes, no
white highlight and no `#999999` shadow (verified with `tools/sample.py`; the scheme's own
`[WM] inactiveBackground=221,221,221` agrees). Correct the art and the provenance, and pin the
inactive frame to the reference pixels.

**Approach.**
- `theme/aurorae/themes/org.macos8.desktop/decoration.svg`: rewrite every `decoration-inactive-*`
  tile to the reference's flat inactive frame — the 1px `#555555` outer and inner outlines
  (the top and bottom rows of `decoration-inactive-top`, the outer and inner columns of the
  side tiles, the outer and inner rows of the bottom tiles, and the corner pixels where they
  meet) and `#DDDDDD` everywhere between; recolor the `#000000` outlines to `#555555` and drop
  the `#999999` shadow and the `#FFFFFF`/`#777777`/`#CCCCCC` bevel fills. Keep the active
  geometry (18x34 canvas, 6px side/bottom border, 22px top border, 6x6 centre). Recompress
  `decoration.svgz` (`gzip -9 -n`) so `test_svgz_is_the_compressed_svg` still passes.
- Reword the `decoration.svg` header comment: name `desktop_fandom.png` (2 image px per logical
  px) as the inactive anchor and `systeminfo_betawiki.png` as lossless corroboration, state the
  flat `#DDDDDD` field with the 1px `#555555` outer and inner outlines, and delete the "the
  reference set has no inactive window" clause.
- `tests/support/aurorae_fixtures.py`: add `INACTIVE_REFERENCE` (`desktop_fandom.png`, with a row
  bound covering y=900), `INACTIVE_FRAME_GREY = "#DDDDDD"` and `INACTIVE_OUTLINE = "#555555"`;
  keep `INACTIVE_GREY = "#CCCCCC"` for the button boxes. Load `INACTIVE_REFERENCE` in
  `ReferenceImageCase.setUpClass` (skip when unmaterialized, like `REFERENCE`) and add an
  `inactive_pixel(x, y)` accessor.
- `tests/test_aurorae_frame.py`: replace `_assert_flattened_inactive_tile` and its callers with
  reference-derived checks; add `TestDecorationSvg.test_inactive_frame_matches_reference`, which
  derives each inactive tile from its active tile (pinned to the reference) with the `#000000`
  outlines recolored `#555555` and every other fill flattened to `#DDDDDD`, so no `#FFFFFF`,
  `#777777`, `#999999` or `#CCCCCC` pixel survives, and cross-checks the field and outline
  against `inactive_pixel(300, 75)`, `(1000, 130)`, `(1500, 80)`, `(300, 880)` (`#DDDDDD`) and
  `(300, 57)`, `(25, 75)` (`#555555`). Reword the module docstring and the inactive tests so they
  name the reference instead of claiming none exists.
- `theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`
  and `tests/test_aurorae_buttons.py`: replace each "the reference set has no inactive window"
  clause with the accurate one — the reference's inactive windows draw no close/collapse boxes in
  their title bars, so the greyed inactive box stays KDE-required. No art change; `INACTIVE_GREY`
  and the button tests are unchanged.
- `macos8.6-screenshots/sources.txt`: extend the `desktop_fandom.png` note to record that it
  grounds the inactive window frame (the flat `#DDDDDD` title bar and 1px `#555555` outline of its
  four unfocused windows).
- `docs/invariants.md`: update the aurorae frame row to name the inactive reference, and the
  title-bar-box row so its inactive grey is recorded as KDE-required rather than re-derived.

**Files touched.** `theme/aurorae/themes/org.macos8.desktop/decoration.svg` (+ `.svgz`),
`theme/aurorae/themes/org.macos8.desktop/close.svg`, `maximize.svg`, `restore.svg`, `shade.svg`,
`tests/support/aurorae_fixtures.py`, `tests/test_aurorae_frame.py`,
`tests/test_aurorae_buttons.py`, `macos8.6-screenshots/sources.txt`, `docs/invariants.md`.

**Acceptance criteria.**
- The `decoration-inactive-*` tiles paint only `#DDDDDD` and `#555555`, with `#555555` on the
  outer edge; no `#FFFFFF`, `#777777`, `#999999` or `#CCCCCC` pixel remains in them.
- `python3 tools/sample.py macos8.6-screenshots/desktop_fandom.png 300 75` (and `1000 130`,
  `1500 80`, `300 880`) prints `221,221,221 #DDDDDD`; `... 300 57` and `... 25 75` print
  `85,85,85 #555555`.
- `TestDecorationSvg.test_inactive_frame_matches_reference` passes when `desktop_fandom.png` is
  materialized and skips (not fails) when it is not, through the `skip_unless_materialized` path.
- No Aurorae SVG header or Aurorae test docstring still claims the reference set has no inactive
  window.
- `decoration.svgz` decompresses to the edited `decoration.svg`.
- `make check` is green.

### Correct the desktop theme's false "no menu-open / no combo-box" reference claims (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** Three desktop-theme SVG header comments justify a palette-only value by claiming the
reference set shows no such surface, but the set does show it, so the stated reason is false and
the real reason the value has no per-pixel sample is hidden.

- `theme/desktoptheme/org.macos8.desktop/widgets/viewitem.svg` says "the reference set has no
  open-menu screenshot, so the menu-item highlight has no per-pixel menu sample". The set's open
  Apple menu is `macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the image the
  `widgets/background.svg` plan already sampled its grey menu body from. That menu shows no
  highlighted item (a scan of the image finds no `#CCCCFF` pixel, the highlight fill), so the
  conclusion holds but the stated reason is wrong.
- `theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg` repeats the claim as "the
  reference set has no menu-open screenshot". The same open Apple menu is a menu-open screenshot;
  its open title is the Apple-logo kicker (a text title is never shown open), so the pressed
  text-title fill has no per-pixel sample for that different reason.
- `theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg` says "no reference screenshot
  shows a combo box or menu button". The set does: the beta `macos8.6-screenshots/
  systeminfo_betawiki.png` Get Info window's "General Information" and "None" popups, and the
  JPEG `macos8.6-screenshots/opendialog_macrumors86.jpg` Open dialog's "ROM-new" popup. Their Mac
  OS indicator is a double (up+down) arrow, not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle is still a KDE-required shape — but the
  comment must give that reason instead of the false one.

Correct all three comments to state what the reference actually shows, and pin the corrected
provenance so the false claim cannot return.

**Approach.**
- `viewitem.svg`: replace the "the reference set has no open-menu screenshot, so the menu-item
  highlight has no per-pixel menu sample" clause with one naming the reference: the reference
  set's open Apple menu (`desktop_archiveorg8.6hd.png`) shows no highlighted item, so the
  menu-item highlight has no per-pixel sample. Keep the `[Colors:Selection]
  BackgroundNormal=204,204,255` token sentence and the `normal`-slices paragraph unchanged.
- `menubaritem.svg`: replace "the reference set has no menu-open screenshot, so the pressed fill
  has no per-pixel menu sample" with: the reference set's open Apple menu
  (`desktop_archiveorg8.6hd.png`) opens the Apple-logo kicker's title, not a text title, so the
  pressed text-title fill has no per-pixel sample. Keep the `[Colors:Selection]` token sentence
  and the side-padding grounding paragraph unchanged.
- `arrows.svg`: replace the "Provenance: no reference screenshot shows a combo box or menu
  button" sentence with one naming the beta Get Info's and the Open dialog's popup buttons and
  stating that their double-arrow indicator is not the single `down-arrow` triangle
  `PlasmaComponents.ComboBox` draws, so the triangle stays a KDE-required shape and the fill
  reuses the grounded Platinum black (`#000000`) `widgets/checkmarks.svg` pins. Keep the
  literal-attribute sentence.
- `tests/test_desktoptheme_provenance.py` (new): a `TestProvenance` case reading each SVG's
  leading XML comment with a small `header_comment(path)` helper (the SVGs open with a single
  `<!-- ... -->` after the XML declaration) and, per `(path, required, forbidden)` case, asserting
  the comment contains the reference filename it must cite and does not contain the false phrase.
  Import the three paths from `support.desktoptheme_paths` (`VIEWITEM_SVG`, `MENUBARITEM_SVG`,
  `ARROWS_SVG`). Cases:
  - `viewitem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no open-menu screenshot`.
  - `menubaritem.svg`: requires `desktop_archiveorg8.6hd.png`; forbids `no menu-open screenshot`.
  - `arrows.svg`: requires `systeminfo_betawiki.png`; forbids `no reference screenshot shows a
    combo box`.
- `docs/invariants.md`: add a `desktoptheme` row `| The `viewitem.svg`, `menubaritem.svg` and
  `arrows.svg` provenance comments name the reference screenshot their claim rests on and do not
  claim the set shows no such surface. | tests/test_desktoptheme_provenance.py::TestProvenance |
  none |`.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/viewitem.svg`,
`theme/desktoptheme/org.macos8.desktop/widgets/menubaritem.svg`,
`theme/desktoptheme/org.macos8.desktop/widgets/arrows.svg`,
`tests/test_desktoptheme_provenance.py` (new), `docs/invariants.md`.

**Acceptance criteria.**
- `viewitem.svg`'s and `menubaritem.svg`'s headers name `desktop_archiveorg8.6hd.png` and no
  longer contain "no open-menu screenshot" / "no menu-open screenshot" respectively;
  `arrows.svg`'s header names `systeminfo_betawiki.png` and no longer contains "no reference
  screenshot shows a combo box".
- `tests/test_desktoptheme_provenance.py::TestProvenance` passes, and fails when any of the three
  comments is reverted to its false phrase or loses its reference filename.
- The new `docs/invariants.md` row resolves through `tests/invariants.py` (its named test case
  exists), and no existing widget assertion changes: the three SVGs' parsed elements and fills are
  untouched.
- `make check` is green.

### Correct the `[Colors:Selection]` anchor's provenance: the reference region is the Setup Assistant's Introduction banner, not a list selection (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `tests/test_colorscheme_reference.py::TestReferenceAnchors.test_selection_background`
grounds `[Colors:Selection] BackgroundNormal=204,204,255` in `firstboot_betawiki.png`, but its
comment calls the sampled region "the Setup Assistant's list selection ... a full-width
highlighted row". The region is the Setup Assistant window's "Introduction" title banner: a flat
`#CCCCFF` band spanning roughly x=31..428, y=61..85, under the `#000000` rule at y=59 and the
`#FFFFFF` highlight at y=60 (verified with `tools/sample.py`). `tests/support/platinum_palette.py`
compounds the error, calling the selection fill one of the "KDE-required `[Colors:Tooltip]` and
`[Colors:Selection]` roles no screenshot shows" — a claim `test_selection_background` itself
contradicts. Correct both to state what the reference shows, and widen the anchor so it pins the
banner's flat extent rather than a single pixel.

**Approach.**
- `tests/test_colorscheme_reference.py`:
  - Reword the `REFERENCE_FIRSTBOOT` comment: the sampled region is the Setup Assistant's flat
    `#CCCCFF` "Introduction" banner, not a list selection, and note that it is the reference
    set's flat `#CCCCFF` region.
  - In `test_selection_background`, reword the comment and assert the fill is flat across the
    banner by calling
    `assert_anchor_at("Colors:Selection", "BackgroundNormal", ..., path=REFERENCE_FIRSTBOOT)` at
    `(100, 63)`, `(200, 63)`, `(300, 63)` and `(200, 80)` (all inside the band, clear of its
    text), and one call for the same point with key `BackgroundAlternate`, which the scheme sets
    to the same `204,204,255`.
  - Reword the class docstring's "``firstboot_betawiki.png`` for the selection anchor" clause to
    name the Introduction banner.
- `tests/support/platinum_palette.py`: rewrite the module docstring so the selection fill is
  grounded by `test_colorscheme_reference.TestReferenceAnchors.test_selection_background` in the
  Setup Assistant's Introduction banner (`firstboot_betawiki.png`) and only the tooltip face is
  the KDE-required role no screenshot shows; update the `SELECTION` comment to name that
  reference.
- `macos8.6-screenshots/sources.txt`: extend the `firstboot_betawiki.png` entry with a grounding
  note (the Setup Assistant's Introduction banner is the flat `#CCCCFF` band at y=61..85 that
  grounds `[Colors:Selection] BackgroundNormal`), mirroring the `setup_emaculation.png` entry.

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/support/platinum_palette.py`,
`macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 100 63` (and `300 63`,
  `200 80`) prints `204,204,255 #CCCCFF`, and
  `python3 tools/sample.py macos8.6-screenshots/firstboot_betawiki.png 200 59` prints
  `0,0,0 #000000`.
- `TestReferenceAnchors.test_selection_background` asserts the scheme's `BackgroundNormal` and
  `BackgroundAlternate` at all four banner points and still skips (not fails) when the Git-LFS
  reference is not materialized, through the existing `pixel`/`skip_unless_materialized` path.
- `tests/test_colorscheme_reference.py` and `tests/support/platinum_palette.py` no longer call
  the sampled region a "list selection" or claim `[Colors:Selection]` is a role "no screenshot
  shows".
- `macos8.6-screenshots/sources.txt`'s `firstboot_betawiki.png` entry names the selection anchor
  and `python3 tools/check_references.py` still accepts the record.
- `make check` is green.

### Ground the `[Colors:View] BackgroundAlternate` scroll-bar trough anchor in `setup_emaculation.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** The color scheme's `[Colors:View] BackgroundAlternate=238,238,238` is the flat
`#EEEEEE` trough that `theme/desktoptheme/org.macos8.desktop/widgets/scrollbar.svg`,
`slider.svg` and `switch.svg` paint. It is the trough that `tests/support/platinum_palette.py`
records as "pinned only by the widget tests that draw it", unlike the face, view, chrome and
selection anchors that `tests/test_colorscheme_reference.py::TestReferenceAnchors` re-derives from
a retail screenshot. The retail installer window in `setup_emaculation.png` shows the trough, so
add an anchor there and tie the scroll bar's own slices to the same pixels.

**Approach.**
- `tests/test_colorscheme_reference.py`: add
  `REFERENCE_SCROLLBAR = os.path.join(ROOT, "macos8.6-screenshots", "setup_emaculation.png")`
  and `SCROLLBAR_ANCHOR_ROWS = 471` (the anchor is at y=470, so the bound must cover row 470),
  load it in `TestReferenceAnchors.setUpClass` next to `REFERENCE_DESKTOP` and
  `REFERENCE_FIRSTBOOT`, and add `test_view_background_alternate` calling
  `assert_anchor_at("Colors:View", "BackgroundAlternate", 200, 470, path=REFERENCE_SCROLLBAR)`.
  The pixel is inside the installer CD window's horizontal scroll bar: the 16px band has a
  `#000000` outline at y=462 and y=477 with a flat `#EEEEEE` trough between them, so (200, 470)
  is clear of both outlines and of the arrow boxes.
- `tests/test_desktoptheme_scrollbar.py`: add a `TestScrollbarReference(ReferenceScreenshotMixin)`
  class, following `tests/test_desktoptheme_line.py::TestLineReference`, with
  `REFERENCE = REFERENCE_SCROLLBAR` (import the path from `support.theme_install`/`ROOT` and
  `TROUGH`/`BLACK` from `support.platinum_palette`). Its `test_trough_matches_reference` asserts
  `self.pixel(200, 470)` is `TROUGH`, `self.pixel(200, 462)` and `self.pixel(200, 477)` are
  `BLACK`, and the trough is flat at `(50, 470)`, `(300, 470)` and `(400, 470)`, so the
  `background-vertical`/`background-horizontal` slices' pinned fills are tied to the screenshot
  and not only to `platinum_palette`.
- `tests/support/platinum_palette.py`: reword the module docstring, which says the trough "is
  pinned only by the widget tests that draw it", to name the new anchor and reference test.
- `macos8.6-screenshots/sources.txt`: extend the `setup_emaculation.png` note to record that it
  grounds the `[Colors:View] BackgroundAlternate` trough anchor (the flat scroll-bar band at
  y=462..477).

**Files touched.** `tests/test_colorscheme_reference.py`, `tests/test_desktoptheme_scrollbar.py`,
`tests/support/platinum_palette.py`, `macos8.6-screenshots/sources.txt`.

**Acceptance criteria.**
- `python3 tools/sample.py macos8.6-screenshots/setup_emaculation.png 200 470` prints
  `238,238,238 #EEEEEE`, and the outlines at `(200, 462)` and `(200, 477)` are `#000000`.
- `TestReferenceAnchors.test_view_background_alternate` passes when the Git-LFS reference is
  materialized and skips (not fails) when it is not, through the existing
  `pixel`/`skip_unless_materialized` path; `SCROLLBAR_ANCHOR_ROWS` covers row 470 so the read
  stays in bounds.
- `TestScrollbarReference.test_trough_matches_reference` passes/skips the same way and pins the
  trough fill and both outlines.
- `tests/support/platinum_palette.py` no longer claims the trough is ungrounded.
- `make check` is green.

### Prove the beta `aboutsystem_betawiki.png` window chrome matches the retail `systemprofiler_betawiki.png` (planned 2026-10-19 by the plan role) — done 2026-10-19

**Goal.** `macos8.6-screenshots/sources.txt` labels `aboutsystem_betawiki.png` "Mac OS 8.6b2c4LB
beta", and the README's reference policy says beta builds "must not be used as retail
reference" — yet `tests/test_render_surface.py` (the render fidelity gate) and
`tests/support/aurorae_fixtures.py` (the Aurorae decoration tests) read that file. The retail
`systemprofiler_betawiki.png` shows the same window chrome, and this run verified the title-bar
strip, the left and right frame borders, and the close and collapse boxes are byte-identical
between the two (0 differing pixels over 1760, 1272, 1272, 169 and 169 pixels). Add a test that
pins that equality, so the beta is an evidence-backed proxy instead of an unrecorded policy
exception, and record the exception in the docs.

**Approach.**
- New `tests/test_aurorae_reference_equivalence.py`: a `unittest.TestCase` that loads both PNGs
  with `tools.png.read_png`/`pixel_at` and asserts these five regions are pixel-for-pixel equal,
  skipping when either Git-LFS image is not materialized (use
  `support.reference_image.skip_unless_materialized`, the way `ReferenceImageCase` does):
  - title bar: aboutsystem `(30, 25, 80, 22)` vs profiler `(232, 22, 80, 22)`;
  - left border: `(7, 47, 6, 212)` vs `(209, 44, 6, 212)`;
  - right border: `(354, 47, 6, 212)` vs `(808, 44, 6, 212)`;
  - close box: `(11, 29, 13, 13)` vs `(213, 26, 13, 13)`;
  - collapse box: `(343, 29, 13, 13)` vs `(797, 26, 13, 13)`.
  Each region is a window-relative crop (`aboutsystem`'s window origin is `(7, 25)`, the
  profiler's `(209, 22)`, a `(+202, -3)` shift), so the test also records why those two origins
  differ.
- `docs/invariants.md`: add a row to the aurorae section naming the new test as the one that
  pins the beta reference's chrome against the retail screenshot.
- `macos8.6-screenshots/sources.txt` and the README "Reference screenshots" section: record that
  `aboutsystem_betawiki.png` is a beta used as a window-chrome proxy, backed by this test, and
  that the render gate's bottom-border crop (aboutsystem `(13, 419, 308, 6)`) stays on the beta
  because the System Profiler window's bottom differs (its sunken content field and bottom
  scrollbar) and the set has no other lossless retail window-bottom crop.

**Files touched.** `tests/test_aurorae_reference_equivalence.py` (new), `docs/invariants.md`,
`macos8.6-screenshots/sources.txt`, `README.md`.

**Acceptance criteria.**
- The new test passes with both LFS images materialized and skips cleanly when they are not.
- A one-pixel change in any of the five regions of either image makes the test fail (prove it by
  mutating a copy in the test itself, never the reference file).
- `docs/invariants.md`'s aurorae section names the test, and `tests/test_invariants.py` stays
  green.
- `make check` passes.

### Mac OS 8.6 Platinum text field: draw the sunken bevel outside the black outline in `widgets/lineedit.svg` (planned 2026-10-18 by the plan role) — done 2026-10-19

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg` paints the sunken
white field `PlasmaComponents.TextField`/`TextArea`/`SpinBox` and the editable `ComboBox` draw.
It puts the 1px `#000000` outline on the *outer* edge and the `#999999`/`#FFFFFF` bevel *inside*
it. The retail 8.6 reference draws the opposite: the bevel is *outside* the `#000000` outline,
which sits next to the white face. Correct the artwork so a text field matches the reference,
and ground it in reference pixels (the file cites none today). Independent of every other entry:
one artwork file plus its test and a shared assertion convention.

**Reference.** `macos8.6-screenshots/firstboot_betawiki.png` (retail Mac OS 8.6 Setup
Assistant, 1024x768 lossless PNG; `sources.txt` labels it "Mac OS 8.6"). Its body text field:
left border at (28, 95)=`#999999`, (29, 95)=`#000000`, (30, 95)=`#FFFFFF` (face); right border at
(429, 150)=`#FFFFFF` (face), (430, 150)=`#000000`, (431, 150)=`#FFFFFF`; bottom border at
(100, 349)=`#FFFFFF` (face), (100, 350)=`#000000`, (100, 351)=`#FFFFFF`. So the outer 1px ring is
the bevel (`#999999` top/left, `#FFFFFF` bottom/right), the inner 1px ring is `#000000`, and the
face is `#FFFFFF`. `systeminfo_betawiki.png` (8.6a3c2 alpha) and `aboutsystem_betawiki.png`
(8.6b2c4L8 beta) show the same order but are not retail and must not be cited.

**Approach.**
- `widgets/lineedit.svg`: rewrite the eight `base-*` tiles as the ring-swap of the current
  geometry -- the outer 1px ring becomes the bevel (`#999999` top/left, `#FFFFFF` bottom/right),
  the inner 1px ring becomes `#000000`, the face stays `#FFFFFF`. Edges: `base-top` rows
  `#999999`/`#000000`/`#FFFFFF`; `base-bottom` rows `#FFFFFF` (face)/`#000000`/`#FFFFFF` (outer);
  `base-left` columns `#999999`/`#000000`/`#FFFFFF`; `base-right` columns `#FFFFFF`
  (face)/`#000000`/`#FFFFFF` (outer). Corners (row-major 3x3): `base-topleft`
  `#999999 #999999 #999999 / #999999 #000000 #000000 / #999999 #000000 #FFFFFF`; `base-topright`
  `#999999 #999999 #999999 / #000000 #000000 #FFFFFF / #FFFFFF #000000 #FFFFFF`;
  `base-bottomleft` `#999999 #000000 #FFFFFF / #999999 #000000 #000000 / #999999 #FFFFFF #FFFFFF`;
  `base-bottomright` `#FFFFFF #000000 #FFFFFF / #000000 #000000 #FFFFFF / #FFFFFF #FFFFFF #FFFFFF`.
  Keep the 12x12 canvas, the 3px border around the 6px centre, and every hint id.
- Rewrite the header: the sunken bevel sits outside the `#000000` outline, sampled from
  `firstboot_betawiki.png` at the pixels above; drop "the frame's sunken bevel inside it".
- `tests/svg_assertions/faces.py`: add a `"sunken-outside"` bevel to `_require_known_bevel`, to
  `face_edge_bands` (`("#999999", "#000000", face)` outward, `(face, "#000000", "#FFFFFF")`
  mirrored) and to `face_corners` via a new `sunken_outside_face_corners(face)` table holding the
  four corners above. Leave the existing `"sunken"` convention for `frame.svg`.
- `tests/test_desktoptheme_lineedit.py`: switch `test_lineedit_edge_bevels_are_sunken` and
  `test_lineedit_corner_bevels_turn_the_corner` to `"sunken-outside"`; add
  `TestLineEditReference(ReferenceScreenshotMixin, unittest.TestCase)` with `REFERENCE` =
  `firstboot_betawiki.png`, `MAX_ROWS = 352`, asserting `hex_colour(self.pixel(x, y))` equals
  `#999999`/`#000000`/`#FFFFFF` for the three border runs above.
- `tests/test_svg_assertions_faces.py`: add the new convention's edge and corner expectations
  beside the existing sunken ones.
- `docs/invariants.md`: the `widgets/lineedit.svg` row's guarantee and its `none` provenance
  exception are unchanged.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/lineedit.svg`,
`tests/test_desktoptheme_lineedit.py`, `tests/svg_assertions/faces.py`,
`tests/svg_assertions/__init__.py` (re-export the new corner table),
`tests/svg_assertions/pixels.py` (docstring only: `assert_face_bevel`'s bevel vocabulary), and
`tests/test_svg_assertions_faces.py`.

**Acceptance criteria.**
- The `base-*` tiles' outer ring is `#999999` (top/left) / `#FFFFFF` (bottom/right) and the inner
  ring `#000000`, with the `#FFFFFF` face; the parsed `fill` set is still
  {`#FFFFFF`, `#999999`, `#000000`}.
- A reference test re-derives the field's left, right and bottom border runs from
  `firstboot_betawiki.png` and skips when the Git LFS image is not materialized.
- The header names `firstboot_betawiki.png` and the sampled pixels and no longer says the bevel is
  inside the outline.
- `frame.svg`'s sunken test and artwork are unchanged.
- `make check` is green.

### Mac OS 8.6 Platinum dialog body: ground `dialogs/background.svg`'s face in the lossless window body (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg` paints the raised
Platinum body that a `PlasmaCore.Dialog` and a `PlasmaCore.AppletPopup` resolve to (the applet and
clock popups). Its header comment says the reference set shows the same grey window bodies but
they are dithered 8-bit captures, so "no single pixel is screenshot-anchored: the values are
palette-derived and recorded as such". Two retail 8.6 references do show an undithered `#DDDDDD`
window body, so the face can be pinned to a pixel and the palette-derived claim dropped.
Independent of every other entry: one reference test class plus one comment rewrite, touching no
artwork.

**Reference.** `macos8.6-screenshots/desktop_archiveorg8.6hd.png` (800x600, lossless PNG): the
About This Computer window body below its title bar, (583..586, 95..100) a solid 4x6 `#DDDDDD`
block ((584, 97) is `#DDDDDD`). Cross-check `macos8.6-screenshots/desktop_fandom.png` (2x,
WebP re-encoded but flat faces exact): the same window body at (1750..1757, 1100..1105) is a solid
8x6 `#DDDDDD` block and (1792, 1126) is `#DDDDDD`. `about_betawiki.png` and
`setup_emaculation.png` are dithered and must not be sampled. `test_colorscheme_reference`
already anchors `[Colors:Window] BackgroundNormal` at (400, 5) of `desktop_archiveorg8.6hd.png`
-- that pixel is the menu bar; this plan anchors the *window body* at a second location, which is
the pixel the header comment says does not exist.

**Approach.**
- `tests/test_desktoptheme_dialog.py`: add `import os`, `from support.platinum_palette import FACE,
  hex_colour`, `from support.reference_image import ReferenceScreenshotMixin` and
  `from support.repo_root import ROOT` (the import pattern `tests/test_desktoptheme_tabbar.py`
  uses); add `TestDialogBackgroundReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE = os.path.join(ROOT, "macos8.6-screenshots", "desktop_archiveorg8.6hd.png")` and
  `MAX_ROWS = 101` (the deepest sampled row is 100), asserting
  `hex_colour(self.pixel(x, y)) == FACE` for the 4x6 block. The mixin skips the class when the Git
  LFS image is not materialized. Leave `TestDialogBackground(RaisedFaceCase, unittest.TestCase)`
  unchanged.
- `theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`: rewrite the provenance
  paragraph -- the `#DDDDDD` face is the window body sampled from `desktop_archiveorg8.6hd.png` at
  (584, 97) and cross-checked at (1792, 1126) of `desktop_fandom.png`; the 1px `#000000` outline
  and the `#FFFFFF`/`#999999` bevel are the shared raised-face rule (the reference window body
  itself is flat, so no window-body pixel grounds them); delete "no single pixel is
  screenshot-anchored: the values are palette-derived and recorded as such".
- `docs/invariants.md`: the `dialogs/background.svg` row's guarantee and its `none` provenance
  exception are unchanged, now that the face is reference-sampled.

**Files touched.** `tests/test_desktoptheme_dialog.py`,
`theme/desktoptheme/org.macos8.desktop/dialogs/background.svg`.

**Acceptance criteria.**
- `TestDialogBackgroundReference` re-derives `#DDDDDD` from `desktop_archiveorg8.6hd.png`'s window
  body and skips when the Git LFS image is not materialized.
- `dialogs/background.svg`'s parsed `fill` set is unchanged (the Platinum four `#DDDDDD`,
  `#000000`, `#FFFFFF`, `#999999`; the hints are painted with `style` and so are not in the parsed
  `fill` set), so `RaisedFaceCase`'s `test_hint_geometry`, `test_frame_bevel` and `test_colours`
  still pass.
- The header comment names `desktop_archiveorg8.6hd.png` (and the `desktop_fandom.png`
  cross-check) with the sampled pixels and no longer calls the face palette-derived or unanchored.
- `make check` is green.

### Mac OS 8.6 Platinum progress bar: paint the reference's vertical gradient in `bar_meter_horizontal.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/bar_meter_horizontal.svg` paints its
`bar-active` fill as a flat `#9B9BEA` face with a `#9A9A9A`/`#7878D1` bevel, sampled from the
low-resolution boot thumbnail `boot2_betawiki.png`. Mac OS 8.6's progress-bar fill is a vertical
gradient — dark at the top and bottom, `#CBCCFF` at the centre — and the lossless 2x reference
`macos8.6-screenshots/desktop_fandom.png` resolves all ten rows of it. Paint that gradient so the
Plasma progress bar matches the reference instead of a flat fill.

**Reference.** `desktop_fandom.png` (2 image px per logical px), the "Mac OS 30.4 MB" memory meter
of the About This Computer window. The fill spans x=1458..1817, y=1230..1249. Its interior column
x=1600 has, at image rows 1230, 1232, 1234, 1236, 1238, 1240, 1242, 1244, 1246, 1248:
`#515372`, `#666799`, `#8484BB`, `#B0B0EB`, `#CBCCFF`, `#B2B2E8`, `#8586BC`, `#66679B`, `#50527F`,
`#24244D`. The fill's 1px left edge column is `#68688D` ((1458, 1238)) and its 1px right edge
column `#50527F` ((1816, 1238)). The boot2 fill rows at x=102, y=99..102 (`#7D7D9A`, `#9B9BEA`,
`#7878D1`, `#83839D`) are the same gradient downscaled, so the two references agree.

**Approach.**
- `widgets/bar_meter_horizontal.svg`: leave `bar-inactive` (the track) unchanged. Replace the
  `bar-active` flat face and its `#9A9A9A`/`#7878D1` bevel with the ten sampled rows: in the
  `bar-active-top` (rows 0-2), `bar-active-center` (rows 3-6) and `bar-active-bottom` (rows 7-9)
  tiles one 4x1 rect per row carrying that row's colour, and in each of the four corner tiles and
  the `bar-active-left`/`bar-active-right` tiles the same per-row rects (3px wide) plus one 1x3 or
  1x4 rect on the outer column carrying `#68688D` (left) or `#50527F` (right). Keep the 3px border
  around a 4px centre tile, the 10x10 canvas and the `hint-bar-size` 10x10 hint.
- Rewrite the header comment's fill paragraph: the fill is the reference's vertical gradient
  sampled from `desktop_fandom.png` at the ten pixels above, with the two edge columns sampled at
  (1458, 1238) and (1816, 1238); the boot2 pixels are the downscaled evidence. Record the
  deviations: the reference's 1px `#000000` outline and its ~12px total height are not drawn (the
  bar keeps the 10px canvas), and the edge columns are painted flat rather than row by row.
- `tests/test_desktoptheme_progressbar.py`: replace `FILL_FACE`/`FILL_LIGHT` with a ten-colour
  `FILL_ROWS` table and the two edge constants; `_assert_bar_pixels` builds the top/centre/bottom
  bands and the corner expectations from the table; `test_progressbar_colours` expects the parsed
  fill set of the track's three colours plus the eleven distinct fill colours. Keep the existing
  `TestProgressBarReference` (the boot2 track) for the three track colours and drop its two fill
  pixels; add a second reference class whose `REFERENCE` is `desktop_fandom.png`,
  `MAX_ROWS = 1250`, sampling the ten interior rows and the two edge columns and comparing each to
  the artwork's own parsed fill.
- `README.md`: the `widgets/bar_meter_horizontal.svg` sentence says a lavender-to-white vertical
  gradient fill instead of "a lavender fill".
- `docs/invariants.md`: the `widgets/bar_meter_horizontal.svg` guarantee ("draws the Platinum
  progress bar") is unchanged; no provenance exception is needed because every fill colour is
  reference-sampled.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/bar_meter_horizontal.svg`,
`tests/test_desktoptheme_progressbar.py`, `README.md`.

**Acceptance criteria.**
- The `bar-active` fill's ten rows are exactly the ten sampled `desktop_fandom.png` colours and the
  left/right edge columns are `#68688D`/`#50527F`, asserted slice by slice.
- A reference test re-derives all ten row colours and the two edge colours from
  `desktop_fandom.png` and skips when the Git LFS image is not materialized.
- `bar-inactive`'s track pixels and the 10x10 nine-slice contract (`hint-tile-center`,
  `hint-bar-size`) are unchanged.
- The header comment names `desktop_fandom.png` and the sampled pixels and no longer calls the
  fill a flat `#9B9BEA` face.
- `make check` is green.

### Mac OS 8.6 Platinum tab face: ground `widgets/tabbar.svg` in the System Profiler tabs (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg` paints every tab face
`#DDDDDD`, the same grey as the menu bar and the dialog body, so a Plasma tab (`TabBar`,
`TabButton`, the kickoff footer, the system-tray current-item and panel expanded applets) reads
as a bare outline on an identical background. The high-resolution lossless reference
`macos8.6-screenshots/desktop_fandom.png` (English retail 8.6, the "Apple System Profiler"
window) shows the Platinum tab face is one grey darker, `#CCCCCC`, with a `#DDDDDD` highlight
inside the `#000000` outline rather than the `#FFFFFF` the artwork paints. The SVG's provenance
comment claims "No screenshot reference exists for tabs", which this reference contradicts.

**Grounding.** In `desktop_fandom.png` the four System Profiler tabs run y=124..157 (a 2x
upscale of a 1280x721 screen, so 2 image pixels per logical pixel). Each tab's interior is
uniformly `#CCCCCC`: the 12x5 rectangles x=2056..2068 y=149..154 (inside "Applications"),
x=2200..2212 y=149..154 ("System Folders") and x=1920..1932 y=149..154 ("Extensions") are each
60/60 `#CCCCCC` (`tools/sample.py`). The 1px band just inside the top black outline is
`#DDDDDD` (rows 128..129 at x=2064), the outline `#000000` (rows 124..125), the tab-bar
background between tabs `#DDDDDD` (221,221,221). Only the solid face, highlight and outline
colours are taken from the reference; the 2x scale leaves the exact 1px bevel placement
unresolved, so the bevel keeps its current black/highlight/face geometry.

**Approach.**
- `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`: in all four `*-active-tab`
  prefixes change the face fill `#DDDDDD` to `#CCCCCC` and the raised-bevel highlight
  `#FFFFFF` to `#DDDDDD`; keep the `#000000` outline, the `#999999` shadow and the face-only
  open edge. Update the header comment to name `desktop_fandom.png` and the sampled rectangles
  and to drop the "No screenshot reference exists for tabs" claim.
- `tests/test_desktoptheme_tabbar.py`: set `FACE = "#CCCCCC"`, add `HIGHLIGHT = "#DDDDDD"`,
  and build `TOP_LEFT_BAND`/`BOTTOM_RIGHT_BAND` and the two fully-raised corners in
  `tab_corners` from `HIGHLIGHT`/`FACE` (the shared `svg_assertions.face_corners` table is
  hard-coded for the `#DDDDDD`/`#FFFFFF` button face, so the tab gets its own raised corner
  table, as the file's `band_rows`/`band_columns` helpers already do for the mixed corners).
  Replace `test_tabbar_colours`'s `assert_fill_palette(self, self.tree)` with an explicit
  `attribute_values(self.tree, "fill") == {"#000000", "#CCCCCC", "#DDDDDD", "#999999"}`,
  and update `test_tabbar_palette`'s expected raw strings to `#CCCCCC`, `#DDDDDD`, `#999999`,
  `#000000`. Add `TestTabBarReference(ReferenceScreenshotMixin, unittest.TestCase)` with
  `REFERENCE` = `desktop_fandom.png` and `MAX_ROWS = 160`, asserting `hex_colour(self.pixel(x, y))`
  is `FACE` for each of the three rectangles above.
- `tests/support/reference_image.py`: give `ReferenceScreenshotMixin` a `MAX_ROWS = None` class
  attribute and pass `max_rows=cls.MAX_ROWS` to `read_reference` in `setUpClass`, so the
  2560x1442 reference decodes only its first 160 rows (0.4s) instead of all of it (3.4s).
- `docs/invariants.md`: the desktoptheme row already names
  `tests/test_desktoptheme_tabbar.py::TestTabBar`; its guarantee ("draws the Platinum tab bar")
  is unchanged.

**Acceptance criteria.**
- Every `*-active-tab` centre and the face part of every slice is `#CCCCCC`, and every
  raised-bevel highlight is `#DDDDDD`; `test_tabbar_centres_are_the_face`,
  `test_tabbar_closed_edges_are_raised` and `test_tabbar_corners` pass.
- The new reference test re-derives `#CCCCCC` from the three `desktop_fandom.png` rectangles and
  passes; a face painted `#DDDDDD` fails it. The test skips, not fails, when the reference is
  not materialized (`skip_unless_materialized`).
- `tabbar.svg`'s comment no longer claims no screenshot reference exists and names the
  reference and the rectangles.
- `make check` exits 0.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/tabbar.svg`,
`tests/test_desktoptheme_tabbar.py`, `tests/support/reference_image.py`.

**Recorded deviation.** The reference tab is a trapezoid whose sides slant outward over the
full tab height; a KSvg nine-slice draws a fixed-corner rectangle, so the shape stays
rectangular. The Kvantum `tab` element (`theme/kvantum/org.macos8.desktop/org.macos8.desktop.svg`)
keeps its own `#DDDDDD`/`#FFFFFF` raised face: it is a separate Qt-widget surface, not part of
this desktop-theme change.

### Mac OS 8.6 Platinum translucent applet background: ship `widgets/translucentbackground.svg` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `BasicAppletContainer.qml` — the Plasma applet container the desktop containment uses for
applets placed on the desktop — picks its background from the applet's
`effectiveBackgroundHints`: the `TranslucentBackground` bit resolves to
`imagePath: "widgets/translucentbackground"`. The desktop theme ships no such file, so KSvg falls
back to the default theme's Breeze `translucentbackground.svgz`, a rounded translucent rectangle
that clashes with Platinum. Ship the Platinum body so those applet containers are Platinum too.

**Grounding.** `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/private/containmentlayoutmanager/BasicAppletContainer.qml`
chooses the path in `background.imagePath`: `effectiveBackgroundHints & TranslucentBackground` →
`widgets/translucentbackground`, else `& StandardBackground` → `widgets/background` (already
shipped), else `""`. The same item sets `prefix: blurEnabled ? "blurred" : ""`; `blurEnabled`
requires the `StandardBackground` bit, so a translucent-hint container reads the **unprefixed**
elements. The installed applets that set the bit are those with `PlasmaCore.Types.DefaultBackground`
(`= StandardBackground | TranslucentBackground`) — `org.kde.plasma.weather`, `org.kde.plasma.comic`
and `org.kde.plasma.systemmonitor` each set `Plasmoid.backgroundHints: PlasmaCore.Types.DefaultBackground
| PlasmaCore.Types.ConfigurableBackground`, and `BasicAppletContainer` tests `TranslucentBackground`
first, so they take the translucent path. Mac OS 8.6 has no translucent applet surface: no reference
screenshot shows one and every Platinum body is opaque, so the KDE-required translucent-hint surface
takes the same opaque Platinum body as the standard hint. No new palette value: the file is a
byte-identical copy of `widgets/background.svg` (the Platinum body the standard hint already draws),
exactly as `solid/widgets/tooltip.svg` copies `widgets/tooltip.svg`.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/widgets/translucentbackground.svg`, byte-identical to
`theme/desktoptheme/org.macos8.desktop/widgets/background.svg` (no header change, so the copy test
compares bytes).
- `tests/support/desktoptheme_paths.py`: add `TRANSLUCENT_BACKGROUND_SVG = os.path.join(PACKAGE,
"widgets", "translucentbackground.svg")` beside `BACKGROUND_SVG`.
- `tests/test_desktoptheme.py`: import `TRANSLUCENT_BACKGROUND_SVG`, add
`("translucentbackground.svg", TRANSLUCENT_BACKGROUND_SVG, 16, 16)` to `SVG_CANVASES` (so the
registry, canvas, id and self-containment tests cover it) and
`os.path.join("widgets", "translucentbackground.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_background.py`: import `TRANSLUCENT_BACKGROUND_SVG` and add
`test_translucent_copy_is_identical` to `TestBackground`, opening `BACKGROUND_SVG` and
`TRANSLUCENT_BACKGROUND_SVG` in binary and asserting equal bytes (mirroring
`TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktoptheme `widgets/background.svg` row's guarantee to "…and
its `widgets/translucentbackground.svg` copy is byte-identical." The row already names
`TestBackground`, which holds the new test.
- `README.md`: in the `widgets/background.svg` sentence, add that a byte-identical copy ships at
`widgets/translucentbackground.svg`, where `BasicAppletContainer.qml` looks for a translucent-hint
applet container's background.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/translucentbackground.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_background.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `widgets/translucentbackground.svg` is byte-identical to `widgets/background.svg`, asserted by
`TestBackground::test_translucent_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 16x16 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (the README prose names the
file) and `tests/test_invariants.py`.
- Removing `widgets/translucentbackground.svg` makes `test_translucent_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer equals
the registry).

### Mac OS 8.6 grey menu body: ground `widgets/background.svg` in the open Apple menu (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `theme/desktoptheme/org.macos8.desktop/widgets/background.svg` paints the body of every
`PlasmaComponents.Menu` (context menus and combo-box dropdowns), `Drawer`, `Popup` and planar
applet container as a flat `#FFFFFF` face, and its comment justifies that with
`[Colors:View] BackgroundNormal`. But the open Apple menu in the retail screenshot
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` — the same image
`tests/test_colorscheme_reference.py::TestReferenceAnchors` samples the menu-bar face from — has a
flat `#DDDDDD` body, the Platinum face, not white. Ship the reference's grey menu body and pin it
to the reference pixels.

**Reference.** The Apple menu is open in `desktop_archiveorg8.6hd.png`, dropping from the top-left
(its body spans roughly x=6..160, y=16..355). The menu's empty right margin, clear of item text and
icons, is flat `#DDDDDD`: (150, 60) = (221, 221, 221) and (150, 200) = (221, 221, 221). The Finder
window's content in the same image is white at (470, 300) — already the `[Colors:View]` anchor —
so the menu body is a distinct grey, not the View background. (The image is stored with Git LFS,
so a clone without it must skip this test, as `test_colorscheme_reference` does.)

**Approach.**
- `widgets/background.svg`: change the face — the centre tile and the interiors of the four edge
tiles — from `#FFFFFF` to `#DDDDDD`, keeping the 1px `#000000` outline and the 3px/10px nine-slice
contract. Rewrite the header comment's face paragraph: the body is the Platinum grey `#DDDDDD`
sampled from the open Apple menu in `desktop_archiveorg8.6hd.png`, not `[Colors:View]`; drop the
"flat white" wording.
- `tests/test_desktoptheme_background.py`: `test_background_pixels` passes `FACE` instead of
`WHITE` to `assert_face_bevel`; `test_background_colours` expects `{BLACK, FACE}`; import `FACE`
from `support.platinum_palette` (it is already `#DDDDDD`). Add a reference case, mirroring the
`ReferenceScreenshotMixin` use in `tests/test_desktoptheme_panel.py` and
`tests/test_desktoptheme_menubaritem.py`, whose `REFERENCE` is
`macos8.6-screenshots/desktop_archiveorg8.6hd.png` and which compares `pixel(150, 60)` and
`pixel(150, 200)` to the artwork's own rendered face, skipping when the LFS image is not
materialized.
- `README.md`: the `widgets/background.svg` sentence at the desktop-theme paragraph says the
Platinum grey menu body instead of "the flat white Platinum body".
- `docs/invariants.md`: the desktoptheme `background.svg` row's guarantee ("draws the Platinum
menu body") still holds; no provenance exception is needed now that the face is reference-sampled.

**Acceptance criteria.**
- `background.svg`'s parsed fill set is exactly `{#000000, #DDDDDD}`, its 10x10 centre and four
edge tiles are `#DDDDDD`, and its outline is 1px `#000000` with no bevel.
- The new reference test compares the artwork's own rendered face to the two `#DDDDDD` pixels
from `desktop_archiveorg8.6hd.png` and skips when the image is missing, exactly as the other
reference-screenshot cases do.
- `background.svg`'s comment names the reference and the sampled pixels and no longer derives the
face from `[Colors:View]`.
- README.md no longer calls the menu body white.
- `make check` is green.

### Fidelity gate for the rendered window's title-bar boxes (close, zoom, collapse) (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate byte-compares the title-bar's middle strip and the
side and bottom borders, but not the three Platinum title-bar boxes, so a regression in how
Aurorae places or sizes them renders unnoticed. Extend `tests/test_render_surface.py::TestRender`
to byte-compare the close, zoom and collapse box regions of the render against the reference
screenshots.

**Grounding (verified 2026-10-18 with `tools/render_surface.py --settle 3` on this tree and
`tools/png`).** The 320x240 render puts the window at the capture's origin, and each box region is
byte-identical to the reference (0 differing pixels):
- close box: render `(4,4,13,13)` vs `aboutsystem_betawiki.png` `(11,29,13,13)`;
- collapse box: render `(303,4,13,13)` vs `aboutsystem_betawiki.png` `(343,29,13,13)`;
- zoom box: render `(282,4,21,13)` vs `systemprofiler_betawiki.png` `(776,26,21,13)`.
The close and collapse boxes use `aboutsystem_betawiki.png` (its collapse box at x=343); the zoom
box uses `systemprofiler_betawiki.png`, the only reference whose window shows a zoom box
(`aboutsystem`'s window cannot be zoomed, as `tests/support/aurorae_fixtures.py` records), with
`ZOOM_BOX_X = 5` matching the 21px gap-plus-box canvas. The title-bar strip gate deliberately
starts at x=30 to clear the close box, so these three regions are currently ungated at render
time.

**Approach.**
- `tests/test_render_surface.py`: beside the existing border crops, add
  `PROFILER_REFERENCE = str(repo_root.ROOT / "macos8.6-screenshots" / "systemprofiler_betawiki.png")`
  and the six crop tuples `CLOSE_CANDIDATE`/`CLOSE_REFERENCE`,
  `COLLAPSE_CANDIDATE`/`COLLAPSE_REFERENCE`, `ZOOM_CANDIDATE`/`ZOOM_REFERENCE` with the values
  above.
- Generalize `TestRender.assert_strip_pixels_match` to take a `reference_path=REFERENCE`
  argument and load that image with `support.reference_image.read_reference` +
  `skip_unless_materialized` (so the zoom test skips when the profiler LFS image is absent), then
  add `test_title_bar_boxes_match_the_reference` iterating the three
  `(candidate_crop, reference_crop, reference_path)` triples. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row `| The rendered window's title-bar boxes are
  byte-identical to the same regions of the reference screenshots. |
  tests/test_render_surface.py::TestRender::test_title_bar_boxes_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph, name the box regions beside the title-bar and
  border strips.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `TestRender.test_title_bar_boxes_match_the_reference` passes where the render tools and both
  references are materialized, and skips when either reference is an unmaterialized LFS pointer.
- Each region is pinned to zero differing pixels: shifting any crop by one pixel, or changing the
  box art or the Aurorae box geometry in `org.macos8.desktoprc`, makes the test fail.
- `docs/invariants.md` resolves the new `tooling` row, and `make check` is green.

### Mac OS 8.6 opaque menu bar: ship the `solid/widgets/panel-background.svg` copy (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `Panel.qml` draws an opaque panel from `solid/widgets/panel-background`, but the
desktop theme ships only `widgets/panel-background.svg`, so the menu bar loses its Platinum bevel
whenever the panel is opaque. Ship the solid copy so the opaque menu bar is Platinum too.

**Grounding.** `/usr/share/plasma/shells/org.kde.plasma.desktop/contents/views/Panel.qml` gives
its two opaque items (`opaqueItem`, `floatingOpaqueItem`) `imagePath:
"solid/widgets/panel-background"`, while the two translucent items use
`widgets/panel-background`. Plasma 6's default panel opacity mode is Adaptive
(`PanelConfiguration.qml`'s opacity combo defaults to index 0), and in Adaptive mode a window
touching the panel (`screenCovered`) drives `panelOpacity` to 1, which hides the translucent item
and shows the opaque one; choosing the Opaque mode does the same always. KSvg does not map
`solid/widgets/panel-background` onto `widgets/panel-background` — the same behaviour
`tests/test_desktoptheme_tooltip.py::TestTooltip::test_solid_copy_is_identical` records for
`PlasmaComponents.ToolTip`'s hardcoded `solid/widgets/tooltip` — so today the opaque menu bar
resolves to the default theme's Breeze `solid/widgets/panel-background.svgz` (the default theme
ships a solid copy; ours ships only `solid/widgets/tooltip.svg`). `widgets/panel-background.svg`
is already fully opaque (its fills are the solid `#FFFFFF`/`#DDDDDD`/`#999999`/`#000000` with no
alpha), so a byte-identical copy is the correct solid variant. Out of scope: a
`solid/widgets/background.svg` (the default theme ships one, but no installed QML requests it —
`DialogBackground.qml` hardcodes `widgets/background` and `libPlasmaQuick` carries no `solid/`
path), so it is not shipped here.

**Approach.**
- Add `theme/desktoptheme/org.macos8.desktop/solid/widgets/panel-background.svg`, byte-identical
to `widgets/panel-background.svg` (no header change, so the copy test compares bytes), matching
the existing `solid/widgets/tooltip.svg`.
- `tests/support/desktoptheme_paths.py`: add `SOLID_PANEL_SVG = os.path.join(PACKAGE, "solid",
"widgets", "panel-background.svg")` beside `SOLID_TOOLTIP_SVG`.
- `tests/test_desktoptheme.py`: import `SOLID_PANEL_SVG`, add `("solid/widgets/panel-background.svg",
SOLID_PANEL_SVG, 12, 22)` to `SVG_CANVASES` (so the registry, canvas, id and self-containment
tests cover it), add `"solid/widgets/panel-background.svg": ("",)` to `ORIGIN_STATES` (its
unprefixed margin rects sit at the origin of the canvas grown to hold the 22px-tall `north-`
state, like `panel-background.svg`), and add
`os.path.join("solid", "widgets", "panel-background.svg")` to `TestInstall.INSTALLED_FILES`.
- `tests/test_desktoptheme_panel.py`: import `SOLID_PANEL_SVG` and add
`test_solid_copy_is_identical` to `TestPanelBackground`, opening `PANEL_SVG` and `SOLID_PANEL_SVG`
in binary and asserting equal bytes (mirroring `TestTooltip::test_solid_copy_is_identical`).
- `docs/invariants.md`: extend the desktoptheme `widgets/panel-background.svg` row's guarantee
to "`widgets/panel-background.svg` draws the menu bar, including its top-panel north state, and
its `solid/` copy is byte-identical." The row already names `TestPanelBackground`, which holds
the new test.
- `README.md`: in the `widgets/panel-background.svg` sentence, add that a byte-identical copy
ships at `solid/widgets/panel-background.svg`, where `Panel.qml` looks for an opaque panel's
background.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/solid/widgets/panel-background.svg`
(new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme.py`,
`tests/test_desktoptheme_panel.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `solid/widgets/panel-background.svg` is byte-identical to `widgets/panel-background.svg`,
asserted by `TestPanelBackground::test_solid_copy_is_identical`.
- `test_registry_covers_every_shipped_svg` passes with the new file in `SVG_CANVASES`, and
`test_root_canvas_matches_the_artwork_layout`, `test_every_svg_declares_unique_ids` and
`test_every_svg_is_self_contained` cover it (its 12x22 canvas, unique ids, no style/script or
external reference).
- `TestInstall` still passes with the new file listed in `INSTALLED_FILES`.
- `make check` exits 0, including `tests/test_readme_theme_files.py` (its `*/*.svg` glob does not
reach the two-level `solid/` path, and the README prose names the file) and
`tests/test_invariants.py`.
- Removing `solid/widgets/panel-background.svg` makes `test_solid_copy_is_identical` fail (the
open raises) and `test_registry_covers_every_shipped_svg` fail (the shipped set no longer
equals the registry).

### Mac OS 8.6 splash: draw the reference's full "Mac OS 8.6" wordmark (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The startup splash's wordmark draws the truncated label `Mac OS`;
`macos8.6-screenshots/boot2_betawiki.png` shows the full `Mac OS 8.6`. Draw the full label so the
login splash matches the reference.

**Grounding.** In `macos8.6-screenshots/boot2_betawiki.png` (240x180, the retail 8.6 boot screen
whose `8.6` is legible) the wordmark's black glyphs occupy `x=89..150, y=71..83` — 62 of the 80
columns of the panel's white face (`x=80..159, y=39..88`, re-derived by
`tests/test_splash_reference.py::TestSplashGeometry::test_grid_geometry`). `Splash.qml`'s
`wordmark` Text draws `text: "Mac OS"`, roughly 38 columns centred on the panel, leaving the
reference's leftmost (`x=89..~100`) and rightmost (`x=~140..150`) glyph columns blank. The
original splash plan (PLANS.md `## Done`, "Mac OS 8.6 Platinum startup splash") and
`tests/test_splash_qml.py::test_wordmark_shows_the_reference_label_at_its_grid_size` both call
`Mac OS` the reference label, which the thumbnail does not support.

**Approach.**
- `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`: change the `wordmark`
  `Text`'s `text` from `"Mac OS"` to `"Mac OS 8.6"`. Leave its `y: 71 * root.unit`,
  `anchors.horizontalCenter: panel.horizontalCenter` and `font.pixelSize: 12 * root.unit`
  unchanged: the 12-row band and the panel centring already match the reference.
- `tests/test_splash_qml.py`: change `test_wordmark_shows_the_reference_label_at_its_grid_size`
  to require `text: "Mac OS 8.6"` and correct its comment, which calls `Mac OS` the reference
  label.
- `tests/test_splash_reference.py`: add `test_wordmark_spans_the_reference_band` to
  `TestSplashGeometry`. Derive the wordmark's black-pixel bounding box from the thumbnail (dark
  pixels with all three channels below a fixed threshold in the band `y=68..86`, `x=84..156`,
  which excludes the logo stem above `y=68`) and assert its width is at least 55 of the face's 80
  columns, so a reference whose label is no wider than `Mac OS` fails instead of silently passing.

**Files touched.** `theme/look-and-feel/org.macos8.desktop/contents/splash/Splash.qml`,
`tests/test_splash_qml.py`, `tests/test_splash_reference.py`.

**Acceptance criteria.**
- The `wordmark` Text's `text` is exactly `"Mac OS 8.6"`; any other string fails
  `test_wordmark_shows_the_reference_label_at_its_grid_size`.
- `test_wordmark_spans_the_reference_band` re-derives the reference wordmark bbox on
  `boot2_betawiki.png` and passes; a label that spans fewer than 55 face columns fails it.
- `make check` exits 0.
- Recorded deviation (not fixed here): the reference wordmark is a high-contrast serif (Apple's
  Garamond-family wordmark) while the QML draws the system UI font, so glyph shapes still differ;
  shipping a typeface is out of scope and the reference set has no larger boot capture to ground
  one.

### Mac OS 8.6 Platinum full-Trash icon (`32x32/places/user-trash-full.svg`) for the icon theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** KDE asks for the icon name `user-trash-full` whenever the Trash holds something
(`/usr/share/plasma/plasmoids/org.kde.plasma.trash/contents/ui/main.qml`:
`hasContents ? "user-trash-full" : "user-trash"`; Dolphin's Places panel and the desktop do the
same). The icon theme ships only `theme/icons/org.macos8.desktop/32x32/places/user-trash.svg`, so
the non-empty state falls through `Inherits=breeze` to Breeze's flat modern `user-trash-full.svg`
— the desktop's Trash visibly stops being Platinum the moment it holds a file. Ship our own
full-Trash art so the non-empty state stays Platinum.

**Approach.**
- Add `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg`: our own 32x32 Platinum
drawing, the same can as `user-trash.svg` (lid, body outline/face, the two grey/white rib pairs),
with the handle replaced by a `#FFFFFF` paper sheet outlined in `#000000` rising above the lid, so
the can reads as full. Recommended drawing, in document order (the implementer may adjust the
paper shape, but the constraints below hold):
  ```xml
  <path d="M12 2 l3 2 l3 -2 l1 7 h-8 Z" fill="#000000"/>
  <path d="M13 3 l2 1 l2 -1 l1 5 h-6 Z" fill="#FFFFFF"/>
  <rect x="6" y="8" width="20" height="5" fill="#000000"/>
  <rect x="7" y="9" width="18" height="4" fill="#DDDDDD"/>
  <rect x="7" y="9" width="18" height="1" fill="#FFFFFF"/>
  <rect x="7" y="12" width="18" height="1" fill="#999999"/>
  <path d="M9 13 h14 l-2 16 H11 Z" fill="#000000"/>
  <path d="M10 14 h12 l-2 14 H12 Z" fill="#DDDDDD"/>
  <rect x="13" y="16" width="1" height="10" fill="#999999"/>
  <rect x="14" y="16" width="1" height="10" fill="#FFFFFF"/>
  <rect x="17" y="16" width="1" height="10" fill="#999999"/>
  <rect x="18" y="16" width="1" height="10" fill="#FFFFFF"/>
  ```
- Register the file in `tests/test_icon_theme.py`: add its package-relative path to `SHIPPED_ICONS`
and its exact drawing-element tuple (via the module's `_shape` helper) to `ICON_SHAPES`. The
existing `TestIndex`/`TestIcons`/`TestIconGeometry` tests then cover the new icon: it must be a
32x32 square SVG whose fills are a subset of `PLATINUM_FILLS`, with no scripts, `<style>`,
external references or duplicate ids, and every drawing element must match the pinned tuple.
`TestInstall.INSTALLED_FILES` is derived from `SHIPPED_ICONS`, so the install lifecycle covers it
with no further edit.
- `32x32/places` is already a declared directory in `theme/icons/org.macos8.desktop/index.theme`,
so the metadata does not change and no new size directory is added.
- `README.md`: in the icon-theme sentence, change "the desktop's hard-disk, folder, document and
Trash icons" to name the full-Trash art as well (e.g. "…document, Trash and full-Trash icons").
- `docs/invariants.md`: the `icons` section's "ships exactly the tracked icons" row already names
`tests/test_icon_theme.py::TestIndex`, which covers the new file; no text change.

**Files touched.** `theme/icons/org.macos8.desktop/32x32/places/user-trash-full.svg` (new),
`tests/test_icon_theme.py`, `README.md`.

**Acceptance criteria.**
- `tests/test_icon_theme.py`'s `SHIPPED_ICONS` and `ICON_SHAPES` both list the new icon, and
`test_the_geometry_registry_covers_every_shipped_icon` passes; changing one drawing element in the
SVG fails `TestIconGeometry::test_each_icon_draws_its_pinned_artwork`.
- Deleting the SVG, or removing it from either registry, fails `make check`.
- `make check` is green, and `make install XDG_DATA_HOME=<tmp>` installs the new icon
(`TestInstall` covers the installed file set).

### Record-checker mutation harness: manufacture the malformed inputs from the shipped registers so a silent accept or drop is observable (planned 2026-10-18 by the steward role; from the recurring `no-observability` validation gap in thirteen Fixed entries) — done 2026-10-18

**Goal.** Twelve Fixed entries share one mechanism: a record checker (`tests/invariants.py`'s
register parser and reference resolver, `tests/placeholders.py`'s marker scanner) accepted or
silently dropped malformed input that the shipped records never contain, so no test or real run
could surface the bug — each was found by reading the checker and fixed with one hand-written case.
Add a mutation harness that manufactures each malformed shape from the shipped registers
(`docs/invariants.md`, `PLACEHOLDERS.md` and the shipped placeholder markers) and asserts the
checker reports it, so the acceptance boundary is exercised by data and the next silent accept or
drop fails a test instead of waiting for a reader.

**From (the `no-observability` Fixed entries).**
- `tests/invariants.py` register checker, ten entries (all fixed 2026-10-18): accepts a class whose
locally defined base only looks like a test case; accepts a register reference that escapes the
repository; accepts a method reference into a class that is not a test case; accepts a register
reference to a class with no tests; accepts a register reference to a non-test method; accepts a
register reference with a segment after the method; accepts a register reference ending in `::`,
pinning a guarantee to no test; drops a row that does not split into three cells; drops a row whose
Test cell has no backticked reference; drops a row whose cell contains an escaped pipe.
- `tests/placeholders.py` marker scanner, two entries (both fixed 2026-10-18): ignores
`PLACEHOLDER:` markers in the theme's `.kvconfig` file; ignores them in the theme's `.js` and
`.desktoprc` files.
- The thirteenth `no-observability` entry, "Palette anchors are not re-derivable from the reference
screenshots" (fixed 2026-10-08), is a different mechanism — a hard-coded anchor assertion — and is
retired by the register's provenance-exception row and `TestProvenanceNote`, not by this harness.

**Approach.**
- Add `tests/support/checker_scratch.py` and its two per-checker tables
(`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`): one named
mutation per rejection shape the two checkers must catch, each a transform of a copy of the real
register or of a scratch theme root plus the diagnostic substring the checker must raise. Seed
the table with the twelve shapes above. The reference mutations point the register's first row
at `tests/support/mutant_module.py`, a shipped
fixture holding the class shapes the shipped tests never define, and at a real test case in
`tests/test_checker_mutations.py`; the placeholder mutations name real shipped theme files, so
every path they cite exists in the tree.
- Add `tests/test_checker_mutations.py`: copy `docs/invariants.md` and the placeholder register into
a scratch root, apply each mutation, run the checker, and assert the named diagnostic; a mutation
the checker does not reject fails. Exercise the `.js`/`.desktoprc`/`.kvconfig` cases by writing one
marked file per text format the theme ships into the scratch theme root.
- Give each checker a `REJECTION_SHAPES` list naming the boundaries it must reject (the shapes its
`cross_check` docstring already enumerates), and add a test asserting the list and the mutation
table name the same rejection boundaries, so a boundary named in one without the other fails.

**Files touched.** The checker-mutation fixtures (now `tests/support/checker_scratch.py`,
`tests/support/invariants_mutations.py` and `tests/support/placeholders_mutations.py`),
`tests/test_checker_mutations.py` (new), `tests/support/mutant_module.py` (new),
`tests/invariants.py`, `tests/placeholders.py` (the `REJECTION_SHAPES` lists).

**Acceptance criteria.**
- Every shape above is a mutation entry, and applying it makes the matching checker raise the named
diagnostic; a scratch run with one mutation's expected diagnostic removed demonstrates the harness
fails.
- `REJECTION_SHAPES` for both checkers is covered by the mutation table; removing a table row fails
the guard test.
- `make check` is green, with the existing hand-written rejection tests still passing.

**Implementation note (2026-10-18).** The escaped-pipe and the three placeholder-format
shapes are acceptance boundaries, not rejections: the checker must keep the row or find the
marker, so the harness pins them with an `observe` assertion instead of a diagnostic. The
`REJECTION_SHAPES` lists hold the nine invariant rejections and the three placeholder
rejections; the guard test asserts each list equals the rejection mutation names, so a name
or a mutation added without the other fails. It is a sync check between two hand-maintained
lists, not a detector of a new rejection branch added to a checker on its own.

### Fidelity gate for the rendered window frame's side and bottom borders (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** The rendered-window fidelity gate compares only the title-bar strip
(`TestRender::test_title_bar_matches_the_reference`). The frame's six-pixel left, right and
bottom borders are still pinned only by the SVG unit tests (`tests/test_aurorae_frame.py`) and the
rc test (`tests/test_aurorae_rc.py`), so nothing checks that KWin paints them at the reference
geometry. Extend the same render-and-byte-compare gate to those three border strips. It reuses
the one render `TestRender.setUpClass` already makes; no second render runs.

**Grounding (sampled 2026-10-18 with `tools.png.read_png` + `pixel_at` on a render from
`tools/render_surface.py --settle 3`).** The 320x240 render puts the window at (0,0): a 6px left
border at x=0..5, a 6px right border at x=314..319 and a 6px bottom border at y=234..239.
`aboutsystem_betawiki.png`'s window has its left outline at x=7 and top outline at y=25, so its
left border is x=7..12, its right border x=354..359 and its bottom border y=419..424. The
reference window is taller than the render, so the side strips compare only the straight part
between the title bar and the bottom border (212 rows), and the bottom strip the horizontal
border between the two corners (308 columns). Byte-exact comparisons:
- left: candidate `(0, 22, 6, 212)` vs reference `(7, 47, 6, 212)` — 0 differing of 1272;
- right: candidate `(314, 22, 6, 212)` vs reference `(354, 47, 6, 212)` — 0 differing of 1272;
- bottom: candidate `(6, 234, 308, 6)` vs reference `(13, 419, 308, 6)` — 0 differing of 1848.

**Approach.**
- `tests/test_render_surface.py`: keep `CANDIDATE_CROP`/`REFERENCE_CROP` for the title bar and add
  six module constants beside them — `LEFT_BORDER_CANDIDATE = (0, 22, 6, 212)`,
  `LEFT_BORDER_REFERENCE = (7, 47, 6, 212)`, `RIGHT_BORDER_CANDIDATE = (314, 22, 6, 212)`,
  `RIGHT_BORDER_REFERENCE = (354, 47, 6, 212)`, `BOTTOM_BORDER_CANDIDATE = (6, 234, 308, 6)`,
  `BOTTOM_BORDER_REFERENCE = (13, 419, 308, 6)`, each with its grounding row above as its comment.
  Extract the body of `test_title_bar_matches_the_reference` (the `read_reference` +
  `skip_unless_materialized` guard and the `process_runner.run` of the real `FIDELITY` CLI with
  `--candidate-crop`/`--crop`) into a helper method
  `assert_strip_matches(self, candidate_crop, reference_crop)`; the title-bar test keeps its name
  and calls the helper with its two constants. Add
  `test_frame_borders_match_the_reference`, which loops the three `(candidate, reference)` border
  pairs and calls the helper under `self.subTest`, so a failure names the strip.
- `docs/invariants.md`: add a second `tooling` row
  `| The rendered window's side and bottom border strips are byte-identical to the same strips of
  the reference screenshot. | tests/test_render_surface.py::TestRender::test_frame_borders_match_the_reference | none |`.
- `README.md`: in the Fidelity checking paragraph's `make check` sentence, extend the compared
  region from the title-bar strip to the title bar and the side and bottom borders.

**Files touched.** `tests/test_render_surface.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `make check` passes. `test_frame_borders_match_the_reference` runs (does not skip) where the
  render tools are on `PATH` and the LFS reference is materialized, and skips when the reference
  is an unmaterialized pointer; the existing title-bar test still passes.
- Each strip reports `differing pixels: 0 / 1272` (left and right) and `0 / 1848` (bottom).
- Changing `BorderLeft`, `BorderRight` or `BorderBottom` in
  `theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc`, or the border colours in
  `decoration.svg`, makes a named test fail.
- `tests/test_invariants.py` still resolves every register row against the repository.

### Fidelity gate for the rendered window decoration: byte-compare the title-bar strip to `aboutsystem_betawiki.png` (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** `tools/render_surface.py` renders the themed window in a headless KWin session and
`tools/fidelity.py` compares a rendered PNG against a reference screenshot, but no reference crop
or threshold for a rendered surface is chosen, so nothing checks that the assembled theme renders
like the reference. This is the later plan the render entry's "Out of scope" names. Choose the
first such crop — the window title bar — add a `--candidate-crop` option so the candidate can be
cropped to the reference crop's size, and pin the whole pipeline (install, KWin, Aurorae, render)
with a `make check` test that byte-compares the strip.

**Grounding (sampled 2026-10-18 with `tools.png.read_png` + `pixel_at`).** A 320x240 render
(`tools/render_surface.py --settle 3`, `org.kde.plasma.calculator`) puts the window's title bar at
the top of the capture: row 0 is the `#000000` top outline, rows 1..20 are the Platinum pinstripes,
row 21 is the `#000000` title-bar bottom outline. `aboutsystem_betawiki.png` (retail) has the same
window chrome one row per row at `y=25..46`: row 25 the top outline, rows 26..45 the pinstripes,
row 46 the bottom outline. So the render's rows `0..21` map to the reference's rows `25..46`.
The pinstripes are horizontal, so the x offset does not matter as long as both crops stay clear of
the close box and the centred title text: the reference's close box face is x=11..22 with its
`#FFFFFF` highlight at x=23, and the title text is centred near x=180. The strip `x=30..109,
y=0..21` of the render is byte-identical to `x=30..109, y=25..46` of the reference (0 differing
pixels of 1760, max channel delta 0); the same render compared to `y=24..45` or `y=26..47` fails,
so the one-row alignment is pinned by the test.

**Approach.**
- `tools/fidelity.py`: add `--candidate-crop X,Y,W,H` (`type=_parse_crop`,
  `metavar="X,Y,W,H"`, help "crop the candidate to this region before comparing"), apply it as
  `candidate = crop(candidate, *args.candidate_crop)` before `compare` (beside the existing
  `reference = crop(reference, *args.crop)`), and print `candidate crop: X,Y,W,H` when set,
  beside the existing `reference crop:` line. Update the module docstring's usage line to
  `[--candidate-crop X,Y,W,H]`. A run without the option is byte-for-byte unchanged in
  behaviour and output.
- `tests/test_fidelity_cli.py`: cover the option in `TestCli`, mirroring the existing `--crop`
  tests: `_write_padded_surface_pair` returns a 2x2 surface and a 4x4 padded image that embeds it
  at (1,1), so pass the padded image as candidate and the surface as reference with
  `--candidate-crop 1,1,2,2` and assert it passes; the `candidate crop:` rectangle is echoed
  only when the option is given; a malformed rectangle (`1,2,3`) is a usage error naming
  `--candidate-crop`; and a rectangle outside the candidate is a read error from `crop()`.
- `tests/test_render_surface.py`: add module constants beside `SCRIPT` — `FIDELITY =
  str(repo_root.ROOT / "tools" / "fidelity.py")`, `REFERENCE =
  str(repo_root.ROOT / "macos8.6-screenshots" / "aboutsystem_betawiki.png")`,
  `CANDIDATE_CROP = (30, 0, 80, 22)` and `REFERENCE_CROP = (30, 25, 80, 22)` — and a
  `test_title_bar_matches_the_reference` method to `TestRender`. It loads `REFERENCE` with
  `support.reference_image.read_reference` + `skip_unless_materialized` (imported beside the
  other `support` imports, so it skips where the LFS image is absent, like the other reference
  tests), then runs the real CLI `[sys.executable, FIDELITY, cls.output, REFERENCE,
  "--candidate-crop", "30,0,80,22", "--crop", "30,25,80,22"]` through `process_runner` and
  asserts exit 0 and `differing pixels: 0 / 1760` in stdout. It reuses the render `setUpClass`
  already makes, so no second render runs.
- `docs/invariants.md`: add a `tooling` row
  `| The rendered window's title-bar strip is byte-identical to the same strip of the reference
  screenshot. | tests/test_render_surface.py::TestRender::test_title_bar_matches_the_reference |
  none |`.
- `README.md`: in the Fidelity checking paragraph, replace the closing sentence "no reference
  crop or threshold for a rendered surface is chosen yet" with the chosen crop: `make check`
  renders the window (`make render`) and byte-compares its title-bar strip at candidate
  `30,0,80,22` against reference `30,25,80,22` of `aboutsystem_betawiki.png`, naming
  `--candidate-crop`.

**Files touched.** `tools/fidelity.py`, `tests/test_fidelity_cli.py`, `tests/test_render_surface.py`,
`docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `python3 tools/fidelity.py <render.png> macos8.6-screenshots/aboutsystem_betawiki.png
  --candidate-crop 30,0,80,22 --crop 30,25,80,22` exits 0 and prints `differing pixels: 0 /
  1760`; without `--candidate-crop` the run still fails on the size mismatch, and a run with
  neither option is unchanged.
- `TestRender.test_title_bar_matches_the_reference` passes where the render tools and the
  materialized reference are present, and skips when the reference is an unmaterialized LFS
  pointer. Changing the Aurorae pinstripe colours, the title-bar height, or the close-box width
  (so the close box reaches x=30) makes it fail.
- The new `--candidate-crop` tests in `tests/test_fidelity_cli.py` pass, and the existing
  `--crop` tests still pass unchanged.
- `docs/invariants.md` resolves the new tooling row, and `make check` is green.

### Mac OS 8.6 Platinum desktop icon action buttons (`widgets/action-overlays.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/action-overlays.svg` so the desktop containment's folder-icon action buttons draw Platinum add/open/remove buttons instead of inheriting Breeze's. The theme ships no `widgets/action-overlays`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last widget name the default session's applets reference and the theme does not ship: the layout's kicker, appmenu, systemtray, digitalclock, windowlist and desktopcontainment reference every other widget name the theme ships. Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README/register lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemActionButton.qml` is an `SvgItem` whose `svg` is `KSvg.Svg { imagePath: "widgets/action-overlays"; multipleImages: true; size: "16x16" }`; it sets `elementId: element + "-normal"`, switching to `element + "-hover"` while the pointer is over it and `element + "-pressed"` while down. Its width and height are `Kirigami.Units.iconSizes` chosen from `Plasmoid.configuration.iconSize` (small 16, smallMedium 22, medium 32, large 48), so the 16x16 art scales.
- `/usr/share/plasma/plasmoids/org.kde.desktopcontainment/contents/ui/FolderItemDelegate.qml` instantiates it with `element: model.selected ? "remove" : "add"` (the selection toggle) and `element: "open"` (the folder-popup button); both appear on hover over a desktop icon in the layout the global theme applies. The default theme's `widgets/action-overlays.svg` ships the plain ids `add-`/`open-`/`remove-` plus `base`, and no size-prefixed ids, so the consumer resolves the plain ids.
- `main.qml` sets `imagePath: "widgets/toolbox"` on an `Svg` it never draws, and no installed desktop theme ships a `toolbox.svgz`; the toolbox is dead code, not a surface to style.

**Provenance.** No Mac OS 8.6 screenshot in the reference set shows a hover action button, so the shape and its three states are KDE-required; the fills reuse the grounded Platinum faces the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face). No new palette constant is introduced.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/action-overlays.svg`, a 16x16 canvas with nine groups, ids `add-normal`, `add-hover`, `add-pressed`, `open-normal`, `open-hover`, `open-pressed`, `remove-normal`, `remove-hover`, `remove-pressed` (the plain ids the consumer resolves):
  - each group opens with the invisible `0,0,16,16` `fill="none"` bounding rect, then the `actionbutton.svg` circle recipe at (8,8): a `#000000` r=7 outline circle, the two bevel half-discs of radius 6 split on the top-right to bottom-left diagonal, and the `#DDDDDD` r=5 face circle;
  - `normal` and `hover` keep the raised bevel (`#FFFFFF` top-left half, `#999999` bottom-right half) and `pressed` swaps it; the `hover` face is `#FFFFFF` (a lit Platinum button), the `normal` and `pressed` face `#DDDDDD`;
  - a `#000000` glyph over the face: `add` a plus, `remove` a minus (each a stroked path with `fill="none"`), `open` a right-pointing filled triangle, sized to fit inside the r=5 face.
- `tests/support/desktoptheme_paths.py`: add `ACTION_OVERLAYS_SVG = os.path.join(PACKAGE, "widgets", "action-overlays.svg")`.
- New `tests/test_desktoptheme_actionoverlays.py`, modelled on `tests/test_desktoptheme_actionbutton.py` (extends `SvgCase`): `TestActionOverlays` pins the nine ids (`assert_ids_present`), the parsed fill set (`PLATINUM_FILLS | {"none"}`), the stroke set (`{"#000000"}`), `assert_no_script_elements`, each group's bounds rect, each state's circle geometry and bevel order, and each kind's glyph path (`d`, `fill`, `stroke`, `stroke-width`).
- `tests/test_desktoptheme.py`: add `("action-overlays.svg", ACTION_OVERLAYS_SVG, 16, 16)` to `SVG_CANVASES` (and a clause about it to the canvas comment) and `os.path.join("widgets", "action-overlays.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktoptheme row `widgets/action-overlays.svg` draws the Platinum desktop icon action buttons. | `tests/test_desktoptheme_actionoverlays.py::TestActionOverlays` | none.
- `README.md`: add `widgets/action-overlays.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/action-overlays.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionoverlays.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `action-overlays.svg` parses with a 16x16 root canvas; the nine element ids are present and unique; every fill is in `PLATINUM_FILLS | {"none"}` and every stroke `#000000`.
- Every group carries the `0,0,16,16` invisible bounds rect; `normal`/`hover` paint the white-top-left/grey-bottom-right bevel and `pressed` the swapped one; the `hover` face is `#FFFFFF`, the `normal`/`pressed` face `#DDDDDD`; each kind's glyph is pinned by its `d` and its stroke/fill attributes.
- `make install` copies the SVG into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), `test_registry_covers_every_shipped_svg` and the README backtick test pass, and `docs/invariants.md` resolves the new row's test.
- `make check` is green.

### Mac OS 8.6 Platinum round action button (`widgets/actionbutton.svg`) for the desktop theme (planned 2026-10-18 by the plan role) — done 2026-10-18

**Goal.** Ship `widgets/actionbutton.svg` so `PlasmaComponents.RoundButton` and `PlasmaComponents.Dial` draw a Platinum circle instead of inheriting Breeze's blue one. The theme ships no `widgets/actionbutton`, so `KSvg` resolves the name to the default theme's Breeze file. It is the last of the `actionbutton`/`busy`/`switch` surfaces the done plans name (`busy` and `switch` are done). Independent of every shipped widget: it adds one artwork file, one path constant, one test module and registry/README lines.

**Consumers (verified in the installed Plasma 6.3.6 tree).**
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RoundButton.qml` reads `imagePath: "widgets/actionbutton"` in one `KSvg.Svg`, draws element `pressed` while down/checked else `normal` (`buttonItem`), and overlays `Private.RoundShadow` with states `hidden`/`hover`/`focus`/`shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/Dial.qml` reads `imagePath: "widgets/actionbutton"`, element `pressed` while pressed else `normal`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/private/RoundShadow.qml` reads `imagePath: "widgets/actionbutton"` and draws element `hover`, `focus` and (default state) `shadow`.
- `/usr/lib/x86_64-linux-gnu/qt6/qml/org/kde/plasma/components/RadioIndicator.qml` uses the older combination: `imagePath: "widgets/actionbutton"`, element `normal`, over `widgets/checkmarks`.
- Breeze's `actionbutton.svg` (the default theme) ships elements `normal`, `pressed`, `hover`, `focus` and no `shadow` element (verified by decoding `/usr/share/plasma/desktoptheme/default/widgets/actionbutton.svgz`); a missing `shadow` draws nothing, so the theme keeps Breeze's behaviour there. No shipped plasmoid uses `RoundButton`/`Dial`/`RoundShadow`, so this surface is not visible in the default session; it completes the widget set for third-party Plasma widgets.

**Provenance.** Mac OS 8.6 draws no round button, so the shape and its hover/focus rings are KDE-required; the fills reuse the grounded Platinum face and bevel the other widgets ship (`#000000` outline, `#FFFFFF` highlight, `#999999` shadow, `#DDDDDD` face), and the focus ring reuses `button.svg`'s 1px `#000000` ring treatment. State this in the file's header comment.

**Approach.**
- New `theme/desktoptheme/org.macos8.desktop/widgets/actionbutton.svg`, a 36x36 canvas with four `<g>` elements, each opening with an invisible 36x36 bounding rect, so `KSvg` scales all four by the same bounds:
  - `normal` (raised): a filled `#000000` circle r=17 (outline), then a `#FFFFFF` half-disc path (top-left half, r=16) and a `#999999` half-disc path (bottom-right half, r=16) painting the 1px bevel, then a filled `#DDDDDD` circle r=15 (face). Each half-disc is one `M`/`A`/`Z` path, so `path_arcs` reads one 180-degree arc.
  - `pressed` (sunken): the same circles with the bevel halves swapped — `#999999` top-left, `#FFFFFF` bottom-right.
  - `hover` and `focus`: a 1px `#000000` ring in the outermost pixel, just outside the r=17 outline, drawn as one donut path — a full r=18 circle and a full r=17 circle wound the other way, so the nonzero fill rule leaves the interior transparent and the underlying `normal` art shows through.
  - no `shadow` element (Breeze ships none).
- `tests/support/desktoptheme_paths.py`: add `ACTIONBUTTON_SVG = os.path.join(PACKAGE, "widgets", "actionbutton.svg")`.
- New `tests/test_desktoptheme_actionbutton.py`, modelled on `tests/test_desktoptheme_radiobutton.py` (circles) and `tests/test_desktoptheme_busywidget.py` (arcs):
  - `TestActionButton(SvgCase, unittest.TestCase)` with `SVG_PATH = ACTIONBUTTON_SVG`.
  - `test_actionbutton_contract`: `assert_ids_present(self, self.tree, ("normal", "pressed", "hover", "focus"))`, the parsed fill set is exactly `PLATINUM_FILLS | {"none"}`, and `assert_no_script_elements`.
  - `test_actionbutton_geometry`: for `normal`, the circles are `(18, 18, 17, "#000000")` then `(18, 18, 15, "#DDDDDD")`, and the two half-disc paths' arcs reconstruct (18,18) at r=16; their fills in document order are `#FFFFFF` then `#999999`, so the paint order pins the top-left highlight. For `pressed`, the same geometry with the two fills swapped. For `hover` and `focus`, the group holds no circle but one `#000000` donut path whose four 180-degree arcs reconstruct (18,18) at radii 18, 18, 17, 17 with the inner pair wound the other way, so a filled disc, a same-winding path or a swapped inner/outer radius fails. Every group must also hold one invisible 36x36 bounding rect, so all four scale identically.
- `tests/test_desktoptheme.py`: add `("actionbutton.svg", ACTIONBUTTON_SVG, 36, 36)` to `SVG_CANVASES` and `os.path.join("widgets", "actionbutton.svg")` to `TestInstall.INSTALLED_FILES`.
- `docs/invariants.md`: add the desktop-theme row `| widgets/actionbutton.svg draws the Platinum round action button. | tests/test_desktoptheme_actionbutton.py::TestActionButton | none |`.
- `README.md`: add `widgets/actionbutton.svg` to the desktop theme's widget inventory sentence.

**Files touched.** `theme/desktoptheme/org.macos8.desktop/widgets/actionbutton.svg` (new), `tests/support/desktoptheme_paths.py`, `tests/test_desktoptheme_actionbutton.py` (new), `tests/test_desktoptheme.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- `actionbutton.svg` parses with a 36x36 root canvas and the four named groups; its parsed fills are exactly the Platinum four plus `none` (the bounding rects).
- `normal`/`pressed` are concentric circles at (18,18) with r=17/16/15 and opposite bevel orders; `hover`/`focus` are a r=17..18 `#000000` donut path with a transparent r=17 interior, all pinned by name.
- `make install` copies the file into the installed desktop theme and `make uninstall` removes it (through `TestInstall`), the SVG registry covers it (through `TestSvgRootCanvas.test_registry_covers_every_shipped_svg`), and the README and `docs/invariants.md` list it.
- `make check` is green.

- Mac OS 8.6 Platinum busy indicator (`widgets/busywidget.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit b42c20a)
- Invariants register: `docs/invariants.md` pinning each subsystem's guarantee to its test (planned 2026-10-18, done 2026-10-18; commit 6dfe56b)
- Mac OS 8.6 Platinum switch widget (`widgets/switch.svg`) for the desktop theme (planned 2026-10-18, done 2026-10-18; commit 448301a)
- Mac OS 8.6 Kvantum widget style, part 4/4: select the Kvantum style from the global theme (planned 2026-10-18, done 2026-10-18; commit 1ce5330)
- Mac OS 8.6 Kvantum widget style, part 3/4: the Platinum surface controls (planned 2026-10-18, done 2026-10-18; commit d16dec4)
- Mac OS 8.6 Kvantum widget style, part 2/4: the Platinum track and value controls (planned 2026-10-18, done 2026-10-18; commit c8220b9)
- Mac OS 8.6 kicker logo: our own non-infringing `start-here-kde-symbolic` icon (planned 2026-10-18, done 2026-10-18; commit 397f190)
- Mac OS 8.6 Kvantum widget style, part 1/4: ship the `org.macos8.desktop` Kvantum theme with the Platinum palette and the core-control art (planned 2026-10-18, done 2026-10-18; commit 1e9762f)
- Mac OS 8.6 Platinum icon theme: replace the placeholder art with final non-infringing art (planned 2026-10-18, done 2026-10-18; commit ca89e96)
- Own icon art: `PLACEHOLDER:` markers and a test that keeps `PLACEHOLDERS.md` complete (planned 2026-10-18, done 2026-10-18; commit 58830a3)
- Mac OS 8.6 Platinum desktop icon theme: a minimal `org.macos8.desktop` icon package for the icons the desktop shows (planned 2026-10-18, done 2026-10-18; commit 364335d)
- Local theme apply, part 2/2: `make install-local-hook` writes an uncommitted `post-commit` hook that runs `make apply` (planned 2026-10-18, done 2026-10-18; commit e897ef0)
- Local theme apply, part 1/2: `make apply` installs and re-applies the theme to the running Plasma session (planned 2026-10-18, done 2026-10-18; commit c7c2d14)
- Mac OS 8.6 menu-bar top highlight: a `north-` panel-background state whose centre carries the white row 0 (planned 2026-10-18, done 2026-10-18; commit cdc6e60)
- Mac OS 8.6 Qt widget style: select Qt's built-in square-bevel `Windows` style from the global theme (planned 2026-10-18, done 2026-10-18; commit a318999)
- Mac OS 8.6 menu-title spacing: 7px horizontal padding in `widgets/menubaritem.svg` (planned 2026-10-18, done 2026-10-18; commit 31208c2)
- Mac OS 8.6 desktop icon labels: one line of text under each icon (planned 2026-10-18, done 2026-10-18; commit 727cde4)
- Mac OS 8.6 desktop icon arrangement: one right-aligned column of 32px icons (planned 2026-10-18, done 2026-10-18; commit aacf578)
- Mac OS 8.6 Platinum tooltip (`widgets/tooltip.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 84cdbbb)
- Mac OS 8.6 menu-bar clock format: 12-hour time with AM/PM, no date, no seconds (planned 2026-10-17, done 2026-10-17; commit dc4dfce)
- Clear the title-bar pinstripes around the zoom box, as Mac OS 8.6 does (planned 2026-10-17, done 2026-10-17; commit d59e398)
- Grow the Aurorae title-bar boxes to 13x13 with their white highlight (planned 2026-10-17, done 2026-10-17; commit 73bd870)
- Mac OS 8.6 zoom box glyph and collapse (windowshade) box for the Aurorae decoration (planned 2026-10-17, done 2026-10-17; commit ffa77e7)
- Mac OS 8.6 Platinum applet-popup heading (`widgets/plasmoidheading.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 262f2d9)
- Mac OS 8.6 Platinum etched separator (`widgets/line.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit 0446a33)
- Mac OS 8.6 menu-bar desktop layout for the global theme (`contents/layouts/`) (planned 2026-10-17, done 2026-10-17; commit 76ba0c4)
- Headless Plasma render-and-capture script that feeds `tools/fidelity.py` (planned 2026-10-17, done 2026-10-17; commit 4422d20)
- Wallpaper, part 2/2: Install the Mac OS 8.6 wallpaper package and select it from the global theme (planned 2026-10-17, done 2026-10-17; commit 884c659)
- Wallpaper, part 1/2: Mac OS 8.6 default desktop pattern as a Plasma wallpaper package (planned 2026-10-17, done 2026-10-17; commit d46c4eb)
- Mac OS 8.6 Platinum progress bar widget (`widgets/bar_meter_horizontal.svg`) for the desktop theme (planned 2026-10-17, done 2026-10-17; commit a683b57)
- Mac OS 8.6 Platinum popup / dropdown arrow widget for the desktop theme (done 2026-10-17; commit 1b5c020)
- Mac OS 8.6 Platinum toolbar background widget for the desktop theme (done 2026-10-17; commit ff71c62)
- Mac OS 8.6 Platinum tab-bar highlight widget for the desktop theme (done 2026-10-17; commit c8d132b)
- Mac OS 8.6 Platinum menu-bar item widget for the desktop theme (done 2026-10-09; commit 370205e)

- Mac OS 8.6 Platinum view item widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 1e1a455)
- Mac OS 8.6 Platinum slider widget for the desktop theme (planned 2026-10-09, done 2026-10-09; commit 698e2b2)
- Wire the Mac OS 8.6 window decoration into the global theme defaults (planned 2026-10-09, done 2026-10-09; commit 0063255)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part B1: inactive frame and inactive widget state (planned 2026-10-08, done 2026-10-09; commit 91189a7)
- Mac OS 8.6 Platinum window decoration (`aurorae/themes/`) part A: active frame, close and zoom widgets (planned 2026-10-08, done 2026-10-08; commit 15bee80)
- Mac OS 8.6 Platinum startup splash (`contents/splash/`) for the global theme (planned 2026-10-08, done 2026-10-08; commit 395994f)
- Mac OS 8.6 Platinum menu / popup background (`widgets/background.svg`) for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 27b7439)
- Mac OS 8.6 Platinum dialog / applet-popup background for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 8df5661)
- Mac OS 8.6 Platinum scroll bar widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 9f51d5b)
- Mac OS 8.6 Platinum list item widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7fe6ddc)
- Mac OS 8.6 Platinum text field widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 0fe5213)
- Mac OS 8.6 Platinum checkmarks widget for the desktop theme (planned 2026-10-08, done 2026-10-08; commit 7313acd)
- Mac OS 8.6 Platinum radio button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit a73c322)
- Mac OS 8.6 Platinum frame widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit ebb65ca)
- Mac OS 8.6 Platinum button widget for the desktop theme (planned 2026-10-07, done 2026-10-07; commit e553908)
- Mac OS 8.6 desktop theme package with the Platinum panel background (planned 2026-10-07, done 2026-10-07; commit 126538c)
- Mac OS 8.6 look-and-feel global theme package (planned 2026-10-07, done 2026-10-07; commit 0c0cd8b)
- Mac OS 8.6 Platinum color scheme and project check harness (planned 2026-10-07, done 2026-10-07; commit 2e58776)

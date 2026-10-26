# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role):** The
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
selected by `apply-gtk`; `make install` copies no GTK files); the standalone Firefox Platinum
sheet under `theme/firefox/` (its `userChrome.css` copied and its profile preference written
only by the opt-in `install-firefox` target); and the render and fidelity tooling.
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
landed, while its profile install is part 2/2, which has landed). Firefox work since that
series landed as single-surface chrome plans (the downloads-panel and all-tabs rows, the
sidebar frame, the menu-bar title box, the tab faces and the app-menu rows), and it now
reaches a content page: the `userContent.css` sheet paints the about:downloads
list (part 1/2), with its opt-in profile install as part 2/2 queued below. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

### Firefox Platinum chrome: paint the toolbar overflow panel rows like a Platinum menu (planned 2026-10-26 by the plan role; independent of the about:downloads content sheet)

**Goal.** Make Firefox's toolbar overflow panel (`#widget-overflow`, the chevron menu that holds toolbar buttons which do not fit) read as a Mac OS 8.6 menu: every row is square, and an enabled row under the pointer takes the flat `#CCCCFF` menu-item highlight with black text and no toolbar bevel. The panel's disabled rows, focus rings, separators, toolbar springs, panel headers and panel body stay Firefox's. This is the same row treatment the app menu already has, applied to the remaining toolbar-facing arrow panel.

**Grounding.** No reference screenshot shows Firefox chrome or its toolbar overflow panel. The row highlight adapts the reference-grounded `widgets/viewitem.svg`, whose `hover`/`selected`/`selected+hover` slices are each a flat square `#CCCCFF` with no bevel or outline (`tests/test_desktoptheme_viewitem.py::TestViewItem`), and reuses the sheet's existing menu-item mapping (`menupopup > menuitem:hover`). `#CCCCFF` is the project's sampled `[Colors:Selection]` token pinned by `tests/test_colorscheme_reference.py::TestReferenceAnchors::test_selection_background`. Record the missing Firefox overflow-panel reference and the dated adaptation in the sheet header and the invariants row.

In the installed Firefox ESR 153.5.1, `browser/omni.ja` `chrome/browser/content/browser/browser.xhtml` defines `<panel id="widget-overflow" type="arrow">` around `<panelmultiview id="widget-overflow-mainView">`; its `.panel-subview-body` holds the `.widget-overflow-list` elements `#widget-overflow-list` and `#widget-overflow-fixed-list`, and its footer row is the `toolbarbutton.subviewbutton.panel-subview-footer-button` `#overflowMenu-customize-button`. `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton, .widget-overflow-list .toolbarbutton-1` `border-radius: var(--panel-menuitem-border-radius)` and gives `toolbarbutton.subviewbutton`, `.widget-overflow-list .toolbarbutton-1` and `.toolbaritem-combined-buttons:is(...) > toolbarbutton` the ghost hover tokens `--button-text-color-ghost-hover` and `--button-background-color-ghost-hover`, with a pressed shadow; `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines `--panel-menuitem-border-radius: var(--border-radius-small)` (4px) and maps the ghost hover to the violet theme token. The sheet's `panel[type="arrow"]` rule already sets the panel face `#DDDDDD` and black text, its generic `toolbarbutton:hover:not([disabled="true"])` adds the raised bevel, and nothing in the sheet targets `#widget-overflow`, so today these rows keep Firefox's violet wash and rounded corners.

**Approach.** In `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, immediately after the app-menu hover rule and before the all-tabs comment, add two rules with a short comment:

```css
#widget-overflow .subviewbutton:not(.panel-header .subviewbutton),
#widget-overflow .widget-overflow-list .toolbarbutton-1 {
  border-radius: 0 !important;
}

#widget-overflow .subviewbutton:not(.panel-header .subviewbutton):hover:not([disabled]),
#widget-overflow .widget-overflow-list .toolbarbutton-1:hover:not([disabled]) {
  background-color: #CCCCFF !important;
  color: #000000 !important;
  box-shadow: none !important;
}
```

Square the rows directly rather than overriding `--panel-menuitem-border-radius`, because that token is shared with the all-tabs, library and history subviewbuttons. The `.subviewbutton` selectors cover the footer customize row and exclude `.panel-header` descendants (the main view has no header today) so a future subview's back or edit button keeps Firefox's paint; the `.widget-overflow-list .toolbarbutton-1` selectors cover the overflowed toolbar items in both lists. The hover rule excludes disabled rows and matches while `:active` too, so it out-specifies Firefox's ghost pressed rule and the sheet's generic toolbar bevel. Add no rule for separators, toolbar springs, focus rings, icons, text, the panel body or the panel header.

In the header, append a provenance paragraph after the app-menu paragraph and before the closing `*/`: no reference shows Firefox's toolbar overflow panel; the row highlight adapts `widgets/viewitem.svg` and the sheet's menu-item mapping (platform colour adaptation 2026-10-26); Firefox's `chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css` gives `.subviewbutton` and `.widget-overflow-list .toolbarbutton-1` their `--panel-menuitem-border-radius` and their `--button-background-color-ghost-hover` violet hover, `chrome/toolkit/skin/classic/global/design-system/tokens-shared.css` defines those tokens, `chrome/browser/content/browser/browser.xhtml` defines `#widget-overflow`, its two `.widget-overflow-list` lists and the `#overflowMenu-customize-button` footer row, and the sheet squares and suppresses the ghost hover and generic toolbar bevel on those rows only, leaving the panel's disabled rows, focus rings, separators, springs and panel-header buttons Firefox's; declaration checks do not establish rendered pixels.

**Files touched.** `theme/firefox/org.macos8.desktop/chrome/userChrome.css`, `tests/test_firefox_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- `REQUIRED_RULES` in `tests/test_firefox_theme.py` gains the four selectors above (each list item of a grouped rule is one entry), with `border-radius: 0 !important` for the two square selectors and `background-color: #CCCCFF !important`, `color: #000000 !important`, `box-shadow: none !important` for the two hover selectors, using `SELECTION` and `BLACK` from `support.platinum_palette`.
- New `TestFirefoxChrome.test_overflow_panel_row_paint_is_scoped_to_the_overflow_panel` asserts the selectors naming `widget-overflow` are exactly those four, each starts with `#widget-overflow`, each equals its `REQUIRED_RULES` entry, the square selectors carry no declaration besides `border-radius`, both hover selectors carry `:hover` and `:not([disabled])`, and no rule in the sheet overrides `--panel-menuitem-border-radius`. It also matches the sheet selectors against a representative element tree with `support.selector_matching.matches`: an overflowed `toolbarbutton.toolbarbutton-1` inside `#widget-overflow-list` and one inside `#widget-overflow-fixed-list` match the square and hover rules, the `.subviewbutton.panel-subview-footer-button` `#overflowMenu-customize-button` matches both rules, a disabled overflowed row matches neither hover selector, a `.panel-header` button carrying `.subviewbutton` matches neither rule, and a `toolbarbutton.toolbarbutton-1` under `#nav-bar` matches none of them.
- `test_header_names_provenance_and_preference` gains the strings `"No reference shows Firefox's toolbar overflow panel"`, `"widgets/viewitem.svg"`, `"tests/test_desktoptheme_viewitem.py::TestViewItem"`, `"test_selection_background"`, `"chrome/browser/skin/classic/browser/customizableui/panelUI-shared.css"`, `"chrome/browser/content/browser/browser.xhtml"`, `"#widget-overflow"`, `"widget-overflow-list"`, `"widget-overflow-fixed-list"`, `"#overflowMenu-customize-button"`, `"--panel-menuitem-border-radius"`, `"--button-background-color-ghost-hover"` and `"platform colour adaptation 2026-10-26"`.
- `docs/invariants.md` gains a row in the `## firefox` table after the app-menu row: the toolbar overflow panel's rows (`#widget-overflow .subviewbutton` outside `.panel-header` and `#widget-overflow .widget-overflow-list .toolbarbutton-1`) are square, an enabled hovered row is flat `#CCCCFF` with black text and no toolbar bevel, and disabled rows, focus rings, separators, toolbar springs, panel headers and the panel body stay Firefox's; its test column names the new test, and its provenance records the missing Firefox overflow-panel reference, the `widgets/viewitem.svg` and menu-item mapping with the pinned anchors, the installed Firefox ESR 153.5.1 files, selectors and tokens above, and that declaration checks do not establish rendered pixels.
- `make check` passes, and the existing sheet, its install and their tests keep their declarations and scope.

### Firefox Platinum chrome, part 2/2: install the about:downloads `userContent.css` beside `userChrome.css` (planned 2026-10-26 by the plan role; independent of the waiting toolbar overflow panel plan)

**Goal.** Make `make install-firefox` copy both standalone Firefox sheets — the landed `userChrome.css` and the part 1/2 about:downloads `userContent.css` — into one profile's `chrome/` directory and add the one marker-delimited `user.js` preference that makes Firefox read them, and make `make remove-firefox` remove exactly those three changes. The two-sheet installer keeps the single-sheet installer's guarantees for both sheets: a non-empty foreign sheet is refused by path with nothing written, an empty or BOM-prefixed sheet of ours is adopted or recognised, a symlinked destination is refused before any write, a failed or interrupted write restores both sheets and `user.js`, and removal leaves a foreign sheet or preference untouched. The sheets' paint and declarations do not change; only how they reach a profile does.

**Grounding.** Part 1/2 landed the sheet at `theme/firefox/org.macos8.desktop/chrome/userContent.css`, whose first line is `/* org.macos8.desktop Firefox content, standalone userContent.css` (pinned by `tests/test_firefox_content_theme.py::TestFirefoxContentTheme::test_first_line_is_the_marker`), and its header still says the sheet is not installed until part 2/2 adds it to `make install-firefox`. The install today lives in `tools/install_firefox.py`: `SHEET` and `CSS_MARKER` name the one sheet, `_apply` reads it and the profile's `chrome/userChrome.css`, refuses a foreign non-empty file, refuses a symlinked destination, publishes the sheet and then `user.js`, and rolls both back from `_restore_file`/`_restore_user_js` on any `BaseException`; `_remove` rewrites `user.js` first, deletes the sheet only when its first line is our marker (BOM-stripped by `_is_our_sheet`), and restores `user.js` whenever the sheet still exists. The destination paths, bounded read and atomic write are `user_chrome_path`, `user_js_path`, `read_profile_text`, `write_profile_bytes` and `MAX_PROFILE_FILE_BYTES` in `tools/firefox_user_files.py`. `docs/invariants.md`'s `## firefox` opt-in-install row states that guarantee, and `tests/test_firefox_install.py` pins it: `TestInstall` and `TestRemove` mock writes and unlinks by exact path, and `TestRemove::test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal` encodes the one-sheet rule that an interrupt after the sheet unlink keeps the rewritten `user.js`. A grep of PLANS-DONE.md for `userContent` finds only the part 1/2 entry; no plan covers installing it.

**Approach.** In `tools/firefox_user_files.py`, add `user_content_path(profile)` returning `profile / "chrome" / "userContent.css"` beside `user_chrome_path`, and update the module docstring's two-file description to the three files the installer now reads and writes.

In `tools/install_firefox.py`, add `CONTENT_SHEET = "theme/firefox/org.macos8.desktop/chrome/userContent.css"`, `CONTENT_CSS_MARKER = "/* org.macos8.desktop Firefox content, standalone userContent.css"`, and an ordered module-level `SHEETS` tuple of `(source relative path, marker, path function)` entries: `(SHEET, CSS_MARKER, user_chrome_path)` then `(CONTENT_SHEET, CONTENT_CSS_MARKER, user_content_path)`. Keep `SHEET` and `CSS_MARKER` so existing imports and tests stand. Change `_is_our_sheet(text)` to `_is_our_sheet(text, marker)` and call it with each entry's marker.

Rewrite `_apply` to drive both sheets from `SHEETS` while preserving today's order and diagnostics. Read both shipped sheets up front in `SHEETS` order, wrapping an `OSError`/`ValueError` as `cannot read <source>` for that source (userChrome first, so the existing missing-source diagnostics still name it). Then read each destination with `read_profile_text`, remembering its previous text, and return `report_failure` for the first non-empty destination whose text is not that sheet's marker; nothing is written yet. Keep the existing `user.js` growth check. Refuse a symlink on every sheet destination and then `user.js` before `mkdir`, so a refused link leaves all three paths untouched. Create `chrome/` once, write the sheets in `SHEETS` order (userChrome, then userContent), then `user.js`. On any `BaseException`, call `_restore_file` for each sheet with its remembered text and `_restore_user_js` once, collecting rollback errors in `SHEETS` then `user.js` order, and raise a `ConfigError` combining the original failure with them exactly as today.

Rewrite `_remove` to read both destinations, treat each as owned when its text is that marker, and rewrite `user.js` before deleting anything, as today. Refuse a symlink on every owned sheet and then `user.js`. Delete the owned sheets in `SHEETS` order. On `BaseException`, restore the previous `user.js` only while at least one owned sheet still exists (replace the single `sheet_path.exists()` test with an `any(path.exists() ...)` over the owned sheet paths); once every owned sheet is gone, the rewrite is the completed removal and stays. Keep the existing by-name `cannot remove`/`cannot write` messages.

Update the module docstring and the parser description/epilog to name both sheets and both markers, the Makefile `install-firefox`/`remove-firefox` comments and help lines (`a foreign userChrome.css` becomes `a foreign userChrome.css or userContent.css`), and README's standalone-Firefox paragraph so it names `userContent.css`, both profile destinations and the fact that removal clears three changes. In `theme/firefox/org.macos8.desktop/chrome/userContent.css`, replace the header sentence "This sheet is not installed until part 2/2 adds it to make install-firefox." with "Part 2/2 installs it through make install-firefox." (keeping the `part 2/2` phrase the header test pins). Update the opt-in-install row in `docs/invariants.md` to cover both sheets, both markers and the extended test column.

**Files touched.** `tools/install_firefox.py`, `tools/firefox_user_files.py`, `Makefile`, `README.md`, `theme/firefox/org.macos8.desktop/chrome/userContent.css`, `tests/test_firefox_install.py`, `tests/test_firefox_content_theme.py` (docstring only, if it still says the install is unplanned), `docs/invariants.md`, `PLANS.md` (this entry's scope sentence).

**Acceptance criteria.**
- `install_firefox.CONTENT_SHEET` names the shipped `userContent.css`; `install_firefox.SHEETS` lists exactly two entries in userChrome-then-userContent order, each pairing its `SHEET`/`CONTENT_SHEET` source with `CSS_MARKER`/`CONTENT_CSS_MARKER` and `user_chrome_path`/`user_content_path`; and `firefox_user_files.user_content_path(profile)` equals `profile / "chrome" / "userContent.css"`.
- `TestUserJs.test_shipped_marker_and_preference_are_pinned` also asserts the content sheet's BOM-stripped first line equals `install_firefox.CONTENT_CSS_MARKER` and `tests/test_firefox_content_theme.py`'s `MARKER`, and that `CONTENT_SHEET` exists. The existing `CSS_MARKER` pin and one-block `user.js` pin stay unchanged.
- `TestInstall.test_install_copies_the_sheet_byte_for_byte_and_adds_one_block` (or a renamed equivalent) asserts both installed sheets byte-equal their shipped files and `user.js` holds the marker and preference once; an empty destination for either sheet is still adopted. The existing foreign-`userChrome.css` test becomes a `SHEETS`-driven test asserting for each sheet: exit 1, the foreign destination's path in stderr, that file unchanged, the other destination absent, and no `user.js`.
- `TestInstall.test_install_refuses_symlinked_profile_files_before_writing_anything` (the existing symlink test extended to `userContent.css`) asserts for all three destinations that exit 2 names `cannot write <path>` and `symbolic link`, the link and its target are untouched, and the other two destination files are not created. The dangling-link loop, the unreadable-file loop and the FIFO test cover `chrome/userContent.css` as well as `chrome/userChrome.css` and `user.js`.
- New `TestInstall.test_a_failed_user_content_write_removes_the_published_user_chrome` fails the write to `chrome/userContent.css` and asserts exit 2 names that path, `chrome/userChrome.css` is absent (or its prior text restored when it existed), and no `user.js` remains. New `TestInstall.test_a_failed_user_js_write_restores_both_previous_sheets` starts with both sheets carrying prior marker-led text and asserts a failed `user.js` write restores both texts exactly. New `TestInstall.test_an_interrupt_after_the_user_content_write_takes_effect_removes_both` publishes then interrupts on the content-sheet write and asserts neither sheet nor `user.js` remains; the existing failed-restore and interrupt tests still pass with the second sheet present.
- `TestRemove.test_remove_deletes_our_sheet_and_block_and_keeps_the_directory` also asserts `chrome/userContent.css` is gone and only the `chrome/` directory remains. New `TestRemove.test_remove_keeps_a_foreign_user_content_and_removes_our_user_chrome` leaves a foreign content sheet and our chrome sheet, then asserts removal drops only the chrome sheet and preference. New `TestRemove.test_remove_deletes_our_user_content_when_user_chrome_is_absent` asserts a lone our-marker content sheet and its preference block are removed. New `TestRemove.test_a_failed_user_content_unlink_is_reported_by_path` unlinks our chrome sheet, fails on the content sheet, and asserts exit 2 names the content path, the content sheet remains, and the previous `user.js` is restored. New `TestRemove.test_an_interrupt_after_only_the_first_sheet_unlink_restores_user_js` interrupts after the chrome-sheet unlink and asserts `user.js` is restored because the content sheet remains; `test_an_interrupt_after_the_sheet_unlink_takes_effect_keeps_the_removal` is retargeted to an interrupt after the last owned (content) sheet unlink, so it still pins the keep-the-removal case. A BOM-prefixed content-sheet marker is recognised for both replacement and removal.
- README's Firefox paragraph names `userContent.css`, `chrome/userChrome.css`, `chrome/userContent.css` and the three changes removal reverses; the Makefile comment and `make help` lines name both sheets and both foreign-sheet refusals; the content sheet's header contains "Part 2/2 installs it through make install-firefox." and `test_header_names_provenance` still passes with its `"part 2/2"` string.
- `docs/invariants.md`'s `## firefox` opt-in-install row now says both sheets are copied byte-for-byte, each with its own marker, and that the refusal, adoption, symlink, rollback, interrupt and removal rules apply to either sheet; its test column names the new and extended tests above, every named test exists, and its provenance records that the profile layout, `userContent.css` name and preference are Firefox-required. `tests/invariants.py` stays green.
- `make check` passes, the two shipped sheets are byte-identical to their pre-change content except the one userContent.css header sentence, and `tests/test_firefox_theme.py` and `tests/test_firefox_content_theme.py`'s paint and palette assertions are unchanged.

## Done

# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
collapse boxes); the desktop wallpaper package; the `org.macos8.desktop` icon theme (our own
final, non-infringing 32x32 Platinum-style art for the desktop's hard-disk, folder, document,
Trash and full-Trash icons, plus the menu bar's kicker logo `start-here-kde-symbolic` and the
`go-next-symbolic` submenu arrow, our own marks rather than Apple's; `PLACEHOLDERS.md` is empty);
the `org.macos8.desktop` Kvantum widget style (Platinum palette and core-control art); the
`org.macos8.desktop` Lato font package (Lato Regular and Bold, the Debian copyright file
carrying the upstream SIL OFL 1.1 body, and the provenance record; installed by `make install`
but not yet selected); the GTK 3 and GTK 4 Platinum stylesheets under `theme/gtk/` (not yet
installable; part 3/4 is planned below); and the render and fidelity tooling
that checks them against `macos8.6-screenshots/`. README.md describes the reference set as the
source of truth for "menu bar, window chrome, widget metrics, icons and colour palette". The
prompt's surfaces the theme does not ship are each tracked here (updated 2026-10-21 by the
steward role): a **Qt widget style** for KDE applications (the desktop theme styles only
Plasma shell widgets, so a KDE app's own buttons, menus and scroll bars would keep the Breeze look) is served
by the global theme's selection of our Kvantum theme: the user answered
2026-10-18 that a pixel-matched Platinum style should ship as a Kvantum theme (a new
dependency) — shipped as the four-part "Mac OS 8.6 Kvantum widget style" series (each part
waited on the one before); a **cursor theme** was out of scope on 2026-10-17 because no reference
screenshot shows a cursor, so no pixel ground truth exists to match; on 2026-10-23 the plan role
queued it anyway as the theme's own Platinum-style art (a black-face, white-outline arrow not
traced from Apple's artwork) with its provenance exception recorded in its entry and
`docs/invariants.md`; **system sounds** are out of scope (not a
visual surface, so the reference set cannot ground them); and a **lock screen** is out of scope
unless a broader login/lock-screen plan is taken up (QUESTIONS.md, answered 2026-10-21). The
shipped work should not be treated as the whole of the prompt.

Two answers on 2026-10-19 widen the scope again, and both now have plan entries in the queue.
**GTK applications and Firefox** are in scope (QUESTIONS.md, answered 2026-10-19) as a
four-part series: parts 1/4 (GTK 3 Platinum theme) and 2/4 (GTK 4/libadwaita stylesheet) have
landed; part 3/4 is queued as three entries — the opt-in install (parts 1/3 and 2/3) and,
blocked on them, the selection (part 3/3) — and part 4/4 is split into two runs: part 1/2 (the
Firefox `userChrome.css` stylesheet) is queued below and part 2/2 (the profile install plus the
preference) is not planned yet. **The UI font** is to be vendored
(QUESTIONS.md, answered 2026-10-19) as a three-part series: part 1/3 vendors Lato as the
Charcoal-style body face and has landed (installed but not yet selected); part 2/3 (a
Chicago-style menu face, whose redistribution licence is still unresolved) is not planned
yet; and part 3/3 (selecting the installed family in KDE/Plasma/Qt) is queued as one entry,
the Lato body face only, because Lato is the only family the package installs. Until part
3/3 lands, KDE, Plasma and Qt applications keep the user's own font; GTK and Firefox
applications keep their own chrome regardless (the queued GTK entries cover GTK, and
Firefox chrome is part 1/2 below).

### Platinum cursor theme, part 3/3: Generate and ship the Xcursor arrow cursor artifact (planned 2026-10-23 by the plan role; "requires part 2/3 landed")

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
X/KDE-required values the reference set does not show. Record that provenance exception in
`docs/invariants.md`. Xcursor files have no image extension, so Git LFS (`.gitattributes`) is
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
  decodes with `read_rgba` and its width/height equal its nominal size; the 16px frame's hotspot is
  (1,1) and its tip pixel (1,1) is opaque `#000000`, the outline corner (0,0) opaque `#FFFFFF`, and
  (15,15) transparent (alpha 0); the committed `arrow`, `default` and `top_left_arrow` are
  byte-identical to `left_ptr`; and corrupting the grid, dropping a nominal size, or moving the
  hotspot fails the matching assertion (the regression pattern `tests/support/mutant_module.py`
  uses).
- `tests/test_icon_theme.py`: `test_icon_theme_ships_exactly_the_tracked_icons` extends its tracked
  set so the tree holds exactly with the four cursor files added; the SVG-level assertions
  (`test_each_icon_is_a_square_svg_of_its_declared_size`, the palette and pins and
  `test_the_geometry_registry_covers_every_shipped_icon`) take the `suffix=".svg"` filter of
  `tests/support/shipped_files.py`'s `shipped_files(root, suffix=None)` so they keep iterating only
  the icons and do not mistake a binary cursor for an icon. The placeholder register and
  `tests/support/package_metadata.py` stay untouched.
- `README.md`: in the "Installing" section's icon theme sentence, add that the package ships the
  `cursors/` Xcursor arrow (black face, white outline, nominal sizes 16/24/32, X-name aliases
  `arrow`, `default`, `top_left_arrow`) and that nothing selects it yet. Name no make target (none
  exists or is planned) and change no artifact count.
- `docs/invariants.md`: add a `## cursors` section with one row — the arrow draws the black face
  and white outline at nominal sizes 16/24/32 with the hotspot at the tip, and the four files are
  byte-identical apart from their names — pinned to `tests/test_cursors_theme.py`, carrying the
  provenance exception above (this is the standing exception window the cursor series uses; no
  screenshot shows a pointer).

**Files touched.** `tools/make_cursors.py` (new),
`theme/icons/org.macos8.desktop/cursors/` (four new generated files), `tests/test_cursors_theme.py`
(new), `tests/test_icon_theme.py`, `README.md`, `docs/invariants.md`, and `PLANS.md` (the entry
moves to `## Done`; see Plan record). The `Makefile` and `.gitattributes` are untouched; do not
edit `PLANS-DONE.md`.

**Acceptance criteria.**
- `python3 tools/make_cursors.py` writes the four files under
  `theme/icons/org.macos8.desktop/cursors/` deterministically: two runs into one temp directory
  are byte-identical, and the regenerated files equal the committed ones byte for byte.
- The test-side parser (`tests/support/xcursor.py`) accepts the committed `left_ptr` (magic,
  version 65536, three image chunks) and rejects a truncated or hand-corrupted copy; the pinned
  pixels and hotspots hold for all three nominal sizes (scaled accordingly); the aliases are
  byte-identical to `left_ptr`; corrupting the committed file, dropping a nominal size from the
  generator's output or moving the hotspot fails the matching assertion.
- `tests/test_icon_theme.py`'s exact-tree pin holds with the four cursor files (removing one, or
  editing the committed grid's colours, fails the matching test), and every SVG-level icon
  assertion keeps iterating only the icons because of its `suffix=".svg"` filter from
  `tests/support/shipped_files.py`.
- `make check` is green with the new modules included and `tests/invariants.py` accepts the
  `## cursors` row; `git diff --name-status` names only the files listed under "Files touched"
  (besides the backlog move) and neither the `Makefile` nor `PLANS-DONE.md`.
- The entry moves from `## Planned` under `## Done` with its Done stamp, verified on the pre-merge
  working diff: `git diff --name-status` names `PLANS.md` and does not name `PLANS-DONE.md`, and
  `grep -n '^## ' PLANS.md` prints exactly `## Planned` and `## Done`. No acceptance criterion
  refers to `PLANS.md` or `PLANS-DONE.md` after the merge.

### Firefox Platinum chrome, part 1/2: Ship the `userChrome.css` stylesheet (planned 2026-10-23 by the plan role; GTK and Firefox series part 4/4, split from the profile install)

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

## Done

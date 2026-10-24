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

### Platinum GTK scroll-bar steppers: paint the reference's arrow boxes and reuse the shipped triangles (planned 2026-10-24 by the plan role; independent of the waiting GTK window-controls plan)

**Goal.** The GTK 3 sheet paints the scroll-bar trough and thumb but names no `scrollbar button` rule, so a non-overlay scroll bar keeps the toolkit's stepper buttons. The reference `setup_emaculation.png` shows a 16px horizontal scroll bar with a 16x16 arrow box at each end: a flat `#EEEEEE` face inside a 1px `#000000` outline, with the arrow glyph centred in it. The desktop theme's `widgets/scrollbar.svg` records that Plasma cannot draw those boxes (`ScrollBar.qml` computes but never uses `arrowPresent`); GTK 3 can, because its steppers are `scrollbar button` nodes whose glyph comes from `-gtk-icon-source`, and they are shown only on a non-overlay scroll bar. Paint them as the reference's arrow boxes using the already-shipped `assets/arrow-up.svg` and `assets/arrow-down.svg`, rotated for the horizontal bar, so no new asset ships and the opt-in install count does not change. GTK 4's installed `Default-light.css` names no `scrollbar button` rule, so the GTK 4 sheet is untouched.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after `scrollbar slider` and before `progressbar trough`, add `scrollbar:not(.overlay-indicator)` with `-GtkScrollbar-has-backward-stepper: true` and `-GtkScrollbar-has-forward-stepper: true`, and `scrollbar.overlay-indicator` with both false. The installed Adwaita GTK 3 sheet sets both properties false globally; this theme turns the reference's boxes back on for a normal scroll bar and keeps an overlay scroll bar slider-only.
- Add `scrollbar button` with `background-color: #EEEEEE`, `background-image: none`, `border: 0`, `border-radius: 0`, `box-shadow: inset 0 0 0 1px #000000`, `min-height: 16px`, `min-width: 16px` and `padding: 0`. The inset ring gives the reference's 16px box a 1px outline without adding border width, so the 16x16 glyph fits the 16px box. Add `scrollbar button:hover` with `background-color: #EEEEEE` and `scrollbar button:active` with `background-color: #EEEEEE` and the inverted `inset 0 0 0 1px #000000, inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` bevel; the scoped selectors outrank the generic `button`, `button:hover` and `button:active` rules, so a stepper does not become a grey push button.
- Add the four direction rules: `scrollbar.vertical button.up` with `-gtk-icon-source: url("../assets/arrow-up.svg")`; `scrollbar.vertical button.down` with the down asset; `scrollbar.horizontal button.up` with the up asset and `-gtk-icon-transform: rotate(-0.25turn)`; `scrollbar.horizontal button.down` with the down asset and the same transform. GTK names the horizontal steppers `.up`/`.down` (start/end), so the counter-clockwise quarter turn points the up triangle left and the down triangle right. `-gtk-icon-transform` is the property the installed Adwaita sheet uses on its icon-source check and radio glyphs.
- Extend the sheet's header provenance paragraph to name the stepper rules, the reference's 16px arrow box, the reused `widgets/arrows.svg` triangles, the normal/overlay stepper switch, and the two details this sheet does not reproduce: the reference's mid-grey divider between the box and the trough (no pinned palette value) and its grey disabled glyph (a URL icon is a fixed fill; the shipped triangle stays black when disabled).
- `tests/support/gtk_theme_spec.py`: add `SCROLLBAR_STEPPER` (the base declarations), `SCROLLBAR_STEPPER_ACTIVE` (the active box-shadow) and `SCROLLBAR_STEPPER_ARROWS` (the four selector → icon-source/transform pairs) beside `FRAME`.
- `tests/test_gtk_theme.py`: add `test_scrollbar_steppers` to `TestGtkTheme`, next to `test_scrollbar`; assert the two stepper-property rules, the base, hover and active button rules, and each of the four direction rules. `test_icon_sources_point_at_shipped_assets` needs no change because the rules reuse the four already-listed URLs.
- `docs/invariants.md`: extend the GTK 3 `## gtk` control row to name the scroll-bar steppers: a normal scroll bar shows the reference's 16px `#EEEEEE` arrow boxes with the shipped up/down triangles, an overlay scroll bar keeps no steppers, the box and overlay/normal property names are GTK-required, and the reference's `#555555` divider and grey disabled glyph are not reproduced.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `docs/invariants.md`. No asset, `Makefile`, README or GTK 4 sheet change: the steppers reuse the two shipped arrow assets.

**Acceptance criteria.**
- The GTK 3 sheet's `scrollbar:not(.overlay-indicator)` sets both stepper properties true and its `scrollbar.overlay-indicator` sets both false; `scrollbar button` carries the `#EEEEEE` face, the 1px `#000000` inset ring, square corners, no border and the 16px minimum; hover keeps the face and active uses the inverted bevel.
- The four direction rules point vertical up/down at `arrow-up.svg`/`arrow-down.svg` and horizontal up/down at the same two assets with `rotate(-0.25turn)`; the sheet's `url(...)` set is still exactly the four shipped asset paths, and no new hex literal appears in the sheet.
- `TestGtkTheme::test_scrollbar_steppers` passes, the GTK 4 suite is unchanged, the updated `## gtk` invariant row is accepted by `tests/invariants.py`, and `make check` is green.

### Platinum GTK headerbars: floor the title bar at the reference's 22px and paint the inactive frame (planned 2026-10-24 by the plan role; independent of the waiting GTK scroll-bar stepper plan)

**Goal.** Both GTK sheets paint the headerbar face and border but leave its height and backdrop state to the toolkit. The installed Adwaita GTK 3 sheet floors every `headerbar` at `min-height: 46px`, and its `headerbar:backdrop` rule paints a `#f6f5f4` face with a white inset shadow, so a GTK 3 client-side title bar is more than twice the reference's 22px `TitleHeight` and its unfocused state is Adwaita's, not Platinum. The reference derives a 22px title bar from `aboutsystem_betawiki.png` (`tests/test_aurorae_rc.py::test_layout_metrics_match_reference`) and a flat inactive frame from the four unfocused windows in `desktop_fandom.png` (`tests/test_aurorae_frame.py`, a `#DDDDDD` field with a `#555555` outer outline), while the Aurorae rc keeps `InactiveTextColor=153,153,153`. Floor both sheets' `headerbar`/`.titlebar` at that 22px title height with the reference's 4px title edge, and give the inactive state the reference's grey field, outline and title text. No reference screenshot shows a GTK widget, so this is the same adaptation the shipped GTK rules already make from the reference-grounded Aurorae art.

**Approach.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: in the existing `headerbar, .titlebar` rule add `padding: 0 4px` and `min-height: 22px`. The 22px is the Aurorae `TitleHeight`; the 4px side padding is the Aurorae `TitleEdgeLeft`/`TitleEdgeRight` value, and the existing title-button rules already set `margin: 0` with a 16px minimum, so the 13px boxes centre in the 22px bar. The declarations are a floor, not a cap: a headerbar carrying a taller child still grows, which is this theme's adaptation.
- Immediately after the existing `headerbar { border-width: 0 0 1px 0; }` rule in each sheet, add `headerbar:backdrop, .titlebar:backdrop` with `background-color: #DDDDDD`, `background-image: none`, `border-color: #555555`, `box-shadow: none` and `color: #999999`. This outranks the toolkit's backdrop face and inset shadow and matches the reference's unfocused window: the `#555555` outline re-derived from `desktop_fandom.png` and the rc's `InactiveTextColor` for the title text. Leave the title-button backdrop rules as they are; the landed rules already keep the boxes transparent in backdrop.
- `tests/support/platinum_palette.py`: add `INACTIVE_OUTLINE = "#555555"` with a comment recording that the inactive Aurorae frame re-derives it from `desktop_fandom.png` (the "Mac OS 8.6" window's outer outline, x=25 and y=57) via `tests/test_aurorae_frame.py`.
- `tests/support/gtk_theme_spec.py`: in the shared `GtkSheetRuleCases.test_headerbar`, assert `min-height: 22px` and `padding: 0 4px` on both `headerbar` and `.titlebar`, and add a loop over `headerbar:backdrop` and `.titlebar:backdrop` asserting the `#DDDDDD` face, `#555555` border, `#999999` text, `background-image: none` and `box-shadow: none`. Import `INACTIVE_OUTLINE` beside the existing palette names.
- `tests/test_gtk_theme.py` and `tests/test_gtk4_theme.py`: add `INACTIVE_OUTLINE` to the palette set in each `test_only_palette_hex_literals`; the GTK 3 case scans the raw sheet, comments included, so the provenance comment's literal is covered too.
- Extend each sheet's header provenance paragraph to name the 22px headerbar (Aurorae `TitleHeight`), the 4px title edge, the inactive `#DDDDDD`/`#555555`/`#999999` backdrop, and the GTK-required headerbar/backdrop node names.
- `docs/invariants.md`: extend both GTK rows (GTK 3 and GTK 4) to name the headerbar floor, the 4px title edge and the inactive backdrop, and add the provenance exception that no reference screenshot shows a GTK widget while the height, outline and title colour copy the reference-grounded Aurorae copy.

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/support/platinum_palette.py`, `tests/support/gtk_theme_spec.py`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`. No asset, `Makefile` or README change.

**Acceptance criteria.**
- Both sheets' `headerbar, .titlebar` rule carries `padding: 0 4px` and `min-height: 22px`; `headerbar` keeps its bottom-only 1px border; both `headerbar:backdrop` and `.titlebar:backdrop` carry the `#DDDDDD` face, `#555555` border, `#999999` text, no background image and no box shadow.
- The shared `GtkSheetRuleCases.test_headerbar` passes for both suites, `test_only_palette_hex_literals` in both suites accepts `#555555`, the updated GTK 3 and GTK 4 invariant rows are accepted by `tests/invariants.py`, and `make check` is green.

### Retire the `no-repro` validation gap with a deterministic-reproduction ledger (planned 2026-10-24 by the steward role; promotes the recurring `gap: no-repro` tag, 3 Fixed entries)

**Goal.** Three Fixed entries in BUGS-FIXED.md carry `gap: no-repro` — confirming the failure was not deterministic when the bug was filed. Each fix now has a test that reproduces the failure deterministically: the cursor write-failure test patches the imported `write_bytes_atomically` helper the generator actually calls, the `CHECK_PATTERN` whitespace test pins the stripped glob the recipe now runs, and the desktop-theme test plants a session-theme `plasmarc` in an isolated `XDG_CONFIG_DIRS`. Add the fifth validation-gap ledger, mirroring the `no-observability`, `unclear-invariant`, `no-fake` and `real-run-needed` ones, so every record names the test that now confirms it deterministically and the suite refuses a new uncovered `no-repro` record instead of letting the tag grow.

**Cited entries.** The three `gap: no-repro` records in BUGS-FIXED.md:
- `` `The cursor generator test patches a removed `_write_atomic` symbol` `` (line 411) — `tests/test_cursors_theme.py::TestMainErrors::test_reports_a_failed_write_and_stops_at_that_cursor` patches the shared atomic-write helper the cursor generator imports and calls.
- `` `make check`'s `CHECK_PATTERN` guard accepts a pattern with surrounding whitespace that then matches no test module `` (line 1260) — `tests/test_make_check.py::TestCheckPattern::test_surrounding_whitespace_pattern_is_stripped` runs the trimmed glob through the project's own check.
- `` `tests/test_desktoptheme.py::TestApplyDesktopTheme` fails when `XDG_CONFIG_DIRS` already names a session theme `` (line 1335) — `tests/test_desktoptheme.py::TestApplyDesktopTheme::test_apply_ignores_a_session_theme_in_the_config_search_path` plants the session-theme `plasmarc` so the failure no longer depends on the developer's ambient config.

**Approach.**
- `tests/support/validation_gaps.py`: add `NO_REPRO_BASELINE = 3` and `NO_REPRO_REPRODUCTIONS` with one `Reproduction` per cited entry (markers that match the record subject and the test reference above); add `no_repro(records)` and `no_repro_reproduction(record)`; dispatch `no-repro` in `reproduction_for` and name the five ledgers in its docstring. Update the module docstring from four ledgers to five and describe the tag: a failure that was not deterministic when filed and now names the test that makes it deterministic.
- `tests/test_validation_gaps.py`: add `TestNoReproLedger` mirroring `TestRealRunNeededLedger`, with `test_every_record_names_a_reproduction`, `test_every_entry_names_a_real_test`, `test_every_ledger_entry_covers_a_shipped_record`, `test_the_record_count_does_not_grow` and `test_an_unmatched_mechanism_has_no_reproduction`; update the module docstring to five ledgers.
- `docs/invariants.md`: extend the tooling row that names the four existing ledgers to name the `no-repro` ledger and `tests/test_validation_gaps.py::TestNoReproLedger`.

**Files touched.** `tests/support/validation_gaps.py`, `tests/test_validation_gaps.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The task's gap query over BUGS.md and BUGS-FIXED.md returns the 3 `no-repro` records; each maps to a `NO_REPRO_REPRODUCTIONS` entry and each entry covers a shipped record.
- Every cited test resolves through `check_reference`; a new `no-repro` record without an entry, or a count above 3, fails the suite.
- The updated tooling row is accepted by `tests/invariants.py`, and `make check` is green.

## Done

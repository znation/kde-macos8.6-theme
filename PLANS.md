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

### Platinum GTK mixed check boxes: draw an inconsistent check box or radio as a 2px black dash in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover submenu-arrow plan)

**Goal.** Both GTK sheets give `check:checked` and `radio:checked` a shipped glyph, but neither names `:indeterminate`. So a check button in the mixed state (`set_inconsistent(True)`, for example a "select all" box over a partial selection) draws GTK's builtin dash, not a Platinum one. I measured this live under `GDK_BACKEND=x11` (DISPLAY=:1), loading each sheet with its asset URLs rewritten to absolute paths:
- GTK 3 (`Gtk.OffscreenWindow.get_pixbuf` of a `Gtk.CheckButton` with `set_inconsistent(True)`): the 14px `#DDDDDD` face shows a broken builtin dash of three separate 2x2 black squares.
- GTK 4 (`Gtk.WidgetPaintable` of the `check` indicator node rendered to a texture): the builtin dash is drawn near-white (`#FFFFFF`/`#FBFBFB`) on rows 6–7 of the 16px indicator texture. So it is faint on the grey check face and invisible on the white radio face.
- With the candidate asset and rule below appended to a copy of each sheet, the check and the radio both show a solid `#000000` dash 8px wide and 2px tall, centred in the 14px glyph area (canvas columns 3–10, rows 6–7). In GTK 3 the dash also wins over `check:checked` when the button is both active and inconsistent, because the rule comes later in the sheet at equal specificity.

**Design (decided; do not widen).**
- New asset `theme/gtk/org.macos8.desktop/assets/check-mixed.svg`. It is a 14x14 canvas like `checkmark.svg`, with the root element first and a comment after it (see the earlier BUGS-FIXED entry about an SVG comment before the root). It holds a single path: `<path d="M 4,7 L 10,7" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="square"/>`. The comment names its provenance: the 2px square-capped black stroke reuses `checkmark.svg`'s stroke, which is adapted from the desktop theme's `widgets/checkmarks.svg`. No reference screenshot shows a mixed-state control, and GTK requires the `:indeterminate` state.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: directly after the `radio:checked` rule, add `check:indeterminate, radio:indeterminate { -gtk-icon-source: url("../assets/check-mixed.svg"); }`. It must come after both `:checked` rules. In each header comment, extend the sentence about the checked glyphs: a mixed (indeterminate) check box or radio loads the shared `assets/check-mixed.svg` dash.
- Out of scope:
  - Menu and popover-row indeterminate checks: their rules stay unchanged, and the new rule applies wherever it matches.
  - The Kvantum (Qt) tristate check box: no Qt bindings are installed to measure it.
  - `:disabled` or `:backdrop` variants.
- Install plumbing for the new tenth asset. Mirror every place `bullet.svg` appears:
  - `Makefile`: the `install-gtk` staging trap, the `install -Dm644`, the `mv`, and the uninstall `rm -f`. That is the four `bullet.svg` occurrences, each with its `.check-mixed.svg.staging` counterpart.
  - `tests/support/gtk_fixtures.py` `SHIPPED_FILES`.
  - `tests/test_gtk_install.py` `STAGING_PATHS`.
  - README: "the nine shared check, radio, …" becomes ten and names the mixed-state dash; both "twelve GTK files" / "twelve opt-in GTK files" become thirteen.
  - `docs/invariants.md`: the GTK install row's "twelve GTK theme files" becomes thirteen.

**Files touched.**
- `theme/gtk/org.macos8.desktop/assets/check-mixed.svg` (new).
- Both GTK sheets: the rule and the header sentence.
- `tests/support/gtk_theme_spec.py`: add `MIXED_GLYPH = {"-gtk-icon-source": 'url("../assets/check-mixed.svg")'}` beside `RADIO_GLYPH`. In `GtkSheetRuleCases.test_check_and_radio`, add `self.assert_rule("check:indeterminate, radio:indeterminate", MIXED_GLYPH)`. First check how `parse_css` keys a selector list (by the full list or by each selector) and use that key form.
- `tests/test_gtk_theme.py`:
  - Add `CHECK_MIXED` beside `BULLET`.
  - Add `'"../assets/check-mixed.svg"'` to `test_icon_sources_point_at_shipped_assets`.
  - In `TestCheckGlyphs`, include the new tree in `test_assets_stand_alone`, `test_assets_put_the_root_first`, `test_assets_span_a_14px_canvas` and `test_assets_use_only_the_two_glyph_fills`, and add `test_mixed_geometry`. It pins the single path's `d`, fill `none`, stroke `#000000`, stroke-width `2` and square linecap.
  - Add `test_mixed_check_draws_a_black_dash`, modelled on `test_entry_progress_draws_a_two_pixel_strip`. It renders a `Gtk.CheckButton` with `set_can_focus(False)` and `set_inconsistent(True)` offscreen, with the `../assets/` URLs rewritten to the absolute assets directory instead of `none`, and asserts three things:
    - `#000000` at the dash centre;
    - the `#DDDDDD` face one row above and one row below the dash;
    - `#DDDDDD` at the face column just left of the dash.
    It skips when GTK 3 introspection or a display is missing.
- `tests/test_gtk4_theme.py`: add `'"../assets/check-mixed.svg"'` to its `test_icon_sources_point_at_shipped_assets`.
- `Makefile`, `tests/support/gtk_fixtures.py`, `tests/test_gtk_install.py`, `README.md`: the plumbing above.
- `docs/invariants.md`:
  - The count edit above.
  - A new row at the end of `## gtk`.
    - Guarantee: both GTK sheets draw an indeterminate check box or radio with the shipped `check-mixed.svg` 2px black dash.
    - Tests: `test_check_and_radio` in both suites, `TestCheckGlyphs::test_mixed_geometry`, and the GTK 3 pixel test.
    - Provenance: no reference screenshot shows a mixed-state control. The stroke reuses the reference-grounded check glyph's 2px black stroke. The 8px dash length is this theme's choice, centred on the 14px glyph canvas.

**Acceptance criteria.**
- In either sheet, removing the rule, renaming its selector, or changing its URL fails `test_check_and_radio`. Changing the asset's path data fails `test_mixed_geometry`.
- The GTK 3 pixel test passes against the edited sheet. Repeat the GTK 4 live capture above against the edited sheet: it shows `#000000` on columns 4–11 of rows 7–8 of the 16px check and radio indicator textures.
- `make install-gtk DESTDIR=…`-style tests in `tests/test_gtk_install.py` install, stage and uninstall the new asset. `test_only_palette_hex_literals`, `TestArrowGlyphs` and the rest of both GTK suites still pass. `tests/invariants.py` accepts the edited rows, and `make check` is green.

## Done

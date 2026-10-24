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


### Platinum GTK switches: paint the track and thumb from the desktop theme's switch (planned 2026-10-24 by the plan role; independent of the waiting `no-repro` ledger plan)

**Goal.** Both opt-in GTK sheets are standalone (they import nothing), and neither names a `switch` node, so a `GtkSwitch` gets no track fill, outline or thumb face. Stock GTK styles it in its own sheets, which we never load: the installed GTK 3 Adwaita `gtk-contained.css` (in the `libgtk-3.so.0` gresource) has `switch`, `switch:checked`, `switch:disabled`, `switch slider` and `switch image { color: transparent; }`, and GTK 4's `Default/Default-light.css` has `switch`, `switch:checked`, `switch:disabled`, `switch > slider` and `switch:disabled > slider`, with no rule hiding the I/O `image` glyphs. Paint the switch the way the desktop theme's `widgets/switch.svg` already does (pinned by `tests/test_desktoptheme_switch.py::TestSwitch`): a flat `#EEEEEE` inactive trough with a 1px `#000000` outline, a flat `#FFFFFF` active field, and the raised `#DDDDDD` slider thumb with no glyph. No new colours are needed.

**Approach.**
- `tests/support/gtk_theme_spec.py`: next to the scale constants add `SWITCH_TRACK = {"background-color": TROUGH, "background-image": "none", "border": f"1px solid {BLACK}", "border-radius": "0", "box-shadow": "none", "min-width": "30px", "min-height": "16px"}` (the 30x16 `hint-bar-size` track in `switch.svg`), `SWITCH_TRACK_CHECKED = {"background-color": WHITE, "background-image": "none"}`, `SWITCH_TRACK_DISABLED = {"border-color": GREY}`, `SWITCH_THUMB = {**SCALE_THUMB, "margin": "-1px", "min-width": "12px", "min-height": "16px"}` (the 12px thumb width, its outline laid over the track's), `SWITCH_THUMB_DISABLED` with the same three declarations `assert_scale` gives a disabled scale thumb (`#DDDDDD` face, `1px solid #999999` border, `box-shadow: none`), and `SWITCH_GLYPH = {"color": "transparent"}`. Add `GtkSheetRuleCases.assert_switch(self, slider, disabled_slider, glyph)`, modelled on `assert_scale`: it asserts `switch`, `switch:checked` and `switch:disabled` against the three track constants, then the suite's slider, disabled-slider and glyph selectors. Name the switch in the module and class docstrings next to the scale.
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: after `scale slider:disabled` add `switch`, `switch:checked`, `switch:disabled`, `switch slider`, `switch:disabled slider` and `switch image` carrying exactly those declarations. In the header comment, say the switch reuses `widgets/switch.svg`'s faces, that GTK splits the track between the two states so the thumb's drawn width is GTK's layout rather than the 12px floor, and that the node names and the hidden I/O glyphs are GTK-required.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: the same rules with the child selectors `switch > slider`, `switch:disabled > slider` and `switch > image`, after `scale > trough > slider:disabled`, plus the same header-comment sentence.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_switch` calls `self.assert_switch(slider="switch slider", disabled_slider="switch:disabled slider", glyph="switch image")`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_switch` calls it with `switch > slider`, `switch:disabled > slider` and `switch > image`.
- `docs/invariants.md`: in both `## gtk` rows (GTK 3 and GTK 4), extend the guarantee sentence to name the switch track and thumb. In the provenance cell, add that the switch reuses the `widgets/switch.svg` faces (the `#EEEEEE` trough, the `#FFFFFF` active field and the raised `#DDDDDD` thumb), whose shape is KDE-required provenance with no reference screenshot, and that the switch node names and hidden glyphs are GTK-required.

**Files touched.** `tests/support/gtk_theme_spec.py`, `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- Both sheets carry the six switch rules with exactly the shared spec's declarations, and `test_switch` in each suite asserts them through `assert_switch`. Removing any one declaration fails that suite.
- `test_only_palette_hex_literals` in both suites passes with its expected set unchanged: the switch adds no hex literal outside the existing palette.
- Both updated `## gtk` invariant rows are accepted by `tests/invariants.py`, and `make check` is green.

## Done

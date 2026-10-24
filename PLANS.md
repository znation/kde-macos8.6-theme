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

### Platinum GTK disabled text: grey the labels and entry text of insensitive widgets (planned 2026-10-24 by the plan role; independent of the waiting GTK rubberband plan)

**Goal.** Neither standalone GTK sheet greys the text of an insensitive widget, so a disabled button, check box, menu item, entry or spin button reads exactly like an enabled one. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): after `set_sensitive(False)`, a GTK 3 `Gtk.Label`, `Gtk.Button`, `Gtk.Entry`, `Gtk.CheckButton` and `Gtk.SpinButton` all resolve `get_color()` to `rgb(0,0,0)`, and in GTK 4 the `Label` child of a `Gtk.Button` or `Gtk.CheckButton`, and the `Text` child of a `Gtk.Entry` or `Gtk.SpinButton`, are also `rgb(0,0,0)`. Stock Adwaita greys them (`rgb(146,149,149)`). The KDE side already greys disabled text with `#888888`: the colour scheme's `ForegroundInactive=136,136,136` and Kvantum's `disabled.text.color`, which `COLOR_ROLES` in `tests/support/kvantum_config_spec.py` pins to `("Button", "ForegroundInactive")`. With the rules below appended to scratch copies of both sheets, the same check gives `rgb(136,136,136)` for each of those labels and text nodes (GTK 3 also greys a disabled `Gtk.MenuBar` item's label) and `rgb(0,0,0)` once they are sensitive again.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: append `label:disabled, entry:disabled, spinbutton:disabled { color: #888888; }` at the end of the sheet. Insensitivity reaches child nodes, so `label:disabled` covers the labels of buttons, check and radio buttons and menu items.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: append `label:disabled, text:disabled { color: #888888; }` at the end of the sheet. `text` is the editable node inside GTK 4 entries and spin buttons.
- Colour only. Do not use `*:disabled`: it would also reach `switch image`, whose transparent colour hides the switch glyph. Out of scope: disabled faces, borders and glyph assets (a URL icon's fill is fixed, as the GTK 3 header comment already says), and `:backdrop`.
- No new hex literal: `#888888` is already in both palettes as `ETCH_DARK`.

**Files touched.**
- Both sheets: the rule above. Add one sentence to each header comment: an insensitive widget's label and entry text use the colour scheme's `ForegroundInactive` grey `#888888`, which Kvantum's disabled text also uses; no reference screenshot shows a disabled GTK widget, and the node names and `:disabled` state are GTK-required.
- `tests/support/gtk_theme_spec.py`: add `DISABLED_TEXT = {"color": ETCH_DARK}` with a short comment, and an `assert_disabled_text(self, selectors)` method in `GtkSheetRuleCases` next to `assert_view_background`. It calls `assert_rule` for each selector. It also re-derives the grey: `hex_colour` of the `int` parts of `load_scheme().get("Colors:Button", "ForegroundInactive")` (`load_scheme` from `support.colorscheme_fixtures`, `hex_colour` from `support.platinum_palette`) must equal `DISABLED_TEXT["color"]`. Mention the disabled-text assertion in the class docstring's list of assertions that take the suite's own selectors.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_disabled_text` calls `self.assert_disabled_text(("label:disabled", "entry:disabled", "spinbutton:disabled"))`.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_disabled_text` calls `self.assert_disabled_text(("label:disabled", "text:disabled"))`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets colour an insensitive widget's labels and entry text with the colour scheme's `ForegroundInactive` grey `#888888`. Tests: the two `test_disabled_text` tests. Provenance exception: no reference screenshot shows a disabled GTK widget; the grey copies the colour scheme's `ForegroundInactive` role (also Kvantum's disabled text), whose value matches the reference-sampled etched-rule dark `#888888`, and the node names and `:disabled` state are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet has the `label:disabled, entry:disabled, spinbutton:disabled` rule and the GTK 4 sheet has the `label:disabled, text:disabled` rule, each with only the `color: #888888` declaration.
- Removing either rule, dropping one of its selectors or changing its colour fails that sheet's `test_disabled_text`. Changing the colour scheme's `[Colors:Button] ForegroundInactive` alone also fails both tests.
- `test_only_palette_hex_literals` still passes in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

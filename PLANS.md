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

### Platinum GTK links: colour link text with the scheme's link blue and visited purple, and drop the GTK 3 link-button face (planned 2026-10-24 by the plan role; independent of the waiting GTK disabled-text plan)

**Goal.** Neither standalone GTK sheet styles links. Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir holding a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`), inside a `Gtk.Window`: a GTK 3 and a GTK 4 `Gtk.LinkButton` both resolve their text to `rgb(0,0,0)`, the same as a plain label. The GTK 3 link button also gets the full Platinum push-button face from the `button` rule: `background-color` `rgb(221,221,221)` and a 1px solid border. So a link looks like ordinary text or like a button. Stock Adwaita colours links `rgb(27,106,203)` (visited `rgb(21,83,158)`) and draws no face. The KDE side already has link colours: the colour scheme's `ForegroundLink=0,0,238` and `ForegroundVisited=85,26,139`, which Kvantum copies as `link.color=#0000EE` and `link.visited.color=#551A8B`. `COLOR_ROLES` in `tests/support/kvantum_config_spec.py` pins those two to `("Window", "ForegroundLink")` and `("Window", "ForegroundVisited")`. With the rules below appended to scratch copies of both sheets, the same check gives this. GTK 3 link button: `background-color` and `border-top-color` `rgba(0,0,0,0)` when normal and when hovered and active; label `rgb(0,0,238)`, then `rgb(85,26,139)` after `set_visited(True)`. GTK 3 `Gtk.Label` with `<a>` markup: `rgb(0,0,238)` for the `LINK` state and `rgb(85,26,139)` for `VISITED`. GTK 4 link button label: `rgb(0,0,238)`, then `rgb(85,26,139)` once visited. Plain labels and plain-button labels stay `rgb(0,0,0)`, and a plain GTK 3 button keeps its `rgb(221,221,221)` face. The GTK 4 `link` node inside a label is not a widget, so it was not measured live; the rule test pins it.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: append at the end of the sheet:
  `button:link, button:visited { background-color: transparent; background-image: none; border-color: transparent; box-shadow: none; }`,
  `label:link, button:link > label { color: #0000EE; text-decoration-line: underline; }` and
  `label:visited, button:visited > label { color: #551A8B; }`.
  These come after `button`, `button:hover` and `button:active, button:checked`, and have the same specificity, so they win by order.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: append at the end of the sheet:
  `button.link { background-color: transparent; background-image: none; border-color: transparent; box-shadow: none; }`,
  `link, button.link > label { color: #0000EE; text-decoration: underline; }` and
  `link:visited, button.link:visited > label { color: #551A8B; }`.
- If the disabled-text plan has landed by then, still append these rules after its rule. Out of scope: greying an insensitive link, hover and active link colours, `:selected` links, `:backdrop`, and the Firefox sheet. Do not use `*:link`: each suite's `test_no_universal_selector` forbids `*`.
- New hex literals: `#0000EE` and `#551A8B`.

**Files touched.**
- Both sheets: the rules above. Add one sentence to each header comment: links use the colour scheme's `ForegroundLink` blue `#0000EE` and `ForegroundVisited` purple `#551A8B` (Kvantum's link colours too), and a link button draws no button face; no reference screenshot shows a GTK link, and the node names and `:link`/`:visited` states are GTK-required.
- `tests/support/gtk_theme_spec.py`: add `LINK = "#0000EE"` and `VISITED_LINK = "#551A8B"` next to `ETCH_DARK`, with a comment naming the scheme roles. Add the rule dicts `LINK_BUTTON = {"background-color": "transparent", "background-image": "none", "border-color": "transparent", "box-shadow": "none"}`, `LINK_TEXT = {"color": LINK}` and `VISITED_TEXT = {"color": VISITED_LINK}`. The underline is not in `LINK_TEXT` because the property name differs per toolkit. Then add an `assert_links(self, button, link, visited, underline)` method in `GtkSheetRuleCases` next to `assert_rubberband`:
  - `button` is the link-button selectors. Each must match `LINK_BUTTON`.
  - `link` is the link-text selectors. Each must match `{**LINK_TEXT, **underline}`.
  - `visited` is the visited-text selectors. Each must match `VISITED_TEXT`.
  - It re-derives both colours from the scheme: `hex_colour` of the `int` parts of `load_scheme().get("Colors:Window", "ForegroundLink")` (and of `"ForegroundVisited"`) must equal `LINK` (and `VISITED_LINK`). `load_scheme` comes from `support.colorscheme_fixtures`.
  - Mention the link assertion in the module docstring's list of assertions that take the suites' own selectors.
- `tests/test_gtk_theme.py`: add `LINK` and `VISITED_LINK` to the `test_only_palette_hex_literals` palette set. Add `TestGtkTheme.test_links`, which calls `self.assert_links(("button:link", "button:visited"), ("label:link", "button:link > label"), ("label:visited", "button:visited > label"), {"text-decoration-line": "underline"})`.
- `tests/test_gtk4_theme.py`: add the same two constants to its `test_only_palette_hex_literals` set. Add `TestGtk4Theme.test_links`, which calls `self.assert_links(("button.link",), ("link", "button.link > label"), ("link:visited", "button.link:visited > label"), {"text-decoration": "underline"})`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets colour link text with the colour scheme's `ForegroundLink` `#0000EE` (underlined) and visited links with `ForegroundVisited` `#551A8B`, and draw link buttons without a face. Tests: the two `test_links` tests. Provenance exception: no reference screenshot shows a link; the colours copy the colour scheme's link roles (Kvantum's link colours too), and the node names and states are GTK-required.

**Acceptance criteria.**
- Both sheets have the three rules above, with exactly the declarations listed.
- Each of these fails that sheet's `test_links`: removing any of the three rules, dropping one of their selectors, or changing a colour or the underline. Changing `[Colors:Window] ForegroundLink` or `ForegroundVisited` in the colour scheme alone fails both suites' `test_links`.
- `test_only_palette_hex_literals` and `test_no_universal_selector` still pass in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

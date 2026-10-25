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

### Platinum GTK spinners: draw a running `GtkSpinner` and hide a stopped one in GTK 3 and GTK 4 (planned 2026-10-24 by the plan role; independent of the waiting GTK 3 popover-row highlight plan)

**Goal.** Neither GTK sheet names `spinner` (grep finds no `spinner` and no `@keyframes` in `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` or `gtk-4.0/gtk.css`). The stock spinner rules live in Adwaita's `gtk-contained.css` (GTK 3) and in GTK 4's `Default-light.css`. Our standalone sheets never load either file, so a `GtkSpinner` loses them.

I measured this live with PyGObject under `GTK_THEME=org.macos8.desktop`, with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to the absolute `theme/gtk/org.macos8.desktop` path.
- GTK 4: a started 16x16 `Gtk.Spinner` in a presented `Gtk.Window` renders nothing. Its `Gtk.WidgetPaintable` snapshot `to_node()` is `None`. With the GTK 4 rules below appended to a `cp -rL` copy of the theme, it renders a `GskMaskNode` with 122 non-transparent pixels. Under `GTK_THEME=Adwaita` it renders 112.
- GTK 3: a stopped spinner's `get_style_context().get_property("opacity", state)` is `1.0` today. With the GTK 3 rules appended it is `0.0`, and a started (`CHECKED`) spinner stays at `1.0`. GTK 3 pixels cannot be measured on this machine, so only the CSS side of GTK 3 is verified.

**Design (decided; do not widen).** Both sheets copy the stock spinner rules. The only difference is the transform property inside the keyframes, which the two toolkits spell differently.
- `gtk-3.0/gtk.css`: directly after the `levelbar.vertical block` rule, add:
  ```css
  @keyframes spin { to { -gtk-icon-transform: rotate(1turn); } }
  spinner { background: none; opacity: 0; -gtk-icon-source: -gtk-icontheme("process-working-symbolic"); }
  spinner:checked { opacity: 1; animation: spin 1s linear infinite; }
  spinner:checked:disabled { opacity: 0.5; }
  ```
- `gtk-4.0/gtk.css`: directly after the `levelbar.vertical > trough > block` rule, add the same four rules, except that the keyframe reads `to { transform: rotate(1turn); }`. That is GTK 4's own spelling in `Default-light.css`.
- Format the rules multi-line, as in the rest of each sheet. Values stay exactly as above.
- The icon comes from the user's icon theme via the GTK-required `process-working-symbolic` name. Our icon theme does not ship that name, so it resolves through the `Inherits` chain (Breeze on KDE). No new asset is added, so the Makefile, `SHIPPED_FILES`, `STAGING_PATHS` and the README asset counts do not change.
- Out of scope:
  - A Platinum spinner asset, such as a GTK copy of the desktop theme's `widgets/busywidget.svg` ring. That would need a new shipped asset plus install and uninstall changes.
  - A `spinner:backdrop` colour.
- No reference screenshot shows a GTK spinner or any busy indicator other than the watch cursor. The rules add no colour or metric. Say so in each sheet's header comment, in one sentence: a spinner shows the icon theme's `process-working-symbolic` while it runs and is hidden while stopped.

**Files touched.**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` and `gtk-4.0/gtk.css`: the rules and the header sentence.
- `tests/support/gtk_theme_spec.py`:
  - Add a `SPINNER_RULES` dict mapping `"spinner"`, `"spinner:checked"` and `"spinner:checked:disabled"` to the declarations above. Values are whitespace-normalised, as `parse_css` stores them, e.g. `"-gtk-icon-source": '-gtk-icontheme("process-working-symbolic")'`.
  - Add a `GtkSheetRuleCases.assert_spinner(self, transform)` helper. It calls `assert_rule` for each `SPINNER_RULES` entry. It also asserts that `gtk_css.strip_comments(self.css)` matches `@keyframes\s+spin\s*\{\s*to\s*\{\s*<transform>\s*:\s*rotate\(1turn\)\s*;?\s*\}\s*\}`, with the property name passed through `re.escape`.
  - Check the regex against the raw text, not `self.rules`: `parse_css` files a nested keyframe block under a bare `to` selector.
  - Add "spinner" to the module docstring's list of shared assertions.
- `tests/test_gtk_theme.py`: add `TestGtkTheme.test_spinner`, which calls `self.assert_spinner("-gtk-icon-transform")`.
- `tests/test_gtk4_theme.py`: add `TestGtk4Theme.test_spinner`, which calls `self.assert_spinner("transform")`.
- `docs/invariants.md`: add one row at the end of the `## gtk` section.
  - Guarantee: the GTK 3 and GTK 4 sheets show a running spinner as the icon theme's `process-working-symbolic`, rotating once per second, and hide a stopped one.
  - Tests: both `test_spinner` methods.
  - Provenance: no reference screenshot shows a GTK spinner. The icon name, states and animation are GTK-required, copied from the toolkits' stock sheets, and add no colour or metric.

**Acceptance criteria.**
- Both sheets carry the four rules exactly as described, with each toolkit's own keyframe property.
- Each of these fails the matching `test_spinner`:
  - deleting any of the four rules;
  - changing `opacity: 0` or the `-gtk-icon-source` value;
  - spelling the GTK 3 keyframe with `transform`, or the GTK 4 keyframe with `-gtk-icon-transform`.
- `test_stands_alone` (GTK 4), `test_icon_sources_point_at_shipped_assets` (GTK 3), `test_only_palette_hex_literals` and the rest of both GTK suites still pass. `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

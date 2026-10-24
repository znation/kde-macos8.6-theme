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

### Platinum GTK rubberbands: draw the drag-selection marquee as a dotted outline with no fill (planned 2026-10-24 by the plan role; independent of the waiting GTK 4 scroll-bar plan)

**Goal.** Neither standalone GTK sheet styles the rubberband, the rectangle a view draws while the pointer drag-selects items (file choosers, icon views, tree views). Measured live with PyGObject under `GTK_THEME=org.macos8.desktop` (with `XDG_DATA_HOME` pointing at a temp dir that holds a `themes/org.macos8.desktop` symlink to `theme/gtk/org.macos8.desktop`): a GTK 3 `Gtk.TreeView` or `Gtk.IconView` style context with the `rubberband` class added resolves `background-color` to opaque `rgb(255,255,255)` (the `.view` rule's white) and `border-top-style` to `none`. So the marquee paints an opaque white block over the items it covers, with no outline. Stock Adwaita gives it a 1px solid border and a 20% alpha fill. The GTK 4 sheet has no rule that matches the `rubberband` child node, so a GTK 4 marquee is invisible. The Mac OS Finder drew its selection marquee as a 1px dotted outline with no fill. With `.rubberband, rubberband { background-color: transparent; border: 1px dotted #000000; }` appended to a scratch copy of the GTK 3 sheet, the same live check gives `rgba(0,0,0,0)`, a 1px border, `rgb(0,0,0)` and `GTK_BORDER_STYLE_DOTTED` for both views. So the rule beats the `.view` white because it comes later at equal specificity.

**Design (decided; do not widen).**
- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`: add `.rubberband, rubberband { background-color: transparent; border: 1px dotted #000000; }` after the `.view, textview text, list` rule. It must come after that rule: GTK 3 tree and icon views draw the marquee with the `.rubberband` class on the view's own `.view` context, and flow boxes and list boxes draw it as a `rubberband` node.
- `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`: add `rubberband { background-color: transparent; border: 1px dotted #000000; }` after the `.view, list` rule. GTK 4 views draw the marquee only as a `rubberband` child node.
- No new colour: black is already in both sheets' palette. Out of scope: `:backdrop`, the GTK 4 text-view selection, and any square-dot pattern art.

**Files touched.**
- Both sheets: the rule above. Add one sentence to each header comment: the drag-selection rubberband is a 1px dotted black outline with no fill, after the Mac OS Finder marquee; no reference screenshot shows a marquee, so its shape is this theme's adaptation, and the `rubberband` node and class names are GTK-required.
- `tests/support/gtk_theme_spec.py`: add a `RUBBERBAND = {"background-color": "transparent", "border": f"1px dotted {BLACK}"}` constant with a short comment (as `TEXT_SELECTION` has), and a `SheetRuleAssertions`-style `assert_rubberband(self, selectors)` method in `GtkSheetRuleCases` next to `assert_view_background`.
- `tests/test_gtk_theme.py`: `TestGtkTheme.test_rubberband` calls `self.assert_rubberband((".rubberband", "rubberband"))`. It also asserts that the rule comes after the `.view` rule in `self.css`: `self.css.index(".rubberband, rubberband {")` is greater than `self.css.index(".view, textview text, list {")`. A later `.view` would win the cascade again.
- `tests/test_gtk4_theme.py`: `TestGtk4Theme.test_rubberband` calls `self.assert_rubberband(("rubberband",))`.
- `docs/invariants.md`: add a new `## gtk` row at the end of the gtk section. Guarantee: both GTK sheets draw the drag-selection rubberband as a 1px dotted `#000000` outline with a transparent fill, and GTK 3's rule follows the white `.view` rule. Tests: the two `test_rubberband` tests. Provenance exception: no reference screenshot shows a selection marquee; the dotted outline with no fill follows the Mac OS Finder marquee, the black reuses the palette's reference-grounded outline, and the `rubberband` node and class names are GTK-required.

**Acceptance criteria.**
- The GTK 3 sheet has the `.rubberband, rubberband` rule after the `.view` rule, and the GTK 4 sheet has the `rubberband` rule, each with exactly the two declarations above.
- Removing either sheet's rule, changing its border style or colour, or giving it a fill fails that sheet's `test_rubberband`. Moving the GTK 3 rule above the `.view` rule also fails it.
- `test_only_palette_hex_literals` still passes in both suites, `tests/invariants.py` accepts the new row, and `make check` is green.

## Done

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
(startup splash, desktop layout, defaults); the desktop theme (twenty-four widget SVGs under
`widgets/` plus `dialogs/background.svg`); the Aurorae window decoration (frame, close, zoom and
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
text I-beam, pointing hand, busy hourglass and move cross, not traced from Apple's artwork), it
has landed inside the icon theme package with its provenance exception recorded in
`docs/invariants.md`, and `make apply-cursor`/`make remove-cursor` link it into the Xcursor path
and select it; **system sounds** are out
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

### Platinum Kvantum secondary controls: map toolbars, tree views and status bars onto the Platinum art (planned 2026-10-23 by the plan role; follows the landed four-part Kvantum series)

**Goal.** The Kvantum style defines the core, track/value and surface controls, but the six
sections Kvantum maps common Qt widgets to are left to its compiled-in default: `[ToolbarButton]`
(a `QToolButton` in a `QToolBar`), `[ToolbarComboBox]`, `[ToolbarLineEdit]`, `[DropDownButton]`
(a tool button with a menu popup), `[TreeExpander]` (a `QTreeView`'s branch indicator) and
`[StatusBar]`. `org.macos8.desktop.kvconfig`'s own header records that Kvantum "merges this file
over its compiled-in default.kvconfig and draws an element the theme SVG lacks from its
compiled-in default.svg", so these six sections are not defined by the Platinum style. State
them explicitly so a KDE application's toolbar buttons, toolbar combo boxes and line edits,
split-button dropdowns, tree-view expanders and status bar draw the same grounded Platinum
controls as the rest of the style instead of inheriting Kvantum's default. Every element the new
sections name (`button`, `lineedit`, `comboarrow`, `arrow`) already ships, so no SVG, palette or
Makefile change is needed.

**Approach.**
- `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`: after `[Toolbar]`, add these
  sections with a short comment naming the provenance exception (no reference screenshot shows a
  KDE/Qt toolbar, tree view or status bar, so the section and key names are Kvantum-required):
  - `[ToolbarButton]` -- `inherits=PanelButtonCommand`, the 2px raised Platinum push button with
    its black label in every state.
  - `[ToolbarComboBox]` -- `inherits=ComboBox`, the raised face whose `comboarrow` indicator is
    the reference popup's double arrow at size 12.
  - `[ToolbarLineEdit]` -- `inherits=LineEdit`, the white sunken field.
  - `[DropDownButton]` -- `inherits=PanelButtonCommand`, the raised face with its `arrow`
    down-indicator at size 9.
  - `[TreeExpander]` -- `inherits=PanelButtonCommand`, `frame=false`, `interior=false`, so only
    the `arrow` branch triangle is drawn (black in the normal states, #999999 disabled).
  - `[StatusBar]` -- `inherits=GenericFrame`, `frame=false`, `interior=false`, a flat bar in the
    `[GeneralColors]` window face with no bevel.
- `tests/support/kvantum_config_spec.py`: add the four framed sections to `CORE_FRAME_MARGINS`
  (all 2) and to `CORE_CONTROL_CONFIG` with the element mappings they resolve to -- for
  `ToolbarButton` and `DropDownButton` the frame and interior `button` and the indicator `arrow`,
  for `ToolbarComboBox` the frame and interior `button` and the indicator `comboarrow`, for
  `ToolbarLineEdit` the frame and interior `lineedit`. Add `TreeExpander` and `StatusBar` to
  `FRAMELESS_SECTIONS` as `{"frame": "false", "interior": "false"}`. No `VALUE_KEYS` entry is
  needed: the six sections hold no key beyond `inherits`, `frame` and `interior`, and the tables
  pin all of those. The existing `test_every_section_is_pinned`,
  `test_every_core_section_mapping_is_pinned`, `test_every_core_section_resolves_to_the_expected_frame_margin`
  and `test_every_frameless_section_suppresses_its_frame` then fail if a section, margin or
  inherited element target is dropped or changed.
- `README.md`: in the Kvantum paragraph, change "Its Platinum palette and core-control art live
  in ..." to "Its Platinum palette and control art live in ..." and add that the toolbar buttons,
  toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar
  map to the same Platinum button, line-edit and arrow art.
- `docs/invariants.md`: add one `## kvantum` row -- the six secondary sections resolve to the
  grounded Platinum elements and margins above -- citing
  `tests/test_kvantum_config_elements.py::TestCoreControlElements` and
  `tests/test_kvantum_config.py::TestSectionCoverage`; its provenance exception is the missing
  reference screenshot (the section and key names are Kvantum-required, the art is grounded).

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`,
`tests/support/kvantum_config_spec.py`, `README.md`, `docs/invariants.md`.

**Acceptance criteria.**
- Each new section resolves (following `inherits`) to its pinned element mapping and, for the four
  framed sections, the 2px frame margin; `TreeExpander` and `StatusBar` resolve `frame` and
  `interior` to `false`.
- `test_every_section_is_pinned` names all six new sections, and deleting one, dropping its frame
  margin, or repointing an inherited element target fails a test.
- No file under `theme/kvantum/org.macos8.desktop/` other than the `.kvconfig` changes, and no new
  colour is introduced.
- `make check` is green and `tests/invariants.py` accepts the new `## kvantum` row.

## Done

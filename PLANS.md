# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._


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
list (part 1/2), and its opt-in profile install as part 2/2 has also landed. That is an
extension of the
2026-10-19 "style Firefox" answer rather than the brief's KDE/Plasma desktop UI, so it is
recorded here to keep the scope deliberate.

_None yet._


### Kvantum Platinum toolbox tabs: paint a QToolBox's tabs with the reference-grounded Platinum tab face (planned 2026-10-26 by the plan role; independent of the waiting downloads-panel-buttons chrome plan) — done 2026-10-26 by the feature role

**Goal.** Make a Qt toolbox's tabs read as Platinum. `org.macos8.desktop.kvconfig` defines no `[ToolboxTab]` section, so a `QToolBox` falls back to Kvantum's compiled-in tab paint instead of the reference-grounded tab face the config already draws for `[Tab]`. Add the section and point it at the existing `[Tab]` surface, so a toolbox's selected and unselected tabs use the same Platinum `#CCCCCC`/`#EEEEEE` tab art, 2px frame margin and 8px side text margins as the theme's tab bars.

**Grounding.** No reference screenshot shows a Qt `QToolBox`, so the `[ToolboxTab]` section name is Kvantum-required: the installed KvantumAlt theme defines `[ToolboxTab]` with `inherits=PanelButtonCommand` in `/usr/share/Kvantum/KvantumAlt/KvantumAlt.kvconfig`. Drawing it from the existing tab surface adapts the reference-grounded System Profiler tab face (`tests/test_kvantum_tab_reference.py::TestTabReference`) rather than introducing new art or a new palette value.

**Approach.** In `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, insert the section immediately after `[Tab]` and before `[TabFrame]`, with `inherits=Tab` as its only key, and extend the container/text-surface comment paragraph to say tabs (including Qt toolbox tabs) draw the same raised Platinum face. In `tests/support/kvantum_config_spec.py`, add `"ToolboxTab": 2` to `CORE_FRAME_MARGINS` immediately after `"Tab"`, and add this entry to `SURFACE_CONTROL_CONFIG` immediately after `"Tab"`:

```python
"ToolboxTab": {
    "frame.element": "tab",
    "interior.element": "tab",
    "indicator.element": "tab",
},
```

No SVG, palette or value-key change: every mapping and margin resolves through `inherits=Tab` to the existing pinned values.

**Files touched.** `theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig`, `tests/support/kvantum_config_spec.py`, `tests/test_kvantum_config_elements.py`, `docs/invariants.md`, `README.md`.

**Acceptance criteria.**
- The `.kvconfig` has exactly one `[ToolboxTab]` section, positioned between `[Tab]` and `[TabFrame]`, whose options are exactly `{"inherits": "Tab"}`; the container/text-surface comment names toolbox tabs.
- `CORE_FRAME_MARGINS` contains `"ToolboxTab": 2` and `SURFACE_CONTROL_CONFIG` contains the `"ToolboxTab"` mapping above. The existing `TestSectionCoverage.test_every_section_is_pinned`, `TestCoreControlElements.test_every_core_section_mapping_is_pinned`, `TestSurfaceElements.test_every_surface_section_maps_to_its_element`, `TestFrameMargins.test_every_core_section_resolves_to_the_expected_frame_margin` and `TestValueKeys.test_every_key_is_pinned` pass unchanged, because the new section adds no non-`inherits` key.
- New `TestToolboxTabSurface.test_toolbox_tab_inherits_the_tab_surface` in `tests/test_kvantum_config_elements.py`, placed after `TestSurfaceElements`, reads `KVCONFIG` through `support.kde_config.read` and asserts `parser.get("ToolboxTab", "inherits") == "Tab"`, `set(parser.options("ToolboxTab")) == {"inherits"}`, and that for `frame.element`, `interior.element`, `indicator.element`, the four `frame.*` margins and `text.margin.left`/`text.margin.right`, `_resolved(parser, "ToolboxTab", key)` equals `_resolved(parser, "Tab", key)`.
- `docs/invariants.md` gains a row in `## kvantum` immediately after the row beginning "The tab face is the reference System Profiler tabs'": the Qt toolbox tab (`[ToolboxTab]`) draws the same reference-grounded Platinum tab face as `[Tab]`, inheriting its frame, interior and indicator art, 2px frame margin and 8px side text margins. Its test column names `tests/test_kvantum_config_elements.py::TestToolboxTabSurface`, `tests/test_kvantum_config_elements.py::TestSurfaceElements`, `tests/test_kvantum_config.py::TestSectionCoverage` and `tests/test_kvantum_config.py::TestFrameMargins`; its provenance records that no reference screenshot shows a Qt QToolBox, that `[ToolboxTab]` is Kvantum-required (the installed KvantumAlt theme defines it), that the mapping adapts the reference-grounded tab face pinned by `tests/test_kvantum_tab_reference.py::TestTabReference`, and that config checks do not establish rendered Qt pixels. `tests/invariants.py` stays green.
- `README.md`: in the Kvantum paragraph's control list, add toolbox tabs alongside the toolbar buttons, toolbar combo boxes and line edits, split-button dropdowns, tree-view expanders and status bar that map onto the shipped Platinum art.
- `make check` passes, and every existing Kvantum section, element, frame-margin and palette assertion keeps its expected value.
## Done

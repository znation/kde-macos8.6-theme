# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned


**Scope drift (2026-10-08, steward; rewritten 2026-10-17, steward; shipped-artifact facts
updated 2026-10-21 by the clean role; plan status re-trimmed 2026-10-22 by the steward role;
font facts re-trimmed 2026-10-22 by the steward role; landed-plan facts re-trimmed 2026-10-23
by the clean role; validation scope clarified 2026-10-25 by the steward role; Firefox artifact
and content-surface status updated 2026-10-26 by the steward role; install-firefox
file list corrected 2026-10-27 by the steward role; shipped-SVG count updated
2026-10-27 by the feature role):** The
initial prompt asks for
"the UI of MacOS 8.6, getting as close as possible to pixel-perfect theming." Shipped so far
(directories under `theme/`): the `MacOS8` color scheme; the `org.macos8.desktop` global theme
(startup splash, desktop layout, defaults); the desktop theme (thirty-one widget SVGs under
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
sheets under `theme/firefox/` (its `userChrome.css` and `userContent.css` copied, and its
profile preference written, only by the opt-in `install-firefox` target); and the render and
fidelity tooling.
The live reference-comparison gate in `tests/test_render_surface.py` checks Aurorae window-chrome
regions when its render prerequisites are available (README.md, "Fidelity checking").
Firefox's `tests/test_firefox_theme_*.py` modules check stylesheet declarations;
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

### Platinum GTK stack switcher: paint its page buttons as the Platinum tabs in GTK 3 and GTK 4 (planned 2026-10-27 by the plan role; the `## Planned` queue holds the status-bar plan ahead of it, which touches the same three landed files, so both anchors below are rule texts and symbol names, not line numbers)

**Goal.** The landed GTK sheets paint a `GtkSwitcher`'s pages (the landed `notebook` tab rules) as the Platinum raised tabs and paint generic push buttons with the raised bevel, but a `GtkStackSwitcher` — the page-group buttons file choosers and stack windows place at a window's top — falls through to the landed generic button rules, so its active page button paints as the landed `button:checked` *sunken* face instead of a raised tab, disagreeing with the landed notebook tab beside which stack switchers appear. This plan paints the stack switcher's child buttons with the landed tab recipe byte-for-byte in both toolkits, so the active page reads as the raised, flat-merged tab and the inactive pages as unpressed tabs, with no new constant, no new hex and no edit to any landed rule.

**Verified facts (checked 2026-10-27).** `grep -c stackswitcher` returns 0 for `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `tests/support/gtk_theme_spec.py`, `tests/support/gtk_rule_cases.py` and `docs/invariants.md`, and no PLANS.md `## Planned` entry nor PLANS-DONE.md or BUGS-FIXED.md finished record names a GTK stack switcher. Live-probed with PyGObject (GTK 3.24.49 and GTK 4.18.6, the toolkits the landed infobar row names): a `Gtk.StackSwitcher` with two pages builds a GTK 3 tree `Window > stackswitcher[stack-switcher,linked,horizontal] > button[text-button,radio]` (the children are `Gtk.RadioButton`s with `relief` 0; the node carries the `radio` *class*, not the `radio` node, so the landed `radio:checked` glyph rule cannot match it) and a GTK 4 tree root css name `stackswitcher` with class `linked` over `button` children with classes `text-button, toggle` (probe of `get_css_name()`/`get_css_classes()`). docs.gtk.org states on both the GtkStackSwitcher pages that the widget has a single CSS node named `stackswitcher`, so the root `stackswitcher` node is the guaranteed handle in both toolkits, and the active page's button carries `:checked` in each (a toggle-type button the stack switches active). The landed generic rules both sheets carry — `button { ... box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA; }` and `button:active, button:checked { box-shadow: inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF; }` — by themselves paint the checked page button *sunken*, the only repaint this plan must clear. The landed tab recipe the sheets already ship (`tab`, `tab:hover`, `tab:checked`, `tab:checked:hover` and the same `tab:backdrop[:checked]` arms) and the suite shares it through `TAB_STATES` in `tests/support/gtk_theme_spec.py` with `RAISED_BEVEL` (=`inset 1px 1px #FFFFFF, inset -1px -1px #999999`, the tab bevel differing from the `button` bevel's `#AAAAAA` depth), `test_tab_states` in `tests/support/gtk_rule_cases.py::GtkSheetRuleCases` builds each state's expected declaration list from `FACE` and `BLACK`; both GTK suites already import `RAISED_BEVEL`, `FACE`, and `BLACK`, and neither imports `TAB_STATES` yet.

**Grounding (platform adaptation, steward clarification 2026-10-25).** No reference screenshot in `macos8.6-screenshots/` shows a GTK stack switcher, so the plan samples no new reference pixel: it reuses only the landed tab recipe's values, whose own provenance the landed `test_tab_states` path already records (the raised tab bevel and the `#DDDDDD` face, pinned by the desktop theme's `widgets/tabbar.svg` case and the notebook tab rules). The `stackswitcher` root node and the `button` child nodes are GTK-required; so is the checked page button's `:checked` state. The checked arm reuses the tab checked recipe byte-for-byte — including the tab's face-coloured `border-bottom-color`, meaningful only where a notebook tab merges with its header — so the sheets keep exactly one tab recipe; this is decided here so no design question is left open. `:backdrop` stays out of scope, as the landed infobar, search-bar and action-bar decisions scoped it out, and the landed tab `:backdrop` arms stay untouched, so an unfocused stack window keeps the landed generic button paint unless a stackswitcher-specific rule matches.

**Approach.** In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, directly after the landed `tab:checked:hover, ... notebook > header > tabs > tab:checked:hover` rule and before the landed `treeview.view header button` rule, add

```css
/* A stack switcher's page buttons draw as the landed tab recipe, the active
   page's button included; :backdrop stays out of scope. */
stackswitcher > button {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999;
}

stackswitcher > button:hover {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999;
}

stackswitcher > button:checked,
stackswitcher > button:checked:hover {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-bottom-color: #DDDDDD;
  border-radius: 0;
  box-shadow: none;
}
```

Verification of the selectors' spellings against the landed tab arms above them is part of the edit: the three blocks reuse the landed arm declaration lines byte-for-byte apart from the importing selector.

In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, directly after the landed `tab:backdrop:checked, ... notebook > header > tabs > tab.reorderable-page:backdrop:checked` rule and before the landed `columnview.view > header > button, treeview.view > header > button` rule, add the same block under the same comment text.

In both sheets' provenance header comments, append one sentence after the search-bar/action-bar sentence and before the closing `*/`: "A stack switcher's page buttons paint as the landed tab recipe byte-for-byte; no reference screenshot shows a GTK stack switcher, and the stackswitcher and button node names are GTK-required."

In `tests/test_gtk_theme.py::TestGtkTheme`, after the landed `test_action_bar`, add `test_stack_switcher_tabs`: build a local dict `forms = {"base": ("stackswitcher > button",), "hover": ("stackswitcher > button:hover",), "checked": ("stackswitcher > button:checked",), "checked+hover": ("stackswitcher > button:checked:hover",)}`, and iterate `TAB_STATES` skipping every state whose name is not in the dict (the two `:backdrop` states stay out of scope), building the same expected declaration list for the state iterated as `test_tab_states` does — `FACE` face, `background-image: none`, `border: 1px solid BLACK`, `border-radius: 0`, and `box-shadow: RAISED_BEVEL` when unchecked, `border-bottom-color: FACE` and `box-shadow: none` when checked — calling `self.assert_rule(selector, expected)` inside a `subTest(state=..., selector=...)` per selector, with no change to `test_tab_states` or the shared cases file.

In `tests/test_gtk4_theme.py::TestGtk4Theme`, after the landed `test_action_bar`, add the same `test_stack_switcher_tabs` body. Add `TAB_STATES` to the existing `from support.gtk_theme_spec import (...)` list in each suite; `FACE` and `BLACK` are already imported in both (`tests/test_gtk_theme.py` line after line 38's list, `tests/test_gtk4_theme.py` from the same lists).

Extend no landed assertion: the shared `assert_rule` machinery already parses both sheets, and both suites keep landing `test_tab_states` unchanged, so the only shared-file change is one added name in each suite's existing `support.gtk_theme_spec` import list.

In `docs/invariants.md`, in the `## gtk` table: append exactly one row after the landed search-bar/action-bar row (`Both GTK sheets paint a search bar ... and an action bar ...` — the table's last row before the trailing live-validation note) with the guarantee in one sentence (both sheets paint a stack switcher's page buttons as the landed tab recipe — the raised bevel for the unpressed states and the flat checked face with the face-coloured bottom border — while the landed notebook tab and generic button rules stay byte-identical and the notebook tab `:backdrop` arms keep covering an unfocused window) and the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_stack_switcher_tabs` and `tests/test_gtk4_theme.py::TestGtk4Theme::test_stack_switcher_tabs`; trim no landed row (this plan closes no other surface).

**Files touched.** `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, `tests/test_gtk_theme.py`, `tests/test_gtk4_theme.py`, `docs/invariants.md`.

**Acceptance criteria.**
- The GTK 3 and GTK 4 sheets each gain exactly the three rule blocks above, each placed between the named landed neighbours, introducing no hex outside `{#DDDDDD, #999999, #000000, #FFFFFF}`, changing no landed rule's text and adding no `!important`.
- Both sheets' headers gain exactly one appended sentence after the search-bar/action-bar sentence and before `*/`.
- The two new tests pass through the landed `assert_rule` path using the shared `TAB_STATES`, `RAISED_BEVEL`, `FACE` and `BLACK` constants, dropping only the states the plan scopes out; `test_tab_states` and every other landed support case changes no text and runs unchanged, and the only support-file touch is the one added `TAB_STATES` name per suite's already existing import.
- `docs/invariants.md` gains exactly one appended row after the search-bar/action-bar row naming the two new tests, with no landed row's wording changed; `tests/support/invariants.py`'s register stays in step.
- `make check` passes.

## Done

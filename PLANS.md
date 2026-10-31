# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

_None yet._

### Platinum GTK 4 OSD overlay containers: repaint the stock dark container
bands with the landed menu-bar band (planned 2026-10-30 by the plan role;
independent of the waiting GTK 3 OSD entry-and-spin-button-fields plan — it
appends one grouped rule at the end of `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`,
adds one test beside `test_progressbar_osd_trough_paint` in
`tests/test_gtk4_theme.py` and appends one row in the `## gtk` invariants
table, while that entry appends field rules to the GTK 3 sheet, adds a test
beside `test_osd_overlay_bands` in `tests/test_gtk_theme.py` and its own
`## gtk` row; no shared file, selector or test)

**Goal.** The landed GTK 4 sheet restates only three OSD arms — video
`image.osd` corners, `progressbar.osd` troughs and the `.osd switch:checked`
track — so every stock OSD overlay container still paints the toolkit's
translucent dark bubble: the video toolbar bar, a scale button's value popup,
an `.app-notification` bubble, the touch-selection and magnifier popovers and
any bare `.osd` container keep stock's `rgba(53,53,53,0.7)` band with greyed
white text. Repaint every stock container arm with the landed menu-bar band
that the GTK 3 OSD container plan already landed, so a GTK 4 OSD overlay is a
Platinum surface like the GTK 3 one.

**Verified facts (probed 2026-10-30, `gresource extract` on
`/usr/lib/x86_64-linux-gnu/libgtk-4.so.1`, libgtk-4 4.18.6, resource
`/org/gtk/libgtk/theme/Default/Default-light.css`, and on
`/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0`, libadwaita 1.7.6, resource
`/org/gnome/Adwaita/styles/base.css`).** The GTK Default resource — the only
stock that paints the OSD container band; libadwaita carries no band rule —
supplies the grouped ten-selector arm (`.osd .scale-popup`, `.app-notification`,
`.rich-list > header`, the six `popover.background` child selectors under the
`.osd`, `.touch-selection` and `.magnifier` classes, and the bare `.osd`)
declaring `color: #eeeeec; border: none; background-color: rgba(53, 53, 53,
0.7); background-clip: padding-box; -gtk-icon-shadow: 0 1px black`; the
`.toolbar.osd` arm declaring `padding: 13px; border: none; border-radius:
5px; background-color: rgba(53, 53, 53, 0.7)`; the transparency re-draw
`.osd popover.background, popover.background.touch-selection,
popover.background.magnifier { background-color: transparent }`; and the
popover child re-draw `.osd popover.background > arrow, .osd
popover.background > contents, popover.background.touch-selection > arrow,
popover.background.touch-selection > contents,
popover.background.magnifier > arrow, popover.background.magnifier >
contents { border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: none }`.
libadwaita's base.css carries the same surfaces' own arms that the landed
popover paint must beat on equal specificity instead: `.osd popover,
popover.touch-selection, popover.magnifier { background-color: transparent;
color: rgba(255, 255, 255, 0.9) }`, the child re-draw `.osd popover > arrow,
.osd popover > contents, popover.touch-selection > arrow,
popover.touch-selection > contents, popover.magnifier > arrow,
popover.magnifier > contents` declaring `border-color:
rgba(255, 255, 255, 0.1); box-shadow: none`, and `.toolbar.osd { padding:
12px; border-radius: 15px }`. Neither resource has a container `:backdrop`
arm, so none is restated. Stock's `.osd .toolbar { background-color:
transparent }` keeps the empty toolbar band transparent over its container
and stays untouched. No collected reference screenshot shows a GTK OSD
overlay (the landed GTK 3 container block records the same exception), so
this reuses the landed menu-bar band adaptation — `INFOBAR` in
`tests/support/gtk_theme_spec.py` (`FACE` band, black text, the
`#888888`/`inset 0 -1px #FFFFFF` etched bottom edge), pinned by the landed
`tests/test_gtk4_theme.py::TestGtk4Theme::test_infobar` — and the stock
selector sets are GTK-required. The landed sheet's own three OSD rests
(`video image.osd`, both `progressbar.osd` troughs, `.osd switch:checked`)
stay as they are.

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`,
append at the end a dated provenance comment naming the missing reference
surface, the two gresource probes above and the reuse of the landed GTK 3
OSD container block's declaration set, followed by exactly one grouped rule
over twenty-one selectors — the stock Default resource's ten, `.osd
popover.background`, `.toolbar.osd`, and libadwaita's nine spellings `.osd
popover`, `popover.touch-selection`, `popover.magnifier`, `.osd popover >
arrow`, `.osd popover > contents`, `popover.touch-selection > arrow`,
`popover.touch-selection > contents`, `popover.magnifier > arrow`,
`popover.magnifier > contents` — declaring `background-color: #DDDDDD;
background-image: none; color: #000000; border: 0; border-bottom: 1px
solid #888888; border-radius: 0; box-shadow: inset 0 -1px #FFFFFF;
text-shadow: none; -gtk-icon-shadow: none;`. Declaring each arm at its own
stock selectors keeps every stock spell-out at an equal-specificity tie the
user sheet wins by order, so Default-theme and libadwaita applications both
see the band. The `border: 0` plus the `border-bottom` clears stock's faint
white popover borders; `.toolbar.osd`'s stock `padding` survives because the
restated arm declares no padding (13px in the Default resource, 12px in
libadwaita — record both in the provenance comment). Touch no landed rule:
not the landed popover/toast block, `video image.osd`, the two
`progressbar.osd` troughs, `.osd switch:checked`, the infobar, banner,
searchbar/actionbar and menu-bar rules, and leave libadwaita's
`colorchooser .popover.osd` radius, `.osd shortcut > .keycap`/`.osd
list.boxed-list`/`.osd .card` card arms, `.osd row.activatable` washes and
`toggle-group.osd` variable arm and the Default `.osd check/radio`, `.osd
button`/flat, `.osd` progress/scale and `.osd spinbutton > text/button`
arms for later surface plans (recorded here, not this change; GTK 3's mirror
list already sits in the landed GTK 3 container plan). (2) In
`tests/test_gtk4_theme.py`, add `TestGtk4Theme.test_osd_container_bands`
beside `test_progressbar_osd_trough_paint`: build one expected dictionary by
extending the landed `INFOBAR` spec with `background-image: none`, `border:
"0"`, `border-radius: "0"`, `text-shadow: none` and `-gtk-icon-shadow: none`
(so the reuse is visible in the code, not a coincidence of literals); assert
each of the twenty-one per-selector keys `tests/support/gtk_css.parse_css`
splits out of the grouped rule against it, and add a scope assertion that
the set of parsed sheet selectors containing `osd`, `touch-selection`,
`magnifier`, `scale-popup` or `app-notification` equals exactly those
twenty-one plus the five landed OSD-keyed selectors (`video image.osd`,
`progressbar.osd > trough`, `progressbar.osd.horizontal > trough`,
`progressbar.osd.vertical > trough`, `.osd switch:checked`), so no other OSD
container arm can appear untested. (3) In `docs/invariants.md`, in the `##
gtk` table, append one row: the guarantee — every stock GTK 4 OSD overlay
container named above draws the landed menu-bar band (opaque `#DDDDDD` face,
black text, the `#888888` etched bottom edge) instead of the toolkit's dark
translucent bubbles, under whatever toolkit loads, with the retained stock
`toolbar.osd` padding — with the test column naming
`tests/test_gtk4_theme.py::TestGtk4Theme::test_osd_container_bands` and the
landed OSD tests it must not disturb (`...::test_video_osd_image_corners`,
`...::test_progressbar_osd_trough_paint`,
`...::test_progressbar_osd_trough_thickness`,
`...::test_switch_osd_checked_track_color`, `...::test_infobar`); the
provenance cell records the missing reference surface, the two gresource
probes (libgtk-4 4.18.6 `Default-light.css` and libadwaita 1.7.6
`base.css`, inspected 2026-10-30), the reused `INFOBAR` spec and landed GTK
3 container block, the GTK-required selector sets, the retained kit
paddings, and the close-out that declaration checks do not establish
rendered pixels. Trim no landed row; `tests/test_invariants.py` parses the
register.

**Acceptance criteria.** The GTK 4 sheet ends with the one grouped
twenty-one-selector rule whose complete parsed dictionaries are exactly the
band nine; changing any of the twenty-one selectors, deleting the rule,
dropping a shadow-clear declaration or leaving stock's faint white popover
border or dark translucent face fails `test_osd_container_bands`;
`test_video_osd_image_corners`, `test_progressbar_osd_trough_paint`,
`test_progressbar_osd_trough_thickness`, `test_switch_osd_checked_track_color`,
`test_infobar`, `test_only_palette_hex_literals`, `test_no_universal_selector`
and `test_no_status_or_translucent_shade_roles` stay green, and the landed
popover, toast, infobar, banner, searchbar/actionbar, `video image.osd`,
`progressbar.osd` and `.osd switch` rules keep their landed text. Scope is
the GTK 4 sheet, `tests/test_gtk4_theme.py`, `docs/invariants.md` and
nothing else: no GTK 3 rule, no Firefox sheet, no new asset, dependency or
`!important`; the only colour literals are the landed `#DDDDDD`, `#888888`,
`#FFFFFF` and `#000000`. `make check` passes.

### Platinum GTK 3 OSD checks and radios: restate the stock dark indicator arms with the landed check and radio recipes (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 OSD overlay-container plan — it appends five check-and-radio arm groups to the GTK 3 sheet, adds one test beside `test_osd_entry_fields` in `tests/test_gtk_theme.py` and appends one row to the `## gtk` invariants table, while that entry appends one grouped rule to the GTK 4 sheet, adds one test in `tests/test_gtk4_theme.py` and appends its own row; the only shared document is `docs/invariants.md`, and each entry appends its own row — no shared selector, test or suite)

**Goal.** The landed GTK 3 OSD container plan repainted every stock OSD
overlay container and the landed fields plan (`PLANS-DONE.md`, "Platinum GTK 3
OSD entry and spin-button fields") repainted the fields inside them, but the
checks and radios inside those light Platinum overlays still paint the
toolkit's dark indicators: the sheet declares nothing for `.osd check` or
`.osd radio` (grep: the sheet's only `osd` selectors are the landed container
and field arms), so the toolkit resource's five `.osd` indicator arms supply
translucent dark bubbles with white text shadows instead of the landed raised
`#DDDDDD` check face and flat white round radio. Restate all five arms with
the landed check and radio recipes, so a check or radio inside a Platinum OSD
overlay draws like one everywhere else.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, libgtk-3 3.24.49).** The
resource's five `.osd check`/`.osd radio` arms: the base and `:hover`
siblings (`color: #eeeeec`, `rgba(0,0,0,0.7)` border colour,
`image(rgba(53,53,53,0.9))` background over a transparent background colour,
`padding-box` clip, `inset 0 1px rgba(255,255,255,0.1)` shadow,
`0 1px black` text and icon shadows, `outline-color:
rgba(238,238,236,0.3)`); the `:active` sibling (`image(rgba(0,0,0,0.7))`
background, remaining shadows cleared); the `:backdrop` sibling (base
background, shadows cleared); the `:disabled` sibling
(`image(rgba(71,71,71,0.5))` background, `#919190` colour, shadows cleared).
No stock `.osd check` state arm sets geometry, an `-gtk-icon-source`, or a
`:checked`/`:indeterminate` spelling — the landed plain `check, radio`,
`check:checked`/`radio:checked` and `check:indeterminate` rules keep governing
inside `.osd` overlays at every specificity, and the static shipped glyph
assets are not recoloured, so the restatement needs no colour, glyph or
geometry decision beyond the recipes below. No collected reference
screenshot shows a GTK OSD indicator, so this is a platform adaptation
reusing the landed recipes — `CHECK` and `RADIO` in
`tests/support/gtk_theme_spec.py` (the raised `#DDDDDD` check face with the
`inset 1px 1px #FFFFFF, inset -1px -1px #888888` etch and square corners, the
flat `#FFFFFF` round radio), pinned by the landed
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio` —
and the arm selectors and state names are GTK-required (they spell the
toolkit resource's rules).

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`,
append after the landed `.osd entry`/`.osd spinbutton` field block a dated
provenance comment naming the missing reference surface, this `gresource`
probe and the reuse of the `CHECK`/`RADIO` recipes, followed by five groups —
one per stock state — each mirroring the landed plain shape at the `.osd`
levels. The base group is literally:

```css
.osd check, .osd radio {
  min-height: 14px;
  min-width: 14px;
  margin: 0 4px;
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #888888;
  outline-color: #000000;
  text-shadow: none;
  -gtk-icon-shadow: none;
}
.osd radio {
  background-color: #FFFFFF;
  border-radius: 50%;
  box-shadow: none;
}
```

and the `:hover`, `:active`, `:backdrop` and `:disabled` groups repeat the
identical two-rule shape at the stock spellings `.osd check:hover, .osd
radio:hover` and so on — the landed hover policy keeps the same face, `:active`
and `:backdrop` keep the recipes unchanged, and `:disabled` changes no
declaration either, because the shipped glyph assets never recolour and the
landed plain rules declare no disabled arm of their own. Four clears ride in
every base group: `outline-color: #000000` (stock claims `outline-color:
rgba(238,238,236,0.3)` in every `.osd` indicator arm; black is the landed
recipes' outline colour, recorded in the provenance comment) and the
`text-shadow: none` / `-gtk-icon-shadow: none` pair, clearing the
white-on-dark text shadows stock paints. Touch no landed rule: not the landed container block, field block, plain
`check`/`radio`/glyph rules or `MENU_CHECK`; leave the `.osd` progress and
scale arms, `progressbar.osd`'s transparent-trough override, the `.scale-popup
button.flat` and `colorchooser .popover.osd` corners, and the `button.osd` and
grouped `.osd button`/flat/suggested-action/destructive-action families for
later surface plans (recorded here, not this change). (2) In
`tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_check_radio` beside
`test_osd_entry_fields`: build one expected check dictionary
(`{**CHECK, "outline-color": BLACK, "text-shadow": "none", "-gtk-icon-shadow":
"none"}` — `CHECK` already carries the geometry, `background-image: none`,
`border-radius: "0"` and the etch) and one expected radio dictionary
(`{**RADIO, "outline-color": BLACK, "text-shadow": "none", "-gtk-icon-shadow":
"none"}`), assert each of the ten per-state, per-node selectors
`tests/support/gtk_css.parse_css` splits out of the five groups against its
node's dictionary, assert the five `.osd check` dicts are mutually equal and
the five `.osd radio` dicts are mutually equal (the state arms are byte-for-
byte the recipes), and add the scope assertion that the set of parsed sheet
selectors containing `.osd check` or `.osd radio` equals exactly those ten. In
the same change, extend `test_osd_overlay_bands`'s existing scope filter —
which already excludes the restated `.osd entry` and `.osd spinbutton`
selectors so they do not enter that test's container set — to exclude `.osd
check` and `.osd radio` selectors the same way, or the new arms fail that
landed test. (Anchoring precedent: the landed fields plan hit exactly this
filter and recorded the correction.) (3) In `docs/invariants.md`, in the
`## gtk` table, append one row: the guarantee — every stock GTK 3 OSD check
and radio indicator arm draws the landed raised `#DDDDDD` check face and flat
white round radio with black borders, cleared shadows and a black focus-
outline colour, under whatever toolkit resource loads, identical in all five
stock states — with the test column naming
`tests/test_gtk_theme.py::TestGtkTheme::test_osd_check_radio` (the register
parser resolves the column only against tests defined in the named module, so
cite the shared base case
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio` in
the provenance cell, not the test column); the provenance cell records the
missing reference surface, the gresource probe (libgtk-3 3.24.49
`gtk-contained.css`, probed 2026-10-30), the reused `CHECK`/`RADIO` specs and
their pinning test, the GTK-required arm spellings, the black
outline-colour clear, the glyph and geometry rules the plain arms keep
governing, and the close-out that declaration checks do not establish
rendered pixels. Trim no landed row; `tests/test_invariants.py` parses the
register.

**Acceptance criteria.** The GTK 3 sheet carries the five five-state arm
groups whose complete parsed dictionaries are exactly the two recipe
dictionaries above; changing any of the ten selectors, deleting a group,
dropping the outline-colour clear or the etched check shadow, or letting stock
keep its dark bubbles fails `test_osd_check_radio`; `test_osd_overlay_bands`
(with its extended filter), `test_osd_entry_fields`, `test_check_and_radio`,
`test_menu_check_and_radio_are_boxless`, `test_only_palette_hex_literals`,
`test_no_universal_selector`, `test_icon_sources_point_at_shipped_assets` and
`test_no_status_or_translucent_shade_roles` stay green, and the landed
container, field and plain check/radio rules keep their landed text. Scope is
the GTK 3 sheet, `tests/test_gtk_theme.py`, `docs/invariants.md` and nothing
else: no GTK 4 rule, no Firefox sheet, no new asset, colour literal beyond the
landed `#DDDDDD`, `#FFFFFF`, `#888888` and `#000000`, dependency or
`!important`. `make check` passes.

## Done


## Done

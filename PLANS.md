# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Platinum GTK 3 OSD scale thumbs: restate the stock `.osd scale slider` arms with the landed scale-slider recipes (planned 2026-10-30 by the plan role; independent of any meter restatement that merges first — it restates only slider-node selectors, neither entry styles the other's selectors, both entries extend `test_osd_overlay_bands`'s scope filter and append at the sheet's tail with append-only edits, and any merge order leaves the cascade correct, as the approach spells)

**Goal.** The landed GTK 3 OSD container, field and check/radio plans repainted
the sheets' other OSD arms, but a scale thumb inside a Platinum OSD overlay
still paints the toolkit's translucent dark bubble: the GTK 3 sheet declares
nothing for `.osd scale slider` (grep: its `osd` selectors are the container
band, the `.osd entry`/`.osd spinbutton` field arms and the `.osd check`/
`.osd radio` arms, nothing else). Restate the toolkit resource's six stock
`.osd scale slider` arms with the landed scale-thumb recipes — the raised
`#DDDDDD` face and bevel, the grey disabled face — so a thumb inside an OSD
overlay draws like the plain raised thumbs everywhere else.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, libgtk-3 3.24.49;
exhaustive scan of every `osd`+`slider` rule in the resource).** The resource
carries exactly six `.osd scale slider` arms — base, `:hover`, `:active`,
`:disabled`, `:backdrop`, `:backdrop:disabled` — each a one-selector rule;
the base/hover/active/disabled/backdrop arms re-declare `border-color` and
`background-color` part-way through, and `tests/support/gtk_css.py::parse_css`
merges rules sharing a selector key, so the effective paints are: base
`background-color #353535` (last-wins over `transparent`),
`background-image image(rgba(53,53,53,0.9))`, `border-color rgba(0,0,0,0.7)`,
`box-shadow inset 0 1px rgba(255,255,255,0.1)`, `text-shadow 0 1px black`,
`-gtk-icon-shadow 0 1px black`, `outline-color rgba(238,238,236,0.3)`,
`background-clip padding-box`; hover swaps the image to
`image(rgba(83,83,83,0.9))` and to white text; active paints
`image(rgba(0,0,0,0.7))` and clears all three shadows; disabled paints
`image(rgba(71,71,71,0.5))` with `#919190` text and shadows none; backdrop
repeats the base paints with every shadow cleared and no outline claim;
backdrop:disabled claims only `background-color #353535`. No stock `.osd`
slider arm sets geometry (no `min-*`, no margin) and none claim a color on
hover-only nodes beyond the dark-thumb text/icon pair; the landed plain
`scale slider`, `scale.horizontal slider`, `scale.vertical slider` and
`scale slider:disabled` rules keep governing size and every state an arm does
not restate. No collected reference screenshot shows a GTK OSD scale, so this
is a platform adaptation reusing the landed recipes — `SCALE_THUMB` in
`tests/support/gtk_theme_spec.py` and the plain sheet rules it drives, pinned
by `tests/support/gtk_rule_cases.py::GtkSheetRuleCases::assert_scale` (the
slider group) and `TestGtkTheme::test_scale` in `tests/test_gtk_theme.py` —
with stock's arm selectors and state names GTK-required (they spell the
toolkit resource's rules). The `.osd .scale-popup button.flat` arms and the
stock `progressbar.osd` thin-bar trio stay out of scope; leave them for their
queued surface plans.

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`,
append immediately after the final rule of the sheet's `.osd` overlay section
(after the `.osd radio:disabled` group as the sheet stands now; when the
meter restatement has merged, after its final block) a dated provenance
comment naming the missing reference surface, this `gresource` probe, the
reuse of the plain-slider recipes (the fields plan cleared the stock
`text-shadow 0 1px black`/`-gtk-icon-shadow 0 1px black` pair, and the
check/radio plan restated stock's translucent `outline-color` as
`outline-color: #000000` — clear the same pair and restate the same
outline), and the note that stock's `background-clip: padding-box` is part of
its translucent dark-bubble arm, while the landed plain thumb draws without
it, so the restated thumb omits it and draws exactly like the plain one.
Then append five rules spelling six selectors — the base/hover/active/
backdrop raised face, the margin only on the stateless arms stock leaves to
the plain base rule, and the disabled metal in every disabled state (a rule
with no state matches every state, so the appended base arm and the plain
`scale slider:disabled` arm tie at equal specificity on the shared
properties and the later base would paint an enabled face over a disabled
thumb — the appended `:disabled` arm outranks both at three-state-classes
and frees the disabled face; the dedicated `:backdrop:disabled` selector
doesn't carry its own colour, but stock declares the arm and keeping it
keeps the arm list complete):

```css
.osd scale slider,
.osd scale slider:hover,
.osd scale slider:active,
.osd scale slider:backdrop {
  background-color: #DDDDDD;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #999999;
  outline-color: #000000;
  text-shadow: none;
  -gtk-icon-shadow: none;
}
.osd scale slider,
.osd scale slider:backdrop {
  margin: -5px;
}
.osd scale slider:disabled,
.osd scale slider:backdrop:disabled {
  background-color: #DDDDDD;
  border: 1px solid #999999;
  box-shadow: none;
}
```

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_scale_slider`
beside `test_osd_check_radio`: add `SCALE_THUMB` to the existing
`support.gtk_theme_spec` import list (`BLACK`, `FACE` and `GREY` are already
imported from `support.platinum_palette`); build one expected raised-face
dictionary (`{**SCALE_THUMB, "outline-color": BLACK, "text-shadow": "none",
"-gtk-icon-shadow": "none"}`), one expected base dictionary (`{**face,
"margin": "-5px"}`) and one expected disabled dictionary
(`{"background-color": FACE, "border": f"1px solid {GREY}",
"box-shadow": "none"}`); assert each of the six selectors
`tests/support/gtk_css.py::parse_css` splits out of the five rules against
its recipe dictionary; cross-check the dictionary carries (
`self.rules[".osd scale slider:disabled"] == self.rules["scale
slider:disabled"]`, and `self.rules[".osd scale slider"] == {**self.rules
["scale slider"], "outline-color": BLACK, "text-shadow": "none",
"-gtk-icon-shadow": "none"}`, both false-tolerance pin the same claim
`assert_scale` pins); and add the scope assertion that the set of parsed
sheet selectors containing `.osd scale slider` equals exactly those six.
In the same change, extend `test_osd_overlay_bands`'s existing scope filter
— which already excludes the restated `.osd entry`, `.osd spinbutton`,
`.osd check` and `.osd radio` selectors — to exclude selectors containing
`.osd scale slider` the same way, or the new arms fail that landed test's
selector scan. (Anchoring precedent: the fields, check/radio and meter plans
all hit exactly this filter and recorded the correction.) (3) In
`docs/invariants.md`, in the `## gtk` table, append one row: the guarantee —
every stock GTK 3 OSD scale thumb draws the landed raised `#DDDDDD` face
with its black border, zero radius, white/grey bevel and the plain thumb's
`-5px` margin, and the landed grey disabled face in both disabled states,
identical across hover, active, disabled and backdrop — with the test column
naming `tests/test_gtk_theme.py::TestGtkTheme::test_osd_scale_slider` (the
register parser resolves the column only against tests defined in the named
module, so cite the shared base cases `assert_scale` in
`tests/support/gtk_rule_cases.py` and `TestGtkTheme::test_scale` in the
provenance cell, not the test column); the provenance cell records the
missing reference surface, the gresource probe (libgtk-3 3.24.49
`gtk-contained.css`, probed 2026-10-30), the reused `SCALE_THUMB` spec and
its pinning tests, the GTK-required six-arm spellings, the cleared text/icon
shadow pair, the restated black outline, the omitted `background-clip`, the
plain rules' governing geometry, the untouched `.osd .scale-popup
button.flat` arms, and the close-out that declaration checks do not
establish rendered pixels. Trim no landed row; `tests/test_invariants.py`
parses the register.

**Acceptance criteria.** The GTK 3 sheet carries the five rules parsing to
exactly those six selectors at the three dictionaries above; changing any of
the six selectors, deleting a rule, dropping the base's `margin: -5px` or
the disabled arm's `border`, changing the disabled border away from the
plain disabled rule's `1px solid #999999`, or letting stock keep its dark
translucent bubbles fails `test_osd_scale_slider`; `test_osd_overlay_bands`
(with its extended filter), `test_osd_entry_fields`, `test_osd_check_radio`,
`test_scale`, `test_switch_focus`, `test_only_palette_hex_literals`,
`test_no_universal_selector`, `test_icon_sources_point_at_shipped_assets`
and `test_no_status_or_translucent_shade_roles` stay green, and the landed
container, field and check/radio rules keep their landed text. Scope is the
GTK 3 sheet, `tests/test_gtk_theme.py`, `docs/invariants.md` and nothing
else: no GTK 4 rule, no Firefox sheet, no new asset, colour literal beyond
the landed `#DDDDDD`, `#999999`, `#FFFFFF`, `#000000` and `transparent`,
dependency or `!important`. `make check` passes.

*(Re-filed 2026-10-30 by the plan role: this completed plan was appended at file end into the Done section of this file by its own planning commit 2e55839d, but its implementation never landed — there is no done stamp, no `TestGtkTheme::test_osd_progress_scale` in `tests/test_gtk_theme.py` and no `.osd` trough/fill/progress rule in the GTK 3 sheet — so the entry returns to the work queue; the text below is unchanged.)*

### Platinum GTK 3 OSD progress and scale arms: restate the stock dark trough, fill and progress paints with the landed progress-bar and scale recipes (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 OSD check-and-radio plan — it appends ten restated rules to `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, adds `TestGtkTheme::test_osd_progress_scale` beside `test_osd_check_radio` in `tests/test_gtk_theme.py` and appends one row to the `## gtk` invariants table, while that entry edits the GTK 4 sheet, `tests/test_gtk4_theme.py` and its own row; the only shared documents are `docs/invariants.md`, where each entry appends its own row, and `tests/support/gtk_theme_spec.py`, from which both import static specs and neither edits — no sheet selector, test or suite overlaps)

**Goal.** The landed GTK 3 OSD container, field and check/radio plans repainted
every stock OSD arm in the sheet except the meters: the GTK 3 sheet declares
nothing for `.osd progressbar trough` or `.osd scale trough` (grep: the
sheet's only `osd` selectors are the landed container band, the `.osd entry`/
`.osd spinbutton` field arms and the ten `.osd check`/`.osd radio` arms), so
the toolkit resource's six `.osd` trough, fill and progress paints supply
translucent dark bubbles (`rgba(0,0,0,0.5)` foundations over `rgba(0,0,0,0.7)`
edges) inside Platinum overlays instead of the landed flat `#EEEEEE` trough
face and flat `#CCCCFF` progress fill. Restate all six paints with the landed
progress-bar and scale recipes, so a meter inside a Platinum OSD overlay draws
like one everywhere else.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-3.so.0
/org/gtk/libgtk/theme/Adwaita/gtk-contained.css`, libgtk-3 3.24.49; exhaustive
scan of every rule in the resource whose selector contains `osd` and one of
`trough`/`fill`/`highlight`/`progress`).** The resource carries exactly six
such paints: the base trough/fill sibling `.osd progressbar trough,
progressbar .osd trough, .osd scale fill, scale .osd fill, .osd scale trough,
scale .osd trough` (`border-color: rgba(0,0,0,0.7)`,
`background-color: rgba(0,0,0,0.5)`); its `:disabled` sibling at the same six
selectors (`background-color: rgba(71,71,71,0.5)`); the base
progress/highlight sibling `.osd progressbar progress, progressbar .osd
progress, .osd scale highlight, scale .osd highlight` (`border-color:
rgba(0,0,0,0.7)`); its `:disabled` sibling at the same four selectors
(`border-color: transparent`); a bare `.osd scale fill` sibling
(`background-color: rgba(91,91,90,0.775)` — the value fill stock shows over
the dark trough, distinct from its trough-group paint); and the fill clear
`.osd scale fill:disabled:backdrop, .osd scale fill:disabled`
(`border-color: transparent`, `background-color: transparent`). The trough
and progress paints set no geometry (no `min-*` or `margin`), no
`-gtk-icon-source`, no `box-shadow`, and no `:backdrop` spelling on a trough
or progress node — the only `:backdrop` in the whole set rides the fill-clear
sibling's `:disabled:backdrop`. Both grouped paints carry identical
declarations across the nodes they couple, so split at the landed recipe
boundaries, each split selector keeps complete equal dictionaries. No stock
`.osd` trough/fill/progress paint recolours anything else or shadows —
nothing is dropped in the restatement, and with no stock arm claiming
`color` either, the restatement needs no paint, glyph or geometry decision
beyond the recipes below. No collected reference screenshot shows a GTK OSD
meter, so this is a platform adaptation reusing the landed recipes —
`PROGRESSBAR_TROUGH`, `PROGRESSBAR_PROGRESS`, `SCALE_TROUGH` and
`SCALE_EMPTY_FILL` in `tests/support/gtk_theme_spec.py` (the flat `#EEEEEE`
trough face with the 1px black border, zero radius and `inset 1px 1px
#999999` etch at 10px/6px minimums, the flat `#CCCCFF` progress fill and the
transparent fill/highlight face) — pinned by the landed
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::assert_progressbar` and
`TestGtkTheme::test_scale` in `tests/test_gtk_theme.py`, and the arm
selectors and state names are GTK-required (they spell the toolkit
resource's rules). The separate `progressbar.osd` thin-bar trio (bare
`progressbar.osd { min-width: 3px; min-height: 3px; background-color:
transparent; }`, its borderless transparent `trough` and borderless
`progress`), the six `.osd scale slider` dark-thumb arms, `.scale-popup
button.flat` and the `colorchooser .popover.osd` corners stay out of scope
(recorded here as later surface plans, not this change).

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`,
append directly after the landed `.osd radio:disabled` group (the sheet's
last block) a dated provenance comment naming the missing reference surface,
this `gresource` probe and the reuse of the `PROGRESSBAR_*`/`SCALE_*`
recipes, followed by ten restated rules — four base groups matching the
landed plain progress-bar and scale recipes, split at the recipe boundaries
stock couples, and five disabled/backdrop groups repeating the same recipes
byte-for-byte (the landed sheet declares no disabled trough, fill or
highlight arm of its own, so all stock states keep the landed paints
unchanged), plus the one landed disabled-progress colour that stock's
`:disabled` group must not erase:

```css
.osd progressbar trough, progressbar .osd trough {
  background-color: #EEEEEE;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #999999;
  min-height: 10px;
  min-width: 10px;
}
.osd scale trough, scale .osd trough {
  background-color: #EEEEEE;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #999999;
  min-height: 6px;
  min-width: 6px;
}
.osd scale fill, scale .osd fill,
.osd scale highlight, scale .osd highlight {
  background-color: transparent;
  background-image: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}
.osd progressbar progress, progressbar .osd progress {
  background-color: #CCCCFF;
  background-image: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}
.osd progressbar trough:disabled, progressbar .osd trough:disabled {
  background-color: #EEEEEE;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #999999;
  min-height: 10px;
  min-width: 10px;
}
.osd scale trough:disabled, scale .osd trough:disabled {
  background-color: #EEEEEE;
  background-image: none;
  border: 1px solid #000000;
  border-radius: 0;
  box-shadow: inset 1px 1px #999999;
  min-height: 6px;
  min-width: 6px;
}
.osd scale fill:disabled:backdrop, .osd scale fill:disabled,
scale .osd fill:disabled {
  background-color: transparent;
  background-image: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}
.osd scale highlight:disabled, scale .osd highlight:disabled {
  background-color: transparent;
  background-image: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}
.osd progressbar progress:disabled, progressbar .osd progress:disabled {
  background-color: #999999;
  background-image: none;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  margin: 0;
}
```

(that is nine rules — the scale-highlight disabled group is the last of the
less-than-ten; spell each exactly as above, with the disabled progress
#999999 matching the landed `progressbar progress:disabled`). Touch no
landed rule: not the container band, the field arms, the ten check/radio
arms, the plain `progressbar`/`scale` rules or `MENU_CHECK`; leave the
`.osd scale slider` arms, the `progressbar.osd` thin-bar trio, `.scale-popup
button.flat`, `colorchooser .popover.osd` corners and the `button.osd` and
grouped `.osd button`/flat/suggested-action/destructive-action families for
later surface plans. (2) In `tests/test_gtk_theme.py`, add
`TestGtkTheme::test_osd_progress_scale` beside `test_osd_check_radio`: add
`PROGRESSBAR_PROGRESS`, `PROGRESSBAR_TROUGH`, `SCALE_EMPTY_FILL` and
`SCALE_TROUGH` to the existing `support.gtk_theme_spec` import list; build
one expected progress-trough dictionary (`PROGRESSBAR_TROUGH`), one expected
scale-trough dictionary (`SCALE_TROUGH`), one expected fill/highlight
dictionary (`SCALE_EMPTY_FILL`), one expected progress dictionary
(`PROGRESSBAR_PROGRESS`) and one expected disabled-progress dictionary
(`{**PROGRESSBAR_PROGRESS, "background-color": GREY}` — `GREY` is already
imported from `support.platinum_palette`); assert each of the twenty-one
selectors `tests/support/gtk_css.py::parse_css` splits out of the nine
against its recipe dictionary; assert the per-recipe dictionaries are
mutually equal and the disabled-progress background colour equals the landed
`progressbar progress:disabled` rule's `background-color` in `self.rules`
(the same cross-check `test_osd_entry_fields` makes against `entry:disabled`);
and add the scope assertion that the set of parsed sheet selectors
containing `.osd` and one of `trough`, `fill`, `highlight` or `progress`
equals exactly those twenty-one (`.scale-popup` carries none of the four
tokens, so the container-band selectors stay outside it). In the same
change, extend `test_osd_overlay_bands`'s existing scope filter — which
already excludes the restated `.osd entry`, `.osd spinbutton`, `.osd check`
and `.osd radio` selectors so they do not enter that test's container set —
to exclude selectors carrying any of the four meter tokens (`trough`,
`fill`, `highlight`, `progress`) the same way, or the new arms fail that
landed test's selector tokens scan. (Anchoring precedent: the landed fields
and check/radio plans both hit exactly this filter and recorded the
correction.) (3) In `docs/invariants.md`, in the `## gtk` table, append one
row: the guarantee — every stock GTK 3 OSD trough, fill and progress paint
draws the landed flat `#EEEEEE` trough face with its black border, zero
radius, `#999999` etch and landed minimum, the transparent scale fill and
highlight face, and the landed `#CCCCFF` progress fill with the `#999999`
disabled fill, identical in every stock state — with the test column naming
`tests/test_gtk_theme.py::TestGtkTheme::test_osd_progress_scale` (the
register parser resolves the column only against tests defined in the named
module, so cite the shared base cases `assert_progressbar` in
`tests/support/gtk_rule_cases.py` and `TestGtkTheme::test_scale` in the
provenance cell, not the test column); the provenance cell records the
missing reference surface, the gresource probe (libgtk-3 3.24.49
`gtk-contained.css`, probed 2026-10-30), the reused specs and their pinning
tests, the GTK-required arm spellings, the geometry the plain rules keep
governing, the untouched `progressbar.osd` thin-bar trio and `.osd scale
slider` arms, and the close-out that declaration checks do not establish
rendered pixels. Trim no landed row; `tests/test_invariants.py` parses the
register.

**Acceptance criteria.** The GTK 3 sheet carries the nine rules whose
complete parsed dictionaries are the twenty-one selectors above at exactly
the five recipe dictionaries; changing any of the twenty-one selectors,
deleting a rule, dropping a trough's `min-height`/`min-width`, changing the
disabled-progress fill away from `#999999`, or letting stock keep its
dark-translucent bubbles fails `test_osd_progress_scale`;
`test_osd_overlay_bands` (with its extended filter), `test_osd_entry_fields`,
`test_osd_check_radio`, `test_progressbar`, `test_scale`,
`test_only_palette_hex_literals`, `test_no_universal_selector`,
`test_icon_sources_point_at_shipped_assets` and
`test_no_status_or_translucent_shade_roles` stay green, and the landed
container, field, check/radio and plain meter rules keep their landed text.
Scope is the GTK 3 sheet, `tests/test_gtk_theme.py`, `docs/invariants.md` and
nothing else: no GTK 4 rule, no Firefox sheet, no new asset, colour literal
beyond the landed `#EEEEEE`, `#999999`, `#CCCCFF` and `transparent`,
dependency or `!important`. `make check` passes.

## Done

### Platinum GTK 4 OSD checks and radios: restate the stock dark indicator arms with the landed check and radio recipes (planned 2026-10-30 by the plan role; independent of the waiting GTK 3 OSD check-and-radio plan — it appends four check-and-radio arm groups to `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`, adds one test beside `test_osd_container_bands` in `tests/test_gtk4_theme.py` and appends one row to the `## gtk` invariants table, while that entry edits only the GTK 3 sheet and `tests/test_gtk_theme.py`; the shared documents are `docs/invariants.md`, where each entry appends its own row, and `tests/support/gtk_theme_spec.py`, from which both import `CHECK`/`RADIO` and neither edits, plus the shared base case both cite — no sheet selector, test function or suite overlaps)
— done 2026-10-30 by the feature role

**Goal.** The landed GTK 4 OSD container plan (`PLANS-DONE.md`, "Platinum
GTK 4 OSD overlay containers") repainted every stock OSD overlay container,
but the checks and radios inside those opaque Platinum `#DDDDDD` overlays
still paint the toolkit's dark indicators: the GTK 4 sheet declares nothing
for `.osd check` or `.osd radio` (grep: the sheet's OSD rests are `video
image.osd`, the two `progressbar.osd` trough groups and the landed
`.osd switch:checked` track, plus the landed container block), so the
Default resource's four `.osd` check-radio arms supply translucent dark
bubbles over an accent-tinted focus outline instead of the landed raised
`#DDDDDD` check face and flat white round radio. Restate all four arms with
the landed recipes, so a check or radio inside a Platinum OSD overlay draws
like one everywhere else.

**Verified facts (probed 2026-10-30, `gresource extract
/usr/lib/x86_64-linux-gnu/libgtk-4.so.1
/org/gtk/libgtk/theme/Default/Default-dark.css` and `Default-light.css`,
libgtk-4 4.18.6).** Both resources carry exactly four `.osd
check`/`.osd radio` arms: base and `:hover` (identical declarations in both
resources — dark: `color: #eeeeec`, `outline-color: rgba(21,83,158,0.7)`,
`border-color: rgba(0,0,0,0.7)`, `background-color: transparent`,
`background-image: image(rgba(38,38,38,0.7))`, `background-clip:
padding-box`; light: `outline-color: rgba(53,132,228,0.5)`,
`background-image: image(rgba(53,53,53,0.7))`, otherwise identical);
`:active` (adds `color: white`, `background-image: image(rgba(0,0,0,0.7))`
dark / `rgba(2,2,2,0.7)` light, `box-shadow: none`); `:disabled`
(`color: #8a8a89`, `background-image: image(rgba(58,58,57,0.5))` dark /
`color: #919190`, `image(rgba(71,71,71,0.5))` light). Neither resource
carries a `:backdrop` arm or any `:checked`/`:indeterminate` spelling on the
arm family. No arm sets geometry — `min-*`, `margin` — or an
`-gtk-icon-source`, or recolours the glyph, so the landed plain `check,
radio`, `check`, `radio` and `check:checked`/`radio:checked`/
`check:indeterminate`/`radio:indeterminate` rules (all governed beyond these
arms at equal or lower specificity) keep drawing the shipped assets and the
14px geometry, and the restatement needs no colour, glyph or geometry
decision beyond the recipes below. The platform style library carries no
`.osd check`/`.osd radio` arm at all (`gresource extract
/usr/lib/x86_64-linux-gnu/libadwaita-1.so.0
/org/gnome/Adwaita/styles/base.css`, libadwaita 1.7.6, probed 2026-10-30);
its only `.osd` check/radio rule is the `.osd popover.menu check, .osd
popover.menu radio { background: none; color: inherit; }` popover-menu
transparency override, which this plan leaves untouched alongside the other
libadwaita OSD descendants (buttons, progress, scale, cards) recorded as
later surfaces. No collected reference screenshot shows a GTK OSD
indicator, so this is a platform adaptation reusing the landed recipes —
`CHECK` and `RADIO` in `tests/support/gtk_theme_spec.py` (the raised
`#DDDDDD` check face with the `inset 1px 1px #FFFFFF, inset -1px -1px
#888888` etch, square corners and `margin: 0 4px`; the flat `#FFFFFF` round
radio) — pinned by the landed
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio`,
and the arm selectors and state names are GTK-required (they spell the
toolkit resources' rules).

**Approach and files.** (1) In `theme/gtk/org.macos8.desktop/gtk-4.0/gtk.css`,
append directly after the landed grouped OSD container block a dated
provenance comment naming the missing reference surface, both `gresource`
probes (libgtk-4 Default-dark/Default-light and the libadwaita no-arm fact),
the reuse of the `CHECK`/`RADIO` recipes and the cleared
`outline-color`, followed by four groups — one per stock state — each
restating the stock arm at `.osd check, .osd radio` with the two-rule
recipe shape (a base pair plus the radio override pair). The base group is
literally:

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
}
.osd radio {
  background-color: #FFFFFF;
  border-radius: 50%;
  box-shadow: none;
}
```

and the `:hover`, `:active` and `:disabled` groups repeat the identical
two-rule shape at the stock spellings `.osd check:hover, .osd radio:hover`
and so on — no stock arm carries a `:backdrop` spelling, and since the
state arms in both resources carry identical paints state-to-state (only
`color` and the translucent bubble differ, both overridden or void), every
state group repeats the recipes byte-for-byte, so a checked arm draws the
shipped glyph over the landed face exactly as it does outside an overlay.
The one clear riding in every group is `outline-color: #000000`: stock
claims an accent-tinted ring (`rgba(21,83,158,0.7)` dark,
`rgba(53,132,228,0.5)` light) in every arm, while the sheet's landed focus
black is `checkbutton:focus:focus-visible { outline-color: #000000 }`, so
black keeps the focus ring like the rest of the sheet (recorded in the
provenance comment). Stock's leftover `color`, `background-clip:
padding-box` and shadow claims stay undeclared: the shipped glyph assets
never recolour or shadow, the check node's node colour reaches no label
(sibling of the check box), and the 1px opaque black border already paints
the padding-box clip's border band — the same call the waiting GTK 3
sibling plan records. Touch no landed rule: not the landed container block,
plain `check`/`radio`/glyph rules, `video image.osd`, the two
`progressbar.osd` trough groups, `.osd switch:checked`, `MENU_CHECK` or the
`.osd popover.menu` transparency override; leave the `button.osd`, grouped
`.osd button`/flat/suggested-action/destructive-action, `.osd entry` and
`.osd spinbutton` field, `.osd progress`/scale, `.scale-popup button.flat`
and libadwaita OSD families for later surface plans (recorded here, not
this change). (2) In `tests/test_gtk4_theme.py`, add
`TestGtk4Theme::test_osd_check_radio` beside `test_osd_container_bands`: add
`CHECK` and `RADIO` to the existing `support.gtk_theme_spec` import list,
build one expected check dictionary (`{**CHECK, "outline-color": BLACK}` —
`BLACK` is already imported from `support.platinum_palette`; `CHECK` already
carries the geometry, margins, `background-image: none`, square corners and
the etch) and one expected radio dictionary (`{**RADIO, "outline-color":
BLACK}`), assert each of the eight per-state, per-node selectors
`tests/support/gtk_css.py::parse_css` splits out of the four groups against
its node's dictionary, assert the four `.osd check` dicts are mutually
equal and the four `.osd radio` dicts are mutually equal (the state arms
are byte-for-byte the recipes), and add the scope assertion that the set of
parsed sheet selectors containing `.osd check` or `.osd radio` equals
exactly those eight. In the same change, extend `test_osd_container_bands`'s
scope filter — the `landed` set that already holds `video image.osd`, the
two `progressbar.osd` trough selectors and `.osd switch:checked` — with the
eight new arm selectors, or the new arms fail that landed test's selector
tokens scan (`.osd check` contains the scanned `osd` token). (3) In
`docs/invariants.md`, in the `## gtk` table, append one row: the guarantee —
every stock GTK 4 OSD check and radio indicator arm draws the landed raised
`#DDDDDD` check face and flat white round radio with black borders, the
etched check shadow and black focus-outline colour, under whatever toolkit
resource loads, identical in all four stock states — with the test column
naming `tests/test_gtk4_theme.py::TestGtk4Theme::test_osd_check_radio` (the
register parser resolves the column only against tests defined in the named
module, so cite the shared base case
`tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_check_and_radio`
in the provenance cell, not the test column); the provenance cell records
the missing reference surface, the `gresource` probes (libgtk-4 4.18.6
Default-dark/Default-light and libadwaita 1.7.6 base.css, probed
2026-10-30), the reused `CHECK`/`RADIO` specs and their pinning test, the
GTK-required arm spellings, the black outline-colour clear, the geometric
and glyph rules the plain arms keep governing, the untouched libadwaita
`.osd popover.menu` transparent override, and the close-out that
declaration checks do not establish rendered pixels. Trim no landed row;
`tests/test_invariants.py` parses the register.

**Acceptance criteria.** The GTK 4 sheet carries the four groups whose
complete parsed dictionaries are the eight selectors at exactly the two
recipe dictionaries above; changing any of the eight selectors, deleting a
group, dropping the outline-colour clear or the etched check shadow, or
letting stock keep its dark bubbles or accent focus rings fails
`test_osd_check_radio`; `test_osd_container_bands` (with its extended
`landed` set), `test_check_and_radio`, `test_switch_osd_checked_track_color`,
`test_video_osd_image_corners`, `test_progressbar_osd_trough_paint`,
`test_only_palette_hex_literals`, `test_no_universal_selector`,
`test_icon_sources_point_at_shipped_assets` and
`test_no_status_or_translucent_shade_roles` stay green, and the landed
container, plain check/radio and remaining OSD rules keep their landed
text. Scope is the GTK 4 sheet, `tests/test_gtk4_theme.py`,
`docs/invariants.md` and nothing else: no GTK 3 rule, no Firefox sheet, no
new asset, colour literal beyond the landed `#DDDDDD`, `#FFFFFF`,
`#888888` and `#000000`, dependency or `!important`. `make check` passes.


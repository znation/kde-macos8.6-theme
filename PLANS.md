# Plans

Planned features, written by the plan loop and implemented by the feature loop.
Each plan: goal, approach, files touched, acceptance criteria. Move finished plans to Done.

## Planned

### Platinum GTK 3 palette swatches: clear the hover overlay bevel (planned 2026-10-30 by the plan role)

**Goal.** Keep the ordinary color swatch overlay flat on hover by clearing its decorative inset shadow, while retaining the chosen color.

**Grounding.** Queue and archive searches found corner coverage and add-color/color-button shadow resets, but no ordinary hover-overlay reset. The finished corner plan explicitly left hover shadows toolkit-controlled. The current GTK 3 sheet has no `colorswatch overlay:hover` rule. The installed `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, extracted with `gresource` on 2026-10-30, declares `colorswatch overlay:hover { box-shadow: inset 0 1px rgba(255, 255, 255, 0.4), inset 0 -1px rgba(0, 0, 0, 0.2); }`; its backdrop-hover and disabled overlay arms already clear shadows. No collected reference shows a GTK palette swatch hover state. Choosing `none` is a platform adaptation reusing the stock backdrop-hover treatment, consistent with the landed swatch shadow resets, rather than a new screenshot measurement.

**Approach and files.**
- In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, add a separate `colorswatch overlay:hover { box-shadow: none; }` after the existing swatch rules, with a dated comment naming the missing reference surface and resource above. Change no other declarations; keep drag-indicator shadows toolkit-controlled (their state selectors have higher specificity).
- In `tests/test_gtk_theme.py::TestGtkTheme`, add `test_color_swatch_hover_shadow` requiring exact dictionary equality with `{"box-shadow": "none"}` for that selector and equality with the existing color-button swatch reset. Extend `test_color_swatch_corners`'s `extra_declarations` mapping with precisely that selector and dictionary, so `tests/support/gtk_rule_cases.py::GtkSheetRuleCases.assert_color_swatch_corners` continues checking its exact selector inventory. Do not weaken the shared helper or GTK 4 expectations.
- Add a row under `## gtk` in `docs/invariants.md` naming the new test, adaptation source and date. Describe declaration coverage without claiming rendered pixels.

**Acceptance criteria.** Removing or changing the hover reset fails its test; the exact swatch inventory still passes. The new rule declares no fill, border, opacity, foreground, geometry or outline. Existing add-color and color-button shadow tests pass; GTK 4 stays outside this change. This is independent of the queued OSD popover corner rule and fits one implementation run in the three named files. `make check` passes.

### Platinum GTK 3 add-color action: use a black border (planned 2026-10-30 by the plan role)

**Goal.** Give the color chooser's add-color action a neutral black border through normal, hover and backdrop states, replacing the stock warm-grey edges.

**Grounding.** The existing four-arm `colorswatch#add-color-button overlay` reset group declares images, shadows and foreground but no border color. Queue and related finished-plan searches found corner, image, shadow and foreground work, with borders explicitly outside those scopes. The installed `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, extracted with `gresource` on 2026-10-30, sets `border-color: #cdc7c2` and `border-bottom-color: #bfb8b1` on base and hover, and `border-color: #d5d0cc` on backdrop. No collected reference shows this GTK action; black is a platform adaptation copied from this sheet's `frame > border, .frame` border, not a new screenshot measurement.

**Approach and files.**
- In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, add `border-color: #000000` to the existing four-arm add-color overlay group. The shorthand sets each edge, including the stock bottom-edge override. Extend the provenance comment with the missing reference surface, chosen source and date. Keep border widths and styles toolkit-controlled.
- In `tests/test_gtk_theme.py::TestGtkTheme`, add `test_add_color_border_colors` checking `border-color` against `BLACK` for base, hover, backdrop and backdrop-hover, and against the black token in the existing frame border. Extend `test_color_swatch_corners`'s exact `extra_declarations` dictionaries with that property. Keep the shared `tests/support/gtk_rule_cases.py::GtkSheetRuleCases.assert_color_swatch_corners` inventory strict, retaining any independently landed ordinary-hover entry.
- Add a `## gtk` row in `docs/invariants.md` naming the new test and dated adaptation provenance; describe declaration coverage without claiming rendered pixels.

**Acceptance criteria.** Removing or changing the border-color declaration on any of the four selectors fails the new test. The swatch inventory, corner, image, shadow and foreground tests pass. The change introduces no fill, width, style, spacing, outline or generic swatch override. GTK 4 stays outside this scope. This is independently mergeable alongside the ordinary-hover shadow plan and fits one implementation run in the three named files. `make check` passes.

## Done

### Platinum GTK 3 color buttons: clear the swatch's decorative shadow (planned 2026-10-30 by the plan role)
— done 2026-10-30 by the feature role

**Goal.** Remove the stock translucent bottom shadow from the color preview inside a GTK 3 color button, keeping its chosen color and existing square corners.

**Grounding.** The shipped GTK 3 sheet had corner and add-color image resets but no `button.color colorswatch:only-child` rule. The installed `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, inspected with `gresource` on 2026-10-30, declares a translucent bottom shadow on the base selector; its `.osd` and state arms clear it with `box-shadow: none`. No collected reference shows a GTK color button, so this is a platform adaptation.

**Approach and files.** Added the base shadow reset after the add-color image reset in the GTK 3 sheet, with a dated provenance comment. Extended the color-swatch corner selector inventory and added an exact declaration test. Added a GTK invariant documenting the missing reference and toolkit resource provenance. No swatch fill or geometry declarations changed.

**Acceptance criteria.** The new selector parses to exactly `{"box-shadow": "none"}`; the existing corner test admits it through its explicit mapping while retaining its exact selector inventory and existing corner/image expectations. The implementation diff adds no swatch color or geometry declaration. The CSS comment and invariant record the missing GTK color-button reference and the stock source of the chosen reset. `make check` passes. This is one CSS rule, a small test extension and an invariant row, independently mergeable from the open Kvantum bugs.

### Platinum GTK 3 add-color action: clear text and icon shadows (planned 2026-10-30 by the plan role)

**Goal.** Remove stock text and icon shadows from the color chooser's add-color action, extending its landed background-image reset with the sheet's existing shadow-free label treatment.

**Grounding.** Selector/property searches in the GTK 3 sheet and heading searches in this queue and `PLANS-DONE.md` found the corner and add-color background-image work, but no add-color label-shadow reset. The installed `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` resource in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0`, inspected with `gresource` on 2026-10-30, sets both `text-shadow` and `-gtk-icon-shadow` to `0 1px rgba(255, 255, 255, 0.769231)` on `colorswatch#add-color-button overlay` and its hover arm; its backdrop arm clears both. No collected reference shows this GTK action. Adopt the existing GTK sheet's `none` text/icon-shadow treatment as a platform adaptation, recording the missing reference surface and toolkit source rather than claiming a sampled value.

**Approach and files.**
- In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, extend the existing four-arm add-color image-reset group (base, `:hover`, `:backdrop`, `:backdrop:hover`) with `text-shadow: none` and `-gtk-icon-shadow: none`, and extend its dated provenance comment. These selectors tie or exceed the stock arm specificity. Keep the corner group and chosen-color swatches intact; change no box shadows, fills, borders, geometry or GTK 4 declarations.
- In `tests/test_gtk_theme.py::TestGtkTheme::test_color_swatch_corners`, extend the four add-color entries in the `extra_declarations` mapping to include the two shadow resets alongside `background-image: none`. Preserve any additional mapping entry introduced by the queued color-button swatch-shadow plan. Leave `tests/support/gtk_rule_cases.py::GtkSheetRuleCases.assert_color_swatch_corners` unchanged: its exact dictionary and selector-set checks already support these additions. Add `test_add_color_label_shadows` asserting both properties on the four explicit arms; retain `test_add_color_background_images`.
- Add a declaration guarantee under `## gtk` in `docs/invariants.md` naming the new test and the adaptation's missing reference and stock source. Do not claim rendered-pixel coverage.

**Acceptance criteria.** The corner helper checks exact dictionaries: the base overlay has its existing radius and image reset plus the two shadow resets; the three state overlays have the image and two shadow resets. Removing either shadow reset from the group fails the new test. The implementation changes only these label-shadow declarations, their provenance, tests and invariant. `make check` passes. This is independently mergeable from the queued color-button swatch-shadow work: the selectors and properties differ, and either merge order must retain both tests' explicit mapping additions.

### Platinum GTK 3 OSD spinbutton steppers: restate the stock horizontal and vertical `.osd spinbutton … button` arms with the landed flat-and-push-button recipe (planned 2026-10-30 by the plan role; independent of the queued `.osd button.destructive-action` entry ahead of it in this queue — both are append-only edits at the GTK 3 sheet's tail with disjoint selectors (a `spinbutton` carrying selector never carries `destructive-action`), the destructive entry's scope assertion sweeps only `button`-plus-`destructive-action` selectors and its entry states it touches no landed scope enumeration, while this entry's sole landed-scope edit is the `test_osd_entry_fields` sweep extension recorded below, so either merge order leaves the cascade right, neither edits the other's test, and the three BUGS.md `## Open` entries stay needs-review-bugfix))
— done 2026-10-30 by the feature role

**Goal.** The landed Platinum OSD overlay band (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the restated `.osd .scale-popup, … toolbar.osd` container painted `#DDDDDD`) fields its spinbuttons with the landed entry-field arms — the restated `.osd spinbutton:not(.vertical)`, `:focus`, `:backdrop` and `:disabled` group — but its stepper buttons still draw the stock claims: the horizontal stepper base arm paints a transparent face clipped of every visual claim except a left-edge separator (`border-style: none none none solid`, `rgba(0, 0, 0, 0.4)`), a near-white `#eeeeec` icon and nine `0 1px black` icon-shadow pair, its `:hover` arm a translucent `rgba(238, 238, 236, 0.1)` bubble with the same border claims, its `:backdrop` and `:disabled` arms transparent faces with grey `#919190` disabled icons — all invisible on the light band — and each edge arm rounds a stock 5px corner (`border-radius: 0 5px 5px 0` on `:dir(ltr):last-child`, `5px 0 0 5px` on `:dir(rtl):first-child`), while the vertical family paints full stock dark faces (`image(rgba(53, 53, 53, 0.9))` base and `:backdrop`, `rgba(83, 83, 83, 0.9)` on hover, `rgba(0, 0, 0, 0.7)` active, `rgba(71, 71, 71, 0.5)` disabled) with `#eeeeec`/`white` icons, a `0 1px black` shadow pair, an `rgba(238, 238, 236, 0.3)` outline and a `background-clip: padding-box` claim — everything other than a Platinum button on the light band. Restate the stock arms with the landed plain push-button recipe so a spinbutton's steppers inside a restated overlay draw the restated coherent unit: the landed `#FFFFFF` entry-field face beside raised `#DDDDDD` push-button faces in every stock state; the stock dark-bubble stepper distinction vanishes inside the overlays exactly as the landed plain, flat, suggested-action and queued destructive-action restatements erased theirs.

**Approach and files.** No collected reference screenshot shows a GTK OSD overlay or a spinbutton inside one; this is the same platform adaptation the landed container, entry, check/radio, meter, scale-thumb, thin-bar, push-button, flat-button and suggested-action plans made — reuse the landed recipe, record the stock claims the restatement overrides. The recipe comes from `tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_button` (the landed "flat"-family dictionaries `tests/test_gtk_theme.py::TestGtkTheme::test_osd_button` and `test_osd_suggested_action` compose) and the `FACE`, `BLACK`, `BUTTON_BEVEL`, `INVERTED_BUTTON_BEVEL` and `ETCH_DARK` specs in `tests/support/platinum_palette.py` and `tests/support/gtk_theme_spec.py`, taken directly so this entry needs nothing from any queued entry to land. The stock arms come from `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49, extracted with `gresource`, probed 2026-10-30: seven horizontal rules — `.osd spinbutton:not(.vertical) button` alone with each of `:dir(rtl)`, `:hover`, `:backdrop`, `:disabled`, `:dir(ltr):last-child` and `:dir(rtl):first-child` — and five vertical rules — `.osd spinbutton.vertical button:first-child` alone with each of `:hover`, `:active`, `:disabled` and `:backdrop`; twelve rules, twelve selectors) — re-probe the resource and re-derive every stock claim before writing.

(1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append a dated provenance comment and the twelve restated rules directly after the sheet's last restated `.osd` block (on the 2026-10-30 planning date that is the landed `.osd button.suggested-action:active:backdrop, …` block closing the sheet; should the queued destructive-action restatement land first, after whichever restated block is then last) at the stock spellings in the stock rule order — horizontal base, `:dir(rtl)`, `:hover`, `:backdrop`, `:disabled`, `:dir(ltr):last-child`, `:dir(rtl):first-child`, then vertical base, `:hover`, `:active`, `:disabled`, `:backdrop` — so each appends after its stock twin at equal specificity and pre-empts exactly the stock arm it restates. Each restated arm declares byte-equal the landed flat-and-push-button dictionary — `background-color: #DDDDDD` (`FACE`), `background-image: none`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` (`BUTTON_BEVEL`), `color: #000000` (`BLACK`), `outline-color: #000000`, `text-shadow: none`, `-gtk-icon-shadow: none` — except: the `:hover` arms repeat the base recipe byte-equal (they must defeat the stock hover's bubble and dark face); the vertical `:active` arm swaps only `box-shadow` to the landed inverted bevel `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` (`INVERTED_BUTTON_BEVEL`; the horizontal stock set carries no active arm — pressed steppers take the hover underline in stock, so nothing to restate there); the two `:disabled` arms keep the base bevel with the Inactive grey `color: #888888` (`ETCH_DARK`, the stock `#919190` cleared) and no `outline-color`, as every landed disabled arm claims none; and the `:backdrop` arms repeat the base recipe byte-equal, recipe `outline-color` included. Record in the provenance comment the claims the restatement erases: the stock `:dir(rtl)` separator flip (`border-style: none solid none none`) and the base arm's right-side separator (`border-style: none none none solid` over `rgba(0, 0, 0, 0.4)`, the hover's `rgba(0, 0, 0, 0.5)` variant) — both cleared by the recipe's full four-sided black border so a stepper draws identically in both directions; the two stock 5px edge radii on `:dir(ltr):last-child`/`:dir(rtl):first-child` — cleared by the recipe's `border-radius: 0`, byte-equal base restatements on both arms; the vertical family's `rgba(238, 238, 236, 0.3)` `outline-color` — restated black, as the landed `.osd` check/radio arms did; and the vertical family's `background-clip: padding-box` — the one clearance stock's own claims force here, as the landed suggested-action restatement's: every vertical stock arm claims `padding-box`, which left standing would clip the `#DDDDDD` face, so each restated vertical arm declares `background-clip: border-box` and the comment records it. The horizontal stock arms claim no `background-clip`, so the restated horizontal arms omit the property, exactly as the landed flat-button blocks stayed omitted. Leave undeclared so geometry keeps governing: `button.osd`'s `min-width: 26px; min-height: 32px` and `min-width: 34px` image-button arm (they never match a spinbutton leftmiddle stepper and are recorded as untouched), the `.osd spinbutton:not(.vertical) entry` `min-width: 28px` inner-entry rule, and the landed entry-field arms themselves.

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_spinbutton_buttons` beside the landed `test_osd_suggested_action`: build three expected dictionaries from the imported specs — the base button dictionary above, the disabled dictionary `{**base, "color": ETCH_DARK}` minus `"outline-color"`, and the active dictionary `{**base, "box-shadow": INVERTED_BUTTON_BEVEL}` — and build the horizontal variants of each so its dictionary omits `"background-clip"` while each vertical dictionary carries the literal `"background-clip": "border-box"`; assert each of the twelve selectors — the seven single-selector horizontal rules and five single-selector vertical rules listed in (1), no comma list in this family — against the right dictionary. Add the scope assertion that the set of parsed sheet selectors carrying the substring `spinbutton` plus the substring ` button` (an underscoreless, space-prefixed match that separates the stepper node from the spinbutton and entry node spellings — the bare `button` token is useless here because `spinbutton` contains it) plus one of the `.osd`, `app-notification`, `touch-selection` or `magnifier` tokens equals exactly that enumerated twelve — grep-verified 2026-10-30 that no landed sheet selector pairs a `spinbutton` and a stepper `button` spelling (the only hits for either pair in today's sheet are provenance-comment lines inside queued-entry records) — so the scan kills dupes and stray variants. In the same change, extend `test_osd_entry_fields`' existing exact-set sweep — selectors carrying `.osd entry` or `.osd spinbutton` — with the same `" button" not in selector` exclusion so the stepper selectors stay out of that landed test's exact-set (the sweep keeps enumerating today's four field comma lists: `test_osd_entry_fields`' four pairs `.osd spinbutton:not(.vertical)`/`.osd entry` through `:disabled`), mirroring the landed push-button plan's `button`-token exclusion in `test_osd_overlay_bands`'s filter, which already clears this entry's twelve selectors since each carries the `button` token; no change beyond that one sweep line to `test_osd_overlay_bands`, `test_osd_button`, `test_osd_flat_button`, `test_osd_suggested_action` or any other landed scope enumeration.

(3) In `docs/invariants.md`, in the `## gtk` table, append one row following the row pinned by `test_osd_suggested_action`: the guarantee — every stock GTK 3 spinbutton stepper (`:first-child` up and down steppers in the horizontal and vertical `.osd spinbutton` node arms) inside the restated Platinum OSD overlay band draws the landed push-button face (`#DDDDDD`, full black square border and bevel, zero radius, black label, grey `#888888` insensitive label, inverted bevel where the stock arms claim a pressed state) in every stock state, the stock dark-bubble and separator/edge-radius claims erased inside overlays as the plain, flat and suggested-action restatements erased theirs — with the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_osd_spinbutton_buttons`, the provenance cell naming the missing reference surface, the gresource probe, the recipe reuse, the erased stock claims and the cleared vertical `background-clip: padding-box` claim (restated `border-box`, matching the suggested-action adaptation), and the declaration-checks note the neighbouring landed rows carry.

**Acceptance criteria.**
- Each of the twelve enumerated selectors parses to the recipe dictionary its arm maps to; the dictionaries differ only where the recipe itself differs — `color` on the two disabled arms, `box-shadow` on the vertical `:active` arm, `outline-color` absent on the disabled arms, and `background-clip` present only on the vertical arms.
- The scope assertion enumerates exactly the twelve restated selectors and nothing else; `test_osd_overlay_bands`, `test_osd_button`, `test_osd_flat_button`, `test_osd_suggested_action` and every landed `.osd` scope enumeration still pass with no change at all, and `test_osd_entry_fields` still enumerates exactly its four field comma lists.
- The sheet's added block sits after the sheet's last restated `.osd` block on the implementation date; no landed rule in the sheet is touched, and the `.osd button.color colorswatch`, `.osd .scale-popup button.flat`, `.scale-popup button:hover` and `colorchooser .popover.osd` arms stay queued (recorded here, not this change); the generic spinbutton stepper arms outside `.osd` keep governing outside overlays, as do `.osd spinbutton:not(.vertical) entry` and the two `button.osd` geometry minimum arms.
- One new `## gtk` invariants row names the missing reference surface, the toolkit probe, the recipe reuse, the erased stepper distinction and the cleared clip claim.
- `make check` is green.

Size: twelve restated rules (twelve selectors) plus one test (with the `test_osd_entry_fields` sweep line recorded above) plus one invariants row and no other filter change — a single implementation run's worth of change; the colorswatch, `.scale-popup` flat and `colorchooser .popover.osd` arms are queued separately after this entry lands.
### Platinum GTK 3 OSD spinbutton steppers: restate the stock horizontal and vertical `.osd spinbutton … button` arms with the landed flat-and-push-button recipe (planned 2026-10-30 by the plan role; independent of the queued `.osd button.destructive-action` entry ahead of it in this queue — both are append-only edits at the GTK 3 sheet's tail with disjoint selectors (a `spinbutton` carrying selector never carries `destructive-action`), the destructive entry's scope assertion sweeps only `button`-plus-`destructive-action` selectors and its entry states it touches no landed scope enumeration, while this entry's sole landed-scope edit is the `test_osd_entry_fields` sweep extension recorded below, so either merge order leaves the cascade right, neither edits the other's test, and the three BUGS.md `## Open` entries stay needs-review-bugfix))
— done 2026-10-30 by the feature role

**Goal.** The landed Platinum OSD overlay band (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the restated `.osd .scale-popup, … toolbar.osd` container painted `#DDDDDD`) fields its spinbuttons with the landed entry-field arms — the restated `.osd spinbutton:not(.vertical)`, `:focus`, `:backdrop` and `:disabled` group — but its stepper buttons still draw the stock claims: the horizontal stepper base arm paints a transparent face clipped of every visual claim except a left-edge separator (`border-style: none none none solid`, `rgba(0, 0, 0, 0.4)`), a near-white `#eeeeec` icon and nine `0 1px black` icon-shadow pair, its `:hover` arm a translucent `rgba(238, 238, 236, 0.1)` bubble with the same border claims, its `:backdrop` and `:disabled` arms transparent faces with grey `#919190` disabled icons — all invisible on the light band — and each edge arm rounds a stock 5px corner (`border-radius: 0 5px 5px 0` on `:dir(ltr):last-child`, `5px 0 0 5px` on `:dir(rtl):first-child`), while the vertical family paints full stock dark faces (`image(rgba(53, 53, 53, 0.9))` base and `:backdrop`, `rgba(83, 83, 83, 0.9)` on hover, `rgba(0, 0, 0, 0.7)` active, `rgba(71, 71, 71, 0.5)` disabled) with `#eeeeec`/`white` icons, a `0 1px black` shadow pair, an `rgba(238, 238, 236, 0.3)` outline and a `background-clip: padding-box` claim — everything other than a Platinum button on the light band. Restate the stock arms with the landed plain push-button recipe so a spinbutton's steppers inside a restated overlay draw the restated coherent unit: the landed `#FFFFFF` entry-field face beside raised `#DDDDDD` push-button faces in every stock state; the stock dark-bubble stepper distinction vanishes inside the overlays exactly as the landed plain, flat, suggested-action and queued destructive-action restatements erased theirs.

**Approach and files.** No collected reference screenshot shows a GTK OSD overlay or a spinbutton inside one; this is the same platform adaptation the landed container, entry, check/radio, meter, scale-thumb, thin-bar, push-button, flat-button and suggested-action plans made — reuse the landed recipe, record the stock claims the restatement overrides. The recipe comes from `tests/support/gtk_rule_cases.py::GtkSheetRuleCases::test_button` (the landed "flat"-family dictionaries `tests/test_gtk_theme.py::TestGtkTheme::test_osd_button` and `test_osd_suggested_action` compose) and the `FACE`, `BLACK`, `BUTTON_BEVEL`, `INVERTED_BUTTON_BEVEL` and `ETCH_DARK` specs in `tests/support/platinum_palette.py` and `tests/support/gtk_theme_spec.py`, taken directly so this entry needs nothing from any queued entry to land. The stock arms come from `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49, extracted with `gresource`, probed 2026-10-30: seven horizontal rules — `.osd spinbutton:not(.vertical) button` alone with each of `:dir(rtl)`, `:hover`, `:backdrop`, `:disabled`, `:dir(ltr):last-child` and `:dir(rtl):first-child` — and five vertical rules — `.osd spinbutton.vertical button:first-child` alone with each of `:hover`, `:active`, `:disabled` and `:backdrop`; twelve rules, twelve selectors) — re-probe the resource and re-derive every stock claim before writing.

(1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append a dated provenance comment and the twelve restated rules directly after the sheet's last restated `.osd` block (on the 2026-10-30 planning date that is the landed `.osd button.suggested-action:active:backdrop, …` block closing the sheet; should the queued destructive-action restatement land first, after whichever restated block is then last) at the stock spellings in the stock rule order — horizontal base, `:dir(rtl)`, `:hover`, `:backdrop`, `:disabled`, `:dir(ltr):last-child`, `:dir(rtl):first-child`, then vertical base, `:hover`, `:active`, `:disabled`, `:backdrop` — so each appends after its stock twin at equal specificity and pre-empts exactly the stock arm it restates. Each restated arm declares byte-equal the landed flat-and-push-button dictionary — `background-color: #DDDDDD` (`FACE`), `background-image: none`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` (`BUTTON_BEVEL`), `color: #000000` (`BLACK`), `outline-color: #000000`, `text-shadow: none`, `-gtk-icon-shadow: none` — except: the `:hover` arms repeat the base recipe byte-equal (they must defeat the stock hover's bubble and dark face); the vertical `:active` arm swaps only `box-shadow` to the landed inverted bevel `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` (`INVERTED_BUTTON_BEVEL`; the horizontal stock set carries no active arm — pressed steppers take the hover underline in stock, so nothing to restate there); the two `:disabled` arms keep the base bevel with the Inactive grey `color: #888888` (`ETCH_DARK`, the stock `#919190` cleared) and no `outline-color`, as every landed disabled arm claims none; and the `:backdrop` arms repeat the base recipe byte-equal, recipe `outline-color` included. Record in the provenance comment the claims the restatement erases: the stock `:dir(rtl)` separator flip (`border-style: none solid none none`) and the base arm's right-side separator (`border-style: none none none solid` over `rgba(0, 0, 0, 0.4)`, the hover's `rgba(0, 0, 0, 0.5)` variant) — both cleared by the recipe's full four-sided black border so a stepper draws identically in both directions; the two stock 5px edge radii on `:dir(ltr):last-child`/`:dir(rtl):first-child` — cleared by the recipe's `border-radius: 0`, byte-equal base restatements on both arms; the vertical family's `rgba(238, 238, 236, 0.3)` `outline-color` — restated black, as the landed `.osd` check/radio arms did; and the vertical family's `background-clip: padding-box` — the one clearance stock's own claims force here, as the landed suggested-action restatement's: every vertical stock arm claims `padding-box`, which left standing would clip the `#DDDDDD` face, so each restated vertical arm declares `background-clip: border-box` and the comment records it. The horizontal stock arms claim no `background-clip`, so the restated horizontal arms omit the property, exactly as the landed flat-button blocks stayed omitted. Leave undeclared so geometry keeps governing: `button.osd`'s `min-width: 26px; min-height: 32px` and `min-width: 34px` image-button arm (they never match a spinbutton leftmiddle stepper and are recorded as untouched), the `.osd spinbutton:not(.vertical) entry` `min-width: 28px` inner-entry rule, and the landed entry-field arms themselves.

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_spinbutton_buttons` beside the landed `test_osd_suggested_action`: build three expected dictionaries from the imported specs — the base button dictionary above, the disabled dictionary `{**base, "color": ETCH_DARK}` minus `"outline-color"`, and the active dictionary `{**base, "box-shadow": INVERTED_BUTTON_BEVEL}` — and build the horizontal variants of each so its dictionary omits `"background-clip"` while each vertical dictionary carries the literal `"background-clip": "border-box"`; assert each of the twelve selectors — the seven single-selector horizontal rules and five single-selector vertical rules listed in (1), no comma list in this family — against the right dictionary. Add the scope assertion that the set of parsed sheet selectors carrying the substring `spinbutton` plus the substring ` button` (an underscoreless, space-prefixed match that separates the stepper node from the spinbutton and entry node spellings — the bare `button` token is useless here because `spinbutton` contains it) plus one of the `.osd`, `app-notification`, `touch-selection` or `magnifier` tokens equals exactly that enumerated twelve — grep-verified 2026-10-30 that no landed sheet selector pairs a `spinbutton` and a stepper `button` spelling (the only hits for either pair in today's sheet are provenance-comment lines inside queued-entry records) — so the scan kills dupes and stray variants. In the same change, extend `test_osd_entry_fields`' existing exact-set sweep — selectors carrying `.osd entry` or `.osd spinbutton` — with the same `" button" not in selector` exclusion so the stepper selectors stay out of that landed test's exact-set (the sweep keeps enumerating today's four field comma lists: `test_osd_entry_fields`' four pairs `.osd spinbutton:not(.vertical)`/`.osd entry` through `:disabled`), mirroring the landed push-button plan's `button`-token exclusion in `test_osd_overlay_bands`'s filter, which already clears this entry's twelve selectors since each carries the `button` token; no change beyond that one sweep line to `test_osd_overlay_bands`, `test_osd_button`, `test_osd_flat_button`, `test_osd_suggested_action` or any other landed scope enumeration.

(3) In `docs/invariants.md`, in the `## gtk` table, append one row following the row pinned by `test_osd_suggested_action`: the guarantee — every stock GTK 3 spinbutton stepper (`:first-child` up and down steppers in the horizontal and vertical `.osd spinbutton` node arms) inside the restated Platinum OSD overlay band draws the landed push-button face (`#DDDDDD`, full black square border and bevel, zero radius, black label, grey `#888888` insensitive label, inverted bevel where the stock arms claim a pressed state) in every stock state, the stock dark-bubble and separator/edge-radius claims erased inside overlays as the plain, flat and suggested-action restatements erased theirs — with the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_osd_spinbutton_buttons`, the provenance cell naming the missing reference surface, the gresource probe, the recipe reuse, the erased stock claims and the cleared vertical `background-clip: padding-box` claim (restated `border-box`, matching the suggested-action adaptation), and the declaration-checks note the neighbouring landed rows carry.

**Acceptance criteria.**
- Each of the twelve enumerated selectors parses to the recipe dictionary its arm maps to; the dictionaries differ only where the recipe itself differs — `color` on the two disabled arms, `box-shadow` on the vertical `:active` arm, `outline-color` absent on the disabled arms, and `background-clip` present only on the vertical arms.
- The scope assertion enumerates exactly the twelve restated selectors and nothing else; `test_osd_overlay_bands`, `test_osd_button`, `test_osd_flat_button`, `test_osd_suggested_action` and every landed `.osd` scope enumeration still pass with no change at all, and `test_osd_entry_fields` still enumerates exactly its four field comma lists.
- The sheet's added block sits after the sheet's last restated `.osd` block on the implementation date; no landed rule in the sheet is touched, and the `.osd button.color colorswatch`, `.osd .scale-popup button.flat`, `.scale-popup button:hover` and `colorchooser .popover.osd` arms stay queued (recorded here, not this change); the generic spinbutton stepper arms outside `.osd` keep governing outside overlays, as do `.osd spinbutton:not(.vertical) entry` and the two `button.osd` geometry minimum arms.
- One new `## gtk` invariants row names the missing reference surface, the toolkit probe, the recipe reuse, the erased stepper distinction and the cleared clip claim.
- `make check` is green.

Size: twelve restated rules (twelve selectors) plus one test (with the `test_osd_entry_fields` sweep line recorded above) plus one invariants row and no other filter change — a single implementation run's worth of change; the colorswatch, `.scale-popup` flat and `colorchooser .popover.osd` arms are queued separately after this entry lands.

### Platinum GTK 3 OSD flat buttons: restate the grouped `.app-notification button.flat, …, .osd button.flat` arms with the landed push-button recipe (planned 2026-10-30 by the plan role; independent of the queued `.osd`/`button.osd` push-button entry ahead of it in this queue — both are append-only edits at the GTK 3 sheet's tail, so either merge order leaves the cascade right, each entry owns its disjoint selectors (`button.flat` versus plain `button` arms), and neither edits the other's test beyond pushing the same one-token clearance into `test_osd_overlay_bands`'s filter — the `button`-token exclusion the two entries word identically, so whichever lands first applies it and the second sees it already there; the three BUGS.md `## Open` entries stay needs-review-bugfix)
— done 2026-10-30 by the feature role

**Goal.** The landed Platinum OSD container band (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the `.osd .scale-popup, … toolbar.osd` block painted `#DDDDDD` with black text) still gives the resource's flat junior buttons their own dark arms inside every restated overlay: the grouped `.app-notification button.flat, popover.background.touch-selection button.flat, popover.background.magnifier button.flat, .osd button.flat` base arm leaves the button faceless with `box-shadow: none` and `text-shadow: 0 1px black`, its `:hover` and `:active`/`:checked` arms switch the label to `color: white` and paint translucent dark faces, and its `:disabled` arm paints `#919190` text — every state something other than a Platinum button on the light band. Restate the five grouped flat arms with the landed plain push-button recipe so a flat button inside a restated overlay draws the same raised face as every other button there; the stock flat-versus-raised distinction vanishes inside the overlays, and the provenance comment records that deviation.

**Approach and files.** No collected reference screenshot shows a GTK OSD overlay or a button inside one; this is the same platform adaptation the landed container, entry, check/radio, meter, scale-thumb and thin-bar plans made — reuse the landed recipe, record the stock claims the restatement overrides. The recipe comes from `tests/support/gtk_rule_cases.py::assert_button` and the `FACE`, `BLACK`, `BUTTON_BEVEL`, `INVERTED_BUTTON_BEVEL` and `ETCH_DARK` specs in `tests/support/gtk_theme_spec.py` — the same recipe source the queued push-button entry names, taken directly so this entry needs nothing from it to land. The stock arms come from `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49), the five grouped `.app-notification button.flat, …` rules between the flat base arm and the `button.suggested-action` block (probed 2026-10-30) — re-probe the resource and re-derive every stock claim before writing; the base arm carries duplicate `box-shadow` and `text-shadow` keys whose last values win and the `:disabled` arm carries duplicate `background-image`, `border-color` and `box-shadow` keys likewise, and restating byte-equal full-recipe deltas sidesteps the stock spelling entirely.

(1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append a dated provenance comment and five restated rules directly after the landed `.app-notification button, …, .osd button` block the queued push-button entry places at the sheet tail, at the stock spellings so they pre-empt exactly the stock arms they restate. Each restated arm declares byte-equal the landed plain push-button recipe — `background-color: #DDDDDD`, `background-image: none`, `border: 1px solid #000000`, `border-radius: 0`, `box-shadow: inset 1px 1px #FFFFFF, inset -1px -1px #AAAAAA` (`BUTTON_BEVEL`), `color: #000000` (`#888888`, `ETCH_DARK`, on the disabled arm), `text-shadow: none`, `-gtk-icon-shadow: none`, and `outline-color: #000000` in the base, hover, active/checked and backdrop arms, as the landed plain-button arms carry it there, while the disabled arm keeps the base bevel with grey text and no `outline-color` because its stock counterpart claims none. The `:hover` arm repeats the full base recipe (it must defeat the stock hover's translucent dark face and white label), the `:active`/`:checked` arms swap only `box-shadow` to the landed inverted bevel `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF` (`INVERTED_BUTTON_BEVEL`), the disabled arm keeps the base bevel with grey text, and the `:backdrop` arm repeats the full base recipe byte-equally; the five blocks keep the stock comma-list spellings in the stock arm order — base, `:hover`, `:disabled`, `:backdrop`, `:active`/`:checked` last — so the active/checked restatement wins the sheet-order tie with the hover arm exactly as stock's order does.

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_flat_button` beside the landed `test_osd_entry_fields`: build two expected dictionaries from the imported specs — the base button dictionary above and the disabled dictionary, the landed disabled dictionary the queued push-button test pins (`**base` without its `outline-color`, with `color: ETCH_DARK`) — and assert each of the 24 selectors `tests/support/gtk_css.py::parse_css` splits out of the five grouped comma lists against the right dictionary (the `.app-notification button.flat` group and its `:hover`, `:disabled` and `:backdrop` splits — four selectors each; the shared `:active`/`:checked` list — eight selectors spanning the four families' `:active` and `:checked` parts in the stock split — against the inverted-bevel variant). Add the scope assertion that the set of parsed sheet selectors carrying both the token `button` and the token `flat` equals exactly that enumerated set — grep-verified today that no landed sheet selector carries `button.flat`, so the scan kills dupes and stray variants. Corrected 2026-10-30 by the feature role: the landed push-button entry has already applied the identically-worded `button`-token exclusion into `test_osd_overlay_bands`'s scope filter (verified in that filter), and `test_osd_button`'s own scope scan — selectors carrying the bare `button` token under the `.osd`/`app-notification`/`touch-selection`/`magnifier` tokens — folds the new grouped `button.flat` selectors in, so the same change excludes `flat` there, mirroring that scan's `spinbutton` exclusion; in the same change, `test_app_notification_band`'s `.app-notification` exact-set grows by its six new grouped flat members (the base, `:hover`, `:active`, `:checked`, `:disabled` and `:backdrop` splits).

(3) In `docs/invariants.md`, in the `## gtk` table, append one row: the guarantee — every stock GTK 3 arm on flat buttons inside the restated Platinum OSD overlay band draws the landed push-button face (`#DDDDDD`, black square border and bevel, zero radius, black label, grey insensitive label, inverted bevel when active or checked) in every stock state, the stock flat distinction erased inside overlays — with the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_osd_flat_button`, the provenance cell naming the missing reference surface, the gresource probe and the re-derived stock claims, and the declaration-checks note the neighbouring landed rows carry.

**Acceptance criteria.**
- Each of the 24 enumerated selectors parses to the recipe dictionary its arm maps to; the dictionaries differ only where the landed recipe itself differs — `box-shadow` on the active/checked arms and, on the disabled arm, `color` plus the base arm's absent `outline-color`.
- The scope assertion enumerates exactly the 24 restated selectors and nothing else; `test_osd_overlay_bands` passes without a change (its `button`-token exclusion is already landed) and `test_osd_button` passes with only the `flat` exclusion added to its scan, while `test_app_notification_band`'s exact-set gains its six flat members.
- The sheet's added block sits after whichever `.osd`-tail block is last on the implementation date; no landed rule in the sheet is touched, and the `.osd button.suggested-action`, `.osd button.destructive-action`, `.osd button.color colorswatch`, `.osd spinbutton … button`, `.osd .scale-popup button.flat` and `colorchooser .popover.osd` arms stay queued (recorded here, not this change).
- One new `## gtk` invariants row names the missing reference surface, the toolkit probe, the recipe reuse and the erased flat distinction.
- `make check` is green.

Size: five restated rules (24 grouped selectors) plus one test plus one filter token plus one invariants row — a single implementation run's worth of change; the suggested-action/destructive-action/colorswatch and spinbutton-button arms are queued separately after this entry lands.

### Platinum GTK 3 OSD push buttons: restate the `button.osd` and grouped `.osd button` arms with the landed push-button recipe (planned 2026-10-30 by the plan role; independent — the landed thin-bar entry appended only the two `progressbar.osd` selectors after the same sheet tail and grew only `test_osd_progress_scale`, this appends only `button`-selector arms and adds its own test beside it, the three BUGS.md `## Open` entries stay needs-review-bugfix, and the queued `.osd button.flat` entry appended after this entry owns only the grouped `button.flat` selectors — the rest of the landed .osd plans both explicitly left the `button.osd` and grouped `.osd button` families for later surface plans, recorded in their leave-untouched lists. Re-filed 2026-10-30 by the plan role from ## Done, where the thin-bar feature's section move stranded it unstamped with nothing implemented anywhere (grep: no restated `button.osd` selector in the GTK 3 sheet, no `test_osd_button` in `tests/test_gtk_theme.py`, no matching `## gtk` row in `docs/invariants.md`)
— done 2026-10-30 by the feature role

**Goal.** Inside the landed Platinum OSD container band (`theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, the `.osd .scale-popup, … toolbar.osd` block painted `#DDDDDD` with black text), a push button still paints the toolkit resource's stock dark arms: `.osd button { color: #eeeeec; background-color: transparent; background-image: image(rgba(53,53,53,0.9)); border: none; box-shadow: none; text-shadow: 0 1px black; -gtk-icon-shadow: 0 1px black; outline-color: rgba(238,238,236,0.3); }` and `button.osd { … border-radius: 5px; … }` — near-white text on the landed light band. Restate the two same-face families — the self-class `button.osd` rules and the grouped `.app-notification button, …, .osd button` rules — with the landed plain push-button recipe so every stock state inside the restated overlays draws the landed Platinum button.

**Approach and files.** No collected reference screenshot shows a GTK OSD overlay or a button inside one; this is the same platform adaptation the landed container, entry, check/radio, meter and scale-thumb plans made — reuse the landed recipe, record the stock claims the restatement overrides. The stock arms and claims come from `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49), the file's lines between the `button.osd` base rule and the `.osd button:backdrop` grouped rule — re-probe the file and re-derive the exact stock claims before writing (the resource's arm list: `button.osd`, `button.osd.image-button` geometry, `button.osd:hover`, `button.osd:active, button.osd:checked`, `button.osd:disabled:backdrop, button.osd:disabled`, `button.osd:backdrop`, and the grouped `.app-notification button, .app-notification.frame button, .csd popover.background.touch-selection button, .csd popover.background.magnifier button, popover.background.touch-selection button, popover.background.magnifier button, .osd button` group with its `:hover`, `:active`/`:checked` (plus `:active:backdrop`, `:checked:backdrop`), `:disabled` (plus `:disabled:backdrop`) and `:backdrop` lines).

(1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append a dated provenance comment and ten restated rules (the 37 selectors below come from the ten restated comma lists; the plan's earlier "eleven" counted the stock `button.osd.image-button` arm, which this entry leaves undeclared) directly after the landed `progressbar.osd progress` arm — the sheet's last block now the thin-bar entry has landed (or after the landed `.osd` flat-button block, should that entry land first) — at the stock spellings so they pre-empt exactly the stock arms they restate, and leave the stock geometry claims governed: do not restate `button.osd`'s `min-width: 26px; min-height: 32px`, the `button.osd.image-button` min-width arm, or any grouped geometry. Each restated arm declares byte-equal the landed plain button recipe from `tests/support/gtk_rule_cases.py::assert_button` — `background-color: #DDDDDD`, `background-image: none`, `border: 1px solid #000000`, `border-radius: 0` (square corner, overriding the stock 5px radius; record that deviation in the provenance comment) — plus the landed adjustments the landed `.osd` entry restatements carry: `color: #000000` (`#888888` on the disabled arms — the landed Inactive grey the sheet's `label:disabled, entry:disabled, spinbutton:disabled` block uses), `text-shadow: none`, `-gtk-icon-shadow: none`, and `outline-color: #000000` in the base, hover and active arms whose stock counterparts claim `rgba(238,238,236,0.3)`. Hover arms repeat the full base recipe (they must defeat the stock hover's rgba face and border claims), the `:active`/`:checked` (and `:active:backdrop`/`:checked:backdrop`) arms swap only `box-shadow` to the landed inverted bevel `inset 1px 1px #AAAAAA, inset -1px -1px #FFFFFF`, the disabled arms keep the base bevel with grey text, and the backdrop arms repeat the full base recipe byte-equally.

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_button` beside the landed `test_osd_entry_fields`: build two expected dictionaries from the imported `FACE`, `BLACK`, `BUTTON_BEVEL`, `INVERTED_BUTTON_BEVEL` and `ETCH_DARK` — the base button dictionary above and the disabled dictionary `{**base, "color": ETCH_DARK}` — assert each of the 37 selectors `tests/support/gtk_css.py::parse_css` splits out of the ten restated comma lists against the right dictionary (self-class: `button.osd`, `button.osd:hover`, `button.osd:active`, `button.osd:checked`, `button.osd:disabled:backdrop`, `button.osd:disabled`, `button.osd:backdrop`; grouped base seven: `.app-notification button` through `.osd button`; grouped hover four; grouped active/checked ten; grouped disabled five; grouped backdrop four), and add the scope assertion that the set of parsed sheet selectors carrying the token `button` plus one of `.osd`, `app-notification`, `touch-selection` or `magnifier` equals exactly that enumerated set (the landed sheet carries none today, so the scan kills both dupes and stray variants). In the same change, extend `test_osd_overlay_bands`'s existing scope filter — which already excludes the restated `.osd entry`, `.osd spinbutton`, `.osd check`, `.osd radio`, `.osd scale slider` and meter-token selectors, and which sweeps the `touch-selection`- and `magnifier`-carrying selectors into its own container set — to exclude selectors carrying the token `button` the same way, so neither the self-class nor any of the grouped comma parts (`.csd popover.background.touch-selection button` and friends) enter the landed test's selector scan.

(3) In `docs/invariants.md`, in the `## gtk` table, append one row: the guarantee — every stock GTK 3 arm on `button.osd` and on buttons inside the landed Platinum overlay band draws the landed push-button face (`#DDDDDD`, black square border and bevel, zero radius, black label, grey insensitive label, inverted bevel when checked), identical in every stock state — with the test column naming `tests/test_gtk_theme.py::TestGtkTheme::test_osd_button`, the provenance cell the missing reference surface, the gresource probe, the re-derived stock claims, the stock geometry kept governing (the 26px/32px minimums and the image-button 34px) and the overridden 5px radius, the leave-untouched record and the declaration-checks note.

**Acceptance criteria.**
- Each of the 37 enumerated selectors parses to the recipe dictionary its arm maps to; the dictionaries differ only where the recipe itself differs — `color` on the disabled arms, `box-shadow` on the active/checked arms.
- The scope assertion enumerates exactly the arms this entry restates; every landed `.osd` scope enumeration still passes without a change beyond the `test_osd_overlay_bands` extension and the seven-member growth of `test_app_notification_band`'s `.app-notification` exact-set (the plan had counted the clearance as one filter token; the landed `.app-notification button` members join that enumeration too, and a bare-`button` token scan excludes `spinbutton` field spellings).
- The sheet's added block sits after the landed `progressbar.osd progress` arm (or the landed `.osd` flat-button block, should that entry land first); no landed rule in the sheet is touched, and the queue lacks the `.flat`, `.suggested-action`, `.destructive-action`, `.color colorswatch` and `.osd spinbutton … button` arms — leave them for later surface plans (recorded here, not this change).
- One new `## gtk` invariants row names the missing reference surface, the toolkit probe and the recipe reuse.
- `make check` is green.

Size: ten restated rules (37 grouped selectors) plus one test (with the `test_osd_overlay_bands` filter token and the `test_app_notification_band` growth recorded above) plus one invariants row — a single implementation run's worth of change; the flat/suggested/destructive/colorswatch and spinbutton-button arms are queued separately after this lands.

### Platinum GTK 3 OSD thin-bar trio: restate the stock `progressbar.osd` trough and progress arms with the landed base meter recipes (planned 2026-10-30 by the plan role; independent — nothing else waits, and the three BUGS.md `## Open` entries stay needs-review-bugfix behind this plan's only overlaps being append-only sheet lines and one test the landed `test_osd_progress_scale` owns; the parked plans recorded in `PLANS.md` `## Done` — the landed GTK 3 OSD meter entry — explicitly held this trio out of scope for a queued surface plan, and the landed GTK 4 sheet already draws the same widget with the base paint, so this entry only closes the GTK 3 side: it appends two restated rules to `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` after the landed `.osd progressbar progress:disabled` block at the sheet tail, grows the selector set in `tests/test_gtk_theme.py::TestGtkTheme::test_osd_progress_scale`'s clearance check, adds `TestGtkTheme::test_osd_thin_bar` beside it, and appends one row to the `## gtk` invariants table in `docs/invariants.md` following the row pinned by `test_osd_progress_scale` — no GTK 4 file, selector, test or suite is touched)
— done 2026-10-30 by the feature role

**Goal.** A self-class `.osd` GTK 3 progress bar (`progressbar.osd`, the thin indicator Epiphany-style headerbars draw) still paints the toolkit resource's stock thin-bar arms: a transparent trough with `border-style: none` and `box-shadow: none` over the landed `#CCCCFF` fill — while the landed GTK 4 sheet reuses the base paint for the same widget (`progressbar.osd > trough` face, pinned by `test_progressbar_osd_trough_paint`) and the landed GTK 3 `.osd progressbar trough, progressbar .osd trough` arms match only bars under an `.osd` ancestor, not a bar that itself carries `.osd`). Restate the two stock widget arms with the landed base meter recipes so a self-class `.osd` bar draws exactly the landed plain progress bar, both toolkits alike.

**Approach and files.** No collected reference screenshot shows a GTK OSD overlay, a meter inside one or a self-class `.osd` thin bar; this is the same platform adaptation the landed GTK 3 OSD meter entry (and the GTK 4 thin-bar restatement it mirrors, whose sheet comment reads "No reference shows an OSD GTK progress trough; reuse the base paint (2026-10-29)") reused the landed recipes for. The stock arms and their claims come from `/org/gtk/libgtk/theme/Adwaita/gtk-contained.css` in `/usr/lib/x86_64-linux-gnu/libgtk-3.so.0` (libgtk-3 3.24.49; the trio reads `progressbar.osd { min-width: 3px; min-height: 3px; background-color: transparent; }`, `progressbar.osd trough { border-style: none; border-radius: 0; background-color: transparent; box-shadow: none; }` and `progressbar.osd progress { border-style: none; border-radius: 0; }`).

(1) In `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, append a dated provenance comment and two rules directly after the landed `.osd progressbar progress:disabled` group — the sheet's last block — and leave the bare `progressbar.osd` node arm undeclared: its `3px` minimum is dominated by the trough's `10px` minimum and its transparent node background stays beneath the trough face. The two restatements are the landed plain recipes byte-for-byte, at the equal specificity `(0,1,2)` so appending after the toolkit resource wins every stock claim:

- `progressbar.osd trough` declares exactly `PROGRESSBAR_TROUGH` in `tests/support/gtk_theme_spec.py` — the `#EEEEEE` face, `background-image: none`, the `1px solid #000000` border, zero radius, the `inset 1px 1px #999999` etch and the landed `10px`/`10px` minimums — replacing the stock transparent, borderless, shadowless trough face. The landed `min-height`/`min-width` already fall through to that rule today (no stock arm claims geometry), so only the face, border and etch change.
- `progressbar.osd progress` declares exactly `PROGRESSBAR_PROGRESS` — the flat `#CCCCFF` fill, no image, `border: 0`, zero radius, no shadow, `margin: 0` — pinning the fill arm instead of letting it fall through. It changes nothing the cascade already yields, but makes the arm explicit and pinnable, as the landed disabled meter restatements did.

The new selectors equal the stock spellings so they pre-empt exactly the stock arms they restate, and stay disjoint from the landed `.osd progressbar trough` / `progressbar .osd trough` ancestor arms (a bar carrying `.osd` itself is not a descendant of an `.osd` element), so no merge order or existing arm is disturbed.

(2) In `tests/test_gtk_theme.py`, add `TestGtkTheme::test_osd_thin_bar` beside `test_osd_progress_scale` in the doc-comment and structure that test follows: assert `self.rules["progressbar.osd trough"] == PROGRESSBAR_TROUGH` and `self.rules["progressbar.osd progress"] == PROGRESSBAR_PROGRESS` with subTests, and — the duty the landed meter plan pinned as the sheet-tail clearance convention — grow `test_osd_progress_scale`'s final equality check, whose expected set holds every selector in `self.rules` containing `.osd` plus `trough`/`fill`/`highlight`/`progress`, by adding `"progressbar.osd trough"` and `"progressbar.osd progress"`. Also extend `test_osd_entry_fields`' clearance duty check if and only if the sheet's restate triggers it — it must, or a third `.osd`-family clearance fails — so verify which of the landed `.osd` clearance enumerations (in `test_osd_overlay_bands`, `test_osd_entry_fields`, `test_osd_check_radio`, `test_osd_scale_slider` and `test_osd_progress_scale`) each new selector trips, and grow exactly those; the new selectors land in the `trough`/`progress`-named exclusions everywhere else, so the expected growth is the one named here.

(3) In `docs/invariants.md`, append one row to the `## gtk` table immediately after the row pinned by `test_osd_progress_scale` (the landed GTK 3 stock-OSD meter row, which records the thin-bar trio "stays undeclared for their queued plans"): the GTK 3 self-class `.osd` thin-bar trough and progress arms declare the landed plain progress-bar recipes; the stock claims come from `gtk-contained.css` in `libgtk-3.so.0`; no collected reference screenshot shows the surface, so the chosen values reuse the landed `PROGRESSBAR_TROUGH`/`PROGRESSBAR_PROGRESS` recipes as the neighbouring landed rows do, with the GTK 4 counterpart pinned by `TestGtk4Theme::test_progressbar_osd_trough_paint`; declaration checks do not establish rendered pixels.

**Acceptance criteria.**

- `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css` declares `progressbar.osd trough` and `progressbar.osd progress` with declarations byte-equal to `PROGRESSBAR_TROUGH` and `PROGRESSBAR_PROGRESS`, each self-class arming pre-empting only its own stock twin, and no other sheet rule changed or rewrapped.
- `test_osd_thin_bar` pins both arms and the grown `test_osd_progress_scale` clearance passes; every landed `.osd` clearance enumeration still passes without a third growth.
- The sheet's last block is still the appended thin-bar comment-and-rule pair; the landed `.osd` meter, scale-thumb, check/radio, entry and overlay-band blocks are byte-unchanged.
- One new `## gtk` invariants row names the missing reference surface, the toolkit probe and the recipe reuse, with the GTK 4 counterpart named.
- `make check` is green.

Size: one sheet block plus one test plus one invariants row — a single implementation run's worth of change.

### Platinum GTK 3 OSD progress and scale arms: restate the stock dark trough, fill and progress paints with the landed progress-bar and scale recipes (planned 2026-10-30 by the plan role; independent of the waiting GTK 4 OSD check-and-radio plan — it appends ten restated rules to `theme/gtk/org.macos8.desktop/gtk-3.0/gtk.css`, adds `TestGtkTheme::test_osd_progress_scale` beside `test_osd_check_radio` in `tests/test_gtk_theme.py` and appends one row to the `## gtk` invariants table, while that entry edits the GTK 4 sheet, `tests/test_gtk4_theme.py` and its own row; the only shared documents are `docs/invariants.md`, where each entry appends its own row, and `tests/support/gtk_theme_spec.py`, from which both import static specs and neither edits — no sheet selector, test or suite overlaps)
— done 2026-10-30 by the feature role

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
append after the landed `.osd scale slider:disabled` group — the
sheet's last block, where the landed scale-thumb plan put its rule block
directly after `.osd radio:disabled` — a dated provenance comment naming the missing reference surface,
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

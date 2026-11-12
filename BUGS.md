# Bugs

Known bugs, recorded by any role and fixed by the bugfix role.
Each bug: symptom, how to reproduce, suspected cause if known. Move fixed bugs to Fixed, with the
required `**Validation gap:** <tag> — <one sentence>` line recording what made the bug hard to
confirm (tag one of: none, no-repro, no-fake, real-run-needed, no-observability, slow-check,
unclear-invariant).

Bugs no role can fix under the project's rules are refused with a dated
`**Refused <date> by <role>: <one-line reason>**` note under the entry's heading; they stay in
`## Open` only while the user has not accepted the refusal. Once accepted, move the entry to
`## Won't fix` — positioned after `## Open` so triage reads only fixable entries first — with a
dated `**Won't fix <date> by the <role> role — user accepted the refusal**` line that records the
limitation the theme now carries and what a fix would have required. A refusal whose reason is
"the fix is a redesign, not a repair" does not end there by default: route the redesign to a
PLANS.md plan and let the user decide whether to fund it before moving the bug. (Directed by the
user 2026-11-01; recorded by the director role.)

## Open

### A command-line HOME make function executes before the shell-syntax refusal (found by the coverage role 2026-11-11)

Run `make -n help 'HOME=$(shell touch /tmp/home-canary)'` with a HOME-independent environment. Make exits with the expected `HOME contains a shell metacharacter` refusal, but the canary is created before that refusal. The existing `test_make_function_text_in_HOME_is_refused_without_evaluation` covers an environment-supplied HOME and does not reproduce this command-line override path. A focused regression test was tried and confirmed the canary; it was left out because the attempted small guard adjustment did not prevent the expansion.

### Cursor artwork is still visually unacceptable to the user (found by the director role 2026-11-11)

**Needs review 2026-11-11 by director: Choose the replacement cursor direction in QUESTIONS.md (redrawn pixel art, smoother original art, or the desktop's existing theme), and identify the affected cursor roles and selected size/display scale; code inspection confirms the scaling mechanism but cannot establish the user's rendered appearance or preferred redesign.**

**Symptom.** User reports: “The mouse cursors still look incredibly ugly.” This is a
visual-quality report; no particular cursor role, selected size or display scale was supplied.

**Reproduction / evidence.** On an explicitly requested desktop inspection, select the
installed Platinum cursor theme with `make apply-cursor`, restart the inspected application,
and compare the arrow, text and pointing-hand roles. Do not apply it or open windows in the
user's session during routine triage. The reported appearance has not been independently
reproduced. For inspection without changing settings, examine `ARROW_GRID`, `XTERM_GRID` and
`HAND2_GRID` in `tools/cursor_art_pointers.py` and their shipped Xcursor frames under
`theme/icons/org.macos8.desktop/cursors/`.

**Suspected cause.** `tools/make_cursors.py::render_rgba` enlarges a shared 16×16 source grid
using nearest-neighbour sampling for `NOMINAL_SIZES = (16, 24, 32)`. At 24 pixels this gives
unequal source-pixel widths; coarse silhouettes and outlines are also possible contributors.
These are code observations and hypotheses, not a diagnosis of the user's selected cursor.

**Routing.** The open cursor-direction question in QUESTIONS.md records the aesthetic fork.
Do not close this report merely because frame encoding, aliases or grid-equality tests pass.
After direction is settled, route a redraw as small per-family PLANS.md entries, with original
artwork, explicit size/hotspot expectations, regression tests and provenance for the reference
surface that is missing. Investigate selection or scale defects separately if demonstrated;
this report does not establish either defect.

**Progress 2026-11-11 by bugfix:** Handed to the director because the reported visual defect
cannot be reproduced without an explicitly requested desktop inspection, and the replacement
direction is still an open user decision. No desktop selection or rendering was attempted. The
recorded inspection path is to select the installed theme and compare arrow, text and pointing-hand
roles; static source inspection identifies nearest-neighbour enlargement from 16×16 to 24/32 and
coarse silhouettes as hypotheses, not a confirmed cause. Do not close on encoding or grid tests.

### post-merge review of 89db8731 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89db87315adf58c524e524be5c3b17d2bd014055` (Land planned GTK 3 OSD suggested-action push-button restatement) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3471442c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3471442cc23eefd762177498941014b393a81e6c` (Pin the render session's Kvantum theme selection with new tests in TestSessionThemeSources) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ea41dae6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ea41dae61dbb2741f0349bf4682728fc71e96143` (Restate the stock `.osd button.destructive-action` arms with the landed push-button recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 08224293 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `08224293bbee16527a0d1fd3e93557bfd1598bd5` (Add Platinum faces for GTK 3 OSD spinbutton steppers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d4609435 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d46094350160d2285fa6698c9e2d8b78d2342108` (Remove the failing button-row assertion) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of dbaee0e4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `dbaee0e4aec010965078ac1266ddda45c8e152e1` (Clear GTK 3 scale-popup buttons’ rounded and borderless overrides) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1e91fbe6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1e91fbe64d2652d35818f679635dcb7672b0ae6e` (Restate GTK 4 OSD progress and scale paints) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 085434b9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `085434b9b0941a66380649c457baeb22eb780888` (Restate GTK 4 OSD scale thumbs with Platinum recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 57a8984e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `57a8984e37e3074a46798216af2b0bab3caa35bf` (Clear the GTK 3 color button swatch shadow) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2c699158 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2c699158366a181189a5a0485597813534def357` (Clear GTK 3 add-color overlay shadows in all four states) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of acaedf4e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `acaedf4ee76eb26479342b1e672971834cdd8a9c` (Share GTK 3 OSD selector inventory checks in one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 34ca72c4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `34ca72c4b76cd7667ec13c268a759bb6cd4351c3` (Pin black foregrounds on GTK 3 add-color overlays) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f506bb76 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f506bb76d19eceb404004ab2e54faaaf08ebb265` (Share the Firefox panel declaration assertion helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 85d12175 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `85d12175ab0f8f85237fe86f4e4babb38d954600` (Style selected-ancestor inline links in GTK 3 backdrop windows) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9a6d0021 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9a6d0021b5058be907c5a006ccca6220216243bc` (Add disabled GTK 4 inline-link styling inside selected ancestors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 99b67519 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `99b67519d9813a07490c14f4a00888ed2fb61cc9` (Restate disabled GTK 3 links inside selected ancestors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a7288806 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a728880630507ddeb44ff134ad1cf126f78126c4` (Add disabled backdrop-link rules inside selected GTK 3 ancestors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a2f04528 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a2f045281a4a204bc4e907865ba7974436dbac01` (Share selected inline-link assertions across GTK 3 tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d1046956 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d1046956d8728dcfa8a8df093ebd321c303a16de` (Implement disabled selected GTK 4 inline-link styling) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b3f5b561 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b3f5b5617e9abbfe29d60e391bce01c8c3b52d91` (Pin disabled self-selected GTK 3 inline-link colours) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 67a2c172 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `67a2c172ed567098ef0f55d981b400776431f05a` (Test the generated file publisher’s default write path) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8ca180d6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8ca180d6c6b838d6989cb03b1096beb2d0dbf6c1` (Reject relative Firefox paths marked `IsRelative=0`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of dad5b35f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `dad5b35f27e37625e459ae0b0d8229642a0a4d37` (Complete the GTK 3 disabled backdrop link feature and resolve its plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9681e407 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9681e40787d8cb3f7884d394bcd884e25d0bb2b0` (Add focused tests for installed GTK sheet lookup) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1341c439 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1341c4399ed2cebe5cdb940693c54b6f449aee49` (Share the held-directory flock fixture across apply-lock tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 95990634 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `959906348a7fa0c016b882c80af02c7a9811d631` (Reflect collapsed GTK 3 disclosure arrows in RTL layouts) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 87464dad never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `87464dad9485aa5f8f9b7219ca1456b761946107` (Refuse uninstall when a destination parent is a symlink) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3a3d2033 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3a3d2033b87b5c71e2a41de7624ad007b1bd23be` (Mirror collapsed GTK 4 disclosure arrows in RTL layouts) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b776336c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b776336ce7500ea9a334f65d29901698f6338a1a` (Add and test GTK 4 view-specific rubberband recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c0de12d5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c0de12d5925a8a2cfead6a245e02b0f3633d9e76` (Add GTK 3 view-specific rubberband recipes and coverage) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fad0a08b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fad0a08bf176d884e441488f3645754eb09d615e` (Share the unrunnable-command test setup and assertions) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c7f27403 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c7f27403487e0d97b6f8dfb05f99b6139f0ac477` (Preserve important declarations when the stylesheet parser merges repeated selectors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bf4b438d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bf4b438d6482579932cfc95ad173137307266f0c` (Preserve non-ASCII spacing in shared stylesheet tokens) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a40e72a9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a40e72a92cff87032258f8c0cccd092ecbb2cff9` (Move render dialog argv recipes into `tools/render_clients.py`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 89b2ecf6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89b2ecf68c56b046cffc6bf639a1b04cb8d035f8` (Complete the shared stylesheet whitespace plan and add U+000B coverage) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 265e50f9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `265e50f9a40fb87d3d73c0c0ee626074e0371758` (Cover Firefox transaction rollback with a concurrent edit) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 169bd857 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `169bd857cfe555f544c02ebaa5a6eb5813bffad9` (Restrict parser priority separators to CSS whitespace) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ef7ba5a0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ef7ba5a0c2eb5af59637b7aa205be71ec28ebc18` (Restrict stylesheet priority separators to CSS whitespace) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ff96d3fe never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ff96d3fec3f32df63bc3f856aa669a6c9d6c67e5` (Open parallel check logs without blocking on FIFO paths) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 141e579c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `141e579c9d36061b331718cd865dff49326f843e` (Preserve non-CSS whitespace at stylesheet declaration boundaries) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0a6d62b1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0a6d62b1a5bcdcd62e01366708cf8c6f862ec428` (Update tests/test_make_cursors.py, tools/make_cursors.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e4d75017 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e4d750178be1e366d1a4e9c8ebd4352877d09e54` (Split the sampler CLI into argument and report modules) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b0b747ce never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b0b747ce8f431cd9d073e39af2daf86901110ab5` (Cover directory worker logs in the results reporter) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0d4193bf never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0d4193bf13d3e65022b93d13a2f27021802fcd10` (Remove per-pixel RGB slice allocations from mismatch ranking) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5eeaef5b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5eeaef5b31c825cb326e1ff8cca13dadab5ee436` (Move Firefox profile actions into a dedicated module) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8e56e4f6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8e56e4f612b4bde68622a18762705fe0f92c9574` (Separate Xcursor container assembly from frame preparation) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7f6270a1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7f6270a1e4b843829ce3b23043cf1824804e6ee7` (Resolve PLANS.md replay conflict, landing the bounds-plan move with main's new split plans kept) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1cbe546a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1cbe546a5d6de06babbdf10b15dc9498881fedcb` (Add opt-in fidelity --channel-counts per-channel report; mark plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b1b976c0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b1b976c0e905f0bff84734664401921107cf90eb` (Share one dialog-render command fixture across the three dialog-client tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 51341247 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `51341247e5116027e1a5d7ccc81c220060ed4243` (Redraw the Platinum arrow family and busy watch cursors in the classic silhouette (cursors part 1/2)) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8b5e86a7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8b5e86a701226cd43ece2934770fc79c0d5ea539` (Have compare() skip the alpha abs_diff lane when planes are opaque) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 20f8f14d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `20f8f14d20462e4043582aa76f91747483b0fdff` (Add write-side worker-log guard tests to tests/test_check_parallel.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0e803af5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0e803af57bbd5f81396fbffc09ebd05f79d14c59` (Redraw cursors 2/2: five grids under the shared arrow drawing rules) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a76196ef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a76196ef9eb169de4bd9eb833f462b9e34fd2232` (Split fidelity CLI report rendering into new tools/fidelity_reports.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8ec2cb47 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8ec2cb4721ae6d176c8e4fe52e5ab0e6de945003` (Share seven interrupt write/unlink stand-ins via two profile-case helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c14e4875 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c14e48758b40900a374cef344ad3284fdb9a3d02` (Move apply's optional Kvantum/KWin selections into theme_apply_optional.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7a9e3063 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7a9e30635805b1b52942444c306157173c300a52` (Text-gate the gi-import scan so only gi-import-bearing files are parsed) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b98857f3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b98857f3bfe94871a8d1209cc9823da1e0be64ac` (Separate `sources.txt` parsing from reference image checks) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 192a66b5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `192a66b542e7a11d4a6819e75228a4097cab7cd0` (Pin invalid CSS hex escape handling in selector matching) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 16e64d53 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `16e64d53a443fa8b465a692f1e1be08d0406909d` (Share the Makefile’s paired Python guards through one macro) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4b36d135 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4b36d135ff7882f294387341955620eb4bec706f` (Use partial selection for limited sampler histograms) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5376920e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5376920e640bf89c138b624594fcc5b206a0d95e` (Add an optional RGBA delta histogram to fidelity reports) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 94e80063 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `94e800638553ccf4fd6aa0575c3d4ab5148ccdaf` (Add bounded RGB tolerance to the reference color sampler) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6b4b8c65 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6b4b8c6595429e411643ad67739b8f1714ba99da` (Test missing-file removal in GTK staging) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8dc47ca4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8dc47ca418d1549e3426ecb282dc614b2fc08412` (Add nearest-rank fidelity delta percentiles) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e6f15f00 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e6f15f00199d02a630bbe42fc3ff127ee6f4f0b4` (Share GTK 3 unchanged-state assertions in config refusal tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 555117b2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `555117b2579b16d032e3a68822e03e17bd1b8b29` (Add alpha reporting to individual reference pixel samples) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 51e352d5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `51e352d5a485dff9b1c7d03b8b580244cdcec5be` (Add signed per-channel bias reporting to the fidelity CLI) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 556d3377 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `556d3377b3939b31f9eb0298794a95a3c38f03b4` (Add signed RGBA channel-bias diagnostics to fidelity reports) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e1fbc097 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e1fbc097236831a44dc0141a3f775d220745600e` (Add alpha-aware RGBA grouping to reference scanline runs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0d6bf30b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0d6bf30b11e685645c0ee0a970253660cf55d711` (Add alpha-aware grouping to reference scanline runs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3c72e93b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3c72e93b17ece4e145e69d60c5434b98dc4e6862` (Build the worker survivor list in one pass) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f4db5be9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f4db5be9c6ea26a7e74e96a13ba9d4b506fcef71` (Add alpha-aware RGBA histogram sampling and mark the plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0a8dcb63 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0a8dcb633bc62d014ff670b5716dafb1e76738e1` (Skip tracked symlinks in the scratch-file scanner test helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9f46cb1f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9f46cb1fd1641ffcef30bed94d8567fcd6b23ca7` (Share paired GTK settings preservation assertions across refusal tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d0f4bc62 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d0f4bc6285fd5b19f88655237a91501e086512a8` (Pin bounded reporting for a worker log with no line breaks) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f83045b2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f83045b2e3285a9e73b9210155dc2191ec6dfdaf` (Share sampler region coordinate mapping across report paths) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 927a76fe never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `927a76feab5858ac12d6f811c92f9e8d0a55dc06` (Add exact alpha filtering to reference color search) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fae67353 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fae67353a7c7897856b81d1be30a60ee886040b7` (Separate render setup from scratch-session state and command building) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 75a0e460 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `75a0e460699eddb803ecc7e71581b8ce247ae265` (Add an explicit RMSE budget to the fidelity gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8aa66f5f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8aa66f5fbece3a34a17f423354dfa6d65c937392` (Add the fidelity gate’s maximum channel delta budget) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c313dd4c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c313dd4cbde42cb5485fa0bd4fc26e9c36bb11e3` (Add optional bounds to emitted histogram colors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f1d079e3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f1d079e3fc960ff70ae038729805e734b72288a9` (Separate sampler search results from text and JSON rendering) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1e7bacff never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1e7bacff7f685d527eb50b43f4314e794277797c` (Remove the two stray tracked scratch artifacts `0` and `ECURITY_CANARY` from the repository root) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1104d34c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1104d34cee5ee05461ead1d96348ba344b11d909` (Restate stock GTK 4 OSD spinbutton steppers with the landed button recipe.) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1b94506b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1b94506b634b19580c8703ad952eed743a39497a` (Share grouped whole-rule sheet assertions through SheetRuleAssertions.assert_rule_group) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 06545561 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `06545561b1d6c7a32a647d083d213e0f196f2d42` (Restate plain GTK 4 spinbutton steppers with the push-button recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7be2bb31 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7be2bb318502c4b4152df7f002dcdb44ccc99756` (Escape the parallel check's verdict-header module name before printing it) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4d317581 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4d31758134b826535efcde18d3a9200d3a871dbc` (Restate GTK 4 needs-attention badges with the landed grouped-clear recipe in the shipped sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e6297f1c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e6297f1cdad6578c66cf33315300425dc2224cc4` (recovered leftover work from feature: Clear stock's needs-attention pulse in the GTK 3 sheet; mark plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b2151320 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b2151320284e00de05098eca0a74c6ba550f42f9` (Name the rejected value in the sampler's scalar range-validator diagnostics) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 004eba83 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `004eba83d004464c9ffe2a9e047cac3ec44dd8f1` (Add the `--gtk-dialog` zenity render mode with a TestGtkDialogRender gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5d07ddad never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5d07ddad3627b7fb041bff8940b0a51ab92218d6` (Pin the rendered GTK 4 entry field cell 1:1 in the dialog render gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f2de0403 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f2de0403c8bbe398fc534d9346502150af822494` (Pin required-command failure triage's unreadable and vanished stderr-log branches) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of dd19429e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `dd19429e6cdb4da377e316ad75b9bf712b64ef31` (Pin zenity's rendered OK action button 1:1 in the GTK dialog gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9d3d5305 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9d3d5305b6a01cb3d9027d9d0d64337e640bc86f` (Retire the stale "queued surface plans" provenance claims in the GTK 3 sheet and register) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of da851084 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `da851084834acb61b4c2f3d7728c05cb9c3f7ab1` (Pin the zenity GTK dialog's Cancel push-button cell byte-1:1 beside the landed OK pin) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4dd5c4db never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4dd5c4db8ccfc7d8fe6b496fb15737dd264cc715` (Pin the GTK dialog capture's CSD window-shell edge with a fourth 1:1 byte-compare test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3cba444b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3cba444b0e8b0264b3b80d8afceff62537be5619` (recovered leftover work from feature: Pin the GTK dialog capture's rendered CSD window-shell edge 1:1 in a fourth render-surface gate test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 39054202 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3905420267adfa8f83345143660c8e0d457a8215` (Share the GTK4 black focus-outline assertion tail through TestGtk4Theme.assert_black_focus_outline) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d3264eb8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d3264eb8a02252d2506899719e50b88aa6ab5635` (Give the GTK dialog gate a longer settle budget) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 14ad4a42 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `14ad4a42b2486decb772dfe99a761d6252483526` (Include rejected GTK theme names in validation errors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0e05d4cd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0e05d4cd7166135a45179285626f2a9b502b2215` (Pin non-integer SystemExit status conversion in the CLI test helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 39eae97c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `39eae97c228a5a495982d546319fb46316f70963` (Share first-line extraction across GTK and Firefox) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 26f61448 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `26f61448f528428c035cd367c476f611f18cc052` (Report Firefox profile inspection failures with the affected path) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a6ef6e38 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a6ef6e388631309be90a37bb3add99a1f91aff6f` (Test stdout log cleanup failure handling) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c9fbb69b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c9fbb69b8157c09a8a6a31c3a738a798e991fed0` (Share raised-frame assertions with the combo field test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a80716ec never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a80716ec005c621e8418d3d04d7d25687e1bae48` (Bound check capture detection to the exact harness command) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 02c19cab never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `02c19cab3245f9081f0610ac11165354e4d160f8` (recovered leftover work from feature: Pin the checkbox dialog’s active Aurorae close box at native size) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7d398a2d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7d398a2d603ee076e43dc43775fe85c2616b1d07` (Pin the GTK dialog render gate’s 20-second settle budget) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c14a73f8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c14a73f895a570a5a6eab290f971613f45b8e21e` (recovered leftover work from feature: Separate fidelity crop geometry from comparison metrics) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 93957615 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `939576155bed24fc040d08f6cdc6a565a3d987a0` (recovered leftover work from coverage: Pin the GTK dialog render gate’s exact 20-second settle budget) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fbdecc00 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fbdecc003ea9672655926ee226f0984ac1df01a7` (Correct GTK dialog shell-edge provenance and close the plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c9344dfa never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c9344dfa183133845995cd27fac487311c61cd32` (Add `make remove-keymap` to remove the swap while preserving other options) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bb4047a1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bb4047a14a539d829beb4b9bcd7aa54b401c30e6` (Add a standalone command to remove the Platinum keyboard swap) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2e0dc0d2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2e0dc0d2c0209b712c0cf99f9f3063684c25bfc8` (Add a standalone `make apply-keymap` target) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 262d3826 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `262d38267f1ac8fae1374a1a89c9093b10548200` (Add standalone `make apply-plasma` for installed Plasma settings) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a242911e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a242911e2ab80e4314942e43d4ef30e75b3bd7e3` (Add a bounded prefix option for sampler run reports) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bb4c7d50 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bb4c7d50ee006ddffd0e185290d44a728caa01f9` (Add dialog capture selection to `make render`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 41c7b800 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `41c7b800c3e8b5513e07acab9b274d1af620b7ab` (Add pagination to reference-pixel scanline runs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d26d20de never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d26d20de0db314524013c1f6631a7687027ecc13` (Cap horizontal mismatch-run output after length filtering) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 559331ec never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `559331ec52d2c81dfcff304a8282887864e14a4b` (Cap vertical mismatch-run reports after length filtering) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8bcba6e6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8bcba6e6113821d7dcbb6ef34720de633474a6a2` (Cap reported horizontal color-match intervals with `--max-match-runs`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f25dab16 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f25dab16e52d83c90d58fe951d304dcfd9ef49a5` (Share mismatch-run filtering and cap accounting) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cd2666f2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cd2666f2f111437483013d0c5d66a64dbae982f1` (Add a cap for vertical color-match intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 41c09108 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `41c0910857ffcbb37c4e2f4b80bebc017baf10a1` (Add a cap for vertical color-match intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9414c83a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9414c83af996629de75713518b1adddbdf5f189b` (Add paging for horizontal color-match intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f3c755ac never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f3c755acf0ecd1dcfb11b7f0f4137d80723580ee` (Add paging for vertical color-match intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d683207d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d683207d401ca789a36667abde7178a32ca8b970` (Add global paging for horizontal mismatch intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c78fc897 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c78fc89776a69dd75b6628eedd37fcd90aed6abd` (Split cursor selection and lifecycle orchestration into focused modules) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6f7adfe1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6f7adfe17a58f1dd01914de7b02b3814cf274897` (Remove the keyboard modifier swap feature) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 87452109 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8745210990df62538797a7953605bf8eb917ce90` (Add global paging for vertical mismatch intervals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 17abeefc never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `17abeefccc344d111c53b3346dff2b213c22f95c` (Extract Firefox profile rollback restoration into a helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bdd0722d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bdd0722dae66390702955c5e01a640c2451a7707` (Drop the stray `_None yet._` above PLANS.md's pending plan; pin with a scan test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f00b21f4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f00b21f42dda9fbd93c38f4080730a1d6f8548d4` (Empty unfocused Aurorae button art; InactiveTextColor 119,119,119) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cab1beb1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cab1beb18ff6d066dee5cf5007dbf379c5fe68bc` (Remove stale None-yet placeholder from PLANS.md, pin with scanner test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ebff8213 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ebff8213d0f0b397054d4f383ec853754c8857fb` (Add `make remove-kvantum` plus the uninstall reset diagnostic) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4dd51fea never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4dd51fea5c9d380769e7c861331328d7765b9115` (recovered leftover work from bugfix: Move the fixed hover/press erasure bug into BUGS.md ## Fixed) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c4100c38 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c4100c3891472f704e373e22d7cd0b4057a39dd5` (Fix remove-kvantum misreporting an occupied kvconfig path as absent) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9e8d17a8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9e8d17a89294776bc0b0b0e779f3444a81a5cfa4` (Add a kcminputrc pointer-selection uninstall diagnostic with tests and docs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a45ce0f4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a45ce0f477f4a115be4825a4eb620ff0b7954032` (Warn at selection time when Kvantum can only resolve our theme from the default data home) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d45bad0b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d45bad0b784100b2eb979660481793f298e5b7a7` (Silence the Kvantum data-home note when the theme exists at the default home) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 52a3d6e1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `52a3d6e147acaa347aca8dd2ccf7261358b02041` (Warn on the kwinrc decoration layout left by make uninstall) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1753a9f6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1753a9f65776e9a8b734e0fad901241781e008c5` (Add a plasmarc uninstall diagnostic naming the plasma-apply-desktoptheme breeze reset) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 27be43b6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `27be43b66bb7868237638f2fc009bec042d3cb07` (Add a kwinrc aurorae-selection uninstall diagnostic naming the two-key --delete reset) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5bdfcf50 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5bdfcf50f87d72baa950e22617a94d94b1eb878f` (Add a kwinrc theme-key uninstall diagnostic naming the two-key --delete reset) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e09f945c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e09f945cb753293c613bfd416878a93e49d3e5cb` (Add kdeglobals widget-style/icon-theme uninstall diagnostics) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a39e6655 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a39e66555229f9906f8d273effc727612c8b8b75` (Open the exit-5 started-test scan through the nonblocking reader) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b7f14f85 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b7f14f851ae1fbee1a3a6ed1833f6200b3508796` (Add a `make uninstall` diagnostic for the five Lato font selections left in kdeglobals) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b69d012a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b69d012a579160a22f577d3da786ecc741c5a077` (Add the `[KDE] LookAndFeelPackage` uninstall diagnostic to `make _uninstall`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0b81ca07 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0b81ca07e2de6e8e964be12d1f15b357f94d7c10` (Deduplicate the shared XDG home-refusal helper into tools/xdg_homes.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c55cbf70 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c55cbf70bd95fe2abee366ea987f8239b5356727` (Diagnose the kdedefaults splash and package defaults `_uninstall` leaves) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9bdcc881 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9bdcc881232134891da7cb59412770628807a8b2` (Add kdedefaults mirror uninstall diagnostics to `make _uninstall`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 98b16c3d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `98b16c3daa38bf93265df5fa56018b9da5bba008` (Merge three palette-filter condition copies into one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1308c630 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1308c630b5449b7c4b28b649d3131dcbd31ffa89` (Make `make uninstall` rmdir the emptied theme-id directories) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7337facb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7337facb4c36fe8921d43b9623c0aa30e3fd88a4` (Square the GTK 4 tab-family corners by extending the shipped GTK 4 sheet, and mark the plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 640a7a09 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `640a7a098305ae5607c59ba7fdef35439b46cef1` (Restate the GTK 4 card focus arms with the landed black outline colour) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cfa36ab4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cfa36ab41785d41fa7e3c80007bb6943ec12b2e0` (Share the HOME refusal wording via xdg_homes.unresolved_home_state) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e47e1f51 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e47e1f519bed8e5edff73df11923de2a5464ff76` (Square GTK 4 cursor-handle contents corners per landed plan; mark plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d16e50e0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d16e50e076bab37b0f500a718ebc7009f357c6b3` (Square GTK 4 toggle-group corners; pin with test and invariant row) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fe773d2d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fe773d2dd2ec092908c4c9a74e3488e91a5a44a1` (Pin gtk_selection.remove's clearing shapes with direct unit tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d6164cd3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d6164cd39c698b483aeccfafd11c94b7f61226e1` (Square the GTK 4 menu-selection corners in the shipped sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of aadefe03 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `aadefe03c9807f9100700a7b92bd7790f76d1075` (Square the GTK 4 check-button wrapper corners per planned entry 52-63) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f4210846 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f421084634c0b3d26a17ce376a76757d93ac4930` (Square GTK 4 alert-dialog corners; pin test_alert_dialog_corners; plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3baec2df never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3baec2df0408ca7021422c91a9404bf7a1726da5` (Make sample CLI decode diagnostics name the typed image path, not the internal /proc/self/fd handle) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f0247aac never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f0247aac99abaf2eb7f82b24e0c2ec5e2b3522b9` (Square GTK 4 expander-title corners; test and record the twin) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2ad412b2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2ad412b296976bde4d09cf4427cb764d7b77ce3e` (Drop the stray `_None yet._` from PLANS.md's Planned section) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1be26d04 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1be26d0450b400c494f21fa84ff9c173483087f2` (Square the GTK 4 AdwBottomSheet/AdwFloatingSheet/drag-handle corners in the shipped GTK 4 sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e9f6917c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e9f6917c9000c57261d4e99a057bdf6a9754ea4a` (Square GTK 4 infobar and searchbar close-button corners with a byte-equal stock comma group) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3c8405e2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3c8405e2531afce0960ba882fda4a425313c7ecc` (Square the GTK 4 indicator-bin badge dot and reveal mask and mark the plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6c59b7a7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6c59b7a7d6710762f56690a0d072de469c9fbbfb` (Square the last seven radius-bearing GTK 4 widget faces stock rounds) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7b802e59 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7b802e5929bf25a7e6318c8117a273117f37f3b5` (Square GTK 4 colour-button and menu-button container corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of da8f850b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `da8f850b157f2c1dc1a745251d9eec3955aa735a` (Square the five leftover GTK 3 round-button faces stock rounds) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2b82694e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2b82694eb4c455e0bb85ad835f9861e64637a076` (Land the GTK 3 CSD container and decoration corners plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6741aef7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6741aef78cd2dfc2fde277e12ec67a9cc144c52d` (Square GTK 3 inline-toolbar, keycap, fine-tune trough and emoji-hover corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b3daeef2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b3daeef289404366af4abd76c9642a060e4f0f7d` (Square stock's 5px linked-field end corners in the GTK 3 sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3182d4b1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3182d4b13843597b0a75770236a4350e9dd2956e` (Add the five missing public-surface docstrings in tools/ to match the codebase's documented style) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a9d79e07 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a9d79e07c8d3951eb01340be9a99620c973ed133` (Move the uninstall config diagnostics into tools/uninstall_diagnostics.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of acdbb27b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `acdbb27b57f7dc97cb73fec16446b4d25c2674bc` (Land GTK 3 residual radii part 4 in the shipped sheet, test and register) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bab2c3dd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bab2c3dd0d5da6049699df4349e5c63afb3808bd` (Factor the duplicated config-home parent lock into file_lock.parent_dir_lock) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0897fdd5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0897fdd5371786d35f5f6bc56ee365a04b3a6e8b` (ship the unselected KWin Decoration QML package and its family lifecycle) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6b5790d7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6b5790d7539007b933c81fe412472cef2da548a7` (Select the shipped KWin decoration QML package and prove it renders byte-identical) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a52f569b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a52f569b9729091b825da63cd461c43b3d96f03a` (Pin tools.theme_config_writer.write_configs's injected-writer shapes directly) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7715d150 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7715d1503641208e52a9fe24cb8d2a0fe97e357f` (Gate the package title-bar buttons' hit areas on window activity (KWin package part 3/3)) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8f06a31e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8f06a31e50cd48246e7f5c2a809f732f390698e8` (square the last three stock-rounded GTK 4 faces; test and record) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e0c241c4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e0c241c404bebf96f90e951c3806d29763525208` (Square the eight plain-axis GTK 4 spin-button end corner chains) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 88fc668a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `88fc668ae6593dab0744b08c2482207343a7242a` (Bound the `make uninstall` diagnostics' config-file reads to the project's shared 1 MiB cap) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of adac4005 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `adac400550b16e38e4de87e7852fecb5e3677fe8` (land the selection-surface corners plan — square the three compound selected-view members' corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5323493a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5323493a1bbce33c936fa094b4dec031bd925766` (Flatten chained-truth ternaries and redundant resets in fidelity report builder) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5e3bc8d8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5e3bc8d8d7958b2ed6be77d78020859a47cdfd83` (Add #CCCCFF selected-view fill to GTK 4 sheet, plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f296e4e6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f296e4e6a6d52bd142c4f2aee969e756d124915e` (Share the sample reports' region and compact-JSON helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b472bf4b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b472bf4b5e5ac8944831df444b05a492cd5ccd13` (Restate stock's disabled-view field as the landed white fill in GTK 4 and mark the plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7a3ccd77 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7a3ccd773d9fe025bb77ad6672aed41a49f2e61c` (Land the GTK 4 view-family census: test module, invariants row, plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ae5616db never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ae5616dbe01f25d2bfe8087caef7a8e439f28fe1` (Keep the GTK uninstall diagnostic's latch when a duplicate key renames) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e1975168 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e1975168666eb98965bbcc147fe018c2f76db1b4` (Reject negative values in the sampler's run-offset paging options) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of eb35911d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `eb35911daee176873832f57848a10d3c8ea3e362` (Add a slow-check validation-gap ledger with three offline reproductions and mark its plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 944bcb18 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `944bcb184a35581f4868d8eeda49e89154c52926` (Drop the stale Planned `_None yet._` left above the tile-check plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 10f7f468 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `10f7f4689b443a7efeb695269fdc4849f0340235` (Revise the tile-check change: drop the stray Planned placeholder and keep the landed faces) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6dea7142 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6dea7142b4538d8579c1cf656ef7afa619a43f3c` (Pin repeated `[file][group]` heading merging in `theme_defaults`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6f46624a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6f46624abb837695e9b4d7474610fddb874a517a` (Collect `test_direct_script_reports_invalid_option_combination` by moving it into its test class) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 71d2bf2a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `71d2bf2abcf2f34d091aefe0afe0d776756c7744` (Drop the stray _None yet._ left above the surviving planned entry) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 25cfbb2a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `25cfbb2aa67700da87f6f8fe866942ecf3f7a622` (Share the bytes atomic-write wrapper between both generators) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3b3a1b60 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3b3a1b60ed5e7a3d788ae85d01804c27fb14548a` (Drop the stray `_None yet._` placeholder left above the planned treeview entry in PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 05a5f2b5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `05a5f2b5df879a84f12ebcb3823281bb2c393a29` (Share the four identical GTK 3 and GTK 4 control rule tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fdae0a02 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fdae0a025364d78f6fc8e0bba7ae4d5ead2bc033` (Fix treeview plan's stray placeholder and Done paste in PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ca665b6f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ca665b6ff72597739630d8785141093073ead26f` (Land the list-row press and open-popup state faces in both GTK sheets and mark the plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 15b29151 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `15b2915111f0b14ffa3f9e79f3e2c46f45f096a4` (Drop the stale `## Planned` `_None yet._` placeholder from PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b174f906 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b174f9061f00ae34d6479a31178e45297e7b1f8f` (Drop stray _None yet._ placeholder left under PLANS.md ## Planned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e7c86286 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e7c86286db280ad75cbbe9ff7b72f964bc5cee06` (Share the exit-2/no-traceback refusal assertion via one support helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a3889479 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a3889479920db3b9219ac7b5c5f04a7e4b48a7e1` (Use the shared exit-2/no-traceback refusal assertion in two suites) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 656c7247 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `656c72479e8229ba89482d4f6f8f9cde28b1896c` (Make uninstall diagnostics refuse a FIFO swapped in after the path check) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 820df718 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `820df718427d54fcb2451a4e4ece6626384c00e7` (Land GTK 3 entry-image ink/margin arms with a clean PLANS move) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4c38f516 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4c38f516434be433bc7697b81355c85c87c3b5b7` (Fix the landed GTK 4 entry-icon change's backlog placement) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8ffa872e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8ffa872ef50188ae4622654c5f46cba9e0393bf0` (Pin `tiled_rgb`'s tile type, length and bytearray guards with tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 705bdea2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `705bdea294438a39e9f3b8f893f4d1908c037182` (Drop the stale `## Planned` `_None yet._` placeholder the calendar entry still falsifies) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bbb272f7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bbb272f7fa60dd0fcf56e380828ffaf6e13a4e04` (Share the four test `kdeglobals` writes through `kde_config.write`) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 04b8031e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `04b8031e4489b6801fa9241f338b14d63ed60efe` (Drop the stale _None yet._ placeholder left under PLANS.md's Planned section) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e1ff9858 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e1ff98586e3802924ad3bbe0fd08404fe7ef165b` (Drop the stale `_None yet._` placeholder `## Planned` kept above a live entry) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b79e09d4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b79e09d4cc5a72040a7ec8ecab5ddc4d7a9f8ece` (Land the GTK 3 sidebar seam and row-geometry restatement plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f357e188 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f357e188fe8788d4090768cee481b6d92da7e840` (Skip key-less `=value` entries in the KDE INI reader instead of raising ParsingError) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 28678a1c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `28678a1c00716728092bc448ccb7725ad833f132` (Join stock sidebar-button geometry into the GTK 3 corner rule and pin it) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 19a9e197 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `19a9e19768ed8b20d2d5b45f7fa049873100bb30` (Use unlink_failing_for in local-hook and cursor unlink-failure tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3cc092b0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3cc092b09f9a38669b378fa1601cfb38db01a160` (Share one rectangular nine-slice hint-geometry helper across three tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1e0b17f2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1e0b17f2021adcbc10057220930354b0c1c18275` (Defer SIGINT around child startup so Ctrl-C still kills its group) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 89a1e826 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89a1e826eb9765a51af900a7ca1450073b9a8936` (Validate pseudo-classes inside the test selector matcher) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 50dd57ef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `50dd57ef233145225e9fea5558a8882c4aa82f0a` (Reject malformed attribute selectors in the test matcher) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0a145072 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0a1450727b80a1436004f0b67280acf5292a810e` (Match an empty quoted attribute value as a value, not presence) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1c73598f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1c73598f6a89877a475091e92e2031d660d6c85d` (Reject leftover text after :not(...) in the selector matcher) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 394e6934 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `394e693444a3a41ec7f1f0d3f2cbb7905fce9425` (Test process_group's first-signal-only deferred replay rule) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ff927cbc never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ff927cbc63c0bc940be68be60963ca6fddc7c0b7` (Make the GTK sheet block scanner treat braces inside unquoted url() values as text) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1bcbfbcf never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1bcbfbcf3c4868916651ce83acd8818f3962d0b5` (Paint Firefox's Page Info dialog as Platinum controls and mark its plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5e89e2ab never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5e89e2ab454fba0a11c928ee3439eaca6db16871` (Handle hex escapes in unquoted attribute values in the selector matcher) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of eb649d44 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `eb649d44d4d01dab0bc3d6eb4d892768f6d5f023` (Anchor the walk's ancestor symlink scan at the repo root; scan the raw path) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 09074a56 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `09074a56a673208fd3a0caea319560cbc0c00600` (Complete the Page Info media-preview Platinum paint and mark it done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 851dc4c9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `851dc4c9c2356a73c002d08b69c439114f6bece3` (Share one header-provenance assertion mixin across the six Firefox sheet provenance tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4d531b83 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4d531b8372aef88c1ca80a829756b80183366ab8` (Wake the snippet-child collector with a bounded select instead of a fixed 5ms sleep) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of efe9c3e2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `efe9c3e26f575471aa7acf1da2e0cef78fce6733` (Paint the Page Info security groupboxes as the etched Platinum frame; plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 243a9687 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `243a9687e12d6f0de9c71bf8308dddfd726d049d` (Pin the SVG parse cache's never-cache-a-failure promise with three tests in TestSvgCaseCache) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1e011068 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1e011068890bb5e82ebaf6e9b571f1add2063ee9` (Make `make uninstall` warn on stderr when a still-published GTK selection names the removed theme) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a7bf0e13 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a7bf0e137a51b9997babfa011c8b91efc1546733` (Share make_cursors and make_wallpaper's refuse-create-write tail in tools/generated_files.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 51099250 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `510992507c18824dd8231148c64b84fac753241e` (Paint QMdiSubWindow's MDI title band as the flat Platinum window face) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 725c8d42 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `725c8d42fcfd548fb1f04c905c2100d35d01d45b` (Add a stdlib unused-import scanner over tools/ and tests/ and remove the two dead imports it finds) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 31e5b618 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `31e5b618f95e8be1c88ed1868c6f63a59389915c` (Add direct tests pinning the shared stat fingerprint in tests/support/file_identity.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c3690ab5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c3690ab5959d4bde690f84e69e4ffab172320de6` (Paint GTK path bars as the Platinum tab recipe in both sheets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a5c2aecd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a5c2aecd21bc6d2cd99cd320d182403fb4b456c4` (Guard PYTHON and RENDER_OUTPUT against recipe-shell injection at make level) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0ff23ef9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0ff23ef90211d205de5e7cbb30bd4e97bf959197` (Treat check_parallel's NO TESTS RAN worker exit as "ran no tests", not a failure) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0e551daa never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0e551daa130d86ea27ee73ef19874377ee4517a2` (Split Firefox content tests into shared and per-page modules) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b45f32ce never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b45f32ceb41043acca3d8a0d41a05e20468a0a21` (Square GTK 4 split-button container corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9294079f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9294079fc1665b9a32a4d5268a90dae464c8d179` (Replace the splash wordmark with Platinum and pin its branding) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 520d5b5a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `520d5b5a95ec63bc8ed478112daae3e9b4d5e303` (Replace the scrollbar TODO marker with a factual comment) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a8e476eb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a8e476eb054bcf74e457e76f9ef5d83aa65f3987` (Replace the reference-cropped wallpaper with a tracked placeholder) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 08a39b10 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `08a39b106eb5fe2edbdff4b0b383a1bc39f18982` (Escape terminal controls in parallel check worker output) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d19b3d02 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d19b3d0207819a305f98388fd1a78e3a21515666` (Align placeholder tracking checks and fixtures with the revised artwork) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 302c20f8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `302c20f8ef384e67b5b0ddc75d3ec3645d653451` (Square GTK 4 assistant sidebar step label corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7174131e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7174131e3cdc5cd4b463251b104ff643a3ee0d2a` (Separate PNG header validation from chunk collection) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 28bcd117 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `28bcd11766faf57475f70d537157f3e1c11ceae5` (Square GTK 4 marked calendar day corners) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d6616220 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d66162202b4e356940b06c6532c5e904d17ff9c8` (Give Xcursor writers a named error for non-iterable input) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a0b84eed never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a0b84eed52ae047da5d5e4f467c3db8f4cf9dd11` (Preserve disabled GTK 4 progress-bar colors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of aaa0f0d6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `aaa0f0d63653b1c7deed497623fa00a38de69665` (Keep GTK 4 directional progress fill corners square) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5fe94488 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5fe94488b01a732fb716415d0eaa38e4b3050102` (Restate the GTK 3 and GTK 4 places-sidebar drag-and-drop arms on the landed #CCCCFF selection with…) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ec391f6d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ec391f6d29dd05bdf55b11014d0718955033e333` (Override GTK 3 selection-mode sidebar separators) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0bab1e1d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0bab1e1d198a5ec9fa139942f4670067091c9b3a` (Guard visible GTK 4 probes behind explicit opt-in) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 537cc591 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `537cc591c116fe3e9b324d06435c415639b2c886` (Contain relative Firefox profiles within the Firefox root) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3ca84144 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3ca84144c1023c74c12726fa6e72dfef24b3feef` (Preserve GTK 4 disabled scale palette opacity) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 519d587f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `519d587fc49c249a13f6fe27abbd0dcb855e5320` (Override GTK 3 selection-mode sidebar separators with the etched face) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 39f92d1b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `39f92d1bd8a7a2c4e443c7edef57850eb8832553` (Require shadow resets for both Page Info radio states) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 944e46eb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `944e46eb695c73a92fd944640215f9b7e435bf92` (Fix GTK diagnostics parsing and align regression expectations) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 34a86df0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `34a86df0f82f5230e771140178078cbebc2d6029` (Replace nested fidelity metric conditionals with explicit branches) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d5144c55 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d5144c557f6443c939d7df6aa397b0f0d2328b74` (Restore full opacity for GTK 3 sidebar row icons) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8f701625 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8f7016257d529c11644138fb2e1e5dddb8777bbf` (Preserve GTK 4 disabled switches’ declared palette opacity) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8ba96a30 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8ba96a306ae90f40699ba09d8af508f98663c86a` (Ignore inherited Git repository-selection overrides during hook discovery) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 77851a15 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `77851a15cb2c07b69be2f5f59c7d1c1663e2c2d0` (Correct the GTK up-arrow test reference and close the review bug) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5d0080d0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5d0080d05bc95299de85360ff688917956ea6446` (Share sampler report context and remove its stale import) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e7abe77a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e7abe77a57fa519e0ab86198ee58de69c22d46cd` (Restore full opacity for GTK 3 sidebar-button images) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c2cb4017 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c2cb4017252f076f1b2f9701d4fe21e62d815281` (Pin the GTK 4 notebook tab keyboard-focus outline color) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 86ea06ba never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `86ea06ba57637043f88a19015f8321f9a1a1f6aa` (Preserve GTK 3 emoji section-label opacity at rest and on hover) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7ef56f7f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7ef56f7f11db52e2363d46d32edf2498f9e7fcda` (Preserve custom SIGTERM handler behavior during child startup) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7ef79b84 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7ef79b84e63afed4e81821009d5cb2ec51a7ddd3` (Make GTK 4 spin-button focus-outline changes immediate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fa984371 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fa984371fd47c986b95f469c35472880dbea6cf3` (Set GTK 4 overlay thumb minimum breadth) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7e4f9e34 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7e4f9e34d9470c7ee3939fb35da73e853dbe84e9` (Handle CSS string continuations in selector attribute values) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9dd07beb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9dd07beb32cd5a3b8a03fa1fa5d8ae9452cf4e1c` (Add reference-derived minimum sizes for GTK 3 overlay thumbs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ed3452b6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ed3452b6c48d4efc9ef5c45e73f1efd765d5826d` (Add a focused outline for GTK 3 radio buttons) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 577e920c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `577e920cd0887f8c59a479840dac094c512d59d6` (Land #CCCCFF accelerator-editor label rules, tests and invariants row) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5bcee291 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5bcee2914fadad073455739b6acb912136f5ae95` (Land GTK 4 treeview/columnview progress-cell faces and mark the PLANS.md entry done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5397daef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5397daef00efa45317671a1ad193b2f31a010775` (Plan the view-family accelerator-editor restatement in PLANS.md ## Planned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 225a5b98 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `225a5b98cf01efa2e04257e298dbd0fcd9d1c81e` (Cut the check coordinator's hand-off poll from 50ms to 10ms) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c655d00f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c655d00f87137cb590a03aae9140efdcbb33a05c` (Add the GTK 4 disabled text-view white field rule and coverage) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3f4f2e71 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3f4f2e71ed48f42bd9306a1f1f58dd844892357e` (Render gate now byte-compares a rendered Kvantum widget (checkbox dialog)) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9628a95d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9628a95d0f6c3cd28eeb20716616beb379999b06` (Add a gate for unresolved README fragment links) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4e1d3e3e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4e1d3e3eb6db427e432de3db64853b8773a8026a` (Refuse double-quote-breaker metacharacters in CHECK_TESTS/CHECK_PARALLEL at make parse time) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 241d73f7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `241d73f7160df60b88a9dd52004547b1ae9b3016` (Restate the four stock GTK 3 OSD entry/spin-button field arms with the landed Platinum entry recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f0e9582a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f0e9582a2c684b70a1ae72ed395b6d09a2a332ec` (Flatten the empty-selection branch in worst-pixel ranking) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5953beb0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5953beb058b63216528585b97d09e2252a48ae90` (Paint GTK 4 OSD overlay containers with the landed menu-bar band) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b93405ea never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b93405ea57f7cf2788ef1a8f4d41c6c09dfd2fe3` (Repaint GTK 4 OSD overlay containers with the Platinum band, test pinned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 81a72d93 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `81a72d93538e77a4fac682dacb6e786198da06f2` (Cover the `GALLIUM_DRIVER` software-renderer skip branch) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

## Won't fix

### A killed GTK selection commit can leave settings files at different transaction versions (found by the robustness role 2026-11-01)

**Won't fix 2026-11-02 by the director role — user accepted the refusal**

Covered by the project-wide SIGKILL decision in PRINCIPLES.md (directed by the user
2026-11-02). Partial publication and leftover backups after SIGKILL are accepted limitations;
roles should use that standing decision when triaging equivalent reports.

`tools/gtk_staging.py::commit` publishes the GTK 3 settings, GTK 4 settings and GTK 4 user CSS
with separate replacements. Its rollback runs only when Python catches an exception; if the
process receives `SIGKILL` after one replacement, later files retain their old contents while
the first file contains the new selection, and its hidden hard-link backup remains. The GTK
selection is then partly applied despite the caller never completing.

Reproduce by staging different contents for two existing settings files, running `commit`, and
delivering `SIGKILL` after the first `os.replace` returns but before the second begins. The first
target contains new bytes, the second retains old bytes, and a `.backup` sibling remains. Recovery
would require a durable transaction record or another crash-consistent publication design;
in-process exception rollback cannot run after `SIGKILL`, and automatic recovery could overwrite
user edits made after the interrupted commit.

## Fixed

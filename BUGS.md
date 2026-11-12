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

### post-merge review of b20cc7c6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b20cc7c622fc7db7f4fcaab3d9db4590910150cc` (Planned a GTK 4 OSD check/radio restatement plan appended to PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 86219db2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `86219db275b9743ed62169d95c5a6b91728f8f27` (Restate the five stock GTK 3 OSD check/radio arms with the landed check and radio recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 77721327 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7772132732703f4de04bd93efd3f52e80fd2e970` (Restate stock GTK 3 OSD scale thumbs with plain scale recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 849b25e6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `849b25e6c14d51301273e6f52e5d140bea617213` (Restate the stock GTK 3 OSD trough/fill/progress paints with the landed Platinum meter recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f6d4e319 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f6d4e319a92c3a8a2d510a306c1291aab922d97e` (Cover valid maximum color fraction inputs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cdc05f16 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cdc05f1631d52f12678074efe649907288346382` (Restate GTK 3 `progressbar.osd` thin-bar arms with landed meter recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d0239110 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d023911076689b13366d55e42a979ba10f73a3b6` (Test the run report’s implicit axis for rectangular regions) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 45c9ef12 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `45c9ef12a39b9848d55af1ecfa74e585919bea4f` (Pin the GTK render client’s Zenity entry arguments) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8ece6cef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8ece6cef1637bc7f3b08a0f8b0b30cd61af51561` (Bound process_runner.finish's second pipe wait by REAP_TIMEOUT) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8383f952 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8383f952c22738cd5022bd092e3517415fb7628a` (Check README navigation anchors and move the plan to Done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c8e9f773 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c8e9f773d465d108f150cb754448cf5c1b1ee66b` (Pin the checkbox dialog’s complete client argv in its unit test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7679bcb3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7679bcb385cc2578405e91a1c35bbbfd4adc1771` (Restate GTK 3 OSD push-button arms with the plain Platinum button) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 43ec4485 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `43ec4485bea92e75edfe45059b160d69b399c1bb` (Bound retained intervals in capped vertical fidelity reports) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4c104c31 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4c104c31c41d16291e53f69d68776e1ba432c4b3` (Pin the complete combo chooser argv and shell-word recovery) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1d36ea1a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1d36ea1a56ffa6315c87491dffc443ab1ccedcb2` (Restate GTK 3 OSD flat-button arms with the landed button recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8bd187d4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8bd187d4e4ba81e958ee22eccebbfd5278d3f597` (Bind CI rendering environment assertions to the check job) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 10c7dff0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `10c7dff0f0b04b9e57dfb0c3de7c54390a69d588` (Pin kcminputrc's unreadable-file arm in the cursor-theme reader tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 46d108ae never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `46d108ae888f0fe69f978c4fe30437249796c65f` (Map Qt’s GenericFrame to the reference sunken field) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 913a21de never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `913a21dec7a2672508f4bade76eb50d6afcf6608` (Reject truncated reference images when validation checks their missing stream terminators) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 519ef843 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `519ef843c64d5a75555ddb971abcdf4f919e3a69` (Flatten fidelity.py's run-report ternaries; fix stale invariant test citation) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b626c635 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b626c635bdd86dd54e62f7eda083cabd74222266` (Share the run-accumulation count/eligibility/cap logic in tools/sample_match_runs.py as _RunPage) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b7c32432 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b7c32432f3e1f097da876505723fd29e8359c8c7` (Pin the `--menu-dialog` client dispatch path) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 034807bb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `034807bbafd1ce5371234c4c2caa6f95b06b2567` (Pin gtk_staging.commit's directory-target refusals in the staging tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e1c44e52 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e1c44e5217187bc731c6e3d2f66050712b043b26` (Style GTK 3 palette swatch drop targets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 03207ecb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `03207ecb665e75101f2f0c91dc5cda171a39620a` (Share Firefox `user.js` fixture block construction) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 001245e1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `001245e181a606fa13c11f09419055bea3fb79bd` (Add missing docstrings to the 16 undocumented module-level defs/classes in tools/) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 677bb692 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `677bb692f00218b408fa83b0cdf4e0b0494c0540` (Add an interrupt-path rollback test for firefox_transaction.publish_install) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9992a275 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9992a2757e27aa0ed96b2db1fcdf4baa5a7aef2d` (Share the GTK suites' copied label.separator pin via a shared helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 59bcd99f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `59bcd99fa815b6f9f7e2708c6ed321a1c16c7588` (Add a test pinning firefox_transaction's user.js rollback-refusal collection) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 16476525 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `164765255f5963927de4fd749787968cf8ad003a` (Land the Kvantum line-edit dialog render gate and its plan entry) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5120d36f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5120d36fe2d319090d0b96bcb1ba5799c2098197` (Share the GTK suites' copied scale-popup button pin via one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2b21968f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2b21968f5f1ed2b9782019950e41b3422807aee2` (Add one focused rollback test for publish_install's user.js read refusal) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6aedc94d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6aedc94d3687559e8b82dc64feb0af6ebff80e2e` (Add the GTK 3 selected-row swatch ring and mark its plan done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 863c362a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `863c362a357eb0cbe0809b641fadcc6790b56973` (Share process-group cleanup helpers with parallel check workers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 68f88496 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `68f88496bd5756da1c8239b2c36fc6d19bbd9f99` (Add the Kvantum slider-dialog render gate (--slider-dialog) pinning the rendered thumb and trough o…) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 48b8857d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `48b8857d241718dd17d7b126751f7c292c02ded3` (Delete the shadowed duplicate test_dim_label_foreground def from TestGtk4Theme) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 564ccd1d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `564ccd1d96635c22b1f58587e3aa6397e99bfffb` (Pin color-offset zero, rgb shapes in validator tests; restore lost GTK swatch rule) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e4770d2e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e4770d2e0cdb9f8fcca32357f7006d3a2613ddb9` (Share the make-refusal suites' four-copied both-targets metacharacter assertion via one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6ccb2d0c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6ccb2d0cf08b5407527528b5637976e01f2354a9` (Bound and validate reads of the parallel check duration cache) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 41247728 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `41247728a6d981c25f4dd223bb78bd21f0be1fb7` (Pin image_stream_format's per-format labels and bytes checks in tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ca74551f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ca74551fedabd7e058a7a07813c60a46e346d116` (Share test_gtk4_theme's thrice-copied scale-anchored focus-outline pin) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 7e28b2d4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `7e28b2d4104aeac7229cd1e99f456d682c6bc1dd` (Consolidate the GTK 3 selected-row swatch ring declaration) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a3327528 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a3327528d4a36b17389760e8d588092fa1155670` (Add TestReconfigureKwin covering the qdbus-found branch of theme_apply_optional.reconfigure_kwin) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 42c774f2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `42c774f2975f3f1815718561d3fe907e0ad3c9ef` (Share the colorchooser suite's 8-copied add-color selector tuple via one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 418d2458 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `418d2458ca80c504b389df1669ddc11213e8aa59` (Declare the GTK 3 content-view field and backdrop) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f4ca601c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f4ca601c87f8e8bb21e90974b1ad5ddf07375a8a` (recovered leftover work from feature: Add a Kvantum progressbar-dialog render gate pinning the meter trough) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6f8e8f6a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6f8e8f6a6f939e75c0cd1125a8c26e97750b9266` (Declare GTK 4 `.dim-label` inactive text in Platinum grey) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 03278395 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `03278395c6ad8816198a58fd35c195d50f758b38` (Share the GTK 3 pixel-probe boilerplate via three module constants) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 24df389f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `24df389fbb9b406a0137084afa84e500ea8a770a` (Restore the shadowed escaped-whitespace coverage in test_gtk_css.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5f8661f5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5f8661f55641b53aebe6e489eb72e2819ab6c825` (Refuse FIFO render captures without blocking) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0c948974 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0c948974a50e58aa04e8ca73e200b36cc7c80fa2` (Declare GTK 4 placeholder text in the inactive-text grey) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ca1d7404 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ca1d740418cfdcd1c35bd345e7e717e31df861a1` (Add direct tests for file_lock.installed_data_lock and pin them in the invariants register) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 791199f3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `791199f36b2d3bb68e8ee6deb522c6eb8ba9ae19` (Add the --textbox-dialog render mode and a scrollbar gate pinning the shipped art recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 02ec3690 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `02ec36906ebade9308efa898ec8952f5f6b2482a` (Share the ten `_uninstall` suites' copied make -n parse test via assert_make_n_uninstall_parses) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 046c1fc6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `046c1fc6d1e118a7353aa1edee83df29105d963a` (Guard tests against same-scope duplicate defs shadowing earlier tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a456cd4a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a456cd4a78c32c75227e56eb49ea35bc1ee771f2` (Share Firefox suites' copied absence asserts via case helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fe0f0dd2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fe0f0dd2c49480db1f6dc31dc12d09af79c4d53f` (Refresh the README CI paragraph and two stale comments to name all seven kdialog dialog renders) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c63160cd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c63160cd9696d81163a61d065391c2d50c6bef7d` (Cover nested GTK 4 vertical spinbutton placeholders) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 198c9cef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `198c9cef2cccefcaa5a4655df44f1ecf40fcfdb3` (Test generated-file publisher's refusal and failure branches) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cff515e8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cff515e8bb6aa483373995ff8296628e4120ba8d` (Share the textbox/progressbar render gates' twice-copied assert_band via _DialogGate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 924ac294 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `924ac29404e6a01a00df262996f7e0abff9bc94b` (Refuse cursor links through a symlinked `~/.icons` directory) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ccbd8783 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ccbd8783cc26fa6b76a800584b06711d199bafe4` (Pin the os.replace failure branch of tools/atomic_write.py in tests/test_atomic_write.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 623ee0ce never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `623ee0ce4520c3eee5d25cff178302d5218c82a0` (Reject line breaks in GTK theme names before writing settings) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a3e0a472 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a3e0a472e873abe4e95ad89f0e10c3345c6e5380` (Share Firefox suites' 21-copied rule-name sweep via one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a3f311b1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a3f311b1b3cff0f037723431fd26a739a2013530` (Pin the render workflow's untested dialog-setup failure paths) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 93a227df never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `93a227df0fb5ffaef605a100a59196db5c68a0f7` (Land the calendar-dialog render gate pinning the kdialog calendar's palette-painted day table) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ec1223a6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ec1223a6a63a7f9a178c357b272c481b70024222` (Pin process_group._popen_deferred's signal-during-failing-start cleanup in two tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ab5e9253 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ab5e9253def2f39bde6c0c17c5d91648cd98fb38` (Add --calendar-dialog to render_surface's usage docstring + guard test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fcbb3e98 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fcbb3e9809ba62375d62a34659151e696965002e` (Run the two dialog render gates concurrently in tests/test_render_surface.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 76f49054 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `76f49054515f0bd7fa4610aa7f3431460d4d1862` (Declare the neutral `#DDDDDD` button face on the GTK 3 add-color overlay arms) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 534650a1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `534650a1d09f77f9af3c402f1e94ed549f885a37` (Land the color-dialog render gate with --color-dialog mode and TestColorDialogRender) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 020d1abd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `020d1abd18a46bb5e88b8533e74277e0b1047713` (Pin render_setup.install_gtk_selection's two arms with direct tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6d4732d6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6d4732d6576df9675de6a30674a4113cd1c957f7` (Share the uninstall suites' copied config-home fallback shape via one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8e7b69ae never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8e7b69aefe7741d41cca68a1b3aeb8b03f0de2cf` (Add the missing lineedit-dialog row to the Makefile render-mode parity test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 55dead92 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `55dead92de528e3030c992fb031188e43336b14d` (Fix stale dialog-gate count prose left by the color-dialog gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2b47c11c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2b47c11c373437b1ed7a2bad145afa265b72f3b3` (Restate GTK 4 scale-popup buttons with the landed push-button recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1b6ba2d7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1b6ba2d7b0832bb460c6d74411d57d2241dba773` (Land the icon-dialog render gate with --icon-dialog mode) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6ce8dec7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6ce8dec7cd1aadbc261b16d7622d5c339441cb50` (Sync the brief to the landed --color-dialog render and repair its missed doc spots) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 078c11ff never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `078c11ff6b4e98fbf0fbd505eff9e93e806126c2` (Restate GTK message-dialog bands and buttons with the landed Platinum recipes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 05609626 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `05609626801e3e10657b52c78fd849f44ee618c6` (recovered leftover work from bugfix: Pin the render session's nested D-Bus bus to QT_QPA_PLATFORM=offscreen so activated services stop c…) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 161fc3bc never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `161fc3bcde019c77c1bed9cf1ff16ba561b27e7a` (recovered leftover work from coverage: Extend the derived dialog-gate count-prose guard to also scan tests/test_render_surface.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 408ec979 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `408ec9796a53283d8f13ac6396f317a9b52d5242` (Share the GTK suites' inline-link state-selector expansion via one support.gtk_css helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4f6be89d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4f6be89dd24a4cde058fba013125fc874acdef47` (Split test_gtk_theme.py into six scope suites; shared cases to a base) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 762705a7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `762705a721c98dc5cf1953e2f781da7064c9e194` (Land the GTK 3 notebook tab-face render probe and retire its PLANS entry) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0da3b326 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0da3b326c1746b38bd9526b26e8cc1216877a25c` (Reword the render CLI's multi-dialog-mode refusal to hold at any count) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e95ab0f2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e95ab0f24be50d79d2ca6d5e0c1675509960a72e` (Clear the stock label/icon emboss on plain enabled GTK 3 push buttons with sheet-tail restatements) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b2281a6b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b2281a6bab81fb66ff3b4910bbc147be44645c25` (Plan the GTK 4 plain suggested-action button restatement in PLANS.md) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 564cda89 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `564cda892977fc377b2c558d4cc4cb6e78d3453b` (Flatten nested link cleanup in the cursor removal test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ef38d449 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ef38d449ddc9f9c55a7634925eb3f6256e63456c` (Declare the Platinum content-view field and hover clearances in both GTK sheets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of dfebb915 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `dfebb9150eaad7b40b83f0648f22a4b6ad4fbdf8` (Reject non-integer dimensions in shared PNG test fixtures) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of edc00dc7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `edc00dc736abc3eae21cb3987fa6d91e893f71c1` (Landed the GTK 4 plain suggested-action button plan (Planned 8-23 → Done)) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f2bb45e5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f2bb45e5093d527c3750d10a385f2d0f74ae6bd5` (Add an opt-in GTK 4 notebook pixel probe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 598434e3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `598434e344f4b02d69c5ce7af7f656fab52518f5` (Pin the untested capture-failure arm of the session script's exit contract) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ece556d0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ece556d062f0f0725c90a14e6ecb4f315e32d567` (Restate GTK 4 plain destructive-action buttons with the landed recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 89cc3159 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89cc31595b9f2fb742236d8ff499103496ce9034` (Guard dialog-gate counts in render-surface prose) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c3296f96 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c3296f96697fcdf6784e920023250b237f21b68c` (Land the GTK 3 plain suggested-action restatement plan and move it to ## Done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 713acc0f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `713acc0f33d91518d6d9499ee1a6f67e9c9bf2e4` (CI installs and verifies kdialog; dialog gates skip when tools are absent) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d07981c5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d07981c5ac12533235fa2daf6055c8d4aa7a59d7` (Pin shell-safe render client argument handling) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c70cb92d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c70cb92d3302a326caa610044716a26bd0112c0e` (Validate byte sizes in the shared image completeness detector) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 30e00781 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `30e00781396a22ad416a1d1c1859ebe7560354dd` (Make apply_theme hold the data-home flock across its re-selections) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c237bb0e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c237bb0e4ddb3c2ec052408a66b7935654d13e46` (Restate GTK 3 colour-class flat arms with the push-button recipe) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 216040d5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `216040d50bf234237cd4ed01c1e52abfb8870189` (Pin the render session’s offscreen Qt environment in a unit test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d91aa7cd never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d91aa7cd1201b19dec2ec8a66cdbf185932232c2` (Pin CI's actions/checkout and actions/setup-python to full commit SHAs with a new invariant test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5b85bca6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5b85bca6c1790cabe473b9ec2d1caf454ecef079` (Share BOM tolerant first line marker matching across GTK and Firefox) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 4718b451 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `4718b4518bcc7b38a15ba727f6bd8ffa31db5028` (Restate stock's selected-row button arms with the landed black in GTK 3+4) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9782ae1d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9782ae1d017dbb624450626b418cf2687dd28175` (Validate JPEG conversion inputs with named errors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f5cb1daf never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f5cb1dafe42d2284e5e9c677fa0bc58b3603c1a7` (Split validation_gaps.py into a per-concern tests/support package) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f452a509 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f452a509badd7d80f9dced6dda4dfb04eb505864` (Restate the stock view-child selection fills on #CCCCFF in both GTK sheets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 55864df0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `55864df061f84b951dcba81ab2bb1c7b7f334a15` (Add the Kvantum radio-list render pixel gate) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0656e3d8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0656e3d83d04fc7f3c19ccb1b56ff4094529b31e` (recovered leftover work from coverage: Test caller-specific errors for capped reads) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cf0479cb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cf0479cbd950c9f5f7ee3fe698faf1e04dffcdd5` (Restate stock icon-view selection on #CCCCFF in both GTK sheets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b6c8ad28 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b6c8ad28917931167c471cf4bef94b204a5381d7` (Test `run_logged_split` stdin byte delivery and EOF) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 91ed4c48 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `91ed4c48a958952bf46485cbc69d5b4d22776ecf` (Nothing to implement; only refreshed the feature role's tumwater notes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 29f4a29a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `29f4a29a9c4f6fd7b4993e77c84679346d50f469` (Restate GTK 3 selected-text arms with the landed palette) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d945e337 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d945e337123d5ba9fab09e3818525e4871c1a3ff` (Reject impossible PNG, JPEG, and GIF stream sizes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9d343cc4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9d343cc44ad08c93fe5523d1b2e4ccafc80bd451` (Override GTK 4 disabled-selected calendar text with inactive grey) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8189290e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8189290e5d905a8e36961d0a6b42886cf02bae19` (Pin JPEG converter failure diagnostics and private path scrubbing) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9ca46d65 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9ca46d65454b1f31e24f9fb5a585438341bc0193` (Complete the GTK 4 disabled link-button label plan) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3954f55e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3954f55e86f6f25721f15f27e41e5542c609a1e7` (Cover shadowed async definitions in the test suite guard) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6e49eea9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6e49eea99a522bdb7ee72d03dc14326f99da8bf2` (Add grey GTK 3 disabled backdrop link states) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of bba60395 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `bba60395a550132294d74084da027fb34a6deda1` (Reap the background render client before the session exits) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 20d60750 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `20d6075077e1af763ac022a43942fefd690cd5ab` (Add selected inline-link ink rules for GTK 3) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of fb169f9f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `fb169f9f01cc384ca7b61a0432b7e229eaab9808` (Publish the render session’s Kvantum config atomically) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5a9a68f3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5a9a68f3908b2f957299bbe269c1443bfe52049b` (Pin dialog versus applet render config selection) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cb3a72e2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cb3a72e2f8f9021542d2f3ce2ba0574568ea356d` (Add GTK 3 selected inline-link styling for backdrop windows) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 89ff3c0c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89ff3c0c399f527620f589251e1cb43a6a58071a` (Report GTK backup cleanup failures after publishing settings) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3e10c046 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3e10c0460c91042a5224dd1e4e73f56b9cd2dc69` (Add black ink for GTK 4 links inside selected nodes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 04e68906 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `04e68906b444e0966c6d2af319f9724b01339758` (Fold ordinary stylesheet declaration names with ASCII rules) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ccd7977d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ccd7977da085b9ba33087e1093462782b8d77398` (Preserve escaped trailing whitespace in parsed stylesheet values) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 78a8afba never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `78a8afbae36d8faba6cf2ba96aafb74b13e11305` (Preserve semicolons inside square bracket values in the shared stylesheet parser) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3ec2f663 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3ec2f6638b84fde394761e335689eea005df6d7f` (Install ImageMagick in CI and verify convert before make check) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cd95cb79 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cd95cb79005af319eb7531d16b748fc680c25959` (Ignore `@define-color` text inside stylesheet rule blocks) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 401b81c9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `401b81c94379249092313c28b3f6acabdf3cdc5b` (Preserve escaped colons in shared stylesheet property names) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 824a1543 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `824a15439ab6b0cdce2b5034341ccf305e752374` (Require exact script bytes to establish local hook ownership) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0736d9e7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0736d9e701fc42cf5e4244e05d7bef684ff5573a` (Preserve escaped colons in shared stylesheet property names) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c4ac7317 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c4ac7317ec6485687e50670dd8e0cc36fff75a96` (Remove empty `~/.icons` after failed cursor-link creation) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f5b97af9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f5b97af96d2ba44021710785b6d98f192183fdb2` (Preserve comment delimiters inside unquoted stylesheet URLs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 23b5f7b1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `23b5f7b14a0694121e7f51fe77a9554ed1ecef46` (Preserve CSS hex-escape terminators during stylesheet normalization) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c5467ca9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c5467ca94e6094591e0f0057a8f6067577cb49c9` (Align PNG encoder type hints with supported bytearray inputs) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 11ebc373 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `11ebc373e99e264c1a048d5850cc8983664945ab` (Canonicalize escaped ordinary CSS property names before cascade merging) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of eec02a80 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `eec02a80c39be46867988935c9ac1b2a4c48aeec` (Accept empty values for named CSS custom properties) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8aa4a648 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8aa4a648919dace044f40d8bfcebea7ed5671b56` (Decode escaped custom-property names before cascade merging) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b5357a6f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b5357a6f49f63775438e35c2a7b765cf7648b402` (Add structured JSON output to the reference pixel sampler) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 522910f9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `522910f93c52ce1084d42bc0068f1f5da61cd0c8` (Add structured JSON output to the reference pixel sampler) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of da1146cb never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `da1146cb2ee14a00535ad81bf09917463d06107f` (Rename theme_apply_optional.py to apply_optional.py beside apply_*) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of e0a94069 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `e0a94069d0965d51c4b52988c772437c68114a3d` (Expand greyscale PNG samples to RGB with strided slice writes) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 96a2954c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `96a2954cd79a0deb94c9b7749a3eb26e0b190663` (Point stale backlog citations at the archive files that hold them) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 9428b020 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `9428b0209cd10fb9c9a291abc45ec023374e2438` (Add JSON output to the Fidelity CLI) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of df31c37c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `df31c37c7d7071c6b35d2bc3df7e54d789b58382` (Point stale BUGS.md citations at BUGS-FIXED.md in CI and invariants) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ecc4ed4c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ecc4ed4cde36c5bf64924c94764a8c6ae9f6b83f` (Pin cursorTheme section tracking past a foreign kcminputrc header) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 09db6f64 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `09db6f64fb3ad649336bb11643dc8177f12cf98e` (Complete Fidelity CLI JSON acceptance coverage and file the plan as done) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 99fa7436 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `99fa7436ea5f61e745d35653a3bd27ad6f456df5` (Share check_parallel_results' log open via open_regular_binary) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 340e0db6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `340e0db6d15ed4d1501c803fa6e3a9399f4ffa84` (recovered leftover work from perf: Unfilter PNG Average scanlines with a per-lane lookup table) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cefbdef9 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cefbdef948b8af774ba5ef75213e1a0a5cd134aa` (recovered leftover work from feature: Span GTK 3 progress fill across the trough interior) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 131a4798 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `131a479890ebbb658c176a5d5b22ad818f325bf6` (recovered leftover work from clean: Table-drive the render dialog client dispatch in render_workflow) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ecebdb4a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ecebdb4a9d1bc391015f431b68bd6a206b04fbd4` (recovered leftover work from robustness: Bound converter log reads in the JPEG failure diagnostic to 4 KiB) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a368d13c never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a368d13c7cf53754ae480299ae25b5c71cb6c640` (Add RGB color location to the reference pixel sampler) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 3f83e349 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `3f83e349e014839a04947d3dcda6c0ff1dc84b86` (recovered leftover work from coverage: Pin inclusive lower bounds of render CLI duration options) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of c56c13ba never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `c56c13ba345f9c52ceb97b2c47197307b37443bc` (recovered leftover work from clean: Flatten deep test nesting in two kwin and GTK CSS tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ddde920a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ddde920ae6da1e90db0cba0ef6bb614baf3a2cf8` (Add bounded worst-pixel diagnostics to fidelity comparisons) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f7c107c0 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f7c107c0cc1ba804c8fdd4287924c8bd38395a5d` (recovered leftover work from feature: Draw one 1px seam per horizontal GTK 3 spin button stepper edge) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5b479bf8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5b479bf8b8552431baa05cb6b5ed24ad98372bb6` (recovered leftover work from coverage: Pin the parallel check's worker concurrency bound and durations) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 68622213 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6862221369ee7e06552f086b338a613f454260d4` (Add an opt-in worst-pixel source-value diagnostic) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 0a0790ea never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `0a0790eac3f0d3366e81000b0022861aae718f3f` (recovered leftover work from clean: Flatten the four-level palette loops in Firefox preferences tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 61ac63a5 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `61ac63a582ef29fde8486ea2722ab732ea3c1a26` (recovered leftover work from coverage: Pin _feed_stdin broken-pipe and close-error handling in tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of be2860d7 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `be2860d76d9b39d90095976d711d179c0bb0f91d` (Add an optional limit for sampler histogram output) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a0991dd4 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a0991dd448e969d59c9453576afb26bf416c5b3e` (recovered leftover work from clean: Flatten deep nesting in sample_report_runs and apply_theme) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 283bf5e2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `283bf5e29da696e6a98e8ee519b482e54c9ad861` (Pin fidelity_metrics.over_table with direct unit tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b152c36a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b152c36abf45ab683f376028ed28854bf39a455a` (Scan validated sampler regions by direct RGB row offsets) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 50c7bb8e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `50c7bb8ebc1fe64dd7944e2662fd06c6aa3244c1` (Refuse an empty Firefox --profile with a clear message) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 77034173 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `77034173b743754578c02530e3c97598130bf2ad` (Share image detector input validation through one helper) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of a84ce1c6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `a84ce1c6b49cd44761b11dd1cbccaaca63ce8b16` (recovered leftover work from feature: Resolve PLANS.md conflict so the scrolled-viewport change can merge) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of d96007c1 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `d96007c123ef612d5e2755e551136f5d0b284e9d` (Fix misattributed ValueError expectations in test_image_format's non-bytes test) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ef308bc6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ef308bc69c95f125a4e6967f7cf7233f63ab37b2` (Share signal-safe child startup between process supervisors) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b89256d3 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b89256d3db85f6c023cf8267072c16469a5a158e` (Fix test_image_format's detector-name expectation; ask about min>max windows) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 586acbef never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `586acbefa494f3f71ec160324711c2470125cbb4` (Make a flat GTK 3 frame draw no border or inset shadow and pin it) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 13146e2a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `13146e2a198e161471366d97c4915492410d8bad` (Add the opt-in per-channel maxima fidelity diagnostic) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 47a08cf6 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `47a08cf6b5e566a27e7bcf1c00fde37068c46d2e` (Add three tests pinning convert_jpeg's untested failure diagnostics in tests/test_sample_jpeg.py) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ae3baa10 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ae3baa101fa311a74dbbab046e6051447dc7912a` (Drop the stale `_None yet._` placeholder PLANS.md left under a non-empty ## Planned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of f81c4303 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `f81c4303bbfd6a8074369883b21b42624d6695b6` (Add the RTL spin-field etch mirror to the GTK 3 Platinum sheet and pin it in tests) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b301e2cc never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b301e2ccd52dee7182b6e7bacd896c86b028cda6` (Add per-column fidelity mismatch diagnostics) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 521ab51d never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `521ab51d4363c6965549b79379d61256db41d2ac` (Move the GTK 3 child-probe harness (constants + runner) from tests/test_gtk_theme_controls.py into…) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 8f78a64a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `8f78a64a6bb6f6c32702b92cdc5eabad06d05494` (Flatten all five depth-4 branch nestings in tools/ by extracting named helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 5e7ce62e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `5e7ce62e76620051f4584dee424d23c65d2ba99f` (Land the GTK 3 OSD spin-field RTL etch mirror as four state twins in the Platinum sheet) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 2fd4e245 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `2fd4e2452a764db59cf48652a01a2ba2f26f7888` (Refuse contradictory min/max sampler filter windows; rewrite empty fixtures) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 741fa00e never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `741fa00ecaff28ae6cc646441b0fffc0c24725d6` (Collapse the render CLI's twelve dialog modes into one DIALOG_MODES table) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 36aefe19 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `36aefe19b1d43f71776ed727844cb251479a5ef0` (Restate GTK 3 disabled-view arms to landed grey ink and white field) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1bb9badc never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1bb9badca4b08f6fd8ddf71892f2f44a5e6a0f86` (Pin the JPEG diagnostic's ImageMagick-temporary path scrub in test_sample_jpeg) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b1727988 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b172798834b6fb988d99ecfc66e1469e6acd5ad3` (Add opt-in horizontal mismatch runs to fidelity reports) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 808c2fb8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `808c2fb8878b1d98bf7aec5e5236f66e3e6aad03` (Add opt-in vertical mismatch-run diagnostics) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cf4a178f never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cf4a178f53737f4e2c9086216cc0d38944a0acb5` (Land the GTK 4 disabled-view grey-ink plan with tests and an invariants row) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 590bed87 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `590bed879b8d067734073f2153ad6892da0d2448` (Share eight fidelity run suites' _pair builder via difference_pair) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of ca6cf610 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `ca6cf610f313a9146c1d902b7076af44a11e214f` (Add horizontal matching segments to reference color searches) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 6f265379 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `6f265379b03367722188b4a61cda39f8084dc5c5` (Report GTK staging cleanup failures with their file paths) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 513110c2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `513110c2d9446d4f2932dc5e276d9d418987b85f` (Add the absolute `--max-differing` fidelity budget) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 89fbd1d2 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `89fbd1d2defd8e7b06abd2197b936b287e7d73b5` (Flatten all eight depth-≥5 nested functions in the test tree by extracting named helpers) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 60483c1b never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `60483c1b2e6a876f6c2ea7d4c8168aed4fd14256` (Add vertical matching segment reports to the reference sampler) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 1e363ab8 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `1e363ab8635dffca73e8805c0c610c2fd0d164e3` (Update tools/fidelity.py, tools/fidelity_arguments.py, tests/test_fidelity_cli_parser.py and 1 more) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of cd47f092 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `cd47f09233e23b84e4c66cfb5ab5ff12985e4683` (Drop the stale `_None yet._` placeholder left in PLANS.md ## Planned) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of 06e39637 never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `06e39637917a583d5c0b206a35f6ef680798913c` (Move theme config writing into its own module) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

### post-merge review of b095f36a never reached a verdict (found by the review role 2026-11-11)

The post-merge review of commit `b095f36afe24e7ffc5c3030972aadf434b341839` (Single-source the Makefile's RENDER_MODE list; pin it to DIALOG_MODES) never reached a verdict: You’ve hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/settings/usage to purchase more credits or try again at 8:49 PM.. It stays on main as ordinary unreviewed backlog work. To settle it, read the commit's diff on main: fix what is wrong, or move this entry to Fixed with a Fix paragraph naming what you checked. Do not park it with a Needs review note: the review never runs again, so nothing would lift the note.

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

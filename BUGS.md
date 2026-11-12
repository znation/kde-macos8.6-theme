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

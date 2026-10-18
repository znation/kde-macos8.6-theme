# Placeholders

Temporary stand-in assets shipped so the theme's plumbing works end to end. Each
is our own generic art, not a reproduction of Apple's Platinum artwork (see the
2026-10-18 answer in QUESTIONS.md). A placeholder asset carries a `PLACEHOLDER:`
comment marker naming what it stands in for; `tests/test_placeholders.py`
cross-checks this table against those markers, so a new placeholder added
without a row fails `make check`.

There are no placeholders left: the icon theme's five icons are now final
non-infringing Platinum-style art (see the "Mac OS 8.6 Platinum icon theme:
replace the placeholder art with final non-infringing art" entry under PLANS.md's
`## Done`). Add a row here in the same change that adds a new placeholder.

| Placeholder | Stands in for |
| --- | --- |

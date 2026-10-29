"""The placeholder register checker's mutation table.

``tests/support/placeholders.py``'s marker scanner enforces a boundary the shipped
data happens not to cross. Each mutation here derives one named boundary from
a copy of the real register (and a scratch theme root), so
``tests/test_checker_mutations.py`` can apply it and observe the checker's
answer instead of waiting for a reader. :mod:`support.checker_scratch` holds
the shared scratch copy and the :data:`~support.checker_scratch.Mutation`
record.

A mutation's ``diagnostic`` is the substring the checker's ``AssertionError``
must contain; a mutation with a diagnostic is a rejection boundary and must be
named in ``tests/support/placeholders.py``'s ``REJECTION_SHAPES``. ``None`` marks an
acceptance boundary, where the checker must find the input and ``observe``
pins what it must produce -- the placeholder formats are accepted, not
rejected, so no diagnostic exists to match.
"""

from __future__ import annotations

from support.checker_scratch import PLACEHOLDERS_REGISTER, Mutation

# Real shipped files the placeholder mutations use. The scratch theme root is
# built from empty subsystem directories, so a mutation can write one of these
# paths, leave it out, or write it unmarked, and the checker's answer is
# observable. Naming a repository path that exists keeps the stage
# self-check's added-nonexistent-path guard satisfied instead of the harness
# hiding the path behind a runtime join.
USER_TRASH_ICON = "theme/icons/org.macos8.desktop/32x32/places/user-trash.svg"
FOLDER_ICON = "theme/icons/org.macos8.desktop/32x32/places/folder.svg"
ABSENT_ICON = "theme/icons/org.macos8.desktop/32x32/places/inode-directory.svg"
KVCONFIG = "theme/kvantum/org.macos8.desktop/org.macos8.desktop.kvconfig"
LAYOUT = "theme/look-and-feel/org.macos8.desktop/contents/layouts/org.kde.plasma.desktop-layout.js"
AURORAE_DESKTOPRC = "theme/aurorae/themes/org.macos8.desktop/org.macos8.desktoprc"
# An existing theme text asset; the mutation replaces the scratch copy with a
# symlink to a missing sibling so the marker scanner's read arm fires.
DANGLING_LINK = "theme/aurorae/themes/org.macos8.desktop/metadata.desktop"


def _append_row(text, asset, description):
    """Return *text* with one ``| `asset` | description |`` register row added."""
    if not text.endswith("\n"):
        text += "\n"
    return text + f"| `{asset}` | {description} |\n"


def _placeholder_acceptance(asset, description):
    """Return an ``apply`` that adds a marked file *asset* and its register row."""

    def apply(scratch):
        scratch.write_repo_file(asset, f"# PLACEHOLDER: {description}\n")
        scratch.write_placeholders(
            _append_row(scratch.placeholders_text, asset, description)
        )

    return apply


def _observe_placeholder(asset):
    """Return an ``observe`` that the marker scanner found the marked file *asset*."""

    def observe(scratch):
        from support.placeholders import markers

        if asset not in markers(scratch.root):
            raise AssertionError(
                f"{asset} carries a PLACEHOLDER: marker the scanner did not find"
            )

    return observe


def _apply_marker_without_row(scratch):
    scratch.write_repo_file(USER_TRASH_ICON, "<!-- PLACEHOLDER: an orphan -->\n")


def _apply_row_without_file(scratch):
    scratch.write_placeholders(
        _append_row(scratch.placeholders_text, ABSENT_ICON, "an absent icon")
    )


def _apply_row_without_marker(scratch):
    scratch.write_repo_file(USER_TRASH_ICON, "<svg/>\n")
    scratch.write_placeholders(
        _append_row(scratch.placeholders_text, USER_TRASH_ICON, "a plain icon")
    )


def _apply_duplicate_register_row(scratch):
    text = _append_row(scratch.placeholders_text, FOLDER_ICON, "a duplicated icon")
    scratch.write_repo_file(FOLDER_ICON, "<!-- PLACEHOLDER: a duplicated icon -->\n")
    scratch.write_placeholders(
        _append_row(text, FOLDER_ICON, "a duplicated icon, again")
    )


def _apply_unreadable_register(scratch):
    scratch.write_directory(PLACEHOLDERS_REGISTER)


def _apply_dangling_symlink(scratch):
    scratch.write_symlink(DANGLING_LINK, "missing.desktop")


PLACEHOLDER_MUTATIONS = (
    Mutation("marker-without-row", _apply_marker_without_row, "has no row", None),
    Mutation("row-without-file", _apply_row_without_file, "does not exist", None),
    Mutation("row-without-marker", _apply_row_without_marker, "carries no", None),
    Mutation(
        "duplicate-register-row",
        _apply_duplicate_register_row,
        "duplicate row",
        None,
    ),
    Mutation(
        "unreadable-register",
        _apply_unreadable_register,
        "cannot be read",
        None,
    ),
    Mutation(
        "dangling-symlink-inside-theme",
        _apply_dangling_symlink,
        "cannot be read",
        None,
    ),
    Mutation(
        "kvconfig-marker",
        _placeholder_acceptance(KVCONFIG, "a Kvantum widget style"),
        None,
        _observe_placeholder(KVCONFIG),
    ),
    Mutation(
        "js-marker",
        _placeholder_acceptance(LAYOUT, "a desktop layout"),
        None,
        _observe_placeholder(LAYOUT),
    ),
    Mutation(
        "desktoprc-marker",
        _placeholder_acceptance(AURORAE_DESKTOPRC, "an Aurorae decoration config"),
        None,
        _observe_placeholder(AURORAE_DESKTOPRC),
    ),
)

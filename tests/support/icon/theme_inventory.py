"""The icon theme package's identity and shipped-icon inventory.

``test_icon_theme`` and ``test_icon_theme_geometry`` share these constants:
the package's id and directory, the icons it ships at each size, the standard
XDG folder places and the folder aliases that draw the folder art.
"""

import os

from support.repo_root import ROOT

ICON_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "icons", ICON_ID)

# The icons the package ships: the desktop's hard disk, folder, document,
# Trash and full Trash (32x32), the `inode-directory` alias KDE resolves a
# directory to plus the `user-home` and `user-desktop` places, all drawing
# the folder art, 16x16 and 22x22 renditions of the folder, aliases, Trash
# and full Trash, 16x16 and 22x22 renditions of the hard disk and document,
# the removable-drive `drive-removable-media` icon at all three sizes (our own
# drawing of a USB stick, sharing the hard disk's body and bevel),
# the kicker logo the menu bar's top-left button shows at the two panel sizes,
# and the `go-next-symbolic` submenu arrow the reference's open Apple menu
# draws.
SHIPPED_ICONS = (
    os.path.join("32x32", "devices", "drive-harddisk.svg"),
    os.path.join("16x16", "devices", "drive-harddisk.svg"),
    os.path.join("22x22", "devices", "drive-harddisk.svg"),
    os.path.join("32x32", "devices", "drive-removable-media.svg"),
    os.path.join("16x16", "devices", "drive-removable-media.svg"),
    os.path.join("22x22", "devices", "drive-removable-media.svg"),
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"),
    os.path.join("16x16", "mimetypes", "text-x-generic.svg"),
    os.path.join("22x22", "mimetypes", "text-x-generic.svg"),
    os.path.join("32x32", "places", "folder.svg"),
    os.path.join("32x32", "places", "inode-directory.svg"),
    os.path.join("32x32", "places", "user-home.svg"),
    os.path.join("32x32", "places", "user-desktop.svg"),
    os.path.join("32x32", "places", "user-trash.svg"),
    os.path.join("32x32", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "folder.svg"),
    os.path.join("16x16", "places", "inode-directory.svg"),
    os.path.join("16x16", "places", "user-home.svg"),
    os.path.join("16x16", "places", "user-desktop.svg"),
    os.path.join("16x16", "places", "user-trash.svg"),
    os.path.join("16x16", "places", "user-trash-full.svg"),
    os.path.join("22x22", "places", "folder.svg"),
    os.path.join("22x22", "places", "inode-directory.svg"),
    os.path.join("22x22", "places", "user-home.svg"),
    os.path.join("22x22", "places", "user-desktop.svg"),
    os.path.join("22x22", "places", "user-trash.svg"),
    os.path.join("22x22", "places", "user-trash-full.svg"),
    os.path.join("16x16", "places", "start-here-kde-symbolic.svg"),
    os.path.join("22x22", "places", "start-here-kde-symbolic.svg"),
    os.path.join("16x16", "actions", "go-next-symbolic.svg"),
    os.path.join("22x22", "actions", "go-next-symbolic.svg"),
)

# The standard XDG folder places KDE resolves; the package draws each one
# with the matching size's Platinum folder, as Mac OS 8.6 draws one folder
# shape for a directory. KIO's places model names these eight names
# (read from `libKF6KIOCore.so.6`), while the standard `user-places.xbel`
# entries spell Downloads with the plural `folder-downloads` (the installed
# file's Downloads bookmark, line 58), so ship both download names.
STANDARD_PLACES = (
    "folder-documents",
    "folder-download",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
    "folder-templates",
    "folder-public",
    "folder-temp",
)
SHIPPED_ICONS += tuple(
    os.path.join(size, "places", place + ".svg")
    for size in ("16x16", "22x22", "32x32")
    for place in STANDARD_PLACES
)

# The blank-document names: files whose type KDE does not recognise, and empty
# files. `application-octet-stream` and `application-x-zerosize` are the
# `application/octet-stream` and `application/x-zerosize` MIME types spelled as
# icon names (both declared in the installed shared MIME database), and
# `unknown` is a string in the installed `libKF6KIOGui.so.6`. Each needs its
# own file: a probe showed that adding one name's file changes only that name.
BLANK_DOCUMENTS = (
    "application-octet-stream",
    "application-x-zerosize",
    "unknown",
)
SHIPPED_ICONS += tuple(
    os.path.join(size, "mimetypes", name + ".svg")
    for size in ("16x16", "22x22", "32x32")
    for name in BLANK_DOCUMENTS
)

# The standard places data's folder names that this package draws. KDE
# writes these into a user's Places list, and its Downloads entry is the
# plural `folder-downloads` rather than the `folder-download` the KIO places
# model also names; pin them separately so the inventory cannot pass by
# dropping a name KDE actually resolves.
USER_PLACES_ICONS = (
    "folder-documents",
    "folder-downloads",
    "folder-music",
    "folder-pictures",
    "folder-videos",
)

# The names that share the folder art: the KDE directory alias, the Home and
# Desktop places, and every standard XDG place.
FOLDER_ALIASES = ("inode-directory", "user-home", "user-desktop", *STANDARD_PLACES)

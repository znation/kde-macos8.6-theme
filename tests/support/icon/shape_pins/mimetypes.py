"""Pins for the mimetypes family: documents, images, media, mail,
archives and blank pages.

Every entry is a ``os.path.join(size, "mimetypes", name.svg)`` key holding
the pinned tuple of drawing elements for that shipped file, in document
order. The pins live beside ``theme_inventory``; the geometry tests in
``test_icon_theme_geometry`` compare each shipped SVG with its tuple.
"""

import os

from support.icon.shape_pins._shared import (
    _PAGE_16,
    _PAGE_22,
    _PAGE_32,
    _SEALED_PACKAGE_16,
    _SEALED_PACKAGE_22,
    _SEALED_PACKAGE_32,
    _shape,
)

PINS = {
    os.path.join("32x32", "mimetypes", "text-x-generic.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="15", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="8", height="1", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "text-x-generic.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="7", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="9", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="11", width="4", height="1", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "text-x-generic.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="10", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="13", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="16", width="5", height="1", fill="#999999"),
    ),
    os.path.join("32x32", "mimetypes", "text-x-generic-template.svg"): (
        *_PAGE_32,
        _shape("rect", x="9", y="13", width="14", height="11", fill="#000000"),
        _shape("rect", x="10", y="14", width="12", height="9", fill="#DDDDDD"),
        _shape("rect", x="15", y="13", width="3", height="1", fill="#FFFFFF"),
        _shape("rect", x="15", y="23", width="3", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="17", width="1", height="3", fill="#FFFFFF"),
        _shape("rect", x="22", y="17", width="1", height="3", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "text-x-generic-template.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="7", height="5", fill="#000000"),
        _shape("rect", x="6", y="7", width="5", height="3", fill="#DDDDDD"),
        _shape("rect", x="7", y="6", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="10", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="1", height="2", fill="#FFFFFF"),
        _shape("rect", x="11", y="7", width="1", height="2", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "text-x-generic-template.svg"): (
        *_PAGE_22,
        _shape("rect", x="6", y="8", width="10", height="7", fill="#000000"),
        _shape("rect", x="7", y="9", width="8", height="5", fill="#DDDDDD"),
        _shape("rect", x="10", y="8", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="10", y="14", width="2", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="10", width="1", height="2", fill="#FFFFFF"),
        _shape("rect", x="15", y="10", width="1", height="2", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="3", y="5", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="6", width="24", height="4", fill="#DDDDDD"),
        _shape("rect", x="4", y="6", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="20", height="1", fill="#999999"),
        _shape("rect", x="4", y="11", width="24", height="15", fill="#FFFFFF"),
        _shape("rect", x="13", y="13", width="2", height="11", fill="#000000"),
        _shape("rect", x="15", y="14", width="2", height="9", fill="#000000"),
        _shape("rect", x="17", y="15", width="2", height="7", fill="#000000"),
        _shape("rect", x="19", y="16", width="2", height="5", fill="#000000"),
        _shape("rect", x="21", y="17", width="2", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="1", y="2", width="14", height="12", fill="#000000"),
        _shape("rect", x="2", y="3", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="2", y="3", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#999999"),
        _shape("rect", x="2", y="7", width="12", height="6", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="2", height="4", fill="#000000"),
        _shape("rect", x="8", y="9", width="2", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-executable.svg"): (
        _shape("rect", x="2", y="3", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="4", width="16", height="3", fill="#DDDDDD"),
        _shape("rect", x="3", y="4", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#999999"),
        _shape("rect", x="3", y="8", width="16", height="10", fill="#FFFFFF"),
        _shape("rect", x="9", y="9", width="1", height="8", fill="#000000"),
        _shape("rect", x="10", y="10", width="1", height="6", fill="#000000"),
        _shape("rect", x="11", y="11", width="1", height="4", fill="#000000"),
        _shape("rect", x="12", y="12", width="1", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="15", width="12", height="7", fill="#000000"),
        _shape("rect", x="12", y="17", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="13", y="18", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="12", y="19", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="15", y="19", width="3", height="1", fill="#FFFFFF"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="5", fill="#000000"),
        _shape("rect", x="6", y="7", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="7", y="8", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="9", width="1", height="1", fill="#FFFFFF"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-shellscript.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="10", width="8", height="5", fill="#000000"),
        _shape("rect", x="8", y="11", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="9", y="12", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#FFFFFF"),
        _shape("rect", x="11", y="13", width="2", height="1", fill="#FFFFFF"),
    ),
    os.path.join("32x32", "mimetypes", "package-x-generic.svg"): (
        *_SEALED_PACKAGE_32,
    ),
    os.path.join("16x16", "mimetypes", "package-x-generic.svg"): (
        *_SEALED_PACKAGE_16,
    ),
    os.path.join("22x22", "mimetypes", "package-x-generic.svg"): (
        *_SEALED_PACKAGE_22,
    ),
    # The ZIP-archive icon shares the package box (every drawing element
    # of `package-x-generic.svg` at that size) and holds a black zipper
    # slider tab riding the grey tape stripe. The name is the type-spelled
    # `application/zip` MIME type in the installed shared MIME database.
    os.path.join("32x32", "mimetypes", "application-zip.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="14", y="18", width="4", height="5", fill="#000000"),
        _shape("rect", x="15", y="19", width="2", height="3", fill="#DDDDDD"),
    ),
    os.path.join("16x16", "mimetypes", "application-zip.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="6", y="8", width="4", height="3", fill="#000000"),
        _shape("rect", x="7", y="9", width="2", height="1", fill="#DDDDDD"),
    ),
    os.path.join("22x22", "mimetypes", "application-zip.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="9", y="10", width="4", height="4", fill="#000000"),
        _shape("rect", x="10", y="11", width="2", height="2", fill="#DDDDDD"),
    ),
    # The tar-archive icon shares the package box (every drawing element
    # of `package-x-generic.svg` at that size) and holds a black capital
    # letter T standing on the white body left of the grey tape stripe.
    # The name is the type-spelled `application/x-tar` MIME type in the
    # installed shared MIME database.
    os.path.join("32x32", "mimetypes", "application-x-tar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="5", y="13", width="10", height="2", fill="#000000"),
        _shape("rect", x="9", y="15", width="2", height="8", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-tar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="2", y="7", width="4", height="2", fill="#000000"),
        _shape("rect", x="3", y="9", width="2", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-tar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="3", y="9", width="6", height="2", fill="#000000"),
        _shape("rect", x="5", y="11", width="2", height="5", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="3", y="7", width="26", height="20", fill="#000000"),
        _shape("rect", x="4", y="8", width="24", height="18", fill="#FFFFFF"),
        _shape("path", d="M13 11 L23 17 L13 23 Z", fill="#000000"),
        _shape("rect", x="12", y="27", width="8", height="2", fill="#000000"),
        _shape("rect", x="8", y="29", width="16", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#FFFFFF"),
        _shape("path", d="M7 6 L10 8 L7 10 Z", fill="#000000"),
        _shape("rect", x="6", y="13", width="4", height="1", fill="#000000"),
        _shape("rect", x="4", y="14", width="8", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "video-x-generic.svg"): (
        _shape("rect", x="2", y="5", width="18", height="13", fill="#000000"),
        _shape("rect", x="3", y="6", width="16", height="11", fill="#FFFFFF"),
        _shape("path", d="M9 8 L15 11 L9 14 Z", fill="#000000"),
        _shape("rect", x="8", y="19", width="6", height="1", fill="#000000"),
        _shape("rect", x="5", y="20", width="12", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "x-office-document.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="12", width="12", height="2", fill="#000000"),
        _shape("rect", x="10", y="15", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="8", height="1", fill="#999999"),
        _shape("rect", x="14", y="24", width="8", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "x-office-document.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="5", width="6", height="1", fill="#000000"),
        _shape("rect", x="5", y="7", width="6", height="1", fill="#999999"),
        _shape("rect", x="5", y="9", width="6", height="1", fill="#999999"),
        _shape("rect", x="6", y="12", width="4", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "x-office-document.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="7", width="8", height="2", fill="#000000"),
        _shape("rect", x="7", y="10", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="13", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="16", width="5", height="1", fill="#999999"),
        _shape("rect", x="10", y="18", width="5", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "x-office-spreadsheet.svg"): (
        *_PAGE_32,
        _shape("rect", x="9", y="12", width="14", height="13", fill="#000000"),
        _shape("rect", x="10", y="13", width="12", height="11", fill="#FFFFFF"),
        _shape("rect", x="10", y="13", width="12", height="2", fill="#DDDDDD"),
        _shape("rect", x="14", y="15", width="1", height="9", fill="#999999"),
        _shape("rect", x="19", y="15", width="1", height="9", fill="#999999"),
        _shape("rect", x="10", y="18", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="21", width="12", height="1", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "x-office-spreadsheet.svg"): (
        *_PAGE_16,
        _shape("rect", x="4", y="6", width="8", height="6", fill="#000000"),
        _shape("rect", x="5", y="7", width="6", height="4", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="6", height="1", fill="#DDDDDD"),
        _shape("rect", x="7", y="8", width="1", height="3", fill="#999999"),
        _shape("rect", x="5", y="9", width="6", height="1", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "x-office-spreadsheet.svg"): (
        *_PAGE_22,
        _shape("rect", x="6", y="8", width="10", height="9", fill="#000000"),
        _shape("rect", x="7", y="9", width="8", height="7", fill="#FFFFFF"),
        _shape("rect", x="7", y="9", width="8", height="2", fill="#DDDDDD"),
        _shape("rect", x="10", y="11", width="1", height="5", fill="#999999"),
        _shape("rect", x="13", y="11", width="1", height="5", fill="#999999"),
        _shape("rect", x="7", y="12", width="8", height="1", fill="#999999"),
        _shape("rect", x="7", y="14", width="8", height="1", fill="#999999"),
    ),
    os.path.join("32x32", "mimetypes", "text-x-script.svg"): (
        *_PAGE_32,
        _shape("rect", x="12", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="8", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="12", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="18", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="20", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="22", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="20", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="18", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="23", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="25", width="8", height="1", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "text-x-script.svg"): (
        *_PAGE_16,
        _shape("rect", x="6", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="11", width="6", height="1", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "text-x-script.svg"): (
        *_PAGE_22,
        _shape("rect", x="9", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="15", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="17", width="8", height="1", fill="#999999"),
    ),
    os.path.join("32x32", "mimetypes", "x-office-presentation.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="12", width="12", height="9", fill="#000000"),
        _shape("rect", x="11", y="13", width="10", height="7", fill="#FFFFFF"),
        _shape("rect", x="11", y="13", width="10", height="2", fill="#DDDDDD"),
        _shape("rect", x="12", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="15", y="16", width="2", height="3", fill="#000000"),
        _shape("rect", x="18", y="15", width="2", height="4", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "x-office-presentation.svg"): (
        *_PAGE_16,
        _shape("rect", x="4", y="6", width="8", height="6", fill="#000000"),
        _shape("rect", x="5", y="7", width="6", height="4", fill="#FFFFFF"),
        _shape("rect", x="5", y="7", width="6", height="1", fill="#DDDDDD"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="8", width="1", height="2", fill="#000000"),
        _shape("rect", x="10", y="9", width="1", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "x-office-presentation.svg"): (
        *_PAGE_22,
        _shape("rect", x="6", y="8", width="10", height="8", fill="#000000"),
        _shape("rect", x="7", y="9", width="8", height="6", fill="#FFFFFF"),
        _shape("rect", x="7", y="9", width="8", height="1", fill="#DDDDDD"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="12", width="1", height="2", fill="#000000"),
        _shape("rect", x="12", y="11", width="1", height="3", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "x-office-address-book.svg"): (
        _shape("rect", x="4", y="2", width="24", height="28", fill="#000000"),
        _shape("rect", x="5", y="3", width="22", height="26", fill="#DDDDDD"),
        _shape("rect", x="5", y="3", width="22", height="2", fill="#FFFFFF"),
        _shape("rect", x="5", y="3", width="2", height="26", fill="#FFFFFF"),
        _shape("rect", x="25", y="3", width="2", height="26", fill="#999999"),
        _shape("rect", x="5", y="27", width="22", height="2", fill="#999999"),
        _shape("rect", x="8", y="7", width="12", height="2", fill="#000000"),
        _shape("rect", x="8", y="11", width="14", height="1", fill="#000000"),
        _shape("rect", x="8", y="13", width="11", height="1", fill="#000000"),
        _shape("rect", x="8", y="15", width="14", height="1", fill="#000000"),
        _shape("rect", x="8", y="17", width="9", height="1", fill="#000000"),
        _shape("rect", x="8", y="19", width="14", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "x-office-address-book.svg"): (
        _shape("rect", x="1", y="1", width="14", height="14", fill="#000000"),
        _shape("rect", x="2", y="2", width="12", height="12", fill="#DDDDDD"),
        _shape("rect", x="2", y="2", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="2", width="1", height="12", fill="#FFFFFF"),
        _shape("rect", x="13", y="2", width="1", height="12", fill="#999999"),
        _shape("rect", x="2", y="13", width="12", height="1", fill="#999999"),
        _shape("rect", x="4", y="4", width="7", height="1", fill="#000000"),
        _shape("rect", x="4", y="6", width="9", height="1", fill="#000000"),
        _shape("rect", x="4", y="8", width="6", height="1", fill="#000000"),
        _shape("rect", x="4", y="10", width="9", height="1", fill="#000000"),
        _shape("rect", x="4", y="12", width="5", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "x-office-address-book.svg"): (
        _shape("rect", x="2", y="1", width="18", height="20", fill="#000000"),
        _shape("rect", x="3", y="2", width="16", height="18", fill="#DDDDDD"),
        _shape("rect", x="3", y="2", width="16", height="2", fill="#FFFFFF"),
        _shape("rect", x="3", y="2", width="2", height="18", fill="#FFFFFF"),
        _shape("rect", x="17", y="2", width="2", height="18", fill="#999999"),
        _shape("rect", x="3", y="18", width="16", height="2", fill="#999999"),
        _shape("rect", x="5", y="6", width="9", height="2", fill="#000000"),
        _shape("rect", x="5", y="10", width="11", height="1", fill="#000000"),
        _shape("rect", x="5", y="12", width="8", height="1", fill="#000000"),
        _shape("rect", x="5", y="14", width="11", height="1", fill="#000000"),
        _shape("rect", x="5", y="16", width="6", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="6", y="23", width="7", height="4", fill="#000000"),
        _shape("rect", x="11", y="6", width="2", height="21", fill="#000000"),
        _shape("rect", x="18", y="21", width="7", height="4", fill="#000000"),
        _shape("rect", x="23", y="6", width="2", height="19", fill="#000000"),
        _shape("rect", x="11", y="6", width="14", height="5", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="4", y="16", width="5", height="3", fill="#000000"),
        _shape("rect", x="8", y="4", width="2", height="15", fill="#000000"),
        _shape("rect", x="12", y="14", width="5", height="3", fill="#000000"),
        _shape("rect", x="15", y="4", width="2", height="13", fill="#000000"),
        _shape("rect", x="8", y="4", width="9", height="3", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "audio-x-generic.svg"): (
        _shape("rect", x="2", y="11", width="4", height="2", fill="#000000"),
        _shape("rect", x="5", y="3", width="1", height="10", fill="#000000"),
        _shape("rect", x="9", y="10", width="4", height="2", fill="#000000"),
        _shape("rect", x="12", y="3", width="1", height="9", fill="#000000"),
        _shape("rect", x="5", y="3", width="8", height="2", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "font-x-generic.svg"): (
        *_PAGE_32,
        _shape("rect", x="16", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="15", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="17", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="15", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="17", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="18", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="15", width="1", height="1", fill="#000000"),
        _shape("rect", x="18", y="15", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="16", width="1", height="1", fill="#000000"),
        _shape("rect", x="19", y="16", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="17", width="1", height="1", fill="#000000"),
        _shape("rect", x="19", y="17", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="18", width="9", height="1", fill="#000000"),
        _shape("rect", x="12", y="19", width="1", height="1", fill="#000000"),
        _shape("rect", x="20", y="19", width="1", height="1", fill="#000000"),
        _shape("rect", x="11", y="20", width="1", height="1", fill="#000000"),
        _shape("rect", x="21", y="20", width="1", height="1", fill="#000000"),
        _shape("rect", x="11", y="21", width="1", height="1", fill="#000000"),
        _shape("rect", x="21", y="21", width="1", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "font-x-generic.svg"): (
        *_PAGE_22,
        _shape("rect", x="11", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="12", width="5", height="1", fill="#000000"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="13", width="1", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "font-x-generic.svg"): (
        *_PAGE_16,
        _shape("rect", x="8", y="5", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="10", width="5", height="1", fill="#000000"),
        _shape("rect", x="5", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="11", y="11", width="1", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "text-html.svg"): (
        _shape("rect", x="3", y="5", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="6", width="24", height="4", fill="#DDDDDD"),
        _shape("rect", x="4", y="6", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="8", width="20", height="1", fill="#999999"),
        _shape("rect", x="4", y="11", width="24", height="15", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="19", r="6", fill="#000000"),
        _shape("circle", cx="16", cy="19", r="5", fill="#FFFFFF"),
        _shape("rect", x="11", y="19", width="11", height="1", fill="#000000"),
        _shape("rect", x="16", y="14", width="1", height="11", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "text-html.svg"): (
        _shape("rect", x="1", y="2", width="14", height="12", fill="#000000"),
        _shape("rect", x="2", y="3", width="12", height="3", fill="#DDDDDD"),
        _shape("rect", x="2", y="3", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="4", width="8", height="1", fill="#999999"),
        _shape("rect", x="2", y="7", width="12", height="6", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="10", r="2", fill="#000000"),
        _shape("circle", cx="8", cy="10", r="1", fill="#FFFFFF"),
        _shape("rect", x="6", y="10", width="5", height="1", fill="#000000"),
        _shape("rect", x="8", y="8", width="1", height="4", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "text-html.svg"): (
        _shape("rect", x="2", y="3", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="4", width="16", height="3", fill="#DDDDDD"),
        _shape("rect", x="3", y="4", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="5", y="5", width="12", height="1", fill="#999999"),
        _shape("rect", x="3", y="8", width="16", height="10", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="13", r="4", fill="#000000"),
        _shape("circle", cx="11", cy="13", r="3", fill="#FFFFFF"),
        _shape("rect", x="8", y="13", width="7", height="1", fill="#000000"),
        _shape("rect", x="11", y="10", width="1", height="7", fill="#000000"),
    ),
    # The mail icon KDE draws for `mailto:` URL items (the item-icon name
    # read from the installed KIO core); one file covers exactly its own
    # name, since the shared MIME database gives it no binding.
    os.path.join("32x32", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="2", y="6", width="28", height="20", fill="#000000"),
        _shape("rect", x="3", y="7", width="26", height="18", fill="#DDDDDD"),
        _shape("path", d="M3 7 L16 17 L29 7 Z", fill="#000000"),
        _shape("path", d="M4 8 L16 16 L28 8 Z", fill="#DDDDDD"),
    ),
    os.path.join("16x16", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="1", y="3", width="14", height="10", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="8", fill="#DDDDDD"),
        _shape("path", d="M2 4 L8 9 L14 4 Z", fill="#000000"),
        _shape("path", d="M3 5 L8 8 L13 5 Z", fill="#DDDDDD"),
    ),
    os.path.join("22x22", "mimetypes", "internet-mail.svg"): (
        _shape("rect", x="1", y="4", width="20", height="14", fill="#000000"),
        _shape("rect", x="2", y="5", width="18", height="12", fill="#DDDDDD"),
        _shape("path", d="M2 5 L11 12 L20 5 Z", fill="#000000"),
        _shape("path", d="M3 6 L11 11 L19 6 Z", fill="#DDDDDD"),
    ),
    # The PDF item icon KDE draws for `application/pdf` items (the
    # type-spelled icon name of the installed shared MIME database's
    # `application/pdf` type, whose `generic-icon` is the shipped
    # `x-office-document`); one file covers exactly its own name, and the
    # drawing shares the generic document's page.
    os.path.join("32x32", "mimetypes", "application-pdf.svg"): (
        *_PAGE_32,
        _shape("rect", x="10", y="12", width="12", height="1", fill="#999999"),
        _shape("rect", x="10", y="15", width="8", height="1", fill="#999999"),
        _shape("rect", x="16", y="18", width="8", height="8", fill="#000000"),
        _shape("rect", x="17", y="19", width="6", height="6", fill="#DDDDDD"),
    ),
    os.path.join("16x16", "mimetypes", "application-pdf.svg"): (
        *_PAGE_16,
        _shape("rect", x="5", y="6", width="6", height="1", fill="#999999"),
        _shape("rect", x="7", y="8", width="5", height="5", fill="#000000"),
        _shape("rect", x="8", y="9", width="3", height="3", fill="#DDDDDD"),
    ),
    os.path.join("22x22", "mimetypes", "application-pdf.svg"): (
        *_PAGE_22,
        _shape("rect", x="7", y="8", width="8", height="1", fill="#999999"),
        _shape("rect", x="11", y="11", width="5", height="5", fill="#000000"),
        _shape("rect", x="12", y="12", width="3", height="3", fill="#DDDDDD"),
    ),
    # The 7z-archive item icon KDE draws for `application/x-7z-compressed`
    # items (the type-spelled icon name of the installed shared MIME
    # database's `application/x-7z-compressed` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its own
    # name, and the drawing shares the sealed package box.
    os.path.join("32x32", "mimetypes", "application-x-7z-compressed.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="8", y="13", width="6", height="2", fill="#000000"),
        _shape("rect", x="11", y="15", width="3", height="2", fill="#000000"),
        _shape("rect", x="9", y="17", width="3", height="2", fill="#000000"),
        _shape("rect", x="7", y="19", width="3", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-7z-compressed.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="3", y="7", width="4", height="1", fill="#000000"),
        _shape("rect", x="5", y="8", width="2", height="1", fill="#000000"),
        _shape("rect", x="4", y="9", width="2", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-7z-compressed.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="5", y="8", width="4", height="2", fill="#000000"),
        _shape("rect", x="7", y="10", width="2", height="2", fill="#000000"),
        _shape("rect", x="6", y="12", width="2", height="2", fill="#000000"),
    ),
    # The gzip-archive item icon KDE draws for `application/gzip`
    # items (the type-spelled icon name of the installed shared MIME
    # database's `application/gzip` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its own
    # name, and the drawing shares the sealed package box.
    os.path.join("32x32", "mimetypes", "application-gzip.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="8", y="13", width="2", height="6", fill="#000000"),
        _shape("rect", x="6", y="19", width="6", height="2", fill="#000000"),
        _shape("rect", x="7", y="21", width="4", height="1", fill="#000000"),
        _shape("rect", x="8", y="22", width="2", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-gzip.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="3", y="7", width="2", height="3", fill="#000000"),
        _shape("rect", x="2", y="10", width="4", height="1", fill="#000000"),
        _shape("rect", x="3", y="11", width="2", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-gzip.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="5", y="9", width="2", height="4", fill="#000000"),
        _shape("rect", x="4", y="13", width="4", height="2", fill="#000000"),
        _shape("rect", x="5", y="15", width="2", height="1", fill="#000000"),
    ),
    # The deb-package item icon KDE draws for
    # `application/vnd.debian.binary-package` items (the type-spelled
    # icon name of the installed shared MIME database's
    # `application/vnd.debian.binary-package` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its own
    # name, and the drawing shares the sealed package box and holds a
    # black capital letter D.
    os.path.join("32x32", "mimetypes", "application-vnd.debian.binary-package.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="5", y="15", width="6", height="1", fill="#000000"),
        _shape("rect", x="5", y="16", width="1", height="5", fill="#000000"),
        _shape("rect", x="10", y="16", width="1", height="5", fill="#000000"),
        _shape("rect", x="5", y="21", width="6", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-vnd.debian.binary-package.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="3", y="7", width="3", height="1", fill="#000000"),
        _shape("rect", x="3", y="8", width="1", height="3", fill="#000000"),
        _shape("rect", x="5", y="8", width="1", height="3", fill="#000000"),
        _shape("rect", x="3", y="11", width="3", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-vnd.debian.binary-package.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="4", y="9", width="5", height="1", fill="#000000"),
        _shape("rect", x="4", y="10", width="1", height="5", fill="#000000"),
        _shape("rect", x="8", y="10", width="1", height="5", fill="#000000"),
        _shape("rect", x="4", y="15", width="5", height="1", fill="#000000"),
    ),
    # The RAR-archive item icon KDE draws for `application/vnd.rar`
    # items (the type-spelled icon name of the installed shared MIME
    # database's `application/vnd.rar` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its
    # own name, and the drawing shares the sealed package box and holds
    # a stepped diamond on the white body left of the grey tape stripe.
    os.path.join("32x32", "mimetypes", "application-vnd.rar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="9", y="16", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="17", width="3", height="1", fill="#000000"),
        _shape("rect", x="7", y="18", width="5", height="1", fill="#000000"),
        _shape("rect", x="8", y="19", width="3", height="1", fill="#000000"),
        _shape("rect", x="9", y="20", width="1", height="1", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-vnd.rar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="4", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="3", y="8", width="3", height="1", fill="#000000"),
        _shape("rect", x="2", y="9", width="5", height="1", fill="#000000"),
        _shape("rect", x="3", y="10", width="3", height="1", fill="#000000"),
        _shape("rect", x="4", y="11", width="1", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-vnd.rar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="6", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="11", width="3", height="1", fill="#000000"),
        _shape("rect", x="4", y="12", width="5", height="1", fill="#000000"),
        _shape("rect", x="5", y="13", width="3", height="1", fill="#000000"),
        _shape("rect", x="6", y="14", width="1", height="1", fill="#000000"),
    ),
    # The gzip-compressed-tar-archive item icon KDE draws for
    # `application/x-compressed-tar` items (the type-spelled icon name
    # of the installed shared MIME database's
    # `application/x-compressed-tar` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its own
    # name, and the drawing shares the sealed package box and holds a
    # stepped capital Z.
    os.path.join("32x32", "mimetypes", "application-x-compressed-tar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="4", y="13", width="11", height="2", fill="#000000"),
        _shape("rect", x="12", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="8", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="4", y="21", width="11", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-compressed-tar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="2", y="7", width="5", height="1", fill="#000000"),
        _shape("rect", x="5", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="4", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="3", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="2", y="11", width="5", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-compressed-tar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="3", y="9", width="7", height="1", fill="#000000"),
        _shape("rect", x="8", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="4", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="3", y="15", width="7", height="1", fill="#000000"),
    ),
    # The xz-compressed-tar item icon KDE draws for
    # `application/x-xz-compressed-tar` items (the type-spelled icon
    # name of the installed shared MIME database's
    # `application/x-xz-compressed-tar` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its
    # own name, and the drawing shares the sealed package box and holds
    # a capital letter X, two stair-stepped strokes crossing at the
    # face's centre, on the white body left of the grey tape stripe.
    os.path.join("32x32", "mimetypes", "application-x-xz-compressed-tar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="5", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="7", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="9", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="11", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="13", y="21", width="2", height="2", fill="#000000"),
        _shape("rect", x="13", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="11", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="7", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="5", y="21", width="2", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-xz-compressed-tar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="2", y="7", width="2", height="2", fill="#000000"),
        _shape("rect", x="4", y="9", width="2", height="2", fill="#000000"),
        _shape("rect", x="4", y="7", width="2", height="2", fill="#000000"),
        _shape("rect", x="2", y="9", width="2", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-xz-compressed-tar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="3", y="9", width="2", height="2", fill="#000000"),
        _shape("rect", x="5", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="7", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="7", y="9", width="2", height="2", fill="#000000"),
        _shape("rect", x="3", y="13", width="2", height="2", fill="#000000"),
    ),
    # The bzip2-compressed-tar item icon KDE draws for
    # `application/x-bzip2-compressed-tar` items (the type-spelled icon
    # name of the installed shared MIME database's
    # `application/x-bzip2-compressed-tar` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its
    # own name (the type's alias `application/x-bzip-compressed-tar`
    # spells its own name), and the drawing shares the sealed package
    # box and holds a lowercase letter b on the white body left of the
    # grey tape stripe.
    os.path.join("32x32", "mimetypes", "application-x-bzip2-compressed-tar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="5", y="13", width="3", height="11", fill="#000000"),
        _shape("rect", x="8", y="17", width="5", height="7", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-bzip2-compressed-tar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="2", y="7", width="1", height="5", fill="#000000"),
        _shape("rect", x="3", y="9", width="3", height="3", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-bzip2-compressed-tar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="3", y="9", width="2", height="8", fill="#000000"),
        _shape("rect", x="5", y="12", width="4", height="5", fill="#000000"),
    ),
    # The lzma-compressed-tar item icon KDE draws for
    # `application/x-lzma-compressed-tar` items (the type-spelled icon
    # name of the installed shared MIME database's
    # `application/x-lzma-compressed-tar` type, whose `generic-icon`
    # is the shipped `package-x-generic`); one file covers exactly its
    # own name, and the drawing shares the sealed package box and holds
    # a capital L on the white body left of the grey tape stripe.
    os.path.join("32x32", "mimetypes", "application-x-lzma-compressed-tar.svg"): (
        *_SEALED_PACKAGE_32,
        _shape("rect", x="4", y="13", width="3", height="10", fill="#000000"),
        _shape("rect", x="7", y="21", width="8", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-lzma-compressed-tar.svg"): (
        *_SEALED_PACKAGE_16,
        _shape("rect", x="2", y="7", width="1", height="5", fill="#000000"),
        _shape("rect", x="3", y="11", width="4", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-lzma-compressed-tar.svg"): (
        *_SEALED_PACKAGE_22,
        _shape("rect", x="3", y="9", width="2", height="6", fill="#000000"),
        _shape("rect", x="5", y="14", width="5", height="1", fill="#000000"),
    ),
    # The cpio-archive item icon KDE draws for `application/x-cpio`
    # items (the type-spelled icon name of the installed shared MIME
    # database's `application/x-cpio` type, whose `generic-icon` is the
    # shipped `package-x-generic`); one file covers exactly its own
    # name (the database holds no alias spelling the icon name), and
    # the drawing shares the sealed package box and holds a capital
    # letter C on the white body left of the grey tape stripe.
    os.path.join("32x32", "mimetypes", "application-x-cpio.svg"): (
        _shape("rect", x="3", y="6", width="26", height="22", fill="#000000"),
        _shape("rect", x="4", y="7", width="24", height="3", fill="#DDDDDD"),
        _shape("rect", x="4", y="7", width="24", height="1", fill="#FFFFFF"),
        _shape("rect", x="4", y="10", width="24", height="17", fill="#FFFFFF"),
        _shape("rect", x="15", y="10", width="2", height="17", fill="#999999"),
        _shape("rect", x="5", y="13", width="8", height="2", fill="#000000"),
        _shape("rect", x="5", y="15", width="2", height="6", fill="#000000"),
        _shape("rect", x="5", y="21", width="8", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-x-cpio.svg"): (
        _shape("rect", x="1", y="3", width="14", height="11", fill="#000000"),
        _shape("rect", x="2", y="4", width="12", height="2", fill="#DDDDDD"),
        _shape("rect", x="2", y="4", width="12", height="1", fill="#FFFFFF"),
        _shape("rect", x="2", y="6", width="12", height="7", fill="#FFFFFF"),
        _shape("rect", x="7", y="6", width="2", height="7", fill="#999999"),
        _shape("rect", x="2", y="7", width="4", height="2", fill="#000000"),
        _shape("rect", x="2", y="9", width="2", height="2", fill="#000000"),
        _shape("rect", x="2", y="11", width="4", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-x-cpio.svg"): (
        _shape("rect", x="2", y="4", width="18", height="16", fill="#000000"),
        _shape("rect", x="3", y="5", width="16", height="2", fill="#DDDDDD"),
        _shape("rect", x="3", y="5", width="16", height="1", fill="#FFFFFF"),
        _shape("rect", x="3", y="7", width="16", height="12", fill="#FFFFFF"),
        _shape("rect", x="10", y="7", width="2", height="12", fill="#999999"),
        _shape("rect", x="3", y="9", width="6", height="2", fill="#000000"),
        _shape("rect", x="3", y="11", width="2", height="3", fill="#000000"),
        _shape("rect", x="3", y="14", width="6", height="2", fill="#000000"),
    ),
    # The ISO disc-image item icon KDE draws for `application/vnd.efi.iso`
    # items (the type-spelled icon name of the canonical `.iso` type,
    # whose `generic-icon` is the theme's own `media-optical` file and
    # whose exact name Breeze ships at every size): each size's tuple is
    # that size's `devices/media-optical` disc elements, in document
    # order, followed by the capital I's top bar, stem and bottom bar on
    # the grey face.
    os.path.join("32x32", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="16", cy="16", r="14", fill="#000000"),
        _shape("circle", cx="16", cy="16", r="13", fill="#DDDDDD"),
        _shape("path", d="M16 16 L8 6 L6 8 Z", fill="#FFFFFF"),
        _shape("path", d="M16 16 L24 26 L26 24 Z", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="5", fill="#999999"),
        _shape("circle", cx="16", cy="16", r="4", fill="#FFFFFF"),
        _shape("circle", cx="16", cy="16", r="2", fill="#000000"),
        _shape("rect", x="22", y="10", width="6", height="2", fill="#000000"),
        _shape("rect", x="25", y="12", width="2", height="6", fill="#000000"),
        _shape("rect", x="22", y="18", width="6", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="8", cy="8", r="7", fill="#000000"),
        _shape("circle", cx="8", cy="8", r="6", fill="#DDDDDD"),
        _shape("path", d="M8 8 L5 3 L3 5 Z", fill="#FFFFFF"),
        _shape("path", d="M8 8 L11 13 L13 11 Z", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="3", fill="#999999"),
        _shape("circle", cx="8", cy="8", r="2", fill="#FFFFFF"),
        _shape("circle", cx="8", cy="8", r="1", fill="#000000"),
        _shape("rect", x="11", y="5", width="3", height="2", fill="#000000"),
        _shape("rect", x="12", y="7", width="1", height="2", fill="#000000"),
        _shape("rect", x="11", y="9", width="3", height="2", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-vnd.efi.iso.svg"): (
        _shape("circle", cx="11", cy="11", r="10", fill="#000000"),
        _shape("circle", cx="11", cy="11", r="9", fill="#DDDDDD"),
        _shape("path", d="M11 11 L6 4 L4 6 Z", fill="#FFFFFF"),
        _shape("path", d="M11 11 L16 18 L18 16 Z", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="4", fill="#999999"),
        _shape("circle", cx="11", cy="11", r="3", fill="#FFFFFF"),
        _shape("circle", cx="11", cy="11", r="1", fill="#000000"),
        _shape("rect", x="15", y="7", width="4", height="2", fill="#000000"),
        _shape("rect", x="16", y="9", width="2", height="3", fill="#000000"),
        _shape("rect", x="15", y="12", width="4", height="2", fill="#000000"),
    ),
    # The JSON-document item icon KDE draws for `application/json` items
    # (the type-spelled icon name of the installed shared MIME database's
    # `application/json` type, whose `generic-icon` is the shipped
    # `text-x-script`); one file covers exactly its own name (the database
    # holds no alias spelling the icon name), and the drawing shares the
    # generic document's page and holds a pair of black curly braces.
    os.path.join("32x32", "mimetypes", "application-json.svg"): (
        *_PAGE_32,
        _shape("rect", x="12", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="8", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="10", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="12", y="19", width="2", height="2", fill="#000000"),
        _shape("rect", x="18", y="11", width="2", height="2", fill="#000000"),
        _shape("rect", x="20", y="13", width="2", height="2", fill="#000000"),
        _shape("rect", x="22", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="20", y="15", width="2", height="2", fill="#000000"),
        _shape("rect", x="20", y="17", width="2", height="2", fill="#000000"),
        _shape("rect", x="18", y="19", width="2", height="2", fill="#000000"),
    ),
    os.path.join("16x16", "mimetypes", "application-json.svg"): (
        *_PAGE_16,
        _shape("rect", x="6", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="4", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="5", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="6", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="6", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="7", width="1", height="1", fill="#000000"),
        _shape("rect", x="11", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="10", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="10", width="1", height="1", fill="#000000"),
    ),
    os.path.join("22x22", "mimetypes", "application-json.svg"): (
        *_PAGE_22,
        _shape("rect", x="9", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="7", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="8", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="9", y="14", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="8", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="9", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="10", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="11", width="1", height="1", fill="#000000"),
        _shape("rect", x="14", y="12", width="1", height="1", fill="#000000"),
        _shape("rect", x="13", y="13", width="1", height="1", fill="#000000"),
        _shape("rect", x="12", y="14", width="1", height="1", fill="#000000"),
    ),
    os.path.join("32x32", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="3", y="3", width="26", height="26", fill="#000000"),
        _shape("rect", x="4", y="4", width="24", height="24", fill="#DDDDDD"),
        _shape("rect", x="6", y="6", width="20", height="20", fill="#FFFFFF"),
        _shape("rect", x="21", y="9", width="3", height="3", fill="#999999"),
        _shape("rect", x="6", y="18", width="4", height="3", fill="#999999"),
        _shape("rect", x="10", y="16", width="4", height="5", fill="#999999"),
        _shape("rect", x="14", y="14", width="4", height="7", fill="#999999"),
        _shape("rect", x="18", y="16", width="4", height="5", fill="#999999"),
        _shape("rect", x="22", y="18", width="4", height="3", fill="#999999"),
        _shape("rect", x="6", y="21", width="20", height="5", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="1", y="1", width="14", height="14", fill="#000000"),
        _shape("rect", x="2", y="2", width="12", height="12", fill="#DDDDDD"),
        _shape("rect", x="3", y="3", width="10", height="10", fill="#FFFFFF"),
        _shape("rect", x="10", y="4", width="2", height="2", fill="#999999"),
        _shape("rect", x="3", y="8", width="2", height="2", fill="#999999"),
        _shape("rect", x="5", y="7", width="2", height="3", fill="#999999"),
        _shape("rect", x="7", y="6", width="2", height="4", fill="#999999"),
        _shape("rect", x="9", y="8", width="2", height="2", fill="#999999"),
        _shape("rect", x="3", y="10", width="10", height="3", fill="#999999"),
    ),
    os.path.join("22x22", "mimetypes", "image-x-generic.svg"): (
        _shape("rect", x="2", y="2", width="18", height="18", fill="#000000"),
        _shape("rect", x="3", y="3", width="16", height="16", fill="#DDDDDD"),
        _shape("rect", x="4", y="4", width="14", height="14", fill="#FFFFFF"),
        _shape("rect", x="15", y="6", width="2", height="2", fill="#999999"),
        _shape("rect", x="4", y="12", width="3", height="2", fill="#999999"),
        _shape("rect", x="7", y="10", width="3", height="4", fill="#999999"),
        _shape("rect", x="10", y="9", width="3", height="5", fill="#999999"),
        _shape("rect", x="13", y="11", width="3", height="3", fill="#999999"),
        _shape("rect", x="4", y="14", width="14", height="4", fill="#999999"),
    ),
    os.path.join("16x16", "mimetypes", "application-octet-stream.svg"): _PAGE_16,
    os.path.join("16x16", "mimetypes", "application-x-zerosize.svg"): _PAGE_16,
    os.path.join("16x16", "mimetypes", "unknown.svg"): _PAGE_16,
    os.path.join("22x22", "mimetypes", "application-octet-stream.svg"): _PAGE_22,
    os.path.join("22x22", "mimetypes", "application-x-zerosize.svg"): _PAGE_22,
    os.path.join("22x22", "mimetypes", "unknown.svg"): _PAGE_22,
    os.path.join("32x32", "mimetypes", "application-octet-stream.svg"): _PAGE_32,
    os.path.join("32x32", "mimetypes", "application-x-zerosize.svg"): _PAGE_32,
    os.path.join("32x32", "mimetypes", "unknown.svg"): _PAGE_32,
}

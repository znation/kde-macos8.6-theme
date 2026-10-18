"""Shared paths, QML probes and reference loader for the splash tests.

The splash artwork is authored on the 240x180 grid of the reference thumbnail
``macos8.6-screenshots/boot2_betawiki.png``. The QML probes read the literals
the artwork actually uses, so each test compares against the shipped value
instead of a second copy.
"""

from __future__ import annotations

import os
import re
import unittest

from reference_image import ReferenceScreenshotMixin
from theme_install import ROOT

LNF_ID = "org.macos8.desktop"
PACKAGE = os.path.join(ROOT, "theme", "look-and-feel", LNF_ID)
SPLASH = os.path.join(PACKAGE, "contents", "splash", "Splash.qml")
LOGO = os.path.join(PACKAGE, "contents", "splash", "images", "macos-logo.svg")
REFERENCE = os.path.join(
    ROOT, "macos8.6-screenshots", "boot2_betawiki.png"
)


def read_qml():
    """Return the splash QML source as one string."""
    with open(SPLASH, encoding="utf-8") as handle:
        return handle.read()


def _match_qml(text, pattern, message):
    """Return the first match of *pattern* in *text*, or fail naming *message*.

    The QML-literal and QML-object probes below read their value through one
    regex, so a pattern that no longer matches must fail with the file named
    rather than a bare ``AttributeError`` on ``None``; *message* says what was
    looked for.
    """
    match = re.search(pattern, text)
    if match is None:
        raise AssertionError(f"{SPLASH}: {message}")
    return match


def qml_int(name):
    """Return the integer literal of ``readonly property int <name>: N``.

    The QML declares every reference-grid coordinate this way, so the geometry
    test reads the same number the artwork uses instead of a second copy.
    """
    match = _match_qml(
        read_qml(),
        rf"readonly property int {re.escape(name)}:\s*(\d+)",
        f"no integer literal for {name}",
    )
    return int(match.group(1))


def qml_rect(name):
    """Return the QML ``(X, Y, Width, Height)`` integer literals for *name*.

    Each reference rectangle's four coordinates are ``readonly property int``
    literals sharing the ``<name>X/Y/Width/Height`` suffix pattern, so the
    geometry test compares the whole rectangle with one call.
    """
    return tuple(
        qml_int(f"{name}{part}") for part in ("X", "Y", "Width", "Height")
    )


def qml_color(name):
    """Return the uppercase ``#RRGGBB`` of ``readonly property color <name>``."""
    match = _match_qml(
        read_qml(),
        rf'readonly property color {re.escape(name)}:\s*'
        r'"(#[0-9A-Fa-f]{6})"',
        f"no colour literal for {name}",
    )
    return match.group(1).upper()


def qml_border_width():
    """Return the integer factor of the panel's ``border.width`` binding."""
    match = _match_qml(
        read_qml(),
        r"border\.width:\s*(\d+) \* root\.unit",
        "no integer border width",
    )
    return int(match.group(1))


def qml_unit_expression():
    """Return the whitespace-normalized expression bound to ``root.unit``.

    Every geometry binding multiplies a reference-grid literal by ``root.unit``,
    so the scale itself is as load-bearing as those bindings: the reference
    thumbnail is 240x180, and the ``Math.max(1, ...)`` floor keeps a window
    smaller than that grid from collapsing the splash to zero. The definition
    is one line today but may wrap, so collapse its whitespace before comparing
    it to the canonical expression.
    """
    match = _match_qml(
        read_qml(),
        r"readonly property int unit:[ \t]*(.+)",
        "no unit property definition",
    )
    return " ".join(match.group(1).split())


def object_source(qml, object_id):
    """Return the brace-balanced QML object whose ``id`` is ``object_id``.

    ``id`` is written just inside the object's opening brace, so the nearest
    preceding ``{`` opens that object and the matching ``}`` closes it. This
    lets the painting test assert a colour binding on the same object whose
    geometry binding the geometry test pins.
    """
    match = _match_qml(
        qml,
        rf"\bid:\s*{re.escape(object_id)}\b",
        f"no object with id {object_id}",
    )
    start = qml.rfind("{", 0, match.start())
    if start < 0:
        raise AssertionError(f"{SPLASH}: id {object_id} is not in an object")
    depth = 0
    for index in range(start, len(qml)):
        if qml[index] == "{":
            depth += 1
        elif qml[index] == "}":
            depth -= 1
            if depth == 0:
                return qml[start : index + 1]
    raise AssertionError(f"{SPLASH}: object {object_id} is not brace-balanced")


class SplashReferenceCase(ReferenceScreenshotMixin, unittest.TestCase):
    """Load the Git LFS reference once; skip the class when it is absent.

    ``make check`` must not require the LFS reference set (that is what
    ``make check-references`` is for), so a clone without the thumbnail skips
    the reference-derived tests instead of failing.
    """

    REFERENCE = REFERENCE

"""The shipped Ghostty theme file `theme/ghostty/.../Platinum` matches its sources.

`Platinum` is a Ghostty config file: `key = value` lines, one option each. The
base colors must equal `[Colors:View]` and `[Colors:Selection]` in
`MacOS8.colors`, and the font must equal `FIXED_VALUE` in `tools/apply_theme.py`.
Those sources are re-read here, so a drift in either one fails a pin. The
16-color palette has no reference screenshot and is pinned against the table
written below. The `ghostty` binary, when installed, must print the same values
back from `ghostty +show-config`.
"""

import configparser
import os
import shutil
import unittest

from support import process_runner
from support.colorscheme_fixtures import SCHEME
from support.repo_root import ROOT
from support.tmp_dir import make_tmp_dir
from tools.apply_theme import FIXED_VALUE

PLATINUM = os.path.join(
    ROOT, "theme", "ghostty", "org.macos8.desktop", "Platinum"
)

# Options a theme file may set. `theme` and `config-file` are absent by design:
# a theme that selects or includes another file would escape this one.
ALLOWED_KEYS = {
    "font-family",
    "font-style",
    "font-size",
    "background",
    "foreground",
    "cursor-color",
    "selection-background",
    "selection-foreground",
    "palette",
}

# Classic Platinum-era 16-color system table, ANSI slot -> color. Slots 12 and
# 14 repeat 4 and 6 because the table has no bright blue or bright cyan. Written
# here as the contract; the file must match it exactly.
PALETTE = {
    0: "#000000",
    1: "#dd0806",
    2: "#006411",
    3: "#562c05",
    4: "#0000d4",
    5: "#4600a5",
    6: "#02abea",
    7: "#c0c0c0",
    8: "#808080",
    9: "#ff6403",
    10: "#1fb714",
    11: "#fcf305",
    12: "#0000d4",
    13: "#f20884",
    14: "#02abea",
    15: "#ffffff",
}


def _read_pairs(path):
    """Return the `(key, value)` pairs of a Ghostty config file, in order."""
    pairs = []
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition(" = ")
            if not sep:
                raise AssertionError(f"not a 'key = value' line: {raw!r}")
            pairs.append((key, value))
    return pairs


def _read_platinum():
    """The shipped file as `(key -> value, palette index -> color)`."""
    options = {}
    palette = {}
    for key, value in _read_pairs(PLATINUM):
        if key == "palette":
            index, sep, color = value.partition("=")
            if not sep:
                raise AssertionError(f"palette value is not N=#rrggbb: {value!r}")
            palette.setdefault(int(index), []).append(color)
        else:
            options.setdefault(key, []).append(value)
    return options, palette


def _source_color(section, key):
    """`[section] key` from MacOS8.colors, formatted as `#rrggbb`."""
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    parser.read(SCHEME, encoding="utf-8")
    red, green, blue = (int(part) for part in parser[section][key].split(","))
    return f"#{red:02x}{green:02x}{blue:02x}"


def _single(options, key):
    values = options.get(key, [])
    if len(values) != 1:
        raise AssertionError(f"{key} must appear once, found {values!r}")
    return values[0]


class TestPlatinumColors(unittest.TestCase):
    """Each base color equals the MacOS8.colors role it is sourced from."""

    @classmethod
    def setUpClass(cls):
        cls.options, cls.palette = _read_platinum()

    def test_background_is_the_view_background(self):
        self.assertEqual(
            _single(self.options, "background"),
            _source_color("Colors:View", "BackgroundNormal"),
        )

    def test_foreground_is_the_view_foreground(self):
        self.assertEqual(
            _single(self.options, "foreground"),
            _source_color("Colors:View", "ForegroundNormal"),
        )

    def test_cursor_is_the_view_foreground(self):
        self.assertEqual(
            _single(self.options, "cursor-color"),
            _source_color("Colors:View", "ForegroundNormal"),
        )

    def test_selection_background_is_the_selection_background(self):
        self.assertEqual(
            _single(self.options, "selection-background"),
            _source_color("Colors:Selection", "BackgroundNormal"),
        )

    def test_selection_foreground_is_the_selection_foreground(self):
        self.assertEqual(
            _single(self.options, "selection-foreground"),
            _source_color("Colors:Selection", "ForegroundNormal"),
        )

    def test_selection_background_is_not_the_view_background(self):
        # The selection tint is the one value a swap could silently break:
        # the View background is white, the selection is the pale blue.
        self.assertNotEqual(
            _single(self.options, "selection-background"),
            _source_color("Colors:View", "BackgroundNormal"),
        )


class TestPlatinumFont(unittest.TestCase):
    """The font face, weight and size equal the approved FIXED_VALUE."""

    @classmethod
    def setUpClass(cls):
        cls.options, _ = _read_platinum()
        # FIXED_VALUE is `"Family,size,...,weight-name"`: family first, size
        # second, the named style last.
        fields = FIXED_VALUE.strip('"').split(",")
        cls.family, cls.size, cls.style = fields[0], fields[1], fields[-1]

    def test_family_is_the_fixed_face(self):
        self.assertEqual(_single(self.options, "font-family"), self.family)

    def test_size_is_the_fixed_point_size(self):
        self.assertEqual(_single(self.options, "font-size"), self.size)

    def test_style_is_the_fixed_weight_name(self):
        self.assertEqual(_single(self.options, "font-style"), self.style)


class TestPlatinumPalette(unittest.TestCase):
    """All sixteen ANSI slots carry the classic table, each exactly once."""

    @classmethod
    def setUpClass(cls):
        _, cls.palette = _read_platinum()

    def test_each_slot_zero_to_fifteen_appears_exactly_once(self):
        self.assertEqual(sorted(self.palette), list(range(16)))
        for index, colors in self.palette.items():
            self.assertEqual(len(colors), 1, index)

    def test_every_slot_matches_the_classic_table(self):
        for index, expected in PALETTE.items():
            self.assertEqual(self.palette[index], [expected], index)


class TestPlatinumKeys(unittest.TestCase):
    """Only the documented theme options appear; `theme` and `config-file` do not."""

    def test_every_key_is_an_allowed_option(self):
        keys = {key for key, _ in _read_pairs(PLATINUM)}
        self.assertLessEqual(keys, ALLOWED_KEYS)

    def test_theme_and_config_file_are_absent(self):
        keys = {key for key, _ in _read_pairs(PLATINUM)}
        self.assertNotIn("theme", keys)
        self.assertNotIn("config-file", keys)


class TestPlatinumThroughGhostty(unittest.TestCase):
    """`ghostty +show-config` prints the shipped values back (a CLI action, no window)."""

    def test_show_config_prints_the_shipped_values(self):
        if shutil.which("ghostty") is None:
            self.skipTest("the ghostty binary is not on PATH")
        home = make_tmp_dir(self)
        config_home = os.path.join(str(home), "config")
        os.makedirs(os.path.join(config_home, "ghostty"))
        with open(
            os.path.join(config_home, "ghostty", "config.ghostty"),
            "w",
            encoding="utf-8",
        ) as handle:
            handle.write(f"theme = {PLATINUM}\n")
        env = dict(os.environ, XDG_CONFIG_HOME=config_home, HOME=str(home))
        result = process_runner.run(
            ["ghostty", "+show-config"],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        printed = []
        for line in result.stdout.splitlines():
            key, sep, value = line.partition(" = ")
            if sep:
                printed.append((key, value))
        options, palette = _read_platinum()
        for key in (
            "background",
            "foreground",
            "font-family",
            "selection-background",
            "selection-foreground",
            "cursor-color",
        ):
            self.assertIn((key, _single(options, key)), printed, key)
        for index, color in sorted(palette.items()):
            self.assertIn(("palette", f"{index}={color[0]}"), printed, index)


if __name__ == "__main__":
    unittest.main()

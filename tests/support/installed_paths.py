"""The installed-tree layout `make install` writes under `$(DESTDIR)`.

Every artifact family lands at a fixed path below `$(DESTDIR)$(XDG_DATA_HOME)`:
the color scheme under `color-schemes/`, the Plasma packages under `plasma/`,
the Aurorae, wallpaper and icon themes in their own user-local directories,
the Lato font package under `fonts/`, and the Kvantum widget style under
`themes/<name>/Kvantum/`. The helpers
below name the paths the install tests share instead of re-deriving them, and
`staging_sibling`/`old_sibling` build the hidden siblings the Makefile's
atomic swap uses.

`support.theme_install` runs `make`; this module only computes where its
output goes.
"""

import os

# The data home inside each test's throwaway DESTDIR.
XDG_DATA_HOME = "/share"


def installed_plasma_dir(destdir, kind):
    """Directory `make install` writes a Plasma package family into.

    The Makefile installs under `$(DESTDIR)$(XDG_DATA_HOME)/plasma/<kind>`;
    `kind` is `look-and-feel` or `desktoptheme`. `installed_package` joins a
    package's own directory onto the result; `staging_sibling`/`old_sibling`
    build a hidden sibling of that directory.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "plasma", kind)


def installed_package(destdir, kind, package_id):
    """Directory `make install` writes one Plasma package into.

    The package family comes from `installed_plasma_dir`; the package's own
    directory is that family joined with its id (`org.macos8.desktop`).
    """
    return os.path.join(installed_plasma_dir(destdir, kind), package_id)


class InstalledPackageLocation:
    """Mixin: resolve a suite's installed package directory from its identity.

    A suite sets `KIND` (`look-and-feel` or `desktoptheme`) and `PACKAGE_ID`;
    `installed_parent` and `installed_package_dir` map them onto the paths
    `make install` writes. A suite whose package installs elsewhere (an Aurorae
    theme under `aurorae/themes`) overrides both methods together. It is a
    plain mixin, not a `TestCase`, so importing it does not collect an
    unconfigured base.
    """

    KIND = None
    PACKAGE_ID = None

    def installed_parent(self, tmp):
        """Directory holding this family's packages.

        Defaults to the `plasma/<kind>` family; a suite whose package installs
        elsewhere (an Aurorae theme under `aurorae/themes`) overrides it.
        """
        return installed_plasma_dir(tmp, self.KIND)

    def installed_package_dir(self, tmp):
        """This package's installed directory.

        Defaults to the `plasma/<kind>/<id>` path; a suite whose package
        installs elsewhere overrides it alongside `installed_parent`.
        """
        return installed_package(tmp, self.KIND, self.PACKAGE_ID)


def installed_aurorae_dir(destdir):
    """Directory `make install` writes the Aurorae window decoration into.

    The Makefile installs the decoration under
    `$(DESTDIR)$(XDG_DATA_HOME)/aurorae/themes`, the KWin sibling of the
    `plasma/` families; `installed_aurorae_theme` joins a theme's own
    directory onto the result.
    """
    return os.path.join(
        destdir, XDG_DATA_HOME.lstrip("/"), "aurorae", "themes"
    )


def installed_aurorae_theme(destdir, theme_id):
    """Directory `make install` writes one Aurorae theme into.

    The family comes from `installed_aurorae_dir`; the theme's own directory
    is that family joined with its id (`org.macos8.desktop`).
    """
    return os.path.join(installed_aurorae_dir(destdir), theme_id)


def installed_wallpaper_dir(destdir):
    """Directory `make install` writes the wallpaper package into.

    The Makefile installs it under `$(DESTDIR)$(XDG_DATA_HOME)/wallpapers`,
    the user-local directory Plasma's image wallpaper searches;
    `installed_wallpaper` joins a package's own directory onto the result.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "wallpapers")


def installed_wallpaper(destdir, package_id):
    """Directory `make install` writes one wallpaper package into."""
    return os.path.join(installed_wallpaper_dir(destdir), package_id)


def installed_icons_dir(destdir):
    """Directory `make install` writes the icon theme into.

    The Makefile installs it under `$(DESTDIR)$(XDG_DATA_HOME)/icons`, the
    user-local directory the icon-theme spec searches;
    `installed_icon_theme` joins a theme's own directory onto the result.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "icons")


def installed_icon_theme(destdir, theme_id):
    """Directory `make install` writes one icon theme into."""
    return os.path.join(installed_icons_dir(destdir), theme_id)


def installed_fonts_dir(destdir):
    """Directory `make install` writes the font package into.

    The Makefile installs it under `$(DESTDIR)$(XDG_DATA_HOME)/fonts`, the
    user-local directory fontconfig searches; `installed_font_package` joins
    a package's own directory onto the result.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "fonts")


def installed_font_package(destdir, package_id):
    """Directory `make install` writes one font package into."""
    return os.path.join(installed_fonts_dir(destdir), package_id)


def installed_color_scheme_dir(destdir):
    """Directory `make install` writes the color scheme into.

    The Makefile installs the scheme under
    `$(DESTDIR)$(XDG_DATA_HOME)/color-schemes`, the non-Plasma sibling of
    `installed_plasma_dir`'s families. `installed_color_scheme` joins a
    scheme's filename onto the result; `staging_sibling` builds its hidden
    sibling.
    """
    return os.path.join(destdir, XDG_DATA_HOME.lstrip("/"), "color-schemes")


def installed_color_scheme(destdir, name="MacOS8.colors"):
    """Path `make install` writes a color scheme file to.

    The directory comes from `installed_color_scheme_dir`; the file is that
    directory joined with the scheme's source basename (`MacOS8.colors` by
    default, or a renamed source passed as `COLOR_SCHEME`).
    """
    return os.path.join(installed_color_scheme_dir(destdir), name)


def staging_sibling(parent, name):
    """Hidden path `make install` copies `name` into before swapping it in.

    The Makefile stages the artifact as `parent/.<name>.staging` and renames it
    into place, so a test that simulates a killed install builds the same path.
    """
    return os.path.join(parent, "." + name + ".staging")


def old_sibling(parent, name):
    """Hidden path `make install` moves the working `name` aside to.

    The Makefile moves the artifact to `parent/.<name>.old` during the swap and
    removes it after the rename, so a killed install can leave it behind.
    """
    return os.path.join(parent, "." + name + ".old")

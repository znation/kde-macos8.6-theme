"""Run the repository's `make install` / `make uninstall` against a temp tree.

The installed artifacts land under `$(DESTDIR)$(XDG_DATA_HOME)`, so the install
tests in `test_colorscheme_install`, `test_lookandfeel` and `test_desktoptheme` pass a
throwaway `DESTDIR` and inspect the result there. Child processes go through
`process_runner`, which applies the suite's timeout and process-group cleanup.
"""

import os

import process_runner

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The data home inside each test's throwaway DESTDIR.
XDG_DATA_HOME = "/share"


def run_captured(argv, **kwargs):
    """Run `argv` under `run`, capturing its output as decoded text.

    A caller that reads the child's `stdout`/`stderr` as `str` gets
    `capture_output` and `text` defaulted here; the rest (`cwd`, `env`,
    `timeout`) is forwarded to `process_runner.run`.
    """
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    return process_runner.run(argv, **kwargs)


def run_make(args, env=None):
    """Run `make *args*` at the repository root under the suite's timeout runner.

    *args* is the target plus any variable assignments (`run_make(["install",
    "DESTDIR=..."])`); *env* replaces the environment for a test that drives
    `make -n` with a controlled one. The return is `process_runner.run`'s
    CompletedProcess, so a caller reads `returncode`, `stdout` and `stderr`.
    """
    return run_captured(
        ["make", *args],
        cwd=ROOT,
        env=env,
    )


def _run(target, destdir, extra=(), env=None):
    return run_make(
        [target, f"DESTDIR={destdir}", f"XDG_DATA_HOME={XDG_DATA_HOME}", *extra],
        env=env,
    )


def install(destdir, extra=(), env=None):
    """Run `make install` rooted at `destdir`; returns the CompletedProcess.

    `extra` appends make variable assignments (e.g. `COLOR_SCHEME=...`); `env`
    replaces the environment, for tests that shadow a tool on PATH.
    """
    return _run("install", destdir, extra, env)


def uninstall(destdir, extra=(), env=None):
    """Run `make uninstall` rooted at `destdir`; returns the CompletedProcess.

    `extra` and `env` are as for `install`.
    """
    return _run("uninstall", destdir, extra, env)


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


def assert_files_identical(case, source, target, msg=None):
    """Assert *target* exists and is byte-identical to *source*.

    *case* is the calling ``unittest.TestCase``; its assertions report the
    mismatch. *msg* labels the comparison, defaulting to *target*. The install
    tests use this to pin that a copy is byte-for-byte, not merely present.
    """
    case.assertTrue(os.path.isfile(target), target)
    with open(source, "rb") as original, open(target, "rb") as copy:
        case.assertEqual(original.read(), copy.read(), msg or target)


def shadow_command_env(destdir, name, script):
    """Write `script` as an executable `name` in `<destdir>/fakebin`.

    Returns an environment whose PATH finds the fake before the real command,
    so a test can make a system tool fail partway through `make install`.
    """
    bindir = os.path.join(destdir, "fakebin")
    os.makedirs(bindir, exist_ok=True)
    command = os.path.join(bindir, name)
    with open(command, "w", encoding="utf-8") as handle:
        handle.write(script)
    os.chmod(command, 0o755)
    env = dict(os.environ)
    env["PATH"] = bindir + os.pathsep + os.environ.get("PATH", "")
    return env

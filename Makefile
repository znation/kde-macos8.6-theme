PYTHON ?= python3
# The XDG Base Directory spec resolves $XDG_DATA_HOME to $HOME/.local/share when
# it is unset or empty, and treats a relative value as invalid and ignores it;
# README's Installing section documents the same default. `?=` alone would keep
# an empty environment value, so `make install` would target $(DESTDIR) itself
# (and, with no DESTDIR, run `install -d ""`). Fall back for an empty or
# relative value; an absolute environment value is kept. A command-line
# assignment (make install XDG_DATA_HOME=...) overrides this line as make
# always lets it, so it is used as given. XDG_DATA_HOME_ENV keeps the raw
# environment value so the guard below can tell an explicit absolute path from
# the fallback.
XDG_DATA_HOME_ENV := $(XDG_DATA_HOME)
# Export the raw value so the guard below can name it in its diagnostic. The
# recipe shell would otherwise see the make variable XDG_DATA_HOME, which the
# line below rewrites to the $HOME fallback for a relative or empty input.
export XDG_DATA_HOME_ENV
XDG_DATA_HOME := $(if $(filter /%,$(XDG_DATA_HOME_ENV)),$(XDG_DATA_HOME_ENV),$(HOME)/.local/share)

# The fallback needs an absolute $HOME: with XDG_DATA_HOME unset or relative
# and HOME also unset, $(HOME)/.local/share is /.local/share, so `make install`
# would write into the filesystem root (and `make uninstall` delete from it);
# with HOME relative the fallback is a path under the current directory. Refuse
# with a diagnostic instead of guessing. $(1) names the target. An absolute
# XDG_DATA_HOME -- including a command-line one -- resolves without $HOME and
# passes.
require_data_home = if [ -z "$(filter /%,$(XDG_DATA_HOME_ENV))" ] && [ -z "$(filter /%,$(HOME))" ]; then if [ -z "$(HOME)" ]; then echo "$(1): HOME is unset and XDG_DATA_HOME is not an absolute path ('$$XDG_DATA_HOME_ENV'); set XDG_DATA_HOME to an absolute path or export an absolute HOME" >&2; else echo "$(1): HOME is not an absolute path ('$$HOME') and XDG_DATA_HOME is not an absolute path ('$$XDG_DATA_HOME_ENV'); set XDG_DATA_HOME to an absolute path or export an absolute HOME" >&2; fi; exit 2; fi

# The data home doubles as the install/uninstall lock (see `install` below).
DATA_HOME := $(DESTDIR)$(XDG_DATA_HOME)

COLOR_SCHEME := theme/color-schemes/MacOS8.colors
# KDE derives the scheme id from the installed filename, so install under the
# source's own basename: renaming the scheme then moves the id with it instead
# of leaving a stale hardcoded name behind.
COLOR_SCHEME_NAME := $(notdir $(COLOR_SCHEME))
# The id KDE resolves a `[General] ColorScheme` value to: the installed
# basename up to the first dot (README's Installing section documents the same
# rule). `uninstall` uses it to detect a stored selection that still points at
# the scheme it just removed.
COLOR_SCHEME_ID := $(shell name='$(COLOR_SCHEME_NAME)'; printf '%s' "$${name%%.*}")
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

LNF_ID := org.macos8.desktop
LNF_PACKAGE := theme/look-and-feel/$(LNF_ID)
LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel

DTHEME_ID := org.macos8.desktop
DTHEME_PACKAGE := theme/desktoptheme/$(DTHEME_ID)
DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme

AURORAE_ID := org.macos8.desktop
AURORAE_PACKAGE := theme/aurorae/themes/$(AURORAE_ID)
AURORAE_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/aurorae/themes

WALLPAPER_ID := org.macos8.desktop
WALLPAPER_PACKAGE := theme/wallpapers/$(WALLPAPER_ID)
WALLPAPER_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/wallpapers

ICON_THEME_ID := org.macos8.desktop
ICON_THEME_PACKAGE := theme/icons/$(ICON_THEME_ID)
ICON_THEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/icons

FONT_ID := org.macos8.desktop
FONT_PACKAGE := theme/fonts/$(FONT_ID)
FONT_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/fonts

# Kvantum's user-local theme search path is
# `$XDG_DATA_HOME/themes/<name>/Kvantum/`, so a Kvantum theme installs as two
# files directly inside a `Kvantum/` directory rather than as a package
# directory; the package-directory swap `install_package` performs does not
# fit, so `_install` stages the two files individually instead.
KVANTUM_ID := org.macos8.desktop
KVANTUM_PACKAGE := theme/kvantum/$(KVANTUM_ID)
KVANTUM_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(KVANTUM_ID)/Kvantum

# GTK themes share the Kvantum theme directory: .../themes/org.macos8.desktop
GTK_ID := org.macos8.desktop
GTK_PACKAGE := theme/gtk/$(GTK_ID)
GTK_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/themes/$(GTK_ID)

# The artifacts `_install` copies, as families. A caller can narrow the install
# to the families it needs (`make install INSTALL_PACKAGES=look-and-feel`), so a
# test of one artifact does not copy all eight; the default installs the families
# INSTALL_PACKAGES names, and `gtk` is opt-in (not in the default). The color
# scheme is a family of its own even though it is one file. INSTALL_FAMILIES is
# the guard's vocabulary; the default below must name the same families, and the
# guard rejects a default that names one it does not know.
INSTALL_FAMILIES := color-scheme look-and-feel desktop-theme aurorae wallpaper icon-theme kvantum fonts gtk
INSTALL_PACKAGES ?= color-scheme look-and-feel desktop-theme aurorae wallpaper icon-theme kvantum fonts

# INSTALL_PACKAGES selects which artifact families `_install` copies. An empty
# value (`?=` keeps one from the environment) filters every family out, so the
# run creates the data home and exits 0 having copied nothing -- a green
# install that installed nothing. A value naming no known family (a typo,
# `colour-scheme`) does the same. Refuse either before the data home exists,
# with a diagnostic that names INSTALL_PACKAGES. $(1) names the target.
require_install_packages = set -f; set -- $(INSTALL_PACKAGES); if [ $$\# -eq 0 ]; then echo "$(1): INSTALL_PACKAGES must name at least one artifact family, not an empty or whitespace-only value: '$(INSTALL_PACKAGES)'" >&2; exit 2; fi; unknown=; for family in "$$@"; do case " $(INSTALL_FAMILIES) " in *" $$family "*) ;; *) unknown="$$unknown $$family";; esac; done; if [ -n "$$unknown" ]; then echo "$(1): INSTALL_PACKAGES names unknown artifact families:$$unknown; known families: $(INSTALL_FAMILIES)" >&2; exit 2; fi

# Stage a directory package as a sibling, then swap it in with a rename, so a
# copy that fails or is interrupted cannot leave a partial package installed or
# delete the working one. The old package is moved aside rather than deleted
# first: the swap is then a rename either way, and if the final rename fails the
# EXIT trap moves the old package back. A reinstall still replaces rather than
# merges, so files deleted from the package source do not stay behind as stale
# QML. A SIGKILL between the two renames cannot run the trap, leaving the
# package absent and its bytes in `.old`; the recovery below moves `.old` back
# before anything is removed, so the next install (or a copy that fails) leaves
# the last working package installed instead of deleting it. The shell also
# creates the parent directory, so a package costs one child process rather
# than a separate `install -d` plus this one. $(1) is the package id, $(2) its
# source directory, $(3) the install dir.
define install_package
	@staging="$(3)/.$(1).staging"; \
	old="$(3)/.$(1).old"; \
	final="$(3)/$(1)"; \
	trap 'rm -rf "$$staging"; if [ ! -e "$$final" ] && [ -e "$$old" ]; then mv "$$old" "$$final"; fi' EXIT; \
	install -d "$(3)" && \
	if [ ! -e "$(3)/$(1)" ] && [ -e "$$old" ]; then mv "$$old" "$(3)/$(1)"; fi && \
	rm -rf "$$staging" "$$old" && \
	cp -r "$(2)" "$$staging" && \
	if [ -e "$(3)/$(1)" ]; then mv "$(3)/$(1)" "$$old"; fi && \
	mv "$$staging" "$(3)/$(1)" && \
	rm -rf "$$old"
endef

.PHONY: help check install-gtk apply-gtk remove-gtk apply-cursor remove-cursor install-firefox remove-firefox check-references render apply install-local-hook uninstall-local-hook install uninstall _install _uninstall

# `check` runs the whole suite by default. A caller can narrow it to the test
# modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`,
# so a focused run does not need `python3 -m unittest discover -s tests ...`
# (the test modules import the `support` package, which needs `tests/` on
# `sys.path`; `discover` and the CHECK_TESTS path below both provide that).
CHECK_PATTERN ?= test*.py

# A caller who wants one test module, class or method rather than a whole-file
# glob sets CHECK_TESTS, e.g. `make check CHECK_TESTS=test_colorscheme.TestAnchors`
# or `make check CHECK_TESTS='test_a test_b.TestC'`. The named specs run from
# tests/ with the same interpreter, so the test modules' `support` imports
# resolve as they do under `discover`.
CHECK_TESTS ?=

# PYTHON is a make variable a caller can override (`make check
# PYTHON=python3.12`) or leave to the environment, but `?=` keeps an empty
# environment value. An empty value leaves the `check` recipe line starting
# with `-`, which make reads as its ignore-errors prefix: the command becomes
# `m -m unittest ...`, fails with status 127, and make exits 0 -- a green run
# that executed no tests. A value that is whitespace, or begins (after leading
# whitespace) with `-`, has the same effect, and no interpreter name begins
# with a dash. Refuse both first with a diagnostic that names PYTHON. $(1)
# names the target.
require_python = set -- "$(PYTHON)"; value="$$1"; while :; do case "$$value" in [[:space:]]*) value=$${value\#?};; *) break;; esac; done; case "$$value" in ''|-*) echo "$(1): PYTHON must name an interpreter, not an empty or option-like value: '$$1'" >&2; exit 2;; esac

# PYTHON must run an interpreter the project supports. Its fidelity tool uses
# int.bit_count(), added in Python 3.10, so an older interpreter fails deep in
# the suite with an AttributeError that names neither PYTHON nor the
# requirement. Probe the version once and refuse with a diagnostic naming both;
# the probe's stderr is discarded so a missing interpreter prints only this
# message. $(1) names the target.
require_python_version = $(PYTHON) -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 3)' 2>/dev/null || { echo "$(1): PYTHON must be Python 3.10 or newer (the fidelity tool uses int.bit_count()): '$(PYTHON)'" >&2; exit 2; }

# CHECK_TESTS names tests instead of discovering them, so a value beginning
# (after leading whitespace) with `-` would reach `unittest` as an option --
# `-x` aborts on the first failure and `-k` filters by pattern -- silently
# changing the run instead of naming a test. Refuse it with a diagnostic that
# names CHECK_TESTS. $(1) names the target.
require_check_tests = set -- "$(CHECK_TESTS)"; value="$$1"; while :; do case "$$value" in [[:space:]]*) value=$${value\#?};; *) break;; esac; done; case "$$value" in -*) echo "$(1): CHECK_TESTS must name test modules, classes or methods, not an option-like value: '$$1'" >&2; exit 2;; esac

# CHECK_PATTERN is the filename glob `check` hands to `unittest discover -p`,
# so an empty value (`?=` keeps one from the environment), a whitespace-only
# one, or a typo (`test_colorscheme*.pyx`) matches no test module and the run
# executes nothing. Interpreters before 3.12 then exit 0 -- a green run that
# ran no tests; 3.12 and newer exit 5 with only "NO TESTS RAN", naming neither
# the variable nor its value. Refuse all three with a diagnostic naming
# CHECK_PATTERN. Make strips leading whitespace from a command-line
# assignment before the recipe sees it, so `make check CHECK_PATTERN=' '`
# arrives empty; the guard recovers the caller's text from make's command
# line through /proc where available, so the diagnostic names the value the
# caller typed rather than an empty string. The guard and the recipe both use
# `$(strip ...)`, so the value checked is the value handed to `unittest`
# (surrounding whitespace would otherwise make it match no file). The pattern
# must match a `tests/test*.py` module, not merely a helper such as
# `tests/invariants.py`: discovery would import the helper and still run no
# tests. A leading dash is not rejected as an option-like value -- `-p`
# receives it as that option's argument -- but it matches no test module and
# so fails the same check. $(1) names the target.
require_check_pattern = set -- "$(CHECK_PATTERN)"; original="$$1"; value="$(strip $(CHECK_PATTERN))"; if [ -z "$$value" ] && [ -z "$$original" ] && [ -r "/proc/$$PPID/cmdline" ]; then original="$$(tr '\0' '\n' < "/proc/$$PPID/cmdline" | sed -n 's/^CHECK_PATTERN=//p' | tail -n 1)"; fi; case "$$value" in '') echo "$(1): CHECK_PATTERN must name a test-module glob, not an empty or whitespace-only value: '$$original'" >&2; exit 2;; esac; if [ -z "$$(find tests -type f -name "$$value" -name 'test*.py' | head -n 1)" ]; then echo "$(1): CHECK_PATTERN must match at least one test module (tests/test*.py): '$$original'" >&2; exit 2; fi

# The CHECK_TESTS recipe runs `cd tests` before it invokes the interpreter, so
# a relative PYTHON path (`PYTHON=./.venv/bin/python`) would resolve against
# tests/ and fail to start -- even though the discovery recipe, which runs
# from the repository root, works with it. Resolve a whitespace-free,
# path-shaped PYTHON against make's working directory first. A bare command
# name (`python3`) has no separator, so it is left for the shell's PATH lookup
# (independent of the recipe's directory); a value carrying arguments
# (`/usr/bin/python3 -X dev`) has whitespace, so it is left whole rather than
# split and rewritten by `abspath`.
PYTHON_RUN := $(if $(filter 1,$(words $(PYTHON))),$(if $(findstring /,$(PYTHON)),$(abspath $(PYTHON)),$(PYTHON)),$(PYTHON))

check:
	@$(call require_python,check)
	@$(call require_python_version,check)
	@$(call require_check_tests,check)
ifeq ($(strip $(CHECK_TESTS)),)
	@$(call require_check_pattern,check)
	$(PYTHON) -m unittest discover -s tests -v -p '$(strip $(CHECK_PATTERN))'
else
	cd tests && $(PYTHON_RUN) -m unittest -v $(CHECK_TESTS)
endif

# Print the contributor-facing targets and the variables that tune them, so
# the workflow is discoverable without reading this file's comments. `check`
# stays the default goal because it is defined above; the test suite reads the
# .PHONY line and pins that every public target appears here, so a target
# added without a help line fails `make check`.
help:
	@echo "Targets:"
	@echo "  help              show this message"
	@echo "  check             run the test suite"
	@echo "  check-references  validate the reference screenshot set (needs git lfs pull)"
	@echo "  render            render a themed Plasma surface headlessly to RENDER_OUTPUT"
	@echo "  apply             install and re-apply the theme to the running Plasma session"
	@echo "  install-local-hook  install a post-commit hook that runs 'make apply' (this clone only)"
	@echo "  uninstall-local-hook  remove that post-commit hook"
	@echo "  install           install the color scheme and theme packages"
	@echo "  install-gtk       install the opt-in GTK 3 and GTK 4 Platinum themes"
	@echo "  apply-gtk         install and select the opt-in GTK 3 and GTK 4 Platinum themes"
	@echo "  remove-gtk        clear the GTK 3 and GTK 4 Platinum theme selection"
	@echo "  apply-cursor      install the icon theme and select its Xcursor pointer set"
	@echo "  remove-cursor     remove our Xcursor link, leaving a foreign path and kcminputrc alone"
	@echo "  install-firefox   install the opt-in Firefox Platinum chrome into one profile"
	@echo "  remove-firefox    remove the Firefox Platinum chrome from one profile"
	@echo "  uninstall         remove the installed artifacts"
	@echo ""
	@echo "Variables (make VAR=value TARGET):"
	@echo "  CHECK_PATTERN=glob  test modules 'check' discovers (default test*.py)"
	@echo "  CHECK_TESTS=spec    test modules/classes/methods to run instead of discovering"
	@echo "  PYTHON=path         Python 3.10+ interpreter for every target that runs Python (default python3)"
	@echo "  RENDER_OUTPUT=path  PNG file 'render' writes (default render.png)"
	@echo "  XDG_DATA_HOME=path  absolute data home to install into (default under HOME)"
	@echo "  DESTDIR=path        staging prefix prepended to XDG_DATA_HOME"
	@echo "  FIREFOX_PROFILE=path  absolute Firefox profile for install-firefox/remove-firefox (default: active profile under \$$HOME/.mozilla/firefox)"
	@echo "  INSTALL_PACKAGES=list  artifact families 'install' copies (default color-scheme look-and-feel desktop-theme aurorae wallpaper icon-theme kvantum fonts)"
	@echo "  FLOCK_TIMEOUT=s     seconds to wait for the install lock (default 60)"

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	@$(call require_python,check-references)
	@$(call require_python_version,check-references)
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

# Opt-in: the render needs a Plasma 6 session's tools (kwin_wayland, spectacle,
# plasmawindowed), so it stays out of `check`. It installs into a scratch data
# home and leaves the user's configuration alone; tools/render_surface.py
# documents the steps and exits 2 when a tool is missing.
RENDER_OUTPUT ?= render.png

render:
	@$(call require_python,render)
	@$(call require_python_version,render)
	$(PYTHON) tools/render_surface.py -- "$(RENDER_OUTPUT)"

# Apply the just-built theme to the running Plasma session. `install` runs as a
# sub-make so this reuses its guards and lock. A non-empty DESTDIR is refused
# first: applying a staged tree to the running session is wrong.
# tools/apply_theme.py re-selects the global theme (without --resetLayout, so
# the user's panels survive), the color scheme and the desktop theme, selects
# the Kvantum widget theme when kvantummanager is available, then asks KWin to
# reconfigure. The startup splash changes only on the next login.
apply:
	@if [ -n "$(DESTDIR)" ]; then echo "apply: DESTDIR must be empty (applying a staged tree to the running Plasma session is wrong): '$(DESTDIR)'" >&2; exit 2; fi
	@$(call require_python,apply)
	@$(call require_python_version,apply)
	$(MAKE) --no-print-directory install
	$(PYTHON) tools/apply_theme.py

# Apply the opt-in GTK themes: install them as `install-gtk` does, then select
# them in the user's GTK 3 and GTK 4 settings and libadwaita user CSS. A
# non-empty DESTDIR is refused first for the same reason as `apply`.
apply-gtk:
	@if [ -n "$(DESTDIR)" ]; then echo "apply-gtk: DESTDIR must be empty (applying a staged tree to the running session is wrong): '$(DESTDIR)'" >&2; exit 2; fi
	@$(call require_python,apply-gtk)
	@$(call require_python_version,apply-gtk)
	$(MAKE) --no-print-directory install INSTALL_PACKAGES=gtk
	$(PYTHON) tools/apply_gtk.py

# Clear only the GTK selection this theme wrote; a foreign gtk-theme-name and
# a foreign gtk-4.0/gtk.css are left untouched.
remove-gtk:
	@$(call require_python,remove-gtk)
	@$(call require_python_version,remove-gtk)
	$(PYTHON) tools/apply_gtk.py --remove

# Apply the opt-in cursor: install the icon theme (which carries the Xcursor
# pointer set), expose it at ~/.icons/org.macos8.desktop -- the path Xcursor searches
# instead of $XDG_DATA_HOME/icons -- and select it with
# plasma-apply-cursortheme. A non-empty DESTDIR is refused for the same reason
# as `apply`: the selection is for the running session, not a staged tree.
apply-cursor:
	@if [ -n "$(DESTDIR)" ]; then echo "apply-cursor: DESTDIR must be empty (applying a staged tree to the running session is wrong): '$(DESTDIR)'" >&2; exit 2; fi
	@$(call require_python,apply-cursor)
	@$(call require_python_version,apply-cursor)
	$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme
	$(PYTHON) tools/apply_cursor.py

# Remove only our ~/.icons symlink; a foreign path and kcminputrc are left
# untouched (the tool notes the reset command when the selection still names
# our theme).
remove-cursor:
	@$(call require_python,remove-cursor)
	@$(call require_python_version,remove-cursor)
	$(PYTHON) tools/apply_cursor.py --remove

# Copy the standalone Firefox sheet into one profile's chrome/ directory and
# add the marker-delimited preference that makes Firefox read it. This is
# opt-in and installs nothing under XDG_DATA_HOME, so it needs no DESTDIR
# guard or data-home lock.
install-firefox:
	@$(call require_python,install-firefox)
	@$(call require_python_version,install-firefox)
	$(PYTHON) tools/install_firefox.py $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")

# Remove only the sheet and preference block this theme wrote; a foreign
# userChrome.css and a foreign user_pref are left untouched.
remove-firefox:
	@$(call require_python,remove-firefox)
	@$(call require_python_version,remove-firefox)
	$(PYTHON) tools/install_firefox.py --remove $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")

# Write a local-only post-commit hook (this clone's git hooks directory, never
# committed) so every commit re-runs `make apply`. tools/local_hook.py refuses
# to overwrite or remove a post-commit hook it did not write, so another tool's
# hook (Git LFS, for example) is left alone with a diagnostic.
install-local-hook:
	@$(call require_python,install-local-hook)
	@$(call require_python_version,install-local-hook)
	$(PYTHON) tools/local_hook.py install

uninstall-local-hook:
	@$(call require_python,uninstall-local-hook)
	@$(call require_python_version,uninstall-local-hook)
	$(PYTHON) tools/local_hook.py uninstall

# `install` and `uninstall` share fixed hidden `.staging`/`.old` names under
# the data home, so overlapping runs can clobber each other's staging, and an
# uninstall can delete an install's in-flight staging. Serialize them on an
# exclusive lock over the data home; flock releases the lock when the holder
# dies, so a SIGKILLed run cannot leave the lock stuck the way a lock
# directory would.
#
# The wait for that lock is bounded. A holder that stays alive -- stopped with
# SIGSTOP, or blocked in the kernel -- keeps the lock, so without a bound every
# later install/uninstall would wait forever. flock exits with
# FLOCK_CONFLICT_EXIT when the bounded wait expires, a status distinct from
# make's own error status, so the recipe can name the cause. FLOCK_TIMEOUT is a
# make variable so a caller can shorten it (the tests do) or lengthen it.
FLOCK_TIMEOUT ?= 60
FLOCK_CONFLICT_EXIT := 75

# FLOCK_TIMEOUT is a make variable a caller can override (`make install
# FLOCK_TIMEOUT=5`) or leave to the environment, but `flock -w` accepts only a
# non-negative whole number of seconds that fits its 64-bit signed timer. An
# empty value (`?=` keeps one from the environment), a typo like `60s`, or a
# value above 2**63 - 1 otherwise reaches flock and fails with its own
# "invalid timeout value" or "cannot set up timer" message that never names
# the variable -- after `install` has already created the data home. Refuse
# first with a diagnostic that names FLOCK_TIMEOUT. Leading zeros are stripped
# before the length check, so a valid value written with them is not refused as
# too large. The remaining digits are compared by length, then (at 19 digits)
# as text, where equal-length decimal strings sort by value, so the guard never
# asks the shell to do big-integer arithmetic. $(1) names the target.
require_flock_timeout = set -- "$(FLOCK_TIMEOUT)"; case "$$1" in ''|*[!0-9]*) echo "$(1): FLOCK_TIMEOUT must be a non-negative integer number of seconds: '$$1'" >&2; exit 2;; esac; digits="$$1"; while [ "$${\#digits}" -gt 1 ] && [ "$${digits\#0}" != "$$digits" ]; do digits="$${digits\#0}"; done; if [ "$${\#digits}" -gt 19 ] || { [ "$${\#digits}" -eq 19 ] && [ "$$digits" \> 9223372036854775807 ]; }; then echo "$(1): FLOCK_TIMEOUT must be a non-negative integer number of seconds at most 9223372036854775807 (flock's 64-bit timer limit): '$$1'" >&2; exit 2; fi

# Run the internal target $(1) under the data-home lock, naming $(2) when the
# bounded wait expires instead of letting the command's own failure be blamed.
run_locked = flock -w $(FLOCK_TIMEOUT) -E $(FLOCK_CONFLICT_EXIT) "$(DATA_HOME)" $(MAKE) --no-print-directory $(1) || { status=$$?; if [ $$status -eq $(FLOCK_CONFLICT_EXIT) ]; then echo "$(2): gave up after $(FLOCK_TIMEOUT)s waiting for the $(DATA_HOME) lock; another install or uninstall holds it" >&2; fi; exit $$status; }

# The guards, the data-home creation and the locked sub-make share one shell
# instead of one child per recipe line: `install` runs on every local-hook commit
# and dozens of times in the suite. A guard's `exit 2` and the lock's failure
# status still stop the recipe, and the guards still run before the data home is
# created. The lock command is braced so its `||` diagnostic binds to flock
# alone: an `install -d` failure that happens to share flock's conflict status
# must not be reported as a lock timeout.
install:
	@$(call require_data_home,install) && \
	$(call require_flock_timeout,install) && \
	$(call require_install_packages,install) && \
	install -d "$(DATA_HOME)" && \
	{ $(call run_locked,_install,install); }

# Stage the color scheme as a hidden sibling and rename it in, so a copy that
# fails or is interrupted cannot truncate the working installed scheme. The
# rename replaces atomically, and the EXIT trap removes the staging file on
# failure.
define install_color_scheme
	@staging="$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging"; \
	trap 'rm -f "$$staging"' EXIT; \
	install -Dm644 "$(COLOR_SCHEME)" "$$staging" && \
	mv "$$staging" "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"
endef

# Stage each Kvantum theme file as a hidden sibling and rename it in, as the
# color scheme does; the two files sit directly in the Kvantum/ directory, so
# the package-directory swap does not fit.
define install_kvantum
	@install -d "$(KVANTUM_INSTALL_DIR)" && \
	for name in $(KVANTUM_ID).kvconfig $(KVANTUM_ID).svg; do \
	  staging="$(KVANTUM_INSTALL_DIR)/.$$name.staging"; \
	  trap 'rm -f "$$staging"' EXIT; \
	  install -Dm644 "$(KVANTUM_PACKAGE)/$$name" "$$staging" && \
	  mv "$$staging" "$(KVANTUM_INSTALL_DIR)/$$name" || exit 1; \
	done
endef

define install_gtk
	@install -d "$(GTK_INSTALL_DIR)/gtk-3.0" "$(GTK_INSTALL_DIR)/gtk-4.0"; \
	trap 'rm -f "$(GTK_INSTALL_DIR)/.index.theme.staging" "$(GTK_INSTALL_DIR)/gtk-3.0/.gtk.css.staging" "$(GTK_INSTALL_DIR)/gtk-4.0/.gtk.css.staging"' EXIT; \
	install -Dm644 "$(GTK_PACKAGE)/index.theme" "$(GTK_INSTALL_DIR)/.index.theme.staging" && \
	mv "$(GTK_INSTALL_DIR)/.index.theme.staging" "$(GTK_INSTALL_DIR)/index.theme" && \
	install -Dm644 "$(GTK_PACKAGE)/gtk-3.0/gtk.css" "$(GTK_INSTALL_DIR)/gtk-3.0/.gtk.css.staging" && \
	mv "$(GTK_INSTALL_DIR)/gtk-3.0/.gtk.css.staging" "$(GTK_INSTALL_DIR)/gtk-3.0/gtk.css" && \
	install -Dm644 "$(GTK_PACKAGE)/gtk-4.0/gtk.css" "$(GTK_INSTALL_DIR)/gtk-4.0/.gtk.css.staging" && \
	mv "$(GTK_INSTALL_DIR)/gtk-4.0/.gtk.css.staging" "$(GTK_INSTALL_DIR)/gtk-4.0/gtk.css"
endef

_install:
	$(if $(filter color-scheme,$(INSTALL_PACKAGES)),$(call install_color_scheme))
	$(if $(filter look-and-feel,$(INSTALL_PACKAGES)),$(call install_package,$(LNF_ID),$(LNF_PACKAGE),$(LNF_INSTALL_DIR)))
	$(if $(filter desktop-theme,$(INSTALL_PACKAGES)),$(call install_package,$(DTHEME_ID),$(DTHEME_PACKAGE),$(DTHEME_INSTALL_DIR)))
	$(if $(filter aurorae,$(INSTALL_PACKAGES)),$(call install_package,$(AURORAE_ID),$(AURORAE_PACKAGE),$(AURORAE_INSTALL_DIR)))
	$(if $(filter wallpaper,$(INSTALL_PACKAGES)),$(call install_package,$(WALLPAPER_ID),$(WALLPAPER_PACKAGE),$(WALLPAPER_INSTALL_DIR)))
	$(if $(filter icon-theme,$(INSTALL_PACKAGES)),$(call install_package,$(ICON_THEME_ID),$(ICON_THEME_PACKAGE),$(ICON_THEME_INSTALL_DIR)))
	$(if $(filter kvantum,$(INSTALL_PACKAGES)),$(call install_kvantum))
	$(if $(filter fonts,$(INSTALL_PACKAGES)),$(call install_package,$(FONT_ID),$(FONT_PACKAGE),$(FONT_INSTALL_DIR)))
	$(if $(filter gtk,$(INSTALL_PACKAGES)),$(call install_gtk))

# Remove only the artifacts this theme installed -- including the opt-in GTK
# files, which the default `install` does not copy: the parent directories are
# shared (other color schemes,
# other look-and-feel/desktop-theme/Aurorae/wallpaper/icon/font packages, other
# Kvantum themes), so leave them and everything else in them alone. The hidden
# `.staging`/`.old` siblings are install's own temporary state: an install
# killed by SIGKILL cannot run its EXIT trap, so remove them here too instead
# of leaking them past uninstall. `rm -f`/`rm -rf` make a repeated run a no-op.
uninstall:
	@$(call require_data_home,uninstall) && \
	$(call require_flock_timeout,uninstall) && \
	install -d "$(DATA_HOME)" && \
	{ $(call run_locked,_uninstall,uninstall); }

# The removals share one shell (and one `set -e`) so a run spawns one child
# process instead of ten; each command keeps its own quoting and a failure
# still stops the recipe, as it did when make ran each line itself.
_uninstall:
	set -e; \
	rm -f "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)" "$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging"; \
	rm -rf "$(LNF_INSTALL_DIR)/$(LNF_ID)" "$(LNF_INSTALL_DIR)/.$(LNF_ID).staging" "$(LNF_INSTALL_DIR)/.$(LNF_ID).old"; \
	rm -rf "$(DTHEME_INSTALL_DIR)/$(DTHEME_ID)" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).staging" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).old"; \
	rm -rf "$(AURORAE_INSTALL_DIR)/$(AURORAE_ID)" "$(AURORAE_INSTALL_DIR)/.$(AURORAE_ID).staging" "$(AURORAE_INSTALL_DIR)/.$(AURORAE_ID).old"; \
	rm -rf "$(WALLPAPER_INSTALL_DIR)/$(WALLPAPER_ID)" "$(WALLPAPER_INSTALL_DIR)/.$(WALLPAPER_ID).staging" "$(WALLPAPER_INSTALL_DIR)/.$(WALLPAPER_ID).old"; \
	rm -rf "$(ICON_THEME_INSTALL_DIR)/$(ICON_THEME_ID)" "$(ICON_THEME_INSTALL_DIR)/.$(ICON_THEME_ID).staging" "$(ICON_THEME_INSTALL_DIR)/.$(ICON_THEME_ID).old"; \
	rm -rf "$(FONT_INSTALL_DIR)/$(FONT_ID)" "$(FONT_INSTALL_DIR)/.$(FONT_ID).staging" "$(FONT_INSTALL_DIR)/.$(FONT_ID).old"; \
	rm -f "$(KVANTUM_INSTALL_DIR)/$(KVANTUM_ID).kvconfig" "$(KVANTUM_INSTALL_DIR)/.$(KVANTUM_ID).kvconfig.staging" "$(KVANTUM_INSTALL_DIR)/$(KVANTUM_ID).svg" "$(KVANTUM_INSTALL_DIR)/.$(KVANTUM_ID).svg.staging"; \
	rm -f "$(GTK_INSTALL_DIR)/index.theme" "$(GTK_INSTALL_DIR)/.index.theme.staging" "$(GTK_INSTALL_DIR)/gtk-3.0/gtk.css" "$(GTK_INSTALL_DIR)/gtk-3.0/.gtk.css.staging" "$(GTK_INSTALL_DIR)/gtk-4.0/gtk.css" "$(GTK_INSTALL_DIR)/gtk-4.0/.gtk.css.staging"; \
	rmdir "$(GTK_INSTALL_DIR)/gtk-3.0" "$(GTK_INSTALL_DIR)/gtk-4.0" 2>/dev/null || true
# Removing the scheme does not touch the user's `[General] ColorScheme`
# selection. If it still names the scheme just removed, KDE cannot resolve the
# id and falls back to BreezeLight on every start without rewriting the stale
# key, so warn and name the reset command. Read `$XDG_CONFIG_HOME/kdeglobals`
# (default `$HOME/.config/kdeglobals`, ignoring an empty or relative
# XDG_CONFIG_HOME) the way KDE reads it: KDE strips a leading UTF-8 BOM,
# trims each line, and ignores a group header that never closes, so a
# BOM-prefixed or indented section header still opens its section while a
# following key stays in the section that was already open; keys are
# case-sensitive in the `[General]` section, where a key repeated in the
# section takes its last value. This is a diagnostic only -- it must not edit
# the file. The awk brackets the value it found, so a present but empty
# `ColorScheme=` (`[]`) is distinguishable from a missing key (no output);
# otherwise an empty id would match either.
	@config_home="$${XDG_CONFIG_HOME:-}"; \
	case "$$config_home" in /*) ;; *) config_home="";; esac; \
	if [ -z "$$config_home" ]; then case "$${HOME:-}" in /*) config_home="$$HOME/.config";; esac; fi; \
	kdeglobals="$$config_home/kdeglobals"; \
	if [ -n "$$config_home" ] && [ -f "$$kdeglobals" ]; then \
	  selected=$$(awk 'NR==1 { sub(/^\357\273\277/, "") } /^[[:space:]]*\[/ { if (index($$0, "]") == 0) next; section=$$0; sub(/^[[:space:]]*\[/,"",section); sub(/\].*$$/,"",section); next } section=="General" && $$0 ~ /^[[:space:]]*ColorScheme[[:space:]]*=/ { value=$$0; sub(/^[[:space:]]*ColorScheme[[:space:]]*=/,"",value); sub(/^[[:space:]]*/,"",value); sub(/[[:space:]]*$$/,"",value); found=1 } END { if (found) printf "[%s]", value }' "$$kdeglobals"); \
	  if [ "$$selected" = "[$(COLOR_SCHEME_ID)]" ]; then \
	    echo "uninstall: color scheme $(COLOR_SCHEME_ID) is still selected in $$kdeglobals after removal; if KDE cannot resolve it, it falls back to BreezeLight on the next start. Reset it with: plasma-apply-colorscheme BreezeLight" >&2; \
	  fi; \
	fi

install-gtk:
	@$(MAKE) --no-print-directory install INSTALL_PACKAGES=gtk

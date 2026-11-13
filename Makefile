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
# Command-line variables are exported by default. Defer HOME's export until
# after its raw value passes the parse-time guard below.
unexport HOME
XDG_DATA_HOME_ENV := $(value XDG_DATA_HOME)
HOME_ENV := $(value HOME)
# Export the raw value so the guard below can name it in its diagnostic. The
# recipe shell would otherwise see the make variable XDG_DATA_HOME, which the
# line below rewrites to the $HOME fallback for a relative or empty input.
export XDG_DATA_HOME_ENV
XDG_DATA_HOME := $(if $(filter /%,$(XDG_DATA_HOME_ENV)),$(XDG_DATA_HOME_ENV),$(HOME_ENV)/.local/share)

# DESTDIR takes the same route: the three apply targets below refuse a
# non-empty staging value and name it in their diagnostics. `$(DESTDIR)`
# expansion would paste the caller-chosen text into those recipes, where a
# quote inside it closes the recipe's own quotes and any following words run
# as shell commands instead of being refused. An environment-origin DESTDIR
# already reaches the recipe shells that way; exporting it here gives a
# command-line `make apply DESTDIR=...` the same safe route. Particularly,
# the unset case still leaves the variable unset in the recipe shell, so
# `[ -n "$$DESTDIR" ]` rejects empty-or-unset exactly as `$(DESTDIR)` did.
export DESTDIR

# The fallback needs an absolute $HOME: with XDG_DATA_HOME unset or relative
# and HOME also unset, $(HOME)/.local/share is /.local/share, so `make install`
# would write into the filesystem root (and `make uninstall` delete from it);
# with HOME relative the fallback is a path under the current directory. Refuse
# with a diagnostic instead of guessing. $(1) names the target. An absolute
# XDG_DATA_HOME -- including a command-line one -- resolves without $HOME and
# passes.
require_data_home = if [ -z "$(filter /%,$(XDG_DATA_HOME_ENV))" ] && [ -z "$(filter /%,$(HOME_ENV))" ]; then if [ -z "$(HOME_ENV)" ]; then echo "$(1): HOME is unset and XDG_DATA_HOME is not an absolute path ('$$XDG_DATA_HOME_ENV'); set XDG_DATA_HOME to an absolute path or export an absolute HOME" >&2; else echo "$(1): HOME is not an absolute path ('$$HOME') and XDG_DATA_HOME is not an absolute path ('$$XDG_DATA_HOME_ENV'); set XDG_DATA_HOME to an absolute path or export an absolute HOME" >&2; fi; exit 2; fi

# The data home doubles as the install/uninstall lock (see `install` below).
DATA_HOME := $(DESTDIR)$(XDG_DATA_HOME)

# DESTDIR, XDG_DATA_HOME, HOME, FLOCK_TIMEOUT and FIREFOX_PROFILE reach recipe
# shells pasted into double-quoted recipe words (`install -d "$(DATA_HOME)"`,
# the staging paths, the lock path, the lock timeout guard's
# `set -- "$(FLOCK_TIMEOUT)"`, install-firefox/remove-firefox's
# `--profile "$(FIREFOX_PROFILE)"`). Inside double quotes exactly four characters are
# shell syntax: a
# double quote closes the recipe's own quoting, and `$`, a backtick and a
# backslash open an expansion or an escape, so the words after any of them run
# as shell commands instead of naming a path. Refuse a value carrying one at
# make level, before any recipe of any target runs, and name the variable, the
# offending character and the value in the diagnostic. A space or an apostrophe
# is inert there and stays legal (TestWhitespaceInInstallPaths installs under
# `O'Brien's root`). A value that itself carries make's `$( )` is expanded by
# make while this guard reads it -- make's documented recursive-variable
# behaviour, outside the shell route this guard closes.
#
# A control byte is not shell syntax, but it is not inert either: the guard's
# own diagnostic pastes `<$(value)>` raw, and `require_flock_timeout` and
# `require_data_home` echo guarded values back at run time -- a byte like
# 0x1b, the terminal escape, reached the operator's terminal inside those
# words, where it mangles or forges the printed text instead of naming a
# value (the same terminal hazard tools/terminal.py's escape_controls guards
# against for the Python diagnostics; TestShellUnsafeControlCharacters pins
# the refusal). Refuse every C0 byte and DEL in a guarded value, before any
# branch of the guard is echoed; the refused value is not echoed back,
# because the diagnostic pastes values raw. Make word-splits a foreach list
# on blank characters, so five bytes -- tab (0x09), newline (0x0a), VT
# (0x0b), FF (0x0c) and CR (0x0d) -- drop out of the awk-generated list
# itself: VT, FF and CR are refused by explicit findstring tests against
# single-byte variables below, and tab and newline stay legal -- neither
# rewrites already-printed terminal text (a tab is inert spacing and a
# newline only starts a new line), and a metacharacter beside either is
# still refused above. The bytes are built by `awk` and `printf`, not
# written literally, so the Makefile text stays printable ASCII.
shell_unsafe_chars = \ " $$ `
make_dollar := $$
make_value = $(subst $(make_dollar)$(make_dollar),$(make_dollar),$(value $(1)))
shell_unsafe_in = $(strip $(foreach c,$(shell_unsafe_chars),$(findstring $(c),$(value $(1)))))
# The awk list leaves out the five blank bytes; tab and newline are the two
# legal residuals, and the three generated alone into scalar variables below
# are refused by the explicit tests in control_char_in -- a blank byte inside
# the foreach list would be word-split away, but findstring reads a scalar
# variable without splitting it. The blank-byte hits are concatenated OUTSIDE
# the strip: a lone CR, VT or FF hit is blank to make too, and strip would
# erase it, so only the non-blank hits are stripped.
# Immediate assignment: the awk program is deterministic, so one shell spawn
# per make invocation holds the value, and every later guard evaluation
# substitutes it instead of re-running awk.
control_chars := $(shell awk 'BEGIN { for (i = 1; i <= 31; i++) if (i != 9 && i != 10 && i != 11 && i != 12 && i != 13) printf "%c ", i; printf "%c ", 127 }')
vt_byte := $(shell printf '\013')
ff_byte := $(shell printf '\014')
cr_byte := $(shell printf '\015')
control_char_in = $(strip $(foreach c,$(control_chars),$(findstring $(c),$(value $(1)))))$(findstring $(vt_byte),$(value $(1)))$(findstring $(ff_byte),$(value $(1)))$(findstring $(cr_byte),$(value $(1)))
# The two refusal branches, control bytes first: the metacharacter branch's
# diagnostic echoes the value, so it only ever sees a value the control-byte
# branch has already cleared of terminal bytes. The check functions take the
# variable NAME (a single `$(call ...)` argument, so the value's own commas
# cannot split it away from the test) and read the value by indirection.
control_refusal = $(error $(subst XDG_DATA_HOME_ENV,XDG_DATA_HOME,$(1)) contains a control character -- a byte in the 0x01-0x1f or 0x7f range, e.g. an escape byte; it would reach a recipe or a diagnostic echo raw, where it mangles or forges the terminal text instead of naming a value; the value is not echoed back for the same reason; pass a printable path, timeout or scheme name)
metachar_refusal = $(error $(subst XDG_DATA_HOME_ENV,XDG_DATA_HOME,$(1)) contains a shell metacharacter ('$(call shell_unsafe_in,$(1))' in '$(call make_value,$(1))'); the value is expanded into double-quoted recipe words, where it would run as shell syntax instead of naming a path; pass a path without ", $$, a backtick or a backslash)
refuse_unsafe_value = $(if $(call control_char_in,$(1)),$(control_refusal),$(if $(call shell_unsafe_in,$(1)),$(metachar_refusal),))
# FLOCK_TIMEOUT is in the list before `FLOCK_TIMEOUT ?= 60` is read: the
# guard evaluates its default as still undefined (empty, harmless), while an
# environment or command-line value is already expanded and checked here.
# RENDER_OUTPUT ?= render.png sits further down with the `render` target for
# the same reason: its default is empty here, and `render` pastes the value
# into the double-quoted word `-- "$(RENDER_OUTPUT)"`. CHECK_PATTERN joins
# the list for the same reason: `check` pastes it into the double-quoted
# words `set -- "$(CHECK_PATTERN)"` and `find ... -name "$value"` in the
# guard that loads the suite. CHECK_PATTERN additionally reaches a
# single-quoted recipe word (`-p '$(CHECK_PATTERN)'`), so its apostrophe —
# inert inside double quotes, so this guard leaves it — is refused
# separately below, where the quoting it closes is different.
# THEME_ROOT := theme sits further down with the scheme source: install's
# symlink guard pastes the value into the double-quoted words of
# `require_theme_links`, where the same recipe-shell metacharacters run.
# CHECK_TESTS ?= and CHECK_PARALLEL ?= sit further down with the `check`
# target for the same reason: their run-time guards (`require_check_tests`,
# `require_check_parallel`) paste the value into the double-quoted words
# `set -- "$(CHECK_TESTS)"` and `set -- "$(CHECK_PARALLEL)"`, so a value
# carrying one of the four metacharacters rewrites the guard lines themselves
# and never reaches the guards' own alphabet refusals -- those keep refusing
# the wider punctuation (a semicolon, an apostrophe and the like are inert
# inside the guards' double quotes and refuse the value before it reaches
# the unquoted unittest or `--workers` positions), so only the four here
# need the parse-time refusal.
# COLOR_SCHEME_NAME joins the list for its override alone: the makefile
# derives it from COLOR_SCHEME (`export COLOR_SCHEME_NAME :=
# $(notdir $(COLOR_SCHEME))`, refused there by the TRANSITIVE value the
# guard reads), but a command-line or environment override bypasses that
# derivation -- a command-line definition is already set when this guard
# runs and otherwise survives the makefile's own `:=` -- and the name is
# expanded into double-quoted recipe words in install_color_scheme and
# _uninstall, namely `staging=".../.$(COLOR_SCHEME_NAME).staging"` and
# `mv "$staging" "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"`. The derived
# default is still undefined when this guard runs (it sits further down),
# so the guard only ever sees a caller's value; the makefile's own value
# is `COLOR_SCHEME`'s guarded text after `$(notdir)` cuts it, which can
# only re-arrange punctuation the guard already refused.
$(foreach v,DESTDIR XDG_DATA_HOME_ENV HOME FIREFOX_PROFILE FLOCK_TIMEOUT RENDER_OUTPUT COLOR_SCHEME COLOR_SCHEME_NAME COLOR_SCHEME_ID CHECK_PATTERN THEME_ROOT CHECK_TESTS CHECK_PARALLEL,$(call refuse_unsafe_value,$(v)))

export HOME := $(HOME_ENV)

# CHECK_PATTERN additionally reaches a single-quoted recipe word: `check`
# pastes it into `-p '$(CHECK_PATTERN)'`, and an apostrophe — inert inside
# double quotes, so the guard above leaves it — closes that quoting instead.
# The suite's own test-module filenames contain none, so the `check` recipe
# never needs it either; a value reaching this diagnostic has already
# passed the metacharacter refusal in the guard above.
$(if $(findstring ',$(CHECK_PATTERN)),$(error CHECK_PATTERN contains an apostrophe ('$(CHECK_PATTERN)'); the value is expanded into the single-quoted `-p '$(CHECK_PATTERN)'` recipe word, where the apostrophe would close the quoting and run the words after it as shell syntax instead of naming a test-module glob; pass a glob without an apostrophe),)

# XDG_CONFIG_HOME is never expanded into a recipe word: the uninstall recipe
# reads it through the shell (`config_home="$${XDG_CONFIG_HOME:-}"`) and,
# when a selection still names our GTK theme after the data-home removals,
# echoes the settings.ini and gtk.css paths under it on stderr. Make
# interpolates nothing of the value, so the metacharacter refusal above
# could see it only through make's non-existent expansion -- but the echo
# pastes whatever the value carries raw into the terminal, exactly like the
# guard echoes the other guarded values. A value carrying a control byte is
# hence refused at parse time, before any recipe runs, and is not echoed
# back. A printable value, spaces and apostrophes alike, stays legal.
$(if $(call control_char_in,XDG_CONFIG_HOME),$(call control_refusal,XDG_CONFIG_HOME))

# PYTHON is expanded into recipe words unquoted -- a value may carry
# arguments (`/usr/bin/python3 -X dev`), so the words cannot be
# double-quoted -- and at an unquoted position a wider set of characters is
# shell syntax than inside double quotes: an apostrophe, a semicolon, a
# pipe, an ampersand, a parenthesis, a redirection character or a newline
# would run the words after it as shell syntax instead of naming an
# interpreter. Refuse such a value at make level like the path variables
# above, naming the variable, the offending character and the value. A
# space stays legal because the multi-word form is the documented one
# (`PYTHON_RUN` below). `PYTHON ?= python3` sits at the top of the file, so
# the guard here sees the default, an environment value and a command-line
# value alike. A lone parenthesis cannot sit in the character list of a
# `$(foreach ...)` call unescaped, so the two come from variables; the
# newline cannot be written literally in an assignment, so it comes from
# `define` and is reported as the word `newline`.
open_paren := (
close_paren := )
define newline


endef
py_extra_unsafe_chars = ' ; | & < > $(open_paren) $(close_paren)
# py_unsafe_in takes the variable NAME like the other checks, because
# shell_unsafe_in reads its value by indirection. Check control bytes first:
# the metacharacter diagnostic echoes PYTHON raw, so it must only handle
# printable values.
py_unsafe_in = $(strip $(call shell_unsafe_in,$(1)) $(foreach c,$(py_extra_unsafe_chars),$(findstring $(c),$(value $(1)))) $(if $(findstring $(newline),$(value $(1))),newline))
$(if $(call control_char_in,PYTHON),$(call control_refusal,PYTHON))
$(if $(call py_unsafe_in,PYTHON),$(error PYTHON contains a shell metacharacter ('$(call py_unsafe_in,PYTHON)' in '<$(call make_value,PYTHON)>'); the value is expanded unquoted into recipe words, where it would run as shell syntax instead of naming an interpreter; pass an interpreter command without an apostrophe, semicolon, pipe, ampersand, parenthesis, redirection character, newline, backtick, dollar sign, backslash or double quote),)

# The theme tree `make install` copies from. A test overrides it on the command
# line to point the symlink guard below at a scratch package tree; the override
# reaches double-quoted recipe words in `require_theme_links`, so it must carry
# no recipe-shell metacharacter (the parse-level guard above refuses one).
THEME_ROOT := theme

# INSTALL_PACKAGES is expanded unquoted into `require_install_packages`'
# shell words (`set -- $(INSTALL_PACKAGES)`), and PYTHON's refusal above
# shows the consequence an unquoted position has: an apostrophe, semicolon,
# pipe, ampersand, parenthesis, redirection character or newline runs the
# words after it as shell syntax. The family-membership check would refuse
# any word such a payload leaves behind, but that check runs in the recipe
# shell the payload has already escaped, so this refusal names the
# variable, the offending character and the value at make level, before the
# value is expanded into any recipe. A space stays legal because the value
# is a list of family names. `INSTALL_PACKAGES ?=` sits below, so the
# default (`color-scheme ... fonts`) is not yet defined when this guard
# runs and only a caller's value is checked.
$(if $(call control_char_in,INSTALL_PACKAGES),$(call control_refusal,INSTALL_PACKAGES))
$(if $(call py_unsafe_in,INSTALL_PACKAGES),$(error INSTALL_PACKAGES contains a shell metacharacter ('$(call py_unsafe_in,INSTALL_PACKAGES)' in '$(call make_value,INSTALL_PACKAGES)'); the value is expanded unquoted into the packaging guard's recipe words, where it would run as shell syntax instead of naming artifact families; pass a list of family names without an apostrophe, semicolon, pipe, ampersand, parenthesis, redirection character, newline, backtick, dollar sign, backslash or double quote),)

# The scheme source. A command-line override renames what `install` reads, so
# `COLOR_SCHEME` reaches double-quoted recipe words below and must carry no
# recipe-shell metacharacter.
COLOR_SCHEME := theme/color-schemes/MacOS8.colors
# KDE derives the scheme id from the installed filename, so install under the
# source's own basename: renaming the scheme then moves the id with it instead
# of leaving a stale hardcoded name behind.
export COLOR_SCHEME_NAME := $(notdir $(COLOR_SCHEME))
# The id KDE resolves a `[General] ColorScheme` value to: the installed
# basename up to the first dot (README's Installing section documents the same
# rule). `uninstall` uses it to detect a stored selection that still points at
# the scheme it just removed. The derivation runs a shell, so the name travels
# through the environment -- make exports the variable to `$(shell)`, too --
# instead of being interpolated into a quoted shell word the value itself
# could escape with a stray apostrophe; the shell word stays a constant.
COLOR_SCHEME_ID := $(shell name="$$COLOR_SCHEME_NAME"; printf '%s' "$${name%%.*}")
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

LNF_ID := org.macos8.desktop
LNF_PACKAGE := theme/look-and-feel/$(LNF_ID)
LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel

# Keep DTHEME_ID in step with tools/apply_theme.py::DTHEME_ID, the desktop
# theme id `make apply` selects with `plasma-apply-desktoptheme`; see the
# uninstall diagnostics below.
DTHEME_ID := org.macos8.desktop
DTHEME_PACKAGE := theme/desktoptheme/$(DTHEME_ID)
DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme

AURORAE_ID := org.macos8.desktop
AURORAE_PACKAGE := theme/aurorae/themes/$(AURORAE_ID)
AURORAE_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/aurorae/themes

# The KWin decoration QML package is the window decoration the shipped
# look-and-feel defaults select: their `[kwinrc][org.kde.kdecoration2]`
# pair `library=org.kde.kwin.aurorae`, `theme=org.macos8.desktop` matches
# this KPackage under `kwin/decorations/` by `KPlugin.Id`; it installs
# beside the aurorae family in the same data home so the package's own QML
# can walk to the aurorae art.
# Family `kwin-decoration`.
KWINDEC_ID := org.macos8.desktop
KWINDEC_PACKAGE := theme/kwin-decoration/$(KWINDEC_ID)
KWINDEC_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/kwin/decorations

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

# The files `make install` copies from the GTK package directory into the
# install dir, relative to both, in the order the GTK staging and rename
# phases copy them. This one list drives the staging loop, the rename loop,
# the staging-cleanup trap and the uninstall removals together
# (gtk_stage_loop and its siblings below), so a file added here cannot miss
# one of those four spellings. Each staged copy is a hidden
# `.<basename>.staging` sibling inside the file's own directory.
GTK_FILES := index.theme \
	gtk-3.0/gtk.css \
	gtk-4.0/gtk.css \
	assets/checkmark.svg \
	assets/bullet.svg \
	assets/check-mixed.svg \
	assets/arrow-down.svg \
	assets/arrow-up.svg \
	assets/arrow-right.svg \
	assets/submenu-arrow.svg \
	assets/window-close.svg \
	assets/window-maximize.svg \
	assets/window-minimize.svg

# The marker comment `tools/gtk_selection.py` publishes as the first line of
# `$XDG_CONFIG_HOME/gtk-4.0/gtk.css`; uninstall's dangling-selection diagnostic
# recognizes a published GTK user CSS by that literal comment.
GTK_USER_CSS_MARKER := /* org.macos8.desktop GTK 4 user CSS */

# The artifacts `_install` copies, as families. A caller can narrow the install
# to the families it needs (`make install INSTALL_PACKAGES=look-and-feel`), so a
# test of one artifact does not copy every other family; the default installs
# every family, GTK included. The color scheme is a family of its own even
# though it is one file. INSTALL_FAMILIES is the guard's vocabulary; the default
# below must name the same families, and the guard rejects a default that names
# one it does not know.
INSTALL_FAMILIES := color-scheme look-and-feel desktop-theme aurorae kwin-decoration wallpaper icon-theme kvantum fonts gtk
INSTALL_PACKAGES ?= color-scheme look-and-feel desktop-theme aurorae kwin-decoration wallpaper icon-theme kvantum fonts gtk

# INSTALL_PACKAGES selects which artifact families `_install` copies. An empty
# value (`?=` keeps one from the environment) filters every family out, so the
# run creates the data home and exits 0 having copied nothing -- a green
# install that installed nothing. A value naming no known family (a typo,
# `colour-scheme`) does the same. Refuse either before the data home exists,
# with a diagnostic that names INSTALL_PACKAGES. $(1) names the target.
require_install_packages = set -f; set -- $(INSTALL_PACKAGES); if [ $$\# -eq 0 ]; then echo "$(1): INSTALL_PACKAGES must name at least one artifact family, not an empty or whitespace-only value: '$(INSTALL_PACKAGES)'" >&2; exit 2; fi; unknown=; for family in "$$@"; do case " $(INSTALL_FAMILIES) " in *" $$family "*) ;; *) unknown="$$unknown $$family";; esac; done; if [ -n "$$unknown" ]; then echo "$(1): INSTALL_PACKAGES names unknown artifact families:$$unknown; known families: $(INSTALL_FAMILIES)" >&2; exit 2; fi

# The theme packages are contributor-supplied, and git stores symlinks. The
# single-file installs use `install`, which follows a source symlink, so one at
# the color scheme, a Kvantum file or a GTK file would copy a private file's
# bytes or stream a device into the installed theme. The directory installs use
# `cp -r`, which preserves a link and puts it in the user's data home, where a
# later reader follows it. Refuse any symlink under the theme tree before the
# data home is created. `find` does not follow links, so it lists one without
# reading its target; the diagnostic names neither the link nor its target, so
# a contributor-supplied name cannot drive the terminal. $(1) names the target.
require_theme_links = if [ -L "$(THEME_ROOT)" ] || [ -n "$$(find "$(THEME_ROOT)" -type l -print -quit 2>/dev/null)" ]; then echo "$(1): refusing a symlink in the theme package tree; theme packages must ship regular files, not links" >&2; exit 2; fi

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

.PHONY: help check install-gtk apply-gtk apply-plasma remove-gtk apply-cursor remove-cursor install-firefox remove-firefox remove-kvantum check-references render apply install-local-hook uninstall-local-hook install uninstall _install _uninstall

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

# Without a value (the default) the discovery run goes through the parallel
# coordinator `tools/check_parallel.py`: each matched module becomes one
# worker process, `python -m unittest -v <module>` from tests/ with the same
# interpreter as every other `check` path, and a bounded number of workers
# run at a time (one per core by default, bounded by the module count). A
# value of `0` restores the serial `unittest discover` run, and a positive
# integer bounds the worker count. The guard refuses a value that is neither,
# with a diagnostic naming CHECK_PARALLEL; the same empty/whitespace handling
# as the other guards keeps an environment value's leading whitespace from
# turning `0 ` into a refusal.
CHECK_PARALLEL ?=

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

# Targets that execute Python share both guards and target-specific diagnostics.
require_python_ready = $(call require_python,$(1)) && $(call require_python_version,$(1))

# The three apply targets (`apply`, `apply-gtk`, `apply-cursor`) share
# one refusal line: each acts on the running session, and a DESTDIR
# staged-tree has no business there. One snippet keeps the three refusals in
# lockstep -- wording, exit status, echoed value -- the way require_python
# shares its guard. $(1) names the target.
refuse_destdir = if [ -n "$$DESTDIR" ]; then echo "$(1): DESTDIR must be empty (applying a staged tree to the running session is wrong): '$$DESTDIR'" >&2; exit 2; fi

# CHECK_TESTS names tests instead of discovering them, so a value beginning
# (after leading whitespace) with `-` would reach `unittest` as an option --
# `-x` aborts on the first failure and `-k` filters by pattern -- silently
# changing the run instead of naming a test. Refuse it with a diagnostic that
# names CHECK_TESTS. Each spec's module component -- the text before its
# first `.` -- must name a tests/<module>.py file, since unittest imports
# that module before it resolves the class and method parts: a typo'd module
# name (`CHECK_TESTS=test_byteop.TestX`) would otherwise fail deep inside
# unittest with a ModuleNotFoundError traceback that names neither CHECK_TESTS
# nor the typo'd value, while CHECK_PATTERN's equally typo'd glob is already
# refused by require_check_pattern. List every unknown spec, quoting none of
# the known ones, so the diagnostic names exactly what is wrong. $(1) names
# the target. Specs are Python dotted names separated by whitespace; validate
# that alphabet before the value reaches its unquoted unittest recipe position.
require_check_tests = set -- "$(CHECK_TESTS)"; value="$$1"; while :; do case "$$value" in [[:space:]]*) value=$${value\#?};; *) break;; esac; done; case "$$value" in -*) echo "$(1): CHECK_TESTS must name test modules, classes or methods, not an option-like value: '$$1'" >&2; exit 2;; esac; case "$$value" in *[!a-zA-Z0-9_.[:space:]]*) echo "$(1): CHECK_TESTS may contain only dotted test names and whitespace: '$$1'" >&2; exit 2;; esac; unknown=; for spec in $$value; do module=$${spec%%.*}; if [ ! -f "tests/$$module.py" ]; then unknown="$$unknown $$spec"; fi; done; if [ -n "$$unknown" ]; then echo "$(1): CHECK_TESTS must name test modules in tests/, but these specs name no tests/<module>.py file:$$unknown" >&2; exit 2; fi

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
# `tests/support/invariants.py`: discovery would import the helper and still run no
# tests. A leading dash is not rejected as an option-like value -- `-p`
# receives it as that option's argument -- but it matches no test module and
# so fails the same check. $(1) names the target.
require_check_pattern = set -- "$(CHECK_PATTERN)"; original="$$1"; value="$(strip $(CHECK_PATTERN))"; if [ -z "$$value" ] && [ -z "$$original" ] && [ -r "/proc/$$PPID/cmdline" ]; then original="$$(tr '\0' '\n' < "/proc/$$PPID/cmdline" | sed -n 's/^CHECK_PATTERN=//p' | tail -n 1)"; fi; case "$$value" in '') echo "$(1): CHECK_PATTERN must name a test-module glob, not an empty or whitespace-only value: '$$original'" >&2; exit 2;; esac; if [ -z "$$(find tests -type f -name "$$value" -name 'test*.py' | head -n 1)" ]; then echo "$(1): CHECK_PATTERN must match at least one test module (tests/test*.py): '$$original'" >&2; exit 2; fi

# CHECK_PARALLEL tunes only how the discovered modules run: an empty value
# (the default, also from the environment) means one worker per core, `0`
# means the serial `unittest discover` path, and a positive integer bounds
# the worker count. Anything else -- a negative number, a spelled-out value,
# trailing text -- names no worker count and would reach the coordinator's
# own type check as argparse's exit-2 usage error, which names the option but
# not the variable that filled it. Refuse such a value here, naming
# CHECK_PARALLEL, before the run starts. $(1) names the target.
require_check_parallel = set -- "$(CHECK_PARALLEL)"; value="$$1"; while :; do case "$$value" in [[:space:]]*) value=$${value\#?};; *) break;; esac; done; case "$$value" in ''|0) ;; *[!0-9]*) echo "$(1): CHECK_PARALLEL must be a worker count (a nonnegative integer; 0 runs the suite serially): '$$1'" >&2; exit 2;; esac

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
	@$(call require_python_ready,check)
	@$(call require_check_tests,check)
ifeq ($(strip $(CHECK_TESTS)),)
	@$(call require_check_pattern,check)
	@$(call require_check_parallel,check)
ifneq ($(strip $(CHECK_PARALLEL)),0)
	$(PYTHON) tools/check_parallel.py -p '$(strip $(CHECK_PATTERN))'$(if $(strip $(CHECK_PARALLEL)), --workers $(strip $(CHECK_PARALLEL)),)
else
	$(PYTHON) -m unittest discover -s tests -v -p '$(strip $(CHECK_PATTERN))'
endif
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
	@echo "  apply             install and apply the theme to the running session"
	@echo "  apply-plasma      reselect only the installed Platinum Plasma settings"
	@echo "  install-local-hook  install a post-commit hook that runs 'make apply' (this clone only)"
	@echo "  uninstall-local-hook  remove that post-commit hook"
	@echo "  install           install every artifact family, GTK included"
	@echo "  install-gtk       install only the GTK 3 and GTK 4 Platinum themes"
	@echo "  apply-gtk         install and select only the GTK 3 and GTK 4 Platinum themes"
	@echo "  remove-gtk        clear the GTK 3 and GTK 4 Platinum theme selection"
	@echo "  remove-kvantum    clear the Kvantum widget-theme selection make apply published"
	@echo "  apply-cursor      install the icon theme and select its Xcursor pointer set"
	@echo "  remove-cursor     remove our Xcursor link, leaving a foreign path and kcminputrc alone"
	@echo "  install-firefox   install the Firefox Platinum userChrome.css and userContent.css into one profile"
	@echo "  remove-firefox    remove the Firefox Platinum userChrome.css and userContent.css from one profile"
	@echo "  uninstall         remove the installed artifacts"
	@echo ""
	@echo "Variables (make VAR=value TARGET):"
	@echo "  CHECK_PATTERN=glob  test modules 'check' discovers (default test*.py)"
	@echo "  CHECK_TESTS=spec    test modules/classes/methods to run instead of discovering"
	@echo "  CHECK_PARALLEL=n    parallel worker count for check (default: one per core); 0 runs the modules serially"
	@echo "  PYTHON=path         Python 3.10+ interpreter for every target that runs Python (default python3)"
	@echo "  RENDER_OUTPUT=path  PNG file 'render' writes (default render.png)"
	@echo "  RENDER_MODE=name   render surface: $(RENDER_MODE_LIST) (default calculator)"
	@echo "  XDG_DATA_HOME=path  absolute data home to install into (default under HOME)"
	@echo "  DESTDIR=path        staging prefix prepended to XDG_DATA_HOME"
	@echo "  FIREFOX_PROFILE=path  absolute Firefox profile for apply/install-firefox/remove-firefox (default: active profile under \$$HOME/.mozilla/firefox)"
	@echo "  INSTALL_PACKAGES=list  artifact families 'install' copies (default color-scheme look-and-feel desktop-theme aurorae kwin-decoration wallpaper icon-theme kvantum fonts gtk)"
	@echo "  FLOCK_TIMEOUT=s     seconds to wait for the install lock (default 60)"
	@echo ""
	@echo "Reference tools (run from the repository root):"
	@echo "  python3 tools/sample.py IMAGE X Y          sample reference PNG pixels"
	@echo "  python3 tools/fidelity.py CANDIDATE REFERENCE  compare rendered and reference PNGs"
	@echo "  Append --help to either command for options."

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	@$(call require_python_ready,check-references)
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

# Opt-in: the render needs a Plasma 6 session's tools (kwin_wayland, spectacle,
# plasmawindowed), so it stays out of `check`. It installs into a scratch data
# home and leaves the user's configuration alone; tools/render_surface.py
# validates and dispatches the render to tools/render_workflow.py, and exits 2
# when a required tool is missing.
RENDER_OUTPUT ?= render.png
# The render modes the `render` target accepts, in the order
# tools/render_surface.py's CLI lists its flags: the calculator applet render
# first, then one entry per tools/render_dialogs.py's DIALOG_MODES table, then
# the standalone desktop mode (not a table entry: the CLI adds its --desktop
# flag beside the table-derived dialog flags). The
# two refusal echoes in the `render` recipe and the help line build their mode
# list from RENDER_MODE_LIST, so the list is spelled once here, and
# tests/test_render_make.py pins RENDER_MODE_VALUES against the DIALOG_MODES
# table plus calculator, desktop and splash so the two cannot drift apart. The recipe's case branches stay
# literal -- make cannot generate recipe text from a variable at recipe time
# without an extra interpreter run -- and that test also pins every branch's
# literal argv, so a mode missing its branch fails there.
RENDER_MODE_VALUES := calculator checkbox-dialog combobox-dialog lineedit-dialog menu-dialog radiolist-dialog calendar-dialog color-dialog icon-dialog progressbar-dialog slider-dialog textbox-dialog gtk-dialog inactive-dialog file-dialog desktop splash
comma := ,
empty :=
space := $(empty) $(empty)
RENDER_MODE_LIST := $(subst $(space),$(comma)$(space),$(RENDER_MODE_VALUES))

RENDER_MODE ?= calculator

render:
	@$(call require_python_ready,render)
	@set -f; set -- $${RENDER_MODE-calculator}; \
	case "$$#" in 1) ;; *) echo "RENDER_MODE must be one of $(RENDER_MODE_LIST)" >&2; exit 2 ;; esac; \
	case "$$1" in \
	  calculator) set -- ;; \
	  checkbox-dialog) set -- --checkbox-dialog ;; \
	  combobox-dialog) set -- --combobox-dialog ;; \
	  lineedit-dialog) set -- --lineedit-dialog ;; \
	  menu-dialog) set -- --menu-dialog ;; \
  radiolist-dialog) set -- --radiolist-dialog ;; \
	  calendar-dialog) set -- --calendar-dialog ;; \
  color-dialog) set -- --color-dialog ;; \
	  icon-dialog) set -- --icon-dialog ;; \
	  progressbar-dialog) set -- --progressbar-dialog ;; \
	  slider-dialog) set -- --slider-dialog ;; \
	  textbox-dialog) set -- --textbox-dialog ;; \
	  gtk-dialog) set -- --gtk-dialog ;; \
	  inactive-dialog) set -- --inactive-dialog ;; \
	  file-dialog) set -- --file-dialog ;; \
  desktop) set -- --desktop ;; \
  splash) set -- --splash ;; \
	  *) echo "RENDER_MODE must be one of $(RENDER_MODE_LIST)" >&2; exit 2 ;; \
	esac; \
	$(PYTHON) tools/render_surface.py "$$@" -- "$(RENDER_OUTPUT)"

# Apply the just-built theme everywhere it reaches. `install` runs as a
# sub-make so this reuses its guards and lock. A non-empty DESTDIR is refused
# first: applying a staged tree to the running session is wrong.
# tools/apply_theme.py re-selects the global theme (without --resetLayout, so
# the user's panels survive), the color scheme and the desktop theme, writes
# the theme's window-button layout into kwinrc with kwriteconfig6 (the
# look-and-feel apply drops those two keys, leaving the stock right-hand
# cluster), selects the Kvantum widget theme when kvantummanager is available,
# then asks KWin to reconfigure; the two best-effort selections and their
# command policy live in tools/apply_optional.py.
# tools/apply_gtk.py selects the installed GTK 3 and GTK 4
# schemes, tools/apply_cursor.py exposes and selects the Xcursor pointer set
# (skipping the selection when plasma-apply-cursortheme is absent), and
# tools/install_firefox.py installs the standalone sheets into the active
# Firefox profile when one exists. The startup splash and Firefox changes
# appear only on the next login or restart.
apply:
	@$(call refuse_destdir,apply)
	@$(call require_python_ready,apply)
	$(MAKE) --no-print-directory install
	$(PYTHON) tools/apply_theme.py
	$(PYTHON) tools/apply_gtk.py
	$(PYTHON) tools/apply_cursor.py --optional
	$(PYTHON) tools/install_firefox.py --optional$(if $(FIREFOX_PROFILE), --profile "$(FIREFOX_PROFILE)")

# Reselect the installed Plasma theme settings without installing packages or
# applying the other theme surfaces.
apply-plasma:
	@$(call refuse_destdir,apply-plasma)
	@$(call require_python_ready,apply-plasma)
	$(PYTHON) tools/apply_theme.py

# Install and select only the GTK themes, for repairing that surface without
# touching the Plasma packages. A non-empty DESTDIR is refused for the same
# reason as `apply`.
apply-gtk:
	@$(call refuse_destdir,apply-gtk)
	@$(call require_python_ready,apply-gtk)
	$(MAKE) --no-print-directory install INSTALL_PACKAGES=gtk
	$(PYTHON) tools/apply_gtk.py

# Clear only the GTK selection this theme wrote; a foreign gtk-theme-name and
# a foreign gtk-4.0/gtk.css are left untouched.
remove-gtk:
	@$(call require_python_ready,remove-gtk)
	$(PYTHON) tools/apply_gtk.py --remove

# Apply the cursor: install the icon theme (which carries the Xcursor
# pointer set), expose it at ~/.icons/org.macos8.desktop -- the path Xcursor searches
# instead of $XDG_DATA_HOME/icons -- and select it with
# plasma-apply-cursortheme. A non-empty DESTDIR is refused for the same reason
# as `apply`: the selection is for the running session, not a staged tree.
apply-cursor:
	@$(call refuse_destdir,apply-cursor)
	@$(call require_python_ready,apply-cursor)
	$(MAKE) --no-print-directory install INSTALL_PACKAGES=icon-theme
	$(PYTHON) tools/apply_cursor.py

# Remove only our ~/.icons symlink; a foreign path and kcminputrc are left
# untouched (the tool notes the reset command when the selection still names
# our theme).
remove-cursor:
	@$(call require_python_ready,remove-cursor)
	$(PYTHON) tools/apply_cursor.py --remove

# Copy the standalone Firefox userChrome.css and userContent.css sheets into
# one profile's chrome/ directory and add the marker-delimited preference that
# makes Firefox read them. Installs nothing under XDG_DATA_HOME, so it needs no
# DESTDIR guard or data-home lock. `make apply` runs this with --optional, so a
# machine without a Firefox profile still applies the other surfaces.
install-firefox:
	@$(call require_python_ready,install-firefox)
	$(PYTHON) tools/install_firefox.py $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")

# Remove only the sheets and preference block this theme wrote; a foreign
# userChrome.css or userContent.css and a foreign user_pref are left untouched.
remove-firefox:
	@$(call require_python_ready,remove-firefox)
	$(PYTHON) tools/install_firefox.py --remove $(if $(FIREFOX_PROFILE),--profile "$(FIREFOX_PROFILE)")

# Clear only the Kvantum selection `make apply` published
# (`kvantummanager --set org.macos8.desktop`, stored as `[General] theme=` in
# $XDG_CONFIG_HOME/Kvantum/kvantum.kvconfig); a foreign theme name and the
# rest of the file are left untouched, and nothing is created when the
# selection is not ours.
remove-kvantum:
	@$(call require_python_ready,remove-kvantum)
	$(PYTHON) tools/kvantum_selection.py

# Write a local-only post-commit hook (this clone's git hooks directory, never
# committed) so every commit re-runs `make apply`. tools/local_hook.py refuses
# to overwrite or remove a post-commit hook it did not write, so another tool's
# hook (Git LFS, for example) is left alone with a diagnostic.
install-local-hook:
	@$(call require_python_ready,install-local-hook)
	$(PYTHON) tools/local_hook.py install

uninstall-local-hook:
	@$(call require_python_ready,uninstall-local-hook)
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
# first with a diagnostic that names FLOCK_TIMEOUT. A value carrying a
# recipe-shell metacharacter is refused earlier still, at make level by the
# guard above, because this guard pastes the value into the double-quoted word
# `set -- "$(FLOCK_TIMEOUT)"` where it would run as shell syntax
# (TestShellUnsafeInstallPaths). Leading zeros are stripped
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
	$(call require_theme_links,install) && \
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

# The per-file loops that stage, rename, trap-clean and remove the GTK theme
# files (GTK_FILES above). They live beside the guards as top-level
# variables, not inside a `define`, so the `$${dest##*/}` basename pattern's
# `##` can be escaped the way require_flock_timeout does (a `define` stores
# text verbatim and the escape would reach the recipe shell still escaped).
# Each loop derives its file's hidden `.<basename>.staging` sibling from the
# destination, so the two phases cannot drift apart. A `call` splices one
# into the caller's recipe shell, as the guards do.
gtk_stage_loop = for name in $(GTK_FILES); do dest="$(GTK_INSTALL_DIR)/$$name"; staging="$${dest%/*}/.$${dest\#\#*/}.staging"; install -Dm644 "$(GTK_PACKAGE)/$$name" "$$staging" || exit 1; done
gtk_rename_loop = for name in $(GTK_FILES); do dest="$(GTK_INSTALL_DIR)/$$name"; mv "$${dest%/*}/.$${dest\#\#*/}.staging" "$$dest" || exit 1; done
gtk_staging_cleanup_loop = for name in $(GTK_FILES); do dest="$(GTK_INSTALL_DIR)/$$name"; rm -f "$${dest%/*}/.$${dest\#\#*/}.staging"; done
gtk_remove_loop = for name in $(GTK_FILES); do dest="$(GTK_INSTALL_DIR)/$$name"; rm -f "$$dest" "$${dest%/*}/.$${dest\#\#*/}.staging"; done

# Stage each GTK theme file as a hidden sibling and rename it in, as the
# color scheme does; the files spread across index.theme and the gtk-3.0/,
# gtk-4.0/ and assets/ subtrees of the shared directory, so the
# package-directory swap `install_package` performs does not fit. Every
# staging step runs before every rename as before, so a staging failure
# leaves the working files alone and the EXIT trap clears the staging
# siblings, while a rename that fails after other renames commit leaves
# those earlier renames standing, as `test_gtk_install` pins.
define install_gtk
	@install -d "$(GTK_INSTALL_DIR)/gtk-3.0" "$(GTK_INSTALL_DIR)/gtk-4.0" "$(GTK_INSTALL_DIR)/assets"; \
	trap '$(call gtk_staging_cleanup_loop)' EXIT; \
	{ $(call gtk_stage_loop); } && \
	{ $(call gtk_rename_loop); }
endef

_install:
	$(if $(filter color-scheme,$(INSTALL_PACKAGES)),$(call install_color_scheme))
	$(if $(filter look-and-feel,$(INSTALL_PACKAGES)),$(call install_package,$(LNF_ID),$(LNF_PACKAGE),$(LNF_INSTALL_DIR)))
	$(if $(filter desktop-theme,$(INSTALL_PACKAGES)),$(call install_package,$(DTHEME_ID),$(DTHEME_PACKAGE),$(DTHEME_INSTALL_DIR)))
	$(if $(filter aurorae,$(INSTALL_PACKAGES)),$(call install_package,$(AURORAE_ID),$(AURORAE_PACKAGE),$(AURORAE_INSTALL_DIR)))
	$(if $(filter kwin-decoration,$(INSTALL_PACKAGES)),$(call install_package,$(KWINDEC_ID),$(KWINDEC_PACKAGE),$(KWINDEC_INSTALL_DIR)))
	$(if $(filter wallpaper,$(INSTALL_PACKAGES)),$(call install_package,$(WALLPAPER_ID),$(WALLPAPER_PACKAGE),$(WALLPAPER_INSTALL_DIR)))
	$(if $(filter icon-theme,$(INSTALL_PACKAGES)),$(call install_package,$(ICON_THEME_ID),$(ICON_THEME_PACKAGE),$(ICON_THEME_INSTALL_DIR)))
	$(if $(filter kvantum,$(INSTALL_PACKAGES)),$(call install_kvantum))
	$(if $(filter fonts,$(INSTALL_PACKAGES)),$(call install_package,$(FONT_ID),$(FONT_PACKAGE),$(FONT_INSTALL_DIR)))
	$(if $(filter gtk,$(INSTALL_PACKAGES)),$(call install_gtk))

# Remove only the artifacts this theme installed -- including the GTK files,
# which every install now copies: the parent directories are shared (other
# color schemes,
# other look-and-feel/desktop-theme/Aurorae/wallpaper/icon/font packages, other
# Kvantum themes), so leave them and everything else in them alone. The hidden
# `.staging`/`.old` siblings are install's own temporary state: an install
# killed by SIGKILL cannot run its EXIT trap, so remove them here too instead
# of leaking them past uninstall. `rm -f`/`rm -rf` make a repeated run a no-op.
uninstall:
	@$(call require_data_home,uninstall) && \
	$(call require_flock_timeout,uninstall) && \
	$(call require_uninstall_parents,uninstall) && \
	install -d "$(DATA_HOME)" && \
	{ $(call run_locked,_uninstall,uninstall); }

# File removals follow symlinks in parent components. Refuse planted links in
# the fixed destination parents before the removal recipe can reach outside
# DATA_HOME; links at the final package directory are removed as links by
# rm -rf and do not redirect traversal.
require_uninstall_parents = for path in "$(DATA_HOME)" "$(INSTALL_DIR)" "$(LNF_INSTALL_DIR)" "$(DTHEME_INSTALL_DIR)" "$(AURORAE_INSTALL_DIR)" "$(KWINDEC_INSTALL_DIR)" "$(WALLPAPER_INSTALL_DIR)" "$(ICON_THEME_INSTALL_DIR)" "$(FONT_INSTALL_DIR)" "$(KVANTUM_INSTALL_DIR)" "$(GTK_INSTALL_DIR)" "$(GTK_INSTALL_DIR)/gtk-3.0" "$(GTK_INSTALL_DIR)/gtk-4.0" "$(GTK_INSTALL_DIR)/assets"; do if [ -L "$$path" ]; then echo "$(1): refusing a symlink in the install destination: $$path" >&2; exit 2; fi; done

# The package removals repeat one shape -- the directory this theme owns
# beside its `install_package` state: the package itself and the hidden
# `.staging`/`.old` siblings a killed install left behind. All seven
# directory-package removals (`_uninstall`) share this one word, so a
# future package family cannot drop a sibling by hand. The two file
# removals (`rm -f`) and the GTK per-file loops are different shapes and
# stay as they are. $(1) is the install dir, $(2) the package id.
remove_installed_package = rm -rf "$(1)/$(2)" "$(1)/.$(2).staging" "$(1)/.$(2).old";

# The removals share one shell (and one `set -e`) so a run spawns one child
# process instead of ten; each command keeps its own quoting and a failure
# still stops the recipe, as it did when make ran each line itself.
_uninstall:
	set -e; \
	rm -f "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)" "$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging"; \
	$(call remove_installed_package,$(LNF_INSTALL_DIR),$(LNF_ID)) \
	$(call remove_installed_package,$(DTHEME_INSTALL_DIR),$(DTHEME_ID)) \
	$(call remove_installed_package,$(AURORAE_INSTALL_DIR),$(AURORAE_ID)) \
	$(call remove_installed_package,$(KWINDEC_INSTALL_DIR),$(KWINDEC_ID)) \
	$(call remove_installed_package,$(WALLPAPER_INSTALL_DIR),$(WALLPAPER_ID)) \
	$(call remove_installed_package,$(ICON_THEME_INSTALL_DIR),$(ICON_THEME_ID)) \
	$(call remove_installed_package,$(FONT_INSTALL_DIR),$(FONT_ID)) \
	rm -f "$(KVANTUM_INSTALL_DIR)/$(KVANTUM_ID).kvconfig" "$(KVANTUM_INSTALL_DIR)/.$(KVANTUM_ID).kvconfig.staging" "$(KVANTUM_INSTALL_DIR)/$(KVANTUM_ID).svg" "$(KVANTUM_INSTALL_DIR)/.$(KVANTUM_ID).svg.staging"; \
	# `rmdir` hungrily removes only the emptied sub-directories and then the
	# shared `Kvantum/` parent and the shared theme directory itself; a
	# directory still holding a file the theme did not install survives, and
	# an absent or symlinked path just fails behind `|| true`.
	{ $(call gtk_remove_loop); }; \
	rmdir "$(GTK_INSTALL_DIR)/assets" "$(GTK_INSTALL_DIR)/gtk-3.0" "$(GTK_INSTALL_DIR)/gtk-4.0" "$(KVANTUM_INSTALL_DIR)" "$(GTK_INSTALL_DIR)" 2>/dev/null || true
# Every selection `make apply` published names an id `make uninstall` removes,
# so each config file the apply wrote is read back afterwards and a selection
# still naming ours prints a diagnostic naming the reset: the color scheme
# (`kdeglobals [General] ColorScheme`), the widget style and icon theme
# (`[KDE] widgetStyle`, `[Icons] Theme`), the GTK theme and marker-css pair
# (`gtk-3.0/settings.ini`, `gtk-4.0/settings.ini`, `gtk-4.0/gtk.css`), the
# Kvantum theme (`Kvantum/kvantum.kvconfig [General] theme`), the Plasma
# desktop theme and pointer pair (`plasmarc [Theme] name`,
# `kcminputrc [Mouse] cursorTheme`), the five Lato font selections
# (`[General] font`, `menuFont`, `toolBarFont`, `smallestReadableFont`,
# `[WM] activeFont`), the global theme (`[KDE] LookAndFeelPackage`) and the
# KWin decoration keys (`[org.kde.kdecoration2]`), then the same
# `kdedefaults/` mirrors the look-and-feel apply left in the defaults layer
# (`ksplashrc`, `package`, `kdeglobals`, `kwinrc`, `plasmarc`). The
# diagnostics are warnings only -- none may edit the user's config files,
# which the recipes above own; the readers share one scanner in
# tools/uninstall_config.py, which resolves the config home the way this
# recipe did (`XDG_CONFIG_HOME` absolute, else `$HOME/.config`) and keeps the
# read rules the corpus in tests/support/kde_ini_corpus.py pins; the handlers
# for one config surface each live in tools/uninstall_live_diagnostics.py and
# tools/uninstall_defaults_diagnostics.py, so tools/uninstall_diagnostics.py
# only owns the CLI and the ordered calls. The scan of
# one shell spawned one extra child per diagnostic before; the module is at
# most one child and a diagnostic failure is still never uninstall's failure.
# The handlers read exactly the thirteen paths the guard loop below stats, so
# the recipe lists them before it spawns the child: when none exists the scan
# cannot name any selection and is skipped. The shell resolves the config
# home exactly the way tools/uninstall_config.py's `config_home` does (an
# absolute `XDG_CONFIG_HOME` wins; an unset, empty or relative one falls back
# to `$HOME/.config`; with neither the scan runs nowhere) -- the config-home
# resolution and these paths are platform-required surfaces the reference
# screenshots do not show; their provenance is the same apply-published
# selections the diagnostics name above. Parity between the guard and the
# scan (every handler path listed, fallback and none-cases resolved alike,
# one child only) is pinned by
# tests/test_uninstall_diagnostics_skip.py.
	@cfg="$$XDG_CONFIG_HOME"; \
	case "$$cfg" in /*) ;; *) cfg="";; esac; \
	if [ -z "$$cfg" ]; then case "$$HOME" in /*) cfg="$$HOME/.config";; esac; fi; \
	if [ -n "$$cfg" ]; then \
	  scan=""; \
	  for path in "$$cfg/kdeglobals" "$$cfg/kdedefaults/kdeglobals" \
	  "$$cfg/kdedefaults/kwinrc" "$$cfg/kdedefaults/plasmarc" \
	  "$$cfg/kdedefaults/ksplashrc" "$$cfg/kdedefaults/package" \
	  "$$cfg/gtk-3.0/settings.ini" "$$cfg/gtk-4.0/settings.ini" \
	  "$$cfg/gtk-4.0/gtk.css" "$$cfg/Kvantum/kvantum.kvconfig" \
	  "$$cfg/plasmarc" "$$cfg/kcminputrc" "$$cfg/kwinrc"; do \
	    if [ -e "$$path" ]; then scan="yes"; break; fi; \
	  done; \
	  if [ -n "$$scan" ]; then \
	    $(PYTHON) tools/uninstall_diagnostics.py --scheme-id "$(COLOR_SCHEME_ID)" --icon-id "$(ICON_THEME_ID)" --kvantum-id "$(KVANTUM_ID)" --gtk-id "$(GTK_ID)" --desktop-id "$(DTHEME_ID)" --lnf-id "$(LNF_ID)" --aurorae-id "$(AURORAE_ID)" --css-marker "$(GTK_USER_CSS_MARKER)" || true; \
	  fi; \
	fi

install-gtk:
	@$(MAKE) --no-print-directory install INSTALL_PACKAGES=gtk

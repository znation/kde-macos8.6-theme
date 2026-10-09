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
DTHEME_PACKAGE := theme/desktop-themes/$(DTHEME_ID)
DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme

AURORAE_ID := org.macos8.desktop
AURORAE_PACKAGE := theme/aurorae/themes/$(AURORAE_ID)
AURORAE_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/aurorae/themes

# Stage a directory package as a sibling, then swap it in with a rename, so a
# copy that fails or is interrupted cannot leave a partial package installed or
# delete the working one. The old package is moved aside rather than deleted
# first: the swap is then a rename either way, and if the final rename fails the
# EXIT trap moves the old package back. A reinstall still replaces rather than
# merges, so files deleted from the package source do not stay behind as stale
# QML. A SIGKILL between the two renames cannot run the trap, leaving the
# package absent and its bytes in `.old`; the recovery below moves `.old` back
# before anything is removed, so the next install (or a copy that fails) leaves
# the last working package installed instead of deleting it. $(1) is the
# package id, $(2) its source directory, $(3) the install dir.
define install_package
	@staging='$(3)/.$(1).staging'; \
	old='$(3)/.$(1).old'; \
	trap 'rm -rf "$$staging"; if [ ! -e "$(3)/$(1)" ] && [ -e "$$old" ]; then mv "$$old" "$(3)/$(1)"; fi' EXIT; \
	if [ ! -e "$(3)/$(1)" ] && [ -e "$$old" ]; then mv "$$old" "$(3)/$(1)"; fi && \
	rm -rf "$$staging" "$$old" && \
	cp -r "$(2)" "$$staging" && \
	if [ -e "$(3)/$(1)" ]; then mv "$(3)/$(1)" "$$old"; fi && \
	mv "$$staging" "$(3)/$(1)" && \
	rm -rf "$$old"
endef

.PHONY: help check check-references install uninstall _install _uninstall

# `check` runs the whole suite by default. A caller can narrow it to the test
# modules a shell glob matches, e.g. `make check CHECK_PATTERN='test_colorscheme*.py'`,
# so a focused run does not need `python3 -m unittest discover -s tests ...`
# (the test modules import each other by bare name, so they only run under
# `discover`, not as `python3 -m unittest tests.<module>`).
CHECK_PATTERN ?= test*.py

# A caller who wants one test module, class or method rather than a whole-file
# glob sets CHECK_TESTS, e.g. `make check CHECK_TESTS=test_colorscheme.TestAnchors`
# or `make check CHECK_TESTS='test_a test_b.TestC'`. The named specs run from
# tests/ with the same interpreter, so the test modules' bare-name imports
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

check:
	@$(call require_python,check)
	@$(call require_python_version,check)
	@$(call require_check_tests,check)
ifeq ($(strip $(CHECK_TESTS)),)
	$(PYTHON) -m unittest discover -s tests -v -p '$(CHECK_PATTERN)'
else
	cd tests && $(PYTHON) -m unittest -v $(CHECK_TESTS)
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
	@echo "  install           install the color scheme and theme packages"
	@echo "  uninstall         remove the installed artifacts"
	@echo ""
	@echo "Variables (make VAR=value TARGET):"
	@echo "  CHECK_PATTERN=glob  test modules 'check' discovers (default test*.py)"
	@echo "  CHECK_TESTS=spec    test modules/classes/methods to run instead of discovering"
	@echo "  PYTHON=path         Python 3.10+ interpreter for check and check-references (default python3)"
	@echo "  XDG_DATA_HOME=path  absolute data home to install into (default under HOME)"
	@echo "  DESTDIR=path        staging prefix prepended to XDG_DATA_HOME"
	@echo "  FLOCK_TIMEOUT=s     seconds to wait for the install lock (default 60)"

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
	@$(call require_python,check-references)
	@$(call require_python_version,check-references)
	$(PYTHON) tools/check_references.py --self-test
	$(PYTHON) tools/check_references.py

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

install:
	@$(call require_data_home,install)
	@$(call require_flock_timeout,install)
	@install -d "$(DATA_HOME)"
	@$(call run_locked,_install,install)

_install:
# Stage the scheme as a hidden sibling and rename it in, so a copy that fails
# or is interrupted cannot truncate the working installed scheme. The rename
# replaces atomically, and the EXIT trap removes the staging file on failure.
	@staging='$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging'; \
	trap 'rm -f "$$staging"' EXIT; \
	install -Dm644 "$(COLOR_SCHEME)" "$$staging" && \
	mv "$$staging" "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)"
	install -d "$(LNF_INSTALL_DIR)"
	$(call install_package,$(LNF_ID),$(LNF_PACKAGE),$(LNF_INSTALL_DIR))
	install -d "$(DTHEME_INSTALL_DIR)"
	$(call install_package,$(DTHEME_ID),$(DTHEME_PACKAGE),$(DTHEME_INSTALL_DIR))
	install -d "$(AURORAE_INSTALL_DIR)"
	$(call install_package,$(AURORAE_ID),$(AURORAE_PACKAGE),$(AURORAE_INSTALL_DIR))

# Remove only the artifacts `install` copied: the parent directories are shared
# (other color schemes, other look-and-feel/desktop-theme packages), so leave
# them and everything else in them alone. The hidden `.staging`/`.old` siblings
# are install's own temporary state: an install killed by SIGKILL cannot run its
# EXIT trap, so remove them here too instead of leaking them past uninstall.
# `rm -f`/`rm -rf` make a repeated run a no-op.
uninstall:
	@$(call require_data_home,uninstall)
	@$(call require_flock_timeout,uninstall)
	@install -d "$(DATA_HOME)"
	@$(call run_locked,_uninstall,uninstall)

_uninstall:
	rm -f "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)" "$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging"
	rm -rf "$(LNF_INSTALL_DIR)/$(LNF_ID)" "$(LNF_INSTALL_DIR)/.$(LNF_ID).staging" "$(LNF_INSTALL_DIR)/.$(LNF_ID).old"
	rm -rf "$(DTHEME_INSTALL_DIR)/$(DTHEME_ID)" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).staging" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).old"
	rm -rf "$(AURORAE_INSTALL_DIR)/$(AURORAE_ID)" "$(AURORAE_INSTALL_DIR)/.$(AURORAE_ID).staging" "$(AURORAE_INSTALL_DIR)/.$(AURORAE_ID).old"
# Removing the scheme does not touch the user's `[General] ColorScheme`
# selection. If it still names the scheme just removed, KDE cannot resolve the
# id and falls back to BreezeLight on every start without rewriting the stale
# key, so warn and name the reset command. Read `$XDG_CONFIG_HOME/kdeglobals`
# (default `$HOME/.config/kdeglobals`, ignoring an empty or relative
# XDG_CONFIG_HOME) the way KDE reads it: case-sensitive keys in the
# `[General]` section. This is a diagnostic only -- it must not edit the file.
	@config_home="$${XDG_CONFIG_HOME:-}"; \
	case "$$config_home" in /*) ;; *) config_home="";; esac; \
	if [ -z "$$config_home" ]; then case "$${HOME:-}" in /*) config_home="$$HOME/.config";; esac; fi; \
	kdeglobals="$$config_home/kdeglobals"; \
	if [ -n "$$config_home" ] && [ -f "$$kdeglobals" ]; then \
	  selected=$$(awk '/^\[/ { section=$$0; sub(/^\[/,"",section); sub(/\].*$$/,"",section); next } section=="General" && $$0 ~ /^[[:space:]]*ColorScheme[[:space:]]*=/ { value=$$0; sub(/^[[:space:]]*ColorScheme[[:space:]]*=/,"",value); sub(/^[[:space:]]*/,"",value); sub(/[[:space:]]*$$/,"",value); print value; exit }' "$$kdeglobals"); \
	  if [ "$$selected" = "$(COLOR_SCHEME_ID)" ]; then \
	    echo "uninstall: color scheme $(COLOR_SCHEME_ID) is still selected in $$kdeglobals after removal; if KDE cannot resolve it, it falls back to BreezeLight on the next start. Reset it with: plasma-apply-colorscheme BreezeLight" >&2; \
	  fi; \
	fi

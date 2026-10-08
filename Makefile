PYTHON ?= python3
XDG_DATA_HOME ?= $(HOME)/.local/share

# The data home doubles as the install/uninstall lock (see `install` below).
DATA_HOME := $(DESTDIR)$(XDG_DATA_HOME)

COLOR_SCHEME := theme/color-schemes/MacOS8.colors
# KDE derives the scheme id from the installed filename, so install under the
# source's own basename: renaming the scheme then moves the id with it instead
# of leaving a stale hardcoded name behind.
COLOR_SCHEME_NAME := $(notdir $(COLOR_SCHEME))
INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/color-schemes

LNF_ID := org.macos8.desktop
LNF_PACKAGE := theme/look-and-feel/$(LNF_ID)
LNF_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/look-and-feel

DTHEME_ID := org.macos8.desktop
DTHEME_PACKAGE := theme/desktop-themes/$(DTHEME_ID)
DTHEME_INSTALL_DIR := $(DESTDIR)$(XDG_DATA_HOME)/plasma/desktoptheme

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

.PHONY: check check-references install uninstall _install _uninstall

check:
	$(PYTHON) -m unittest discover -s tests -v

# Opt-in: the repository check needs materialized Git LFS images, so it stays
# out of `check`. The deterministic self-test runs first and fails fast.
check-references:
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

# Run the internal target $(1) under the data-home lock, naming $(2) when the
# bounded wait expires instead of letting the command's own failure be blamed.
run_locked = flock -w $(FLOCK_TIMEOUT) -E $(FLOCK_CONFLICT_EXIT) "$(DATA_HOME)" $(MAKE) --no-print-directory $(1) || { status=$$?; if [ $$status -eq $(FLOCK_CONFLICT_EXIT) ]; then echo "$(2): gave up after $(FLOCK_TIMEOUT)s waiting for the $(DATA_HOME) lock; another install or uninstall holds it" >&2; fi; exit $$status; }

install:
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

# Remove only the artifacts `install` copied: the parent directories are shared
# (other color schemes, other look-and-feel/desktop-theme packages), so leave
# them and everything else in them alone. The hidden `.staging`/`.old` siblings
# are install's own temporary state: an install killed by SIGKILL cannot run its
# EXIT trap, so remove them here too instead of leaking them past uninstall.
# `rm -f`/`rm -rf` make a repeated run a no-op.
uninstall:
	@install -d "$(DATA_HOME)"
	@$(call run_locked,_uninstall,uninstall)

_uninstall:
	rm -f "$(INSTALL_DIR)/$(COLOR_SCHEME_NAME)" "$(INSTALL_DIR)/.$(COLOR_SCHEME_NAME).staging"
	rm -rf "$(LNF_INSTALL_DIR)/$(LNF_ID)" "$(LNF_INSTALL_DIR)/.$(LNF_ID).staging" "$(LNF_INSTALL_DIR)/.$(LNF_ID).old"
	rm -rf "$(DTHEME_INSTALL_DIR)/$(DTHEME_ID)" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).staging" "$(DTHEME_INSTALL_DIR)/.$(DTHEME_ID).old"

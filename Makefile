at ?= @
makefile_directory := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  build     : build compressed package locally"
	@echo "  check     : run pre-commit and pytest"
	@echo "  clean     : delete all generated content"
	@echo "  distclean : delete all builds"
	@echo "  sync      : fill the venv"
	@echo "  setup     : make a venv"
	@echo "  publish   : publish to PyPi"

venv := $(makefile_directory)/.venv
activate := $(venv)/bin/activate

$(venv)/bin/activate:
	@echo "########"
	@echo "# venv #"
	@echo "########"
	$(at)uv --directory $(makefile_directory) venv
	@echo ""

.PHONY: setup
setup: $(venv)/bin/activate

.PHONY: sync
sync: setup
	@echo "########"
	@echo "# sync #"
	@echo "########"
	$(at)uv --directory $(makefile_directory) sync --all-extras
	@echo ""

.PHONY: check
check: sync
	@echo "#########"
	@echo "# check #"
	@echo "#########"
	$(at)$(MAKE) -C samples/material build
	$(at)$(MAKE) -C samples/mkdocs build
	$(at)$(MAKE) -C samples/mkdocs-material build
	@echo ""
	$(at). $(activate) && pre-commit run --all-files
	@echo ""

.PHONY: build
build: check
	@echo "#########"
	@echo "# build #"
	@echo "#########"
	$(at)uv --directory $(makefile_directory) lock \
		&& uv --directory $(makefile_directory) build
	@echo ""

token_argument = $(shell \
	if [ -f $(makefile_directory)/.token ]; then \
		echo "--token $$(cat $(makefile_directory)/.token)"; \
	else \
		echo ""; \
	fi)

.PHONY: publish
publish: clean build
	@echo "###########"
	@echo "# publish #"
	@echo "###########"
	$(at)uv --directory $(makefile_directory) publish $(token_argument)
	@echo ""

.PHONY: clean
clean:
	$(at)rm -rf $(makefile_directory)/.venv
	$(at)rm -rf $(makefile_directory)/dist/
	$(at)$(MAKE) -C samples/material clean
	$(at)$(MAKE) -C samples/mkdocs clean
	$(at)$(MAKE) -C samples/mkdocs-material clean

.PHONY: distclean
distclean: clean
	$(at)rm -rf $(makefile_directory)/.aider*
	$(at)rm -rf $(makefile_directory)/.mypy_cache
	$(at)rm -rf $(makefile_directory)/.ruff_cache
	$(at)find $(makefile_directory)/src -type d -name __pycache__ -exec rm -rf {} +
	$(at)$(MAKE) -C samples/material distclean
	$(at)$(MAKE) -C samples/mkdocs distclean
	$(at)$(MAKE) -C samples/mkdocs-material distclean

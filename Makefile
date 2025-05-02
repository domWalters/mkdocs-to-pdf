at ?= @
makefile_directory := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  all       : clean, setup, sync, build, check, docs, samples"
	@echo "  build     : build wheel and compressed source"
	@echo "  check     : run pre-commit"
	@echo "  clean     : delete all generated content"
	@echo "  distclean : delete the venv and all cached data"
	@echo "  docs      : build the documentation"
	@echo "  publish   : publish to PyPi"
	@echo "  samples   : build the samples"
	@echo "  setup     : make a venv"
	@echo "  sync      : fill the venv"

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
	$(at). $(activate) \
        && uv --directory $(makefile_directory) lock \
	    && uv --directory $(makefile_directory) sync --extra all
	@echo ""

.PHONY: build
build: sync
	@echo "#########"
	@echo "# build #"
	@echo "#########"
	$(at). $(activate) \
        && uv --directory $(makefile_directory) lock \
		&& uv --directory $(makefile_directory) build
	@echo ""

.PHONY: check
check: sync
	@echo "#########"
	@echo "# check #"
	@echo "#########"
	$(at). $(activate) && pre-commit run --all-files
	@echo ""

.PHONY: docs
docs: sync
	@echo "########"
	@echo "# docs #"
	@echo "########"
	$(at). $(activate) && cd $(makefile_directory) && mkdocs build
	@echo ""

.PHONY: samples
samples: sync
	@echo "###########"
	@echo "# samples #"
	@echo "###########"
	$(at)$(MAKE) -C samples/mkdocs build
	$(at)$(MAKE) -C samples/mkdocs-material build
	@echo ""

.PHONY: all
all: clean build check docs samples

token_argument = $(shell \
	if [ -f $(makefile_directory)/.token ]; then \
		echo "--token $$(cat $(makefile_directory)/.token)"; \
	else \
		echo ""; \
	fi)

.PHONY: publish
publish: all
	@echo "###########"
	@echo "# publish #"
	@echo "###########"
	$(at)uv --directory $(makefile_directory) publish $(token_argument)
	@echo ""

.PHONY: clean
clean:
	$(at)rm -rf $(makefile_directory)/dist/
	$(at)$(MAKE) -C samples/mkdocs clean
	$(at)$(MAKE) -C samples/mkdocs-material clean

.PHONY: distclean
distclean: clean
	$(at)rm -rf $(makefile_directory)/.aider*
	$(at)rm -rf $(makefile_directory)/.mypy_cache
	$(at)rm -rf $(makefile_directory)/.ruff_cache
	$(at)rm -rf $(makefile_directory)/.venv
	$(at)find $(makefile_directory)/src -type d -name __pycache__ -exec rm -rf {} +
	$(at)$(MAKE) -C samples/mkdocs distclean
	$(at)$(MAKE) -C samples/mkdocs-material distclean

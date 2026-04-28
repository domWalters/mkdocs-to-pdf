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

$(activate):
	@echo "########"
	@echo "# venv #"
	@echo "########"
	$(at)uv --directory $(makefile_directory) venv
	@echo ""

.PHONY: setup
setup: $(activate)

.PHONY: sync
sync: setup
	@echo "########"
	@echo "# sync #"
	@echo "########"
	$(at)git -C $(makefile_directory) submodule update --init --recursive
	$(at). $(activate) \
		&& uv --directory $(makefile_directory) lock \
		&& uv --directory $(makefile_directory) sync --extra all
	@echo ""

$(makefile_directory)/.git/hooks/pre-commit:
	@echo "###############"
	@echo "# setup-check #"
	@echo "###############"
	$(at). $(activate) \
		&& cd $(makefile_directory) \
		&& pre-commit install
	@echo ""

.PHONY: setup-check
setup-check: $(makefile_directory)/.git/hooks/pre-commit

.PHONY: check
check: sync setup-check
	@echo "#########"
	@echo "# check #"
	@echo "#########"
	$(at). $(activate) \
		&& pre-commit run --all-files
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

.PHONY: docs
docs: sync
	@echo "########"
	@echo "# docs #"
	@echo "########"
	$(at). $(activate) \
		&& cd $(makefile_directory) \
		&& mkdocs build
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
all: clean check docs samples build

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
	$(at)rm -rf \
        $(makefile_directory)/dist/ \
	    $(makefile_directory)/docs/build/
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs clean
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs-material clean

.PHONY: distclean
distclean: clean
	$(at)rm -rf \
        $(makefile_directory)/.aider* \
		$(makefile_directory)/.cache \
		$(makefile_directory)/.coverage \
		$(makefile_directory)/.coverage.xml \
		$(makefile_directory)/.htmlcov \
		$(makefile_directory)/.junit.xml \
		$(makefile_directory)/.pytest_cache \
	    $(makefile_directory)/.ruff_cache \
	    $(venv)
	$(at)find $(makefile_directory) -type d -name ".mypy_cache" -exec rm -rf {} +
	$(at)find $(makefile_directory) -type d -name "__pycache__" -exec rm -rf {} +
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs distclean
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs-material distclean

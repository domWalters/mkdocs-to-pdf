at ?= @
makefile_directory := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: help
help:
	@echo "Usage:"
	@echo "  all             : clean, setup, sync, build, check, docs, samples"
	@echo "  build           : build wheel and compressed source"
	@echo "  changelog       : regenerate CHANGELOG.md from commit history"
	@echo "  check           : run pre-commit"
	@echo "  clean           : delete all generated content"
	@echo "  clean-build     : delete all builds"
	@echo "  distclean       : delete the venv and all cached data"
	@echo "  docs            : build the documentation"
	@echo "  publish         : publish to PyPi"
	@echo "  samples         : build the samples"
	@echo "  setup           : make a venv"
	@echo "  setup-check     : install pre-commit hooks"
	@echo "  setup-venv      : make a venv without filling it"
	@echo "  sync            : perform all setup and sync steps"
	@echo "  sync-submodules : update all submodules"
	@echo "  sync-venv       : fill / refresh the venv"
	@echo "  tests           : run tests"

venv := $(makefile_directory)/.venv
activate := $(venv)/bin/activate

$(activate):
	@echo "########"
	@echo "# venv #"
	@echo "########"
	$(at)uv --directory $(makefile_directory) venv
	@echo ""

.PHONY: setup-venv
setup-venv: $(activate)

.PHONY: sync-submodules
sync-submodules:
	$(at)git -C $(makefile_directory) submodule update --init --recursive

.PHONY: sync-venv
sync-venv: setup-venv
	@echo "########"
	@echo "# sync #"
	@echo "########"
	$(at). $(activate) \
		&& uv --directory $(makefile_directory) lock \
		&& uv --directory $(makefile_directory) sync --all-extras --upgrade
	@echo ""

$(venv)/bin/pre-commit: | sync-venv

.PHONY: sync
sync: sync-submodules sync-venv

$(makefile_directory)/.git/hooks/pre-commit: | $(venv)/bin/pre-commit
	@echo "###############"
	@echo "# setup-check #"
	@echo "###############"
	$(at). $(activate) \
		&& cd $(makefile_directory) \
		&& pre-commit install --install-hooks
	@echo ""

.PHONY: setup-check
setup-check: $(makefile_directory)/.git/hooks/pre-commit

.PHONY: setup
setup: sync setup-check

.PHONY: check
check: sync-venv setup-check
	@echo "#########"
	@echo "# check #"
	@echo "#########"
	$(at). $(activate) \
		&& pre-commit run --files $$(git diff --name-only HEAD)
	@echo ""

.PHONY: check-all
check-all: sync-venv setup-check
	@echo "#############"
	@echo "# check-all #"
	@echo "#############"
	$(at). $(activate) \
		&& pre-commit run --all-files
	@echo ""

.PHONY: build
build: sync-venv clean-build
	@echo "#########"
	@echo "# build #"
	@echo "#########"
	$(at). $(activate) \
		&& uv --directory $(makefile_directory) lock \
		&& uv --directory $(makefile_directory) build
	@echo ""

.PHONY: changelog
changelog:
	@echo "#############"
	@echo "# changelog #"
	@echo "#############"
	$(at). $(activate) \
		&& $(makefile_directory)/hooks/update-changelog.py
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
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs build
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs-material build
	@echo ""

ifeq ($(strip $(PY)),)
hatch_test_args=--all
else
hatch_test_args=-i py=$(PY)
endif

.PHONY: tests
tests: sync
	@echo "########"
	@echo "# test #"
	@echo "########"
	$(at). $(activate) \
		&& cd $(makefile_directory) \
		&& hatch test $(hatch_test_args)
	@echo ""

.PHONY: all
all: clean check docs samples tests build

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

.PHONY: clean-build
clean-build:
	$(at)rm -rf \
        $(makefile_directory)/dist/ \
	    $(makefile_directory)/docs/build/

.PHONY: clean
clean: clean-build
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
		$(makefile_directory)/.opencode/node_modules \
		$(makefile_directory)/.opencode/package*.json \
		$(makefile_directory)/.pytest_cache \
		$(makefile_directory)/.ruff_cache \
	    $(venv)
	$(at)find $(makefile_directory) -type d -name ".mypy_cache" -exec rm -rf {} +
	$(at)find $(makefile_directory) -type d -name "__pycache__" -exec rm -rf {} +
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs distclean
	$(at)$(MAKE) -C $(makefile_directory)/samples/mkdocs-material distclean

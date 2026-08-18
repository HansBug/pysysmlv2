PYTHON ?= python
DOC_DIR := docs
SRC_DIR := pysysmlv2
TEST_DIR := test
RANGE_DIR ?= .

RANGE_TEST_DIR := $(TEST_DIR)/$(RANGE_DIR)
RANGE_SRC_DIR := $(SRC_DIR)/$(RANGE_DIR)
COV_TYPES ?= xml term-missing
MIN_COVERAGE ?=
WORKERS ?=
COV_REPORT_ARGS := $(foreach type,$(COV_TYPES),--cov-report=$(type))

.PHONY: help install install-dev antlr_update antlr_build antlr_check rst_auto rst_auto_check unittest doctest test format format_check lint docs docs_en docs_zh docs_check package package_check clean

help:
	@echo "pysysmlv2 build system"
	@echo "====================="
	@echo ""
	@echo "Environment:"
	@echo "  PYTHON=...                       Python interpreter (default: python)"
	@echo "  RANGE_DIR=...                    Source/test scope (default: .)"
	@echo ""
	@echo "Installation and packaging:"
	@echo "  make install                     Install the package in editable mode"
	@echo "  make install-dev                 Install development, test, docs, and tooling extras"
	@echo "  make package                     Build sdist and wheel into dist/"
	@echo "  make package_check               Check VERSION and generated package data"
	@echo "  make clean                       Remove build, dist, and egg-info output"
	@echo ""
	@echo "ANTLR grammar:"
	@echo "  make antlr_update                Copy the pinned submodule G4 files and regenerate"
	@echo "  make antlr_build                 Regenerate Python lexer/parser from copied G4 files"
	@echo "  make antlr_check                 Verify generated artifacts, manifest, and symlink contracts"
	@echo "                                  Requires Java only when the pinned ANTLR JAR is absent"
	@echo ""
	@echo "Documentation source generation:"
	@echo "  make rst_auto                    Generate API RST pages and bilingual API indexes"
	@echo "  make rst_auto_check              Fail when generated API RST pages are stale"
	@echo "  make docs_en                     Build strict English Sphinx HTML"
	@echo "  make docs_zh                     Build strict Chinese Sphinx HTML"
	@echo "  make docs                        Build both English and Chinese Sphinx HTML"
	@echo "  make docs_check                  Build both languages with warnings as errors"
	@echo ""
	@echo "Testing and quality:"
	@echo "  make unittest                    Run unit tests with XML and term-missing coverage"
	@echo "  make test                        Alias for make unittest"
	@echo "  make unittest RANGE_DIR=syntax   Run only the syntax test subtree"
	@echo "  make unittest COV_TYPES='xml term-missing'"
	@echo "                                  Select coverage report types"
	@echo "  make unittest MIN_COVERAGE=80   Enforce a minimum coverage percentage"
	@echo "  make unittest WORKERS=4         Pass -n 4 to pytest-xdist when installed"
	@echo "  make doctest                     Run all public docstring examples"
	@echo "  make format                     Format service-owned Python files with Ruff"
	@echo "  make format_check                Check Python formatting without changing files"
	@echo "  make lint                        Run Ruff lint and import ordering checks"

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev,test,docs,tooling]

antlr_update:
	$(PYTHON) -m tools.antlr_update

antlr_build:
	$(PYTHON) -m tools.antlr_build

antlr_check:
	$(PYTHON) -m tools.check_generated

rst_auto:
	$(PYTHON) -m tools.auto_rst
	$(PYTHON) -m tools.auto_rst_top_index

rst_auto_check:
	$(PYTHON) -m tools.auto_rst --check
	$(PYTHON) -m tools.auto_rst_top_index --check

unittest:
	UNITTEST=1 $(PYTHON) -m pytest "$(RANGE_TEST_DIR)" -s -v -m unit \
		--junitxml=junit.xml -o junit_family=legacy \
		$(COV_REPORT_ARGS) --cov="$(RANGE_SRC_DIR)" \
		$(if $(MIN_COVERAGE),--cov-fail-under=$(MIN_COVERAGE),) \
		$(if $(WORKERS),-n $(WORKERS),)

test: unittest

doctest:
	$(PYTHON) -m pytest --doctest-modules pysysmlv2 tools \
		--ignore=pysysmlv2/syntax/generated --ignore=upstream

format:
	$(PYTHON) -m ruff format pysysmlv2 test tools setup.py

format_check:
	$(PYTHON) -m ruff format --check pysysmlv2 test tools setup.py

lint:
	$(PYTHON) -m ruff check pysysmlv2 test tools setup.py

docs:
	$(MAKE) -C "$(DOC_DIR)" html_en
	$(MAKE) -C "$(DOC_DIR)" html_zh

docs_en:
	$(MAKE) -C "$(DOC_DIR)" html_en

docs_zh:
	$(MAKE) -C "$(DOC_DIR)" html_zh

docs_check:
	$(MAKE) -C "$(DOC_DIR)" check

package:
	$(PYTHON) -m build --sdist --wheel --outdir dist

package_check:
	$(PYTHON) -m tools.package_check

clean:
	rm -rf build dist *.egg-info

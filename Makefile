PYTHON ?= python
DOC_DIR := docs
SRC_DIR := pysysmlv2
TEST_DIR := test
RANGE_DIR ?= .
UPSTREAM_GRAMMAR_DIR := upstream/sysml-v2-grammar/grammar
UPSTREAM_CONFIG := upstream/sysml-v2-grammar/scripts/config.json
GENERATED_DIR := pysysmlv2/syntax/generated
ANTLR_DIR := .antlr
ANTLR_VERSION := 4.13.2
ANTLR_SHA256 := eae2dfa119a64327444672aff63e9ec35a20180dc5b8090b7a6ab85125df4d76
ANTLR_JAR := $(ANTLR_DIR)/antlr-$(ANTLR_VERSION)-complete.jar
ANTLR_TEMP := $(ANTLR_DIR)/generated

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
	@echo "                                  Requires Java and the pinned ANTLR JAR (downloaded if absent)"
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
	mkdir -p "$(GENERATED_DIR)"
	cp "$(UPSTREAM_GRAMMAR_DIR)/SysMLv2Lexer.g4" "$(GENERATED_DIR)/SysMLv2Lexer.g4"
	cp "$(UPSTREAM_GRAMMAR_DIR)/SysMLv2Parser.g4" "$(GENERATED_DIR)/SysMLv2Parser.g4"
	$(MAKE) antlr_build

antlr_build:
	mkdir -p "$(ANTLR_DIR)" "$(GENERATED_DIR)"
	$(PYTHON) -c 'from pathlib import Path; import urllib.request; path=Path("$(ANTLR_JAR)"); path.parent.mkdir(parents=True, exist_ok=True); path.exists() or urllib.request.urlretrieve("https://www.antlr.org/download/antlr-$(ANTLR_VERSION)-complete.jar", str(path))'
	$(PYTHON) -c 'import hashlib,sys; from pathlib import Path; path=Path("$(ANTLR_JAR)"); actual=hashlib.sha256(path.read_bytes()).hexdigest(); expected="$(ANTLR_SHA256)"; sys.exit("ANTLR JAR checksum mismatch: "+actual) if actual != expected else None'
	rm -rf "$(ANTLR_TEMP)"
	mkdir -p "$(ANTLR_TEMP)"
	java -jar "$(ANTLR_JAR)" -Dlanguage=Python3 -Xexact-output-dir -o "$(ANTLR_TEMP)" \
		"$(GENERATED_DIR)/SysMLv2Lexer.g4" "$(GENERATED_DIR)/SysMLv2Parser.g4"
	rm -f "$(GENERATED_DIR)"/*.py "$(GENERATED_DIR)"/*.tokens "$(GENERATED_DIR)"/*.interp
	cp "$(ANTLR_TEMP)"/*.py "$(ANTLR_TEMP)"/*.tokens "$(ANTLR_TEMP)"/*.interp "$(GENERATED_DIR)"
	printf '%s\n' '"""Generated ANTLR4 Python modules; regenerate with ``make antlr_build``."""' > "$(GENERATED_DIR)/__init__.py"
	$(PYTHON) -m ruff format --no-force-exclude "$(GENERATED_DIR)"/*.py
	$(PYTHON) -c 'import hashlib,json,subprocess; from pathlib import Path; root=Path("."); generated=root/"$(GENERATED_DIR)"; config=json.loads((root/"$(UPSTREAM_CONFIG)").read_text(encoding="utf-8")); digest=lambda path: hashlib.sha256(path.read_bytes()).hexdigest(); run=lambda args: subprocess.run(args, cwd=str(root/"upstream/sysml-v2-grammar"), capture_output=True, text=True).stdout.strip(); commit=run(["git","rev-parse","HEAD"]) or "unknown"; tag=run(["git","describe","--tags","--exact-match"]) or "v"+config["grammar_version"]; metadata={"antlr_jar_sha256":digest(root/"$(ANTLR_JAR)"),"antlr_version":"$(ANTLR_VERSION)","grammar_version":config["grammar_version"],"omg_release":config["release_tag"],"source_commit":commit,"source_grammar_sha256":{"lexer":digest(generated/"SysMLv2Lexer.g4"),"parser":digest(generated/"SysMLv2Parser.g4")},"source_repository":"https://github.com/daltskin/sysml-v2-grammar","source_tag":tag}; (generated/"manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True)+"\n", encoding="utf-8")'

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

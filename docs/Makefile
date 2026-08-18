PYTHON ?= python
SOURCE := source
BUILD := build
MASTER_DOC ?= index_en
LANGUAGE ?= en
OUTPUT ?= $(BUILD)/html/en
export PY_SYSMLV2_MASTER_DOC := $(MASTER_DOC)

.PHONY: build build_en build_zh html_en html_zh check clean

build:
	$(PYTHON) -m sphinx -b html -W --keep-going -D language=$(LANGUAGE) $(SOURCE) $(OUTPUT)

build_en:
	$(MAKE) build MASTER_DOC=index_en LANGUAGE=en OUTPUT=$(BUILD)/html/en

build_zh:
	$(MAKE) build MASTER_DOC=index_zh LANGUAGE=zh_CN OUTPUT=$(BUILD)/html/zh

html_en: build_en

html_zh: build_zh

check: build_en build_zh

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('$(BUILD)', ignore_errors=True)"

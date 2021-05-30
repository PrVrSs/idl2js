SHELL := /usr/bin/env bash

ANTLR4 := java -jar antlr-4.9.2-complete.jar
PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: unit
unit:
	poetry run pytest -v \
		-vv \
		--cov=idl2js \
		--capture=no \
		--cov-report=term-missing \
 		--cov-config=.coveragerc \

.PHONY: mypy
mypy:
	poetry run mypy idl2js

.PHONY: lint
lint:
	poetry run pylint idl2js

.PHONY: grammar
grammar:
	$(ANTLR4) -no-listener \
		-visitor -Dlanguage=Python3 \
		-o $(PROJECT_DIR)/idl2js/webidl/generated \
		$(PROJECT_DIR)/grammar/WebIDLParser.g4 $(PROJECT_DIR)/grammar/WebIDLLexer.g4

test: mypy lint unit

.PHONY: unit mypy lint grammar

SHELL := /usr/bin/env bash

ANTLR4 := java -jar antlr-4.10.1-complete.jar
PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


unit:
	poetry run pytest


mypy:
	poetry run mypy idl2js


lint:
	poetry run pylint idl2js


grammar:
	$(ANTLR4) -no-listener \
		-visitor -Dlanguage=Python3 \
		-o $(PROJECT_DIR)/idl2js/webidl/generated \
		$(PROJECT_DIR)/grammar/WebIDLParser.g4 $(PROJECT_DIR)/grammar/WebIDLLexer.g4


test: mypy lint unit
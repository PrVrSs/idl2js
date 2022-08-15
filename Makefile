.PHONY: unit mypy lint grammar

SHELL := /usr/bin/env bash


unit:
	poetry run pytest


mypy:
	poetry run mypy idl2js


lint:
	poetry run pylint idl2js


test: mypy lint unit
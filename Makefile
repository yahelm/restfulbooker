.EXPORT_ALL_VARIABLES:
include makes/py.mk
include makes/test.mk

-include makes/local.mk

.PHONY: help
help: py/help test/help

.DEFAULT_GOAL := help
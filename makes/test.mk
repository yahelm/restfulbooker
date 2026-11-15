.EXPORT_ALL_VARIABLES:

.PHONY: test/help
test/help:
	@echo "Test targets:"
	@echo "  test/unit        - Run unit tests"
	@echo "  test/api         - Run API tests"
	@echo "  test/all         - Run unit tests, then API tests"

.PHONY: test/unit
test/unit:
	uv run pytest tests/unit --skip-healthcheck $(opts)

.PHONY: test/api
test/api:
	uv run pytest tests/api -n auto --junitxml=reports/junit.xml $(opts)

.PHONY: test/all
test/all: test/unit test/api

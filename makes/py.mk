.EXPORT_ALL_VARIABLES:

.PHONY: py/help
py/help:
	@echo "Python targets:"
	@echo "  py/install       - Install project dependencies"
	@echo "  py/fmt           - Format code"
	@echo "  py/lint/ruff     - Lint code with ruff"
	@echo "  py/lint/mypy     - Type check code with mypy"
	@echo "  py/lint          - Lint code (ruff+mypy)"


.PHONY: py/install
py/install:
	uv lock --check
	uv sync --frozen

.PHONY: py/fmt
py/fmt:
	uv run ruff format .
	uv run ruff check . --fix

.PHONY: py/lint/ruff
py/lint/ruff:
	uv run ruff check .
	uv run ruff format --check --diff .

.PHONY: py/lint/mypy
py/lint/mypy:
	uv run mypy

.PHONY: py/lint
py/lint: py/lint/ruff py/lint/mypy


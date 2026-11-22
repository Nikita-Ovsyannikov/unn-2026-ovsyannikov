.PHONY: build install ruff-cs-check ruff-cs-fix ruff-linter-check ruff-linter-fix mypy-check test check

build:
	docker build -t unn-2026-ovsyannikov .

test:
	uv run python -m unittest discover -s tests -v

check: ruff-cs-check ruff-linter-check mypy-check test

install:
	uv sync --locked --group dev

ruff-cs-check:
	uv run ruff format --check .

ruff-cs-fix:
	uv run ruff format .

ruff-linter-check:
	uv run ruff check .

ruff-linter-fix:
	uv run ruff check --fix .

mypy-check:
	uv run mypy
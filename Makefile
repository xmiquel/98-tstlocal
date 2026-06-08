# Quality gate commands for 98-tstlocal
# Spec: openspec/changes/dev-tooling/specs/python-toolchain/spec.md (Makefile Targets requirement)
# All targets delegate to `uv run`; `make ci` mirrors the local portion of .github/workflows/ci.yml

# Dev server defaults — override via environment or `make run HOST=127.0.0.1 PORT=9000`
HOST ?= 0.0.0.0
PORT ?= 8000

.PHONY: help test lint format format-check typecheck lock-check ci run

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

test:  ## Run pytest
	uv run pytest

lint:  ## Run ruff check
	uv run ruff check .

format:  ## Run ruff format (in-place)
	uv run ruff format .

format-check:  ## Check formatting without modifying
	uv run ruff format --check .

typecheck:  ## Run mypy
	uv run mypy .

lock-check:  ## Verify lockfile is in sync
	uv lock --check

# Mirrors .github/workflows/ci.yml in the same step order (CI-infra steps skipped).
run:  ## Start the uvicorn dev server with hot-reload
	uv run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

ci:  ## Run all local quality checks
	uv sync --frozen
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
	uv run pytest
	uv lock --check

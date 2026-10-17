.DEFAULT_GOAL := help
.PHONY: help check fmt lint typecheck test scripts

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

# No loops in this file: a loop's exit code is only its last pass, which
# once let a failing folder pass on Playthroughd (docs/lessons.md). Each
# target is one command per line, and make stops at the first that fails.

check: lint typecheck test scripts ## Everything CI runs. Run this before you push.
	@echo "All checks passed."

fmt: ## Format everything in place
	uv run ruff format .
	uv run ruff check --fix .

lint: ## Formatting and lint, without changing files
	uv run ruff format --check .
	uv run ruff check .

typecheck: ## mypy --strict over src and tests
	uv run mypy

test: ## The test suite (no camera, no GPU needed)
	uv run pytest

scripts: ## The CI scripts themselves still parse
	bash -n .github/scripts/lessons.sh
	bash -n .github/scripts/pipefail.sh
	.github/scripts/pipefail.sh

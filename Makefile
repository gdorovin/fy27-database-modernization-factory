.PHONY: help install install-dev format format-check lint typecheck test test-fast \
        validate validate-repo validate-playbook validate-skills validate-agents \
        scenarios gate clean

PY ?= python
PIP ?= $(PY) -m pip

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	$(PIP) install -e .

install-dev: ## Install the package with development tooling
	$(PIP) install -e ".[dev]"

format: ## Apply formatting
	$(PY) -m ruff format src tests scripts
	$(PY) -m ruff check --fix src tests scripts

format-check: ## Verify formatting without writing
	$(PY) -m ruff format --check src tests scripts

lint: ## Lint
	$(PY) -m ruff check src tests scripts

typecheck: ## Static type check
	$(PY) -m mypy

test: ## Full test suite
	$(PY) -m pytest

test-fast: ## Test suite excluding slow tests
	$(PY) -m pytest -m "not slow"

validate-repo: ## Repository structure and safety checks
	$(PY) -m dbmodernize.cli validate-repo

validate-playbook: ## Validate the default playbook
	$(PY) -m dbmodernize.cli validate-playbook playbooks/default

validate-skills: ## Validate every Agent Skill
	$(PY) -m dbmodernize.cli validate-skill .github/skills

validate-agents: ## Validate every agent definition
	$(PY) -m dbmodernize.cli validate-agent .github/agents

scenarios: ## Run every scenario against its committed expectations
	$(PY) -m dbmodernize.cli validate-scenario scenarios

validate: validate-repo validate-playbook validate-skills validate-agents scenarios ## All deterministic validators

gate: format-check lint typecheck test validate ## The full merge gate

clean: ## Remove build and cache artifacts
	$(PY) scripts/clean.py

#!/usr/bin/env -S make -f

MAKEFLAGS += --warn-undefined-variable
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --silent

-include Makefile.*

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := help

help: Makefile  ## Show help
	for makefile in $(MAKEFILE_LIST)
	do
		@echo "$${makefile}"
		@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' "$${makefile}" | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'
	done


# =============================================================================
# Common
# =============================================================================
install:  ## Install the app locally
	poetry install --no-root
.PHONY: install

init:  ## Initialize project repository
	pre-commit autoupdate
	pre-commit install --install-hooks --hook-type pre-commit --hook-type commit-msg
.PHONY: init

run:  ## Run development server
	cd testproj && \
		poetry run python manage.py runserver \
			$$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: run


# =============================================================================
# CI
# =============================================================================
ci: lint scan test  ## Run CI tasks
.PHONY: ci

generate:  ## Autogenerate stuffs

.PHONY: generate

format:  ## Run autoformatters
	poetry run ruff check --fix .
	poetry run black .
.PHONY: format

lint:  ## Run all linters
	poetry run ruff check .
	poetry run black --check .
	poetry run mypy --show-error-codes --pretty .
.PHONY: lint

scan:  ## Run all scans
	checkov --quiet --directory .
.PHONY: scan

test:  ## Run tests
	poetry run pytest
.PHONY: test

docs:  ## Generate dev documents

.PHONY: docs


# =============================================================================
# Handy Scripts
# =============================================================================
clean:  ## Remove temporary files
	rm -rf .mypy_cache/ .pytest_cache/ .ruff-cache/ htmlcov/ .coverage coverage.xml report.xml
	find . -path '*/__pycache__*' -delete
	find . -path "*.log*" -delete
.PHONY: clean

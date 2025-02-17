#!/usr/bin/env -S make -f

MAKEFLAGS += --warn-undefined-variable
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --silent

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
.DEFAULT_GOAL := help

help: Makefile  ## Show help
	@grep -E '(^[a-zA-Z_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'


# =============================================================================
# Common
# =============================================================================
install:  ## Install deps
	uv python install
	uv sync --frozen --all-extras
	pre-commit install --install-hooks
.PHONY: install

update:  ## Update deps and tools
	uv sync --upgrade --all-extras
	pre-commit autoupdate
.PHONY: update

run:  ## Run development server
	uv run python manage.py runserver \
		$$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: run

serve-docs:  ## Serve dev documents
	uv run mkdocs serve \
		--dev-addr $$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: serve-docs

makemessages:  ## Update translation files
	uv run python manage.py makemessages --all --ignore 'examples/*' --no-obsolete
.PHONY: makemessages

compilemessages:  ## Compile translation files
	uv run python manage.py compilemessages --ignore 'examples/*'
.PHONY: compilemessages


# =============================================================================
# CI
# =============================================================================
ci: lint test  ## Run CI tasks
.PHONY: ci

format:  ## Run autoformatters
	uv run ruff check --fix .
	uv run ruff format .
.PHONY: format

lint:  ## Run all linters
	uv run ruff check .
	uv run mypy --show-error-codes --pretty .
.PHONY: lint

test:  ## Run tests
	uv run pytest
	uv run coverage html
.PHONY: test

docs:  ## Generate dev documents
	uv run mkdocs build
.PHONY: docs


# =============================================================================
# Handy Scripts
# =============================================================================
shell:  ## Run test project' Django shell
	uv run python manage.py shell
.PHONY: shell

migration:  ## Make migrations
	uv run python manage.py makemigrations
.PHONY: migration

migrate:  ## Apply migrations
	uv run python manage.py migrate
.PHONY: migration

superuser:  ## Create superuser (ID/PW: admin/admin)
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@admin.admin DJANGO_SUPERUSER_PASSWORD=admin \
		uv run python manage.py createsuperuser --no-input
.PHONY: superuser

clean:  ## Remove temporary files
	rm -rf .mypy_cache/ .pytest_cache/ .ruff-cache/ htmlcov/ .coverage coverage.xml report.xml
	find . -path '*/__pycache__*' -delete
	find . -path "*.log*" -delete
.PHONY: clean

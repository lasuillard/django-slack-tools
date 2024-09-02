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
install:  ## Install deps
	POETRY_VIRTUALENVS_IN_PROJECT=1 poetry install --no-root
	pre-commit install --install-hooks
.PHONY: install

update:  ## Update deps and tools
	poetry update
	pre-commit autoupdate
.PHONY: update

run:  ## Run development server
	poetry run python manage.py runserver \
		$$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: run

serve-docs:  ## Serve dev documents
	poetry run mkdocs serve \
		--dev-addr $$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: serve-docs


# =============================================================================
# CI
# =============================================================================
ci: lint test  ## Run CI tasks
.PHONY: ci

format:  ## Run autoformatters
	poetry run ruff check --fix .
	poetry run ruff format .
.PHONY: format

lint:  ## Run all linters
	poetry run ruff check .
	poetry run mypy --show-error-codes --pretty .
.PHONY: lint

test:  ## Run tests
	poetry run pytest
	poetry run coverage html
.PHONY: test

docs:  ## Generate dev documents
	poetry run mkdocs build
.PHONY: docs


# =============================================================================
# Handy Scripts
# =============================================================================
shell:  ## Run test project' Django shell
	poetry run python manage.py shell
.PHONY: shell

migration:  ## Make migrations
	poetry run python manage.py makemigrations
.PHONY: migration

migrate:  ## Apply migrations
	poetry run python manage.py migrate
.PHONY: migration

superuser:  ## Create superuser (ID/PW: admin/admin)
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@admin.admin DJANGO_SUPERUSER_PASSWORD=admin \
		poetry run python manage.py createsuperuser --no-input
.PHONY: superuser

clean:  ## Remove temporary files
	rm -rf .mypy_cache/ .pytest_cache/ .ruff-cache/ htmlcov/ .coverage coverage.xml report.xml
	find . -path '*/__pycache__*' -delete
	find . -path "*.log*" -delete
.PHONY: clean

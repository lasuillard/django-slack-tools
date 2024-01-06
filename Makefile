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
	poetry run python manage.py runserver \
		$$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')
.PHONY: run


# =============================================================================
# CI
# =============================================================================
ci: lint scan test  ## Run CI tasks
.PHONY: ci

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

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
	uv sync --frozen
.PHONY: install

run:  ## Run development server
	docker compose up -d
	uv run python manage.py runserver \
		$$([ ! -z "$${CONTAINER:-}" ] && echo '0.0.0.0:8000' || echo '127.0.0.1:8000')

	docker compose down
.PHONY: run

run-celery-worker:
	uv run celery -A todo.celery_app worker -l DEBUG
.PHONY: run-celery-worker

run-celery-beat:
	uv run celery -A todo.celery_app beat -l DEBUG
.PHONY: run-celery-beat


# =============================================================================
# Handy Scripts
# =============================================================================
shell:  ## Run test project' Django shell
	uv run python manage.py shell
.PHONY: shell

setup: install migrate superuser  ## Set up the example project
	uv run python manage.py loaddata ./dump.json
.PHONY: setup

migrate:  ## Apply migrations
	uv run python manage.py migrate
.PHONY: migration

superuser:  ## Create superuser (ID/PW: admin/admin)
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@admin.admin DJANGO_SUPERUSER_PASSWORD=admin \
		uv run python manage.py createsuperuser --no-input
.PHONY: superuser

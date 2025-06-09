.PHONY: help install test lint format type-check clean build publish dev-setup

# Default target
help:
	@echo "Simple Enum Generator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies with uv"
	@echo "  dev-setup   Full development setup (install + pre-commit)"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run ruff linting"
	@echo "  format      Run ruff formatting"
	@echo "  type-check  Run mypy type checking"
	@echo "  test        Run pytest tests"
	@echo "  check-all   Run all code quality checks"
	@echo ""
	@echo "Building:"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build distribution packages"
	@echo "  publish     Publish to PyPI (use with caution)"
	@echo ""
	@echo "Development:"
	@echo "  install-hooks  Install pre-commit hooks"
	@echo "  update-deps    Update dependencies"

# Installation
install:
	uv sync --all-extras --dev

dev-setup: install install-hooks
	@echo "✅ Development environment ready!"

install-hooks:
	uv run pre-commit install

# Code Quality
lint:
	uv run ruff check .

format:
	uv run ruff format .

type-check:
	uv run mypy simple_enum_generator

test:
	uv run pytest

test-cov:
	uv run pytest --cov=simple_enum_generator --cov-report=html --cov-report=term-missing

test-verbose:
	uv run pytest -v

check-all: lint type-check test
	@echo "✅ All checks passed!"

# Building
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	uv build

publish: build
	@echo "⚠️  This will publish to PyPI. Are you sure? (Ctrl+C to cancel)"
	@read -p "Press Enter to continue..."
	uv run twine upload dist/*

# Development helpers
update-deps:
	uv lock --upgrade

run-example:
	@echo "Running example in example/ directory..."
	cd example && python -c "from models import *; print('✅ Example models loaded successfully')"

# Local testing with Docker PostgreSQL
test-docker:
	@echo "Starting PostgreSQL container for testing..."
	docker run --rm -d \
		--name postgres-test \
		-e POSTGRES_PASSWORD=test \
		-e POSTGRES_DB=test_db \
		-p 5432:5432 \
		postgres:15
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "Running tests..."
	DATABASE_URL=postgresql://postgres:test@localhost:5432/test_db uv run pytest
	@echo "Stopping PostgreSQL container..."
	docker stop postgres-test

# Documentation
docs-serve:
	@echo "📖 README.md contains all documentation"
	@echo "🌐 View online: https://github.com/yourusername/simple-enum-generator"

# Release helpers
tag-release:
	@echo "Current version: $$(grep version pyproject.toml | head -1 | cut -d'"' -f2)"
	@read -p "Enter new version (e.g., 1.0.1): " version; \
	sed -i '' "s/version = \".*\"/version = \"$$version\"/" pyproject.toml; \
	sed -i '' "s/__version__ = \".*\"/__version__ = \"$$version\"/" simple_enum_generator/__init__.py; \
	git add pyproject.toml simple_enum_generator/__init__.py; \
	git commit -m "chore: bump version to $$version"; \
	git tag "v$$version"; \
	echo "✅ Tagged version $$version. Push with: git push origin main --tags"

# Utility commands
check-deps:
	uv tree

security-check:
	uv run pip-audit

# Quick development workflow
quick-check: format lint type-check test
	@echo "🚀 Quick check complete - ready to commit!"

# Full CI simulation
ci-local: clean install check-all build
	@echo "🎉 Local CI simulation complete!"
.PHONY: help install test lint typecheck ci clean coverage coverage-html coverage-report build publish publish-test version run format check-build bump-patch bump-minor bump-major release-patch release-minor release-major test-verbose test-coverage test-quick coverage-check ci-full lint-fix

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies using uv"
	@echo "  make run          - Run the virtual shell"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run ruff linting"
	@echo "  make format       - Format code with ruff"
	@echo "  make typecheck     - Run mypy type checking"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make coverage-html - Generate HTML coverage report"
	@echo "  make coverage-report - Show coverage report in terminal"
	@echo "  make ci            - Run all CI checks (lint, typecheck, test)"
	@echo "  make clean         - Clean up cache and temporary files"
	@echo "  make build        - Build distribution packages"
	@echo "  make publish-test - Publish to TestPyPI"
	@echo "  make publish      - Publish to PyPI"
	@echo "  make version      - Show current version"

install:
	uv sync --all-extras --dev

test:
	uv run pytest

test-verbose:
	uv run pytest -v

test-coverage:
	uv run pytest --cov=chuk_virtual_shell --cov-report=term-missing

coverage:
	uv run pytest --cov=chuk_virtual_shell --cov-report=term-missing --cov-report=html --cov-report=term:skip-covered

coverage-html:
	uv run pytest --cov=chuk_virtual_shell --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"
	@echo "Opening coverage report..."
	@python -c "import webbrowser; webbrowser.open('htmlcov/index.html')" 2>/dev/null || open htmlcov/index.html 2>/dev/null || echo "Please open htmlcov/index.html manually"

coverage-report:
	uv run pytest --cov=chuk_virtual_shell --cov-report=term-missing --cov-report=term:skip-covered --cov-fail-under=80
	@echo ""
	@echo "Coverage summary:"
	@uv run coverage report --precision=2

lint:
	uv run ruff check chuk_virtual_shell

lint-fix:
	uv run ruff check chuk_virtual_shell --fix --unsafe-fixes

typecheck:
	uv run mypy chuk_virtual_shell

ci: lint typecheck test-quick coverage-check
	@echo "✅ All CI checks passed!"

ci-full: lint typecheck coverage-report
	@echo "✅ All CI checks with coverage passed!"

test-quick:
	uv run pytest -q --tb=short

coverage-check:
	@echo "Running coverage check (minimum 65%)..."
	@uv run pytest --cov=chuk_virtual_shell --cov-fail-under=65 --cov-report= -q
	@echo "✅ Coverage check passed (>65%)"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true

# Run the application
run:
	uv run virtual-shell

# Format code
format:
	uv run ruff format chuk_virtual_shell

# Build distribution packages
build: clean
	uv build

# Check if package builds correctly
check-build: build
	@echo "Checking wheel contents..."
	@python -m zipfile -l dist/*.whl | head -20
	@echo ""
	@echo "Checking sdist contents..."
	@tar -tzf dist/*.tar.gz | head -20

# Publish to TestPyPI (for testing)
publish-test: build
	@echo "Publishing to TestPyPI..."
	@if [ ! -d "dist" ] || [ -z "$$(ls -A dist 2>/dev/null)" ]; then \
		echo "Error: No distribution files found. Run 'make build' first."; \
		exit 1; \
	fi
	@last_build=$$(ls -t dist/*.tar.gz dist/*.whl 2>/dev/null | head -n 2); \
	if [ -z "$$last_build" ]; then \
		echo "Error: No valid distribution files found."; \
		exit 1; \
	fi; \
	echo "Uploading to TestPyPI: $$last_build"; \
	twine upload --repository testpypi $$last_build
	@echo "Test publish complete."

# Publish to PyPI (production)
publish: build
	@echo "Publishing package..."
	@if [ ! -d "dist" ] || [ -z "$$(ls -A dist 2>/dev/null)" ]; then \
		echo "Error: No distribution files found. Run 'make build' first."; \
		exit 1; \
	fi
	@last_build=$$(ls -t dist/*.tar.gz dist/*.whl 2>/dev/null | head -n 2); \
	if [ -z "$$last_build" ]; then \
		echo "Error: No valid distribution files found."; \
		exit 1; \
	fi; \
	echo "Uploading: $$last_build"; \
	twine upload $$last_build
	@echo "Publish complete."

# Version management
version:
	@grep "^version" pyproject.toml | cut -d'"' -f2

bump-patch:
	@echo "Current version: $$(make version)"
	@echo "Bumping patch version..."
	@current=$$(make version); \
	new=$$(echo $$current | awk -F. '{print $$1"."$$2"."$$3+1}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && \
	rm pyproject.toml.bak && \
	echo "New version: $$new"

bump-minor:
	@echo "Current version: $$(make version)"
	@echo "Bumping minor version..."
	@current=$$(make version); \
	new=$$(echo $$current | awk -F. '{print $$1"."$$2+1".0"}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && \
	rm pyproject.toml.bak && \
	echo "New version: $$new"

bump-major:
	@echo "Current version: $$(make version)"
	@echo "Bumping major version..."
	@current=$$(make version); \
	new=$$(echo $$current | awk -F. '{print $$1+1".0.0"}'); \
	sed -i.bak "s/version = \"$$current\"/version = \"$$new\"/" pyproject.toml && \
	rm pyproject.toml.bak && \
	echo "New version: $$new"

# Release workflow shortcuts
release-patch: bump-patch ci build
	@echo "Ready to release patch version $$(make version)"
	@echo "Run 'make publish' to upload to PyPI"

release-minor: bump-minor ci build
	@echo "Ready to release minor version $$(make version)"
	@echo "Run 'make publish' to upload to PyPI"

release-major: bump-major ci build
	@echo "Ready to release major version $$(make version)"
	@echo "Run 'make publish' to upload to PyPI"
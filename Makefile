.PHONY: help install test lint typecheck ci clean coverage coverage-html coverage-report

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies using uv"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run ruff linting"
	@echo "  make typecheck     - Run mypy type checking"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make coverage-html - Generate HTML coverage report"
	@echo "  make coverage-report - Show coverage report in terminal"
	@echo "  make ci            - Run all CI checks (lint, typecheck, test)"
	@echo "  make clean         - Clean up cache and temporary files"

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
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
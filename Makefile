# Makefile for Puter Python SDK

.PHONY: help install install-dev test test-all lint format clean build docs release
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy

help: ## Show this help message
	@echo "Puter Python SDK - Development Commands"
	@echo "======================================"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Environment

install: ## Install package for production
	$(PIP) install .

install-dev: ## Install package for development
	$(PIP) install -e .[dev]
	$(PYTHON) -m pre_commit install

setup-dev: ## Set up complete development environment
	$(PYTHON) scripts/setup_dev.py

##@ Code Quality

format: ## Format code with black and isort
	$(BLACK) puter/ tests/ examples/ scripts/ *.py
	$(ISORT) puter/ tests/ examples/ scripts/ *.py
	@echo "✅ Code formatted successfully"

lint: ## Run all linting tools
	$(FLAKE8) puter/ tests/ examples/ scripts/
	$(BLACK) --check puter/ tests/ examples/ scripts/ *.py
	$(ISORT) --check-only puter/ tests/ examples/ scripts/ *.py
	$(MYPY) puter/ --ignore-missing-imports
	@echo "✅ Linting completed successfully"

security: ## Run security checks
	$(PYTHON) -m bandit -r puter/ -f txt
	$(PYTHON) -m safety check
	@echo "✅ Security checks completed"

quality: lint security ## Run all quality checks

##@ Testing

test: ## Run unit tests
	$(PYTEST) tests/ -v --tb=short

test-unit: ## Run only unit tests
	$(PYTEST) tests/ -v -m "unit" --tb=short

test-integration: ## Run integration tests
	$(PYTEST) tests/ -v -m "integration" --tb=short

test-all: ## Run all tests with coverage
	$(PYTEST) tests/ -v --cov=puter --cov-report=html --cov-report=xml --cov-report=term-missing

test-fast: ## Run tests in parallel
	$(PYTEST) tests/ -n auto --tb=short

benchmark: ## Run performance benchmarks
	$(PYTEST) tests/benchmarks/ --benchmark-only --benchmark-json=benchmark-results.json

##@ Documentation

docs: ## Build documentation
	@mkdir -p docs_build
	cd docs && sphinx-build -b html . ../docs_build
	@echo "✅ Documentation built successfully"
	@echo "📖 Open docs_build/index.html to view"

docs-serve: docs ## Build and serve documentation locally
	cd docs_build && $(PYTHON) -m http.server 8000
	@echo "📖 Documentation server running at http://localhost:8000"

docs-clean: ## Clean documentation build
	rm -rf docs_build/

##@ Package Management

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned all build artifacts"

build: clean ## Build package
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*
	@echo "✅ Package built successfully"

##@ Release Management

version: ## Show current version
	@$(PYTHON) -c "import puter; print(f'Current version: {puter.__version__}')"

release: ## Create a new release (usage: make release VERSION=1.0.0)
ifndef VERSION
	@echo "❌ Error: VERSION is required"
	@echo "Usage: make release VERSION=1.0.0"
	@exit 1
endif
	$(PYTHON) scripts/release.py $(VERSION)

release-dry: ## Dry run release (usage: make release-dry VERSION=1.0.0)
ifndef VERSION
	@echo "❌ Error: VERSION is required"
	@echo "Usage: make release-dry VERSION=1.0.0"
	@exit 1
endif
	$(PYTHON) scripts/release.py $(VERSION) --dry-run

##@ Git Operations

git-setup: ## Set up git hooks and configuration
	git config core.hooksPath .githooks
	chmod +x .githooks/*
	@echo "✅ Git hooks configured"

pre-commit: ## Run pre-commit hooks
	$(PYTHON) -m pre_commit run --all-files

##@ Docker (if applicable)

docker-build: ## Build Docker image
	docker build -t puter-python-sdk .

docker-test: ## Run tests in Docker
	docker run --rm puter-python-sdk make test

##@ Utilities

deps-update: ## Update dependencies
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt

deps-security: ## Check for security vulnerabilities in dependencies
	$(PIP) install safety
	$(PYTHON) -m safety check

example: ## Run basic example
	$(PYTHON) examples/basic_chat.py

check: format lint test ## Run format, lint, and test (pre-commit simulation)

ci: clean install-dev lint test-all security build ## Run full CI pipeline locally

##@ Information

info: ## Show project information
	@echo "Puter Python SDK"
	@echo "================"
	@echo "Repository: https://github.com/CuzImSlymi/puter-python-sdk"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Pip: $(shell $(PIP) --version)"
	@echo ""
	@$(MAKE) version

deps: ## Show installed dependencies
	$(PIP) list

tree: ## Show project structure
	@command -v tree >/dev/null 2>&1 && tree -I '__pycache__|*.pyc|.git|venv|node_modules|.pytest_cache|.mypy_cache|htmlcov|build|dist|*.egg-info' || find . -type f -name "*.py" | grep -E "(puter|tests|examples)" | sort

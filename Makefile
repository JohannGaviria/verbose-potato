PYTHON=python3

# Colors for output
GREEN=\033[0;32m
BLUE=\033[0;34m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

.PHONY: \
	help \
	setup \
	up down logs clean \
	build-dev dev \
	build-test test test-unit test-integration test-e2e test-coverage \
	format lint check pre-commit

help: ## Show this help message
	@echo "$(YELLOW)=== Available Commands ===$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-22s$(NC) %s\n", $$1, $$2}'

# --- Setup ---

setup: ## Install development dependencies and git hooks
	@echo "$(BLUE)Installing project dependencies...$(NC)"
	poetry install

	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	poetry run pre-commit install

# --- Docker ---

up: ## Start development environment
	@echo "$(BLUE)Starting development containers...$(NC)"
	docker compose --profile dev up --build

down: ## Stop development and testing containers
	@echo "$(BLUE)Stopping containers...$(NC)"
	docker compose --profile dev --profile test down

logs: ## Follow container logs
	@echo "$(BLUE)Following container logs...$(NC)"
	docker compose logs -f

clean: ## Remove containers, volumes and local images
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker compose --profile dev --profile test down -v --rmi local

# --- Development ---

build-dev: ## Build development image
	@echo "$(BLUE)Building development image...$(NC)"
	docker compose build app-dev

dev: build-dev ## Start development container
	@echo "$(BLUE)Starting development container...$(NC)"
	docker compose --profile dev up app-dev

# --- Testing ---

build-test: ## Build testing image
	@echo "$(BLUE)Building testing image...$(NC)"
	docker compose build backend-test

test: build-test ## Run all tests
	@echo "$(BLUE)Running complete test suite...$(NC)"
	docker compose --profile test run --rm backend-test pytest tests

test-unit: ## Run unit tests (no Docker/Postgres/Redis required)
	@echo "$(BLUE)Running unit tests...$(NC)"
	poetry run pytest tests/unit -v

test-integration: build-test ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	docker compose --profile test run --rm backend-test pytest tests/integration -v

test-integration-no-db: ## Run integration tests that don't need Postgres/Redis
	@echo "$(BLUE)Running infra-free integration tests...$(NC)"
	poetry run pytest tests/integration -m "not db" -v

test-e2e: build-test ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	docker compose --profile test run --rm backend-test pytest tests/e2e -v

test-coverage: build-test ## Run all tests with a coverage report and enforce the threshold
	@echo "$(BLUE)Running test suite with coverage...$(NC)"
	docker compose --profile test run --rm backend-test \
		pytest tests \
		--cov=src \
		--cov-report=term-missing \
		--cov-fail-under=70

test-coverage-unit: ## Collect coverage data from unit tests only
	@echo "$(BLUE)Collecting unit test coverage...$(NC)"
	COVERAGE_FILE=tests/.coverage.unit poetry run pytest tests/unit --cov=src --cov-report=

test-coverage-integration: build-test ## Collect coverage data from integration tests only
	@echo "$(BLUE)Collecting integration test coverage...$(NC)"
	docker compose --profile test run --rm \
		-e COVERAGE_FILE=tests/.coverage.integration \
		backend-test pytest tests/integration --cov=src --cov-report=

test-coverage-e2e: build-test ## Collect coverage data from e2e tests only
	@echo "$(BLUE)Collecting e2e test coverage...$(NC)"
	docker compose --profile test run --rm \
		-e COVERAGE_FILE=tests/.coverage.e2e \
		backend-test pytest tests/e2e --cov=src --cov-report=

test-coverage-report: ## Combine collected coverage data (tests/.coverage.*) and enforce the threshold
	@echo "$(BLUE)Combining coverage data and checking threshold...$(NC)"
	poetry run coverage combine tests/
	poetry run coverage report --show-missing --fail-under=70

# --- Code Quality ---

format: ## Format and auto-fix code
	@echo "$(BLUE)Fixing lint issues...$(NC)"
	poetry run ruff check --fix .

	@echo "$(BLUE)Formatting code...$(NC)"
	poetry run ruff format .

lint: ## Run linting and type checking
	@echo "$(BLUE)Running Ruff...$(NC)"
	poetry run ruff check .

	@echo "$(BLUE)Running mypy...$(NC)"
	poetry run mypy .

check: ## Verify formatting, linting and typing
	@echo "$(BLUE)Checking formatting...$(NC)"
	poetry run ruff format --check .

	@echo "$(BLUE)Checking lint...$(NC)"
	poetry run ruff check .

	@echo "$(BLUE)Checking types...$(NC)"
	poetry run mypy .

pre-commit: ## Run all pre-commit hooks
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	poetry run pre-commit run --all-files

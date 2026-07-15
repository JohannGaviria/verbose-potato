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

test-unit: build-test ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	poetry run pytest tests/unit -v

test-integration: build-test ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	docker compose --profile test run --rm backend-test pytest tests/integrations -v

test-e2e: build-test ## Run end-to-end tests
	@echo "$(BLUE)Running end-to-end tests...$(NC)"
	docker compose --profile test run --rm backend-test pytest tests/e2e -v

test-coverage: build-test ## Run tests with coverage
	@echo "$(BLUE)Running test suite with coverage...$(NC)"
	docker compose --profile test run --rm backend-test \
		pytest tests \
		--cov=src \
		--cov-report=term-missing \

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

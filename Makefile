.PHONY: dev dev-build down logs test lint build clean migrate seed shell-be shell-fe help

# Default target
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start all services in development mode
	docker compose up -d

dev-build: ## Build and start all services
	docker compose up -d --build

down: ## Stop all services
	docker compose down

logs: ## Follow logs from all services
	docker compose logs -f

test: ## Run backend tests with pytest
	cd backend && pytest

lint: ## Run linters for backend and frontend
	cd backend && ruff check .
	cd frontend && npm run lint

build: ## Build production images
	docker compose -f docker-compose.yml -f docker-compose.prod.yml build

clean: ## Stop services and remove volumes
	docker compose down -v --remove-orphans

migrate: ## Run database migrations
	docker compose exec fastapi alembic upgrade head

seed: ## Seed database with sample data
	docker compose exec fastapi python -m scripts.seed_data

shell-be: ## Open a shell in the backend container
	docker compose exec fastapi bash

shell-fe: ## Open a shell in the frontend container
	docker compose exec frontend sh

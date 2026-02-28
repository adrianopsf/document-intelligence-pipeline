.PHONY: install dev run test lint format docker-up docker-down migrate help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync

dev: ## Install all dependencies (including dev)
	uv sync --all-extras

run: ## Run the API server locally
	uv run uvicorn docai.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=docai --cov-report=term-missing

lint: ## Run linter
	uv run ruff check src/ tests/

format: ## Format code
	uv run ruff format src/ tests/

typecheck: ## Run type checker
	uv run mypy src/

migrate: ## Run database migrations
	uv run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create msg="description")
	uv run alembic revision --autogenerate -m "$(msg)"

docker-up: ## Start all services with Docker Compose
	docker-compose up --build -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## Tail Docker logs
	docker-compose logs -f app

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov dist build *.egg-info

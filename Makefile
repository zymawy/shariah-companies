# Makefile for Argaam Shariah Companies Scraper

.PHONY: help install test run api scheduler docker-build docker-up docker-down clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html

run: ## Run the scraper once
	python main.py --export-format all

run-tasi: ## Run scraper for TASI market only
	python main.py --market تاسي --export-format all

run-nomu: ## Run scraper for Nomu market only
	python main.py --market نمو --export-format all

api: ## Start the API server
	python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

api-prod: ## Start the API server in production mode
	python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

scheduler: ## Start the scheduler
	python -m src.scheduler.scheduler --interval 24

scheduler-once: ## Run scheduler once
	python -m src.scheduler.scheduler --run-once

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-scrape: ## Run scraper in Docker (once)
	docker-compose run --rm scraper

clean: ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf build dist *.egg-info

db-init: ## Initialize database
	python -c "from src.database.models import DatabaseManager; db = DatabaseManager(); print('Database initialized')"

db-reset: ## Reset database (WARNING: deletes all data)
	rm -f data/shariah_companies.db
	python -c "from src.database.models import DatabaseManager; db = DatabaseManager(); print('Database reset complete')"

dirs: ## Create necessary directories
	mkdir -p data/raw data/processed data/exports logs

env-example: ## Copy example environment file
	cp .env.example .env

setup: dirs env-example install db-init ## Complete setup

format: ## Format code with black
	black src/ tests/ --line-length 100

lint: ## Lint code with flake8
	flake8 src/ tests/ --max-line-length 100

requirements-freeze: ## Freeze current requirements
	pip freeze > requirements-frozen.txt

docker-shell: ## Open shell in Docker container
	docker-compose exec app /bin/bash

docker-clean: ## Clean Docker resources
	docker-compose down -v
	docker system prune -f
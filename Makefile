# Makefile for Qwen3-VL Inference Server

.PHONY: help install build up down restart logs health clean backup restore test dev prod

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(GREEN)Qwen3-VL Inference Server - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# Setup and Installation
install: ## Install Python dependencies locally
	@echo "$(GREEN)Installing dependencies...$(NC)"
	pip install -r requirements.txt

setup: ## Setup environment (create .env from template)
	@if [ ! -f .env ]; then \
		echo "$(GREEN)Creating .env file from template...$(NC)"; \
		cp .env.docker .env; \
		echo "$(YELLOW)Please edit .env file with your configuration$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists$(NC)"; \
	fi

# Docker Build
build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker-compose build

build-no-cache: ## Build Docker image without cache
	@echo "$(GREEN)Building Docker image (no cache)...$(NC)"
	docker-compose build --no-cache

# Docker Run
up: ## Start services in detached mode
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d

up-build: ## Build and start services
	@echo "$(GREEN)Building and starting services...$(NC)"
	docker-compose up -d --build

down: ## Stop and remove containers
	@echo "$(GREEN)Stopping services...$(NC)"
	docker-compose down

down-volumes: ## Stop and remove containers and volumes
	@echo "$(GREEN)Stopping services and removing volumes...$(NC)"
	docker-compose down -v

restart: ## Restart services
	@echo "$(GREEN)Restarting services...$(NC)"
	docker-compose restart

# Logs and Monitoring
logs: ## Show logs (follow mode)
	docker-compose logs -f

logs-tail: ## Show last 100 lines of logs
	docker-compose logs --tail=100

health: ## Check service health
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost:8000/api/health || (echo "$(RED)Service is unhealthy$(NC)" && exit 1)

ps: ## Show running containers
	docker-compose ps

stats: ## Show container resource usage
	docker stats qwen3-vl-server

gpu: ## Show GPU usage
	docker-compose exec qwen3-vl-server nvidia-smi

# Development
dev: ## Start in development mode
	@echo "$(GREEN)Starting in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build and start in development mode
	@echo "$(GREEN)Building and starting in development mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Stop development services
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production
prod: ## Start in production mode
	@echo "$(GREEN)Starting in production mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Build and start in production mode
	@echo "$(GREEN)Building and starting in production mode...$(NC)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production services
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Shell Access
shell: ## Open shell in running container
	docker-compose exec qwen3-vl-server bash

# Backup and Restore
backup: ## Create backup of volumes and configuration
	@echo "$(GREEN)Creating backup...$(NC)"
	@bash scripts/backup.sh

restore: ## Restore from backup (requires BACKUP_DIR variable)
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "$(RED)Please specify BACKUP_DIR: make restore BACKUP_DIR=./backups/qwen-backup-XXXXXX$(NC)"; \
		exit 1; \
	fi
	@bash scripts/restore.sh $(BACKUP_DIR)

# Cleaning
clean: ## Remove all containers, images, and volumes
	@echo "$(YELLOW)Warning: This will remove all containers, images, and volumes$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	docker-compose down -v
	docker rmi qwen3-vl-inference:latest qwen3-vl-inference:dev qwen3-vl-inference:prod 2>/dev/null || true

clean-cache: ## Clean Docker build cache
	docker builder prune -f

clean-all: ## Clean everything (containers, images, volumes, cache)
	@echo "$(YELLOW)Warning: This will remove EVERYTHING$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	$(MAKE) clean
	docker system prune -a --volumes -f

# Testing
test: ## Run tests (placeholder - implement your tests)
	@echo "$(YELLOW)No tests configured yet$(NC)"

test-api: ## Test API endpoints
	@echo "$(GREEN)Testing API endpoints...$(NC)"
	@curl -f http://localhost:8000/api/health && echo "$(GREEN)✓ Health endpoint OK$(NC)" || echo "$(RED)✗ Health endpoint failed$(NC)"
	@curl -f http://localhost:8000/docs && echo "$(GREEN)✓ Docs endpoint OK$(NC)" || echo "$(RED)✗ Docs endpoint failed$(NC)"

# Deployment
deploy-dev: setup build up ## Full deployment for development
	@echo "$(GREEN)Development deployment complete!$(NC)"
	@$(MAKE) health

deploy-prod: setup build-no-cache prod ## Full deployment for production
	@echo "$(GREEN)Production deployment complete!$(NC)"
	@$(MAKE) health

# Documentation
docs: ## Open API documentation in browser
	@echo "$(GREEN)Opening API documentation...$(NC)"
	@python -m webbrowser http://localhost:8000/docs 2>/dev/null || xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || echo "$(YELLOW)Please open http://localhost:8000/docs in your browser$(NC)"

# Version Info
version: ## Show version information
	@echo "$(GREEN)Version Information:$(NC)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(docker-compose --version)"
	@echo "Python: $$(python --version 2>&1)"
	@echo ""
	@echo "$(GREEN)Container Status:$(NC)"
	@docker-compose ps 2>/dev/null || echo "No containers running"

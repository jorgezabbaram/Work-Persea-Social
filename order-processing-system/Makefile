# Makefile for Order Processing System

.PHONY: help build up down logs clean test

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-logs: ## Start all services with logs
	docker-compose up

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-order: ## Show logs for order service
	docker-compose logs -f order-service

logs-inventory: ## Show logs for inventory service
	docker-compose logs -f inventory-service

logs-payment: ## Show logs for payment service
	docker-compose logs -f payment-service

logs-notification: ## Show logs for notification service
	docker-compose logs -f notification-service

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8001/health || echo "Order Service: DOWN"
	@curl -s http://localhost:8002/health || echo "Inventory Service: DOWN"
	@curl -s http://localhost:8003/health || echo "Payment Service: DOWN"
	@curl -s http://localhost:8004/health || echo "Notification Service: DOWN"

test-order: ## Run tests for order service
	cd order-service && poetry run pytest

test-all: ## Run tests for all services
	cd order-service && poetry run pytest
	cd inventory-service && poetry run pytest
	cd payment-service && poetry run pytest
	cd notification-service && poetry run pytest

dev-setup: ## Setup development environment
	@echo "Setting up development environment..."
	cd order-service && poetry install
	cd inventory-service && poetry install
	cd payment-service && poetry install
	cd notification-service && poetry install
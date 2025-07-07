.PHONY: help dev build test clean deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  dev     - Start development environment"
	@echo "  build   - Build Docker images"
	@echo "  test    - Run tests"
	@echo "  clean   - Clean up Docker containers and images"
	@echo "  deploy  - Deploy to production"
	@echo "  logs    - Show application logs"
	@echo "  shell   - Open shell in backend container"

# Development environment
dev:
	@echo "Starting development environment..."
	cp -n .env.example .env 2>/dev/null || true
	docker-compose up -d
	@echo "Services are running:"
	@echo "  Frontend: http://localhost:8080"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker-compose build

# Run tests
test:
	@echo "Running backend tests..."
	docker-compose exec backend python -m pytest
	@echo "Running frontend tests..."
	docker-compose exec frontend go test ./...

# Clean up Docker containers and images
clean:
	@echo "Cleaning up Docker containers and images..."
	docker-compose down -v
	docker system prune -f

# Show logs
logs:
	docker-compose logs -f

# Backend shell
shell:
	docker-compose exec backend bash

# Frontend shell
shell-frontend:
	docker-compose exec frontend sh

# Database shell
db-shell:
	docker-compose exec postgres psql -U user -d symptom_checker

# Run migrations
migrate:
	docker-compose exec backend python -m alembic upgrade head

# Create migration
migration:
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend python -m alembic revision --autogenerate -m "$$msg"

# Restart services
restart:
	docker-compose restart

# Stop services
stop:
	docker-compose stop

# Production deployment check
deploy-check:
	@echo "Checking deployment configuration..."
	@if [ ! -f render.yaml ]; then echo "render.yaml not found!"; exit 1; fi
	@echo "✓ render.yaml exists"
	@echo "✓ Ready for deployment"

# Install dependencies locally (for development without Docker)
install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && go mod download

# Run linting
lint:
	@echo "Running backend linting..."
	docker-compose exec backend flake8 app/
	docker-compose exec backend black --check app/
	@echo "Running frontend linting..."
	docker-compose exec frontend gofmt -l .

# Format code
format:
	@echo "Formatting backend code..."
	docker-compose exec backend black app/
	@echo "Formatting frontend code..."
	docker-compose exec frontend gofmt -w .

# Security scan
security:
	@echo "Running security scan..."
	docker-compose exec backend safety check
	docker-compose exec backend bandit -r app/

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8080/health || echo "Frontend health check failed"
	@curl -f http://localhost:8000/health || echo "Backend health check failed"

# Backup database
backup:
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U user symptom_checker > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Load test data
seed:
	@echo "Loading test data..."
	docker-compose exec backend python scripts/seed_data.py
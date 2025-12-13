# Makefile pour gérer l'environnement Docker

# Variables pour la gestion des environnements
ENV ?= development
FRONTEND_ENV ?= development

.PHONY: help build up down restart logs clean dev prod test configure-env

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Configuration des environnements
configure-env: ## Configurer l'environnement (dev, staging, prod, test)
	@echo "Configuring environment: $(ENV)"
	@cd search_api_solr && cp .env.$(ENV) .env
	@cd front && cp .env.$(FRONTEND_ENV) .env
	@echo "Environment configured successfully!"
	@echo "Backend environment: $(ENV)"
	@echo "Frontend environment: $(FRONTEND_ENV)"

# Développement
dev: ## Lancer l'environnement de développement
	@$(MAKE) configure-env ENV=development FRONTEND_ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build et lancer l'environnement de développement
	@$(MAKE) configure-env ENV=development FRONTEND_ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Arrêter l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Staging
staging: ## Lancer l'environnement de staging
	@$(MAKE) configure-env ENV=staging FRONTEND_ENV=staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml up

staging-build: ## Build et lancer l'environnement de staging
	@$(MAKE) configure-env ENV=staging FRONTEND_ENV=staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml up --build

staging-down: ## Arrêter l'environnement de staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml down

# Production
prod: ## Lancer l'environnement de production
	@$(MAKE) configure-env ENV=production FRONTEND_ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Build et lancer l'environnement de production
	@$(MAKE) configure-env ENV=production FRONTEND_ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## Arrêter l'environnement de production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Tests backend
test: ## Lancer les tests backend (environnement test)
	@$(MAKE) configure-env ENV=test FRONTEND_ENV=test
	docker-compose -f docker-compose.yml run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

test-dev: ## Lancer les tests en environnement de développement
	@$(MAKE) configure-env ENV=development FRONTEND_ENV=development
	docker-compose run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

test-staging: ## Lancer les tests en environnement de staging
	@$(MAKE) configure-env ENV=staging FRONTEND_ENV=staging
	docker-compose run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

test-prod: ## Lancer les tests en environnement de production (simulé)
	@$(MAKE) configure-env ENV=production FRONTEND_ENV=production
	docker-compose run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

# Commandes avec environnement personnalisé
run-dev: ## Lancer avec environnement personnalisé (ex: make run-dev ENV=staging)
	@$(MAKE) configure-env ENV=$(ENV) FRONTEND_ENV=$(FRONTEND_ENV)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

run-prod: ## Lancer production avec environnement personnalisé
	@$(MAKE) configure-env ENV=$(ENV) FRONTEND_ENV=$(FRONTEND_ENV)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configuration rapide
set-dev: ## Configurer pour le développement sans lancer
	@$(MAKE) configure-env ENV=development FRONTEND_ENV=development

set-staging: ## Configurer pour le staging sans lancer
	@$(MAKE) configure-env ENV=staging FRONTEND_ENV=staging

set-prod: ## Configurer pour la production sans lancer
	@$(MAKE) configure-env ENV=production FRONTEND_ENV=production

set-test: ## Configurer pour les tests sans lancer
	@$(MAKE) configure-env ENV=test FRONTEND_ENV=test

# Commandes générales
build: ## Build les images Docker
	docker-compose build

up: ## Démarrer les conteneurs
	docker-compose up -d

down: ## Arrêter les conteneurs
	docker-compose down

restart: ## Redémarrer les conteneurs
	docker-compose restart

logs: ## Voir les logs de tous les services
	docker-compose logs -f

logs-api: ## Voir les logs de l'API
	docker-compose logs -f api

logs-frontend: ## Voir les logs du frontend
	docker-compose logs -f frontend

# Tests CI

test-ci: ## CI-friendly tests: build a test image with dev deps and run pytest inside it
	# Build image with dev/test deps included
	docker build --build-arg INSTALL_DEV=true -t search_api_solr:test .
	# Run pytest inside the built image (overrides default CMD)
	docker run --rm search_api_solr:test pytest

test-cov: ## Lancer les tests avec couverture
	docker-compose exec api pytest --cov=app --cov-report=html

test-front: ## Lancer les tests E2E du frontend (Headless)
	# Ensure node modules and playwright browsers are installed, then run headless tests
	cd front && npm ci && npx playwright install --with-deps && npm run test:e2e

test-front-ui: ## Lancer les tests E2E du frontend avec UI
	# Ensure node modules and playwright browsers are installed, then run UI test runner
	cd front && npm ci && npx playwright install --with-deps && npm run test:e2e:ui

test-front-ci: ## CI-friendly: run frontend E2E inside Playwright Docker image (headless)
	# Build static frontend, serve it and run Playwright tests; we set CI empty so Playwright will reuse the existing server
	docker run --rm -v ${PWD}/front:/src -w /src mcr.microsoft.com/playwright:latest bash -lc "npm ci && npm run build && npx http-server build -p 3000 & CI= npx playwright test"

test-front-ci-ui: ## CI-friendly: run Playwright UI (note: running UI inside container may need additional setup)
	# This attempts to start the Playwright UI; containers have no X server by default.
	# We install xvfb and run the UI under a virtual framebuffer so browsers can start.
	# Note: UI mode still requires forwarding the UI port (9323) to the host.
	docker run --rm -v ${PWD}/front:/src -w /src -p 9323:9323 mcr.microsoft.com/playwright:latest bash -lc \
		"npm ci && npx playwright install --with-deps && apt-get update && apt-get install -y xvfb && \
		xvfb-run -s '-screen 0 1920x1080x24' npx playwright test --ui --project=chromium --reporter=list"

test-front-ci-ui-debug: ## Diagnostic: run Playwright container interactively to inspect failures
	# Starts a container and drops you into a shell inside /src so you can run commands interactively
	docker run --rm -it -v ${PWD}/front:/src -w /src mcr.microsoft.com/playwright:latest bash

build-playwright-image: ## Build a dedicated Playwright image with the frontend preinstalled
	docker build -f front/Dockerfile.playwright -t openedition_playwright:local .

test-front-ci-image: ## Run headless Playwright tests inside the prebuilt Playwright image
	# Build image (if needed), build static frontend, serve it and execute headless tests
	docker build -f front/Dockerfile.playwright -t openedition_playwright:local .
	docker run --rm openedition_playwright:local bash -lc "npm run build && npx http-server build -p 3000 & CI= npx playwright test"

test-front-ci-ui-image: ## Run Playwright UI inside prebuilt Playwright image (exposes 9323)
	# Builds an image that contains node_modules and browsers so playback is fast
	docker build -f front/Dockerfile.playwright -t openedition_playwright:local .
	# Run UI under Xvfb inside the container, build static site and expose port 9323 to host
	docker run --rm -p 9323:9323 openedition_playwright:local bash -lc "npm run build && npx http-server build -p 3000 & xvfb-run -s '-screen 0 1920x1080x24' npx playwright test --ui --project=chromium --reporter=list"


# Shell
shell-api: ## Accéder au shell de l'API
	docker-compose exec api bash

shell-frontend: ## Accéder au shell du frontend
	docker-compose exec frontend sh

# Nettoyage
clean: ## Nettoyer les conteneurs et volumes
	docker-compose down -v
	docker system prune -f

clean-all: ## Nettoyage complet (incluant les images)
	docker-compose down -v --rmi all
	docker system prune -af

# Utilitaires
ps: ## Lister les conteneurs en cours d'exécution
	docker-compose ps

stats: ## Voir les statistiques des conteneurs
	docker stats

health: ## Vérifier la santé des services
	@echo "=== API Health ==="
	@curl -f http://localhost:8007/docs > /dev/null 2>&1 && echo "✓ API is healthy" || echo "✗ API is down"
	@echo "\n=== Frontend Health ==="
	@curl -f http://localhost:${FRONTEND_PORT:-3009} > /dev/null 2>&1 && echo "✓ Frontend is healthy" || echo "✗ Frontend is down"
	@echo "\n=== Solr Health (distant) ==="
	@curl -f https://solrslave-sec.labocleo.org/solr/documents/admin/ping > /dev/null 2>&1 && echo "✓ Solr distant is healthy" || echo "✗ Solr distant is down"

# Installation
install: ## Installation initiale (build + up)
	@echo "Installation de l'environnement OpenEdition Search..."
	@echo "Note: Utilise Solr distant (https://solrslave-sec.labocleo.org/solr/documents)"
	@$(MAKE) configure-env ENV=development FRONTEND_ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✓ Installation terminée"
	@echo "API: http://localhost:8007"
	@echo "Frontend: http://localhost:${FRONTEND_PORT:-3009}"

install-prod: ## Installation en production
	@echo "Installation de l'environnement OpenEdition Search en production..."
	@$(MAKE) configure-env ENV=production FRONTEND_ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Installation production terminée"
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:80"


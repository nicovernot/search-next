# Makefile pour gérer l'environnement Docker

# Détection de la commande docker-compose (v1) ou docker compose (v2)
DOCKER_COMPOSE := $(shell docker compose version > /dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

# Variables pour la gestion des environnements
ENV ?= development
FRONTEND_ENV ?= development
POSTGRES_PORT ?= 5435
REDIS_PORT ?= 6376
API_PORT ?= 8003
FRONTEND_PORT ?= 3003

# Exposer les variables pour docker-compose
export POSTGRES_PORT
export REDIS_PORT
export API_PORT
export FRONTEND_PORT

.PHONY: help build up down restart logs clean dev prod test configure-env sync-env check-env

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Configuration des environnements avec la nouvelle approche centralisée
sync-env: ## Synchroniser l'environnement (dev, staging, prod, test)
	@echo "Synchronizing environment: $(ENV)"
	@./scripts/sync_env.sh $(ENV)
	@echo "Environment synchronized successfully!"
	@echo "Backend: search_api_solr/.env.local"
	@echo "Frontend: front/.env.local"

check-env: ## Vérifier la configuration d'environnement
	@./scripts/check_env_setup.sh

# Configuration des environnements (ancienne méthode - dépréciée)
configure-env: ## Configurer l'environnement (dev, staging, prod, test) - DEPRECATED
	@echo "WARNING: This method is deprecated. Use 'make sync-env' instead."
	@echo "Configuring environment: $(ENV)"
	@cd search_api_solr && cp .env.$(ENV) .env
	@cd front && cp .env.$(FRONTEND_ENV) .env.local
	@echo "Environment configured successfully!"
	@echo "Backend environment: $(ENV)"
	@echo "Frontend environment: $(FRONTEND_ENV)"

# Développement
dev: ## Lancer l'environnement de développement
	@$(MAKE) sync-env ENV=development
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build et lancer l'environnement de développement
	@$(MAKE) sync-env ENV=development
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Arrêter l'environnement de développement
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml down

# Staging
staging: ## Lancer l'environnement de staging
	@$(MAKE) sync-env ENV=staging
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.staging.yml up

staging-build: ## Build et lancer l'environnement de staging
	@$(MAKE) sync-env ENV=staging
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.staging.yml up --build

staging-down: ## Arrêter l'environnement de staging
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.staging.yml down

# Production
prod: ## Lancer l'environnement de production
	@$(MAKE) sync-env ENV=production
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Build et lancer l'environnement de production
	@$(MAKE) sync-env ENV=production
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## Arrêter l'environnement de production
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml down

# Tests backend
test: ## Lancer les tests backend dans le container (recommandé)
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm api sh -c "pip install -r requirements.txt -r requirements-dev.txt > /dev/null 2>&1 && pytest -v"

test-cov: ## Lancer les tests avec couverture dans le container
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm api pytest --cov=app --cov-report=html --cov-report=term -v

test-local: ## Lancer les tests en local (nécessite les dépendances installées)
	@$(MAKE) sync-env ENV=test
	cd search_api_solr && python -m pytest -v

test-ci: ## Lancer les tests pour CI/CD (dans container, sortie XML)
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml run --rm api pytest --junitxml=test-results.xml -v

# Tests Frontend
test-front: ## Lancer les tests E2E Playwright (headless)
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) up -d api frontend
	@sleep 5
	cd front && npx playwright test --reporter=list
	$(DOCKER_COMPOSE) down

test-front-ui: ## Lancer les tests E2E Playwright avec UI
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) up -d api frontend
	@sleep 5
	cd front && npx playwright test --ui
	$(DOCKER_COMPOSE) down



test-front-ci: ## Tests E2E dans container Playwright (CI/CD) - 100% containerisé
	@$(MAKE) sync-env ENV=test
	$(DOCKER_COMPOSE) up -d api frontend
	@echo "Waiting for services to be ready..."
	@sleep 15
	docker run --rm --network search-next_search-next_network \
		-v $(PWD)/front:/app -w /app \
		-e BASE_URL=http://frontend:3000 \
		-e CI=true \
		mcr.microsoft.com/playwright:v1.59.1-noble \
		sh -c "npm install --legacy-peer-deps --silent && npx playwright test --reporter=list --project=chromium"
	$(DOCKER_COMPOSE) down

# Tests complets
test-all: ## Lancer tous les tests (backend + frontend)
	@echo "=== Tests Backend ==="
	@$(MAKE) test
	@echo ""
	@echo "=== Tests Frontend E2E ==="
	@$(MAKE) test-front

test-prod: ## Lancer les tests en environnement de production (simulé)
	@$(MAKE) sync-env ENV=production
	$(DOCKER_COMPOSE) run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

# Commandes avec environnement personnalisé
run-dev: ## Lancer avec environnement personnalisé (ex: make run-dev ENV=staging)
	@$(MAKE) sync-env ENV=$(ENV)
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up

run-prod: ## Lancer production avec environnement personnalisé
	@$(MAKE) sync-env ENV=$(ENV)
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configuration rapide
set-dev: ## Configurer pour le développement sans lancer
	@$(MAKE) sync-env ENV=development

set-staging: ## Configurer pour le staging sans lancer
	@$(MAKE) sync-env ENV=staging

set-prod: ## Configurer pour la production sans lancer
	@$(MAKE) sync-env ENV=production

set-test: ## Configurer pour les tests sans lancer
	@$(MAKE) sync-env ENV=test

# Commandes générales
build: ## Build les images Docker
	$(DOCKER_COMPOSE) build

up: ## Démarrer les conteneurs
	$(DOCKER_COMPOSE) up -d

down: ## Arrêter les conteneurs
	$(DOCKER_COMPOSE) down

restart: ## Redémarrer les conteneurs
	$(DOCKER_COMPOSE) restart

logs: ## Voir les logs de tous les services
	$(DOCKER_COMPOSE) logs -f

logs-api: ## Voir les logs de l'API
	$(DOCKER_COMPOSE) logs -f api

logs-frontend: ## Voir les logs du frontend
	$(DOCKER_COMPOSE) logs -f frontend

# Gestion des environnements (nouvelle approche)

env-check: ## Vérifier la configuration d'environnement
	@$(MAKE) check-env

env-sync: ## Synchroniser l'environnement courant
	@$(MAKE) sync-env ENV=$(ENV)

env-list: ## Lister les fichiers d'environnement disponibles
	@echo "Available environment files:"
	@ls -1 .env.* 2>/dev/null | grep -v "\.local" | sed 's/^\.env\./  /'

build-playwright-image: ## Build a dedicated Playwright image with the frontend preinstalled
	docker build -f front/Dockerfile.playwright -t search-next_playwright:local .

test-front-ci-image: ## Run headless Playwright tests inside the prebuilt Playwright image
	docker build -f front/Dockerfile.playwright -t search-next_playwright:local .
	docker run --rm search-next_playwright:local bash -lc "npm run build && npx playwright test"

test-front-ci-ui-image: ## Run Playwright UI inside prebuilt Playwright image (exposes 9323)
	docker build -f front/Dockerfile.playwright -t search-next_playwright:local .
	docker run --rm -p 9323:9323 search-next_playwright:local bash -lc "xvfb-run -s '-screen 0 1920x1080x24' npx playwright test --ui --project=chromium --reporter=list"


# Shell
shell-api: ## Accéder au shell de l'API
	$(DOCKER_COMPOSE) exec api bash

shell-frontend: ## Accéder au shell du frontend
	$(DOCKER_COMPOSE) exec frontend sh

# Nettoyage
clean: ## Nettoyer les conteneurs et volumes
	$(DOCKER_COMPOSE) down -v
	docker system prune -f

clean-all: ## Nettoyage complet (incluant les images)
	$(DOCKER_COMPOSE) down -v --rmi all
	docker system prune -af

# Utilitaires
ps: ## Lister les conteneurs en cours d'exécution
	$(DOCKER_COMPOSE) ps

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
	@$(MAKE) sync-env ENV=development
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml build
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✓ Installation terminée"
	@echo "API: http://localhost:8007"
	@echo "Frontend: http://localhost:${FRONTEND_PORT:-3009}"

install-prod: ## Installation en production
	@echo "Installation de l'environnement OpenEdition Search en production..."
	@$(MAKE) sync-env ENV=production
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml build
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Installation production terminée"
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:80"


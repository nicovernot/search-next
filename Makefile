# Makefile pour gérer l'environnement Docker

# Variables pour la gestion des environnements
ENV ?= development
FRONTEND_ENV ?= development

.PHONY: help build up down restart logs clean dev prod test configure-env sync-env check-env

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Configuration des environnements avec la nouvelle approche centralisée
sync-env: ## Synchroniser l'environnement (dev, staging, prod, test)
	@echo "Synchronizing environment: $(ENV)"
	@./scripts/sync_env.sh $(ENV)
	@echo "Environment synchronized successfully!"
	@echo "Backend: search_api_solr/.env.local"
	@echo "Frontend: front-next/.env.local"

check-env: ## Vérifier la configuration d'environnement
	@./scripts/check_env_setup.sh

# Configuration des environnements (ancienne méthode - dépréciée)
configure-env: ## Configurer l'environnement (dev, staging, prod, test) - DEPRECATED
	@echo "WARNING: This method is deprecated. Use 'make sync-env' instead."
	@echo "Configuring environment: $(ENV)"
	@cd search_api_solr && cp .env.$(ENV) .env
	@cd front-next && cp .env.$(FRONTEND_ENV) .env.local
	@echo "Environment configured successfully!"
	@echo "Backend environment: $(ENV)"
	@echo "Frontend environment: $(FRONTEND_ENV)"

# Développement
dev: ## Lancer l'environnement de développement
	@$(MAKE) sync-env ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build et lancer l'environnement de développement
	@$(MAKE) sync-env ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Arrêter l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Staging
staging: ## Lancer l'environnement de staging
	@$(MAKE) sync-env ENV=staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml up

staging-build: ## Build et lancer l'environnement de staging
	@$(MAKE) sync-env ENV=staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml up --build

staging-down: ## Arrêter l'environnement de staging
	docker-compose -f docker-compose.yml -f docker-compose.staging.yml down

# Production
prod: ## Lancer l'environnement de production
	@$(MAKE) sync-env ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Build et lancer l'environnement de production
	@$(MAKE) sync-env ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## Arrêter l'environnement de production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Tests backend
test: ## Lancer les tests backend dans le container (recommandé)
	@$(MAKE) sync-env ENV=test
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm api pytest -v

test-cov: ## Lancer les tests avec couverture dans le container
	@$(MAKE) sync-env ENV=test
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm api pytest --cov=app --cov-report=html --cov-report=term -v

test-local: ## Lancer les tests en local (nécessite les dépendances installées)
	@$(MAKE) sync-env ENV=test
	cd search_api_solr && python -m pytest -v

test-ci: ## Lancer les tests pour CI/CD (dans container, sortie XML)
	@$(MAKE) sync-env ENV=test
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm api pytest --junitxml=test-results.xml -v

# Tests Frontend
test-front: ## Lancer les tests E2E Playwright (headless)
	@$(MAKE) sync-env ENV=test
	docker-compose up -d api search_next
	@sleep 5
	cd front-next && npx playwright test --reporter=list
	docker-compose down

test-front-ui: ## Lancer les tests E2E Playwright avec UI
	@$(MAKE) sync-env ENV=test
	docker-compose up -d api search_next
	@sleep 5
	cd front-next && npx playwright test --ui
	docker-compose down

test-front-unit: ## Lancer les tests unitaires du frontend
	docker run --rm -v $(PWD)/front-next:/app -w /app node:20-alpine sh -c "npm install && npm test -- --watchAll=false --ci --passWithNoTests"

test-front-ci: ## Tests E2E dans container Playwright (CI/CD) - 100% containerisé
	@$(MAKE) sync-env ENV=test
	docker-compose up -d api search_next
	@echo "Waiting for services to be ready..."
	@sleep 8
	docker run --rm --network search-next_openedition_network \
		-v $(PWD)/front-next:/app -w /app \
		-e BASE_URL=http://search_next:3000 \
		-e CI=true \
		mcr.microsoft.com/playwright:v1.57.0-noble \
		sh -c "npm ci --silent && npx playwright test --reporter=list --project=chromium"
	docker-compose down

# Tests complets
test-all: ## Lancer tous les tests (backend + frontend)
	@echo "=== Tests Backend ==="
	@$(MAKE) test
	@echo ""
	@echo "=== Tests Frontend E2E ==="
	@$(MAKE) test-front

test-prod: ## Lancer les tests en environnement de production (simulé)
	@$(MAKE) sync-env ENV=production
	docker-compose run --rm api sh -c "pip install --no-cache-dir -r requirements-dev.txt && pytest"

# Commandes avec environnement personnalisé
run-dev: ## Lancer avec environnement personnalisé (ex: make run-dev ENV=staging)
	@$(MAKE) sync-env ENV=$(ENV)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

run-prod: ## Lancer production avec environnement personnalisé
	@$(MAKE) sync-env ENV=$(ENV)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

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
	docker-compose logs -f search_next

# Gestion des environnements (nouvelle approche)

env-check: ## Vérifier la configuration d'environnement
	@$(MAKE) check-env

env-sync: ## Synchroniser l'environnement courant
	@$(MAKE) sync-env ENV=$(ENV)

env-list: ## Lister les fichiers d'environnement disponibles
	@echo "Available environment files:"
	@ls -1 .env.* 2>/dev/null | grep -v "\.local" | sed 's/^\.env\./  /'

build-playwright-image: ## Build a dedicated Playwright image with the frontend preinstalled
	docker build -f front-next/Dockerfile.playwright -t openedition_playwright:local .

test-front-ci-image: ## Run headless Playwright tests inside the prebuilt Playwright image
	docker build -f front-next/Dockerfile.playwright -t openedition_playwright:local .
	docker run --rm openedition_playwright:local bash -lc "npm run build && npx playwright test"

test-front-ci-ui-image: ## Run Playwright UI inside prebuilt Playwright image (exposes 9323)
	docker build -f front-next/Dockerfile.playwright -t openedition_playwright:local .
	docker run --rm -p 9323:9323 openedition_playwright:local bash -lc "xvfb-run -s '-screen 0 1920x1080x24' npx playwright test --ui --project=chromium --reporter=list"


# Shell
shell-api: ## Accéder au shell de l'API
	docker-compose exec api bash

shell-frontend: ## Accéder au shell du frontend
	docker-compose exec search_next sh

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
	@$(MAKE) sync-env ENV=development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✓ Installation terminée"
	@echo "API: http://localhost:8007"
	@echo "Frontend: http://localhost:${FRONTEND_PORT:-3009}"

install-prod: ## Installation en production
	@echo "Installation de l'environnement OpenEdition Search en production..."
	@$(MAKE) sync-env ENV=production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✓ Installation production terminée"
	@echo "API: http://localhost:8000"
	@echo "Frontend: http://localhost:80"


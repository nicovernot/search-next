# Makefile pour gérer l'environnement Docker

.PHONY: help build up down restart logs clean dev prod test

help: ## Afficher l'aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Développement
dev: ## Lancer l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Build et lancer l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down: ## Arrêter l'environnement de développement
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production
prod: ## Lancer l'environnement de production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-build: ## Build et lancer l'environnement de production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-down: ## Arrêter l'environnement de production
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

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

# Tests
test: ## Lancer les tests
	docker-compose exec api pytest

test-cov: ## Lancer les tests avec couverture
	docker-compose exec api pytest --cov=app --cov-report=html

test-front: ## Lancer les tests E2E du frontend (Headless)
	cd front && npm run test:e2e

test-front-ui: ## Lancer les tests E2E du frontend avec UI
	cd front && npm run test:e2e:ui


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
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "✓ Installation terminée"
	@echo "API: http://localhost:8007"
	@echo "Frontend: http://localhost:${FRONTEND_PORT:-3009}"


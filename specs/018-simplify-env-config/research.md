# Phase 0 Research: Simplification de la configuration d'environnement

Toutes les inconnues du Technical Context ont été résolues par inspection directe du dépôt (aucun `NEEDS CLARIFICATION` ne subsiste). Ce document consigne les décisions techniques et leurs alternatives.

## 1. Mécanisme du "fichier unique par environnement"

- **Decision**: Trois fichiers modèles versionnés et autonomes (`.env.development`, `.env.test`, `.env.production`) remplacent l'actuelle pile `.env.shared` + `.env.{env}` + `.env.example`. Un script `scripts/use-env.sh <environment>` "active" l'un des trois en le copiant vers `.env` (racine, non versionné — déjà le fichier que Docker Compose charge nativement pour la substitution `${VAR}`). Deux symlinks (`front/.env -> ../.env` et `search_api_solr/.env -> ../.env`) rendent ce même fichier visible aux deux services, qui résolvent chacun leurs fichiers `.env*` relativement à leur propre répertoire de travail (contrainte native de Next.js et de `pydantic-settings`).
- **Rationale**: Élimine complètement les deux causes racines de la panne diagnostiquée en session de debug : (1) plusieurs fichiers pouvaient contenir des valeurs différentes pour la même variable sans qu'aucun ne soit clairement "la source de vérité" (`.env` racine vs `.env.development` vs fichiers générés) ; (2) une étape de génération (`sync_env.sh`) pouvait laisser des fichiers `*.env.local` obsolètes si elle n'était pas rejouée après chaque édition. Avec un symlink, il n'existe plus qu'un seul fichier réel : toute édition est immédiatement visible partout, sans étape de synchronisation à se rappeler d'exécuter.
- **Alternatives considered**:
  - *Un seul fichier versionné avec variables préfixées par environnement* (`DEV_SOLR_URL`, `PROD_SOLR_URL`, ...) + chargeur applicatif qui filtre par préfixe : rejeté par l'utilisateur (Q1) — plus verbeux (chaque variable ×3), nécessite un chargeur applicatif dans chaque service (Python **et** Next.js), et ne résout pas le vrai problème (le nombre de *fichiers* n'était pas le souci, la duplication et la génération silencieuse l'étaient).
  - *Conserver `sync_env.sh` mais réduire à 3 environnements* : rejeté — le script de génération lui-même (copie vers des fichiers dérivés) est la source du bug observé (fichiers dérivés non resynchronisés) ; le supprimer au profit d'un symlink retire la classe d'erreur entière plutôt que de la réduire.

## 2. Devenir de l'environnement "staging"

- **Decision**: Suppression complète — `.env.staging`, `docker-compose.staging.yml`, et toute cible Make/CI associée sont retirés. Grep du dépôt : 20 fichiers référencent "staging" (docs, scripts, Makefile, `specs/012` et `specs/006` historiques, `.github/workflows/ci.yml`). Les fichiers `specs/*` historiques (plans/tasks de features déjà livrées) sont laissés tels quels (ce sont des archives de décisions passées, pas de la documentation vivante) ; seuls les fichiers de configuration/doc/CI actifs sont mis à jour.
- **Rationale**: Décision explicite de l'utilisateur (Q2 = option B) après avoir été informé du compromis (staging perd son isolement propre). Réduit le nombre d'environnements à exactement 3 comme demandé.
- **Alternatives considered**: Fusion dans production avec indicateur (option A, non retenue) ; conservation comme cible de déploiement hors variable sélectrice (option C, non retenue).
- **Risque identifié**: La constitution du projet (`.specify/memory/constitution.md`, section *Product Constraints*) mentionne explicitement "Local, staging, and production deployments". Cette phrase devient obsolète après ce chantier — traité comme point de vigilance non bloquant (voir Constitution Check dans plan.md), à corriger par un amendement de gouvernance séparé.

## 3. Gestion des secrets de production dans le fichier unique

- **Decision**: `.env.production` (modèle versionné) contient des valeurs placeholders explicites et non fonctionnelles (ex. `change-me-in-production`, cohérent avec la valeur déjà utilisée dans `.env.example` actuel pour `SECRET_KEY`). `search_api_solr/app/core/env_validation.py` (déjà appelé au démarrage de l'API, cf. `docs/ENVIRONMENTS.md` existant) est étendu pour lever une erreur bloquante si `ENVIRONMENT=production` et qu'un secret (`SECRET_KEY`, `JWT_SECRET`, `SESSION_SECRET`) est encore égal à sa valeur placeholder connue.
- **Rationale**: Réutilise un mécanisme de validation déjà en place et déjà invoqué au démarrage (`validate_environment()` dans `main.py`), plutôt que d'introduire un nouvel outil. Cohérent avec le principe constitutionnel IV (secrets hors dépôt, contrôles explicites).
- **Alternatives considered**: Secrets exclusivement hors fichier versionné (option B, non retenue par l'utilisateur — casse la promesse "un seul fichier suffit pour démarrer").

## 4. Contrainte Next.js : variables `NEXT_PUBLIC_*` inlinées au build

- **Decision**: Le script `scripts/verify_env_docker.sh` (FR-008) vérifie les variables runtime des conteneurs (`docker exec <service> printenv`) pour tous les environnements, et documente explicitement (dans `docs/ENVIRONMENTS.md`) que pour `NEXT_PUBLIC_*` en production, une valeur runtime correcte ne garantit pas que le bundle déployé l'utilise — il faut un rebuild (`docker compose build`) après changement, car `docker-compose.prod.yml` passe `NEXT_PUBLIC_API_URL` en `build.args`.
- **Rationale**: Risque réel déjà présent dans le code actuel (`docker-compose.prod.yml` ligne `build.args.NEXT_PUBLIC_API_URL`) ; l'ignorer produirait une fausse impression de sécurité après vérification.
- **Alternatives considered**: Aucune — c'est une contrainte du framework Next.js (variables publiques inlinées statiquement), non contournable dans le périmètre de ce chantier.

## 5. Consolidation de la documentation

- **Decision**: `docs/ENVIRONMENTS.md` est réécrit comme document de référence unique couvrant : structure des 3 fichiers modèles, mécanisme d'activation, règles de précédence, liste complète des variables (dont `CORS_ORIGINS`) avec valeur par environnement, procédure de vérification Docker, résolution de problèmes. `search_api_solr/ENVIRONMENTS.md` (456 lignes, largement redondant avec `docs/ENVIRONMENTS.md` et non mis à jour depuis le renommage `CORS_ALLOWED_ORIGINS` → `CORS_ORIGINS`) est supprimé.
- **Rationale**: Deux documents concurrents sur le même sujet, l'un des deux obsolète, est exactement la classe de "doute documentaire" que la feature demande de corriger.
- **Alternatives considered**: Garder les deux et les synchroniser manuellement — rejeté, c'est le mécanisme même qui a produit la divergence actuelle.

---

description: "Task list for logging strategy"
---

# Tasks: Stratégie de logs applicatifs

**Input**: Design documents from `specs/013-logging-strategy/`

**Prerequisites**: `plan.md`, `spec.md`

**Note**: Cette liste de tâches a été reconstituée a posteriori (feature 014, T017) car la spec 013 avait été livrée sans `tasks.md`. Les cases cochées ci-dessous sont reliées à une preuve vérifiable (fichier, commit ou règle de configuration présente dans le dépôt).

## Phase 1: Configuration backend centrale

- [x] T001 Revoir `search_api_solr/app/core/logging.py` et garantir un root logger unique — *Preuve : fichier présent, `setup_logging()` appelle `python-json-logger`.*
- [x] T002 Aligner la propagation vers les loggers de modules (`get_logger(__name__)`) — *Preuve : `search_api_solr/app/core/logging.py`.*

## Phase 2: Normalisation backend métier

- [x] T003 Supprimer les appels `logging.basicConfig()` restants dans le code métier — *Preuve : `grep -rn "basicConfig(" search_api_solr/app` ne retourne aucun résultat.*
- [x] T004 Convertir les f-strings de log en `extra={"context": ...}` dans `SuggestService`, `PermissionsService`, `docs_permissions_client.py` — *Preuve : commit `ea54d67` « feat(013): logging hardening — redaction, structured logs, ESLint no-console ».*

## Phase 3: Redaction et politique par environnement

- [x] T005 Éviter la fuite d'URL Solr complète en DEBUG (remplacée par `base_url` + `params_count` structurés) — *Preuve : commit `ea54d67`.*
- [x] T006 Masquage IP (`_mask_ip`) déjà en place — *Preuve : code présent dans les services de permissions.*

## Phase 4: Frontend

- [x] T007 Conserver `front/app/lib/logger.ts` comme point d'entrée unique — *Preuve : fichier présent.*
- [x] T008 Ajouter une règle ESLint interdisant `console.*` direct hors exceptions — *Preuve : `front/eslint.config.mjs` ligne 19 (`"no-console": "error"`), exception ligne 25 pour le wrapper lui-même.*

## Phase 5: Documentation et vérification

- [x] T009 Documenter la stratégie de logs dans `docs/LOGGING.md` — *Preuve : fichier présent, mis à jour le 2026-05-10 (voir feature 014, T012).*
- [ ] T010 Relancer les commandes de vérification `rg` du plan (`basicConfig\(|console\.(log|error|warn|info|debug)`, `getLogger\(|get_logger\(`) dans l'environnement cible et consigner le résultat — *Bloqué : nécessite une exécution manuelle documentée ; non ré-exécuté depuis la livraison du 2026-05-10.*

**Checkpoint**: Le socle de logging backend/frontend est livré et durci (2026-05-10, PR #9 `feat/013-logging-durcissement`) ; seule la ré-exécution périodique des commandes de vérification reste ouverte, sans effet bloquant sur le statut livré.

# Implementation Plan: Simplification de la configuration d'environnement

**Branch**: `018-simplify-env-config` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-simplify-env-config/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Remplacer la configuration d'environnement actuellement répartie sur 6+ fichiers (`.env.shared`, `.env.development`, `.env.test`, `.env.staging`, `.env.production`, `.env.example`) et deux couches de génération par service (`front/.env.local`, `search_api_solr/.env.local`) par **trois fichiers modèles versionnés autonomes** — un par environnement (`.env.development`, `.env.test`, `.env.production`) — activés un par un via un script d'activation qui écrit le fichier actif à la racine (`.env`, non versionné) et le rend visible aux deux services par symlink, éliminant toute étape de fusion/génération intermédiaire. L'environnement "staging" est retiré. Un script de vérification confirme que chaque conteneur Docker a bien pris en compte les variables attendues (dont `CORS_ORIGINS`). La documentation est consolidée dans un unique document de référence.

## Technical Context

**Language/Version**: Bash (scripts d'activation/vérification), Python 3.10 (FastAPI + pydantic-settings pour la validation backend), TypeScript/Next.js 15 (chargement natif des fichiers `.env*` du frontend)

**Primary Dependencies**: Docker Compose (fichiers `docker-compose.yml` + `docker-compose.{dev,prod}.yml`), `pydantic-settings` (`search_api_solr/app/core/env_validation.py`), GNU Make (points d'entrée développeur), Next.js (résolution native de `front/.env*`)

**Storage**: N/A — fichiers de configuration uniquement, aucune donnée persistée

**Testing**: `pytest` (validation backend, y compris un nouveau test couvrant le rejet d'une valeur `ENVIRONMENT` invalide et la détection de secret placeholder en production), vérification manuelle/scriptée des conteneurs Docker (`scripts/verify_env_docker.sh`), suite Playwright existante (`make test-front`) exécutée après bascule d'environnement pour non-régression

**Target Platform**: Postes de développement Linux/macOS via Docker Compose (dev, test) et serveur Linux de production (Docker Compose ou `install_no_docker.sh`)

**Project Type**: Web application (frontend Next.js + backend FastAPI) — ce chantier est une modification transverse de configuration/outillage, pas une fonctionnalité produit

**Performance Goals**: N/A — chantier de configuration, aucun objectif de performance applicative

**Constraints**:
- Ne jamais committer de secret réel dans un fichier versionné (placeholders uniquement, cf. FR-010)
- `make dev` (et équivalents test/prod) doivent continuer à fonctionner en une seule commande après la simplification
- Les variables `NEXT_PUBLIC_*` sont inlinées au build en production (`docker-compose.prod.yml` les passe en `build.args`) — la vérification en production doit tenir compte de cette contrainte propre à Next.js (une variable runtime correcte dans le conteneur ne garantit pas qu'elle a été utilisée au build)
- La CI existante (`.github/workflows/ci.yml`) et les scripts qui référencent `staging` doivent être mis à jour en cohérence avec sa suppression

**Scale/Scope**: 3 environnements × 2 services applicatifs (front, API) ; ~15 fichiers identifiés comme référençant l'ancien modèle ou "staging" (voir research.md) à faire évoluer : `docker-compose.staging.yml`, `Makefile`, `scripts/sync_env.sh`, `scripts/configure_env.sh`, `scripts/check_env_setup.sh`, `docs/ENVIRONMENTS.md`, `search_api_solr/ENVIRONMENTS.md`, `docs/CORS_CONFIGURATION.md`, `docs/REDIS_INTEGRATION.md`, `docs/LOGGING.md`, `docs/RECOMMENDATIONS.md`, `.github/workflows/ci.yml`, `search_api_solr/app/core/env_validation.py`, `.env.shared`, `.env.example`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principe | Évaluation | Statut |
|---|---|---|
| I. Search Quality Is Non-Negotiable | Aucun impact — ce chantier ne touche ni la pertinence ni le ranking. | N/A — PASS |
| II. User-Centered Product Experience | Aucun impact utilisateur final direct ; améliore l'expérience développeur (public visé par cette spec). | PASS |
| III. Evidence-Driven Delivery | Le plan prévoit un script de vérification Docker (FR-008) et le maintien des suites de tests existantes après bascule d'environnement ; la documentation est mise à jour en cohérence (exigence constitutionnelle explicite : "Documentation... must be updated when... infrastructure assumptions change"). | PASS, sous réserve d'exécuter Phase 2 (tasks) avec les étapes de vérification incluses |
| IV. Secure and Permission-Aware Access | Renforce ce principe : secrets hors dépôt (placeholders obligatoires, FR-010) + détection de placeholder non surchargé en production (FR-014), aligné avec "Sensitive configuration and secrets must stay outside source control". | PASS |
| V. Simplicity, Maintainability, and Explicit Change | C'est l'objectif premier du chantier : suppression de couches dupliquées/cachées (`.env.shared`, fichiers générés, override racine invisible) responsables d'une régression réelle constatée en session de debug. | PASS |

**Point de vigilance (non bloquant, à traiter hors de cette implémentation)** : la section *Product Constraints* de la constitution mentionne explicitement "Local, staging, and production deployments must remain traceable...". La suppression de l'environnement staging (décision utilisateur, FR-013) rend cette phrase obsolète. Ce plan n'amende pas la constitution (changement de gouvernance distinct, cf. section *Governance*) ; une proposition d'amendement (PATCH) retirant la mention de staging doit être soumise séparément après livraison de cette feature. Voir tâche de suivi dans `tasks.md`.

*Aucune violation nécessitant la table Complexity Tracking : ce chantier réduit la complexité existante, il n'en ajoute pas.*

### Re-check post-Phase 1

Le design (data-model.md, contracts/, quickstart.md) confirme les évaluations ci-dessus : aucune nouvelle violation introduite. Le schéma des variables (`contracts/env-schema.md`) a révélé des écarts existants (ex. `CORS_ORIGINS` absent de l'actuel `.env.production`, valeurs de "staging" parfois reconduites sans validation pour la vraie prod) — ces écarts renforcent plutôt qu'ils n'affaiblissent le principe IV (accès sécurisé) en les rendant visibles avant implémentation plutôt qu'en les laissant latents. Point de vigilance sur la mention de "staging" dans la constitution inchangé (toujours à traiter par amendement séparé).

## Project Structure

### Documentation (this feature)

```text
specs/018-simplify-env-config/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md         # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── cli-contract.md
│   └── env-schema.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
.env.development          # Modèle versionné — remplace .env.shared + .env.development actuels
.env.test                 # Modèle versionné — remplace .env.shared + .env.test actuels
.env.production            # Modèle versionné (placeholders secrets) — remplace .env.shared + .env.production actuels
.env                       # Fichier ACTIF, non versionné — copie du modèle sélectionné par scripts/use-env.sh
.env.shared                 # SUPPRIMÉ (fusionné dans chaque modèle)
.env.example                # SUPPRIMÉ (.env.development sert de référence d'onboarding)
.env.staging                 # SUPPRIMÉ
docker-compose.staging.yml   # SUPPRIMÉ

scripts/
├── use-env.sh              # NOUVEAU — active un environnement (copie + symlinks), remplace sync_env.sh/configure_env.sh
├── verify_env_docker.sh    # NOUVEAU — vérifie la config effective dans les conteneurs Docker (FR-008)
├── sync_env.sh              # SUPPRIMÉ (remplacé par use-env.sh)
├── configure_env.sh          # SUPPRIMÉ (remplacé par use-env.sh)
└── check_env_setup.sh        # MIS À JOUR (liste de fichiers requis alignée sur le nouveau modèle)

front/
└── .env -> ../.env          # symlink créé par use-env.sh (remplace front/.env + front/.env.local)

search_api_solr/
├── .env -> ../.env          # symlink créé par use-env.sh (remplace search_api_solr/.env.local)
└── app/core/env_validation.py  # MIS À JOUR — valide ENVIRONMENT ∈ {development,test,production} + détection placeholder secret en prod (FR-009, FR-014)

docs/
└── ENVIRONMENTS.md          # RÉÉCRIT — document de référence unique (fusionne docs/ENVIRONMENTS.md et search_api_solr/ENVIRONMENTS.md, inclut CORS)

search_api_solr/ENVIRONMENTS.md  # SUPPRIMÉ (contenu fusionné dans docs/ENVIRONMENTS.md)

Makefile                    # MIS À JOUR — cibles staging retirées, cibles dev/test/prod appellent use-env.sh
.github/workflows/ci.yml    # MIS À JOUR — toute référence à staging retirée/adaptée
```

**Structure Decision**: Application web existante (frontend Next.js dans `front/`, backend FastAPI dans `search_api_solr/`, orchestration via Docker Compose à la racine). Ce chantier ne modifie pas cette structure applicative ; il modifie exclusivement la couche de configuration/outillage à la racine du dépôt et les points d'intégration Docker/CI qui la consomment. Le mécanisme retenu (fichier actif unique à la racine + symlinks par service) respecte la contrainte technique de Next.js et de pydantic-settings, qui résolvent chacun leurs fichiers `.env*` relativement à leur propre répertoire de travail.

## Complexity Tracking

*Aucune entrée — ce chantier réduit le nombre de sources de configuration (de 6+ fichiers et 2 couches de génération à 3 fichiers modèles + 1 fichier actif). Aucune complexité nouvelle n'est introduite qui nécessiterait une justification.*

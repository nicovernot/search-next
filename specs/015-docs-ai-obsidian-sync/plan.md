# Implementation Plan: Documentation technique fiable, lisible dans Obsidian et exploitable par l'IA

**Branch**: `015-docs-ai-obsidian-sync` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/015-docs-ai-obsidian-sync/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Mettre à jour les 12 fichiers de `docs/` pour qu'ils soient exacts par rapport au code actuel, dépourvus de marqueurs de conflit Git, dotés d'une date de fraîcheur, navigables via un point d'entrée et des liens relatifs portables (Obsidian + IA), et illustrés par des exemples concrets utilisant exclusivement des valeurs génériques. L'approche fusionne les résumés ponctuels qui font doublon avec un document de référence vivant (`CORS_IMPLEMENTATION_SUMMARY.md` → `CORS_CONFIGURATION.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md` → `ENVIRONMENTS.md`), ajoute un contrôle non destructif réexécutable (`scripts/check_docs_coherence.sh`, sur le modèle de `scripts/check_spec_coherence.sh` livré en feature 014), et ne touche à aucun code applicatif.

## Technical Context

**Language/Version**: Markdown et scripts POSIX shell existants (mêmes outils que la feature 014)

**Primary Dependencies**: Git, ripgrep, `scripts/check_spec_coherence.sh` comme modèle réutilisé

**Storage**: Fichiers Markdown sous `docs/` et métadonnées Git ; aucune base de données

**Testing**: Contrôle shell non destructif + suite de tests shell (sur le modèle de `scripts/test_check_spec_coherence.sh`) ; vérification manuelle des exemples contre le code actuel

**Target Platform**: Dépôt Git sous environnement Linux/macOS compatible POSIX ; dossier `docs/` ouvrable comme vault Obsidian sans configuration additionnelle

**Project Type**: Documentation technique/opérationnelle + outillage de dépôt (gouvernance documentaire)

**Performance Goals**: Produire un rapport d'audit de `docs/` en moins de 5 secondes sur le dépôt courant (12 fichiers, périmètre plus restreint que la feature 014)

**Constraints**: Aucune modification du comportement applicatif ; exemples ajoutés strictement génériques/anonymisés (FR-012) ; documents historiques conservés sauf doublon fusionnable (FR-008) ; liens internes en chemins relatifs uniquement (FR-006)

**Scale/Scope**: Les 12 fichiers de `docs/` ; le nombre de fichiers finaux peut descendre à 10 après fusion des deux doublons identifiés (`CORS_IMPLEMENTATION_SUMMARY.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md`) ; nouveau point d'entrée `docs/README.md` ; nouveau script `scripts/check_docs_coherence.sh` + `scripts/test_check_docs_coherence.sh`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

* **I. Search Quality** : PASS — aucun comportement de recherche ou de classement n'est modifié.
* **II. User-Centered Experience** : PASS — la feature améliore la clarté et la fiabilité de la documentation consultée par les mainteneurs et les agents IA ; aucune interface utilisateur applicative n'est modifiée.
* **III. Evidence-Driven Delivery** : PASS — chaque correction factuelle est traçable à une source vérifiable (FR-010) et un contrôle automatisé réexécutable (FR-011) confirme la garantie dans le temps.
* **IV. Secure Access** : PASS — les exemples ajoutés utilisent exclusivement des valeurs génériques/anonymisées (FR-012), aucune valeur réelle d'environnement (même non sensible) n'est exposée.
* **V. Simplicity and Explicit Change** : PASS — réutilisation du script et du gabarit de tests de la feature 014 ; les doublons de contenu sont fusionnés plutôt qu'accumulés (FR-008), réduisant la surface documentaire au lieu de l'étendre.

No constitution violations identified. Gate status: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/015-docs-ai-obsidian-sync/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
docs/
├── README.md                          # NOUVEAU — point d'entrée (FR-007), liste des 10-12 fichiers avec description 1 ligne
├── ARCHITECTURE.md                    # référence vivante — résoudre 3 conflits Git, ajouter date de fraîcheur
├── API_V1.md                          # référence vivante — anonymiser les exemples curl (FR-012), ajouter date
├── LOGGING.md                         # référence vivante — déjà daté (feature 014) ; vérifier fraîcheur
├── ENVIRONMENTS.md                    # référence vivante — cible de fusion, ajouter date
├── CORS_CONFIGURATION.md              # référence vivante — cible de fusion, ajouter date
├── CORS_IMPLEMENTATION_SUMMARY.md     # SUPPRIMÉ après fusion dans CORS_CONFIGURATION.md (FR-008)
├── ENVIRONMENT_MANAGEMENT_SUMMARY.md  # SUPPRIMÉ après fusion dans ENVIRONMENTS.md (FR-008)
├── INSTALL_PROD_NO_DOCKER.md          # référence vivante — ajouter date, vérifier commandes
├── RECOMMENDATIONS.md                 # déjà étiqueté ARCHIVE — ajouter date de vérification
├── REDIS_INTEGRATION.md               # référence vivante — ajouter date, anonymiser exemples
├── SETUP_COMPLETE.md                  # déjà étiqueté ARCHIVE — ajouter date de vérification
└── CHANGELOG.md                       # log continu — clarifier le rôle vs specs/CHANGELOG.md (FR-008)

scripts/
├── check_docs_coherence.sh            # NOUVEAU — contrôle non destructif (FR-011), sur le modèle de check_spec_coherence.sh
└── test_check_docs_coherence.sh       # NOUVEAU — suite de tests, sur le modèle de test_check_spec_coherence.sh
```

**Structure Decision**: Aucun nouveau module applicatif. Le travail porte sur les fichiers Markdown existants de `docs/` (édition en place, deux suppressions après fusion, un nouvel index), et deux nouveaux scripts shell dans `scripts/` réutilisant le patron établi par la feature 014 (`check_spec_coherence.sh` / `test_check_spec_coherence.sh`).

## Research Summary

Les décisions détaillées sont consignées dans [research.md](research.md), à partir d'un audit intégral des 12 fichiers de `docs/`. Les choix structurants sont :

1. Entête de fraîcheur en texte simple (`**Dernière vérification** : AAAA-MM-JJ`), cohérent avec la convention déjà utilisée par `LOGGING.md`.
2. Point d'entrée `docs/README.md`, groupant les fichiers par rôle (référence vivante / historique / log continu).
3. Fusion des deux paires déjà étiquetées `DOUBLON` (`CORS_IMPLEMENTATION_SUMMARY.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md`) dans leur référence vivante, puis suppression.
4. Exemples anonymisés via des espaces réservés entre chevrons (`<HOST>`, `<PORT>`, ou nom de variable d'environnement documentée).
5. `scripts/check_docs_coherence.sh` + `scripts/test_check_docs_coherence.sh`, sur le patron déjà revu de la feature 014.
6. `docs/CHANGELOG.md` reçoit un bandeau de rôle plutôt qu'une fusion, car son contenu ne fait pas réellement doublon avec `specs/CHANGELOG.md`.

## Validation Strategy

Les scénarios exécutables et leurs résultats attendus sont décrits dans [quickstart.md](quickstart.md) : absence de marqueurs de conflit, présence d'une date de fraîcheur par fichier, couverture complète du point d'entrée, suppression effective des deux fichiers fusionnés, exécution du contrôle automatisé sans modification de fichier, cohérence des endpoints cités avec le code, absence de valeurs réelles d'environnement dans les exemples, et vérification manuelle de rendu dans Obsidian.

## Constitution Check (post-design)

Re-vérifié après la Phase 1 (data-model.md, quickstart.md) : aucune décision de conception n'introduit de nouvelle surface applicative, de nouvelle dépendance externe, ou de donnée sensible. Les 5 principes restent PASS sans changement par rapport à la vérification initiale ci-dessus.

## Complexity Tracking

No constitution violations or additional complexity require justification.

# Implementation Plan: Cohérence du dépôt et des artefacts de spécification

**Branch**: `feature/014-repository-spec-coherence` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/014-repository-spec-coherence/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Rétablir une source de vérité documentaire pour les specs du dépôt en réconciliant les statuts, les artefacts `spec/plan/tasks`, la numérotation des features et les preuves de validation. L'approche consiste à appliquer un inventaire reproductible en lecture seule, à corriger les documents de référence, puis à vérifier que le workflow Spec Kit peut retrouver les artefacts attendus pour chaque feature active.

## Technical Context

**Language/Version**: Markdown et scripts POSIX shell existants

**Primary Dependencies**: Git, ripgrep, scripts Spec Kit du dépôt

**Storage**: Fichiers Markdown et métadonnées Git ; aucune base de données

**Testing**: Contrôles shell non destructifs, vérification des liens/artefacts, contrôles frontend/backend existants si une validation est citée

**Target Platform**: Dépôt Git sous environnement Linux/macOS compatible POSIX

**Project Type**: Documentation de gouvernance et outillage de dépôt

**Performance Goals**: Produire un rapport d'audit local en moins de 10 secondes sur le dépôt courant

**Constraints**: Lecture seule pendant l'audit ; aucune modification du code applicatif ; les entrées historiques restent conservées lorsqu'elles sont justifiées

**Scale/Scope**: Toutes les sous-répertoires `specs/*`, les documents centraux `README.md`, `PLANNING.md`, `CHANGELOG.md`, `docs/ARCHITECTURE.md` et les artefacts Spec Kit associés

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

* **I. Search Quality** : PASS — aucun comportement de recherche ou classement n'est modifié.
* **II. User-Centered Experience** : PASS — la feature améliore la lisibilité des statuts et des prochaines actions sans modifier l'interface utilisateur.
* **III. Evidence-Driven Delivery** : PASS — chaque correction documentaire sera reliée à un contrôle reproductible ou à une preuve existante.
* **IV. Secure Access** : PASS — aucun secret, token, contrôle d'accès ou flux d'authentification n'est modifié.
* **V. Simplicity and Explicit Change** : PASS — l'approche réutilise les artefacts et scripts existants, sans nouvelle abstraction applicative.

No constitution violations identified. Gate status: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/014-repository-spec-coherence/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
specs/
├── README.md                         # catalogue des specs et artefacts
├── PLANNING.md                       # dépendances et ordre de livraison
├── CHANGELOG.md                      # historique des décisions documentaires
├── TECHNICAL_REQUIREMENTS.md         # contraintes transverses
├── 001-*/spec.md                     # exigences et statuts feature
├── 001-*/plan.md                     # conception et prérequis feature
└── 001-*/tasks.md                    # tâches et preuves d'avancement

docs/
└── ARCHITECTURE.md                   # documentation opérationnelle liée

.specify/
├── feature.json                      # contexte de feature actif
└── scripts/bash/check-prerequisites.sh
```

**Structure Decision**: La feature reste dans les artefacts documentaires existants. Les corrections portent sur les fichiers Markdown et le contexte Spec Kit ; aucun code source, endpoint ou schéma de données applicatif n'est introduit.

## Research Summary

Les décisions détaillées sont consignées dans [research.md](research.md). Les choix structurants sont :

1. Git et les fichiers présents sont la source de vérité de l'état du dépôt.
2. Un statut livré doit être distingué de la complétude des tâches historiques.
3. Les anciens identifiants sont conservés uniquement dans les entrées historiques du changelog.
4. L'audit doit rester non destructif et produire les mêmes résultats à état identique.

## Phase Plan

### Phase 0 — Inventaire et décisions

- Recenser les dossiers de specs et leurs artefacts.
- Comparer les statuts du catalogue, du planning et des specs.
- Identifier les références de numérotation obsolètes.
- Recenser les tâches ouvertes, les tâches cochées sans preuve et les validations citées.

### Phase 1 — Réconciliation documentaire

- Compléter les artefacts manquants des specs actives.
- Corriger les statuts, identifiants et textes contradictoires.
- Ajouter les preuves ou blocages nécessaires aux tâches.
- Enregistrer les changements importants dans le changelog.

### Phase 2 — Contrôle final

- Exécuter le contrôle de cohérence en lecture seule.
- Vérifier les prérequis Spec Kit pour chaque feature traitée.
- Vérifier que les validations citées correspondent à des commandes exécutables ou à des décisions explicitement documentées.

## Validation Strategy

Les scénarios exécutables et leurs résultats attendus sont décrits dans [quickstart.md](quickstart.md). Le contrôle doit signaler les artefacts manquants, les statuts divergents, les références de numérotation incohérentes et les tâches sans preuve, sans modifier les fichiers.

## Complexity Tracking

No constitution violations or additional complexity require justification.

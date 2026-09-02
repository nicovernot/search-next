# Feature Specification: Cohérence du dépôt et des artefacts de spécification

**Feature Branch**: `feature/014-repository-spec-coherence`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: « Créer une spec pour traiter les incohérences relevées entre le dépôt, les specs, les plans, les tâches et les validations. »

## Contexte

Le dépôt contient plusieurs générations de documentation de projet. Certaines fonctionnalités sont déclarées livrées alors que leurs tâches restent ouvertes, la numérotation du logging apparaît sous deux identifiants, et une spec livrée ne possède pas encore de liste de tâches. Ces écarts rendent le statut du produit difficile à comprendre et empêchent d'utiliser le workflow Spec Kit de manière fiable.

Cette feature vise à rétablir une source de vérité documentaire unique, vérifiable et maintenable. Elle ne modifie pas le comportement applicatif.

## User Scenarios & Testing

### User Story 1 - Lire un statut fiable (Priority: P1)

En tant que mainteneur, je veux connaître l'état réel de chaque spec depuis les documents centraux, afin de décider quel travail peut commencer.

**Why this priority**: Un statut contradictoire peut provoquer une livraison incomplète ou faire reprendre un travail déjà réalisé.

**Independent Test**: Comparer les statuts du catalogue, du planning et des specs avec les tâches cochées et les validations disponibles, puis vérifier qu'aucune contradiction de statut ne subsiste.

**Acceptance Scenarios**:

1. **Given** une feature déclarée livrée, **When** son statut est consulté dans le catalogue et le planning, **Then** les deux documents indiquent le même état et renvoient aux preuves pertinentes.
2. **Given** une feature partiellement livrée, **When** ses tâches sont consultées, **Then** les tâches restantes et leurs blocages sont explicitement identifiés.

### User Story 2 - Exécuter le workflow Spec Kit (Priority: P1)

En tant qu'implémenteur, je veux que chaque feature active possède les artefacts nécessaires, afin de pouvoir analyser, planifier et exécuter son travail sans erreur de contexte.

**Why this priority**: L'absence de `tasks.md` ou d'un plan obsolète bloque directement le workflow de livraison.

**Independent Test**: Pour chaque feature active, vérifier la présence et la cohérence de `spec.md`, `plan.md` et `tasks.md`, puis lancer le contrôle de prérequis correspondant.

**Acceptance Scenarios**:

1. **Given** une spec active, **When** le contrôle des artefacts est exécuté, **Then** les fichiers obligatoires sont présents ou l'absence est explicitement classée comme intentionnelle.
2. **Given** une tâche cochée, **When** l'état du code et les validations sont comparés, **Then** la tâche est justifiée par une preuve ou repasse à l'état ouvert.

### User Story 3 - Suivre les changements documentaires (Priority: P2)

En tant que reviewer, je veux relier chaque correction documentaire à une décision et à une validation, afin de conserver un historique compréhensible.

**Why this priority**: La traçabilité réduit les régressions de documentation lors des merges et des changements de priorité.

**Independent Test**: Examiner le journal des changements et vérifier que chaque correction de cohérence importante possède un sujet, un statut, une date et une référence de validation.

**Acceptance Scenarios**:

1. **Given** une correction de numérotation ou de statut, **When** elle est enregistrée dans l'historique, **Then** l'ancien état, le nouvel état et la raison sont compréhensibles.
2. **Given** une validation technique, **When** elle est citée dans la documentation, **Then** la commande, le périmètre et le résultat sont identifiables.

## Edge Cases

- Une fonctionnalité peut être livrée dans le code mais conserver des tâches historiques non cochées ; le statut doit alors distinguer l'implémentation de la complétude documentaire.
- Une spec renommée peut laisser des références à son ancien identifiant dans les docs ; les références historiques doivent être conservées uniquement lorsqu'elles expliquent une migration.
- Une tâche dépendant d'une validation métier ou d'un accès d'infrastructure ne doit pas être cochée par une simple présence de code.
- Une validation peut être indisponible localement ; la documentation doit distinguer un test non exécuté d'un test échoué.
- Le contexte de branche affiché par un outil peut diverger de la branche rapportée par Git ; Git doit rester la référence pour l'état du dépôt.

## Requirements

### Functional Requirements

- **FR-001**: Le dépôt DOIT disposer d'un catalogue indiquant, pour chaque spec, si elle est livrée, partielle, en cours ou au backlog.
- **FR-002**: Le catalogue, le planning et le statut déclaré dans chaque spec DOIVENT utiliser la même numérotation et le même vocabulaire d'état.
- **FR-003**: Chaque spec active DOIT avoir un `spec.md`, un `plan.md` et un `tasks.md`, sauf exception explicitement documentée avec sa justification.
- **FR-004**: Toute tâche cochée DOIT être reliée à une preuve vérifiable : code, test, documentation validée ou décision métier enregistrée.
- **FR-005**: Toute tâche non cochée DOIT préciser son blocage, sa dépendance ou la validation nécessaire avant exécution.
- **FR-006**: Les références à une spec renommée DOIVENT pointer vers son identifiant courant, avec conservation des anciens identifiants uniquement dans un contexte historique explicite.
- **FR-007**: Les plans DOIVENT refléter l'état actuel des prérequis et ne pas présenter comme futures des étapes déjà livrées.
- **FR-008**: Le journal des changements DOIT enregistrer les corrections de cohérence importantes avec une date, une description et une référence de livraison ou de validation.
- **FR-009**: Le contrôle de cohérence DOIT être exécutable sans modifier les fichiers et DOIT signaler les contradictions, artefacts manquants et tâches non justifiées.
- **FR-010**: La correction de la documentation NE DOIT PAS modifier le comportement applicatif sans être enregistrée comme une feature distincte.

### Key Entities

- **Spec**: description fonctionnelle d'une feature, son statut et ses exigences.
- **Plan**: conception et ordre de réalisation associés à une spec.
- **Task**: unité de travail traçable, avec état ouvert ou terminé.
- **Validation Evidence**: test, commande, décision ou fichier permettant de justifier l'état d'une tâche.
- **Status Vocabulary**: ensemble partagé des états `livré`, `partiel`, `en cours` et `backlog`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100 % des specs classées actives disposent d'un ensemble cohérent d'artefacts ou d'une exception documentée.
- **SC-002**: 100 % des statuts affichés dans le catalogue et le planning correspondent au statut déclaré dans la spec concernée.
- **SC-003**: 100 % des tâches cochées des specs actives disposent d'au moins une preuve de validation identifiable.
- **SC-004**: Le contrôle de cohérence produit un rapport reproductible sans modification du dépôt.
- **SC-005**: Aucun identifiant de spec courant n'est utilisé avec deux titres différents dans les documents de référence.
- **SC-006**: Un mainteneur peut identifier les prochaines actions bloquantes en moins de cinq minutes à partir du catalogue et du planning.

## Assumptions

- Les fichiers `spec.md`, `plan.md` et `tasks.md` restent les artefacts de référence du workflow Spec Kit.
- Le code existant et les résultats de tests constituent des preuves, mais ne remplacent pas une décision métier lorsqu'une validation métier est explicitement requise.
- Les entrées historiques du journal des changements peuvent conserver d'anciens identifiants si elles sont clairement datées et contextualisées.
- Cette feature traite la cohérence documentaire et la traçabilité ; elle ne réalise pas les phases fonctionnelles encore au backlog de la recherche sémantique.

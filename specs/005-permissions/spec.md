# Feature Specification: Permissions & Accès aux Résultats

**Feature Branch**: à créer — `feature/005-permissions`  
**Created**: 2026-04-13  
**Status**: Backlog — non démarré (backend déjà implémenté)

## Overview

Afficher les droits d'accès de l'utilisateur courant sur chaque résultat de recherche, en s'appuyant sur le endpoint backend `GET /permissions` déjà opérationnel. L'objectif est de rendre visible, directement sur les cartes de résultats, si un document est accessible en lecture complète, en accès restreint (abonné), ou fermé.

## Contexte technique

Le backend expose déjà `GET /permissions?urls=url1,url2&remote_ip=x.x.x.x` via `DocsPermissionsClient`. La réponse contient, pour chaque URL demandée, un flag `isPermitted: bool` et les infos d'organisation (abonné, acheté, etc.).

L'IP de l'utilisateur final doit être transmise côté backend (via header `X-Forwarded-For` ou détection dans FastAPI) — le frontend Next.js ne la connaît pas directement.

## User Scenarios & Testing (Playwright)

*Note: All End-to-End tests must be implemented using **Playwright** framework.*

### User Story 1 - Badge d'accès sur les cartes résultats (Priority: P0)
En tant qu'utilisateur, je veux voir sur chaque résultat si le document est accessible librement, accessible via abonnement institutionnel, ou fermé, afin de savoir sans cliquer si je peux lire le contenu.  
**Why this priority**: Évite les clics frustrés vers des murs payants — valeur UX immédiate.  
**Independent Test**: Après une recherche retournant des résultats, chaque carte affiche un badge d'accès (icône cadenas ouvert / fermé / institutionnel). Le badge est correct vis-à-vis du statut renvoyé par `/permissions`.

### User Story 2 - Chargement asynchrone non bloquant (Priority: P0)
En tant qu'utilisateur, je veux que les résultats s'affichent immédiatement et que les badges d'accès apparaissent ensuite (skeleton → badge), sans que la vérification des permissions retarde l'affichage des résultats.  
**Why this priority**: `/permissions` peut être lent (appel auth.openedition.org) — bloquer l'affichage serait rédhibitoire.  
**Independent Test**: Les résultats s'affichent sans attendre les permissions. Les badges apparaissent dans un second temps, sans flash ni layout shift.

### User Story 3 - Contexte institutionnel (Priority: P1)
En tant qu'utilisateur connecté depuis un réseau institutionnel abonné, je veux que les documents couverts par l'abonnement de mon institution s'affichent comme "accessibles" (pas comme "fermés").  
**Why this priority**: C'est le cas d'usage principal des bibliothèques universitaires — si le badge est faux, l'outil perd sa crédibilité.  
**Independent Test**: Simulation d'une IP correspondant à une organisation abonnée (`purchased=true`) → les documents concernés ont `isPermitted=true` et le badge "accès libre" ou "institutionnel" s'affiche.

### Edge Cases
- Pas de réponse de `/permissions` (timeout, erreur réseau) → les badges restent en état neutre (ex: gris / "inconnu"), sans bloquer l'affichage.
- Résultats sans URL valide → la carte s'affiche normalement, pas de badge.
- Batch de permissions partiel (certaines URLs non retournées) → les URLs manquantes gardent le badge neutre.
- Utilisateur anonyme (pas d'organisation détectée) → badge "accès restreint" sur les documents non libres.

## Requirements

### Functional Requirements
- **FR-001**: Après affichage des résultats, le frontend DOIT envoyer les URLs de la page courante à `GET /permissions` (batch, une seule requête par page de résultats).
- **FR-002**: Chaque `ResultItem` DOIT afficher un badge visuel selon le statut : `open` (cadenas ouvert, vert), `restricted` (cadenas fermé, rouge/orange), `institutional` (bâtiment/institution, bleu).
- **FR-003**: Le chargement des permissions DOIT être non-bloquant — les résultats s'affichent avant les badges (skeleton permissions → badge).
- **FR-004**: L'IP de l'utilisateur DOIT être transmise via un header `X-Forwarded-For` côté serveur Next.js (SSR ou route handler) vers le backend FastAPI.
- **FR-005**: Les badges DOIVENT être traduits (tooltips ou labels) dans les 6 langues.

### Key Entities
- **PermissionStatus**: `open | restricted | institutional | unknown`
- **PermissionsCache**: Cache côté frontend (Map<url, PermissionStatus>) pour éviter les appels dupliqués lors d'un changement de page.

## Success Criteria

### Measurable Outcomes
- **SC-001**: Les badges d'accès apparaissent sur 100% des résultats dans un délai < 1 s après l'affichage des résultats (hors timeout réseau).
- **SC-002**: L'appel à `/permissions` est un seul batch par page (pas N appels pour N résultats).
- **SC-003**: En cas d'erreur `/permissions`, les résultats restent accessibles et fonctionnels — aucun crash.
- **SC-004**: Les labels/tooltips des badges sont correctement traduits dans les 6 langues.

### Tests Playwright (à créer)
| Fichier | Cas à couvrir |
|---|---|
| `tests/permissions.spec.ts` | Badges présents après recherche (mock API), badge open/restricted/institutional corrects selon réponse mockée, chargement non-bloquant (résultats visibles avant badges), erreur /permissions → pas de crash + badge neutre, labels traduits en EN et FR |

# Feature Specification: Recherche sémantique, catégorisation disciplinaire et API mutualisable

**Feature Branch**: `feature/012-semantic-search-api-platform`  
**Created**: 2026-04-21  
**Status**: Backlog prioritaire

## Overview

Le projet doit évoluer d'un moteur de recherche web spécialisé vers une plateforme de recherche réutilisable dans d'autres applications de l'unité. Cette évolution comporte trois axes liés :

1. ajouter une recherche sémantique, en complément de la recherche lexicale Solr existante ;
2. enrichir les documents avec une catégorisation disciplinaire exploitable dans l'UI et dans l'API ;
3. stabiliser l'API comme produit mutualisable, avec une documentation contractuelle et des clients PHP, Python et Node.js.

Le code actuel fournit déjà une base favorable :

- frontend Next.js avec client API centralisé (`front/app/lib/api.ts`) ;
- backend FastAPI typé avec modèles Pydantic et OpenAPI natif (`search_api_solr/app/main.py`, `search_api_solr/app/models/search_models.py`) ;
- moteur lexical Solr distant déjà en production ;
- PostgreSQL et Redis déjà présents pour stocker des métadonnées et accélérer certains flux.

La nouvelle capacité doit rester réaliste par rapport à cette architecture : la recherche sémantique ne remplace pas Solr, elle s'ajoute sous forme de recherche hybride.

## User Scenarios & Testing

### User Story 1 - Recherche hybride sémantique (Priority: P1)

En tant qu'utilisateur, je veux obtenir des résultats pertinents même si mes mots-clés ne correspondent pas exactement au vocabulaire indexé, afin de trouver des contenus proches par sens.
**Why this priority**: C'est l'évolution la plus visible du moteur et elle répond à une limite structurelle d'une recherche purement lexicale.
**Independent Test**: Une requête paraphrasée ou conceptuelle retourne des résultats pertinents via un mode hybride lexical + sémantique, sans régression sur la recherche exacte.

### User Story 2 - Filtrer et explorer par discipline (Priority: P1)

En tant qu'utilisateur, je veux voir la ou les disciplines d'un document et filtrer les résultats par discipline, afin de mieux naviguer dans le corpus.
**Why this priority**: La discipline devient un axe métier transverse pour l'exploration, les facettes et les réusages externes.
**Independent Test**: Les résultats affichent les disciplines disponibles, la facette discipline filtre correctement, et les clients API récupèrent la même information.

### User Story 3 - Réutiliser l'API dans d'autres applications (Priority: P1)

En tant qu'équipe technique de l'unité, je veux intégrer le moteur de recherche dans d'autres applications sans recopier la logique HTTP, afin de mutualiser l'investissement.
**Why this priority**: Le projet doit devenir une brique transverse, pas seulement une interface web autonome.
**Independent Test**: Une application externe peut interroger la recherche, lire les facettes, exploiter les disciplines et l'authentification via un SDK officiel PHP, Python ou Node.js.

### User Story 4 - Gouverner les enrichissements IA (Priority: P2)

En tant qu'administrateur métier, je veux distinguer les disciplines issues des métadonnées sources, celles inférées automatiquement, et celles corrigées manuellement, afin de conserver la confiance dans les résultats.
**Why this priority**: Une catégorisation automatique sans gouvernance dégrade vite la qualité perçue.
**Independent Test**: L'API expose l'origine de la classification et les règles de priorité restent stables.

## Requirements

### Functional Requirements

- **FR-001**: Le système DOIT conserver la recherche lexicale Solr comme socle principal.
- **FR-002**: Le système DOIT ajouter un mode de recherche sémantique ou hybride sans casser le contrat actuel de `/search`.
- **FR-003**: Le backend DOIT pouvoir enrichir chaque document avec un ou plusieurs vecteurs d'embedding calculés hors du chemin critique de requête.
- **FR-004**: Le backend DOIT pouvoir attribuer à un document une ou plusieurs disciplines normalisées.
- **FR-005**: Le système DOIT exploiter en priorité les métadonnées disciplinaires déjà présentes dans les sources quand elles existent.
- **FR-006**: Le système DOIT utiliser une inférence automatique seulement en complément ou fallback des métadonnées existantes.
- **FR-007**: L'API publique DOIT exposer les disciplines et leur provenance (`source_metadata`, `inferred`, `manual_override`).
- **FR-008**: Le frontend DOIT pouvoir afficher les disciplines dans les résultats et proposer une facette discipline.
- **FR-009**: L'API DOIT devenir explicitement versionnée pour les usages externes (`/api/v1/...` ou équivalent documenté avec compatibilité).
- **FR-010**: Le projet DOIT publier un contrat OpenAPI exploitable pour générer ou maintenir des clients officiels.
- **FR-011**: Le projet DOIT fournir des clients officiels PHP, Python et Node.js pour les endpoints publics de recherche, suggestion, facettes, permissions et auth si exposée aux applications tierces.
- **FR-012**: Les SDK DOIVENT couvrir au minimum la configuration, les appels principaux, les erreurs typées et des exemples d'intégration.
- **FR-013**: Les requêtes sémantiques DOIVENT être traçables et désactivables par configuration ou feature flag.

### Non-Functional Requirements

- **NFR-001**: La recherche hybride DOIT rester compatible avec l'infrastructure existante `FastAPI + Solr + PostgreSQL + Redis`.
- **NFR-002**: Les embeddings DOIVENT être calculés dans une pipeline asynchrone d'indexation/enrichissement, pas pendant une requête utilisateur.
- **NFR-003**: Le stockage vectoriel DOIT reposer sur une technologie réaliste pour l'équipe et l'infra ; le choix cible prioritaire est `pgvector` sur PostgreSQL existant.
- **NFR-004**: Le modèle d'embedding DOIT être multilingue et auto-hébergeable ; les choix cibles réalistes sont `bge-m3` ou `multilingual-e5`.
- **NFR-005**: La classification disciplinaire DOIT commencer par une taxonomie limitée, stable et validée métier, plutôt qu'une ontologie ouverte trop ambitieuse.
- **NFR-006**: Les SDK DOIVENT être générés ou régénérables à partir du contrat OpenAPI pour éviter trois implémentations divergentes.
- **NFR-007**: Toute évolution de contrat DOIT être versionnée et testée pour éviter les régressions côté applications consommatrices.

## Key Entities

- **Discipline**: catégorie métier normalisée, identifiée par un code stable, un libellé multilingue et un niveau éventuel dans la taxonomie.
- **DocumentEnrichment**: enrichissements calculés pour un document : embeddings, disciplines, score de confiance, provenance.
- **SearchMode**: `lexical`, `semantic`, `hybrid`.
- **ApiClientPackage**: paquet SDK officiel pour `php`, `python`, `node`.
- **ContractVersion**: version explicite du contrat d'API et des SDK associés.

## Technical Direction

### Choix techniques réalistes pour ce projet

- **Recherche lexicale**: Apache Solr reste la source de vérité pour le filtrage, les facettes et la recherche exacte.
- **Recherche sémantique**: ajout d'un index vectoriel parallèle stocké en PostgreSQL via `pgvector`, interrogé par le backend FastAPI.
- **Fusion des résultats**: stratégie hybride côté backend avec pondération configurable entre score lexical Solr et score sémantique.
- **Embeddings**: service Python d'enrichissement batch/asynchrone s'appuyant sur `sentence-transformers`.
- **Catégorisation disciplinaire**:
  - phase 1: mapping depuis les métadonnées existantes si disponibles ;
  - phase 2: classification automatique supervisée ou zero-shot guidée par taxonomie restreinte ;
  - phase 3: overrides manuels si besoin métier.
- **SDKs**: génération depuis OpenAPI avec `openapi-generator` ou outil équivalent, puis couche minimale de packaging/documentation par langage.

### Pourquoi ce choix

- Le backend est déjà en Python, ce qui rend l'enrichissement embeddings/classification plus cohérent que d'ajouter un nouveau runtime principal.
- PostgreSQL existe déjà dans la stack ; `pgvector` évite d'introduire trop tôt une nouvelle base spécialisée.
- Solr est distant et déjà intégré ; le remplacer ou le transformer en moteur vectoriel principal serait plus risqué que de lui adjoindre une couche vectorielle.
- FastAPI expose déjà un schéma OpenAPI natif ; c'est le meilleur point d'appui pour des SDKs réalistes à court terme.

## API Evolution

### Évolutions minimales attendues

- Ajouter un paramètre explicite de mode de recherche : `mode=lexical|semantic|hybrid`.
- Étendre le modèle de document retourné avec :
  - `disciplines`
  - `discipline_source`
  - `semantic_score` si pertinent
- Publier une documentation d'API versionnée destinée à d'autres applications.
- Préserver les usages frontend actuels via compatibilité ascendante pendant la migration.

### Endpoints cibles

| Méthode | Path cible | Rôle |
|---|---|---|
| `POST` | `/api/v1/search` | Recherche versionnée avec mode lexical/sémantique/hybride |
| `GET` | `/api/v1/search` | Variante URL-friendly pour intégrations simples |
| `GET` | `/api/v1/suggest` | Suggestions |
| `GET` | `/api/v1/facets/config` | Configuration des facettes et champs |
| `GET` | `/api/v1/permissions` | Permissions documentaires |
| `GET` | `/api/v1/openapi.json` | Contrat de génération SDK |

## Success Criteria

- **SC-001**: Une requête conceptuelle ou paraphrasée améliore le rappel par rapport au mode lexical seul sur un jeu d'évaluation métier.
- **SC-002**: Au moins 90 % des documents exposés par l'API ont une discipline exploitable, issue des métadonnées ou d'une inférence.
- **SC-003**: Les résultats de recherche exposent les disciplines sans régression pour le frontend actuel.
- **SC-004**: Les applications externes peuvent consommer l'API via un SDK PHP, Python ou Node.js sans écrire de client HTTP spécifique.
- **SC-005**: Les SDKs sont générés depuis le même contrat OpenAPI et versionnés conjointement avec l'API.
- **SC-006**: Le mode sémantique peut être activé progressivement par environnement et désactivé sans interrompre la recherche lexicale.

## Risks and Guardrails

- Ne pas promettre une qualité sémantique générale sans corpus d'évaluation métier.
- Ne pas inventer une taxonomie trop fine avant validation par les équipes documentaires.
- Ne pas rendre la recherche synchrone dépendante du calcul d'embeddings.
- Ne pas maintenir trois SDKs entièrement artisanaux ; partir d'une génération contract-first.
- Ne pas casser les contrats déjà consommés par le frontend Next.js pendant la phase de transition.

## Dependencies

- Dépend de `001-search-core` et `002-advanced-search-suite` pour les flux de recherche existants.
- Dépend de `TECHNICAL_REQUIREMENTS.md` pour la gouvernance des contrats, tests et qualité.
- Impacte potentiellement `docs/ARCHITECTURE.md`, la documentation d'environnement et les pipelines d'indexation à venir.

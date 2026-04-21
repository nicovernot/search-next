# Plan 012 — Recherche sémantique, catégorisation disciplinaire et API mutualisable

## Intent

Faire évoluer l'application actuelle en plateforme de recherche hybride réutilisable sans remettre en cause les fondations déjà stables :

- `front/app/lib/api.ts` centralise déjà la consommation HTTP côté frontend ;
- `search_api_solr/app/main.py` expose déjà des endpoints FastAPI compatibles OpenAPI ;
- `search_api_solr/app/models/search_models.py` fournit une base typée à étendre ;
- Solr reste le moteur lexical, PostgreSQL et Redis sont déjà présents dans la stack.

## Target Architecture

```
Applications web et tierces
├── Frontend Next.js existant
├── SDK Node.js
├── SDK Python
└── SDK PHP
          │
          ▼
FastAPI Search Platform
├── API versionnée /api/v1
├── Recherche lexicale via Solr
├── Recherche vectorielle via PostgreSQL + pgvector
├── Fusion hybride des scores
└── Contrat OpenAPI + génération SDK
          │
          ├── Solr distant (index lexical)
          ├── PostgreSQL (users, saved searches, enrichissements, vecteurs)
          └── Redis (cache, états temporaires)

Pipeline d'enrichissement asynchrone
├── extraction texte/métadonnées
├── mapping discipline depuis source
├── classification complémentaire
└── calcul d'embeddings multilingues
```

## Phases

### Phase 0 - Cadrage métier et technique

1. Recenser les métadonnées disciplinaires déjà disponibles dans les documents Solr.
2. Définir une taxonomie cible réaliste, courte et gouvernable.
3. Constituer un jeu d'évaluation métier pour comparer lexical vs hybride.
4. Décider officiellement du mode de versionnement API et du périmètre public des endpoints.

### Phase 1 - Stabilisation de l'API comme produit

> **Point de départ** : `app/api/v1/saved_searches.py` existe déjà sous `/api/v1/`. En revanche, `/search`, `/suggest` et `/facets/config` sont encore définis à la racine dans `main.py`. La Phase 1 doit consolider ce namespace partiel avant tout usage externe.

> **Prérequis technique identifié** : `SearchResponse.results` est actuellement `list[Any]`. Tant que ce champ n'est pas typé `list[DocumentResponse]`, le contrat OpenAPI n'expose pas la structure réelle des documents — les disciplines ajoutées en Phase 2 seraient invisibles du schéma. Ce typage doit être résolu en Phase 1 avant de publier l'OpenAPI de référence.

1. Déplacer `/search`, `/suggest`, `/facets/config` sous `app/api/v1/` avec compatibilité ascendante (alias ou redirection depuis les routes racine le temps de la transition frontend).
2. Typer `SearchResponse.results` en `list[DocumentResponse]` pour rendre le contrat document exploitable par OpenAPI et les SDKs.
3. Compléter les `response_model` publics pour les endpoints encore implicites.
4. Publier un `openapi.json` versionné et documenté.
5. Décider si `/auth/*` est exposé aux applications tierces (SDK) ou réservé au frontend — documenter dans "Decisions Already Recommended".
6. Décrire les erreurs, quotas et modes d'auth (JWT uniquement — pas d'API key dans la stack actuelle) des endpoints destinés aux applications tierces.
7. Préparer des exemples d'intégration hors frontend Next.js.

### Phase 2 - Socle disciplinaire

> **Prérequis** : taxonomie validée (Phase 0) + `SearchResponse.results` typé (Phase 1).

> **Types à figer avant implémentation** : `discipline_confidence: float` (0.0–1.0), `discipline_source: Literal["source_metadata", "inferred", "manual_override"]`, `disciplines: list[str]` (codes taxonomie stables). Ces types doivent être décidés avant l'écriture du modèle pour garantir la stabilité du contrat (NFR-007).

1. Auditer les champs disciplinaires disponibles dans les documents Solr existants (ex : `subject`, `keywords`, domaines HAL, classifications éditeur) — résultat documenté dans "Decisions Already Recommended".
2. Ajouter les champs `disciplines`, `discipline_source`, `discipline_confidence` aux modèles backend (`document.py`, `search_models.py`).
3. Étendre la normalisation des résultats pour propager ces champs jusqu'au frontend (`front/app/types.ts`, `ResultItem.tsx`).
4. Ajouter une facette discipline à la config backend (`facets_json/`) et à l'UI (`Facets.tsx`).
5. Implémenter le mapping niveau 1 (métadonnées source Solr).
6. Prévoir un mécanisme d'override manuel, même s'il est opéré d'abord hors UI.

### Phase 3 - Pipeline d'enrichissement IA

> **Prérequis** : taxonomie validée (Phase 0) + modèle disciplinaire en base (Phase 2) + modèle d'embedding choisi (Phase 0).

> **Architecture pipeline** : le job d'enrichissement s'exécute comme script CLI Python autonome (hors chemin HTTP), ce qui le rend compatible avec la session SQLAlchemy synchrone existante (`db/session.py`). Aucune migration vers `create_async_engine` n'est requise pour cette phase. Si une intégration async future est nécessaire, elle fera l'objet d'une spec dédiée.

> **Dépendances à ajouter** :
> - `pgvector>=0.3.0` dans `requirements.txt` (client Python pour pgvector)
> - `sentence-transformers>=3.0` dans `requirements.txt`
> - Extension PostgreSQL : migration Alembic `CREATE EXTENSION IF NOT EXISTS vector` (vérifier compatibilité version PG de l'infra cible)

1. Vérifier que la version PostgreSQL de l'infra supporte `pgvector` (≥ PG 14 recommandé).
2. Ajouter `pgvector>=0.3.0` et `sentence-transformers>=3.0` à `requirements.txt`.
3. Créer une migration Alembic activant l'extension `vector` et la table d'enrichissement documentaire (`document_enrichments` : `doc_id`, `embedding vector(N)`, `disciplines`, `discipline_source`, `discipline_confidence`, `model_version`, `computed_at`).
4. Implémenter un job Python CLI d'embeddings sur batch documentaire (entrée : liste de docs Solr, sortie : vecteurs en PG).
5. Implémenter un classifieur disciplinaire niveau 2 guidé par la taxonomie validée en Phase 0.
6. Stocker provenance, version du modèle, horodatage et score de confiance pour chaque enrichissement.

### Phase 4 - Recherche hybride

> **Stratégie de fusion recommandée** : **RRF (Reciprocal Rank Fusion)**. Robuste car ne requiert pas de normalisation des scores (scores Solr et pgvector sont sur des échelles différentes). Formule : `score_rrf = Σ 1/(k + rank_i)` avec `k=60` par défaut. Alternative linéaire pondérée si les scores sont normalisés — à décider et documenter dans "Decisions Already Recommended" avant implémentation.

> **Feature flag** : ajouter `semantic_search_enabled: bool = False` dans `search_api_solr/app/settings.py` (modèle `Settings` Pydantic). Désactivé par défaut, activable par variable d'environnement `SEMANTIC_SEARCH_ENABLED=true`. Quand désactivé, le mode `semantic` et `hybrid` retournent une erreur 501 ou basculent silencieusement en `lexical`.

1. Ajouter `semantic_search_enabled: bool = False` à `Settings` dans `settings.py`.
2. Ajouter `SearchMode: Literal["lexical", "semantic", "hybrid"] = "lexical"` au modèle `SearchRequest`.
3. Implémenter la requête vectorielle pgvector dans `search_service.py` (calcul de l'embedding de la requête, recherche ANN dans pgvector).
4. Fusionner les résultats Solr et pgvector via RRF (ou stratégie décidée en Phase 0).
5. Exposer `semantic_score` dans les réponses de debug ; masquer en mode production si non pertinent pour l'UI publique.
6. Déployer derrière le feature flag `semantic_search_enabled` — vérifier que le mode `lexical` n'est jamais dégradé si le flag est désactivé.

### Phase 5 - SDKs officiels

1. Générer un client Node.js/TypeScript à partir d'OpenAPI.
2. Générer un client Python.
3. Générer un client PHP.
4. Ajouter packaging, versioning, exemples et guide d'usage minimal pour chaque SDK.
5. Mettre en place une vérification CI garantissant que les SDKs restent synchronisés avec l'OpenAPI.

## Deliverables

| Lot | Sortie attendue |
|---|---|
| API platform | endpoints versionnés + OpenAPI stabilisé |
| Métadonnées | disciplines exposées dans les réponses |
| IA | pipeline embeddings + classification |
| Recherche | mode `semantic` et `hybrid` exploitable |
| Intégration | SDKs `node`, `python`, `php` + exemples |

## Code Impact Map

| Zone actuelle | Impact attendu |
|---|---|
| `search_api_solr/app/main.py` | versionnement API, nouveaux endpoints ou alias, nouveaux paramètres |
| `search_api_solr/app/models/search_models.py` | ajout de `SearchMode`, enrichissement des réponses, schémas SDK |
| `search_api_solr/app/models/document.py` | ajout des champs discipline et scores associés |
| `search_api_solr/app/services/search_service.py` | fusion lexical + sémantique |
| `search_api_solr/app/services/solr_client.py` | inchangé en socle, éventuels ajustements de récupération de métadonnées |
| `front/app/lib/api.ts` | support du mode de recherche et de la nouvelle API versionnée |
| `front/app/types.ts` | nouvelles propriétés documentaires |
| `front/app/components/Facets.tsx` et `ResultItem.tsx` | affichage et filtrage par discipline |

## Recommended Order

1. Stabiliser l'API publique et le contrat OpenAPI.
2. Ajouter la discipline dans le modèle documentaire sans activer encore la sémantique.
3. Mettre en place la pipeline d'enrichissement et `pgvector`.
4. Activer le mode hybride derrière feature flag.
5. Générer et publier les SDKs.

## Decisions Already Recommended

- Garder Solr pour le lexical.
- Utiliser PostgreSQL + `pgvector` pour le vectoriel.
- Utiliser Python pour l'enrichissement et la classification.
- Générer les SDKs depuis OpenAPI au lieu d'écrire trois clients divergents.
- Démarrer avec une taxonomie disciplinaire restreinte et validée métier.
- Pipeline d'enrichissement = script CLI Python autonome (sync, hors FastAPI) — pas de migration async DB pour cette phase.
- `discipline_confidence` : `float` 0.0–1.0 ; `discipline_source` : `Literal["source_metadata", "inferred", "manual_override"]`.
- Feature flag sémantique : champ `semantic_search_enabled: bool = False` dans `Settings`, variable d'env `SEMANTIC_SEARCH_ENABLED`.
- Stratégie de fusion hybride : **RRF (k=60)** — à confirmer ou remplacer après Phase 0 selon le corpus d'évaluation.

**Décisions en attente (Phase 0) :**
- Modèle d'embedding : `bge-m3` (lourd, SOTA multilingue) vs `multilingual-e5-large` (plus léger, bon compromis) — à choisir selon contraintes mémoire/GPU de l'infra.
- Champs Solr disciplinaires disponibles : à auditer avant Phase 2.
- Exposition de `/auth/*` dans les SDKs : oui (JWT tiers) ou non (frontend uniquement) — décision métier/sécurité.

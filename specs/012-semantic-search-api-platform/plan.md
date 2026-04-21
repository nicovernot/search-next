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

1. Auditer le schéma Solr : recenser les champs disponibles, en particulier les champs disciplinaires (`subject`, `keywords`, domaines HAL, classifications éditeur) et les champs textuels exploitables pour l'embedding (`title`, `overview`, abstracts). Documenter les champs retenus dans "Decisions Already Recommended".
2. Définir une taxonomie cible réaliste, courte et gouvernable (≤ 30 disciplines, codes stables, libellés fr/en).
3. Constituer un jeu d'évaluation métier (≥ 50 requêtes avec résultats attendus) pour comparer lexical vs hybride.
4. Choisir le modèle d'embedding (`bge-m3` vs `multilingual-e5-large`) selon les contraintes mémoire/GPU de l'infra.
5. Confirmer ou ajuster la stratégie de fusion hybride (RRF k=60 recommandé).
6. Décider officiellement du mode de versionnement API et du périmètre public des endpoints (dont exposition de `/auth/*` dans les SDKs).

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

#### Stratégie d'indexation

**Parcours du corpus Solr — cursor-based pagination obligatoire**

Le `SolrClient` actuel n'expose qu'une méthode `search()` générique. Pour exporter le corpus entier depuis le Solr distant (`solrslave-sec.labocleo.org`), le job doit utiliser la pagination par curseur Solr (`cursorMark`) :

```
GET /solr/documents/select?q=*:*&sort=id asc&rows=500&cursorMark=*
→ répéter avec cursorMark=<nextCursorMark> jusqu'à cursorMark stable
```

L'approche `start` offset classique est **interdite** sur un grand corpus (explosion mémoire côté Solr au-delà de ~10 000 docs). Le `SolrClient` doit être étendu avec une méthode `export_cursor()` dédiée, ou le job CLI utilise `httpx` directement sans passer par le client FastAPI.

**Champs Solr à embarquer**

À auditer en Phase 0. Candidats prioritaires basés sur `DocumentBase` existant :
- `title` (présent dans tous les types de documents)
- `overview` (max 500 chars, déjà normalisé dans le modèle)
- `subtitle` si disponible dans Solr

Champs à exclure de l'embedding : `url`, `platformID`, `access_type`, `date`, `isbn_*` — pas de valeur sémantique.

**Texte d'entrée de l'embedding** : concaténation `f"{title}. {subtitle or ''}. {overview or ''}"` après nettoyage des `None`. Décision finale après audit Phase 0.

**Gestion des mises à jour — stratégie incrémentale**

Trois niveaux, du plus simple au plus complet :

| Niveau | Mécanisme | Déclenchement | Couverture |
|---|---|---|---|
| **L1 — Polling périodique** | `datemisenligne:[{last_run} TO NOW]` (champ déjà dans `DocumentBase`) | Cron nightly | Docs récents uniquement |
| **L2 — Ré-indexation complète planifiée** | Relancer le job cursor complet | Cron hebdomadaire ou manuel | Corpus entier |
| **L3 — Événementiel** | Hook Solr DataImportHandler ou signal applicatif | À chaque mise à jour Solr | Temps réel |

**Recommandation** : démarrer avec L1 (polling nightly sur `datemisenligne`) + L2 (ré-indexation complète hebdomadaire le weekend). L3 implique de modifier la configuration Solr distante — hors périmètre Phase 3.

**Ré-indexation après changement de modèle**

Le champ `model_version` dans `document_enrichments` permet d'identifier les vecteurs obsolètes :
```sql
SELECT doc_id FROM document_enrichments WHERE model_version != 'bge-m3-v1'
```
Un sous-job de ré-indexation ciblée est relancé sur ces documents. La table garde toujours la version la plus récente (upsert sur `doc_id + model_version`).

**Taille de batch et performance**

- Batch Solr : 500 docs/requête (limite conservative pour le Solr distant)
- Batch embedding : 32–64 docs selon la VRAM disponible (paramètre configurable)
- Écriture PG : upsert par batch de 500 via `execute_many`
- Estimation pour 100 000 docs : ~3–5h sur CPU, ~20–40min sur GPU modeste

1. Vérifier que la version PostgreSQL de l'infra supporte `pgvector` (≥ PG 14 recommandé).
2. Ajouter `pgvector>=0.3.0` et `sentence-transformers>=3.0` à `requirements.txt`.
3. Créer une migration Alembic activant l'extension `vector` et la table `document_enrichments` (`doc_id`, `embedding vector(N)`, `disciplines`, `discipline_source`, `discipline_confidence`, `model_version`, `computed_at`, `text_input` pour traçabilité).
4. Étendre `SolrClient` ou créer un client export dédié avec méthode `export_cursor(batch_size, fields)` utilisant `cursorMark`.
5. Implémenter le job CLI `enrichment_job.py` : cursor Solr → extraction texte → batch embedding → upsert pgvector.
6. Implémenter le cron L1 (polling nightly sur `datemisenligne`) et L2 (ré-indexation complète hebdomadaire).
7. Implémenter le classifieur disciplinaire niveau 2 guidé par la taxonomie validée en Phase 0.
8. Stocker provenance, version du modèle, `text_input`, horodatage et score de confiance pour chaque enrichissement.

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

- Export Solr par **cursor-based pagination** (`cursorMark` + `sort=id asc`) — l'offset classique est interdit sur grand corpus.
- Texte d'entrée embedding : `f"{title}. {subtitle or ''}. {overview or ''}"` (décision provisoire, à confirmer après audit Phase 0).
- Stratégie de mises à jour : L1 polling nightly (`datemisenligne`) + L2 ré-indexation complète hebdomadaire. L3 événementiel hors périmètre Phase 3.
- Batch Solr : 500 docs/requête. Batch embedding : 32–64 docs (paramétrable).
- Upsert pgvector : `INSERT ... ON CONFLICT (doc_id, model_version) DO UPDATE`.

**Décisions en attente (Phase 0) :**
- Modèle d'embedding : `bge-m3` (lourd, SOTA multilingue) vs `multilingual-e5-large` (plus léger, bon compromis) — à choisir selon contraintes mémoire/GPU de l'infra.
- Champs Solr disciplinaires et textuels disponibles : à auditer avant Phase 2.
- Exposition de `/auth/*` dans les SDKs : oui (JWT tiers) ou non (frontend uniquement) — décision métier/sécurité.

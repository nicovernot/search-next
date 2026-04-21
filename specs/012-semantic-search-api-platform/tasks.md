# Tasks 012 — Phase 1 : Stabilisation de l'API comme produit

**Statut**: À faire — prérequis : Phase 0 (périmètre endpoints décidé)  
**Skill associé**: SKILL 9 — VersionnerAPIPubliqueRésultat  
**Dépendances code** : `search_api_solr/app/main.py`, `app/api/v1/`, `app/models/search_models.py`

---

## Phase 0 — Cadrage (avant tout démarrage Phase 1)

- [ ] Auditer les champs disciplinaires disponibles dans les documents Solr (chercher : `subject`, `keywords`, `discipline`, classifications HAL, domaines éditeur) — documenter les champs trouvés dans `plan.md`
- [ ] Valider la taxonomie disciplinaire avec les équipes métier (≤ 30 disciplines stables, codes normalisés, libellés multilingues fr/en minimum)
- [ ] Choisir le modèle d'embedding : `bge-m3` vs `multilingual-e5-large` — documenter le choix et la contrainte infra (mémoire/GPU)
- [ ] Décider si `/auth/*` est exposé dans les SDKs ou réservé au frontend — documenter
- [ ] Décider du périmètre exact des endpoints publics tiers vs internes
- [ ] Confirmer ou ajuster la stratégie de fusion hybride (RRF k=60 recommandé)
- [ ] Documenter toutes ces décisions dans `plan.md` § "Decisions Already Recommended"
- [ ] Constituer le jeu d'évaluation lexical vs hybride (≥ 50 requêtes métier avec résultats attendus)

---

## Phase 1 — Consolidation `/api/v1` et publication OpenAPI

### 1.1 — Déplacement des endpoints sous `/api/v1/`

- [ ] Créer `search_api_solr/app/api/v1/search.py` avec les routes `POST /search` et `GET /search`
- [ ] Créer `search_api_solr/app/api/v1/suggest.py` avec la route `GET /suggest`
- [ ] Créer `search_api_solr/app/api/v1/facets.py` avec la route `GET /facets/config`
- [ ] Inclure les nouveaux routers dans `main.py` sous le préfixe `/api/v1`
- [ ] Ajouter des aliases de compatibilité sur les routes racine (`/search`, `/suggest`, `/facets/config`) le temps de la transition frontend
- [ ] Vérifier que `saved_searches` (déjà sous `/api/v1/`) reste inchangé

### 1.2 — Typer `SearchResponse.results` et compléter les `response_model`

- [ ] Typer `SearchResponse.results` en `list[DocumentResponse]` dans `search_models.py` (prérequis pour que le schéma OpenAPI expose la structure des documents et les champs disciplines à venir)
- [ ] Vérifier que tous les endpoints `/api/v1/*` déclarent un `response_model` Pydantic explicite
- [ ] Documenter les erreurs HTTP stables par endpoint (400, 401, 403, 404, 422, 503) via `responses=`
- [ ] Documenter les modes d'auth requis par endpoint (JWT uniquement — pas d'API key dans la stack actuelle)

### 1.3 — Publication du contrat OpenAPI

- [ ] Exposer `/api/v1/openapi.json` (route dédiée ou export du schéma FastAPI)
- [ ] Vérifier que le schéma généré est exploitable pour `openapi-generator`
- [ ] Ajouter un exemple d'intégration hors frontend Next.js dans `docs/` ou `README.md`

### 1.4 — Tests et compatibilité

- [ ] Adapter les tests backend existants aux nouvelles routes `/api/v1/*`
- [ ] Ajouter un test vérifiant que les routes racine (alias) retournent les mêmes réponses
- [ ] Ajouter un test Playwright vérifiant que le frontend continue de fonctionner sans régression
- [ ] Lancer `make test` et `pnpm run test:e2e` — suite verte ou écarts documentés

### 1.5 — Mise à jour des specs et docs

- [ ] Mettre à jour `docs/ARCHITECTURE.md` avec le nouveau namespace `/api/v1`
- [ ] Marquer Ph.1 comme ✅ dans `specs/PLANNING.md`
- [ ] Mettre à jour `specs/012-semantic-search-api-platform/tasks.md` (ce fichier) : démarrer les tasks Phase 2

---

## Phase 2 — Socle disciplinaire (à détailler après Phase 1 + taxonomie validée)

> Prérequis : Phase 0 (taxonomie + audit Solr) + Phase 1 (`SearchResponse.results` typé).

### 2.1 — Schéma PostgreSQL et taxonomie

- [ ] Créer la migration Alembic pour la table `discipline` (code PK, label_fr, label_en, parent_code auto-référentiel)
- [ ] Peupler la table `discipline` depuis la taxonomie validée en Phase 0 (script de seed ou fixture Alembic)
- [ ] Créer la migration Alembic pour la table `document_enrichment` :
  - `doc_id VARCHAR` (clé Solr — pas de FK SQL, cohérence garantie par le pipeline)
  - `model_version VARCHAR`
  - `embedding vector(N)` (N = 768 pour multilingual-e5-large, 1024 pour bge-m3)
  - `disciplines VARCHAR[]` (codes depuis `discipline.code`)
  - `discipline_source VARCHAR`, `discipline_confidence FLOAT`, `text_input TEXT`, `computed_at TIMESTAMPTZ`
  - Contrainte `UNIQUE (doc_id, model_version)` — permet la coexistence de plusieurs versions pendant ré-indexation
  - Index `ivfflat (embedding vector_cosine_ops)` avec `lists = sqrt(nb_docs_estimé)`
  - Index classique sur `doc_id`

### 2.2 — Modèles Pydantic et SQLAlchemy

- [ ] Créer `app/models/document_enrichment.py` (SQLAlchemy ORM, conventions `Base` existantes)
- [ ] Figer les types Pydantic : `disciplines: list[str]`, `discipline_source: Literal["source_metadata", "inferred", "manual_override"]`, `discipline_confidence: float | None`
- [ ] Ajouter ces champs à `document.py` (`DocumentBase`) — optionnels (`= None`) pour rétrocompatibilité
- [ ] Ajouter `active_model_version: str` à `Settings` pour que le service sache quelle version lire

### 2.3 — Enrichissement au moment de la réponse (merge Solr ↔ PG)

- [ ] Implémenter `SearchService._enrich_with_pg(solr_docs, db)` :
  - Requête `IN` sur les `doc_id` des résultats courants (≤ `page_size`, coût négligeable)
  - Filtre sur `model_version == settings.active_model_version`
  - Merge des champs disciplines dans chaque doc Solr
  - Fallback gracieux si enrichissement absent (nouveau doc non encore indexé) : `disciplines=[]`
- [ ] Injecter la session DB dans `SearchService` via `Depends(get_db)` (pattern existant dans le projet)

### 2.4 — Frontend et facette discipline

- [ ] Propager les champs disciplines jusqu'au frontend : `front/app/types.ts`, `ResultItem.tsx`
- [ ] Ajouter la facette discipline à la config backend (`facets_json/`) et à l'UI (`Facets.tsx`)
  - La facette discipline est servie depuis PostgreSQL (pas Solr) — requête `GROUP BY unnest(disciplines)`
- [ ] Implémenter le mapping niveau 1 depuis les champs Solr audités en Phase 0 (dans le pipeline batch)

### 2.5 — Override manuel

- [ ] Prévoir le mécanisme d'override manuel via `discipline_source = "manual_override"` — hors UI dans un premier temps (opéré par requête SQL ou script admin)
- [ ] Marquer Ph.2 comme ✅ dans `specs/PLANNING.md`

---

## Phase 3 — Pipeline d'enrichissement IA (à détailler après Phase 2)

> Prérequis : Phase 0 (modèle embedding choisi, champs Solr audités, taxonomie) + Phase 2 (modèle disciplinaire en base).

### 3.1 — Infrastructure

- [ ] Vérifier la version PostgreSQL de l'infra cible (pgvector requiert PG ≥ 14)
- [ ] Ajouter `pgvector>=0.3.0` et `sentence-transformers>=3.0` à `requirements.txt`
- [ ] Vérifier que la migration Phase 2 a bien créé `document_enrichment` avec l'extension `vector` et l'index `ivfflat`
- [ ] Calibrer le paramètre `lists` de l'index `ivfflat` selon le nombre de documents estimés (`lists ≈ sqrt(nb_docs)` : 100 pour 10k docs, 316 pour 100k docs)

### 3.2 — Export Solr par curseur

- [ ] Étendre `SolrClient` avec une méthode `export_cursor(fields, batch_size=500)` utilisant `cursorMark` Solr
  - Paramètres : `q=*:*`, `sort=id asc`, `rows=500`, `cursorMark=*` → itérer jusqu'à `cursorMark` stable
  - Champs à récupérer : `id`, `title`, `subtitle`, `overview` (+ champs disciplinaires audités en Phase 0)
  - **Ne pas utiliser** l'offset `start` classique (explosion mémoire Solr > 10 000 docs)
- [ ] Valider que le Solr distant accepte les requêtes cursor (droits, config `sort` obligatoire sur champ unique)

### 3.3 — Job CLI d'indexation

- [ ] Créer `search_api_solr/scripts/enrichment_job.py` (script CLI autonome, session DB synchrone)
  - Mode **full** : cursor complet sur tout le corpus
  - Mode **incremental** : filtre `datemisenligne:[{last_run} TO NOW]` (champ existant dans `DocumentBase`)
  - Batch embedding : 32–64 docs selon VRAM, configurable via argument CLI
  - Texte d'entrée : `f"{title}. {subtitle or ''}. {overview or ''}"` après nettoyage `None`
  - Upsert pgvector par batch de 500 (`INSERT ... ON CONFLICT (doc_id, model_version) DO UPDATE`)
- [ ] Stocker `text_input` utilisé pour traçabilité et débogage de qualité
- [ ] Ajouter `--dry-run` pour estimer le nombre de docs sans écrire en base

### 3.4 — Stratégie de mises à jour

- [ ] Configurer le cron **L1 — polling nightly** : relancer le mode `incremental` chaque nuit
- [ ] Configurer le cron **L2 — ré-indexation complète** hebdomadaire (weekend, hors heures de pointe)
- [ ] Documenter la procédure de ré-indexation après changement de modèle :
  - Requête des docs obsolètes : `SELECT doc_id FROM document_enrichments WHERE model_version != '{new_version}'`
  - Relancer le job en mode ciblé sur ces `doc_id`

### 3.5 — Classifieur disciplinaire

- [ ] Implémenter le classifieur niveau 2 guidé par taxonomie (zero-shot ou supervisé selon corpus d'éval Phase 0)
- [ ] Stocker provenance, version modèle, horodatage et score de confiance

### 3.6 — Validation

- [ ] Vérifier la couverture : `SELECT COUNT(*) FROM document_enrichments` vs `numFound` Solr
- [ ] Valider le critère SC-002 : ≥ 90 % des documents ont une discipline exploitable
- [ ] Marquer Ph.3 comme ✅ dans `specs/PLANNING.md`

---

## Phase 4 — Recherche hybride (à détailler après Phase 3)

> Prérequis : Phase 3 (pgvector actif + embeddings calculés).

- [ ] Ajouter `semantic_search_enabled: bool = False` dans `Settings` (`settings.py`) + variable d'env `SEMANTIC_SEARCH_ENABLED`
- [ ] Ajouter `mode: Literal["lexical", "semantic", "hybrid"] = "lexical"` à `SearchRequest`
- [ ] Implémenter la requête vectorielle pgvector dans `search_service.py` (embed de la requête → recherche ANN)
- [ ] Implémenter la fusion RRF (k=60) entre résultats Solr et pgvector
- [ ] Exposer `semantic_score` en debug, masquer si non pertinent côté UI publique
- [ ] Vérifier que le mode `lexical` n'est jamais dégradé quand `semantic_search_enabled=False`
- [ ] Ajouter tests backend pour les trois modes (`lexical`, `semantic`, `hybrid`)
- [ ] Marquer Ph.4 comme ✅ dans `specs/PLANNING.md`

---

## Phase 5 — SDKs officiels (à détailler après Phase 4)

> Prérequis : Phase 1 (OpenAPI stable) + Phase 4 (contrat figé avec SearchMode et disciplines).

- [ ] Générer le client Node.js/TypeScript depuis `openapi.json` via `openapi-generator`
- [ ] Générer le client Python
- [ ] Générer le client PHP
- [ ] Packager, versionner, documenter chaque SDK
- [ ] Mettre en place la vérification CI garantissant la synchronisation SDK ↔ OpenAPI
- [ ] Marquer Ph.5 comme ✅ dans `specs/PLANNING.md`

---

## Définition de terminé — Phase 1

- [ ] Routes `/api/v1/*` opérationnelles et testées
- [ ] Aliases de compatibilité racine fonctionnels
- [ ] `openapi.json` exportable et valide pour génération SDK
- [ ] `make test` vert
- [ ] `pnpm run test:e2e` vert ou écarts documentés
- [ ] `PLANNING.md` et `ARCHITECTURE.md` mis à jour

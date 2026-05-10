# Tasks 012 — Phase 1 : Stabilisation de l'API comme produit

**Statut**: Phase 1 ✅ livrée (2026-05-05) — Phase 0 cadrage en cours (taxonomie + audit Solr + modèle embedding restants) — Phase 2 à faire
**Skill associé**: SKILL 9 — VersionnerAPIPubliqueRésultat  
**Dépendances code** : `search_api_solr/app/main.py`, `app/api/v1/`, `app/models/search_models.py`

---

## Phase 0 — Cadrage (avant tout démarrage Phase 1)

- [x] Auditer les champs disciplinaires disponibles dans les documents Solr — **aucun champ discipline dans `fl` actuel** ; candidats textuels : `naked_titre`, `naked_soustitre`, `naked_resume` ; vérification manuelle `fl=*` requise sur Solr de staging avant Phase 2 (voir `plan.md` § Phase 0)
- [ ] **[métier]** Valider la taxonomie disciplinaire avec les équipes métier — proposition 25 disciplines documentée dans `plan.md` § Phase 0 ; codes + libellés fr/en à confirmer
- [x] Choisir le modèle d'embedding : **`multilingual-e5-large`** — 768 dims, 560M params, ~2.2 GB VRAM, compatible sentence-transformers 3.x (voir `plan.md` § Phase 0)
- [x] Décider si `/auth/*` est exposé dans les SDKs ou réservé au frontend — réservé au frontend en Phase 1
- [x] Décider du périmètre exact des endpoints publics tiers vs internes — recherche, suggest, facettes, permissions, OpenAPI
- [x] Confirmer si `saved_searches` doit rester public sous `/api/v1/saved-searches` ou rester réservé au frontend authentifié — monté sous v1, authentifié, hors SDK public Phase 1
- [x] Confirmer ou ajuster la stratégie de fusion hybride (RRF k=60 recommandé) — RRF k=60 conservé comme défaut cible
- [x] Documenter toutes ces décisions dans `plan.md` § "Decisions Already Recommended"
- [x] Constituer le jeu d'évaluation lexical vs hybride — template 50 requêtes créé dans `checklists/eval-corpus.md` ; **[métier] à renseigner par les équipes avant Phase 4**

---

## Phase 1 — Consolidation `/api/v1` et publication OpenAPI

### 1.1 — Déplacement des endpoints sous `/api/v1/`

- [x] Créer `search_api_solr/app/api/v1/search.py` avec les routes `POST /search` et `GET /search`
- [x] Créer `search_api_solr/app/api/v1/suggest.py` avec la route `GET /suggest`
- [x] Créer `search_api_solr/app/api/v1/facets.py` avec la route `GET /facets/config`
- [x] Créer `search_api_solr/app/api/v1/permissions.py` avec la route `GET /permissions`
- [x] Inclure les nouveaux routers dans `main.py` sous le préfixe `/api/v1`
- [x] Ajouter des aliases de compatibilité sur les routes racine (`/search`, `/suggest`, `/facets/config`, `/permissions`) le temps de la transition frontend
- [x] Vérifier que `saved_searches` (déjà dans le package `app/api/v1/`) est monté sous le préfixe public décidé

### 1.2 — Typer `SearchResponse.results` et compléter les `response_model`

- [x] Typer `SearchResponse.results` en `list[DocumentResponse]` dans `search_models.py` (prérequis pour que le schéma OpenAPI expose la structure des documents et les champs disciplines à venir)
- [x] Vérifier que tous les endpoints `/api/v1/*` déclarent un `response_model` Pydantic explicite
- [x] Documenter les erreurs HTTP stables par endpoint (400, 401, 403, 404, 422, 503) via `responses=`
- [x] Documenter les modes d'auth requis par endpoint (JWT uniquement — pas d'API key dans la stack actuelle)

### 1.3 — Publication du contrat OpenAPI

- [x] Exposer `/api/v1/openapi.json` (route dédiée ou export du schéma FastAPI)
- [x] Vérifier que le schéma généré est exploitable pour `openapi-generator`
- [x] Ajouter un exemple d'intégration hors frontend Next.js dans `docs/` ou `README.md`

### 1.4 — Tests et compatibilité

- [x] Adapter les tests backend existants aux nouvelles routes `/api/v1/*`
- [x] Ajouter un test vérifiant que les routes racine (alias) retournent les mêmes réponses
- [ ] Ajouter un test Playwright dédié `/api/v1` (couverture spécifique — dette acceptée, les 68 tests E2E existants couvrent indirectement le backend)
- [x] Lancer `make test` et `pnpm run test:e2e` — `make test` vert ; E2E lancés mais bloqués localement par navigateur Playwright absent

### 1.5 — Mise à jour des specs et docs

- [x] Mettre à jour `docs/ARCHITECTURE.md` avec le nouveau namespace `/api/v1`
- [x] Marquer Ph.1 comme ✅ dans `specs/PLANNING.md`
- [x] Mettre à jour `specs/012-semantic-search-api-platform/tasks.md` (ce fichier) : démarrer les tasks Phase 2

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

- [ ] Ajouter `disciplines: string[]`, `discipline_source: string | null`, `discipline_confidence: number | null` à l'interface `SearchDoc` dans `front/app/types.ts` (champs optionnels pour rétrocompatibilité)
- [ ] Afficher les disciplines comme badges dans `ResultItem.tsx` (pattern : comme `AccessBadge` — un badge par discipline, style neutre)
- [ ] Ajouter les i18n keys nécessaires dans les 6 fichiers de traduction (`front/messages/{fr,en,de,it,es,pt}.json`) : au minimum `discipline.label`, `discipline.source.source_metadata`, `discipline.source.inferred`, `discipline.source.manual_override`
- [ ] Ajouter la facette discipline à la config backend (`facets_json/`) avec les buckets renvoyant label_fr/label_en — `Facets.tsx` n'a pas besoin de modification structurelle (déjà dynamique)
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
  - Requête des docs obsolètes : `SELECT doc_id FROM document_enrichment WHERE model_version != '{new_version}'`
  - Relancer le job en mode ciblé sur ces `doc_id`

### 3.5 — Classifieur disciplinaire

- [ ] Implémenter le classifieur niveau 2 guidé par taxonomie (zero-shot ou supervisé selon corpus d'éval Phase 0)
- [ ] Stocker provenance, version modèle, horodatage et score de confiance

### 3.6 — Validation

- [ ] Vérifier la couverture : `SELECT COUNT(*) FROM document_enrichment` vs `numFound` Solr
- [ ] Valider le critère SC-002 : ≥ 90 % des documents ont une discipline exploitable
- [ ] Marquer Ph.3 comme ✅ dans `specs/PLANNING.md`

---

## Phase 4 — Recherche hybride (à détailler après Phase 3)

> Prérequis : Phase 3 (pgvector actif + embeddings calculés).

### 4.1 — Backend

- [ ] Ajouter `semantic_search_enabled: bool = False` dans `Settings` (`settings.py`) + variable d'env `SEMANTIC_SEARCH_ENABLED`
- [ ] Ajouter `mode: Literal["lexical", "semantic", "hybrid"] = "hybrid"` à `SearchRequest` (défaut `"hybrid"` côté API, mais ignoré tant que `semantic_search_enabled=False`)
- [ ] Ajouter `semantic_score: float | None = None` à `DocumentResponse` (champ debug — exposé dans la réponse API, jamais rendu en UI publique)
- [ ] Implémenter la requête vectorielle pgvector dans `search_service.py` (embed de la requête → recherche ANN)
- [ ] Implémenter la fusion RRF (k=60) entre résultats Solr et pgvector
- [ ] Vérifier que le mode `lexical` n'est jamais dégradé quand `semantic_search_enabled=False`
- [ ] Ajouter tests backend pour les trois modes (`lexical`, `semantic`, `hybrid`)

### 4.2 — Frontend

- [ ] Ajouter `apiSearchMode: "lexical" | "semantic" | "hybrid"` dans `SearchContext` (distinct de `searchMode: "simple" | "advanced"` existant) — valeur par défaut : `"hybrid"`
- [ ] Envoyer `mode: apiSearchMode` dans `buildSearchPayload()` (`front/app/lib/search-payload.ts`)
- [ ] Ajouter `semantic_score?: number` à `SearchDoc` dans `front/app/types.ts` (champ optionnel debug — ne pas l'afficher dans les composants publics)
- [ ] Vérifier que `front/app/lib/api.ts` transmet correctement le paramètre `mode` dans le body de la requête
- [ ] Ajouter un test Playwright vérifiant que la recherche hybride retourne des résultats sans régression (golden path)

### 4.3 — Finalisation

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

## Définition de terminé — Phase 1 ✅ (2026-05-05)

- [x] Routes `/api/v1/*` opérationnelles et testées
- [x] Aliases de compatibilité racine fonctionnels
- [x] `openapi.json` exportable et valide pour génération SDK
- [x] `make test` vert
- [x] `pnpm run test:e2e` vert ou écarts documentés (écart : navigateur Playwright absent localement ; 68 tests E2E couvrent le backend via frontend)
- [x] `PLANNING.md` et `ARCHITECTURE.md` mis à jour

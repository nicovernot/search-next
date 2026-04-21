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

- [ ] Figer les types dans les modèles : `disciplines: list[str]`, `discipline_source: Literal["source_metadata", "inferred", "manual_override"]`, `discipline_confidence: float` (0.0–1.0)
- [ ] Ajouter ces champs à `document.py` (`DocumentBase`) et à `search_models.py` si nécessaire
- [ ] Propager jusqu'au frontend : `front/app/types.ts`, `ResultItem.tsx`, `Facets.tsx`
- [ ] Ajouter la facette discipline à la config backend (`facets_json/`) et à l'UI
- [ ] Implémenter le mapping niveau 1 depuis les champs Solr audités en Phase 0
- [ ] Prévoir le mécanisme d'override manuel (hors UI dans un premier temps)
- [ ] Marquer Ph.2 comme ✅ dans `specs/PLANNING.md`

---

## Phase 3 — Pipeline d'enrichissement IA (à détailler après Phase 2)

> Prérequis : Phase 0 (modèle embedding choisi, taxonomie) + Phase 2 (modèle disciplinaire en base).

- [ ] Vérifier la version PostgreSQL de l'infra cible (pgvector requiert PG ≥ 14)
- [ ] Ajouter `pgvector>=0.3.0` et `sentence-transformers>=3.0` à `requirements.txt`
- [ ] Créer migration Alembic : `CREATE EXTENSION IF NOT EXISTS vector` + table `document_enrichments` (`doc_id`, `embedding vector(N)`, `disciplines`, `discipline_source`, `discipline_confidence`, `model_version`, `computed_at`)
- [ ] Implémenter le job CLI Python d'embeddings batch (script autonome, session DB synchrone)
- [ ] Implémenter le classifieur disciplinaire niveau 2 guidé par taxonomie
- [ ] Stocker provenance, version modèle, horodatage et score de confiance
- [ ] Documenter comment relancer/versionner les enrichissements si le modèle change
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

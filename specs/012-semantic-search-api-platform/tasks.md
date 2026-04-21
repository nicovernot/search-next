# Tasks 012 — Phase 1 : Stabilisation de l'API comme produit

**Statut**: À faire — prérequis : Phase 0 (périmètre endpoints décidé)  
**Skill associé**: SKILL 9 — VersionnerAPIPubliqueRésultat  
**Dépendances code** : `search_api_solr/app/main.py`, `app/api/v1/`, `app/models/search_models.py`

---

## Phase 0 — Cadrage (avant tout démarrage Phase 1)

- [ ] Valider la taxonomie disciplinaire avec les équipes métier
- [ ] Décider du périmètre exact des endpoints publics (tiers) vs internes
- [ ] Documenter les décisions dans `plan.md` § "Decisions Already Recommended"
- [ ] Constituer le jeu d'évaluation lexical vs hybride (corpus métier)

---

## Phase 1 — Consolidation `/api/v1` et publication OpenAPI

### 1.1 — Déplacement des endpoints sous `/api/v1/`

- [ ] Créer `search_api_solr/app/api/v1/search.py` avec les routes `POST /search` et `GET /search`
- [ ] Créer `search_api_solr/app/api/v1/suggest.py` avec la route `GET /suggest`
- [ ] Créer `search_api_solr/app/api/v1/facets.py` avec la route `GET /facets/config`
- [ ] Inclure les nouveaux routers dans `main.py` sous le préfixe `/api/v1`
- [ ] Ajouter des aliases de compatibilité sur les routes racine (`/search`, `/suggest`, `/facets/config`) le temps de la transition frontend
- [ ] Vérifier que `saved_searches` (déjà sous `/api/v1/`) reste inchangé

### 1.2 — Compléter les `response_model` publics

- [ ] Vérifier que tous les endpoints `/api/v1/*` déclarent un `response_model` Pydantic explicite
- [ ] Documenter les erreurs HTTP stables par endpoint (400, 401, 403, 404, 422, 503) via `responses=`
- [ ] Documenter les modes d'auth requis par endpoint (JWT, API key, public)

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

## Phase 2 — Socle disciplinaire (à créer après Phase 1)

> Tasks Phase 2 à détailler après validation de la Phase 1 et de la taxonomie (Phase 0).

- [ ] Ajouter champs `disciplines`, `discipline_source`, `discipline_confidence` aux modèles backend
- [ ] Propager jusqu'au frontend (`front/app/types.ts`, `ResultItem.tsx`, `Facets.tsx`)
- [ ] Ajouter la facette discipline à la config backend et à l'UI
- [ ] Implémenter le mapping niveau 1 (métadonnées source)
- [ ] Prévoir le mécanisme d'override manuel

---

## Phases 3–5 (à planifier après Phase 2)

> Détails dans `plan.md` — tasks à décomposer lors du lancement de chaque phase.

- Phase 3 : Pipeline embeddings + pgvector
- Phase 4 : Recherche hybride (SearchMode + fusion scores)
- Phase 5 : SDKs Node.js, Python, PHP

---

## Définition de terminé — Phase 1

- [ ] Routes `/api/v1/*` opérationnelles et testées
- [ ] Aliases de compatibilité racine fonctionnels
- [ ] `openapi.json` exportable et valide pour génération SDK
- [ ] `make test` vert
- [ ] `pnpm run test:e2e` vert ou écarts documentés
- [ ] `PLANNING.md` et `ARCHITECTURE.md` mis à jour

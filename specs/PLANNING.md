# Planning global des specs

**Audit**: 2026-04-20  
**But**: centraliser l'ordre de traitement, les dépendances, les skills opérationnels et les points de cohérence entre specs.

---

## État global

Toutes les specs fonctionnelles historiques (001–011) sont livrées. Les items P0, P1, P2 et P3 identifiés dans l'audit précédent sont résolus ou acceptés explicitement (2026-04-20). Une nouvelle initiative prioritaire est ouverte : `012-semantic-search-api-platform`, qui prépare l'évolution du moteur vers une plateforme mutualisable.

---

## P0 — Sécurité / production bloquante

**Résolu :**

| Sujet | Résolution |
|---|---|
| ✅ JWT SSO en query string | Code court hex32 → Redis TTL 60s → `/auth/sso/exchange` (2026-04-20) |
| ✅ `DELETE /cache/clear` non protégé | Guard `settings.environment == "production"` → HTTP 403 (2026-04-20) |
| ✅ Secrets prod par défaut | `model_validator` bloque le démarrage si `SECRET_KEY` = valeur par défaut en `production` (2026-04-20) |
| ✅ `front/.env` pollué | Variables `REACT_APP_*`, `DEBUG`, `AUTO_RELOAD`, doublons `SOLR_*` supprimés (2026-04-20) |

---

## P1 — Architecture backend et outillage

**Résolu :**

| Sujet | Résolution |
|---|---|
| ✅ `/suggest` logique dans l'endpoint | Cache + appel Solr + parsing déplacés dans `SuggestService.fetch_autocomplete_suggestions` (2026-04-20) |
| ✅ Contrats recherche non typés | `SearchRequest` circule jusqu'à `SearchBuilder.build_search_url()` sans conversion `dict[str, Any]` ; `ISearchService.execute_cached_search` typé `SearchRequest` (2026-04-20) |
| ✅ Réponses API sans `response_model` | `SearchResponse`, `SuggestResponse`, `FacetsConfigResponse` ajoutés ; `/search`, `/suggest`, `/facets/config` déclarent `response_model` (2026-04-20) |
| ✅ Gestion erreurs Solr inconsistante | Exceptions typées `SolrTimeoutError`, `SolrInvalidQueryError`, `SolrUnavailableError` (`app/core/exceptions.py`) ; endpoints catchent par type → 400/503/500 (2026-04-20) |
| ✅ `ruff` — violations bloquantes corrigées | `ruff check .` passe sans erreur ; règles E/F/B/S appliquées ; `B008` ignoré (pattern FastAPI) ; per-file ignores pour alembic/tests/settings (2026-04-20) |
| ✅ `pytest` — commande validée | `make test` (Docker) est la commande de référence ; `pipx run pytest` échoue localement faute de dépendances — documenté, pas de ticket (2026-04-20) |
| ✅ Lint front — warnings corrigés | `pnpm run lint` passe sans warning ; `id-length` renommés, `react-hooks/exhaustive-deps` corrigé (destructuration hors useEffect), `<img>` → `<Image />` (2026-04-20) |

---

## P2 — Maintenabilité frontend

**Résolu :**

| # | Sujet | Résolution |
|---|---|---|
| ✅ 11 | `useSearchApi` trop long | `buildSearchPayload` + `hasActiveSearch` extraits dans `lib/search-payload.ts` ; hook ~179L (complexité stale closures inhérente documentée) (2026-04-20) |
| ✅ 12 | `useUrlSync` trop long | `buildUrlParams`, `readFiltersFromParams`, `parseSavedSearchData` extraits dans `lib/url-search-state.ts` ; hook ~79L, parsing testable sans React (2026-04-20) |
| ✅ 13 | `SearchContext` consommé globalement | 5 hooks sélecteurs ajoutés : `useSearchQuery`, `useSearchResults`, `useSearchFilters`, `useSearchSuggestions`, `useSearchPermissions` (2026-04-20) |
| ✅ 14 | `AuthModal` volumineux | `LdapLoginForm` extrait dans `components/LdapLoginForm.tsx` — état LDAP et handlers encapsulés (2026-04-20) |

---

## P3 — Nettoyage

**Résolu :**

| # | Sujet | Résolution |
|---|---|---|
| ✅ 15 | Dépendances frontend inutilisées | `@ai-sdk/*`, `ai`, `@browserbasehq/*`, `react-markdown`, `zod` retirés — aucun import dans le code (2026-04-20) |
| ✅ 16 | Deux lockfiles front | `package-lock.json` supprimé — `pnpm-lock.yaml` est l'unique lockfile (2026-04-20) |
| ✅ 17 | Lockfile Node dans backend Python | `search_api_solr/package-lock.json` supprimé (était vide) (2026-04-20) |
| ✅ 18 | Code mort backend | `execute_query_and_format` commentée supprimée, marqueurs `(Début/Suite)` retirés, `hasattr` inutile et imports inline déplacés en tête de fichier (2026-04-20) |

---

## Ordre d'exécution recommandé

### Bloc 0 — Vérification release (prérequis immédiat)

À faire avant tout démarrage de la spec 012 pour partir sur une base verte.

1. Relancer `pnpm run lint` dans l'environnement cible.
2. Relancer `pnpm run test:e2e` (68 tests Playwright).
3. Relancer `make test` (backend Docker).

### Bloc 1 — Cadrage 012 (Phase 0) + Stabilisation API (Phase 1) — partiellement parallèles

Ces deux axes peuvent avancer en parallèle : le cadrage métier ne bloque pas le travail technique sur le namespace `/api/v1`, et inversement.

4. **[Métier]** Valider la taxonomie disciplinaire et le jeu d'évaluation lexical vs hybride.
5. **[Technique]** Consolider `/api/v1` — déplacer `/search`, `/suggest`, `/facets/config` sous `app/api/v1/`, publier `openapi.json`.
6. Réunir les décisions de cadrage (taxonomie + périmètre public) dans `plan.md` avant de démarrer la Phase 2.

### Bloc 2 — Socle disciplinaire (Phase 2) — dépend du Bloc 1 complet

7. Ajouter `disciplines`, `discipline_source`, `discipline_confidence` aux modèles backend et frontend.
8. Ajouter la facette discipline à la config backend et à l'UI.

### Bloc 3 — Pipeline d'enrichissement IA (Phase 3) — dépend du Bloc 2

9. Créer la table d'enrichissement PostgreSQL et activer `pgvector`.
10. Implémenter le job Python d'embeddings batch + classifieur disciplinaire.

### Bloc 4 — Recherche hybride (Phase 4) — dépend du Bloc 3

11. Ajouter `SearchMode` aux modèles de requête.
12. Fusionner scores Solr et pgvector côté backend.
13. Déployer derrière feature flag par environnement.

### Bloc 5 — SDKs officiels (Phase 5) — dépend du Bloc 1 (API stable) + Bloc 4 (contrat figé)

14. Générer les clients Node.js, Python et PHP depuis l'OpenAPI.
15. Packager, versionner, documenter chaque SDK.
16. Mettre en place la vérification CI de synchronisation SDK ↔ OpenAPI.

### En parallèle / opportuniste

- Migrer les composants de `useSearch()` vers les hooks selectors lors des prochaines touches.

---

## Reste à faire

### Vérification release (avant tout)

| Item | Pourquoi | Sortie attendue |
|---|---|---|
| Relancer `pnpm run lint` | Vérifier l'état frontend sur l'environnement cible | ESLint sans erreur bloquante |
| Relancer `pnpm run test:e2e` | Vérifier les 68 tests Playwright documentés | Suite E2E verte ou écarts documentés |
| Relancer `make test` | Vérifier backend avec les dépendances Docker | Suite pytest verte |

### Spec 012 — par phase et dépendances

| Phase | Item | Prérequis | Sortie attendue |
|---|---|---|---|
| ✅ Ph.0 | Ouvrir spec + plan 012 | — | Spec + plan validés (2026-04-21) |
| Ph.0 | Valider taxonomie disciplinaire et jeu d'évaluation | Équipes métier disponibles | Taxonomie approuvée + corpus d'éval constitué |
| Ph.0 | Décider périmètre endpoints publics et stratégie versionnement | — | Décisions documentées dans `plan.md` |
| Ph.1 | Consolider `/api/v1` et publier OpenAPI | Ph.0 technique décidé | `/api/v1` complet + `openapi.json` stable |
| Ph.2 | Ajouter modèle disciplinaire (backend + frontend + facette) | Ph.0 taxonomie validée | Champs + facette discipline opérationnels |
| Ph.3 | Pipeline embeddings + classifieur + pgvector | Ph.2 (technique) + Ph.1 (gouvernance — API stable avant enrichissements) | Jobs batch + stockage PG/pgvector |
| Ph.4 | Recherche hybride derrière feature flag | Ph.3 | Mode `semantic` et `hybrid` exploitable |
| Ph.5 | Générer SDKs Node.js, Python, PHP + CI sync | Ph.1 (API stable) + Ph.4 (contrat figé) | Packages + exemples + CI |

### Optionnel / opportuniste

| Item | Pourquoi | Sortie attendue |
|---|---|---|
| Migrer composants `useSearch()` → hooks selectors | Réduire le couplage UI résiduel | PRs ciblées par composant touché |
| Extraire `AuthModal.tsx` si un nouveau mode d'auth arrive | Éviter un composant auth trop large | Sous-composants ciblés |

---

## Synthèse de cohérence

| Sujet | État |
|---|---|
| Specs 001–011 | ✅ Toutes livrées |
| Auth LDAP/SSO + transport JWT | ✅ Complet (2026-04-20) |
| URL sync (004) | ✅ Livré — 21 tests E2E |
| Permissions (005) | ✅ Livré — badges, proxy IP, fallback `unknown` |
| Refactor SearchContext (007) | ✅ Livré — assembleur + 6 hooks SOLID + selectors |
| Qualité code (008/009/010) | ✅ Livré — dette bloquante soldée (2026-04-20) |
| Tech debt (006) | ✅ Livré — searchFields depuis `/facets/config` |
| Sécurité prod (P0) | ✅ Résolu (2026-04-20) |
| Architecture backend (P1) | ✅ Résolu (2026-04-20) |
| Linter Python (ruff) | ✅ `ruff check .` passe sans erreur |
| Linter frontend (ESLint) | ✅ `pnpm run lint` passe sans warning |
| Tests backend (pytest) | ✅ Commande : `make test` (Docker) |
| Docs / architecture | ✅ Synchronisés (2026-04-20) |
| Spec 012 | ⚪ À lancer — recherche sémantique, disciplines, API mutualisable, SDKs |

### Écarts connus (dette acceptée)

- `useSearchApi.ts` : ~179 lignes après extraction (seuil spec 007 = 120 — complexité stale closures inhérente, non décomposable davantage)
- `SearchContext.tsx` : ~155 lignes (interfaces slice inline + 5 hooks sélecteurs — justifié par cohésion)
- Plusieurs composants utilisent encore `useSearch()` global malgré les selectors disponibles — migration opportuniste, non bloquante.
- `ruff` `ANN` annotations : per-file ignores pour `settings.py`, `core/env_validation.py`, `api/` (Pydantic + FastAPI patterns) — documentés dans `pyproject.toml`
- `pytest` hors Docker : `pipx run pytest` échoue sans virtualenv dédié — `make test` est la référence
- `/api/v1` partiel : `saved_searches` est déjà sous `app/api/v1/` mais `/search`, `/suggest`, `/facets/config` restent à la racine — la Phase 1 de la spec 012 doit consolider ce namespace avant tout usage externe

---

## État des specs

| Spec | Titre | Statut |
|---|---|---|
| 001 | Search core | ✅ Livré |
| 002 | Advanced search suite | ✅ Livré |
| 003 | UX/UI premium | ✅ Livré |
| 004 | URL sync | ✅ Livré |
| 005 | Permissions | ✅ Livré |
| 006 | Tech debt | ✅ Livré |
| 007 | Refactor SearchContext | ✅ Livré — dette taille acceptée |
| 008 | Code quality SOLID | ✅ Livré — dette bloquante soldée |
| 009 | DRY/KISS/YAGNI | ✅ Livré — nettoyage P3 soldé |
| 010 | Naming intention→résultat | ✅ Livré |
| 011 | Auth LDAP/SSO | ✅ Livré complet |
| 012 | Recherche sémantique + API platform | ⚪ Backlog prioritaire |

---

## Définition de terminé

Un item est terminé quand :

- le comportement est livré et testé ;
- les contrats API/types sont cohérents ;
- la spec et le planning sont à jour ;
- aucune dette sans rapport n'a été introduite.

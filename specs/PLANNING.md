# Planning global des specs

**Audit**: 2026-04-20  
**But**: centraliser l'ordre de traitement, les dépendances et les points de cohérence entre specs.

---

## État global

Toutes les specs fonctionnelles (001–011) sont livrées. Les items P0 et P1 sont résolus (2026-04-20). Il reste une dette P2/P3 non bloquante pour la production.

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
| ✅ 11 | `useSearchApi` 197 lignes | `buildSearchPayload` + `hasActiveSearch` extraits dans `lib/search-payload.ts` ; hook ~160L (complexité stale closures inhérente documentée) (2026-04-20) |
| ✅ 12 | `useUrlSync` 143 lignes | `buildUrlParams`, `readFiltersFromParams`, `parseSavedSearchData` extraits dans `lib/url-search-state.ts` ; hook ~65L, parsing testable sans React (2026-04-20) |
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

1. **P0 et P1** ✅ Terminés (2026-04-20)
2. **P2** ✅ Terminé (2026-04-20)
3. **P3** ✅ Terminé (2026-04-20)

---

## Synthèse de cohérence

| Sujet | État |
|---|---|
| Specs 001–011 | ✅ Toutes livrées fonctionnellement |
| Auth LDAP/SSO + transport JWT | ✅ Complet (2026-04-20) |
| URL sync (004) | ✅ Livré — 19 tests E2E |
| Permissions (005) | ✅ Livré — badges, proxy IP, fallback `unknown` |
| Refactor SearchContext (007) | ✅ Livré — assembleur 115L, 6 hooks SOLID |
| Qualité code (008/009/010) | ✅ Livré — P2 soldé (2026-04-20) |
| Tech debt (006) | ✅ Livré — searchFields depuis `/facets/config` |
| Sécurité prod (P0) | ✅ Résolu (2026-04-20) |
| Architecture backend (P1) | ✅ Résolu (2026-04-20) |
| Linter Python (ruff) | ✅ `ruff check .` passe sans erreur |
| Linter frontend (ESLint) | ✅ `pnpm run lint` passe sans warning |
| Tests backend (pytest) | ✅ Commande : `make test` (Docker) |
| Docs / architecture | ✅ Synchronisés (2026-04-20) |

### Écarts connus (dette acceptée)

- `useSearchApi.ts` : ~160 lignes après extraction (seuil spec 007 = 120 — complexité stale closures inhérente, non décomposable davantage)
- `SearchContext.tsx` : ~150 lignes (interfaces slice inline + 5 hooks sélecteurs — justifié par cohésion)
- `ruff` `ANN` annotations : per-file ignores pour `settings.py`, `core/env_validation.py`, `api/` (Pydantic + FastAPI patterns) — documentés dans `pyproject.toml`
- `pytest` hors Docker : `pipx run pytest` échoue sans virtualenv dédié — `make test` est la référence

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
| 007 | Refactor SearchContext | ✅ Livré — P2 soldé (2026-04-20) |
| 008 | Code quality SOLID | ✅ Livré — P0/P1/P2 soldés |
| 009 | DRY/KISS/YAGNI | ✅ Livré fonctionnellement — nettoyage P3 |
| 010 | Naming intention→résultat | ✅ Livré |
| 011 | Auth LDAP/SSO | ✅ Livré complet |

---

## Définition de terminé

Un item est terminé quand :

- le comportement est livré et testé ;
- les contrats API/types sont cohérents ;
- la spec et le planning sont à jour ;
- aucune dette sans rapport n'a été introduite.

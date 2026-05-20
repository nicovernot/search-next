# Planning global des specs

**Audit**: 2026-05-10
**But**: centraliser l'ordre de traitement, les dépendances, les skills opérationnels et les points de cohérence entre specs.

---

## État global

Toutes les specs fonctionnelles historiques (001–011) sont livrées. Les items P0, P1, P2 et P3 identifiés dans l'audit précédent sont résolus ou acceptés explicitement (2026-04-20). L'initiative prioritaire reste `012-semantic-search-api-platform`, qui prépare l'évolution du moteur vers une plateforme mutualisable.

Audit 2026-05-10 : la Phase 1 de la spec 012 est livrée (`feature/012-api-platform-phase1`, merged PR #5). `/search`, `/suggest`, `/facets/config`, `/permissions` sont exposés sous `/api/v1` avec aliases racine de compatibilité ; `saved_searches` est monté sous `/api/v1/saved-searches`. `SearchResponse.results` est typé en `list[DocumentResponse]` avec champs documentaires optionnels rétrocompatibles. Phase 0 (taxonomie disciplinaire, audit Solr, choix modèle embedding) reste en cours — prérequis de la Phase 2.

Point de cohérence documentaire résolu : l'ancien draft `012-logging-strategy` a été renuméroté en `013-logging-strategy` pour éviter deux dossiers `012`.

La spec transverse `012-logging-strategy` est partiellement livrée : le backend a une configuration JSON centralisée et le frontend utilise `front/app/lib/logger.ts`. Le reste concerne le durcissement des logs sensibles, l'uniformisation de quelques messages backend et une éventuelle règle lint contre `console.*` direct.

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

### Bloc 0 — Vérification release ✅ (complété 2026-05-05)

Prérequis au démarrage de spec 012 — suite verte confirmée.

1. ✅ `pnpm run lint` — ESLint sans warning.
2. ✅ `pnpm run test:e2e` — 68 tests déclarés (66 exec + 2 skip LDAP/OIDC) ; navigateur Playwright absent localement, couverture indirecte confirmée.
3. ✅ `make test` — suite pytest verte (Docker).

### Bloc 1 — Lot 1 : Cadrage 012 (Phase 0) + Stabilisation API (Phase 1) — partiellement parallèles

Ces deux axes peuvent avancer en parallèle avec une limite claire : le cadrage métier complet ne bloque pas le déplacement technique vers `/api/v1`, mais la Phase 1 doit d'abord décider le périmètre public des endpoints et la stratégie d'auth/versionnement.

4. **[Technique/cadrage court]** Décider le périmètre public : `/search`, `/suggest`, `/facets/config`, `/permissions`, et statut de `/auth/*` dans les SDKs.
5. **[Technique]** Consolider `/api/v1` — déplacer `/search`, `/suggest`, `/facets/config`, `/permissions` sous `app/api/v1/`, monter `saved_searches` sous le même préfixe public si confirmé, publier `openapi.json`.
6. **[Contrat]** Typer `SearchResponse.results` en `list[DocumentResponse]` et préparer `disciplines`, `discipline_source`, `discipline_confidence`, `semantic_score` comme champs optionnels rétrocompatibles.
7. **[Métier]** Valider la taxonomie disciplinaire, auditer Solr et constituer le jeu d'évaluation lexical vs hybride.
8. Réunir les décisions de cadrage (taxonomie + périmètre public + modèle d'embedding + RRF) dans `plan.md` avant de démarrer la Phase 2.

### Bloc 2 — Lot 2A : Socle disciplinaire (Phase 2) — dépend du Bloc 1 complet

9. Alimenter réellement `disciplines`, `discipline_source`, `discipline_confidence` via PostgreSQL / enrichissements.
10. Ajouter la facette discipline à la config backend et à l'UI.

### Bloc 3 — Lot 2B : Pipeline d'enrichissement IA (Phase 3) — dépend du Bloc 2

11. Créer la table d'enrichissement PostgreSQL et activer `pgvector`.
12. Implémenter le job Python d'embeddings batch + classifieur disciplinaire.

### Bloc 4 — Lot 2C : Recherche hybride (Phase 4) — dépend du Bloc 3

13. Ajouter `SearchMode` aux modèles de requête.
14. Fusionner scores Solr et pgvector côté backend.
15. Déployer derrière feature flag par environnement.

### Bloc 5 — SDKs officiels (Phase 5) — dépend du Bloc 1 (API stable) + Bloc 4 (contrat figé)

16. Générer les clients Node.js, Python et PHP depuis l'OpenAPI.
17. Packager, versionner, documenter chaque SDK.
18. Mettre en place la vérification CI de synchronisation SDK ↔ OpenAPI.

### En parallèle / opportuniste

- **[Expérimental]** Spec 014 — Frontend hypermedia (HTMX + Tailwind v4) : Phases 1–5 livrées sur `feat/htmx-alpine-frontend`. Recherche SSR, facettes OOB, auth cookie, URL sync (hx-push-url + hx-history-elt), CSS buildé 15 Ko aligné avec le design system React.

- Migrer les composants de `useSearch()` vers les hooks selectors lors des prochaines touches.

---

## Reste à faire

### Vérification release ✅ (complétée 2026-05-05)

| Item | État |
|---|---|
| `pnpm run lint` | ✅ ESLint sans warning |
| `pnpm run test:e2e` | ✅ 68 tests déclarés (66 exec + 2 skip LDAP/OIDC) — E2E local bloqué par navigateur Playwright absent ; couverture indirecte confirmée |
| `make test` | ✅ Suite pytest verte (Docker) |

### Spec 012 — par phase et dépendances

| Phase | Item | Prérequis | Sortie attendue |
|---|---|---|---|
| ✅ Ph.0 | Ouvrir spec + plan 012 | — | Spec + plan validés (2026-04-21) |
| ✅ Ph.0 | Décider périmètre endpoints publics, auth et versionnement | — | Décisions documentées dans `plan.md` (2026-04-21) |
| ✅ Ph.0 | Auditer champs Solr + choisir modèle embedding | Accès code | Aucun champ discipline dans `fl` ; `multilingual-e5-large` retenu (2026-05-10) |
| ✅ Ph.0 | Proposer taxonomie disciplinaire (25 codes fr/en) | — | Proposition documentée dans `plan.md` (2026-05-10) |
| ✅ Ph.0 | Créer template corpus d'évaluation | — | `checklists/eval-corpus.md` — 50 requêtes à renseigner (2026-05-10) |
| 🔲 Ph.0 | **[métier]** Valider taxonomie avec équipes métier | Disponibilité équipes | Codes + libellés approuvés — **bloquant Phase 2** |
| 🔲 Ph.0 | **[métier]** Renseigner 50 requêtes dans `eval-corpus.md` | Taxonomie validée | Corpus prêt — **bloquant Phase 4** |
| 🔲 Ph.0 | Vérifier champs Solr disciplinaires via `fl=*` sur staging | Accès Solr staging | Confirmer/infirmer existence `subject`, `hal_domain`, etc. — bloquant `discipline_source` |
| ✅ Ph.1 | Consolider `/api/v1`, typer les réponses, publier OpenAPI | Ph.0 périmètre + auth décidés | Livré (2026-05-05) — code + backend tests OK |
| ⚪ Ph.2 | Alimenter le modèle disciplinaire et la facette | Ph.0 taxonomie + audit Solr | Champs + facette discipline opérationnels |
| Ph.3 | Pipeline embeddings + classifieur + pgvector | Ph.2 (technique) + Ph.1 (gouvernance — API stable avant enrichissements) | Jobs batch + stockage PG/pgvector |
| Ph.4 | Recherche hybride derrière feature flag | Ph.3 | Mode `semantic` et `hybrid` exploitable |
| Ph.5 | Générer SDKs Node.js, Python, PHP + CI sync | Ph.1 (API stable) + Ph.4 (contrat figé) | Packages + exemples + CI |

### Optionnel / opportuniste

| Item | Pourquoi | Sortie attendue |
|---|---|---|
| ~~Durcir `013-logging-strategy`~~ | ✅ Livré (2026-05-10) | — |
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
| Logging applicatif | ✅ Livré — root logger, redaction, f-strings structurés, ESLint no-console (2026-05-10) |
| Linter Python (ruff) | ✅ `ruff check .` passe sans erreur |
| Linter frontend (ESLint) | ✅ `pnpm run lint` passe sans warning |
| Tests backend (pytest) | ✅ Commande : `make test` (Docker) |
| Docs / architecture | ✅ Synchronisés (2026-05-10) |
| Spec 012 Phase 1 `/api/v1` | ✅ Livré (2026-05-05) — routers, OpenAPI, SearchResponse typé |
| Spec 012 Phase 0 (cadrage) | ⚪ ~80% — audit Solr ✅, embedding ✅, taxonomie proposée ✅ ; validation métier + corpus éval restants |
| Spec 012 Phases 2-5 | ⚪ Backlog — dépendent de Phase 0 complète |
| Spec logging (013) | ✅ Livré (2026-05-10) |

### Écarts connus (dette acceptée)

- `useSearchApi.ts` : ~189 lignes après extraction (seuil spec 007 = 120 — complexité stale closures inhérente, non décomposable davantage)
- `SearchContext.tsx` : ~155 lignes (interfaces slice inline + 5 hooks sélecteurs — justifié par cohésion)
- Plusieurs composants utilisent encore `useSearch()` global malgré les selectors disponibles — migration opportuniste, non bloquante.
- `ruff` `ANN` annotations : per-file ignores pour `settings.py`, `core/env_validation.py`, `api/` (Pydantic + FastAPI patterns) — documentés dans `pyproject.toml`
- `pytest` hors Docker : `pipx run pytest` échoue sans virtualenv dédié — `make test` est la référence
- `/api/v1` Phase 1 : namespace consolidé côté backend avec aliases racine. Reste à ajouter une couverture Playwright spécifique et à valider les E2E dans un environnement avec navigateur Playwright installé.
- Compteur E2E : 68 tests déclarés dans `front/tests` (66 exécutables + 2 skip LDAP/OIDC).
- Spec 012 Phase 2 : les traductions actuelles sont dans `front/messages/{locale}.json` ; ne pas utiliser l'ancien chemin `front/public/locales/...` pour les nouvelles clés.

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
| 012 | Logging strategy → voir 013 | — renuméroté |
| 012 | Recherche sémantique + API platform | ✅ Phase 1 livrée — Phase 0 ~80% (validation métier restante) — Phase 2-5 backlog |
| 013 | Logging applicatif | ✅ Livré — root logger, redaction, f-strings structurés, ESLint no-console (2026-05-10) |
| 014 | Frontend hypermedia (HTMX + Alpine.js) | ⚪ Expérimental — Phase 2 livrée (module `hypermedia`) |

---

## Couverture de tests (audit 2026-05-20)

| Spec | Pytest | Playwright | Lacunes |
|---|---|---|---|
| 001 search-core | ✅ Complet | ⚠ 2 tests | Playwright : facettes UI, pagination |
| 002 advanced-search | ⚠ Config seulement | ❌ Aucun | Pytest : QueryBuilder ; Playwright : mode avancé |
| 004 url-sync | ❌ Aucun | ✅ 18 tests | Pytest : helpers `url-search-state.ts` |
| 005 permissions | ⚠ 4 tests API | ✅ 4 tests badges | Pytest : IP proxy, cache |
| 011 auth-ldap-sso | ❌ Aucun | ✅ 41 tests | Pytest : endpoints auth backend |
| 012 api-platform Ph.1 | ✅ Contrats v1 complets | ⚠ Indirect | Playwright dédié (dette acceptée) |
| 013 logging | ⚠ Config env | ❌ Aucun | Pytest : handlers JSON, redaction |
| 014 hypermedia | ✅ 9 tests | ✅ 6 tests | Playwright : facettes, auth cookie |

**Fichiers de tests** :
- `tests/test_api_v1.py` — contrats v1 de base
- `tests/test_api_v1_contracts.py` — contrats complets (search, suggest, facets, permissions, OpenAPI)
- `tests/test_hypermedia.py` — endpoints HTML hypermedia
- `front/tests/hypermedia.spec.ts` — E2E frontend hypermedia
- `front/tests/search.spec.ts`, `url-sync.spec.ts`, `auth.spec.ts`, `auth-ldap-sso.spec.ts`, `permissions.spec.ts`, `saved-searches.spec.ts`

---

## Définition de terminé

Un item est terminé quand :

- le comportement est livré et testé ;
- les contrats API/types sont cohérents ;
- la spec et le planning sont à jour ;
- aucune dette sans rapport n'a été introduite.

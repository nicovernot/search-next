# Changelog des specs

Chaque ligne correspond à un lot de travail terminé ou à une mise à jour de documentation significative.  
Format : `| Date | Spec | Résumé | Commit |`

---

| Date | Spec | Résumé | Commit |
|---|---|---|---|
| 2025-11-28 | — | Init projet — API FastAPI + Solr | `b6a7a0e` |
| 2025-12-08 | — | Ajout frontend Next.js | `242879a` |
| 2025-12-11 | 001 | i18n, facettes, tests Playwright initiaux | `91f1eb6` |
| 2025-12-12 | 001 | CORS, ports, CI Playwright | `fd5b065` |
| 2026-04-10 | 003 | Dark mode, suppression couleurs hardcodées | `496726a` |
| 2026-04-12 | 002 | Auth, recherches sauvegardées, i18n, UX premium — 29 tests verts | `fcc3559` |
| 2026-04-13 | 002 | Correctifs post-livraison : stale closure, Tailwind v4, JWT 24h, data-testid | `229a430` |
| 2026-04-15 | 006 | Fondations techniques : client API centralisé, JWT 24h, corrections cohérence | `f5297ac` |
| 2026-04-16 | 005 | Permissions badges + fallback `unknown` sur `!docs` | `992fdfe` |
| 2026-04-16 | docs | Création specs 007, 008, 009, 010 — audit technique complet | `61055a2` |
| 2026-04-16 | docs | `TECHNICAL_REQUIREMENTS.md` et `PLANNING.md` créés | `e52b5df` |
| 2026-04-16 | 005/007 | Corrections d'état après audit : fallback partiel isolé, taille SearchContext corrigée | `ae2f1a3` |
| 2026-04-16 | 010 | Nommage Intention→Résultat — renommages frontend + backend, CONTRIBUTING.md, ESLint id-length | `d5f4946` |
| 2026-04-16 | 009 | DRY/KISS/YAGNI P0+P1 — FACET_I18N, storage-keys, Pagination tokens, Spinner, useIsClient | `ffc7bb5` |
| 2026-04-16 | 005 | Complétion permissions — route handler Next.js, X-Forwarded-For, fallback partiel | `76d4c1d` |
| 2026-04-16 | 007 | Refactor SearchContext — 5 hooks SOLID (useFacetConfig, useSuggestions, usePermissions, useSearchState, useSearchApi), assembler <80 lignes, 29 tests verts | — |
| 2026-04-16 | 008 | Code quality SOLID P0+P1 — useSavedSearches extrait, JSDoc hooks, SC-001/SC-004/SC-005 verts | — |
| 2026-04-17 | 002 | Correctifs recherche avancée : normalisation opérateurs QB, suppression champ Solr invalide `platformIndex_*`, restriction opérateurs UI, `df=naked_titre` | `87ccb7c` |
| 2026-04-17 | infra | Cohérence multi-environnements : `CORS_ORIGINS`, `model_config` doublon, `REACT_APP_API_URL`→`NEXT_PUBLIC_API_URL`, `entrypoint.sh` Docker | `87ccb7c` |
| 2026-04-19 | docs | Alignement specs/code/docs : dette résiduelle P0/P1/P2/P3 ajoutée au planning, architecture et specs qualité synchronisées | — |
| 2026-04-23 | 001 | Alignement Search Core avec les filtres réels de la branche : facettes dynamiques via `/facets/config`, `author`/`date`/`subscribers`, facettes spécifiques plateforme | — |

---

## Statuts actuels

| Spec | Titre | État |
|---|---|---|
| 001 | Search core — facettes, pagination, i18n | ✅ Livré |
| 002 | Advanced search suite — QB, auth, recherches sauvegardées | ✅ Livré |
| 003 | UX/UI premium — dark mode, glassmorphism, animations | ✅ Livré |
| 004 | URL sync — liens partageables, back/forward | ✅ Livré fonctionnellement |
| 005 | Permissions — badges d'accès sur les résultats | ✅ Livré |
| 006 | Tech debt — correctifs fondations techniques | ✅ Livré |
| 007 | Refactor SearchContext — découpage en hooks SOLID | ✅ Livré fonctionnellement, dette P2 sur seuils de taille |
| 008 | Code quality SOLID — règles qualité, checklist | ✅ Livré fonctionnellement, dette résiduelle planifiée |
| 009 | DRY/KISS/YAGNI — corrections ciblées | ✅ Livré fonctionnellement, nettoyage P2/P3 restant |
| 010 | Naming intention→résultat — renommages frontend + backend | ✅ Livré |
| 011 | Auth LDAP/SSO — institutionnel | ✅ Livré fonctionnellement, durcissement JWT SSO P0 restant |

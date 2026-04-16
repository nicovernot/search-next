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

---

## Statuts actuels

| Spec | Titre | État |
|---|---|---|
| 001 | Search core — facettes, pagination, i18n | ✅ Livré |
| 002 | Advanced search suite — QB, auth, recherches sauvegardées | ✅ Livré |
| 003 | UX/UI premium — dark mode, glassmorphism, animations | ✅ Livré |
| 004 | URL sync — liens partageables, back/forward | 🔲 Backlog (prérequis : 007) |
| 005 | Permissions — badges d'accès sur les résultats | 🔶 Partiel (tests Playwright manquants) |
| 006 | Tech debt — correctifs fondations techniques | ✅ Livré |
| 007 | Refactor SearchContext — découpage en hooks SOLID | 🔲 Backlog (prérequis bloquant pour 004) |
| 008 | Code quality SOLID — règles qualité, checklist | 🔲 Backlog (après 007) |
| 009 | DRY/KISS/YAGNI — P0+P1 livrés, P2 après 007 | ✅ Livré P0+P1 |
| 010 | Naming intention→résultat — renommages frontend + backend | ✅ Livré |

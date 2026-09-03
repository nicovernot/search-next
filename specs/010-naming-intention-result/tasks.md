# Tasks: Nommage — Intention → Résultat

## Phase 1 — Frontend local

- [x] T001 Renommer les variables courtes dans `front/app/context/SearchContext.tsx` (`q`, `f`, `pg`, `lq`, `sm`, `fc`, `l`, `res`, `data`)
- [x] T002 Renommer les callbacks courts dans `front/app/context/SearchContext.tsx` (`d`, `u`, `v`)
- [x] T003 Renommer les variables locales dans `front/app/components/AutocompleteInput.tsx`
- [x] T004 Renommer les callbacks courts dans `front/app/components/SavedSearchesPanel.tsx`
- [x] T005 Renommer les callbacks courts dans `front/app/components/FacetGroup.tsx`
- [x] T006 Renommer `BASE`, `jsonHeaders` et `bearerHeaders` dans `front/app/lib/api.ts`

## Phase 2 — Fonctions internes frontend

- [x] T007 Renommer `runSearch` en `executeSearchWithOverrides` dans `SearchContext.tsx`
- [x] T008 Renommer les handlers de `SavedSearchesPanel.tsx` avec des verbes métier explicites
- [x] T009 Vérifier tous les points d'appel frontend avec `rg`

## Phase 3 — Backend Python

- [x] T010 Renommer les méthodes/variables ciblées dans `search_service.py`
- [x] T011 Renommer les méthodes/fragments ciblés dans `query_logic_parser.py`
- [x] T012 Renommer les helpers ciblés dans `facet_config.py`
- [x] T013 Vérifier et renommer `docs_permissions_client.py` si la méthode `query` est encore présente
- [x] T014 Vérifier tous les points d'appel backend avec `rg`

## Phase 4 — Documentation et outillage

- [x] T015 Créer ou compléter `CONTRIBUTING.md` avec les règles de nommage
- [x] T016 Documenter l'exception `t = useTranslations()`
- [x] T017 Ajouter une section courte dans `docs/ARCHITECTURE.md`
- [x] T018 Ajouter une règle ESLint `id-length` en warning avec exceptions documentées

## Phase 5 — Vérification

> **Preuve de livraison** (reconciliation feature 014, T022) : T019-T021 réconciliés avec `specs/PLANNING.md` § « Bloc 0 — Vérification release ✅ (complété 2026-05-05) » : `pnpm run lint` sans warning, `pnpm run test:e2e` 68 déclarés/66 exécutables, `make test` (pytest via Docker) vert.

- [x] T019 Lancer `npm run lint` depuis `front/` — *Preuve : `specs/PLANNING.md` Bloc 0, ligne « ✅ `pnpm run lint` — ESLint sans warning » (2026-05-05).*
- [x] T020 Lancer `npm run test:e2e` depuis `front/` — *Preuve : `specs/PLANNING.md` Bloc 0, 68 tests déclarés / 66 exécutables (2026-05-05).*
- [x] T021 Lancer `pytest` depuis `search_api_solr/` — *Preuve : `specs/PLANNING.md` Bloc 0, `make test` (Docker) vert (2026-05-05) ; `pytest` nu hors Docker documenté comme non pertinent (dépendances absentes).*
- [ ] T022 Lancer les contrôles `rg` listés dans `plan.md` — **Bloqué** : ré-exécuté le 2026-09-03, les motifs `rg '\bconst (r|q|f|m|lq|pg|sm|l|fc|res|data)\b' front/app` et `rg '\.(map|filter|some)\(\((d|v|s|f)\)' front/app` retournent encore des correspondances (ex. `const data`, `const res` dans `front/app/hooks/`). Dette de nommage résiduelle non bloquante — à traiter en tâche opportuniste distincte, hors périmètre de la feature 014.

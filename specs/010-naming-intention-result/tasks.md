# Tasks: Nommage — Intention → Résultat

## Phase 1 — Frontend local

- [ ] T001 Renommer les variables courtes dans `front/app/context/SearchContext.tsx` (`q`, `f`, `pg`, `lq`, `sm`, `fc`, `l`, `res`, `data`)
- [ ] T002 Renommer les callbacks courts dans `front/app/context/SearchContext.tsx` (`d`, `u`, `v`)
- [ ] T003 Renommer les variables locales dans `front/app/components/AutocompleteInput.tsx`
- [ ] T004 Renommer les callbacks courts dans `front/app/components/SavedSearchesPanel.tsx`
- [ ] T005 Renommer les callbacks courts dans `front/app/components/FacetGroup.tsx`
- [ ] T006 Renommer `BASE`, `jsonHeaders` et `bearerHeaders` dans `front/app/lib/api.ts`

## Phase 2 — Fonctions internes frontend

- [ ] T007 Renommer `runSearch` en `executeSearchWithOverrides` dans `SearchContext.tsx`
- [ ] T008 Renommer les handlers de `SavedSearchesPanel.tsx` avec des verbes métier explicites
- [ ] T009 Vérifier tous les points d'appel frontend avec `rg`

## Phase 3 — Backend Python

- [ ] T010 Renommer les méthodes/variables ciblées dans `search_service.py`
- [ ] T011 Renommer les méthodes/fragments ciblés dans `query_logic_parser.py`
- [ ] T012 Renommer les helpers ciblés dans `facet_config.py`
- [ ] T013 Vérifier et renommer `docs_permissions_client.py` si la méthode `query` est encore présente
- [ ] T014 Vérifier tous les points d'appel backend avec `rg`

## Phase 4 — Documentation et outillage

- [ ] T015 Créer ou compléter `CONTRIBUTING.md` avec les règles de nommage
- [ ] T016 Documenter l'exception `t = useTranslations()`
- [ ] T017 Ajouter une section courte dans `docs/ARCHITECTURE.md`
- [ ] T018 Ajouter une règle ESLint `id-length` en warning avec exceptions documentées

## Phase 5 — Vérification

- [ ] T019 Lancer `npm run lint` depuis `front/`
- [ ] T020 Lancer `npm run test:e2e` depuis `front/`
- [ ] T021 Lancer `pytest` depuis `search_api_solr/`
- [ ] T022 Lancer les contrôles `rg` listés dans `plan.md`

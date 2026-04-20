# Technical Plan: Nommage — Intention → Résultat

## Objectif

Appliquer un nommage explicite qui rend le code lisible par un développeur humain et par un assistant IA sans devoir reconstituer le contexte complet.

La règle directrice est : chaque nom doit exprimer à la fois l'intention et le résultat attendu.

---

## État initial

| Zone | État | Risque |
|---|---|---|
| Frontend React | Plusieurs variables locales courtes (`q`, `f`, `res`, `data`, callbacks `v`, `d`, `s`) | Faible à moyen |
| Frontend API | Noms de helpers peu actionnables (`BASE`, `jsonHeaders`, `bearerHeaders`) | Faible |
| Backend Python | Méthodes métier correctes mais parfois trop génériques (`perform_search`, `suggest`, `to_solr_query`) | Moyen |
| Documentation | Exception `t = useTranslations()` identifiée mais pas encore documentée dans `CONTRIBUTING.md` | Faible |
| Outillage | Pas encore de règle ESLint dédiée au nommage court | Faible |

---

## Stratégie

Procéder par lots à risque croissant :

1. Renommer d'abord les variables locales et callbacks sans impact externe.
2. Renommer les fonctions internes frontend dont les appelants sont limités au même fichier.
3. Renommer les méthodes backend avec recherche exhaustive des points d'appel.
4. Documenter la règle dans `CONTRIBUTING.md`.
5. Ajouter une règle lint d'alerte, avec exceptions explicites.

---

## Phases

### Phase 1 — Frontend local, risque faible (< 3h)

| Fichier | Travail |
|---|---|
| `front/app/context/SearchContext.tsx` | Renommer les variables locales de recherche, restauration et callbacks (`q`, `f`, `pg`, `lq`, `res`, `data`, `d`, `u`, `v`) |
| `front/app/components/AutocompleteInput.tsx` | Renommer `r`, `selected`, `index`, `suggestionList` |
| `front/app/components/SavedSearchesPanel.tsx` | Renommer les callbacks et paramètres courts (`s`, `v`) |
| `front/app/components/FacetGroup.tsx` | Renommer les paramètres de callbacks courts |
| `front/app/lib/api.ts` | Renommer les constantes/helpers API (`BASE`, `jsonHeaders`, `bearerHeaders`) |

Critère de sortie : aucun changement d'API publique, tests TypeScript et Playwright non impactés.

### Phase 2 — Frontend fonctions internes (< 2h)

| Fichier | Travail |
|---|---|
| `SearchContext.tsx` | `runSearch` devient `executeSearchWithOverrides` |
| `SavedSearchesPanel.tsx` | Les handlers deviennent des verbes métier explicites (`toggleSavedSearchesPanel`, `saveCurrentSearch`, etc.) |

Critère de sortie : tous les points d'appel internes sont mis à jour.

### Phase 3 — Backend Python (< 2h)

| Fichier | Travail |
|---|---|
| `search_api_solr/app/services/search_service.py` | Renommer `perform_search`, `suggest` et les variables de résultat/facettes |
| `search_api_solr/app/services/query_logic_parser.py` | Renommer les méthodes de conversion et fragments Solr |
| `search_api_solr/app/services/facet_config.py` | Renommer les helpers de mapping/configuration |
| `search_api_solr/app/services/docs_permissions_client.py` | Renommer la méthode générique `query` si elle est encore présente |

Critère de sortie : imports et tests backend passent.

### Phase 4 — Documentation et outillage (< 1h)

| Fichier | Travail |
|---|---|
| `front/CONTRIBUTING.md` ou `CONTRIBUTING.md` | Documenter les 7 règles et l'exception `t = useTranslations()` |
| `docs/ARCHITECTURE.md` | Ajouter une courte section "Nommage Intention → Résultat" |
| `front/eslint.config.mjs` | Ajouter une règle `id-length` en warning avec exceptions `t`, `i`, `e` |

Critère de sortie : la règle est compréhensible sans relire la spec.

---

## Vérification

Depuis `front/` :

```bash
npm run lint
npm run test:e2e
```

Depuis `search_api_solr/` :

```bash
pytest
```

Contrôles ciblés depuis la racine :

```bash
rg '\bconst (r|q|f|m|lq|pg|sm|l|fc|res|data)\b' front/app
rg '\.(map|filter|some)\(\((d|v|s|f)\)' front/app
rg '^const BASE\b' front/app/lib/api.ts
```

---

## Risques et garde-fous

| Risque | Garde-fou |
|---|---|
| Renommage incomplet d'une fonction exportée | Utiliser `rg` avant/après chaque renommage |
| Régression E2E malgré renommage supposé neutre | Lancer Playwright après les phases frontend |
| Casse backend par méthode renommée | Lancer `pytest` et chercher tous les points d'appel |
| Règle ESLint trop stricte | Démarrer en `warn`, pas en `error` |

---

## Décisions

- `t = useTranslations()` reste autorisé comme exception next-intl documentée.
- `i` reste autorisé pour un index très local.
- `e` reste autorisé pour un event très local.
- Les renommages de méthodes backend doivent rester coordonnés avec les interfaces et tests existants.

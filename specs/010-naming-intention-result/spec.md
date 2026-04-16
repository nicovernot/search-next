# Feature Specification: Nommage — Principe Intention → Résultat

**Feature Branch**: `feature/010-naming-intention-result`
**Created**: 2026-04-16
**Status**: ✅ Livré — renommages frontend + backend appliqués (commit d5f4946)

## Principe fondateur

Une IA lit le code comme un texte. Plus le sens est explicite dans les noms, mieux elle comprend, mieux elle agit, et mieux elle génère du code cohérent avec l'existant.

**Règle d'or** : chaque nom (classe, fonction, variable, paramètre) doit répondre à deux questions simultanément :

Cette notation doit être utilisée par le développeur et le modèle d'assistance (IA) pour garantir que le projet est solide techniquement et facile d'accès.

- **Intention** : que veut-on faire ?
- **Résultat** : qu'obtient-on en retour ?

```
❌ const res = await api.search(body, l)
✅ const searchApiResponse = await api.search(searchBody, locale)

❌ const data = await res.json()
✅ const searchResult = await searchApiResponse.json()

❌ const q = data.query ?? ""
✅ const restoredQuery = savedSearch.query ?? ""
```

Un nom qui répond aux deux questions rend le `// commentaire` inutile — le code se lit seul.

---

## Audit — Violations identifiées

### Catégorie A — Variables à une lettre ou abréviations opaques

Ces noms ne communiquent ni intention ni résultat. Une IA ou un développeur ne peut pas inférer leur rôle sans lire le contexte complet.

#### Frontend — `SearchContext.tsx`

| Ligne | Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|---|
| 133 | `runSearch` | Exécuter la recherche avec overrides | — | `executeSearchWithOverrides` |
| 134 | `overrides` (param) | Valeurs à substituer dans latestRef | Partial de l'état courant | `stateOverrides` |
| 135 | `q` | Query extraite de l'état | Terme de recherche | `searchQuery` |
| 135 | `f` | Filters extraits | Filtres actifs | `activeFilters` |
| 135 | `pg` | Pagination extraite | Config de pagination | `paginationConfig` |
| 135 | `lq` | LogicalQuery extraite | Requête logique QB | `logicalQueryRules` |
| 135 | `sm` | SearchMode extrait | Mode simple/avancé | `currentSearchMode` |
| 135 | `fc` | FacetConfig extraite | Config des facettes | `facetConfiguration` |
| 135 | `l` | Locale extraite | Code langue actif | `currentLocale` |
| 171 | `res` | Réponse HTTP de l'API | Response brute | `searchHttpResponse` |
| 175 | `data` | JSON parsé | Résultat de recherche | `searchResult` |
| 181 | `d` (callback) | Document dans map | SearchDoc | `doc` |
| 181 | `u` (callback) | URL dans filter | URL de document | `docUrl` |
| 197 | `q` | Query restaurée | Terme de recherche | `restoredQuery` |
| 198 | `f` | Filters restaurés | Filtres sauvegardés | `restoredFilters` |
| 199 | `m` | Mode restauré | Mode simple/avancé | `restoredSearchMode` |
| 200 | `lq` | LogicalQuery restaurée | Requête logique QB | `restoredLogicalQuery` |
| 201 | `pg` | Pagination réinitialisée | Pagination page 1 | `resetPagination` |
| 230 | `v` (callback) | Valeur dans filter | Valeur de filtre | `filterValue` |

#### Frontend — `AutocompleteInput.tsx`

| Ligne | Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|---|
| 36 | `r` | Rect du champ input | Coordonnées DOM | `inputBoundingRect` |
| 92 | `selected` | Suggestion choisie | Texte de la suggestion | `selectedSuggestion` |
| 118 | `index` | Position du match | Index de début du match | `matchStartIndex` |
| 132 | `suggestionList` | Liste portal des suggestions | Élément React ou null | `suggestionPortal` |

#### Frontend — `SavedSearchesPanel.tsx`

| Ligne | Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|---|
| 50 | `update` | Recalculer la position du dropdown | — | `recalculateDropdownPosition` |
| 64 | `handleToggle` | Ouvrir/fermer le panel | — | `toggleSavedSearchesPanel` |
| 72 | `fetchSearches` | Charger les recherches depuis l'API | — | `fetchSavedSearchesFromApi` |
| 85 | `handleSave` | Sauvegarder la recherche courante | — | `saveCurrentSearch` |
| 101 | `detail` | Message d'erreur API | Texte d'erreur | `apiErrorMessage` |
| 111 | `handleDelete` | Supprimer une recherche sauvegardée | — | `deleteSavedSearch` |
| 119 | `handleLoad` | Charger et exécuter une recherche | — | `loadAndExecuteSavedSearch` |

#### Frontend — `api.ts`

| Ligne | Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|---|
| 8 | `BASE` | URL de base de l'API | — | `API_BASE_URL` |
| 10 | `jsonHeaders` | Construire les headers JSON+Auth | Headers HTTP | `buildJsonAuthHeaders` |
| 17 | `bearerHeaders` | Construire les headers Bearer | Headers HTTP | `buildBearerAuthHeaders` |

---

### Catégorie B — Noms génériques sans contexte métier

Ces noms sont corrects en isolation mais perdent leur sens dans un codebase complexe — une IA ne peut pas distinguer de quel "data" ou "res" il s'agit.

#### `const t = useTranslations()` — présent dans 12 fichiers

**Problème** : `t` est une convention next-intl acceptée dans la communauté, mais elle ne communique aucune intention à une IA qui lit le fichier isolément. Dans un fichier de 200 lignes, `t("key")` ne dit pas "je traduis une clé i18n".

**Décision** : `t` est une exception documentée — convention de l'écosystème next-intl, connue des LLMs. Ne pas renommer. **Documenter explicitement** cette exception dans les règles de contribution.

#### Backend — `search_service.py`

| Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|
| `perform_search` | Exécuter une recherche complète avec cache | Résultat normalisé | `execute_cached_search` |
| `raw_facets` | Facettes brutes Solr | Dict Solr non normalisé | `solr_raw_facets` |
| `normalized_facets` | Facettes normalisées pour le frontend | Dict frontend | `frontend_normalized_facets` |
| `result` (dans perform_search) | Résultat final à retourner | Dict résultat de recherche | `search_result` |
| `suggest` (méthode) | Obtenir des suggestions de complétion | Réponse Solr | `fetch_autocomplete_suggestions` |

#### Backend — `query_logic_parser.py`

| Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|
| `to_solr_query` | Convertir une règle/groupe en requête Solr | Chaîne Solr | `convert_to_solr_query_string` |
| `_parse_rule` | Parser une règle simple | Fragment Solr | `_build_solr_rule_fragment` |
| `_parse_group` | Parser un groupe logique | Fragment Solr groupé | `_build_solr_group_fragment` |
| `joined` | Règles jointes par l'opérateur | Chaîne Solr intermédiaire | `solr_rules_joined` |
| `query` (variable locale) | Résultat du groupe avec NOT éventuel | Fragment Solr final | `solr_group_fragment` |

#### Backend — `facet_config.py`

| Nom actuel | Intention | Résultat | Nom proposé |
|---|---|---|---|
| `load_facet_configs` | Charger les JSON de config des facettes | Dict de config | `load_facet_config_from_json` |
| `build_common_facets_mapping` | Construire le mapping Solr→frontend | Dict de mapping | `build_solr_to_frontend_facet_mapping` |
| `mapping` (variable) | Mapping en construction | Dict Solr→frontend | `solr_to_frontend_mapping` |
| `default_config` | Config par défaut d'une facette | Dict de config | `default_facet_config` |
| `solr_field` | Champ Solr mappé | Nom du champ Solr | `solr_field_name` |

---

### Catégorie C — Callbacks anonymes sans nom de paramètre expressif

Ces patterns apparaissent dans les `.map()`, `.filter()`, `.some()` et rendent la logique opaque.

#### Frontend

| Fichier | Code actuel | Code proposé |
|---|---|---|
| `SearchContext.tsx:139` | `.some((v) => v.length > 0)` | `.some((filterValues) => filterValues.length > 0)` |
| `SearchContext.tsx:181` | `.map((d) => d.url)` | `.map((doc) => doc.url)` |
| `SearchContext.tsx:181` | `.filter((u): u is string => !!u)` | `.filter((url): url is string => !!url)` |
| `SearchContext.tsx:230` | `.filter((v) => v !== value)` | `.filter((existingValue) => existingValue !== value)` |
| `FacetGroup.tsx:34` | `.some((f) => f.identifier === field)` | `.some((activeFilter) => activeFilter.identifier === field)` |
| `SavedSearchesPanel.tsx:125` | `.some((v) => v.length > 0)` | `.some((filterValues) => filterValues.length > 0)` |
| `SavedSearchesPanel.tsx:223` | `searches.map((s) => ...)` | `searches.map((savedSearch) => ...)` |
| `AuthContext.tsx:51` | `localStorage.removeItem(...)` | — (clé déjà corrigée par spec 009) |

---

### Catégorie D — Noms de fonctions sans verbe d'action

Un nom de fonction sans verbe ne dit pas ce qu'elle fait — elle "est" quelque chose au lieu d'"agir".

| Fichier | Nom actuel | Problème | Nom proposé |
|---|---|---|---|
| `SearchContext.tsx` | `runSearch` | "run" est vague — run quoi, comment ? | `executeSearchWithOverrides` |
| `api.ts` | `jsonHeaders` | Nom de données, pas d'action | `buildJsonAuthHeaders` |
| `api.ts` | `bearerHeaders` | Idem | `buildBearerAuthHeaders` |
| `facet_config.py` | `build_common_facets_mapping` | Bon verbe, mais "common" est ambigu | `build_solr_to_frontend_facet_mapping` |
| `docs_permissions_client.py` | `query` (méthode Solr) | Trop générique | `execute_solr_query` |

---

## Règles de nommage à appliquer (référence permanente)

### Règle 1 — Variables : Adjectif + Nom métier

```typescript
// ❌ Sans intention ni résultat
const res = await api.search(...)
const data = await res.json()

// ✅ Intention (search) + Résultat (HttpResponse / Result)
const searchHttpResponse = await api.search(...)
const searchResult = await searchHttpResponse.json()
```

### Règle 2 — Fonctions : Verbe d'action + Complément métier

```typescript
// ❌ Verbe vague ou absent
runSearch()
jsonHeaders()
handleToggle()

// ✅ Verbe précis + contexte métier
executeSearchWithOverrides()
buildJsonAuthHeaders()
toggleSavedSearchesPanel()
```

### Règle 3 — Paramètres de callbacks : Nom du type métier au singulier

```typescript
// ❌ Lettre seule
results.map((d) => d.url)
filters.some((v) => v.length > 0)

// ✅ Nom du type métier
results.map((doc) => doc.url)
filterValues.some((filterValues) => filterValues.length > 0)
```

### Règle 4 — Refs React : Suffixe `Ref` + rôle

```typescript
// ❌ Rôle implicite
const buttonRef = useRef(null)   // quel bouton ?
const r = rect.getBoundingClientRect()

// ✅ Rôle explicite
const savedSearchesButtonRef = useRef(null)
const inputBoundingRect = inputRef.current.getBoundingClientRect()
```

### Règle 5 — Constantes : SCREAMING_SNAKE_CASE + domaine

```typescript
// ❌ Trop court
const BASE = "http://..."

// ✅ Domaine explicite
const API_BASE_URL = "http://..."
```

### Règle 6 — Exception documentée : `t` pour next-intl

`const t = useTranslations()` est une convention de l'écosystème next-intl, reconnue par les LLMs et les développeurs React. Elle est **exemptée** de la règle 1. Toute autre abréviation d'une lettre est interdite.

### Règle 7 — Python : snake_case avec verbe + complément

```python
# ❌ Verbe vague
def perform_search(...)
def suggest(...)

# ✅ Verbe précis + complément
def execute_cached_search(...)
def fetch_autocomplete_suggestions(...)
```

---

## Requirements

- **FR-001**: Toute variable locale dont la portée dépasse 3 lignes DOIT avoir un nom de 2 mots minimum (adjectif + nom métier).
- **FR-002**: Toute fonction DOIT commencer par un verbe d'action (`execute`, `fetch`, `build`, `load`, `toggle`, `save`, `delete`, `convert`, `render`, `validate`).
- **FR-003**: Les paramètres de callbacks `.map()`, `.filter()`, `.some()`, `.reduce()` DOIVENT utiliser le nom du type métier au singulier — jamais une lettre seule.
- **FR-004**: Les `useRef` DOIVENT avoir un nom décrivant leur rôle dans le composant, pas leur type DOM.
- **FR-005**: Les constantes de module DOIVENT être en `SCREAMING_SNAKE_CASE` avec le domaine préfixé.
- **FR-006**: L'exception `const t = useTranslations()` DOIT être documentée dans `CONTRIBUTING.md`.
- **FR-007**: Toute variable nommée `res`, `data`, `result`, `response` sans qualificatif métier DOIT être renommée.

---

## Plan d'action

### Phase 1 — Corrections P0 sans risque de régression (< 3h)

Renommages purement locaux (portée de fonction, pas d'export) :

| Fichier | Corrections | Effort |
|---|---|---|
| `SearchContext.tsx` — `loadSearch` | `q→restoredQuery`, `f→restoredFilters`, `m→restoredSearchMode`, `lq→restoredLogicalQuery`, `pg→resetPagination` | 20 min |
| `SearchContext.tsx` — `runSearch` | `q→searchQuery`, `f→activeFilters`, `pg→paginationConfig`, `lq→logicalQueryRules`, `sm→currentSearchMode`, `fc→facetConfiguration`, `l→currentLocale`, `res→searchHttpResponse`, `data→searchResult`, `d→doc`, `u→docUrl` | 30 min |
| `SearchContext.tsx` — callbacks | `.some((v)→(filterValues)`, `.filter((v)→(existingValue)` | 10 min |
| `AutocompleteInput.tsx` | `r→inputBoundingRect`, `selected→selectedSuggestion`, `index→matchStartIndex`, `suggestionList→suggestionPortal` | 15 min |
| `SavedSearchesPanel.tsx` — callbacks | `(s)→(savedSearch)`, `(v)→(filterValues)` | 10 min |
| `FacetGroup.tsx` | `(f)→(activeFilter)` | 5 min |
| `api.ts` | `BASE→API_BASE_URL`, `jsonHeaders→buildJsonAuthHeaders`, `bearerHeaders→buildBearerAuthHeaders` | 15 min |

### Phase 2 — Renommages avec impact sur les appelants (< 2h)

Ces renommages touchent des exports ou des méthodes publiques — vérifier tous les points d'appel :

| Fichier | Renommage | Points d'appel à mettre à jour |
|---|---|---|
| `SearchContext.tsx` | `runSearch → executeSearchWithOverrides` | interne uniquement |
| `SavedSearchesPanel.tsx` | `handleToggle → toggleSavedSearchesPanel`, `fetchSearches → fetchSavedSearchesFromApi`, `handleSave → saveCurrentSearch`, `handleDelete → deleteSavedSearch`, `handleLoad → loadAndExecuteSavedSearch` | interne uniquement |
| `SavedSearchesPanel.tsx` | `update → recalculateDropdownPosition` | interne uniquement |

### Phase 3 — Backend Python (< 2h)

| Fichier | Renommages | Effort |
|---|---|---|
| `search_service.py` | `perform_search→execute_cached_search`, `raw_facets→solr_raw_facets`, `normalized_facets→frontend_normalized_facets`, `result→search_result`, `suggest→fetch_autocomplete_suggestions` | 30 min |
| `query_logic_parser.py` | `to_solr_query→convert_to_solr_query_string`, `_parse_rule→_build_solr_rule_fragment`, `_parse_group→_build_solr_group_fragment`, `joined→solr_rules_joined`, `query→solr_group_fragment` | 20 min |
| `facet_config.py` | `load_facet_configs→load_facet_config_from_json`, `build_common_facets_mapping→build_solr_to_frontend_facet_mapping`, `mapping→solr_to_frontend_mapping`, `default_config→default_facet_config`, `solr_field→solr_field_name` | 20 min |

### Phase 4 — Documentation (< 1h)

- Créer `front/CONTRIBUTING.md` avec les 7 règles de nommage + l'exception `t`
- Ajouter une section "Naming" dans `docs/ARCHITECTURE.md`
- Configurer ESLint `id-length: ["warn", { min: 2, exceptions: ["t", "i", "e"] }]`

---

## Success Criteria

- **SC-001**: `grep -rn "\bconst r =\|\bconst q =\|\bconst f =\|\bconst m =\|\bconst lq =\|\bconst pg =\|\bconst sm =\|\bconst l =\b\|\bconst fc =" front/app/` → 0 résultat.
- **SC-002**: `grep -rn "\.map((d) =>\|\.filter((v) =>\|\.some((v) =>\|\.map((s) =>" front/app/` → 0 résultat.
- **SC-003**: `grep -rn "^const BASE " front/app/lib/api.ts` → 0 résultat.
- **SC-004**: `grep -rn "\bconst res =\|\bconst data =" front/app/context/SearchContext.tsx` → 0 résultat.
- **SC-005**: Les 29 tests Playwright restent verts après tous les renommages.
- **SC-006**: `CONTRIBUTING.md` existe avec les 7 règles documentées.

---

## Checklist de revue de code (Nommage)

Pour chaque PR touchant `front/app/` ou `search_api_solr/app/` :

- [ ] Aucune variable locale nommée avec une seule lettre (sauf `t` next-intl, `i` index de boucle, `e` event)
- [ ] Chaque fonction commence par un verbe d'action précis
- [ ] Les paramètres de callbacks `.map/.filter/.some` utilisent le nom du type métier
- [ ] Les `useRef` ont un nom décrivant leur rôle, pas leur type DOM
- [ ] Les constantes de module sont en `SCREAMING_SNAKE_CASE`
- [ ] Aucune variable nommée `res`, `data`, `result` sans qualificatif métier

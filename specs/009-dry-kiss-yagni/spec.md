# Feature Specification: Principes DRY, KISS & YAGNI

**Feature Branch**: `feature/009-dry-kiss-yagni` (à créer depuis `main`)
**Created**: 2026-04-16
**Status**: ✅ Livré complet — P0+P1 (commit ffc7bb5) + P2 (DRY-004/005/KISS-001/002 + DRY-003 résiduel sur Facets.tsx) après livraison de spec 007

## Overview

Audit complet des violations des principes DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid) et YAGNI (You Aren't Gonna Need It) dans le codebase frontend et backend. Chaque violation est documentée avec sa localisation exacte, son impact, et la correction à apporter.

---

## Audit DRY — Duplications identifiées

### DRY-001 — `FACET_I18N` dupliqué dans deux composants

**Fichiers** :
- `front/app/components/Facets.tsx` lignes 9-17
- `front/app/components/ResultsList.tsx` lignes 24-32

**Problème** : La même constante `Record<string, string>` mappant les clés Solr vers les clés i18n est définie deux fois à l'identique. Toute modification (ajout d'une facette) doit être faite dans les deux fichiers.

**Correction** : Extraire dans `front/app/lib/facet-i18n.ts` et importer depuis les deux composants.

```typescript
// front/app/lib/facet-i18n.ts
export const FACET_I18N: Record<string, string> = {
  platform: "platform",
  type: "documentType",
  access: "access",
  translations: "languageFilter",
  author: "qb_fieldAuthor",
  date: "facet_date",
  subscribers: "facet_subscribers",
};
```

---

### DRY-002 — `getFacetLabel` dupliqué dans deux composants

**Fichiers** :
- `front/app/components/Facets.tsx` ligne 27
- `front/app/components/ResultsList.tsx` ligne 29

**Problème** : Deux fonctions `getFacetLabel` avec une logique similaire (lookup config + fallback i18n + fallback clé brute). Les signatures diffèrent légèrement mais le comportement est identique.

**Correction** : Extraire dans `front/app/lib/facet-i18n.ts` comme fonction utilitaire exportée.

---

### DRY-003 — `activeFilters` recalculé dans deux composants

**Fichiers** :
- `front/app/components/Facets.tsx` ligne 23
- `front/app/components/ResultsList.tsx` ligne 20

**Problème** : `Object.entries(filters).flatMap(([field, values]) => values.map(value => ({ identifier: field, value })))` est calculé deux fois indépendamment à partir du même `filters` du contexte.

**Correction** : Exposer `activeFilters` directement depuis `SearchContext` (calculé une seule fois via `useMemo`), ou l'extraire dans un hook `useActiveFilters`.

---

### DRY-004 — Pattern portal + positionnement `getBoundingClientRect` dupliqué

**Fichiers** :
- `front/app/components/SavedSearchesPanel.tsx` lignes 24-66
- `front/app/components/AutocompleteInput.tsx` lignes 27-48

**Problème** : Les deux composants implémentent indépendamment le même pattern :
1. `useState` pour la position `{ top, left/right, width }`
2. `getBoundingClientRect()` sur un `ref`
3. `useEffect` avec `window.addEventListener('scroll', update, true)` + `resize`
4. `createPortal` sur `document.body` avec `position: fixed`

C'est ~30 lignes de logique identique dupliquées.

**Correction** : Extraire un hook `useAnchoredPortal(anchorRef)` qui retourne `{ portalStyle, updatePosition }`.

```typescript
// front/app/hooks/useAnchoredPortal.ts
export function useAnchoredPortal(anchorRef: RefObject<HTMLElement>, open: boolean) {
  const [style, setStyle] = useState<CSSProperties>({});
  const update = useCallback(() => {
    if (!anchorRef.current) return;
    const r = anchorRef.current.getBoundingClientRect();
    setStyle({ position: "fixed", top: r.bottom + 8, left: r.left, width: r.width, zIndex: 2147483647 });
  }, [anchorRef]);
  useEffect(() => {
    if (!open) return;
    update();
    window.addEventListener("scroll", update, true);
    window.addEventListener("resize", update);
    return () => { window.removeEventListener("scroll", update, true); window.removeEventListener("resize", update); };
  }, [open, update]);
  return { style, update };
}
```

---

### DRY-005 — Pattern `useClickOutside` dupliqué

**Fichiers** :
- `front/app/components/SavedSearchesPanel.tsx` lignes 33-46
- `front/app/components/AutocompleteInput.tsx` lignes 55-62

**Problème** : Les deux composants implémentent un `useEffect` avec `document.addEventListener('mousedown', handleClickOutside)` pour fermer au clic extérieur. Logique identique, ~10 lignes dupliquées.

**Correction** : Extraire un hook `useClickOutside(refs: RefObject[], onClose: () => void)`.

```typescript
// front/app/hooks/useClickOutside.ts
export function useClickOutside(refs: RefObject<HTMLElement | null>[], onClose: () => void) {
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as Node;
      if (refs.some(r => r.current?.contains(target))) return;
      onClose();
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [refs, onClose]);
}
```

---

### DRY-006 — Spinner CSS dupliqué dans 3 composants

**Fichiers** :
- `front/app/components/AuthModal.tsx` ligne 256 : `w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin`
- `front/app/components/SavedSearchesPanel.tsx` ligne 194 : `w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin`
- `front/app/components/AutocompleteInput.tsx` ligne 190 : `w-5 h-5 border-2 border-highlight border-t-transparent rounded-full animate-spin`

**Problème** : Le même pattern de spinner CSS est répété 3 fois avec de légères variations de taille et couleur.

**Correction** : Créer un composant `<Spinner size={sm|md|lg} color="white|highlight" />`.

---

### DRY-007 — Guard SSR `typeof document === "undefined"` dupliqué

**Fichiers** :
- `front/app/components/AuthModal.tsx` ligne 89
- `front/app/components/SavedSearchesPanel.tsx` ligne 127
- `front/app/components/AutocompleteInput.tsx` ligne 133

**Problème** : Le guard SSR est répété dans chaque composant utilisant `createPortal`. Pas critique mais symptomatique d'un pattern non centralisé.

**Correction** : Créer un hook `useIsClient()` retournant `boolean`, ou un composant `<ClientOnly>`.

---

### DRY-008 — Logique "has active search" dupliquée dans 3 endroits

**Fichiers** :
- `front/app/context/SearchContext.tsx` lignes 139-142 et 257-259
- `front/app/components/ResultsList.tsx` lignes 37-38
- `front/app/components/SavedSearchesPanel.tsx` ligne 124-125

**Problème** : La condition "est-ce qu'une recherche est active ?" est recalculée différemment dans chaque fichier :
- `SearchContext` : `!q && !hasFilters && !hasLogical`
- `ResultsList` : `searchMode === "simple" ? !!query : hasLogicalRules`
- `SavedSearchesPanel` : `query || Object.values(filters).some(...) || Array.isArray(logicalQuery?.rules)...`

Trois variantes légèrement différentes de la même logique métier.

**Correction** : Exposer `hasActiveSearch: boolean` depuis `SearchContext` (calculé une seule fois via `useMemo`).

---

### DRY-009 — Clés `localStorage` dupliquées en strings littérales

**Fichier** : `front/app/context/AuthContext.tsx` lignes 44, 45, 51, 52, 72, 73, 107, 108

**Problème** : Les clés `"auth_token"` et `"auth_user"` apparaissent 4 fois chacune comme strings littérales. Une faute de frappe sur l'une d'elles crée un bug silencieux.

**Correction** :
```typescript
// front/app/lib/storage-keys.ts
export const STORAGE_KEYS = { TOKEN: "auth_token", USER: "auth_user" } as const;
```

---

### DRY-010 — Couleurs hardcodées dans `Pagination.tsx` au lieu des tokens Tailwind

**Fichier** : `front/app/components/Pagination.tsx` lignes 44, 51, 58-59, 70

**Problème** : `#f03603`, `#e6e4e2`, `#969493` sont utilisés directement au lieu des classes `text-highlight`, `border-border`, `text-muted-foreground` déjà définies dans le thème. Incohérence avec le reste du codebase et rupture du dark mode.

**Correction** : Remplacer par les classes Tailwind du design system :
- `#f03603` → `text-highlight` / `border-highlight` / `bg-highlight`
- `#e6e4e2` → `border-border`
- `#969493` → `text-muted-foreground`

---

## Audit KISS — Complexité inutile identifiée

### KISS-001 — `AutocompleteInput` couplé à `SearchContext`

**Fichier** : `front/app/components/AutocompleteInput.tsx` ligne 8

**Problème** : `AutocompleteInput` importe directement `useSearch()` pour accéder à `suggestions`, `fetchSuggestions`, `loadingSuggestions`. Ce composant est utilisé dans `SearchBar` ET dans `AdvancedQueryBuilder` (via `QueryBuilderAutocompleteValueEditor`), mais il est impossible de l'utiliser dans un autre contexte sans `SearchProvider`.

**Correction** : Passer `suggestions`, `onFetchSuggestions`, `loadingSuggestions` en props. `SearchBar` et `AdvancedQueryBuilder` les récupèrent depuis le contexte et les passent en props. Le composant devient pur et testable.

---

### KISS-002 — `AuthContext` gère l'état de la modal

**Fichier** : `front/app/context/AuthContext.tsx` lignes 18-21, 35-36, 116-126

**Problème** : `AuthContext` expose `modalOpen`, `modalTab`, `openModal`, `closeModal` — l'état UI de la modal est mélangé avec la logique d'authentification. Un contexte d'auth ne devrait pas savoir qu'une modal existe.

**Impact** : Tester `AuthContext` nécessite de gérer l'état modal. Remplacer la modal par un autre mécanisme UI nécessite de modifier le contexte.

**Correction** : Déplacer l'état modal dans un `useAuthModal` local à `AuthButtons.tsx` ou dans un contexte `UIContext` séparé.

---

### KISS-003 — `page.tsx` contient la logique de layout ET les données `PLATFORMS`

**Fichier** : `front/app/[locale]/page.tsx` lignes 29-35

**Problème** : La constante `PLATFORMS` avec les couleurs des plateformes est définie directement dans le composant de page. C'est une donnée de configuration qui devrait vivre dans `lib/constants.ts` ou `lib/platforms.ts`.

**Correction** : Extraire dans `front/app/lib/platforms.ts`.

---

### KISS-004 — `AdvancedQueryBuilder` contient un `<style jsx global>`

**Fichier** : `front/app/components/AdvancedQueryBuilder.tsx` lignes 100-115

**Problème** : Des styles globaux CSS pour `.query-builder-premium` sont injectés via `<style jsx global>` dans un composant React. Ces styles devraient être dans `globals.css`.

**Correction** : Déplacer le bloc CSS dans `front/app/globals.css` sous un commentaire `/* QueryBuilder premium styles */`.

---

### KISS-005 — `placeholder` extrait via une chaîne de 8 vérifications `typeof`

**Fichier** : `front/app/components/AdvancedQueryBuilder.tsx` lignes 19-33

**Problème** : L'extraction du placeholder depuis `props.schema.translations.value.label` utilise 8 vérifications `typeof` imbriquées pour éviter un crash. C'est du code défensif excessif pour accéder à une propriété optionnelle.

**Correction** :
```typescript
// Avant — 8 lignes de typeof
const placeholder = typeof props.schema === "object" && ...

// Après — 1 ligne
const placeholder = (props.schema as any)?.translations?.value?.label ?? "Value";
```

---

## Audit YAGNI — Code non nécessaire identifié

### YAGNI-001 — `PermissionsCache` spécifié mais non implémenté

**Fichier** : `specs/005-permissions/spec.md` — Key Entities

**Problème** : La spec 005 mentionnait une `PermissionsCache: Map<url, PermissionStatus>` pour éviter les appels dupliqués lors d'un changement de page. Cette cache n'est pas implémentée et le comportement actuel (reset à chaque page) est fonctionnel. Implémenter une cache côté frontend avant de mesurer si c'est un problème réel serait du YAGNI.

**Décision** : Ne pas implémenter tant que les métriques de performance ne montrent pas un problème réel. La mention de `PermissionsCache` a été supprimée des Key Entities de la spec 005 le 2026-04-16. Le cache existant côté backend Redis reste conservé.

---

### YAGNI-002 — `SearchState` interface dans `types.ts` non utilisée

**Fichier** : `front/app/types.ts` lignes 95-106

**Problème** : L'interface `SearchState` est définie mais n'est importée nulle part dans le codebase. Elle duplique partiellement `SearchContextValue`.

**Correction** : Supprimer `SearchState` de `types.ts`.

```bash
grep -rn "SearchState" front/app/  # → 0 résultat hors types.ts
```

---

### YAGNI-003 — Commentaire `// setSuggestions([])` laissé dans le code

**Fichier** : `front/app/components/AutocompleteInput.tsx` ligne 72

**Problème** : `// setSuggestions([]); // Géré par fetchSuggestions si q court` — code commenté laissé en place. Pas de valeur, crée du bruit.

**Correction** : Supprimer la ligne.

---

### YAGNI-004 — `highlighting` retourné par le backend mais jamais consommé

**Fichier** : `search_api_solr/app/services/search_service.py` ligne 87

**Problème** : `"highlighting": solr_data.get("highlighting", {})` est inclus dans la réponse de recherche mais le frontend ne l'utilise jamais (`SearchDoc` ne contient pas de champ highlighting, `ResultItem` n'affiche pas de texte surligné).

**Décision** : Ne pas supprimer pour l'instant (utile pour une future spec), mais documenter explicitement que c'est une fondation pour une future feature de highlighting — sinon c'est du YAGNI silencieux.

---

## Requirements

### Functional Requirements

- **FR-001**: `FACET_I18N` et `getFacetLabel` DOIVENT exister en un seul endroit (`lib/facet-i18n.ts`).
- **FR-002**: `activeFilters` et `hasActiveSearch` DOIVENT être exposés par `SearchContext` (calculés une seule fois).
- **FR-003**: Les patterns `useClickOutside` et `useAnchoredPortal` DOIVENT être des hooks réutilisables dans `front/app/hooks/`.
- **FR-004**: `AutocompleteInput` NE DOIT PAS importer `useSearch` — ses données arrivent par props.
- **FR-005**: Les clés `localStorage` DOIVENT être des constantes dans `lib/storage-keys.ts`.
- **FR-006**: `Pagination.tsx` DOIT utiliser les classes Tailwind du design system, pas des couleurs hex hardcodées.
- **FR-007**: `AuthContext` NE DOIT PAS gérer l'état de la modal.
- **FR-008**: `SearchState` (interface inutilisée) DOIT être supprimée de `types.ts`.
- **FR-009**: `<style jsx global>` dans `AdvancedQueryBuilder` DOIT être déplacé dans `globals.css`.

### Non-Functional Requirements

- **NFR-001**: Aucune régression sur les 33 tests Playwright existants.
- **NFR-002**: `grep -rn "FACET_I18N" front/app/components/` retourne 0 résultat après correction.
- **NFR-003**: `grep -rn "#f03603\|#e6e4e2\|#969493" front/app/components/` retourne 0 résultat après correction.
- **NFR-004**: `grep -rn "style jsx global" front/app/components/` retourne 0 résultat après correction.

---

## Plan d'action

### Priorité P0 — Corrections sans risque (< 2h chacune)

| ID | Correction | Fichiers touchés | Effort |
|---|---|---|---|
| DRY-001/002 | Extraire `FACET_I18N` + `getFacetLabel` dans `lib/facet-i18n.ts` | `Facets.tsx`, `ResultsList.tsx`, nouveau `lib/facet-i18n.ts` | 30 min |
| DRY-009 | Extraire clés localStorage dans `lib/storage-keys.ts` | `AuthContext.tsx`, nouveau `lib/storage-keys.ts` | 15 min |
| DRY-010 | Remplacer couleurs hex dans `Pagination.tsx` par classes Tailwind | `Pagination.tsx` | 15 min |
| KISS-004 | Déplacer `<style jsx global>` dans `globals.css` | `AdvancedQueryBuilder.tsx`, `globals.css` | 15 min |
| YAGNI-002 | Supprimer `SearchState` de `types.ts` | `types.ts` | 5 min |
| YAGNI-003 | Supprimer commentaire mort dans `AutocompleteInput.tsx` | `AutocompleteInput.tsx` | 5 min |
| KISS-005 | Simplifier extraction placeholder QB | `AdvancedQueryBuilder.tsx` | 10 min |
| KISS-003 | Extraire `PLATFORMS` dans `lib/platforms.ts` | `page.tsx`, nouveau `lib/platforms.ts` | 10 min |

### Priorité P1 — Corrections avec refactorisation légère (< 4h chacune)

| ID | Correction | Fichiers touchés | Effort |
|---|---|---|---|
| DRY-003/008 | Exposer `activeFilters` + `hasActiveSearch` depuis `SearchContext` | `SearchContext.tsx`, `Facets.tsx`, `ResultsList.tsx`, `SavedSearchesPanel.tsx` | 1h |
| DRY-006 | Créer composant `<Spinner>` | nouveau `components/Spinner.tsx`, 3 composants | 30 min |
| DRY-007 | Créer hook `useIsClient()` | nouveau `hooks/useIsClient.ts`, 3 composants | 20 min |

### Priorité P2 — Corrections structurelles (dépendent de `007`)

| ID | Correction | Fichiers touchés | Effort | Prérequis |
|---|---|---|---|---|
| DRY-004 | Extraire `useAnchoredPortal` | nouveau `hooks/useAnchoredPortal.ts`, `SavedSearchesPanel.tsx`, `AutocompleteInput.tsx` | 2h | `007` recommandé |
| DRY-005 | Extraire `useClickOutside` | nouveau `hooks/useClickOutside.ts`, `SavedSearchesPanel.tsx`, `AutocompleteInput.tsx` | 1h | `007` recommandé |
| KISS-001 | Découpler `AutocompleteInput` de `SearchContext` | `AutocompleteInput.tsx`, `SearchBar.tsx`, `AdvancedQueryBuilder.tsx` | 2h | `007` recommandé |
| KISS-002 | Sortir état modal de `AuthContext` | `AuthContext.tsx`, `AuthButtons.tsx`, `AuthModal.tsx` | 2h | — |

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: `grep -rn "FACET_I18N" front/app/components/` → 0 résultat.
- **SC-002**: `grep -rn "#f03603\|#e6e4e2\|#969493" front/app/components/` → 0 résultat.
- **SC-003**: `grep -rn "style jsx global" front/app/components/` → 0 résultat.
- **SC-004**: `grep -rn "SearchState" front/app/` → 0 résultat hors `types.ts` (supprimé).
- **SC-005**: `grep -rn "auth_token\|auth_user" front/app/` → 0 résultat hors `lib/storage-keys.ts`.
- **SC-006**: `AutocompleteInput.tsx` ne contient plus d'import `useSearch`.
- **SC-007**: Les 33 tests Playwright restent verts.

### Checklist de revue de code (DRY/KISS/YAGNI)

Pour chaque PR touchant `front/app/` :

- [ ] Aucune constante définie dans plus d'un fichier
- [ ] Aucune logique métier dupliquée entre composants (extraire dans un hook ou `lib/`)
- [ ] Aucune couleur hex hardcodée — utiliser les tokens Tailwind du thème
- [ ] Aucun code commenté laissé en place
- [ ] Aucune interface TypeScript définie mais non utilisée
- [ ] Aucun composant UI qui importe directement un contexte dont il n'a pas besoin
- [ ] Aucune feature implémentée sans use-case concret documenté dans une spec

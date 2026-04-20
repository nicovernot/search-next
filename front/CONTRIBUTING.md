# Règles de contribution — OpenEdition Search (frontend)

## Nommage — Principe Intention → Résultat

Chaque nom doit répondre à deux questions : *que veut-on faire ?* et *qu'obtient-on ?*

### Règle 1 — Variables : Adjectif + Nom métier

```typescript
// ❌
const res = await api.search(...)
const data = await res.json()

// ✅
const searchHttpResponse = await api.search(...)
const searchResult = await searchHttpResponse.json()
```

### Règle 2 — Fonctions : Verbe d'action + Complément métier

```typescript
// ❌
runSearch()
handleToggle()

// ✅
executeSearchWithOverrides()
toggleSavedSearchesPanel()
```

Verbes autorisés : `execute`, `fetch`, `build`, `load`, `toggle`, `save`, `delete`, `convert`, `render`, `validate`.

### Règle 3 — Callbacks `.map/.filter/.some` : Nom du type métier au singulier

```typescript
// ❌
results.map((d) => d.url)
filters.some((v) => v.length > 0)

// ✅
results.map((doc) => doc.url)
filterValues.some((filterValues) => filterValues.length > 0)
```

### Règle 4 — `useRef` : Suffixe `Ref` + rôle dans le composant

```typescript
// ❌
const buttonRef = useRef(null)  // quel bouton ?

// ✅
const savedSearchesButtonRef = useRef(null)
```

### Règle 5 — Constantes de module : `SCREAMING_SNAKE_CASE` + domaine

```typescript
// ❌
const BASE = "http://..."

// ✅
const API_BASE_URL = "http://..."
```

### Règle 6 — Exception documentée : `t` pour next-intl

`const t = useTranslations()` est une convention de l'écosystème next-intl, reconnue des développeurs React et des LLMs. Elle est **exemptée** de la règle 1. Toute autre abréviation d'une lettre est interdite sauf :

- `i` pour un index de boucle très local
- `e` pour un event très local

### Règle 7 — Interdictions explicites

Toute variable nommée `res`, `data`, `result`, `response`, `q`, `f`, `m`, `l` sans qualificatif métier est interdite si sa portée dépasse 3 lignes.

---

## Checklist de revue de code

Pour chaque PR touchant `front/app/` :

- [ ] Aucune variable locale nommée avec une seule lettre (sauf `t`, `i`, `e`)
- [ ] Chaque fonction commence par un verbe d'action précis
- [ ] Les callbacks `.map/.filter/.some` utilisent le nom du type métier
- [ ] Les `useRef` ont un nom décrivant leur rôle
- [ ] Les constantes de module sont en `SCREAMING_SNAKE_CASE`
- [ ] Aucune variable nommée `res`, `data`, `result` sans qualificatif métier
- [ ] Aucune constante définie dans plus d'un fichier
- [ ] Aucune couleur hex hardcodée — utiliser les tokens Tailwind du thème
- [ ] Aucun code commenté laissé en place
- [ ] Aucune interface TypeScript définie mais non utilisée

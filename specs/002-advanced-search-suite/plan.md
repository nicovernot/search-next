# Technical Plan: Advanced Search Suite

## Options retenues
- **Mode avancé** : `react-querybuilder`
- **Langues** : `next-intl` avec routing `[locale]`
- **Base de données backend** : PostgreSQL avec SQLAlchemy (via FastAPI)

---

## Avancement au 2026-04-13

| Phase | Statut |
|---|---|
| Phase 1 — Backend Infrastructure & DB | ✅ Complète |
| Phase 2 — Autocomplétion | ✅ Complète |
| Phase 3 — Query Builder avancé | ✅ Complète |
| Phase 4 — i18n (FR/EN/ES/DE/IT/PT) | ✅ Complète — 67 clés, 6 langues, 0 hardcodé |
| Phase 5 — Saved Searches | ✅ Complète |
| Spec 003 — UX Premium | ✅ Complète (dark mode, glassmorphism, animations) |
| Correctifs CORS + pagination/filtres + i18n | ✅ Appliqués le 2026-04-13 |
| Refactor SearchContext (latest ref) + loadSearch | ✅ Appliqué le 2026-04-13 |

---

## Décisions clôturées

### D-001 : Langue allemande (DE) → **Option A retenue**
- 6 langues : FR, EN, ES, DE, IT, PT

### D-002 : next-intl vs I18nContext custom → **Option A retenue**
- Migration complète vers next-intl v4 avec routing `[locale]` (`/fr/`, `/en/`, etc.)
- `I18nContext` custom supprimé

---

## 1. Phase 5 — Recherches Sauvegardées

### Backend (FastAPI)

**Nouveau fichier** : `search_api_solr/app/api/v1/saved_searches.py`

Endpoints à implémenter :
```
GET  /saved-searches          → liste les recherches de l'utilisateur connecté
POST /saved-searches          → sauvegarde une nouvelle recherche
DELETE /saved-searches/{id}   → supprime une recherche
```

Tous les endpoints nécessitent le header `Authorization: Bearer <token>`.

Dépendance de sécurité à créer : `get_current_user` qui décode le JWT et retourne l'utilisateur.

**Modèle SavedSearch** (déjà dans la DB) :
```python
class SavedSearch(Base):
    id, user_id, name, query_json, created_at
```

**Implémenté** :
- [x] `app/api/v1/saved_searches.py`
- [x] `app/core/dependencies.py` avec `get_current_user`
- [x] Router enregistré dans `main.py`

### Frontend (Next.js)

**AuthContext** (`front/app/context/AuthContext.tsx`) :
- Stocke `{ user, token }` dans `localStorage`
- Expose `login(email, password)`, `register(email, password)`, `logout()`
- Appels vers `/auth/login` et `/auth/register`

**Composants implémentés** :
- `AuthModal.tsx` — Modal login/register avec deux onglets
- `SavedSearchesPanel.tsx` — Dropdown listant les recherches sauvegardées et l'action de sauvegarde

**Intégration dans page.tsx** :
- Ajouter le bouton "Se connecter" dans le header
- `SavedSearchesPanel` accessible depuis le header

---

## 2. Frontend (Next.js - `front`)
1. **Intégration next-intl** :
   - Routing `[locale]` en place
   - `I18nContext` custom supprimé
2. **Auth & Saved Searches** :
   - `AuthContext` avec `localStorage`
   - Composants : `AuthModal`, `SavedSearchesPanel`

---

## 3. Backend (FastAPI - `search_api_solr`)
1. **CRUD Saved Searches** :
   - Endpoint `/saved-searches` (GET, POST, DELETE)
   - Middleware de décodage JWT (`get_current_user`)
2. **Enregistrement du router** dans `main.py`

---

## Notes de cohérence

1. La spec décrit maintenant l'état final livré, sans options abandonnées.
2. L'autocomplétion est branchée sur la recherche simple et sur les champs de valeur de la recherche avancée.
3. Le thème premium est suivi dans la spec `003`.

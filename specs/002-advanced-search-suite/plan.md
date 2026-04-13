# Technical Plan: Advanced Search Suite

## Options retenues
- **Mode avancé** : `react-querybuilder`
- **Langues** : `I18nContext` custom (next-intl installé mais non utilisé pour le routing)
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

## 1. Phase 4 — Compléter i18n (si applicable)

### Ajouter DE (si décision D-001 = Option A ou B)
- Créer `/public/locales/de/translation.json` avec toutes les clés
- Ajouter `"de"` dans `SUPPORTED_LANGS` de `I18nContext.tsx`
- Ajouter l'option dans le `LanguageSelector`

---

## 2. Phase 5 — Recherches Sauvegardées

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

**À faire** :
- [ ] Créer `app/api/v1/saved_searches.py` avec les 3 endpoints
- [ ] Créer `app/core/dependencies.py` avec `get_current_user(token: str, db: Session)`
- [ ] Enregistrer le router dans `main.py`

### Frontend (Next.js)

**AuthContext** (`front/app/context/AuthContext.tsx`) :
- Stocke `{ user, token }` dans `localStorage`
- Expose `login(email, password)`, `register(email, password)`, `logout()`
- Appels vers `/auth/login` et `/auth/register`

**Composants à créer** :
- `AuthModal.tsx` — Modal login/register avec deux onglets
- `SaveSearchButton.tsx` — Bouton "Sauvegarder" affiché après une recherche (si connecté)
- `SavedSearchesPanel.tsx` — Panneau latéral ou dropdown listant les recherches sauvegardées

**Intégration dans page.tsx** :
- Ajouter le bouton "Se connecter" dans le header
- Afficher `SaveSearchButton` après les résultats si `token` présent
- `SavedSearchesPanel` accessible depuis le header

---

## 3. Frontend (Next.js - `front`)
1. **Intégration next-intl** (si décision D-002 = Option A) :
   - Migration vers routing `[locale]` — breaking change
   - Sinon : conserver I18nContext (fonctionnel)
2. **Auth & Saved Searches** :
   - `AuthContext` avec `localStorage`
   - Composants : `AuthModal`, `SaveSearchButton`, `SavedSearchesPanel`

---

## 4. Backend (FastAPI - `search_api_solr`)
1. **CRUD Saved Searches** :
   - Endpoint `/saved-searches` (GET, POST, DELETE)
   - Middleware de décodage JWT (`get_current_user`)
2. **Enregistrement du router** dans `main.py`

---

## Ordre d'implémentation recommandé

1. Décisions D-001 et D-002 à valider
2. Phase 5 Backend : `saved_searches.py` + `get_current_user`
3. Phase 5 Frontend : `AuthContext` + `AuthModal`
4. Phase 5 Frontend : `SaveSearchButton` + `SavedSearchesPanel`
5. Tests Playwright pour le flow complet (register → login → search → save → reload)
6. (Optionnel) Ajout langue DE

# 🔒 Configuration CORS — OpenEdition Search

**Dernière vérification** : 2026-09-03 — configuration confirmée contre `search_api_solr/app/settings.py` (`get_cors_origins`, `Settings.cors_*`) et `search_api_solr/app/main.py` (montage du middleware).

Ce document décrit la configuration CORS (Cross-Origin Resource Sharing) réellement implémentée dans le backend FastAPI, environnement par environnement.

## Contexte historique

Le middleware CORS était initialement configuré en `allow_origins=["*"]` (tout autorisé). Cette configuration a été remplacée par une liste blanche pilotée par environnement — voir `specs/PLANNING.md` § P0 (résolu 2026-04-20).

## Configuration actuelle

### 1. Origines par défaut (`app/settings.py::get_cors_origins`)

La fonction lit d'abord la variable d'environnement `CORS_ORIGINS` (liste CSV ou JSON) ; si elle est absente, elle retourne une liste par défaut selon `ENVIRONMENT` :

| Environnement | Origines par défaut si `CORS_ORIGINS` non définie |
|---|---|
| `production` | `https://search.openedition.org`, `https://www.openedition.org` |
| `staging` | `https://staging.search.openedition.org`, `https://search.openedition.org` |
| `test` | `http://localhost:8007`, `http://localhost:3009`, `http://127.0.0.1:3009`, `http://127.0.0.1:8007` |
| `development` (défaut) | `http://localhost:<PORT>` / `http://127.0.0.1:<PORT>` / `http://0.0.0.0:<PORT>` pour les ports frontend historiques et actuels (3000, 3003, 3007, 3009) |

### 2. Champs `Settings` associés

`cors_origins`, `cors_allow_credentials` (défaut `true`), `cors_allow_methods` (`GET,POST,PUT,DELETE,OPTIONS`), `cors_allow_headers`, `cors_expose_headers` (`X-Total-Count,X-Pagination`), `cors_max_age` — ajusté automatiquement par environnement (86400s en dev/staging, 3600s en production, 60s en test) via un `field_validator` Pydantic.

### 3. Montage du middleware (`app/main.py`)

```python
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        expose_headers=settings.cors_expose_headers,
        max_age=settings.cors_max_age,
    )
else:
    logger.warning("No CORS origins configured. CORS middleware not added.")
```

### 4. Configurer une nouvelle origine

Ajouter/modifier `CORS_ORIGINS` dans le fichier `.env.{environment}` correspondant (voir [ENVIRONMENTS.md](./ENVIRONMENTS.md)) :

```env
CORS_ORIGINS=<https://mon-origine-1>,<https://mon-origine-2>
```

## Vérifier la configuration

```bash
# Tests unitaires dédiés
cd search_api_solr && pytest tests/test_environment_config.py -k CORS

# Vérification manuelle des headers CORS retournés par l'API
curl -I -H "Origin: <ORIGIN_ATTENDUE>" <API_BASE_URL>/api/v1/search
```

## Bonnes pratiques

- `allow_credentials=True` n'est utile que si l'application envoie des cookies/auth via CORS — vérifier que ce n'est pas activé sans raison.
- En production, les origines doivent être en HTTPS et listées explicitement (jamais `*`).
- Toute nouvelle origine ajoutée doit être documentée ici et dans `.env.{environment}`.

## Résolution des problèmes courants

**CORS bloqué en développement**
1. Vérifier que `.env.development` (ou `CORS_ORIGINS`) contient l'origine du frontend utilisée.
2. Vérifier que `ENVIRONMENT=development` est bien défini.
3. Après modification, recréer le conteneur API pour relire l'environnement : `docker compose up -d --force-recreate --no-deps api`.

**Les credentials ne sont pas envoyés**
1. Vérifier `cors_allow_credentials=True` côté backend.
2. Le frontend doit inclure `credentials: 'include'` dans ses requêtes.
3. L'origine doit être exacte (pas de wildcard) — incompatible avec `allow_credentials=True`.

## Ressources externes

- [MDN Web Docs — CORS](https://developer.mozilla.org/fr/docs/Web/HTTP/CORS)
- [OWASP — CORS Security](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#cross-origin-resource-sharing)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)

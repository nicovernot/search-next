# Plan 006 — Corrections & Fondations Techniques

## Architecture

```
search_api_solr/
├── app/
│   ├── api/
│   │   └── auth.py                # 409 conflict + messages d'erreur
│   ├── services/
│   │   ├── search_service.py      # logique de recherche et config
│   │   └── facet_config.py        # mapping des facettes / champs QB
│   ├── settings.py                # durée du token JWT, envs
│   └── main.py                    # endpoints backend
front/
├── app/
│   ├── context/
│   │   ├── AuthContext.tsx        # session + erreurs UI
│   │   └── SearchContext.tsx      # accès aux searchFields + API client
│   ├── lib/
│   │   ├── api.ts                 # client API centralisé
│   │   ├── qb-fields.ts           # fallback des champs QB
│   │   └── storage-keys.ts        # centralisation des clés storage
│   ├── messages/
│   │   └── *.json                 # clés d'erreur traduites
│   └── components/
│       └── AdvancedQueryBuilder.tsx # champs chargés depuis config
```

## Data Flow

1. Les paramètres de configuration de l'environnement alimentent les tokens et paramètres backend.
2. Le frontend centralise ses appels API dans `lib/api.ts` pour éviter la dispersion de `fetch()`.
3. `/facets/config` alimente les champs avancés du QueryBuilder et la configuration des facettes.
4. Les erreurs d'authentification sont normalisées en codes stables puis traduites via next-intl.
5. Les retours backend cohérents garantissent un comportement correct avec les futures specs de permissions et de recherche avancée.

## Key Files

| Fichier | Rôle |
|---------|------|
| `search_api_solr/app/settings.py` | Durée de vie des tokens JWT |
| `search_api_solr/app/api/auth.py` | Conformité HTTP 409 sur email existant |
| `search_api_solr/app/services/facet_config.py` | Configuration Solr / champs QB |
| `front/app/lib/api.ts` | Client API centralisé |
| `front/app/context/AuthContext.tsx` | Gestion des codes d'erreur + session |
| `front/app/context/SearchContext.tsx` | Exposition des `searchFields` et hooks API |
| `front/app/components/AdvancedQueryBuilder.tsx` | Use des champs dynamiques |
| `front/messages/*.json` | Traductions d'erreurs |

## Path to Production Readiness

- Vérifier les valeurs d'environnement pour les tokens prod/staging.
- Valider que les appels API backend passent tous par le client unique.
- Vérifier la compatibilité du QueryBuilder avec les champs Solr dynamiques.
- S'assurer que les erreurs d'auth restent traduites dans les locales supportées.

## Risks / Follow-up

- Risque de régression si un appel `fetch()` est réintroduit hors `lib/api.ts`.
- Risque d'impact sur l'expérience si les champs QB ne sont plus synchronisés avec les facettes backend.
- Risque d'incohérence dépendant de l'environnement si les variables d'environnement diffèrent entre zones.

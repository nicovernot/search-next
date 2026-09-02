# Plan 005 — Permissions & Accès aux Résultats

## Architecture

```
front/
├── app/
│   ├── api/
│   │   └── permissions/route.ts    # relay côté serveur
│   ├── components/
│   │   ├── ResultItem.tsx           # badge d'accès par document
│   │   └── ResultsList.tsx          # affichage et pass-through des états
│   ├── context/
│   │   └── SearchContext.tsx        # state permissions + org context
│   ├── hooks/
│   │   └── usePermissions.ts        # batch `/permissions`
│   └── lib/
│       └── api.ts                   # client dédié pour les appels API
search_api_solr/
├── app/
│   └── services/
│       ├── search_service.py
│       ├── docs_permissions_client.py
│       └── cache_service.py
└── app/main.py                      # endpoint `/permissions` et forwarding IP
```

## Data Flow

1. Les résultats sont affichés sans bloquer sur les permissions.
2. `usePermissions` récupère les URLs visibles sur la page courante.
3. Le frontend appelle un batch `/permissions` via la route interne Next.js.
4. La route transmet la bonne IP via `X-Forwarded-For` au backend.
5. Le backend répond avec le statut d'accès (`open`, `restricted`, `institutional`, `unknown`).
6. `ResultItem` mappe cette réponse en label visuel et en couleur.
7. En cas d'erreur ou de réponse partielle, le système retombe sur un état neutre sans casser l'affichage.

## Key Files

| Fichier | Rôle |
|---------|------|
| `front/app/hooks/usePermissions.ts` | Appel batch et stockage des permissions |
| `front/app/components/ResultItem.tsx` | Badge d'accès visuel |
| `front/app/components/ResultsList.tsx` | Affichage des résultats + états de permission |
| `front/app/api/permissions/route.ts` | Proxy côté serveur vers le backend |
| `front/app/lib/api.ts` | Client API partagé pour les appels internes |
| `search_api_solr/app/main.py` | Endpoint `/permissions` et stratégie IP |
| `search_api_solr/app/services/docs_permissions_client.py` | Vérification du statut d'accès |

## Operational Constraints

- Les permissions doivent rester non bloquantes pour la recherche.
- La route Next.js doit transmettre l'IP réelle de l'utilisateur à l'API backend.
- Les cas d'erreur doivent tomber en mode `unknown` sans crash UI.
- Les statuts doivent être exposés en i18n dans les 6 langues.

## Risks / Follow-up

- Risque de latence si un batch trop volumineux est envoyé au backend.
- Risque de faux positifs si l'IP est mal transmise ou si X-Forwarded-For est absent.
- Risque d'incohérence entre backend et UI si les statuts sont ajoutés plus tard.

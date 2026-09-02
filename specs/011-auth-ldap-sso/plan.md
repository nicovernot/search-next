# Plan 011 — Auth LDAP / SSO

## Architecture

```
search_api_solr/
├── app/
│   ├── api/
│   │   └── auth.py                # login, register, SSO, LDAP
│   ├── services/
│   │   ├── auth_service.py        # logique d'authentification
│   │   ├── ldap_service.py        # intégration LDAP
│   │   └── sso_service.py         # OIDC / SSO à code court
│   ├── settings.py                # config auth, JWT, environnements
│   └── main.py                    # endpoints auth et verification
front/
├── app/
│   ├── context/
│   │   └── AuthContext.tsx        # session et refresh auth
│   ├── components/
│   │   ├── AuthModal.tsx          # modale d'auth et méthodes sociales
│   │   └── SSOButton.tsx          # bouton SSO / LDAP
│   ├── lib/
│   │   └── api.ts                 # appels bearer auth
│   └── messages/
│       └── *.json                 # libellés auth et erreurs
```

## Data Flow

1. L'utilisateur choisit un mode d'authentification : email/mot de passe, LDAP ou SSO.
2. Le frontend envoie la demande au backend par le client API centralisé.
3. `auth_service` valide les identifiants ou la session institutionnelle.
4. Pour le cas SSO, un code court à usage unique est utilisé afin de sécuriser le flux.
5. Le backend émet un token JWT en fonction du rôle et des droits d'accès.
6. L'UI met à jour l'état de session et la recherche continue avec les droits corrects.

## Key Files

| Fichier | Rôle |
|---------|------|
| `search_api_solr/app/api/auth.py` | Endpoints login / register / LDAP / SSO |
| `search_api_solr/app/services/auth_service.py` | Logique d'échange authentification |
| `search_api_solr/app/services/ldap_service.py` | Intégration LDAP institutionnelle |
| `search_api_solr/app/services/sso_service.py` | Flux SSO sécurisé |
| `front/app/context/AuthContext.tsx` | Gestion de session côté client |
| `front/app/components/AuthModal.tsx` | Interface d'auth et gestion erreurs |
| `front/messages/*.json` | Traductions de l'interface auth |

## Security Requirements

- Les flux SSO doivent utiliser un code court à usage unique.
- Les tokens JWT doivent respecter les TTLs et secrets d'environnement.
- Les décisions d'accès doivent faire l'objet d'un contrôle côté backend et non seulement côté client.
- Les messages d'erreur doivent rester traduits et sans fuite d'information sensible.

## Risks / Follow-up

- Risque d'incohérence entre le backend et le frontend sur les rôles / permissions.
- Risque de régression sur les parcours connectés dans les environnements staging/prod.
- Le flux LDAP/SSO doit rester compatible avec les politiques d'accès à la recherche.

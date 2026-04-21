# Exigences techniques — OpenEdition Search

**Statut**: référence canonique  
**Créé**: 2026-04-16  
**Portée**: frontend, backend, API, tests, qualité, sécurité, documentation

Ce document définit les exigences techniques transverses du projet. Les specs fonctionnelles décrivent ce qu'une feature doit faire ; ce document décrit les contraintes techniques que toute feature doit respecter.

Les specs `008`, `009` et `010` appliquent ces règles à la dette existante :

- [`008-code-quality-solid`](008-code-quality-solid/spec.md) : Clean Code, SOLID, interfaces, responsabilités.
- [`009-dry-kiss-yagni`](009-dry-kiss-yagni/spec.md) : duplication, simplicité, suppression du bruit.
- [`010-naming-intention-result`](010-naming-intention-result/spec.md) : nommage lisible par un humain et par une IA.

---

## 1. Stack officielle

| Couche | Exigence |
|---|---|
| Frontend | Next.js App Router, React, TypeScript, Tailwind CSS |
| Routing/i18n | `next-intl` avec routes localisées (`/[locale]`) |
| Recherche avancée | `react-querybuilder` pour le QueryBuilder |
| Backend | FastAPI, Pydantic v2, SQLAlchemy |
| Auth | JWT HS256, bcrypt (local), LDAP3 (institutionnel), OIDC/OAuth2 (SSO fédéré) |
| Données | PostgreSQL pour users/recherches sauvegardées |
| Cache | Redis pour cache search/suggest/permissions |
| Search | Apache Solr distant |
| Recherche sémantique cible | PostgreSQL + `pgvector` + pipeline Python d'embeddings |
| Tests E2E | Playwright |
| Infra locale | Docker Compose et Makefile |

Toute nouvelle dépendance doit être justifiée par un besoin mesurable. Une librairie n'est ajoutée que si elle réduit clairement le risque ou la complexité.

---

## 2. Architecture cible

### Frontend

- Les appels API passent par `front/app/lib/api.ts` ou par des route handlers Next.js dédiés quand le serveur doit relayer des headers sensibles.
- Les composants de présentation ne doivent pas appeler directement `api.*`.
- La logique métier frontend vit dans des hooks, contextes ciblés ou modules `lib/`.
- `SearchContext` doit rester un assembleur de hooks après la spec `007`.
- Les données de configuration réutilisables doivent vivre dans `front/app/lib/`, pas dans les composants de page.

### Backend

- Les endpoints FastAPI doivent déléguer la logique métier aux services.
- Les services doivent rester injectables ou mockables via les dépendances existantes.
- Les modèles Pydantic doivent valider les payloads publics ; `Any` est interdit sauf adaptateur explicitement documenté.
- Les accès Solr doivent passer par les clients/services existants, pas être recodés dans les endpoints.
- Les enrichissements IA lourds (embeddings, classification) doivent passer par une pipeline asynchrone dédiée, pas par le chemin critique HTTP.
- Les erreurs publiques doivent utiliser des codes HTTP stables et compréhensibles.

---

## 3. Contrats API

- Toute réponse publique doit avoir une structure stable et typée.
- Les erreurs attendues doivent retourner un code HTTP métier (`400`, `401`, `403`, `404`, `409`, `422`) plutôt qu'une erreur serveur générique.
- Les changements de contrat doivent être reflétés dans les types frontend.
- Toute API destinée à d'autres applications de l'unité doit être explicitement versionnée et documentée via OpenAPI.
- Les SDK multi-langages doivent être générés ou régénérables à partir du contrat OpenAPI de référence.
- Les endpoints appelés par le navigateur doivent être compatibles CORS ou proxifiés côté Next.js.
- Les appels dépendant de l'IP utilisateur doivent passer par une chaîne fiable de headers (`X-Forwarded-For` côté route handler, lecture explicite côté FastAPI).

---

## 4. Qualité de code

- Chaque module doit avoir une responsabilité principale claire.
- Les abstractions sont ajoutées uniquement quand elles réduisent une duplication ou isolent une complexité réelle.
- La duplication de logique métier est interdite entre composants.
- Le code mort, les commentaires de code désactivé et les interfaces inutilisées doivent être supprimés.
- Les constantes partagées doivent être définies une seule fois dans un module `lib/` ou équivalent.
- Les styles globaux doivent vivre dans `globals.css`, pas dans un composant.
- Les composants UI doivent rester réutilisables : données via props ou contexte ciblé, pas dépendance implicite à un contexte large.

Références opérationnelles :

- [`008-code-quality-solid/spec.md`](008-code-quality-solid/spec.md)
- [`009-dry-kiss-yagni/spec.md`](009-dry-kiss-yagni/spec.md)

### Checklist de revue de code (source canonique)

À appliquer pour chaque PR touchant `front/app/` :

- [ ] Le composant/hook modifié a une responsabilité unique (peut être décrite en une phrase)
- [ ] Aucun appel `api.*` dans un composant de présentation
- [ ] Aucun `any` introduit sans commentaire justificatif
- [ ] Les nouvelles interfaces sont segmentées (pas de props inutilisées)
- [ ] Les styles sont dans `globals.css` ou des classes Tailwind — pas de `<style>` inline dans les composants
- [ ] Aucune constante définie dans plus d'un fichier
- [ ] Aucune logique métier dupliquée entre composants (extraire dans un hook ou `lib/`)
- [ ] Aucune couleur hex hardcodée — utiliser les tokens Tailwind du thème
- [ ] Aucun code commenté laissé en place
- [ ] Aucune interface TypeScript définie mais non utilisée
- [ ] Aucun composant UI qui importe directement un contexte dont il n'a pas besoin
- [ ] Aucune feature implémentée sans use-case concret documenté dans une spec
- [ ] Les tests existants passent

---

## 5. Nommage et lisibilité

Le nommage suit le principe **Intention -> Résultat** :

- Une variable indique ce qu'elle représente dans le domaine métier.
- Une fonction commence par un verbe d'action précis.
- Un callback `.map`, `.filter`, `.some`, `.reduce` utilise un nom de paramètre métier, pas une lettre seule.
- Les constantes de module utilisent `SCREAMING_SNAKE_CASE` avec un domaine explicite.
- Les noms génériques comme `data`, `res`, `result`, `response` doivent être qualifiés (`searchResult`, `searchHttpResponse`, etc.).

Exceptions autorisées :

- `t` pour `useTranslations()` de `next-intl`.
- `i` pour un index de boucle très local.
- `e` pour un event très local.

Référence opérationnelle : [`010-naming-intention-result/spec.md`](010-naming-intention-result/spec.md).

---

## 6. Frontend UX et accessibilité

- L'interface doit rester responsive sur mobile et desktop.
- Les états de chargement doivent être non bloquants quand la donnée est secondaire, par exemple les permissions.
- Les interactions critiques doivent être testables via Playwright.
- Les labels visibles doivent passer par `next-intl`.
- Les couleurs doivent passer par les tokens du thème/Tailwind, pas par des hexadécimaux dispersés.
- Le dark mode ne doit pas être cassé par des styles hardcodés.
- Les changements d'état ne doivent pas provoquer de layout shift important sur les composants principaux.

---

## 7. Sécurité et auth

- Les tokens JWT doivent respecter la durée configurée par environnement.
- Les routes protégées doivent vérifier le token côté backend.
- Le frontend ne doit pas exposer de secret serveur.
- Les tokens JWT longue durée ne doivent pas transiter en query string. Le callback SSO utilise un code court hex32 à usage unique (Redis TTL 60s), échangé par `GET /auth/sso/exchange`.
- Les erreurs d'auth doivent être traduites côté UI avec des codes stables.
- Les routes proxy Next.js ne doivent relayer que les headers nécessaires.
- Les endpoints sensibles doivent conserver les limites de taux existantes ou en définir une nouvelle si nécessaire.

---

## 8. i18n

- Les langues supportées sont `fr`, `en`, `es`, `de`, `it`, `pt`.
- Toute nouvelle chaîne visible doit être ajoutée dans les 6 fichiers de messages.
- Les erreurs utilisateur doivent être traduites.
- Le changement de locale doit conserver l'état utilisateur quand la feature le requiert (implémenté dans `004-url-sync`).

---

## 9. Tests et vérification

### Exigences minimales

- Une feature frontend visible doit avoir au moins un test Playwright si elle touche un flux utilisateur critique.
- Une modification backend métier doit avoir un test backend ou une justification si elle est couverte autrement.
- Les refactors doivent préserver les tests existants.
- Les specs doivent indiquer les tests attendus quand une feature est en backlog.

### Commandes de référence

Frontend :

```bash
cd front
pnpm run lint       # ESLint via eslint-config-next (id-length, react-hooks, typescript)
pnpm run test:e2e   # Playwright
```

Backend :

```bash
make test           # Référence — pytest via Docker Compose (pipx run pytest échoue sans virtualenv dédié)
cd search_api_solr
ruff check .        # Linter (pycodestyle, pyflakes, bugbear, bandit, annotations)
ruff check . --fix  # Auto-correction des violations simples
```

Projet :

```bash
make test
make test-front
```

Si une commande ne peut pas être lancée, la raison doit être documentée dans le compte-rendu de changement.

---

## 10. Documentation et specs

- Une spec doit décrire le besoin, les exigences, les critères de succès et les tests attendus.
- Un `plan.md` est requis quand la spec implique plusieurs phases techniques ou des dépendances.
- Un `tasks.md` est requis quand l'implémentation doit être suivie étape par étape.
- Le planning global vit dans [`PLANNING.md`](PLANNING.md).
- La dette résiduelle validée par audit doit être suivie dans [`PLANNING.md`](PLANNING.md), même quand une spec est livrée fonctionnellement.
- `docs/ARCHITECTURE.md` décrit l'état architectural, mais ce fichier reste la source de vérité pour les exigences techniques transverses.
- Les specs touchant l'API mutualisée doivent documenter le contrat public, la stratégie de versionnement et l'impact SDK.

---

## 11. Recherche sémantique et enrichissements documentaires

- La recherche sémantique doit être pensée comme un mode complémentaire à la recherche lexicale existante, pas comme un remplacement implicite.
- Le stockage vectoriel cible doit privilégier l'outillage déjà présent dans le projet ; `pgvector` sur PostgreSQL est la cible par défaut sauf contrainte démontrée.
- Les modèles d'embedding doivent être multilingues, auto-hébergeables et compatibles avec les corpus académiques du projet.
- La catégorisation disciplinaire doit d'abord réutiliser les métadonnées source disponibles avant de recourir à une inférence automatique.
- Toute discipline calculée automatiquement doit exposer une provenance et, si pertinent, un score de confiance.
- Les enrichissements documentaires doivent être recalculables et versionnables indépendamment du frontend.

---

## 12. Définition de terminé technique

Une modification est techniquement terminée quand :

- le comportement demandé est livré ;
- les contrats API/types sont cohérents ;
- les textes visibles sont traduits ;
- les tests pertinents passent ou l'impossibilité est documentée ;
- la spec concernée et le planning sont à jour si l'état change ;
- aucune dette sans rapport n'a été introduite ;
- le code respecte les règles de qualité, simplicité et nommage ci-dessus.

---

## 13. Ordre de résolution des conflits

Quand deux documents semblent se contredire :

1. Le code actuel et les tests déterminent l'état réel.
2. Ce document détermine les exigences techniques transverses.
3. La spec active détermine les exigences fonctionnelles locales.
4. `PLANNING.md` détermine l'ordre de traitement.
5. `docs/ARCHITECTURE.md` sert de contexte et doit être synchronisé si obsolète.

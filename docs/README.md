# Documentation technique — OpenEdition Search

**Dernière vérification** : 2026-09-03 — point d'entrée du dossier `docs/`, mis à jour à chaque ajout/suppression de fichier (feature `specs/015-docs-ai-obsidian-sync`).

Point d'entrée pour naviguer la documentation technique et opérationnelle du projet, que ce soit dans un vault Obsidian ou pour un agent IA. Voir aussi [`../README.md`](../README.md) (vue d'ensemble du dépôt) et [`../specs/README.md`](../specs/README.md) (specs fonctionnelles Spec Kit).

## Référence vivante

Documents tenus à jour, décrivant l'état actuel du code.

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — vue d'ensemble de l'architecture technique (stack, flux de données, dette technique).
- [`API_V1.md`](./API_V1.md) — endpoints publics `/api/v1` et exemples d'appel.
- [`LOGGING.md`](./LOGGING.md) — stratégie de logs backend/frontend.
- [`ENVIRONMENTS.md`](./ENVIRONMENTS.md) — gestion des fichiers `.env.*`, ports, variables d'environnement.
- [`CORS_CONFIGURATION.md`](./CORS_CONFIGURATION.md) — configuration CORS par environnement.
- [`INSTALL_PROD_NO_DOCKER.md`](./INSTALL_PROD_NO_DOCKER.md) — installation en production sans Docker.
- [`REDIS_INTEGRATION.md`](./REDIS_INTEGRATION.md) — cache Redis, endpoints de monitoring, TTL.

## Historique / archive

Documents conservés pour la traçabilité, ne reflétant plus nécessairement l'état actuel.

- [`RECOMMENDATIONS.md`](./RECOMMENDATIONS.md) — analyse et recommandations antérieures à la migration Next.js 16 / React 19.
- [`SETUP_COMPLETE.md`](./SETUP_COMPLETE.md) — récapitulatif d'une configuration Docker/frontend antérieure (ports et stack obsolètes).

## Log continu

- [`CHANGELOG.md`](./CHANGELOG.md) — historique technique/opérationnel par commit (distinct de [`../specs/CHANGELOG.md`](../specs/CHANGELOG.md), qui trace les livraisons de specs).

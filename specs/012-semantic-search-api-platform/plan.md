# Plan 012 — Recherche sémantique, catégorisation disciplinaire et API mutualisable

## Intent

Faire évoluer l'application actuelle en plateforme de recherche hybride réutilisable sans remettre en cause les fondations déjà stables :

- `front/app/lib/api.ts` centralise déjà la consommation HTTP côté frontend ;
- `search_api_solr/app/main.py` expose déjà des endpoints FastAPI compatibles OpenAPI ;
- `search_api_solr/app/models/search_models.py` fournit une base typée à étendre ;
- Solr reste le moteur lexical, PostgreSQL et Redis sont déjà présents dans la stack.

## Target Architecture

```
Applications web et tierces
├── Frontend Next.js existant
├── SDK Node.js
├── SDK Python
└── SDK PHP
          │
          ▼
FastAPI Search Platform
├── API versionnée /api/v1
├── Recherche lexicale via Solr
├── Recherche vectorielle via PostgreSQL + pgvector
├── Fusion hybride des scores
└── Contrat OpenAPI + génération SDK
          │
          ├── Solr distant (index lexical)
          ├── PostgreSQL (users, saved searches, enrichissements, vecteurs)
          └── Redis (cache, états temporaires)

Pipeline d'enrichissement asynchrone
├── extraction texte/métadonnées
├── mapping discipline depuis source
├── classification complémentaire
└── calcul d'embeddings multilingues
```

## Phases

### Phase 0 - Cadrage métier et technique

1. Recenser les métadonnées disciplinaires déjà disponibles dans les documents Solr.
2. Définir une taxonomie cible réaliste, courte et gouvernable.
3. Constituer un jeu d'évaluation métier pour comparer lexical vs hybride.
4. Décider officiellement du mode de versionnement API et du périmètre public des endpoints.

### Phase 1 - Stabilisation de l'API comme produit

> **Point de départ** : `app/api/v1/saved_searches.py` existe déjà sous `/api/v1/`. En revanche, `/search`, `/suggest` et `/facets/config` sont encore définis à la racine dans `main.py`. La Phase 1 doit consolider ce namespace partiel avant tout usage externe.

1. Déplacer `/search`, `/suggest`, `/facets/config` sous `app/api/v1/` avec compatibilité ascendante (alias ou redirection depuis les routes racine le temps de la transition frontend).
2. Compléter les `response_model` publics pour les endpoints encore implicites.
3. Publier un `openapi.json` versionné et documenté.
4. Décrire les erreurs, quotas et modes d'auth des endpoints destinés aux applications tierces.
5. Préparer des exemples d'intégration hors frontend Next.js.

### Phase 2 - Socle disciplinaire

1. Ajouter les champs `disciplines`, `discipline_source`, `discipline_confidence` aux modèles backend.
2. Étendre la normalisation des résultats pour propager ces champs jusqu'au frontend.
3. Ajouter une facette discipline à la config backend et à l'UI.
4. Prioriser les valeurs déjà présentes dans les sources avant toute inférence.
5. Prévoir un mécanisme d'override manuel, même s'il est opéré d'abord hors UI.

### Phase 3 - Pipeline d'enrichissement IA

1. Créer une table d'enrichissement documentaire dans PostgreSQL.
2. Activer `pgvector` dans l'environnement cible.
3. Implémenter un job Python d'embeddings sur batch documentaire.
4. Implémenter un classifieur disciplinaire initial guidé par taxonomie.
5. Stocker provenance, horodatage de calcul et score de confiance.

### Phase 4 - Recherche hybride

1. Ajouter un `SearchMode` dans les modèles de requête.
2. Interroger Solr pour la partie lexicale et `pgvector` pour la proximité sémantique.
3. Fusionner les résultats avec une pondération simple et explicable.
4. Exposer les scores utiles au debug et les masquer si besoin côté UI publique.
5. Déployer derrière feature flag par environnement.

### Phase 5 - SDKs officiels

1. Générer un client Node.js/TypeScript à partir d'OpenAPI.
2. Générer un client Python.
3. Générer un client PHP.
4. Ajouter packaging, versioning, exemples et guide d'usage minimal pour chaque SDK.
5. Mettre en place une vérification CI garantissant que les SDKs restent synchronisés avec l'OpenAPI.

## Deliverables

| Lot | Sortie attendue |
|---|---|
| API platform | endpoints versionnés + OpenAPI stabilisé |
| Métadonnées | disciplines exposées dans les réponses |
| IA | pipeline embeddings + classification |
| Recherche | mode `semantic` et `hybrid` exploitable |
| Intégration | SDKs `node`, `python`, `php` + exemples |

## Code Impact Map

| Zone actuelle | Impact attendu |
|---|---|
| `search_api_solr/app/main.py` | versionnement API, nouveaux endpoints ou alias, nouveaux paramètres |
| `search_api_solr/app/models/search_models.py` | ajout de `SearchMode`, enrichissement des réponses, schémas SDK |
| `search_api_solr/app/models/document.py` | ajout des champs discipline et scores associés |
| `search_api_solr/app/services/search_service.py` | fusion lexical + sémantique |
| `search_api_solr/app/services/solr_client.py` | inchangé en socle, éventuels ajustements de récupération de métadonnées |
| `front/app/lib/api.ts` | support du mode de recherche et de la nouvelle API versionnée |
| `front/app/types.ts` | nouvelles propriétés documentaires |
| `front/app/components/Facets.tsx` et `ResultItem.tsx` | affichage et filtrage par discipline |

## Recommended Order

1. Stabiliser l'API publique et le contrat OpenAPI.
2. Ajouter la discipline dans le modèle documentaire sans activer encore la sémantique.
3. Mettre en place la pipeline d'enrichissement et `pgvector`.
4. Activer le mode hybride derrière feature flag.
5. Générer et publier les SDKs.

## Decisions Already Recommended

- Garder Solr pour le lexical.
- Utiliser PostgreSQL + `pgvector` pour le vectoriel.
- Utiliser Python pour l'enrichissement et la classification.
- Générer les SDKs depuis OpenAPI au lieu d'écrire trois clients divergents.
- Démarrer avec une taxonomie disciplinaire restreinte et validée métier.

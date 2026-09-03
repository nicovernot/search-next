# Research — Configuration Solr multi-core

## Audit du code actuel (Phase 0)

Avant de choisir une méthode, le chemin réel de résolution du core Solr a été tracé dans `search_api_solr/` :

| Point de construction | Fichier:ligne | Source de l'URL |
|---|---|---|
| Client Solr principal | `app/api/dependencies.py::get_solr_client` | `SOLR_CONFIG["base_url"]` (= `settings.solr_base_url`) |
| Builder de requêtes | `app/api/dependencies.py::get_search_builder` | idem, injecté au constructeur (`SearchBuilder(solr_base_url=...)`) |
| Vérification des permissions | `app/services/search_service.py:233-248` (`PermissionsService.get_document_permissions`) | **Contournement complet de la DI** : réimporte `SOLR_CONFIG` et instancie un **second type de client Solr** (`app/services/docs_permissions_client.py::SolrClient`, distinct de `app/services/solr_client.py::SolrClient`), sans passer par `self.solr_client` pourtant injecté au constructeur |

Deux constats structurants :
- `SolrClient.search()` (`app/services/solr_client.py:34`) traite son paramètre `query` comme une **URL déjà complète** (elle appelle `client.get(query, ...)` directement) — l'URL est entièrement construite en amont par `SearchBuilder.build_search_url()`. L'attribut `self.base_url` de `SolrClient` n'est donc pas consommé dans `search()` : le vrai point de résolution du core est **`SearchBuilder`**, pas `SolrClient`.
- `PermissionsService` reçoit un `ISolrClient` injecté par DI (`app/api/dependencies.py::get_permissions_service`) mais ne l'utilise jamais pour la vérification réelle — elle construit son propre client ad hoc à partir de `SOLR_CONFIG` directement. C'est le point de divergence le plus concret qui justifie FR-006 : sans correction, une future config multi-core y serait invisible.
- Une configuration parallèle non branchée existe déjà (`app/core/config.py::SOLR_CORE_NAME`, `app/core/env_validation.py::solr_collection` exporté en `VALIDATED_SOLR_COLLECTION` mais jamais relu) — confirmé mort par recherche exhaustive (aucun import).
- `GET /facets/config` (`app/api/v1/facets.py`) ne construit aucune requête Solr : il retourne un JSON statique (`FACET_CONFIG`). Les définitions de facettes sont donc **indépendantes du core** interrogé (cohérent avec l'Assumption de la spec : les cores partagent une structure de documents compatible) — cet endpoint n'a pas besoin de connaître le core cible.

## Décision 1 — Mécanisme de configuration des cores

- **Decision**: Un core Solr = un fichier JSON dans un nouveau dossier `app/services/solr_cores/`, nommé `<nom_du_core>.json`, contenant `{"base_url": "...", "default": true|false}` (`default` optionnel, absent = `false`). Exactement un fichier doit porter `"default": true`.
- **Rationale**: C'est l'extension directe d'un patron déjà en place et éprouvé dans ce même service — `app/services/facet_config.py::load_facet_config_from_json()` charge déjà `facets_json/*.json` de la même façon (un fichier = une entrée nommée par son nom de fichier, agrégés dans un dict au chargement). Réutiliser ce patron respecte le principe V de la constitution (simplicité, pas de nouvelle abstraction) et donne trois propriétés utiles gratuitement : (1) ajouter un core = ajouter un fichier, sans toucher au code (FR-001/FR-002/SC-001) ; (2) deux cores ne peuvent pas porter le même nom par construction du système de fichiers (FR-007, doublons impossibles) ; (3) chaque ajout/retrait de core est un diff Git isolé et revuable.
- **Alternatives considered**:
  - *Variable d'environnement unique* (JSON ou CSV dans `SOLR_CORES`, sur le modèle de `CORS_ORIGINS`) — rejeté : fonctionne pour une liste de valeurs simples (déjà utilisé pour des listes), mais ici chaque core porte plusieurs attributs (nom, URL, indicateur par défaut) ; les caser dans une seule variable d'environnement force soit un format JSON imbriqué peu lisible dans un `.env`, soit une syntaxe ad hoc à inventer — moins lisible et moins revuable qu'un fichier par core, et incohérent avec le patron JSON déjà utilisé pour `facets_json/`/`fields_json/`.
  - *Un seul fichier `solr_cores.json` avec une liste imbriquée* — rejeté : la détection de doublon de nom devient une validation applicative à écrire, alors qu'elle est gratuite avec un fichier par core (le système de fichiers l'empêche déjà).
  - *Table PostgreSQL* — rejeté : sur-dimensionné pour une configuration de déploiement qui change rarement, ajoute une dépendance base de données à un chemin qui n'en a pas besoin aujourd'hui (le reste de la config Solr est déjà fichier/variable d'environnement), et casse la garantie « aucune modification de code, juste de la config » (une migration de schéma serait nécessaire pour le tout premier déploiement).

## Décision 2 — Résolution du core par requête

- **Decision**: `SearchBuilder` (aujourd'hui construit avec un seul `solr_base_url` figé) est reconstruit pour recevoir le registre complet des cores (nom → `base_url`) et résout le core à l'intérieur de `build_search_url(request)`, à partir d'un nouveau champ optionnel `SearchRequest.core`. Idem pour `SuggestService`/`PermissionsService`, qui reçoivent un paramètre `core: str | None` optionnel (déjà véhiculé côté endpoint via un paramètre de requête `core` pour `/suggest` et `/permissions`, puisque ces endpoints n'ont pas de corps JSON).
- **Rationale**: `SearchBuilder` est aujourd'hui instancié une fois par requête HTTP via `Depends()`, **avant** que FastAPI n'ait fini de parser le corps `SearchRequest` — le core cible n'est donc pas connu au moment de la construction. Le registre (immuable, résolu une fois au démarrage) peut en revanche être injecté sans ce problème ; seule la résolution finale doit attendre le contenu de la requête.
- **Alternatives considered**: Construire un `SearchBuilder` différent par core à l'avance et sélectionner l'instance au niveau de l'endpoint — rejeté : duplique la construction pour chaque core à chaque requête HTTP alors qu'un seul registre immuable partagé suffit ; complique inutilement la DI FastAPI existante.

## Décision 3 — Erreur « core inconnu » distincte de « core injoignable »

- **Decision**: Nouvelle exception `SolrCoreNotFoundError` (→ HTTP 404), ajoutée à `app/core/exceptions.py` aux côtés de `SolrTimeoutError`/`SolrInvalidQueryError`/`SolrUnavailableError` déjà là, et mappée dans la même chaîne `isinstance` que ces dernières dans chaque endpoint concerné (`search.py`, `suggest.py`, `permissions.py`).
- **Rationale**: `SolrUnavailableError` (→ HTTP 503) existe déjà et couvre exactement le cas « core configuré mais Solr distant injoignable » (FR-010, second cas) — inutile de la dupliquer. Le cas « nom de core absent de la configuration » (FR-004, FR-010 premier cas) est un problème de requête client, pas un problème de disponibilité de service : 404 est sémantiquement correct (ressource — le core nommé — introuvable) et distinct de 503, ce qui satisfait directement FR-010 sans introduire un nouveau mécanisme d'erreur.
- **Alternatives considered**: Réutiliser `SolrInvalidQueryError` (→ HTTP 400) pour un core inconnu — rejeté : sémantiquement, la requête Solr elle-même n'est pas invalide, c'est le nom du core demandé qui n'existe pas ; 404 est plus précis et plus facilement diagnostiqué côté appelant.

## Décision 3bis — SolrCoreNotFoundError et les patrons de gestion d'erreur existants

- **Decision**: `search.py` propage déjà les exceptions Solr typées vers `_raise_public_search_error` — `SolrCoreNotFoundError` s'y ajoute sans changement de patron. `SuggestService.fetch_autocomplete_suggestions()` et `PermissionsService.get_document_permissions()` interceptent aujourd'hui **toute** exception (`except Exception`) et dégradent silencieusement (liste vide / `info.error` en HTTP 200) — un comportement délibéré et préexistant pour les pannes Solr génériques. `SolrCoreNotFoundError` DOIT être intercepté et re-levé (ou converti en erreur explicite) **avant** ce bloc `except Exception` générique, dans les deux services, sans modifier la dégradation gracieuse existante pour les autres erreurs (ex. `SolrUnavailableError`).
- **Rationale**: Sans ce contournement ciblé, un nom de core invalide sur `/suggest` ou `/permissions` serait absorbé par le catch-all existant et retournerait un succès trompeur (liste vide / erreur noyée dans un 200) — exactement le repli silencieux que FR-004 interdit. Le catch-all existant reste néanmoins la bonne réponse UX pour une panne Solr générique (ce n'est pas une régression à corriger, juste un cas à ne pas y mélanger).
- **Alternatives considered**: Uniformiser les trois endpoints sur le patron strict de `/search` (toujours lever une `HTTPException`) — rejeté : changerait le contrat existant de `/suggest`/`/permissions` pour toutes les autres erreurs, bien au-delà du périmètre de cette feature (FR-009/principe V — ne pas étendre le changement au-delà du nécessaire).

## Décision 4 — Endpoints concernés

- **Decision**: `POST/GET /api/v1/search` gagne un champ optionnel `core` (dans `SearchRequest` pour POST, en paramètre de requête pour l'alias GET). `GET /api/v1/suggest` et `GET /api/v1/permissions` gagnent un paramètre de requête optionnel `core`. `GET /api/v1/facets/config` n'est **pas modifié** (aucune requête Solr, config déjà indépendante du core — voir audit ci-dessus).
- **Rationale**: Couvre exactement les points identifiés dans l'audit comme construisant une connexion Solr (FR-006), sans étendre le périmètre à un endpoint qui n'en a structurellement pas besoin (principe V, éviter la complexité non justifiée).
- **Alternatives considered**: Exposer le core comme un en-tête HTTP transverse (`X-Solr-Core`) plutôt qu'un paramètre par endpoint — rejeté : moins découvrable dans l'OpenAPI généré (`/api/v1/openapi.json`, déjà consommé par les futurs SDKs de la spec 012) qu'un champ/paramètre documenté explicitement par endpoint.

## Décision 5 — Compatibilité ascendante au démarrage

- **Decision**: La migration crée un fichier `app/services/solr_cores/documents.json` avec `{"base_url": "<valeur actuelle de settings.solr_base_url>", "default": true}` au moment de l'implémentation, pour que le comportement par défaut (US3) soit strictement identique à l'existant dès le premier déploiement.
- **Rationale**: Répond directement à FR-005/SC-002 — aucun appelant existant ne doit percevoir de changement.
- **Alternatives considered**: Garder `settings.solr_base_url` comme filet de sécurité si `solr_cores/` est vide — rejeté : contredit FR-007 (une configuration vide doit échouer clairement au démarrage, pas retomber silencieusement sur une valeur historique) et créerait deux sources de vérité concurrentes.

# Feature Specification: Catalogue des cores Solr et intégration du core « calenda »

**Feature Branch**: `017-solr-core-catalog`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Améliorer le système multi-core Solr (spec 016) pour le rendre découvrable et documenté côté API : 1. Ajouter un endpoint de listing des cores disponibles (ex: GET /api/v1/cores) qui retourne les noms des cores configurés et lequel est le core par défaut, en s'appuyant sur le SolrCoreRegistry existant. 2. Documenter un exemple pas-à-pas de comment intégrer/ajouter un nouveau core Solr au système. 3. Ajouter concrètement un nouveau core nommé "calenda" (calendrier) au registre, en plus du core existant "documents", sans changer le core par défaut."

## Contexte

La feature 016 a introduit un registre de cores Solr configurables et un paramètre `core` sur les endpoints de recherche, suggestions et permissions. Ce paramètre est un champ texte libre : rien dans l'API ne permet à un appelant de découvrir la liste des cores réellement configurés, ni de savoir lequel est utilisé par défaut si le paramètre est omis. Un seul core (`documents`) est configuré à ce jour, ce qui masque encore davantage l'existence du mécanisme.

Cette feature ajoute un moyen de lister les cores disponibles, documente la procédure d'ajout d'un nouveau core pour les opérateurs de la plateforme, et applique cette procédure pour enregistrer un second core nommé `calenda`, destiné à une collection de documents de type calendrier/agenda, distincte de la collection `documents` existante.

## Clarifications

### Session 2026-09-03

- Q: Le core `calenda` doit être enregistré dans le registre avec une adresse Solr réelle (`base_url`). Quelle est l'adresse Solr du core calendrier à interroger ? → A: Même serveur que le core `documents`, chemin de collection différent — `https://solrslave-sec.labocleo.org/solr/calenda`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lister les cores disponibles (Priority: P1)

En tant qu'appelant de l'API (client front-end ou intégrateur tiers), je veux pouvoir demander la liste des cores Solr configurés et savoir lequel est utilisé par défaut, afin de choisir une valeur valide pour le paramètre `core` sans avoir à consulter la configuration serveur ou la documentation à chaque changement.

**Why this priority**: C'est le point bloquant identifié — sans ce moyen de découverte, le paramètre `core` existant reste invisible et inutilisable en pratique dès qu'il y a plus d'un core.

**Independent Test**: Appeler le nouvel endpoint de listage sans aucun autre changement et vérifier qu'il renvoie la liste actuelle des cores configurés et le nom du core par défaut, cohérente avec le contenu du registre.

**Acceptance Scenarios**:

1. **Given** un registre contenant un ou plusieurs cores configurés, **When** un appelant interroge l'endpoint de listage des cores, **Then** la réponse contient le nom de chaque core configuré et indique lequel est le core par défaut.
2. **Given** un registre où un opérateur vient d'ajouter un nouveau core, **When** un appelant interroge à nouveau l'endpoint de listage sans redéploiement de code applicatif, **Then** le nouveau core apparaît dans la réponse.
3. **Given** la réponse de l'endpoint de listage, **When** un appelant utilise l'un des noms renvoyés comme valeur du paramètre `core` sur `/search`, `/suggest` ou `/permissions`, **Then** la requête est acceptée et ciblée sur ce core.

---

### User Story 2 - Documenter l'ajout d'un core Solr (Priority: P2)

En tant qu'opérateur/mainteneur de la plateforme, je veux disposer d'un exemple documenté pas-à-pas pour intégrer un nouveau core Solr, afin de pouvoir reproduire l'opération de façon autonome et sans erreur, sans devoir relire le code source du registre.

**Why this priority**: Complète la découvrabilité côté API par une découvrabilité côté procédure opérateur ; dépend de la terminologie stabilisée par l'endpoint de la Story 1 mais reste utile indépendamment.

**Independent Test**: Suivre uniquement les instructions documentées (sans autre source) pour ajouter un core de test au registre, et vérifier qu'il devient interrogeable et visible dans le listage.

**Acceptance Scenarios**:

1. **Given** la documentation d'intégration, **When** un opérateur suit les étapes décrites pour ajouter un core, **Then** le core devient interrogeable via l'API sans modification du code applicatif.
2. **Given** la documentation d'intégration, **When** un opérateur consulte les informations requises pour déclarer un core, **Then** il trouve la liste exhaustive des informations à fournir (nom du core, adresse Solr, statut par défaut ou non) et un exemple concret.

---

### User Story 3 - Enregistrer le core « calenda » (Priority: P3)

En tant qu'opérateur de la plateforme, je veux que le core `calenda` soit enregistré dans le registre de cores au même titre que `documents`, afin que la collection calendrier devienne interrogeable via l'API sans devenir le core utilisé par défaut.

**Why this priority**: Application concrète des Stories 1 et 2 sur un cas réel ; dépend de la disponibilité de l'adresse Solr réelle du core calendrier (voir Clarifications).

**Independent Test**: Après enregistrement, appeler l'endpoint de listage et vérifier la présence de `calenda` avec `default = false`, puis effectuer une recherche avec `core=calenda` et vérifier qu'elle cible la bonne collection plutôt que `documents`.

**Acceptance Scenarios**:

1. **Given** le registre existant avec `documents` comme core par défaut, **When** le core `calenda` est ajouté à la configuration, **Then** les deux cores apparaissent dans le listage, et `documents` reste le core par défaut.
2. **Given** le core `calenda` enregistré, **When** un appelant effectue une recherche avec `core=calenda`, **Then** la requête est envoyée à la collection calendrier et non à la collection documents.
3. **Given** le core `calenda` enregistré, **When** un appelant effectue une recherche sans préciser `core`, **Then** la recherche continue de cibler `documents` (comportement par défaut inchangé).

### Edge Cases

- Que renvoie l'endpoint de listage si un seul core est configuré (cas actuel) ? Il doit tout de même renvoyer ce core et le signaler comme défaut, pour rester cohérent une fois un second core ajouté.
- Que se passe-t-il si le core `calenda` est déclaré dans le registre mais que son adresse Solr est injoignable au moment d'une recherche ? Le comportement d'erreur doit rester celui déjà défini par la feature 016 pour un core dont le service Solr sous-jacent est indisponible (erreur explicite, pas de repli silencieux sur un autre core).
- Que se passe-t-il si deux cores sont déclarés comme défaut, ou aucun ? Ce cas est déjà couvert par la validation existante du registre (feature 016) et n'est pas modifié par cette feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT exposer un moyen, via l'API, de lister l'ensemble des cores Solr actuellement configurés, identifiés par leur nom.
- **FR-002**: Pour chaque core listé, le système DOIT indiquer s'il s'agit du core utilisé par défaut lorsque le paramètre `core` est omis.
- **FR-003**: La liste des cores renvoyée DOIT refléter l'état courant de la configuration (tout core ajouté ou retiré de la configuration doit apparaître ou disparaître de la liste sans modification du code applicatif).
- **FR-004**: La documentation destinée aux opérateurs DOIT décrire, étape par étape, comment déclarer un nouveau core Solr dans la configuration, incluant la liste des informations requises pour chaque core (nom, adresse Solr, statut par défaut) et un exemple concret.
- **FR-005**: Le système DOIT enregistrer un core nommé `calenda`, distinct du core `documents`, interrogeable via le paramètre `core` existant sur les endpoints de recherche, suggestions et permissions.
- **FR-006**: L'ajout du core `calenda` NE DOIT PAS changer le core par défaut ; les recherches sans paramètre `core` explicite continuent de cibler `documents`.
- **FR-007**: Le système DOIT continuer d'appliquer, pour le core `calenda`, les mêmes règles d'erreur déjà en place pour un core inconnu ou indisponible (comportement hérité de la feature 016, non modifié).

### Key Entities

- **Core Solr (entrée de catalogue)**: représente une collection Solr interrogeable — attributs : nom (identifiant utilisé dans le paramètre `core`), adresse Solr, indicateur « core par défaut ». Entité déjà introduite par la feature 016 ; cette feature en expose la liste et en ajoute une instance (`calenda`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un appelant de l'API découvre la liste complète des cores disponibles et le core par défaut en un seul appel, sans consulter la configuration serveur ni la documentation.
- **SC-002**: Un opérateur suivant uniquement la documentation d'intégration parvient à ajouter un nouveau core Solr interrogeable en une seule tentative, sans lire le code source.
- **SC-003**: Le core `calenda` apparaît dans le listage et répond correctement aux recherches qui le ciblent explicitement, sans qu'aucune recherche existante ciblant implicitement le core par défaut ne change de comportement.

## Assumptions

- La feature 016 (registre de cores, paramètre `core` sur `/search`, `/suggest`, `/permissions`) est en place et n'est pas remise en cause ; cette feature s'appuie dessus sans la modifier.
- « Lister les cores disponibles » signifie exposer au minimum le nom de chaque core et lequel est le défaut ; l'exposition d'informations supplémentaires (ex. adresse Solr) n'est pas requise et reste une décision d'implémentation, l'adresse Solr étant une information d'infrastructure interne.
- Le core `calenda` référence une collection Solr distincte déjà existante côté infrastructure Solr (cette feature ne crée pas de collection Solr, conformément au périmètre déjà posé par la feature 016) ; seule son adresse reste à fournir.
- Aucune restriction d'accès par core n'est introduite (cohérent avec la clarification déjà actée en feature 016 : tous les cores configurés sont ouverts à tout appelant autorisé à utiliser l'API).

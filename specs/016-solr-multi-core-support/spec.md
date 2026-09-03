# Feature Specification: Configuration Solr multi-core

**Feature Branch**: `016-solr-multi-core-support`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "actuellements on utilise le core documents, il faut que ça soit possible d'ajouter d'autre core, il faut que la conf soie changeable. possiblité d'utiliser pluseiur core en meme temps. etudier la meilleur methode"

## Contexte

Le moteur de recherche interroge aujourd'hui un unique core Solr distant nommé `documents`, dont l'adresse est codée en dur dans une seule chaîne de configuration (`solr_base_url`). Deux points du backend construisent chacun leur propre connexion Solr à partir de cette même valeur (le point d'entrée de recherche principal, et le service de vérification des permissions), sans passer par une notion explicite de « core » ou de « collection ». Il existe par ailleurs des restes de configuration non utilisés qui suggéraient déjà une intention de séparer l'URL Solr du nom du core, sans jamais avoir été branchés au chemin réellement exécuté.

Cette feature vise à rendre le core Solr interrogé configurable, à permettre l'ajout d'autres cores sans modification de code, et à permettre qu'une recherche cible explicitement l'un des cores configurés — sur un modèle de sélection ciblée (une recherche interroge un seul core à la fois, choisi parmi ceux disponibles), plutôt qu'une fusion automatique des résultats de tous les cores actifs à chaque recherche.

Solr reste un service distant, en lecture seule pour ce projet : cette feature ne construit pas de pipeline d'indexation ni de création de core côté Solr — elle change uniquement la façon dont la plateforme se connecte aux cores existants et les interroge.

## Clarifications

### Session 2026-09-03

- Q: Quand plusieurs cores Solr sont actifs en même temps, une recherche utilisateur doit-elle interroger tous les cores actifs et fusionner les résultats en une seule liste, ou cibler un seul core à la fois (choisi par requête/contexte) parmi ceux disponibles ? → A: Sélection ciblée — chaque recherche cible un seul core à la fois ; plusieurs cores peuvent coexister dans la configuration mais ne sont pas fusionnés automatiquement.
- Q: Un appelant qui a accès à l'API de recherche doit-il pouvoir cibler n'importe quel core configuré, ou certains cores doivent-ils être restreints à certains appelants ? → A: Tous les cores configurés sont ouverts à tout appelant autorisé à utiliser l'API — pas de restriction d'accès par core ; le contrôle d'accès reste au niveau document (badges de permission existants), inchangé par cette feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ajouter un core Solr par configuration (Priority: P1)

En tant qu'opérateur/mainteneur de la plateforme, je veux ajouter un nouveau core Solr en modifiant uniquement la configuration, afin de rendre une nouvelle collection de documents interrogeable sans changement de code applicatif.

**Why this priority**: C'est la demande centrale de la feature — sans cette capacité, le reste (ciblage, visibilité) n'a pas d'objet.

**Independent Test**: Ajouter l'entrée d'un second core (nom + adresse) dans la configuration, redémarrer/recharger la configuration sans toucher au code source, et vérifier qu'une recherche ciblant ce nouveau core renvoie des résultats.

**Acceptance Scenarios**:

1. **Given** un seul core `documents` configuré, **When** un opérateur ajoute un second core dans la configuration, **Then** ce second core devient interrogeable sans qu'aucun fichier de code applicatif n'ait été modifié.
2. **Given** une configuration listant plusieurs cores, **When** un opérateur retire un core de la configuration, **Then** ce core n'est plus interrogeable et les recherches qui le ciblaient explicitement échouent avec une erreur claire plutôt que d'être silencieusement redirigées vers un autre core.

---

### User Story 2 - Cibler un core précis pour une recherche (Priority: P1)

En tant que développeur intégrant (frontend interne ou consommateur de l'API), je veux pouvoir indiquer quel core doit être interrogé pour une recherche donnée, afin d'obtenir des résultats provenant de la collection voulue.

**Why this priority**: Sans mécanisme de ciblage, ajouter un core (US1) ne sert à rien — c'est le second pilier indissociable du besoin exprimé.

**Independent Test**: Envoyer deux recherches identiques en ne faisant varier que le core ciblé, et vérifier que chacune renvoie des résultats issus du core demandé et non d'un autre.

**Acceptance Scenarios**:

1. **Given** plusieurs cores configurés, **When** une recherche précise explicitement un core existant, **Then** les résultats proviennent uniquement de ce core.
2. **Given** plusieurs cores configurés, **When** une recherche ne précise aucun core, **Then** elle cible le core par défaut désigné dans la configuration, de façon prévisible et documentée.
3. **Given** une recherche qui cible un nom de core absent de la configuration, **When** elle est exécutée, **Then** le système renvoie une erreur explicite plutôt que de basculer silencieusement sur un autre core.

---

### User Story 3 - Ne rien casser sur le comportement actuel (Priority: P2)

En tant qu'opérateur responsable du service en production, je veux que l'introduction du support multi-core ne modifie aucun comportement existant pour les appelants qui ne connaissent pas cette nouvelle capacité, afin d'éviter toute régression sur la recherche déjà en production.

**Why this priority**: Le service de recherche est déjà utilisé en production ; une régression sur le comportement par défaut aurait un impact direct sur les utilisateurs finaux.

**Independent Test**: Rejouer un jeu de recherches existantes (sans paramètre de core) avant et après l'introduction de la feature, et vérifier que les résultats et le comportement (y compris les vérifications de permissions) sont identiques.

**Acceptance Scenarios**:

1. **Given** la configuration migrée pour supporter plusieurs cores, **When** un appelant existant effectue une recherche sans préciser de core, **Then** il obtient exactement le même core et le même comportement qu'avant l'introduction de cette feature.
2. **Given** les différents points du backend qui construisent aujourd'hui chacun leur propre connexion Solr (recherche, permissions), **When** le core par défaut est résolu, **Then** tous ces points utilisent la même résolution de configuration, sans divergence possible entre eux.

---

### User Story 4 - Découvrir les cores configurés (Priority: P3)

En tant qu'opérateur ou développeur, je veux pouvoir consulter la liste des cores actuellement configurés et leur état (accessible ou non), afin de diagnostiquer la configuration sans avoir à lire le code source ou à deviner.

**Why this priority**: Utile pour l'exploitation et le diagnostic, mais non bloquant pour la valeur centrale (ajouter et cibler des cores).

**Independent Test**: Consulter la source de vérité de configuration (ou une sortie diagnostique) et vérifier qu'elle liste exactement les cores actifs, avec de quoi identifier lesquels sont actuellement joignables.

**Acceptance Scenarios**:

1. **Given** une configuration avec plusieurs cores, **When** un opérateur consulte la configuration ou un diagnostic dédié, **Then** il voit la liste complète des cores configurés, incluant celui par défaut.
2. **Given** un core configuré mais devenu injoignable sur le Solr distant, **When** une recherche le cible, **Then** l'erreur renvoyée permet de distinguer « core inconnu de la configuration » de « core configuré mais injoignable ».

---

### Edge Cases

- Une recherche cible un nom de core qui n'existe pas dans la configuration : erreur explicite, jamais de repli silencieux vers un autre core.
- La configuration ne liste aucun core (erreur de configuration) : le système doit échouer clairement au démarrage plutôt que de démarrer dans un état invalide.
- La configuration contient deux entrées avec le même nom de core : doit être détecté et rejeté plutôt que de laisser un comportement ambigu (lequel des deux est utilisé ?).
- Un core listé dans la configuration a été supprimé ou est temporairement injoignable côté Solr distant : la recherche qui le cible doit échouer avec une erreur distincte d'une erreur de configuration (cf. Edge Case précédent), pas planter silencieusement ni retourner un résultat vide sans explication.
- Les différents services backend qui construisent aujourd'hui indépendamment leur connexion Solr (recherche et vérification des permissions) doivent résoudre le core de façon cohérente entre eux ; toute divergence constituerait une régression couverte par User Story 3.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT permettre de configurer un ou plusieurs cores Solr (nom + cible de connexion) sans modification du code source applicatif.
- **FR-002**: Un opérateur DOIT pouvoir ajouter, retirer ou modifier la liste des cores configurés en ne changeant que la configuration, le changement prenant effet via le cycle de vie de configuration existant de la plateforme (pas de modification de code).
- **FR-003**: Chaque recherche DOIT cibler exactement un core configuré, soit explicitement précisé, soit par défaut sur un core désigné lorsque non précisé.
- **FR-004**: Le système DOIT rejeter avec une erreur explicite toute recherche ciblant un nom de core absent de la configuration courante, plutôt que d'utiliser silencieusement un autre core.
- **FR-005**: Le comportement de recherche existant sur le core `documents` DOIT rester inchangé pour tout appelant qui ne précise pas de core.
- **FR-006**: Tous les chemins de code backend qui établissent une connexion Solr pour un usage donné (recherche, suggestions, facettes, vérification des permissions, etc.) DOIVENT résoudre le core de façon cohérente à partir de la même source de configuration — aucune résolution dupliquée ou divergente entre services.
- **FR-007**: Le système DOIT valider la liste des cores configurés à son démarrage et échouer clairement (pas silencieusement) en cas de configuration invalide (liste vide, noms de cores dupliqués, cible de connexion manquante).
- **FR-008**: Un opérateur DOIT pouvoir déterminer, à partir de la configuration ou d'une surface de diagnostic, la liste des cores actuellement configurés ainsi que celui utilisé par défaut.
- **FR-009**: Cette feature NE DOIT PAS inclure la création de core côté Solr ni un pipeline d'indexation/import de données — elle change uniquement la manière dont la plateforme se connecte à des cores Solr existants et les interroge ; Solr reste un service distant en lecture seule pour ce projet.
- **FR-010**: Le système DOIT distinguer, dans l'erreur renvoyée, le cas « core inconnu de la configuration » du cas « core configuré mais actuellement injoignable sur le Solr distant ».
- **FR-011**: Le ciblage d'un core NE DOIT PAS introduire de restriction d'accès par core : tout appelant déjà autorisé à utiliser l'API de recherche DOIT pouvoir cibler n'importe quel core configuré ; le contrôle d'accès aux documents (badges de permission existants) reste inchangé et continue de s'appliquer au niveau document, pas au niveau core.

### Key Entities

- **Core Solr (entrée de configuration)** : un core interrogeable — nom logique, cible de connexion, indicateur « core par défaut » éventuel.
- **Recherche** : une requête de recherche, désormais associée à un core cible (explicite ou par défaut).
- **Registre des cores actifs** : l'ensemble résolu, au moment de l'exécution, des cores actuellement configurés et de leur accessibilité.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un opérateur peut ajouter un nouveau core Solr à la configuration et le rendre interrogeable en modifiant uniquement de la configuration, sans écrire ni modifier de code source.
- **SC-002**: 100 % des recherches existantes qui ne précisent pas de core continuent, après l'introduction de cette feature, à renvoyer des résultats identiques à ceux d'avant (même core, même comportement de permissions).
- **SC-003**: 100 % des recherches ciblant explicitement un core configuré renvoient des résultats exclusivement issus de ce core.
- **SC-004**: Une recherche ciblant un core absent de la configuration échoue avec un message d'erreur explicite dans 100 % des cas, sans jamais retourner de résultats d'un autre core.
- **SC-005**: Un opérateur peut déterminer la liste complète des cores configurés et celui par défaut sans lire le code source.
- **SC-006**: Une configuration invalide (liste vide, noms dupliqués) est détectée et signalée avant qu'une recherche ne puisse être exécutée dans cet état.

## Assumptions

- Solr demeure un service distant et en lecture seule pour ce projet ; « ajouter un core » signifie configurer la plateforme pour interroger un core Solr déjà existant et peuplé côté serveur distant, pas créer ou indexer ce core.
- Le ciblage du core d'une recherche se fait au niveau de la requête de recherche (paramètre explicite optionnel), avec repli sur un core par défaut désigné dans la configuration lorsque non précisé — cohérent avec la décision de « sélection ciblée » actée en Clarifications.
- La méthode technique exacte de configuration (format, mécanisme de rechargement) est volontairement laissée ouverte à la phase de planification, qui doit étudier et documenter la méthode la plus adaptée à l'architecture existante (« étudier la meilleure méthode », demande explicite de l'utilisateur).
- Le périmètre de cette feature est le backend de recherche (`search_api_solr`) et sa configuration ; l'exposition éventuelle du choix de core dans l'interface frontend n'est pas requise par cette feature et pourra faire l'objet d'un travail de suivi si nécessaire.
- Les cores ajoutés sont supposés partager une structure de documents compatible avec celle déjà exploitée par la plateforme ; l'adaptation à une structure de documents fondamentalement différente est hors périmètre.
- Le ciblage de core n'introduit pas de nouveau périmètre d'autorisation : aucun contrôle d'accès par core n'est requis par cette feature (voir Clarifications, session 2026-09-03) ; un futur besoin de restreindre certains cores à certains appelants ferait l'objet d'une feature distincte.

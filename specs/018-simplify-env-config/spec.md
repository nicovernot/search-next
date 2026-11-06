# Feature Specification: Simplification de la configuration d'environnement

**Feature Branch**: `018-simplify-env-config`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "simplifier les environments , il faut jjuste trois envorinements dev et prod et test on doit utiliser un seul .env ( me dire si c'est une bonne idéé ) avec la varieble avec trois valeurs env , prod , test. verifier le bon fonctionnement . documenter le dout . il faut aue ça soit facile pour le developpeur . verifier dans docker que ça bient pris en compte partout . la conf de cors doit etre sur le point enve ainsi que toutes les varables necessares."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.

  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Un développeur configure son environnement en un seul endroit (Priority: P1)

Un développeur qui clone le projet ou change de contexte de travail (dev, test, prod) doit pouvoir configurer et comprendre toute la configuration applicative (URLs de service, CORS, Solr, Redis, base de données, authentification) à partir d'un unique point d'entrée, sans avoir à chercher dans plusieurs fichiers `.env.*` dispersés ni à deviner quel fichier généré prévaut sur quel autre.

**Why this priority**: C'est le problème central signalé — la configuration actuelle est répartie sur au moins 6 fichiers (`.env.shared`, `.env.development`, `.env.test`, `.env.staging`, `.env.production`, `.env.example`) plus un fichier racine non versionné et des fichiers générés par service (`front/.env.local`, `search_api_solr/.env.local`), ce qui a déjà provoqué des pannes difficiles à diagnostiquer (valeur obsolète prise en compte, variable de shell qui prime silencieusement sur le fichier). Sans corriger ce point, aucune autre amélioration n'a de valeur.

**Independent Test**: Un développeur peut, en ne modifiant qu'un seul fichier et en changeant la valeur d'une seule variable, faire basculer l'application entre le mode dev, test et prod, et retrouver un comportement correct et prévisible à chaque bascule.

**Acceptance Scenarios**:

1. **Given** un poste de développement fraîchement cloné, **When** le développeur suit la documentation pour démarrer en local, **Then** il ne configure qu'un seul fichier de variables d'environnement pour obtenir un environnement de développement fonctionnel.
2. **Given** le fichier de configuration unique renseigné pour un environnement donné, **When** le développeur change la valeur de la variable d'environnement sélectrice (dev / test / prod), **Then** l'ensemble des services (API, front, tâches Docker) utilisent la configuration correspondant à la valeur choisie, sans qu'il soit nécessaire d'éditer un autre fichier.
3. **Given** un ancien fichier généré ou un ancien override désormais obsolète, **When** le nouveau système de configuration est utilisé, **Then** il n'existe plus de source de configuration concurrente cachée capable de silencieusement prendre le pas sur le fichier unique documenté.

---

### User Story 2 - Un développeur retrouve toutes les variables et leur rôle dans une documentation unique (Priority: P2)

Un développeur (ou une nouvelle recrue) doit pouvoir consulter une documentation qui liste toutes les variables nécessaires (y compris celles de configuration CORS), leur rôle, les valeurs attendues par environnement, et les valeurs par défaut sûres, sans avoir à lire le code source des services pour deviner leur usage.

**Why this priority**: La confusion sur la provenance de `CORS_ORIGINS` et `NEXT_PUBLIC_API_URL` (répétés et parfois contradictoires entre fichiers) a directement causé une régression de connectivité front/API. Documenter clairement ce doute élimine la classe d'erreur la plus coûteuse observée.

**Independent Test**: Un développeur qui n'a jamais touché au projet peut, à la seule lecture de la documentation, identifier quelle variable contrôle le CORS, quelles valeurs elle doit contenir par environnement, et où la modifier — sans consulter d'autre source.

**Acceptance Scenarios**:

1. **Given** la documentation de configuration, **When** un développeur cherche comment configurer les origines autorisées par le CORS, **Then** il trouve une explication claire de la variable concernée, de son format, et de sa valeur par défaut pour chaque environnement (dev / test / prod).
2. **Given** la documentation de configuration, **When** un développeur cherche une variable quelconque utilisée par l'API ou le front, **Then** il la retrouve listée avec sa description, sans avoir à parcourir le code.

---

### User Story 3 - Un développeur vérifie que Docker applique réellement la configuration attendue (Priority: P3)

Un développeur qui démarre les conteneurs Docker (API, front, etc.) doit pouvoir vérifier facilement, service par service, que la configuration effectivement utilisée à l'intérieur des conteneurs correspond bien à ce qui est déclaré dans le fichier de configuration, pour éviter les régressions silencieuses type "le conteneur tourne encore avec une ancienne valeur".

**Why this priority**: Pendant le diagnostic de cette session, plusieurs recréations de conteneurs ont été nécessaires car la valeur réellement appliquée dans le conteneur ne correspondait pas à celle du fichier édité (héritage de variables de shell, fichiers générés non resynchronisés). Une vérification simple et documentée évite de reproduire ce cycle de débogage long.

**Independent Test**: Un développeur peut exécuter une procédure de vérification documentée (ou un script dédié) qui confirme, pour chaque service Docker concerné, que les variables critiques (dont `CORS_ORIGINS` et l'URL publique de l'API) affichées dans le conteneur correspondent à celles attendues pour l'environnement sélectionné.

**Acceptance Scenarios**:

1. **Given** les conteneurs Docker démarrés pour un environnement donné, **When** le développeur suit la procédure de vérification, **Then** il obtient une confirmation explicite que chaque service critique utilise bien la configuration attendue.
2. **Given** une valeur de configuration modifiée dans le fichier unique, **When** le développeur relance les conteneurs selon la procédure documentée, **Then** la nouvelle valeur est effectivement appliquée dans les conteneurs, sans reliquat de l'ancienne configuration.

---

### Edge Cases

- Que se passe-t-il si le fichier de configuration unique est absent au démarrage (nouveau poste, CI) ? Le système doit signaler clairement quelle variable manque plutôt que d'échouer silencieusement ou de démarrer avec une configuration incohérente.
- Que se passe-t-il si la variable sélectrice d'environnement contient une valeur autre que les trois valeurs autorisées (dev / test / prod) ? Le système doit refuser de démarrer avec un message d'erreur explicite plutôt que d'appliquer une configuration par défaut ambiguë.
- Que se passe-t-il si une variable de shell (exportée dans le terminal du développeur) porte le même nom qu'une variable du fichier de configuration ? Le comportement de précédence doit être documenté et vérifiable, afin d'éviter la classe de bug déjà rencontrée où une variable de shell obsolète primait silencieusement sur le fichier édité.
- Que se passe-t-il pour les secrets de production (mots de passe, clés JWT/session, identifiants LDAP) dans le fichier de l'environnement de production ? Le fichier versionné contient des placeholders explicites (ex. `change-me-in-production`) ; le système doit rendre visible/détectable le cas où un placeholder n'a pas été surchargé alors que l'environnement actif est la production.
- L'environnement de staging (fichiers et compose dédiés) est supprimé : toute référence à staging dans la documentation, les scripts ou les workflows CI/CD doit être retirée ou explicitement redirigée vers production.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le système DOIT exposer exactement trois environnements applicatifs possibles — développement, test, production — pilotés par une seule variable sélectrice d'environnement.
- **FR-002**: Le système DOIT fournir, pour chaque environnement (dev / test / prod), un unique fichier de configuration autonome et auto-suffisant comme point d'entrée documenté : un développeur travaillant sur un poste ou un déploiement donné ne doit jamais avoir besoin de consulter ou de modifier plus d'un fichier à la fois. Cela remplace la configuration actuellement répartie sur `.env.shared`, `.env.development`, `.env.test`, `.env.staging`, `.env.production` et `.env.example`.
- **FR-003**: Le système DOIT permettre de changer d'environnement applicatif (dev / test / prod) en activant le fichier de configuration correspondant (ex. via un mécanisme de sélection simple tel qu'un lien ou une copie vers un nom de fichier standard), sans qu'aucune variable de configuration n'ait besoin d'être déplacée, dupliquée ou fusionnée manuellement entre plusieurs fichiers.
- **FR-004**: Le système DOIT supprimer les sources de configuration concurrentes actuellement capables de prendre le pas silencieusement sur le fichier de configuration actif documenté (notamment : fichier racine `.env` non versionné utilisé par Docker Compose pour la substitution de variables, fichier `.env.shared` fusionné séparément, fichiers générés `front/.env.local` et `search_api_solr/.env.local`, variables héritées du shell) — chaque service (API, front, Docker Compose) DOIT lire directement le fichier de l'environnement actif, sans étape de génération/fusion intermédiaire.
- **FR-005**: Le système DOIT inclure, dans le fichier de configuration unique (ou son schéma documenté), la configuration CORS (origines autorisées) ainsi que l'ensemble des variables nécessaires au fonctionnement de l'API et du front (URLs de service, Solr, Redis, base de données, authentification LDAP/SSO, secrets).
- **FR-006**: Le système DOIT documenter, pour chaque variable de configuration, son rôle, son format attendu, et sa valeur par environnement (dev / test / prod), dans un document unique facilement consultable par un développeur.
- **FR-007**: Le système DOIT documenter explicitement les règles de précédence de la configuration (quelle source gagne en cas de conflit) afin qu'un développeur puisse diagnostiquer lui-même une incohérence de configuration sans support extérieur.
- **FR-008**: Le système DOIT permettre de vérifier, pour chaque service Docker démarré, que la configuration réellement appliquée dans le conteneur correspond à la configuration attendue pour l'environnement sélectionné.
- **FR-009**: Le système DOIT refuser de démarrer, avec un message d'erreur explicite, si la variable sélectrice d'environnement contient une valeur autre que les trois valeurs autorisées, ou si une variable requise pour l'environnement sélectionné est absente.
- **FR-010**: Le système NE DOIT PAS permettre qu'un secret réel de production (mot de passe, clé JWT/session, identifiant LDAP) soit committé en clair dans le dépôt : le fichier de configuration de l'environnement de production versionné DOIT contenir des valeurs placeholders explicites (ex. `change-me-in-production`) et non des secrets réels.
- **FR-011**: Le système DOIT rester simple d'usage pour un développeur découvrant le projet : la procédure de mise en route en local ne doit nécessiter la modification que d'un seul fichier, en s'appuyant sur des valeurs par défaut sûres pour le développement.
- **FR-012**: Le système DOIT fournir exactement trois fichiers de configuration modèles versionnés (un par environnement : dev, test, prod), chacun autonome et complet, activé individuellement selon le contexte (poste de développement, exécution des tests, déploiement de production) — aucun fichier partagé (`.env.shared`) ni fichier d'exemple séparé (`.env.example`) ne doit être requis en plus du fichier de l'environnement actif.
- **FR-013**: Le système DOIT retirer l'environnement de déploiement "staging" (fichier de configuration dédié et configuration Docker Compose associée) ; toute documentation, script ou workflow CI/CD qui y fait encore référence DOIT être mis à jour ou supprimé en conséquence.
- **FR-014**: Le système DOIT signaler de façon visible (avertissement ou blocage au démarrage) si l'environnement actif est la production et qu'une valeur de secret encore égale à son placeholder par défaut est détectée, afin d'éviter un déploiement en production avec des secrets non surchargés.

### Key Entities

- **Fichier de configuration unique**: point d'entrée documenté contenant (ou référençant) l'ensemble des variables nécessaires au fonctionnement de l'application ; porte la variable sélectrice d'environnement.
- **Variable sélectrice d'environnement**: variable dont la valeur (dev / test / prod) détermine quel jeu de configuration est actif pour l'ensemble des services.
- **Documentation des variables**: référence listant chaque variable, son rôle, son format, ses valeurs par environnement, y compris la configuration CORS.
- **Procédure de vérification Docker**: méthode documentée (manuelle ou scriptée) permettant de confirmer que la configuration appliquée dans chaque conteneur correspond à la configuration attendue.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un développeur peut passer d'un environnement à un autre (dev / test / prod) en modifiant une seule variable dans un seul fichier, sans avoir à toucher un second fichier.
- **SC-002**: Le nombre de fichiers de configuration qu'un développeur doit connaître pour faire fonctionner le projet en local passe d'au moins 6 fichiers actuellement à 1 fichier documenté comme point d'entrée.
- **SC-003**: 100% des variables de configuration utilisées par l'API et le front (y compris CORS) sont listées et décrites dans un document unique de référence.
- **SC-004**: Après démarrage des conteneurs Docker pour un environnement donné, un développeur peut confirmer en moins de 2 minutes, via la procédure documentée, que la configuration appliquée dans chaque conteneur correspond à celle attendue.
- **SC-005**: Zéro incident de type "configuration silencieusement obsolète prise en compte" reproduit lors du scénario de test de régression (changement de valeur, redémarrage, vérification) une fois la procédure suivie.

## Assumptions

- **"Un seul fichier" signifie un seul fichier actif à la fois, par contexte** : trois fichiers modèles versionnés existent (un par environnement : dev, test, prod), chacun autonome et complet, mais un développeur ou un déploiement donné n'en consulte et n'en modifie jamais qu'un seul. Ce n'est pas un fichier unique contenant simultanément les valeurs des trois environnements (décision Q1 = option A).
- **L'environnement "staging" est supprimé** : le fichier de configuration dédié et la configuration Docker Compose de staging sont retirés ; seuls dev, test et prod subsistent comme environnements et cibles de déploiement (décision Q2 = option B). Tout usage de staging par ailleurs (documentation, CI/CD) doit être identifié et traité en amont de l'implémentation.
- **Les secrets de production restent des placeholders dans le fichier versionné** : le fichier de configuration de production committé contient des valeurs par défaut explicitement invalides (ex. `change-me-in-production`), à surcharger obligatoirement au moment du déploiement réel ; le système ajoute une vérification pour rendre visible l'oubli d'une telle surcharge (décision Q3 = option A).
- Les développeurs travaillent principalement en local via Docker Compose (mode déjà en place dans ce projet) ; la simplification ne remet pas en cause l'usage de Docker Compose comme méthode de démarrage recommandée.
- La mécanique précise d'"activation" d'un fichier de configuration (copie, lien symbolique, variable pointant vers un chemin, etc.) sera déterminée lors de la phase de planification ; cette spécification fixe l'expérience développeur attendue (un seul fichier à la fois, une bascule simple entre environnements) indépendamment du mécanisme technique final.
- La compatibilité avec les scripts et workflows CI/CD existants (tests, déploiement) doit être préservée ou explicitement mise à jour dans le cadre de ce chantier, notamment pour retirer toute référence à staging.

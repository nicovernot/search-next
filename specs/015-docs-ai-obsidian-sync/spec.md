# Feature Specification: Documentation technique fiable, lisible dans Obsidian et exploitable par l'IA

**Feature Branch**: `015-docs-ai-obsidian-sync`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "mettre à jours les docs en accord avec le code il faut que les dos soient utilisables par l'ia et qu'elle puissent etre visualisés dans obsidian. il faut des exmples concrets etc ;"

## Contexte

Le dossier `docs/` (12 fichiers : `ARCHITECTURE.md`, `API_V1.md`, `LOGGING.md`, `ENVIRONMENTS.md`, `CORS_CONFIGURATION.md`, `CORS_IMPLEMENTATION_SUMMARY.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md`, `INSTALL_PROD_NO_DOCKER.md`, `RECOMMENDATIONS.md`, `REDIS_INTEGRATION.md`, `SETUP_COMPLETE.md`, `CHANGELOG.md`) contient la documentation technique et opérationnelle du projet. Le `README.md` racine avertit déjà que « les fichiers de `docs/` peuvent contenir des références historiques à d'anciens ports ou à d'anciennes briques frontend ».

Un audit rapide confirme des écarts concrets : `docs/ARCHITECTURE.md` contient trois blocs de conflit Git non résolus (`<<<<<<< HEAD` / `=======` / `>>>>>>>`) toujours présents dans le fichier suivi, ce qui rend ces sections illisibles telles quelles pour un humain, cassées dans un rendu Obsidian, et trompeuses pour un agent IA qui les lirait comme du texte normal. D'autres fichiers documentent des états ponctuels (audits, résumés de mise en place) sans indiquer clairement s'ils reflètent encore l'état courant du code.

Cette feature ne modifie aucun comportement applicatif : elle met à jour le contenu de `docs/` pour qu'il soit exact, daté, navigable dans Obsidian et directement exploitable par un agent IA — avec des exemples concrets plutôt que des descriptions abstraites.

**Périmètre** : uniquement les fichiers du dossier `docs/` (12 fichiers). `specs/` a été traité par la feature 014 (cohérence du dépôt et des artefacts de spécification). Le `README.md` racine, `front/README.md`, `front/CONTRIBUTING.md`, `search_api_solr/*.md` et `solrconfig/*.md` sont hors périmètre de cette feature.

## Clarifications

### Session 2026-09-03

- Q: Cette feature doit-elle produire un script de vérification réutilisable pour `docs/` (sur le modèle de `scripts/check_spec_coherence.sh` de la feature 014), ou se limiter à une mise à jour manuelle ponctuelle du contenu ? → A: Oui — script de vérification réutilisable, aligné sur `scripts/check_spec_coherence.sh`.
- Q: Quand deux fichiers de `docs/` couvrent un sujet proche sous des noms différents (ex. `CORS_CONFIGURATION.md` vs `CORS_IMPLEMENTATION_SUMMARY.md`), faut-il les fusionner en un seul fichier de référence, ou les garder séparés avec un rôle étiqueté ? → A: Fusionner — le contenu vérifié du résumé ponctuel est intégré au document de référence vivant, le résumé est retiré.
- Q: Les exemples concrets ajoutés doivent-ils utiliser exclusivement des valeurs génériques/anonymisées, ou peuvent-ils reprendre des valeurs réelles de l'environnement de développement local ? → A: Exclusivement générique/anonymisé — aucune valeur réelle, même non sensible (y compris ports et hôtes de dev local), n'est copiée telle quelle dans un exemple.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Se fier à une documentation exacte (Priority: P1)

En tant que mainteneur ou agent IA consultant `docs/`, je veux que chaque affirmation factuelle (versions, endpoints, ports, chemins de fichiers, commandes) corresponde à l'état actuel du code, afin de prendre des décisions ou répondre à des questions sans devoir vérifier chaque détail dans le code source.

**Why this priority**: Une documentation inexacte ou cassée (blocs de conflit Git non résolus) est pire que l'absence de documentation : elle induit en erreur silencieusement et fait perdre du temps à qui s'y fie, humain ou IA.

**Independent Test**: Ouvrir chaque fichier de `docs/`, vérifier qu'aucun marqueur de conflit Git ne subsiste, et comparer un échantillon d'affirmations (versions de dépendances, endpoints exposés, ports, commandes) avec le code et la configuration actuels.

**Acceptance Scenarios**:

1. **Given** `docs/ARCHITECTURE.md` contient des blocs `<<<<<<< HEAD` / `=======` / `>>>>>>>` non résolus, **When** le fichier est mis à jour, **Then** il ne reste aucun marqueur de conflit et chaque section affiche une seule version cohérente de l'information.
2. **Given** un fichier de `docs/` affirme un port, un endpoint ou une commande, **When** cette affirmation est comparée au code ou à la configuration actuels, **Then** elle est soit exacte, soit corrigée, soit explicitement signalée comme historique avec une date.

---

### User Story 2 - Naviguer la documentation comme un vault Obsidian (Priority: P2)

En tant que mainteneur qui ouvre `docs/` comme vault Obsidian, je veux trouver un point d'entrée listant tous les documents et des liens internes qui se résolvent correctement, afin de naviguer d'un sujet à l'autre sans deviner quel fichier contient quelle information.

**Why this priority**: Sans point d'entrée ni liens fiables, la documentation reste une collection de fichiers isolés — inutilisable comme base de connaissance, que ce soit dans Obsidian ou pour un agent IA qui doit choisir quel fichier ouvrir.

**Independent Test**: Ouvrir le dossier `docs/` comme vault Obsidian (ou équivalent) et vérifier qu'un fichier d'index liste chaque document avec une description d'une ligne, que les liens internes s'ouvrent sur la bonne cible, et qu'aucune syntaxe brisée n'apparaît à l'affichage.

**Acceptance Scenarios**:

1. **Given** le dossier `docs/`, **When** un lecteur cherche « comment est configuré CORS », **Then** il trouve le document pertinent en moins d'une minute via le point d'entrée, sans ouvrir chaque fichier un par un.
2. **Given** un document de `docs/` référence un autre document ou un fichier de code, **When** ce lien est ouvert dans Obsidian ou suivi par un agent IA, **Then** il pointe vers une cible existante via un chemin relatif portable (pas de chemin absolu propre à une machine).

---

### User Story 3 - Vérifier un comportement via un exemple concret (Priority: P3)

En tant que développeur ou agent IA qui découvre une fonctionnalité via `docs/`, je veux un exemple concret et exécutable (commande, requête, réponse) pour chaque comportement documenté, afin de vérifier immédiatement que je l'ai bien compris sans devoir construire l'exemple moi-même.

**Why this priority**: Une description abstraite laisse place à l'interprétation ; un exemple concret est directement vérifiable et réutilisable, en particulier pour un agent IA qui doit produire du code ou des commandes cohérentes avec le système réel.

**Independent Test**: Pour chaque document de `docs/` qui décrit un comportement exécutable (endpoint, commande, configuration), vérifier qu'il contient au moins un exemple concret (commande shell, requête/réponse, extrait de configuration) et que cet exemple est cohérent avec le code actuel.

**Acceptance Scenarios**:

1. **Given** un document décrit un endpoint ou une commande, **When** le document est consulté, **Then** il contient un exemple concret (ex. commande `curl`, commande shell, extrait de configuration) illustrant ce comportement.
2. **Given** un exemple concret présent dans la documentation, **When** il est comparé au code ou testé, **Then** il reste valide (endpoint existant, commande exécutable, paramètres corrects).

---

### Edge Cases

- Un document décrit un état ponctuel passé (audit, résumé de mise en place terminée) plutôt qu'une référence vivante : il doit être explicitement étiqueté comme historique/daté, sans être présenté comme l'état courant.
- Deux versions divergentes d'une même information subsistent dans un bloc de conflit Git non résolu (ex. deux dates d'audit différentes pour `docs/ARCHITECTURE.md`) : la version la plus récente et vérifiable via le code fait foi ; l'autre est retirée.
- Un fichier de `docs/` porte un nom qui entre en collision avec un autre document du dépôt sans faire réellement doublon de contenu (ex. `docs/CHANGELOG.md` pour l'historique technique/opérationnel face à `specs/CHANGELOG.md` pour l'historique des livraisons de specs) : les deux sont conservés, mais leur rôle respectif doit être explicite pour qu'un lecteur ou une IA sache lequel consulter pour quel usage.
- Un fichier résumé ponctuel (ex. `CORS_IMPLEMENTATION_SUMMARY.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md`, `SETUP_COMPLETE.md`) fait doublon avec un document de référence vivant sur le même sujet : son contenu encore vérifiable est fusionné dans le document de référence vivant, et le fichier résumé est retiré.
- Un exemple documenté (port, chemin, commande) ne fonctionne plus en l'état : il doit être corrigé pour refléter le comportement actuel, ou retiré s'il n'est plus pertinent.
- Une information ne peut pas être vérifiée automatiquement (ex. décision opérationnelle passée) : elle reste en l'état mais n'est ni supprimée ni présentée comme vérifiée si elle ne l'est pas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Le contenu de chaque fichier de `docs/` DOIT refléter l'état actuel du code, de la configuration ou du comportement qu'il décrit (versions, endpoints, ports, chemins de fichiers, commandes).
- **FR-002**: Aucun fichier de `docs/` NE DOIT contenir de marqueur de conflit de contrôle de version non résolu (`<<<<<<<`, `=======`, `>>>>>>>`) — vérifié automatiquement (FR-011) — ni d'autre syntaxe Markdown manifestement cassée (bloc de code non fermé, tableau malformé) — vérifié manuellement lors de l'édition de chaque fichier.
- **FR-003**: Chaque fichier de `docs/` DOIT indiquer, près du début, ce qu'il documente et la date à laquelle son contenu a été vérifié par rapport au code, afin qu'un lecteur ou une IA puisse juger sa fraîcheur sans lire l'intégralité du fichier.
- **FR-004**: Un fichier dont le contenu décrit un événement ponctuel passé (audit, résumé de mise en place terminée) plutôt qu'une référence vivante DOIT être explicitement étiqueté comme historique/daté.
- **FR-005**: Lorsqu'un fichier de `docs/` décrit un comportement exécutable (endpoint, commande, configuration), il DOIT inclure au moins un exemple concret et structurellement exact (commande à exécuter, requête et réponse d'exemple, extrait de configuration) plutôt qu'une description abstraite seule — la syntaxe, les chemins d'endpoint, les paramètres et le format sont exacts, avec des valeurs de substitution génériques conformes à FR-012 pour les éléments propres à un environnement.
- **FR-006**: Les références internes entre fichiers de `docs/`, et vers des fichiers hors `docs/` qu'ils décrivent, DOIVENT utiliser des chemins relatifs qui se résolvent correctement à la fois comme liens cliquables dans un vault Obsidian et comme chemins exploitables par un lecteur humain ou un agent IA — sans chemin absolu propre à une machine.
- **FR-007**: `docs/` DOIT fournir un point d'entrée unique listant chaque fichier du dossier avec une description d'une ligne de son objet, afin qu'un lecteur (humain ou IA) trouve le document pertinent sans ouvrir chaque fichier.
- **FR-008**: Lorsqu'un fichier de `docs/` est un résumé ponctuel (audit, mise en place terminée) dont le contenu vérifié fait doublon avec un document de référence vivant sur le même sujet (ex. `CORS_IMPLEMENTATION_SUMMARY.md` face à `CORS_CONFIGURATION.md`, `ENVIRONMENT_MANAGEMENT_SUMMARY.md` face à `ENVIRONMENTS.md`), ce contenu DOIT être fusionné dans le document de référence vivant et le fichier résumé retiré. Lorsque deux fichiers du dépôt couvrent des sujets proches sous des noms similaires mais servent chacun un usage distinct et légitime en continu (ex. `docs/CHANGELOG.md` pour l'historique technique/opérationnel face à `specs/CHANGELOG.md` pour l'historique des livraisons de specs), leurs rôles respectifs DOIVENT être explicitement documentés plutôt que fusionnés.
- **FR-009**: La mise à jour de `docs/` NE DOIT PAS modifier le comportement applicatif, la configuration par défaut, ou le code source.
- **FR-010**: Toute correction factuelle apportée à `docs/` DOIT être traçable à une source vérifiable (code actuel, test, fichier de configuration, ou commit Git) plutôt qu'à une supposition.
- **FR-011**: Le périmètre DOIT inclure un contrôle automatisé, non destructif et réexécutable qui vérifie pour les fichiers de `docs/` : l'absence de marqueurs de conflit (FR-002), la présence d'une date de fraîcheur (FR-003) et la résolution des liens internes (FR-006) — sur le modèle de `scripts/check_spec_coherence.sh` livré en feature 014, afin que la garantie de cohérence reste vérifiable dans le temps et pas seulement au moment de la livraison.
- **FR-012**: Tout exemple concret ajouté à `docs/` DOIT utiliser exclusivement des valeurs génériques ou anonymisées (hôtes, ports, identifiants, tokens, exemples de documents) — aucune valeur réelle propre à l'environnement, même non sensible, ne DOIT être copiée telle quelle, y compris les ports ou noms d'hôtes de développement local actuellement configurés. Un exemple reste néanmoins structurellement exact (endpoint, méthode, paramètres, format) : seules les valeurs propres à un environnement sont remplacées par un espace réservé explicite (ex. `<HOST>`, `<PORT>`, ou le nom de la variable d'environnement documentée qui la définit).

### Key Entities

- **Fichier de documentation** : un fichier Markdown de `docs/` — son sujet, sa date de dernière vérification, son statut de fraîcheur (courant / historique).
- **Exemple concret** : illustration exécutable rattachée à une affirmation d'un fichier de documentation (commande, requête/réponse, extrait de configuration).
- **Référence croisée** : lien entre deux fichiers de documentation, ou entre un fichier de documentation et un fichier de code.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100 % des fichiers de `docs/` sont exempts de marqueurs de conflit non résolus (vérifié automatiquement) et d'autre syntaxe Markdown manifestement cassée (vérifié manuellement à l'édition).
- **SC-002**: 100 % d'un échantillon d'affirmations factuelles vérifiables (versions, endpoints, ports, commandes) contrôlées contre le code actuel sont exactes, ou explicitement signalées comme historiques.
- **SC-003**: Un lecteur trouve le document pertinent pour un sujet donné (ex. « comment est configuré CORS ») en moins d'une minute via le point d'entrée de `docs/`, sans avoir à ouvrir le code.
- **SC-004**: 100 % des documents décrivant un comportement exécutable contiennent au moins un exemple concret, structurellement exact et vérifiable après substitution des espaces réservés génériques documentés (FR-012).
- **SC-005**: L'ouverture du dossier `docs/` comme vault Obsidian n'affiche aucun lien interne cassé ni artefact de syntaxe non résolue.
- **SC-006**: Un agent IA répondant à une question d'intégration standard (ex. « comment est configuré le logging », « quels sont les endpoints de l'API v1 ») en utilisant uniquement `docs/` produit une réponse cohérente avec le code actuel, sans avoir besoin de lire les fichiers source.
- **SC-007**: Le contrôle automatisé de `docs/` s'exécute sans modifier aucun fichier et peut être relancé à tout moment pour confirmer que les garanties SC-001, SC-002 (partie vérifiable) et SC-005 restent vraies dans le temps.

## Assumptions

- Le périmètre de cette feature est le dossier `docs/` (12 fichiers) uniquement ; `specs/` a déjà été traité par la feature 014. `README.md` racine, `front/README.md`, `front/CONTRIBUTING.md`, `search_api_solr/*.md` et `solrconfig/*.md` restent hors périmètre (candidats à une feature de suivi si nécessaire).
- « Utilisable par l'IA » signifie un Markdown structuré, exact, daté et indexé — pas un format machine-readable spécifique (pas de schéma JSON/YAML obligatoire au-delà d'un éventuel entête léger).
- « Visualisable dans Obsidian » signifie un Markdown valide et portable avec des liens relatifs fonctionnels et sans syntaxe cassée — cela n'implique pas de créer une configuration de vault Obsidian (`.obsidian/`) ni d'installer des plugins.
- Lorsqu'un bloc de conflit Git non résolu contient deux versions divergentes d'une information, la version la plus récente et vérifiable via le code actuel fait foi.
- Un document historique/ponctuel dont le contenu vérifiable fait doublon avec un document de référence vivant est fusionné dans ce dernier puis retiré (voir Clarifications, session 2026-09-03). Un document historique/ponctuel qui n'a pas d'équivalent de référence vivant (aucun doublon à fusionner) est conservé mais clairement étiqueté comme historique, non supprimé — cohérent avec la pratique documentaire non destructive déjà appliquée en feature 014.

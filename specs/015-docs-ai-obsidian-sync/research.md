# Research — Documentation technique fiable, lisible dans Obsidian et exploitable par l'IA

## Constat d'audit (Phase 0)

Avant de figer les décisions ci-dessous, `docs/` (12 fichiers) a été inspecté intégralement :

| Fichier | État constaté |
|---|---|
| `ARCHITECTURE.md` | 3 blocs de conflit Git non résolus (lignes 3-9, 216-222, 265-269) ; pas de date de fraîcheur exploitable (elle est dans le conflit) |
| `API_V1.md` | Exemples `curl` déjà présents mais avec valeurs réelles (`localhost:8003`, URL de document réelle) ; pas de date de fraîcheur |
| `LOGGING.md` | Déjà daté (« Dernière mise à jour : 2026-05-10 », corrigé en feature 014) ; exemples déjà génériques (motifs `rg`) |
| `ENVIRONMENTS.md` | Pas de date de fraîcheur ; cible de fusion pour `ENVIRONMENT_MANAGEMENT_SUMMARY.md` |
| `CORS_CONFIGURATION.md` | Pas de date de fraîcheur ; cible de fusion pour `CORS_IMPLEMENTATION_SUMMARY.md` |
| `CORS_IMPLEMENTATION_SUMMARY.md` | Déjà étiqueté `> **DOUBLON**` pointant vers `CORS_CONFIGURATION.md` — étiquetage fait, fusion+suppression restant à faire |
| `ENVIRONMENT_MANAGEMENT_SUMMARY.md` | Déjà étiqueté `> **DOUBLON**` pointant vers `ENVIRONMENTS.md` — même situation |
| `INSTALL_PROD_NO_DOCKER.md` | Pas de date de fraîcheur ; commandes à vérifier |
| `RECOMMENDATIONS.md` | Déjà étiqueté `> **ARCHIVE**` (React 18 obsolète vs React 19 actuel) — étiquetage déjà fait, seule une date de vérification manque |
| `REDIS_INTEGRATION.md` | Pas de date de fraîcheur ; exemples à vérifier/anonymiser |
| `SETUP_COMPLETE.md` | Déjà étiqueté `> **ARCHIVE**` avec renvoi vers `search_api_solr/DOCKER.md` (hors périmètre) — pas de doublon interne au périmètre, reste historique en l'état |
| `CHANGELOG.md` | Aucun bandeau de rôle ; homonyme de `specs/CHANGELOG.md` (périmètre différent : historique technique/ops vs historique de livraison de specs) |

Aucun lien Markdown interne (`[texte](chemin)`) n'existe actuellement dans `docs/` — le point d'entrée et les références croisées sont un ajout, pas une réparation de liens cassés.

## Décision 1 — Format de l'entête de fraîcheur (FR-003)

- **Decision**: Chaque fichier de `docs/` porte, juste après le titre `#`, une ligne `**Dernière vérification** : AAAA-MM-JJ — <ce que documente le fichier en une phrase>`.
- **Rationale**: Convention déjà utilisée par `LOGGING.md` (« Dernière mise à jour ») et par les specs (`**Created**`, `**Status**`) — cohérent avec l'existant, lisible en clair par un humain, un rendu Obsidian, et un agent IA sans parsing spécial.
- **Alternatives considered**: Frontmatter YAML (`---\nupdated: ...\n---`) — rejeté : Obsidian l'affiche dans un panneau de propriétés (bien supporté), mais un agent IA lisant le fichier comme texte brut doit alors parser du YAML en plus du Markdown, et la convention existante (`LOGGING.md`) est déjà en texte simple ; introduire un second format casserait la cohérence entre fichiers pour un gain marginal.

## Décision 2 — Point d'entrée (FR-007)

- **Decision**: Créer `docs/README.md` listant chaque fichier restant avec une description d'une ligne et un lien relatif (`[ARCHITECTURE.md](./ARCHITECTURE.md)`), groupés par rôle (référence vivante / historique·archive / log continu).
- **Rationale**: `README.md` est le nom conventionnel qu'Obsidian, GitHub et un agent IA reconnaissent immédiatement comme point d'entrée d'un dossier ; aucun outillage supplémentaire requis.
- **Alternatives considered**: `docs/INDEX.md` — rejeté, moins conventionnel que `README.md` pour un dossier de dépôt Git ; `docs/_index.md` (convention Hugo/Jekyll) — rejeté, le projet n'utilise pas de générateur de site statique pour `docs/`.

## Décision 3 — Fusion des doublons résumé/référence (FR-008, Clarifications session 2026-09-03)

- **Decision**: `CORS_IMPLEMENTATION_SUMMARY.md` est fusionné dans `CORS_CONFIGURATION.md` (tout contenu vérifiable absent de la référence est porté dedans, ex. contexte du problème initial si utile) puis supprimé ; même traitement pour `ENVIRONMENT_MANAGEMENT_SUMMARY.md` → `ENVIRONMENTS.md`. `RECOMMENDATIONS.md` et `SETUP_COMPLETE.md` restent en l'état (déjà étiquetés `ARCHIVE`, sans document de référence vivant équivalent dans le périmètre `docs/`) : seule une date de vérification leur est ajoutée.
- **Rationale**: Les deux bandeaux `DOUBLON` existants confirment que l'équipe avait déjà identifié ces deux paires comme redondantes ; la Clarification du 2026-09-03 tranche explicitement pour la fusion plutôt que la coexistence étiquetée.
- **Alternatives considered**: Garder les 4 fichiers avec juste le bandeau `DOUBLON` (déjà fait) — rejeté par la clarification utilisateur : cela laisse deux fichiers par sujet à maintenir en cohérence indéfiniment.

## Décision 4 — Convention d'anonymisation des exemples (FR-012)

- **Decision**: Les valeurs propres à un environnement sont remplacées par un espace réservé entre chevrons reprenant le nom de la variable d'environnement documentée quand elle existe (`<API_BASE_URL>`, `<REDIS_URL>`), ou un espace réservé générique sinon (`<HOST>`, `<PORT>`). Les identifiants de documents d'exemple utilisent un motif visiblement fictif (`example-doc-id`, `https://example.org/...`) plutôt qu'une URL de document réel.
- **Rationale**: Les chevrons (`<...>`) sont une convention universellement reconnue dans la documentation technique pour « à remplacer » ; réutiliser le nom de variable d'environnement documentée relie directement l'exemple à sa source de configuration réelle (traçable, FR-010) sans exposer sa valeur.
- **Alternatives considered**: Domaines `example.com`/`example.org` seuls sans chevrons — rejeté pour les ports/valeurs numériques qui n'ont pas d'équivalent RFC 2606 ; garder les valeurs réelles de dev local (option B de la clarification) — explicitement écarté par la réponse utilisateur (option A retenue).

## Décision 5 — Contrôle automatisé (FR-011)

- **Decision**: `scripts/check_docs_coherence.sh` réutilise la structure de `scripts/check_spec_coherence.sh` (option `--root`, sections `note`/`finding`, code de sortie 0/1/2) mais restreint son périmètre à `docs/` et vérifie : absence de marqueurs de conflit (Section A), présence d'une ligne « Dernière vérification » par fichier (Section B), résolution de tous les liens Markdown relatifs internes trouvés dans n'importe quel fichier `docs/*.md` — pas seulement ceux listés dans `docs/README.md` (Section C). `scripts/test_check_docs_coherence.sh` reprend le même patron de fixtures temporaires que `scripts/test_check_spec_coherence.sh`.
- **Rationale**: Réponse à la Clarification du 2026-09-03 (option A) ; réutiliser un patron déjà revu et testé (feature 014) réduit le risque et le temps de développement (principe V de la constitution).
- **Alternatives considered**: Étendre `scripts/check_spec_coherence.sh` pour couvrir aussi `docs/` dans le même script — rejeté : la feature 014 a un périmètre déjà livré et stable (`specs/`) ; mélanger les deux périmètres dans un seul script complique les tests et le message de sortie sans bénéfice pour l'utilisateur.

## Décision 6 — Rôle de `docs/CHANGELOG.md` vs `specs/CHANGELOG.md` (FR-008, second cas)

- **Decision**: Ajouter en tête de `docs/CHANGELOG.md` une ligne explicite : « Historique technique/opérationnel (correctifs, config infra). Pour l'historique des livraisons de specs, voir `specs/CHANGELOG.md`. »
- **Rationale**: Les deux fichiers ont un contenu réellement différent (vérifié : `docs/CHANGELOG.md` liste des correctifs techniques ponctuels par commit, `specs/CHANGELOG.md` liste des livraisons de specs par feature) — ce n'est pas un doublon à fusionner mais une collision de nom à désambiguïser, conformément à FR-008 second cas.
- **Alternatives considered**: Renommer `docs/CHANGELOG.md` en `docs/TECHNICAL_CHANGELOG.md` — rejeté : renommer casserait tout lien externe existant vers ce fichier pour un gain de clarté marginal par rapport à un simple bandeau explicatif ; hors périmètre d'une feature documentaire non destructive.

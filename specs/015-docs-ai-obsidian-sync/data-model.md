# Modèle de données — Documentation technique fiable, lisible dans Obsidian et exploitable par l'IA

## DocumentationFile

Représente un fichier Markdown de `docs/`.

| Champ | Description | Règle |
|---|---|---|
| `path` | Chemin relatif dans `docs/` | Unique dans le dossier |
| `subject` | Ce que le fichier documente | Renseigné dans la ligne de fraîcheur (FR-003) |
| `last_verified` | Date de dernière vérification par rapport au code | Format `AAAA-MM-JJ`, obligatoire (FR-003) |
| `freshness_status` | `courant` ou `historique` | `historique` si le contenu décrit un événement ponctuel passé (FR-004) |
| `role` | `référence vivante`, `historique/archive`, ou `log continu` | Détermine le regroupement dans `docs/README.md` (Décision 2) |
| `merge_target` | Fichier de référence vivant dans lequel ce fichier est fusionné, si doublon | Rempli uniquement pour les fichiers marqués `DOUBLON` retenus pour fusion (FR-008) ; `null` sinon |

## ConcreteExample

Illustration exécutable rattachée à une affirmation d'un `DocumentationFile`.

| Champ | Description | Règle |
|---|---|---|
| `parent_file` | `DocumentationFile.path` auquel l'exemple appartient | Doit référencer un fichier existant |
| `type` | `commande`, `requête/réponse`, ou `extrait de configuration` | — |
| `uses_placeholder` | Les valeurs propres à l'environnement sont-elles substituées par un espace réservé ? | DOIT être vrai (FR-012) |
| `structurally_exact` | La syntaxe/l'endpoint/les paramètres sont-ils exacts par rapport au code actuel ? | DOIT être vrai (FR-005) |
| `evidence_ref` | Source vérifiable de l'exactitude (fichier de code, test, commit) | Requis (FR-010) |

## CrossReference

Lien entre deux `DocumentationFile`, ou entre un `DocumentationFile` et un fichier de code.

| Champ | Description | Règle |
|---|---|---|
| `source_file` | `DocumentationFile.path` d'origine | — |
| `target` | Chemin relatif cible (fichier de doc ou fichier de code) | Chemin relatif uniquement, jamais absolu propre à une machine (FR-006) |
| `resolves` | La cible existe-t-elle réellement à ce chemin ? | DOIT être vrai |

## CoherenceFinding

Ligne de sortie du contrôle automatisé `scripts/check_docs_coherence.sh` (FR-011).

| Champ | Description |
|---|---|
| `type` | `CONFLICT_MARKER`, `MISSING_FRESHNESS_DATE`, ou `BROKEN_LINK` |
| `file` | `DocumentationFile.path` concerné |
| `detail` | Ligne ou motif détecté |

## Relationships

- Un `DocumentationFile` possède zéro ou plusieurs `ConcreteExample`.
- Un `DocumentationFile` possède zéro ou plusieurs `CrossReference` sortantes (vers un autre `DocumentationFile` ou vers du code).
- Un `DocumentationFile` marqué doublon référence au plus un `merge_target` (un autre `DocumentationFile`) ; après fusion, le fichier source est retiré du dossier et n'apparaît plus dans `docs/README.md`.
- `scripts/check_docs_coherence.sh` produit zéro ou plusieurs `CoherenceFinding`, chacun rattaché à un `DocumentationFile.path`.

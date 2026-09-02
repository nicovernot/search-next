# Modèle de données — Cohérence du dépôt et des artefacts

## SpecRecord

Représente une feature documentée dans `specs/`.

| Champ | Description | Règle |
|---|---|---|
| `identifier` | Numéro courant de la spec | Unique dans le catalogue courant |
| `directory` | Dossier de la feature | Doit être présent sous `specs/` |
| `title` | Titre canonique | Identique dans les documents de référence |
| `status` | État fonctionnel | `livré`, `partiel`, `en cours`, `backlog` |
| `artifacts` | Présence de `spec.md`, `plan.md`, `tasks.md` | Complète ou exception justifiée |

## TaskRecord

Représente une tâche d'implémentation ou de validation.

| Champ | Description | Règle |
|---|---|---|
| `task_id` | Identifiant de tâche | Unique dans son `tasks.md` |
| `description` | Travail attendu | Action et résultat attendus identifiables |
| `checked` | État de réalisation | Ne peut être coché sans preuve |
| `blocking_reason` | Dépendance ou blocage | Requis lorsqu'une tâche reste ouverte |
| `evidence_ref` | Référence de preuve | Commande, fichier, test ou décision |

## ValidationEvidence

Représente une preuve permettant de justifier un état.

| Type | Contenu minimal |
|---|---|
| `test` | Commande, périmètre et résultat |
| `code` | Fichier ou symbole concerné |
| `documentation` | Fichier et section réconciliée |
| `decision` | Décision métier ou d'architecture, date et responsable |
| `environment` | Environnement vérifié et limitation éventuelle |

## Relationships

- Un `SpecRecord` possède un `spec.md`, au plus un `plan.md` courant et un `tasks.md` courant.
- Un `SpecRecord` possède zéro ou plusieurs `TaskRecord`.
- Un `TaskRecord` peut référencer une ou plusieurs `ValidationEvidence`.
- Un `SpecRecord` peut être référencé par les documents centraux `README`, `PLANNING` et `CHANGELOG`.
- Un ancien identifiant peut être relié à un `SpecRecord` courant uniquement par une entrée historique datée.

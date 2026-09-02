# Quickstart — Vérifier la cohérence du dépôt

## Prérequis

- Être à la racine du dépôt.
- Disposer de Git et de `ripgrep` (`rg`).
- Ne pas modifier les fichiers pendant l'audit.

## 1. Vérifier l'état Git

```bash
git status --short --branch
git diff --check
```

Résultat attendu : l'état de branche et les changements sont connus avant l'audit ; aucune erreur de whitespace n'est signalée.

## 2. Inventorier les artefacts

```bash
for d in specs/*/; do
  printf '%s ' "${d%/}"
  for f in spec.md plan.md tasks.md; do
    test -f "$d$f" && printf '%s ' "$f" || printf 'missing:%s ' "$f"
  done
  printf '\n'
done
```

Résultat attendu : toute spec active possède les trois artefacts ou une exception documentée.

## 3. Compter les tâches

```bash
for f in specs/*/tasks.md; do
  total=$(rg -c '^-[[:space:]]\[[xX ]\]' "$f" || true)
  checked=$(rg -c '^-[[:space:]]\[[xX]\]' "$f" || true)
  unchecked=$(rg -c '^-[[:space:]]\[ \]' "$f" || true)
  printf '%s total=%s checked=%s unchecked=%s\n' "$f" "$total" "$checked" "$unchecked"
done
```

Résultat attendu : les tâches ouvertes sont cohérentes avec les statuts déclarés et leurs blocages sont documentés.

## 4. Vérifier le contexte Spec Kit

```bash
./.specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
```

Résultat attendu : `FEATURE_DIR` pointe vers une feature possédant `spec.md`, `plan.md` et `tasks.md`.

## 5. Vérifier les références de numérotation

```bash
rg -n '012-logging-strategy|013-logging-strategy' specs docs README.md
```

Résultat attendu : les références courantes au logging utilisent un seul identifiant ; les anciennes références sont limitées aux notes historiques.

## Critère de fin

L'audit est réussi lorsque les contradictions sont soit supprimées, soit explicitement documentées comme dette, et que chaque statut de livraison possède une preuve identifiable.

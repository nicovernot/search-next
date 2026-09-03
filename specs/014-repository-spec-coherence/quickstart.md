# Quickstart — Vérifier la cohérence du dépôt

## Prérequis

- Être à la racine du dépôt.
- Disposer de Git et de `ripgrep` (`rg`).
- Ne pas modifier les fichiers pendant l'audit.

## Périmètre de l'audit

Le contrôle couvre les documents centraux et les artefacts par spec :

- `specs/README.md` — catalogue des specs.
- `specs/PLANNING.md` — planning et dépendances.
- `specs/CHANGELOG.md` — historique des décisions documentaires.
- `docs/ARCHITECTURE.md` — documentation opérationnelle liée aux specs.
- `specs/*/spec.md`, `specs/*/plan.md`, `specs/*/tasks.md` — artefacts par feature.

## Garantie de non-modification

`scripts/check_spec_coherence.sh` n'écrit, ne déplace et ne supprime aucun fichier : il n'exécute que des lectures (`cat`, `grep`/`rg`, `test -f`, `git status`) et un rapport sur la sortie standard. `scripts/test_check_spec_coherence.sh` vérifie cette garantie (voir T029) en s'assurant qu'aucun fichier suivi par Git n'est modifié après une exécution du contrôle.

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

## 6. Lancer le contrôle de cohérence automatisé

```bash
scripts/check_spec_coherence.sh
scripts/test_check_spec_coherence.sh
```

`check_spec_coherence.sh` est non destructif (voir garantie ci-dessus) et couvre : inventaire d'artefacts, comptage de tâches, numérotation dupliquée, références obsolètes hors `CHANGELOG.md`, statut « livré » sans tâche cochée, et tâches cochées sans référence de preuve détectable.

## Résultat de la dernière exécution (2026-09-03, T030)

```text
$ scripts/check_spec_coherence.sh ; echo "exit=$?"
...
12 incohérence(s) détectée(s)
exit=1

$ scripts/test_check_spec_coherence.sh
13 passed, 0 failed
```

Détail des 12 `FINDING` restants et leur disposition :

| Type | Détail | Disposition |
|---|---|---|
| `STALE_REF` (×5) | `PLANNING.md:15`, `README.md:64`, `docs/LOGGING.md:3`, `quickstart.md:70`, `research.md:35-37` mentionnent encore `012-logging-strategy` | **Faux positif attendu** — mentions historiques datées et contextualisées (Décision 3), le contrôle n'exempte que `CHANGELOG.md` par simplicité (voir `research.md` § Exceptions historiques) |
| `CHECKED_WITHOUT_EVIDENCE_HINT` (×6) | `001-search-core`, `003-ux-ui-premium-overhaul`, `006-tech-debt`, `007-refactor-search-context`, `011-auth-ldap-sso`, `012-semantic-search-api-platform` : tâches cochées sans marqueur de preuve explicite dans leur `tasks.md` | **Dette documentaire identifiée mais hors périmètre** de cette feature (`tasks.md` de 014 ne liste que 004/005/008/009/010/013 comme cibles de réconciliation) — à traiter dans une feature de suivi dédiée, conformément à la règle « toute correction découverte devient une feature séparée » |

Aucune incohérence de type `MISSING_ARTIFACT`, `TASK_STATUS_MISMATCH` ou `DUPLICATE_NUMBER` ne subsiste après réconciliation (T010-T022).

## Critère de fin

L'audit est réussi lorsque les contradictions sont soit supprimées, soit explicitement documentées comme dette, et que chaque statut de livraison possède une preuve identifiable. C'est l'état atteint ci-dessus : les 12 findings restants sont classés (faux positifs assumés ou dette hors périmètre documentée), aucun n'est une contradiction non traitée.

#!/usr/bin/env bash
#
# check_spec_coherence.sh — audit non destructif de la cohérence des specs.
#
# N'écrit, ne déplace ni ne supprime aucun fichier. N'exécute que des lectures
# (git status, grep/rg, test -f) et imprime un rapport sur la sortie standard.
#
# Usage:
#   scripts/check_spec_coherence.sh [--root DIR]
#
# Exit codes:
#   0 — aucune incohérence détectée
#   1 — au moins une incohérence détectée (voir rapport)
#   2 — erreur d'usage (root introuvable, etc.)

set -u

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --root)
            shift
            [[ $# -eq 0 ]] && { echo "ERROR: --root requires a directory" >&2; exit 2; }
            ROOT="$1"
            ;;
        --help|-h)
            grep '^#' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "ERROR: unknown option '$1'" >&2
            exit 2
            ;;
    esac
    shift
done

if [[ ! -d "$ROOT" ]]; then
    echo "ERROR: root directory not found: $ROOT" >&2
    exit 2
fi

SPECS_DIR="$ROOT/specs"
if [[ ! -d "$SPECS_DIR" ]]; then
    echo "ERROR: specs directory not found: $SPECS_DIR" >&2
    exit 2
fi

if command -v rg >/dev/null 2>&1; then
    GREP() { rg "$@"; }
else
    GREP() { grep -E "$@"; }
fi

FINDINGS=0
note() { printf '%s\n' "$1"; }
finding() { printf 'FINDING %s\n' "$1"; FINDINGS=$((FINDINGS + 1)); }

# --- Section A: Git state -----------------------------------------------
note "== Git state =="
if command -v git >/dev/null 2>&1 && git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
    git -C "$ROOT" status --short --branch
else
    note "(pas un dépôt Git ou git indisponible — section ignorée)"
fi

# --- Section B: Inventaire des artefacts ---------------------------------
note ""
note "== Inventaire des artefacts (spec.md / plan.md / tasks.md) =="
for d in "$SPECS_DIR"/*/; do
    dir_name="$(basename "$d")"
    for f in spec.md plan.md tasks.md; do
        if [[ ! -f "$d$f" ]]; then
            finding "MISSING_ARTIFACT $dir_name $f"
        fi
    done
done

# --- Section C: Comptage des tâches + statut vs complétude --------------
note ""
note "== Comptage des tâches par spec =="
for f in "$SPECS_DIR"/*/tasks.md; do
    [[ -f "$f" ]] || continue
    dir_name="$(basename "$(dirname "$f")")"
    total=$(grep -cE '^-[[:space:]]*\[[xX ]\]' "$f" || true)
    checked=$(grep -cE '^-[[:space:]]*\[[xX]\]' "$f" || true)
    unchecked=$(grep -cE '^-[[:space:]]*\[ \]' "$f" || true)
    printf 'TASKS %s total=%s checked=%s unchecked=%s\n' "$dir_name" "$total" "$checked" "$unchecked"
done

# --- Section D: Numérotation dupliquée -----------------------------------
note ""
note "== Numérotation dupliquée =="
prev_num=""
prev_dir=""
for d in "$SPECS_DIR"/*/; do
    dir_name="$(basename "$d")"
    num="${dir_name%%-*}"
    [[ "$num" =~ ^[0-9]+$ ]] || continue
    if [[ "$num" == "$prev_num" ]]; then
        finding "DUPLICATE_NUMBER $num $prev_dir $dir_name"
    fi
    prev_num="$num"
    prev_dir="$dir_name"
done

# --- Section E: Références obsolètes hors contexte historique -----------
note ""
note "== Références de numérotation obsolètes hors CHANGELOG =="
if [[ -d "$SPECS_DIR/013-logging-strategy" ]]; then
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        file="${line%%:*}"
        base="$(basename "$file")"
        if [[ "$base" != "CHANGELOG.md" ]]; then
            finding "STALE_REF $line"
        fi
    done < <(GREP -n '012-logging-strategy' "$SPECS_DIR" "$ROOT/docs" 2>/dev/null || true)
fi

# --- Section F: Statut livré sans preuve de tâche cochée -----------------
note ""
note "== Statut « livré » avec 0 tâche cochée (dette documentaire potentielle) =="
for f in "$SPECS_DIR"/*/tasks.md; do
    [[ -f "$f" ]] || continue
    dir_name="$(basename "$(dirname "$f")")"
    spec_file="$(dirname "$f")/spec.md"
    [[ -f "$spec_file" ]] || continue
    checked=$(grep -cE '^-[[:space:]]*\[[xX]\]' "$f" || true)
    total=$(grep -cE '^-[[:space:]]*\[[xX ]\]' "$f" || true)
    if grep -qE 'Status.*Livré|✅ Livré' "$spec_file" && [[ "$total" -gt 0 && "$checked" -eq 0 ]]; then
        finding "TASK_STATUS_MISMATCH $dir_name status=livré checked=0/$total"
    fi
done


# --- Section G: Tâches cochées sans référence de preuve -----------------
note ""
note "== Tâches cochées sans référence de preuve détectable =="
for f in "$SPECS_DIR"/*/tasks.md; do
    [[ -f "$f" ]] || continue
    dir_name="$(basename "$(dirname "$f")")"
    checked=$(grep -cE '^-[[:space:]]*\[[xX]\]' "$f" || true)
    if [[ "$checked" -gt 0 ]] && ! grep -qE 'Preuve|`[0-9a-f]{7,40}`|\.spec\.ts|test_' "$f"; then
        finding "CHECKED_WITHOUT_EVIDENCE_HINT $dir_name checked=$checked (aucune référence 'Preuve', commit, ou fichier de test trouvée)"
    fi
done

note ""
note "== Résumé =="
note "$FINDINGS incohérence(s) détectée(s)"

if [[ "$FINDINGS" -gt 0 ]]; then
    exit 1
fi
exit 0

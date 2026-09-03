#!/usr/bin/env bash
#
# check_docs_coherence.sh — audit non destructif de la cohérence de docs/.
#
# N'écrit, ne déplace ni ne supprime aucun fichier. N'exécute que des lectures
# (grep/rg, test -f) et imprime un rapport sur la sortie standard.
#
# Usage:
#   scripts/check_docs_coherence.sh [--root DIR]
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

DOCS_DIR="$ROOT/docs"
if [[ ! -d "$DOCS_DIR" ]]; then
    echo "ERROR: docs directory not found: $DOCS_DIR" >&2
    exit 2
fi

FINDINGS=0
note() { printf '%s\n' "$1"; }
finding() { printf 'FINDING %s\n' "$1"; FINDINGS=$((FINDINGS + 1)); }

# --- Section A: Marqueurs de conflit Git non résolus ---------------------
note "== Marqueurs de conflit Git =="
for f in "$DOCS_DIR"/*.md; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    while IFS=: read -r lineno line; do
        [[ -z "$lineno" ]] && continue
        finding "CONFLICT_MARKER $base:$lineno"
    done < <(grep -nE '^(<<<<<<<|=======$|>>>>>>>)' "$f" || true)
done

# --- Section B: Date de fraîcheur manquante -------------------------------
note ""
note "== Date de fraîcheur (« Dernière vérification ») =="
for f in "$DOCS_DIR"/*.md; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    if ! grep -q 'Dernière vérification' "$f"; then
        finding "MISSING_FRESHNESS_DATE $base"
    fi
done

# --- Section C: Liens Markdown relatifs cassés ----------------------------
note ""
note "== Liens Markdown internes =="
for f in "$DOCS_DIR"/*.md; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f")"
    dir="$(dirname "$f")"
    while IFS= read -r match; do
        [[ -z "$match" ]] && continue
        target="$(printf '%s' "$match" | sed -E 's/^\[[^]]*\]\(([^)]+)\)$/\1/')"
        # Ignorer les liens externes et les ancres pures
        case "$target" in
            http://*|https://*|mailto:*|\#*) continue ;;
        esac
        target_path="${target%%#*}"
        [[ -z "$target_path" ]] && continue
        resolved="$dir/$target_path"
        if [[ ! -e "$resolved" ]]; then
            finding "BROKEN_LINK $base -> $target"
        fi
    done < <(grep -oE '\[[^]]*\]\([^)]+\)' "$f" || true)
done

note ""
note "== Résumé =="
note "$FINDINGS incohérence(s) détectée(s)"

if [[ "$FINDINGS" -gt 0 ]]; then
    exit 1
fi
exit 0

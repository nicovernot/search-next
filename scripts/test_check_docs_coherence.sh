#!/usr/bin/env bash
#
# test_check_docs_coherence.sh — tests non destructifs pour check_docs_coherence.sh
#
# Chaque test construit un dossier docs/ synthétique dans un répertoire
# temporaire, exécute scripts/check_docs_coherence.sh --root <fixture>, et
# vérifie le code de sortie et/ou la présence de lignes FINDING attendues.
# Aucun fichier du dépôt réel n'est modifié.
#
# Usage: scripts/test_check_docs_coherence.sh

set -u

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/check_docs_coherence.sh"

PASS=0
FAIL=0

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

fixture_dir() {
    local name="$1"
    local dir="$TMP_ROOT/$name"
    mkdir -p "$dir/docs"
    printf '%s' "$dir"
}

assert_exit_code() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        printf 'PASS  %s (exit=%s)\n' "$desc" "$actual"
        PASS=$((PASS + 1))
    else
        printf 'FAIL  %s (expected exit=%s got=%s)\n' "$desc" "$expected" "$actual"
        FAIL=$((FAIL + 1))
    fi
}

assert_contains() {
    local desc="$1" needle="$2" haystack="$3"
    if grep -qF "$needle" <<<"$haystack"; then
        printf 'PASS  %s\n' "$desc"
        PASS=$((PASS + 1))
    else
        printf 'FAIL  %s (attendu: %s)\n' "$desc" "$needle"
        FAIL=$((FAIL + 1))
    fi
}

assert_not_contains() {
    local desc="$1" needle="$2" haystack="$3"
    if grep -qF "$needle" <<<"$haystack"; then
        printf 'FAIL  %s (ne devrait pas contenir: %s)\n' "$desc" "$needle"
        FAIL=$((FAIL + 1))
    else
        printf 'PASS  %s\n' "$desc"
        PASS=$((PASS + 1))
    fi
}

# --- Usage errors -----------------------------------------------------

test_usage_error_missing_root() {
    "$CHECK_SCRIPT" --root /nonexistent/path/xyz >/dev/null 2>&1
    assert_exit_code "usage: root introuvable -> exit 2" 2 "$?"
}

test_usage_error_unknown_option() {
    "$CHECK_SCRIPT" --bogus-flag >/dev/null 2>&1
    assert_exit_code "usage: option inconnue -> exit 2" 2 "$?"
}

test_usage_error_missing_docs_dir() {
    local d
    d="$(mktemp -d)"
    "$CHECK_SCRIPT" --root "$d" >/dev/null 2>&1
    assert_exit_code "usage: docs/ introuvable -> exit 2" 2 "$?"
    rm -rf "$d"
}

test_clean_fixture_exit_zero() {
    local d
    d="$(fixture_dir clean)"
    cat >"$d/docs/GUIDE.md" <<'EOF'
# Guide

**Dernière vérification** : 2026-09-03 — exemple propre.

Voir [autre guide](./OTHER.md).
EOF
    cat >"$d/docs/OTHER.md" <<'EOF'
# Autre

**Dernière vérification** : 2026-09-03
EOF
    "$CHECK_SCRIPT" --root "$d" >/dev/null 2>&1
    assert_exit_code "fixture propre -> exit 0" 0 "$?"
}

# --- T006: détection CONFLICT_MARKER --------------------------------------

test_conflict_marker_detected() {
    local d out
    d="$(fixture_dir conflict)"
    cat >"$d/docs/BROKEN.md" <<'EOF'
# Broken

<<<<<<< HEAD
version A
=======
version B
>>>>>>> abc123
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "marqueur de conflit détecté" "CONFLICT_MARKER BROKEN.md" "$out"
}

test_no_conflict_marker_not_flagged() {
    local d out
    d="$(fixture_dir no_conflict)"
    cat >"$d/docs/CLEAN.md" <<'EOF'
# Clean

**Dernière vérification** : 2026-09-03
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "aucun marqueur de conflit sur fichier propre" "CONFLICT_MARKER CLEAN.md" "$out"
}

# --- T007: détection MISSING_FRESHNESS_DATE -------------------------------

test_missing_freshness_date_detected() {
    local d out
    d="$(fixture_dir missing_date)"
    cat >"$d/docs/NODATE.md" <<'EOF'
# No date

Contenu sans entête de fraîcheur.
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "date de fraîcheur manquante détectée" "MISSING_FRESHNESS_DATE NODATE.md" "$out"
}

test_freshness_date_present_not_flagged() {
    local d out
    d="$(fixture_dir has_date)"
    cat >"$d/docs/DATED.md" <<'EOF'
# Dated

**Dernière vérification** : 2026-09-03
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "date présente non signalée" "MISSING_FRESHNESS_DATE DATED.md" "$out"
}

# --- T018: détection BROKEN_LINK (tous les fichiers docs/*.md, pas seulement README) ---

test_broken_link_in_readme_detected() {
    local d out
    d="$(fixture_dir broken_link_readme)"
    cat >"$d/docs/README.md" <<'EOF'
# Index

**Dernière vérification** : 2026-09-03

- [Fichier manquant](./MISSING.md)
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "lien cassé dans README détecté" "BROKEN_LINK README.md -> ./MISSING.md" "$out"
}

test_broken_link_outside_readme_detected() {
    local d out
    d="$(fixture_dir broken_link_body)"
    cat >"$d/docs/ARCHITECTURE.md" <<'EOF'
# Architecture

**Dernière vérification** : 2026-09-03

Voir aussi [Logging](./LOGGING.md) pour le détail.
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "lien cassé hors README.md détecté (portée élargie, cf. remédiation I1)" "BROKEN_LINK ARCHITECTURE.md -> ./LOGGING.md" "$out"
}

test_valid_relative_link_not_flagged() {
    local d out
    d="$(fixture_dir valid_link)"
    cat >"$d/docs/A.md" <<'EOF'
# A

**Dernière vérification** : 2026-09-03

Voir [B](./B.md).
EOF
    cat >"$d/docs/B.md" <<'EOF'
# B

**Dernière vérification** : 2026-09-03
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "lien relatif valide non signalé" "BROKEN_LINK A.md" "$out"
}

test_external_link_not_flagged() {
    local d out
    d="$(fixture_dir external_link)"
    cat >"$d/docs/EXT.md" <<'EOF'
# External

**Dernière vérification** : 2026-09-03

Voir [OpenEdition](https://www.openedition.org) et [ancre](#section).
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "lien externe non signalé" "BROKEN_LINK EXT.md" "$out"
}

# --- Non-destructiveness on the real repo ----------------------------------

test_non_destructive_on_real_repo() {
    local repo_root before after
    repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
    if [[ -z "$repo_root" ]]; then
        printf 'SKIP  non-destructive check (pas de dépôt git)\n'
        return
    fi
    before="$(git -C "$repo_root" status --porcelain)"
    "$CHECK_SCRIPT" --root "$repo_root" >/dev/null 2>&1
    after="$(git -C "$repo_root" status --porcelain)"
    if [[ "$before" == "$after" ]]; then
        printf 'PASS  %s\n' "check_docs_coherence.sh ne modifie aucun fichier suivi"
        PASS=$((PASS + 1))
    else
        printf 'FAIL  %s\n' "check_docs_coherence.sh a modifié l'état du dépôt"
        FAIL=$((FAIL + 1))
    fi
}

# --- Run all ---------------------------------------------------------------

test_usage_error_missing_root
test_usage_error_unknown_option
test_usage_error_missing_docs_dir
test_clean_fixture_exit_zero
test_conflict_marker_detected
test_no_conflict_marker_not_flagged
test_missing_freshness_date_detected
test_freshness_date_present_not_flagged
test_broken_link_in_readme_detected
test_broken_link_outside_readme_detected
test_valid_relative_link_not_flagged
test_external_link_not_flagged
test_non_destructive_on_real_repo

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]

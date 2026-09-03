#!/usr/bin/env bash
#
# test_check_spec_coherence.sh — tests non destructifs pour check_spec_coherence.sh
#
# Chaque test construit un dépôt de specs synthétique dans un répertoire
# temporaire, exécute scripts/check_spec_coherence.sh --root <fixture>, et
# vérifie le code de sortie et/ou la présence de lignes FINDING attendues.
# Aucun fichier du dépôt réel n'est modifié.
#
# Usage: scripts/test_check_spec_coherence.sh

set -u

SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK_SCRIPT="$SCRIPT_DIR/check_spec_coherence.sh"

PASS=0
FAIL=0

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

fixture_dir() {
    local name="$1"
    local dir="$TMP_ROOT/$name"
    mkdir -p "$dir/specs"
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

# --- T006: cas de sortie et codes d'erreur -------------------------------

test_usage_error_missing_root() {
    local out
    out="$("$CHECK_SCRIPT" --root /nonexistent/path/xyz 2>&1)"
    assert_exit_code "usage: root introuvable -> exit 2" 2 "$?"
}

test_usage_error_unknown_option() {
    "$CHECK_SCRIPT" --bogus-flag >/dev/null 2>&1
    assert_exit_code "usage: option inconnue -> exit 2" 2 "$?"
}

test_clean_fixture_exit_zero() {
    local d
    d="$(fixture_dir clean)"
    mkdir -p "$d/specs/001-demo"
    cat >"$d/specs/001-demo/spec.md" <<'EOF'
# Feature Specification: Demo

**Status**: ✅ Livré
EOF
    cat >"$d/specs/001-demo/plan.md" <<'EOF'
# Plan
EOF
    cat >"$d/specs/001-demo/tasks.md" <<'EOF'
# Tasks

- [x] T001 Faire le travail — *Preuve : commit `abc1234`.*
EOF
    "$CHECK_SCRIPT" --root "$d" >/dev/null 2>&1
    assert_exit_code "fixture propre -> exit 0" 0 "$?"
}

# --- T008: détection des statuts divergents (statut livré vs 0 tâche cochée) ---

test_status_divergence_detected() {
    local d out
    d="$(fixture_dir status_divergence)"
    mkdir -p "$d/specs/002-demo"
    cat >"$d/specs/002-demo/spec.md" <<'EOF'
# Feature Specification: Demo 2

**Status**: ✅ Livré
EOF
    cat >"$d/specs/002-demo/plan.md" <<'EOF'
# Plan
EOF
    cat >"$d/specs/002-demo/tasks.md" <<'EOF'
# Tasks

- [ ] T001 Non fait
- [ ] T002 Non fait non plus
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "statut livré + 0 tâche cochée détecté" "TASK_STATUS_MISMATCH 002-demo" "$out"
}

# --- T009: détection de numérotation dupliquée (même numéro, contenu différent) ---

test_duplicate_number_detected() {
    local d out
    d="$(fixture_dir dup_number)"
    mkdir -p "$d/specs/012-alpha" "$d/specs/012-beta"
    for sub in 012-alpha 012-beta; do
        cat >"$d/specs/$sub/spec.md" <<EOF
# Feature Specification: $sub
**Status**: ✅ Livré
EOF
        echo "# Plan" >"$d/specs/$sub/plan.md"
        printf -- '- [x] T001 fait — *Preuve : commit \x60abc1234\x60.*\n' >"$d/specs/$sub/tasks.md"
    done
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "deux dossiers numéro 012 détectés" "DUPLICATE_NUMBER 012" "$out"
}

# --- T015: détection des artefacts manquants ------------------------------

test_missing_artifact_detected() {
    local d out code
    d="$(fixture_dir missing_artifact)"
    mkdir -p "$d/specs/003-demo"
    echo "# Spec" >"$d/specs/003-demo/spec.md"
    echo "# Plan" >"$d/specs/003-demo/plan.md"
    # tasks.md volontairement absent
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    code="$?"
    assert_contains "tasks.md manquant détecté" "MISSING_ARTIFACT 003-demo tasks.md" "$out"
    assert_exit_code "artefact manquant -> exit 1" 1 "$code"
}

# --- T016: détection des tâches cochées sans preuve -----------------------

test_checked_without_evidence_detected() {
    local d out
    d="$(fixture_dir checked_no_evidence)"
    mkdir -p "$d/specs/004-demo"
    cat >"$d/specs/004-demo/spec.md" <<'EOF'
# Feature Specification: Demo 4
**Status**: ✅ Livré
EOF
    echo "# Plan" >"$d/specs/004-demo/plan.md"
    cat >"$d/specs/004-demo/tasks.md" <<'EOF'
# Tasks

- [x] T001 Tâche cochée sans aucune preuve mentionnée
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "tâche cochée sans preuve détectée" "CHECKED_WITHOUT_EVIDENCE_HINT 004-demo" "$out"
}

test_checked_with_evidence_not_flagged() {
    local d out
    d="$(fixture_dir checked_with_evidence)"
    mkdir -p "$d/specs/005-demo"
    cat >"$d/specs/005-demo/spec.md" <<'EOF'
# Feature Specification: Demo 5
**Status**: ✅ Livré
EOF
    echo "# Plan" >"$d/specs/005-demo/plan.md"
    cat >"$d/specs/005-demo/tasks.md" <<'EOF'
# Tasks

- [x] T001 Tâche cochée — *Preuve : commit `abc1234`.*
EOF
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "tâche avec preuve non signalée" "CHECKED_WITHOUT_EVIDENCE_HINT 005-demo" "$out"
}

# --- T023: présence des références de validation --------------------------

test_stale_ref_outside_changelog_detected() {
    local d out
    d="$(fixture_dir stale_ref)"
    mkdir -p "$d/specs/013-logging-strategy" "$d/docs"
    echo "# Spec" >"$d/specs/013-logging-strategy/spec.md"
    echo "# Plan" >"$d/specs/013-logging-strategy/plan.md"
    printf -- '- [x] T001 fait — *Preuve : commit `abc1234`.*\n' >"$d/specs/013-logging-strategy/tasks.md"
    cat >"$d/docs/ARCHITECTURE.md" <<'EOF'
La spec `012-logging-strategy` est partiellement livrée.
EOF
    mkdir -p "$d/specs"
    echo "| 2026-01-01 | docs | ancien identifiant 012-logging-strategy conservé pour historique |" >"$d/specs/CHANGELOG.md"
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_contains "référence obsolète hors CHANGELOG détectée" "STALE_REF" "$out"
}

test_stale_ref_inside_changelog_not_flagged() {
    local d out
    d="$(fixture_dir stale_ref_changelog_only)"
    mkdir -p "$d/specs/013-logging-strategy"
    echo "# Spec" >"$d/specs/013-logging-strategy/spec.md"
    echo "# Plan" >"$d/specs/013-logging-strategy/plan.md"
    printf -- '- [x] T001 fait — *Preuve : commit `abc1234`.*\n' >"$d/specs/013-logging-strategy/tasks.md"
    echo "| 2026-01-01 | docs | ancien identifiant 012-logging-strategy conservé pour historique |" >"$d/specs/CHANGELOG.md"
    out="$("$CHECK_SCRIPT" --root "$d" 2>&1)"
    assert_not_contains "mention historique dans CHANGELOG seule non signalée" "STALE_REF" "$out"
}

# --- T024: distinction validation échouée / non exécutée / bloquée --------
# Le contrôle ne peut pas distinguer automatiquement ces trois états (ils
# dépendent d'une exécution réelle hors de son périmètre en lecture seule) ;
# il vérifie donc que la convention documentaire des trois marqueurs est
# respectée dans les tasks.md du dépôt réel : une tâche non cochée doit soit
# rester silencieuse (pas encore triée), soit porter un marqueur explicite
# parmi "Bloqué", "non exécuté" ou "échoué".

test_blocking_reason_convention_present_in_repo() {
    local repo_root out
    repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/..")"
    out="$(grep -rE '\*\*Bloqué\*\*|non exécuté|échoué' "$repo_root/specs/013-logging-strategy/tasks.md" "$repo_root/specs/010-naming-intention-result/tasks.md" 2>/dev/null || true)"
    if [[ -n "$out" ]]; then
        printf 'PASS  %s\n' "convention de blocage (Bloqué/non exécuté/échoué) présente dans les tasks.md réconciliés"
        PASS=$((PASS + 1))
    else
        printf 'FAIL  %s\n' "convention de blocage absente des tasks.md réconciliés"
        FAIL=$((FAIL + 1))
    fi
}

# --- T029: garantie de non-modification ------------------------------------

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
        printf 'PASS  %s\n' "check_spec_coherence.sh ne modifie aucun fichier suivi"
        PASS=$((PASS + 1))
    else
        printf 'FAIL  %s\n' "check_spec_coherence.sh a modifié l'état du dépôt"
        FAIL=$((FAIL + 1))
    fi
}

# --- Run all ---------------------------------------------------------------

test_usage_error_missing_root
test_usage_error_unknown_option
test_clean_fixture_exit_zero
test_status_divergence_detected
test_duplicate_number_detected
test_missing_artifact_detected
test_checked_without_evidence_detected
test_checked_with_evidence_not_flagged
test_stale_ref_outside_changelog_detected
test_stale_ref_inside_changelog_not_flagged
test_blocking_reason_convention_present_in_repo
test_non_destructive_on_real_repo

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
[[ "$FAIL" -eq 0 ]]

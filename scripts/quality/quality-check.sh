#!/bin/bash
# Quality Gate Check Script
#
# Usage:
#   ./scripts/quality/quality-check.sh              # Full check (default)
#   ./scripts/quality/quality-check.sh --quick       # Quick check (changed files only)
#   ./scripts/quality/quality-check.sh --report      # Generate report without failing
#
# Individual checks:
#   ./scripts/quality/quality-check.sh --lint         # Ruff lint only
#   ./scripts/quality/quality-check.sh --format       # Ruff format check only
#   ./scripts/quality/quality-check.sh --conventions  # Code convention checks only
#   ./scripts/quality/quality-check.sh --tests        # Pytest only
#
# Options:
#   --changed     Only check files changed in git
#   --fix         Auto-fix lint and format issues
#   --open        Open HTML report in browser after running
#   -h, --help    Show this help message
#
# Exit codes:
#   0 = All checks passed
#   1 = Quality gate failed

set -euo pipefail
cd "$(dirname "$0")/../.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
MODE="full"
CHANGED_ONLY=false
AUTO_FIX=false
OPEN_REPORT=false
INDIVIDUAL_CHECK=false
RUN_LINT=""
RUN_FORMAT=""
RUN_CONVENTIONS=""
RUN_TESTS=""

show_help() {
    sed -n '2,22p' "$0" | sed 's/^# \?//'
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)    MODE="quick"; shift ;;
        --report)   MODE="report"; shift ;;
        --changed)  CHANGED_ONLY=true; shift ;;
        --fix)      AUTO_FIX=true; shift ;;
        --open)     OPEN_REPORT=true; shift ;;
        --lint)         RUN_LINT=true; INDIVIDUAL_CHECK=true; shift ;;
        --format)       RUN_FORMAT=true; INDIVIDUAL_CHECK=true; shift ;;
        --conventions)  RUN_CONVENTIONS=true; INDIVIDUAL_CHECK=true; shift ;;
        --tests)        RUN_TESTS=true; INDIVIDUAL_CHECK=true; shift ;;
        -h|--help)  show_help; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Determine which checks to run
should_run() {
    local flag_var="RUN_$1"
    local flag="${!flag_var}"

    if [ "$INDIVIDUAL_CHECK" = true ]; then
        [ "$flag" = true ]
        return $?
    fi

    case $MODE in
        quick)
            # Quick mode: lint + format only
            [[ "$1" == "LINT" || "$1" == "FORMAT" || "$1" == "CONVENTIONS" ]]
            ;;
        *)
            # Full and report modes: everything
            true
            ;;
    esac
}

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

record_result() {
    local name="$1"
    local result="$2"
    if [ "$result" -eq 0 ]; then
        echo -e "  ${GREEN}✓ $name: PASSED${NC}"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo -e "  ${RED}✗ $name: FAILED${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

# Build file list for --changed mode
FILES_ARG=""
if [ "$CHANGED_ONLY" = true ]; then
    CHANGED_PY=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.py$' || true)
    if [ -z "$CHANGED_PY" ]; then
        CHANGED_PY=$(git diff --name-only --diff-filter=ACM 2>/dev/null | grep '\.py$' || true)
    fi
    if [ -z "$CHANGED_PY" ]; then
        echo -e "${YELLOW}No changed Python files found.${NC}"
        exit 0
    fi
    FILES_ARG="$CHANGED_PY"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Quality Gate — screencast-narrator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$CHANGED_ONLY" = true ]; then
    echo -e "  Scope: ${YELLOW}changed files only${NC}"
fi
if [ "$AUTO_FIX" = true ]; then
    echo -e "  Mode:  ${YELLOW}auto-fix enabled${NC}"
fi
echo ""

# ── Ruff Lint ─────────────────────────────────────────────────────────────────
if should_run LINT; then
    echo -e "${BLUE}## Ruff Lint (Static Analysis)${NC}"
    LINT_EXIT=0
    if [ "$AUTO_FIX" = true ]; then
        ruff check --fix $FILES_ARG || LINT_EXIT=$?
    else
        ruff check $FILES_ARG || LINT_EXIT=$?
    fi

    if [ "$MODE" = "report" ]; then
        # Generate report but don't fail
        LINT_EXIT=0
    fi
    record_result "Ruff Lint" "$LINT_EXIT"
    echo ""
fi

# ── Ruff Format ───────────────────────────────────────────────────────────────
if should_run FORMAT; then
    echo -e "${BLUE}## Ruff Format (Code Formatting)${NC}"
    FORMAT_EXIT=0
    if [ "$AUTO_FIX" = true ]; then
        ruff format $FILES_ARG || FORMAT_EXIT=$?
    else
        ruff format --check $FILES_ARG || FORMAT_EXIT=$?
    fi

    if [ "$MODE" = "report" ]; then
        FORMAT_EXIT=0
    fi
    record_result "Ruff Format" "$FORMAT_EXIT"
    echo ""
fi

# ── Conventions ───────────────────────────────────────────────────────────────
if should_run CONVENTIONS; then
    echo -e "${BLUE}## Code Conventions${NC}"
    CONV_EXIT=0
    python scripts/quality/conventions.py || CONV_EXIT=$?

    if [ "$MODE" = "report" ]; then
        CONV_EXIT=0
    fi
    record_result "Conventions" "$CONV_EXIT"
    echo ""
fi

# ── Pytest ────────────────────────────────────────────────────────────────────
if should_run TESTS; then
    echo -e "${BLUE}## Pytest (Unit Tests)${NC}"
    TEST_EXIT=0
    pytest --ignore=tests/test_e2e_search_screencast.py -q || TEST_EXIT=$?

    if [ "$MODE" = "report" ]; then
        TEST_EXIT=0
    fi
    record_result "Pytest" "$TEST_EXIT"
    echo ""
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
TOTAL=$((PASS_COUNT + FAIL_COUNT))
echo -e "  Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC} / $TOTAL checks"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ "$FAIL_COUNT" -gt 0 ] && [ "$MODE" != "report" ]; then
    exit 1
fi

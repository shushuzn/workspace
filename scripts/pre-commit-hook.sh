#!/usr/bin/env bash
# Auto-installed by ci-fix-runner.mjs --install-hook
# Runs pre-flight CI check on all staged files (predictive scan)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Running CI pre-flight check..."

# Get all staged files
cd "$ROOT_DIR"
STAGED=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)

if [ -z "$STAGED" ]; then
  echo "No files staged — skipping"
  exit 0
fi

# 1. Workflow-specific checks (existing ci-fix-runner logic)
STAGED_YML=$(echo "$STAGED" | grep -E '\.(yml|yaml)$' || true)
WORKFLOW_ISSUES=0

if [ -n "$STAGED_YML" ]; then
  echo "Checking workflow files..."
  if node scripts/ci-fix-runner.mjs git-check HEAD 2>/dev/null; then
    :
  else
    WORKFLOW_ISSUES=$?
  fi
fi

# 2. Predictive scan on ALL staged files (new)
echo ""
echo "Predictive scan..."
PREDICT_OUTPUT=$(node scripts/ci-fix-predictor.mjs --staged 2>&1 || true)
PREDICT_EXIT=$?

if echo "$PREDICT_OUTPUT" | grep -q "No known CI failure"; then
  PREDICT_HAS_RISK=0
elif echo "$PREDICT_OUTPUT" | grep -q "Top risk"; then
  PREDICT_HAS_RISK=1
  echo "$PREDICT_OUTPUT"
else
  PREDICT_HAS_RISK=0
fi

# Determine final exit
# P0 in workflow check → exit 2 (hard block)
# Predictor found high risk → exit 1 (warning)
# Workflow issues (non-P0) → exit 1 (warning)
if [ $WORKFLOW_ISSUES -eq 2 ]; then
  echo ""
  echo "🔴 P0 pattern in workflow — commit blocked"
  exit 2
fi

if [ $PREDICT_HAS_RISK -eq 1 ]; then
  echo ""
  echo "🟡 Predictive risk detected — review recommended (git commit --no-verify to skip)"
  exit 1
fi

if [ $WORKFLOW_ISSUES -eq 1 ]; then
  echo "🟡 P1/P2 workflow issue detected — review recommended"
  exit 1
fi

echo "✅ Pre-flight CI check passed"
exit 0

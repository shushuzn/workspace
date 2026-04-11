#!/usr/bin/env bash
# Auto-installed by ci-fix-runner.mjs --install-hook
# Runs pre-flight CI check on staged workflow files

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX_RUNNER="$SCRIPT_DIR/../node_modules/.bin/node scripts/ci-fix-runner.mjs"

# Fallback if node_modules not available
if [ ! -f "$FIX_RUNNER" ]; then
  FIX_RUNNER="node scripts/ci-fix-runner.mjs"
fi

echo "Running CI pre-flight check..."

# Get staged .yml/.yaml files
STAGED_YML=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -E '\.(yml|yaml)$' || true)

if [ -z "$STAGED_YML" ]; then
  echo "No workflow files staged — skipping CI pre-flight"
  exit 0
fi

echo "Checking staged workflow files: $STAGED_YML"

# Run git-check which compares against HEAD
cd "$(git rev-parse --show-toplevel)"
node scripts/ci-fix-runner.mjs git-check HEAD

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Pre-flight CI check passed"
elif [ $EXIT_CODE -eq 2 ]; then
  echo "🔴 P0 pattern detected — commit blocked"
else
  echo "🟡 P1/P2 pattern detected — review recommended (use --no-verify to skip)"
fi

exit $EXIT_CODE

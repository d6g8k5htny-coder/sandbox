#!/usr/bin/env bash
# Local verify only. Does not push. Scientific effect NONE.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
WORK="${1:-/tmp/pr87-apply-verify}"
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then
  TOKEN="$(gh auth token)"
fi
rm -rf "$WORK"
git clone --depth 1 -b chatgpt/downstream-crosswalk-20260925 \
  "https://x-access-token:${TOKEN}@github.com/d6g8k5htny-coder/main.git" "$WORK"
cd "$WORK"
echo "BEFORE:"
python3 tools/math_status_check.py | tail -2 || true
git apply "$ROOT/pr87_unblock.patch"
echo "AFTER:"
python3 tools/math_status_check.py | tee /tmp/math_status_after.txt
grep -q 'problems=0' /tmp/math_status_after.txt
grep -q 'lemma_closed=false' /tmp/math_status_after.txt
echo "OK apply_verify; scientific_effect=NONE"

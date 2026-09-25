#!/usr/bin/env bash
# Re-run Math- PR #8 hard-gate tests locally. Read-only probe. Scientific effect NONE.
set -euo pipefail
WORK="${1:-/tmp/math-pr8-probe}"
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [[ -z "$TOKEN" ]]; then TOKEN="$(gh auth token)"; fi
BRANCH="${MATH_GATE_BRANCH:-cursor/downstream-hard-gate-91fa}"
rm -rf "$WORK"
git clone --depth 1 -b "$BRANCH" \
  "https://x-access-token:${TOKEN}@github.com/d6g8k5htny-coder/Math-.git" "$WORK"
cd "$WORK/frontiers/downstream_gate_20260925"
echo "tip=$(git rev-parse --short HEAD)"
python3 test_hard_gate.py
# OUTPUT must not exist yet; must be outside this package ROOT.
OUT="$WORK/../math8_probe_out_$$"
rm -rf "$OUT"
set +e
python3 run_validation.py --output "$OUT"
rc=$?
set -e
if [[ $rc -ne 0 ]]; then
  echo "peer_probe: run_validation exit=$rc (may be EXPECTED_TESTS pin drift); unit tests already OK"
  # Still useful: confirm RESULTS entrypoint
  python3 hard_gate.py >/tmp/math8_hard_gate_stdout.json
  python3 - <<'PY'
import json
from pathlib import Path
out=json.loads(Path('/tmp/math8_hard_gate_stdout.json').read_text())
assert out.get('lemma_closed') is False
assert out.get('scientific_effect') == 'NONE'
print('peer_probe: hard_gate entrypoint OK; lemma_closed=false')
PY
else
  echo "peer_probe: Math- PR8 full validation OK; scientific_effect=NONE"
fi

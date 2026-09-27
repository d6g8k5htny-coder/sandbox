# Porting `formal/` from sandbox to Math- (and what goes where)

**Scientific effect: NONE.** Moving files moves no status.

## Why port

The sandbox-launched Cloud Agent that built Layer 1 measured `403 Permission denied to
cursor[bot]` on push to `trial`, `main`, `Math-` and `governance-` (2026-09-27; matches
the governance write-scope amendment). Layer 1 therefore landed here. Its intended home
is Math-, next to the informal objects it binds and the hard gate it feeds.

## Destination map

| Content | Destination | Reason |
|---|---|---|
| `formal/lean/**`, `FORMALIZATION_STATUS.json`, `SOURCE_FILES.json`, `BUILD_EVIDENCE.json`, `formal_gate.py`, `test_formal_gate.py`, `run_validation.py`, `pin_sources.py`, `lean_build_evidence.py`, `blueprint/**`, `blueprint_check.py`, `test_blueprint_check.py`, `GLOSSARY.md`, `FORMALIZATION_REVIEW_LANE.md`, `README.md` | Math- `formal/` (same relative layout) | proofs live with their informal sources; hard gate consumes the status file |
| `.github/workflows/formal-gate.yml` | Math- `.github/workflows/formal-gate.yml` | Math- already runs per-package exact-replay workflows |
| `handoff/MATH_HARD_GATE_EXTENSION.md` | implement in Math- `frontiers/downstream_gate_20260925/` | see that file |
| cross-repo pin test (status `informal_source` ↔ live Math- bytes) | trial `federation/` | trial owns cross-repo eng tests |
| museum `formalization` column, per-object alignment-review issues | main | main owns display and review discussion |
| process amendment (ladders, tokens, non-discharge rule) | governance- README "Process amendments" + `AGENTS.md` | working contract |

## Steps (any agent with Math- write; owner autonomy already granted)

```sh
# 1. Take the exact bytes from the sandbox tip you are porting.
git -C sandbox rev-parse HEAD                                   # record this OID in the PR body
git -C sandbox archive --format=tar HEAD formal .github/workflows/formal-gate.yml | tar -x -C Math-

# 2. Nothing in formal/ hard-codes 'sandbox' paths; the informal_source already points at Math-.
#    Update FORMALIZATION_STATUS.json "repository" to "d6g8k5htny-coder/Math-".

# 3. Replay everything on the final tree.
python -B -S formal/pin_sources.py --check
python -B -S formal/run_validation.py --output /tmp/formal-port-run
cd formal/lean && lake exe cache get && lake build && cd ../..
python -B -S formal/lean_build_evidence.py --check

# 4. Open a DRAFT PR; keep it draft until the Lean CI job is green; scientific Booleans stay false.
```

Then apply `handoff/agents/Math-.AGENTS.md.patch` (`git apply`), and follow
`MATH_HARD_GATE_EXTENSION.md` in a **separate** PR (it touches byte-pinned gate sources).

## Do not

* Do not copy `experiments/` or anything outside `formal/` + the workflow — sandbox stays
  private per the contract; the formal layer references only public Math- identities.
* Do not "fix" a `specified` component by adding `sorry`. It fails the gate and the kernel
  records `sorryAx`.
* Do not mark any `formalization_review` as `nonauthor-aligned` while porting. Porting is
  not review.

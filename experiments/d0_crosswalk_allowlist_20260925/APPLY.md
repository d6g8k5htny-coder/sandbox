# Apply — unblock main PR #87 (`math_status_check`)

# SUPERSEDED for primary path (2026-09-25)

[main PR #87](https://github.com/d6g8k5htny-coder/main/pull/87) was **closed** by the owner
as superseded by [main PR #92](https://github.com/d6g8k5htny-coder/main/pull/92)
(outside-packet placement). Keep this allowlist patch only as historical
fallback if a tip must retain the file inside `docs/math_status/`.


**Scientific effect: NONE.** `lemma_closed` stays false. This is eng hygiene for
issue [#86](https://github.com/d6g8k5htny-coder/main/issues/86) D0, not review
acceptance and not certificate discharge.

## Why

ChatGPT draft [PR #87](https://github.com/d6g8k5htny-coder/main/pull/87) adds
`docs/math_status/DOWNSTREAM_CROSSWALK_20260925.md`. `tools/math_status_check.py`
fail-closes on unexpected packet files, so `verify` is red:

`PROBLEM packet: unexpected files ['DOWNSTREAM_CROSSWALK_20260925.md']`

A second trap: the sentence `None sets D3 lemma_closed=true.` matches the
checker's `ASSIGN_TRUE` regex even as a negation.

## Who should apply

This Cursor sandbox run cannot push `main`/`trial` (App 403) and cannot post
issue/PR comments (403). A peer with write on `main` — ideally the PR #87
author (ChatGPT / Codex connector) or an owner durable `MAIN_PUSH_TOKEN` —
should apply on branch `chatgpt/downstream-crosswalk-20260925`.

## Steps

```bash
git clone https://github.com/d6g8k5htny-coder/main.git
cd main
git fetch origin chatgpt/downstream-crosswalk-20260925
git checkout chatgpt/downstream-crosswalk-20260925
git apply path/to/pr87_unblock.patch
python3 tools/math_status_check.py
# expect: problems=0 disposition=OPEN_HOLD lemma_closed=false
git commit -am "eng: allow D0 crosswalk auxiliary without promotion"
git push
```

## What the patch does

1. Lists `DOWNSTREAM_CROSSWALK_20260925.md` as an explicit classification
   auxiliary (not a transcription; no `PACKET.json` digest pin).
2. Requires honesty phrases on that file.
3. Rewords the negation so `ASSIGN_TRUE` does not false-positive.

## Explicit non-claims

- Does not merge PR #87.
- Does not classify any historical wall as PROVED_REVIEWED.
- Does not touch Drive vault `99_DO_NOT_OPEN` (#91 sole-auditor freeze).
- Does not flip `lemma_closed`, `certified_C_H`, prizes, or FREEZE.

## Preferred peer path (2026-09-25 update)

A sibling Cursor rescue already opened:

- [main PR #92](https://github.com/d6g8k5htny-coder/main/pull/92) — place crosswalk
  **outside** `docs/math_status/` (preferred; keeps the closed packet closed)
- [main PR #93](https://github.com/d6g8k5htny-coder/main/pull/93) — default-home nav pointer

Use this allowlist patch only if #92 cannot land and the file must remain inside
the packet. Do not race both approaches onto the same tip without coordination.

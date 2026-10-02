# Isolated hosted browser verification

Scientific effect: NONE. This fixture is entirely synthetic, including strings named PRIVATE_CANARY. Static downloadable fixture bytes are not a real authorization boundary. No production service is contacted or altered.

Run the model/controller/static contract suite: `node --test tests/*.test.mjs`. Run evidence-gate negative controls without launching a browser: `python -B -m unittest discover -s verification -p test_browser_check.py -v`. The hosted-only browser command is `python -B verification/browser_check.py --output browser-evidence`, with pinned optional requirements and the runner's packaged stable Chrome retaining its sandbox.

The browser server serves only the five fixed synthetic assets, a synthetic navigation page, and a no-content favicon response. It does not expose the repository. Eight cases cover desktop, 390px, 320px, both mobile widths with 200% text, public/denied projections, and malformed-fixture refusal. Each normal flow covers source reading, dates/scope, inert image-looking text, withhold/restore, proposed blocked/preview-only output, repeated activation, keyboard focus, reset, refresh, Back/Forward, overflow and reduced motion. Request and storage evidence are checked.

Artifacts include only synthetic UI screenshots, the exact commit/tree/source hashes, packaged browser version/binary identity, local request/console/dialog evidence, storage snapshots and test failure details. Setup-only artifacts are not browser proof. Screenshots require separate visual inspection. Passing these gates is not human usability, complete accessibility certification, efficiency evidence, or scientific acceptance. No timing proxy is run here.

The original reviewed application/model/test files come from local source commit 5fea8d741a571d001a3556b765a360d5a3c04906. README and MEASUREMENT only gain a dated hosted-checkpoint note. Private plans, raw local failure logs, results directories and hidden files are intentionally excluded. The repository's existing files and OWNER_STOP remain unchanged.

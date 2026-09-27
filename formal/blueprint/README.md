# Lean Blueprint — SIDE24 pilot

`src/content.tex` is a [leanblueprint](https://github.com/PatrickMassot/leanblueprint)
document: informal statements with `\lean{}` bindings to declarations in
`formal/lean`, `\leanok` where the proof is kernel-checked, and `\uses{}` for the
dependency graph.

Two checks keep it honest:

* `python -B -S formal/blueprint_check.py` — every `\lean{}` name must be a component
  in `FORMALIZATION_STATUS.json`; `\leanok` is allowed only on `kernel-checked`
  components; every formalized component must appear. Run in CI.
* `formal_gate.py` binds each component's `lean_statement` verbatim to the module
  bytes, so the Lean statement cannot drift from what the blueprint aligned.

To render (optional, not required by CI):

```sh
pip install leanblueprint            # needs a TeX distribution + plasTeX
cd formal/blueprint && leanblueprint pdf && leanblueprint web
```

`lean_decls` lists the bound declarations for `lake exe checkdecls` if a future
change adds the `checkdecls` dependency to `lakefile.toml`.

Scientific effect: NONE.

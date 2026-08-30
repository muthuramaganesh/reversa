# Requirements — CLI

CLI — purpose reconstructed from 18 claims (18 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `not files` in cmd_status.  
  _claims: C-313 · evidence: reversa/cli.py:54_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `args.verbose or f.status != "intact"` in cmd_status.  
  _claims: C-314 · evidence: reversa/cli.py:60_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `st.exists(` in cmd_status.  
  _claims: C-315 · evidence: reversa/cli.py:64_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `not o.registry.claims` in cmd_migrate.  
  _claims: C-316 · evidence: reversa/cli.py:95_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `q.id == args.id` in cmd_answer.  
  _claims: C-317 · evidence: reversa/cli.py:107_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `g.id == args.id` in cmd_answer.  
  _claims: C-318 · evidence: reversa/cli.py:111_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `not hit` in cmd_answer.  
  _claims: C-319 · evidence: reversa/cli.py:115_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

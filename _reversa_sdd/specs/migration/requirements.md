# Requirements — MIGRATION

MIGRATION — purpose reconstructed from 9 claims (9 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `c["kind"] not in {k.value for k in _SCEN_KINDS} or c["confidence"] == "gap"` in heuristic.  
  _claims: C-396 · evidence: reversa/agents/migration.py:54_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `c["kind"] == "exception"` in heuristic.  
  _claims: C-397 · evidence: reversa/agents/migration.py:58_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `n_inf` in heuristic.  
  _claims: C-398 · evidence: reversa/agents/migration.py:83_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

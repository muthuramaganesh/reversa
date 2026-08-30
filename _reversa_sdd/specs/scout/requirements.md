# Requirements — SCOUT

SCOUT — purpose reconstructed from 15 claims (15 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `f["path"] not in facts_by` in heuristic.  
  _claims: C-456 · evidence: reversa/agents/scout.py:45_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `prog` in heuristic.  
  _claims: C-457 · evidence: reversa/agents/scout.py:57_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `f["path"] not in facts_by` in heuristic.  
  _claims: C-458 · evidence: reversa/agents/scout.py:65_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `tgt in seen` in heuristic.  
  _claims: C-459 · evidence: reversa/agents/scout.py:72_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `c.kind == "call" and tgt not in known_units` in heuristic.  
  _claims: C-460 · evidence: reversa/agents/scout.py:77_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `not files` in run.  
  _claims: C-461 · evidence: reversa/agents/scout.py:108_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `ev` in _unit_for.  
  _claims: C-462 · evidence: reversa/agents/scout.py:128_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `f in u.files` in _unit_for.  
  _claims: C-463 · evidence: reversa/agents/scout.py:131_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

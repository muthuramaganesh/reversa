# Requirements — WRITER

WRITER — purpose reconstructed from 8 claims (8 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `c["kind"] in {k.value for k in _REQ_KINDS}` in heuristic.  
  _claims: C-464 · evidence: reversa/agents/writer.py:51_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `not cids` in run.  
  _claims: C-465 · evidence: reversa/agents/writer.py:102_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

# Requirements — REVIEWER

REVIEWER — purpose reconstructed from 16 claims (16 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `c["id"] in answered` in heuristic.  
  _claims: C-446 · evidence: reversa/agents/reviewer.py:52_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `c.confidence == Confidence.GAP` in run.  
  _claims: C-447 · evidence: reversa/agents/reviewer.py:64_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `not c.evidence` in run.  
  _claims: C-448 · evidence: reversa/agents/reviewer.py:66_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run.  
  _claims: C-449 · evidence: reversa/agents/reviewer.py:67_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `not any(ok for ok, _ in results` in run.  
  _claims: C-450 · evidence: reversa/agents/reviewer.py:73_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run.  
  _claims: C-451 · evidence: reversa/agents/reviewer.py:74_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `not c` in run.  
  _claims: C-452 · evidence: reversa/agents/reviewer.py:97_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `new == Confidence.CONFIRMED and not (c.evidence and any(` in run.  
  _claims: C-453 · evidence: reversa/agents/reviewer.py:103_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `new != c.confidence` in run.  
  _claims: C-454 · evidence: reversa/agents/reviewer.py:106_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `new == Confidence.GAP` in run.  
  _claims: C-455 · evidence: reversa/agents/reviewer.py:109_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

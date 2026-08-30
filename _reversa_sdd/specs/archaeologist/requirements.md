# Requirements — ARCHAEOLOGIST

ARCHAEOLOGIST — purpose reconstructed from 13 claims (13 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `paras` in heuristic.  
  _claims: C-365 · evidence: reversa/agents/archaeologist.py:39_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `lk` in heuristic.  
  _claims: C-366 · evidence: reversa/agents/archaeologist.py:56_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `ws` in heuristic.  
  _claims: C-367 · evidence: reversa/agents/archaeologist.py:62_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `acc` in heuristic.  
  _claims: C-368 · evidence: reversa/agents/archaeologist.py:77_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `not any(x.name == p.name for x in paras` in heuristic.  
  _claims: C-369 · evidence: reversa/agents/archaeologist.py:83_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `not paras and not ff.of("select") and not ws` in heuristic.  
  _claims: C-370 · evidence: reversa/agents/archaeologist.py:87_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `out.get("summary") and not u.description` in run.  
  _claims: C-371 · evidence: reversa/agents/archaeologist.py:108_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

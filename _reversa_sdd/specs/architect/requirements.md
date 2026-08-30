# Requirements — ARCHITECT

ARCHITECT — purpose reconstructed from 18 claims (18 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `entry` in heuristic.  
  _claims: C-372 · evidence: reversa/agents/architect.py:42_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `shared` in heuristic.  
  _claims: C-373 · evidence: reversa/agents/architect.py:45_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `rest` in heuristic.  
  _claims: C-374 · evidence: reversa/agents/architect.py:48_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `n >= 2` in heuristic.  
  _claims: C-375 · evidence: reversa/agents/architect.py:54_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `len(users) >= 2` in heuristic.  
  _claims: C-376 · evidence: reversa/agents/architect.py:59_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `not entry` in heuristic.  
  _claims: C-377 · evidence: reversa/agents/architect.py:68_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `c.kind == ClaimKind.DEPENDENCY` in run.  
  _claims: C-378 · evidence: reversa/agents/architect.py:79_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `m` in run.  
  _claims: C-379 · evidence: reversa/agents/architect.py:81_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `c.kind == ClaimKind.DATA` in run.  
  _claims: C-380 · evidence: reversa/agents/architect.py:83_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `m` in run.  
  _claims: C-381 · evidence: reversa/agents/architect.py:85_
- ✅ **REQ-11** The reimplementation shall preserve: Branch guarded by `a != b` in _write.  
  _claims: C-382 · evidence: reversa/agents/architect.py:151_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

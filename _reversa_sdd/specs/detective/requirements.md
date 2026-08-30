# Requirements — DETECTIVE

DETECTIVE — purpose reconstructed from 16 claims (16 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `near and _CMP.search(text` in heuristic.  
  _claims: C-386 · evidence: reversa/agents/detective.py:59_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `n in ("0", "1") or n in seen_consts` in heuristic.  
  _claims: C-387 · evidence: reversa/agents/detective.py:66_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `cases` in heuristic.  
  _claims: C-388 · evidence: reversa/agents/detective.py:81_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `not any(0 < m.line - c.line <= 4 for c in ff.of("condition")` in heuristic.  
  _claims: C-389 · evidence: reversa/agents/detective.py:84_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `re.search(r"(senha|pin|pass|auth|login|usuario|user)", a.name, re.I` in heuristic.  
  _claims: C-390 · evidence: reversa/agents/detective.py:90_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `not ff.of("condition") and not ff.of("dispatch"` in heuristic.  
  _claims: C-391 · evidence: reversa/agents/detective.py:98_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `isinstance(idx, int) and 0 <= idx < len(made` in run.  
  _claims: C-392 · evidence: reversa/agents/detective.py:124_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `not cs` in _write.  
  _claims: C-393 · evidence: reversa/agents/detective.py:137_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `not sub` in _write.  
  _claims: C-394 · evidence: reversa/agents/detective.py:142_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `st` in _write.  
  _claims: C-395 · evidence: reversa/agents/detective.py:150_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

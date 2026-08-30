# Requirements — ENGINES

ENGINES — purpose reconstructed from 7 claims (7 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `any((root / m).exists() for m in e.markers` in detect_engines.  
  _claims: C-327 · evidence: reversa/engines.py:57_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `keys` in resolve_engines.  
  _claims: C-328 · evidence: reversa/engines.py:64_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `unknown` in resolve_engines.  
  _claims: C-329 · evidence: reversa/engines.py:66_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

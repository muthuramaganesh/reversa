# Requirements — MANIFEST

MANIFEST — purpose reconstructed from 11 claims (11 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `self.path.exists(` in load.  
  _claims: C-344 · evidence: reversa/manifest.py:46_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `not p.exists(` in classify.  
  _claims: C-345 · evidence: reversa/manifest.py:72_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `fs.path == rel` in status_of.  
  _claims: C-346 · evidence: reversa/manifest.py:82_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

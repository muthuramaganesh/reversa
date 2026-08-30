# Requirements — PROJECT

PROJECT — purpose reconstructed from 9 claims (9 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `lang is None` in inventory.  
  _claims: C-361 · evidence: reversa/project.py:56_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `size > MAX_FILE_BYTES` in inventory.  
  _claims: C-362 · evidence: reversa/project.py:62_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `rel not in self._cache` in lines.  
  _claims: C-363 · evidence: reversa/project.py:69_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `max_lines` in numbered.  
  _claims: C-364 · evidence: reversa/project.py:83_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

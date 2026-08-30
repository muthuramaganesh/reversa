# Requirements — CONFIDENCE

CONFIDENCE — purpose reconstructed from 13 claims (13 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `self.total == 0` in index.  
  _claims: C-320 · evidence: reversa/confidence.py:29_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `not claims` in traceability_density.  
  _claims: C-321 · evidence: reversa/confidence.py:53_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `not p.exists(` in verify_evidence.  
  _claims: C-322 · evidence: reversa/confidence.py:73_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `ev.line_start < 1 or ev.line_start > len(lines` in verify_evidence.  
  _claims: C-323 · evidence: reversa/confidence.py:79_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `not ev.excerpt.strip(` in verify_evidence.  
  _claims: C-324 · evidence: reversa/confidence.py:81_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `_norm(ev.excerpt) in region` in verify_evidence.  
  _claims: C-325 · evidence: reversa/confidence.py:86_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `head and head in region` in verify_evidence.  
  _claims: C-326 · evidence: reversa/confidence.py:90_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

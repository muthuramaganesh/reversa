# Requirements — MODELS

MODELS — purpose reconstructed from 17 claims (17 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `self.line_start == self.line_end` in ref.  
  _claims: C-347 · evidence: reversa/models.py:57_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `m` in next_id.  
  _claims: C-348 · evidence: reversa/models.py:170_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `not isinstance(kw.get("kind"), ClaimKind` in add_claim.  
  _claims: C-349 · evidence: reversa/models.py:175_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `not isinstance(kw.get("confidence"), Confidence` in add_claim.  
  _claims: C-350 · evidence: reversa/models.py:180_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `g.unit == kw.get("unit") and g.description == kw.get("description"` in add_gap.  
  _claims: C-351 · evidence: reversa/models.py:191_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `not isinstance(sev, Severity` in add_gap.  
  _claims: C-352 · evidence: reversa/models.py:194_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `q.unit == kw.get("unit") and q.question == kw.get("question"` in add_question.  
  _claims: C-353 · evidence: reversa/models.py:206_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `c not in q.related_claims` in add_question.  
  _claims: C-354 · evidence: reversa/models.py:208_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `not path.exists(` in load.  
  _claims: C-355 · evidence: reversa/models.py:236_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

# Requirements — BASE

BASE — purpose reconstructed from 30 claims (29 confirmed, 1 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `self.units_filter` in selected_units.  
  _claims: C-383 · evidence: reversa/agents/base.py:58_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `not stmt` in add_claims.  
  _claims: C-384 · evidence: reversa/agents/base.py:102_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `conf == Confidence.CONFIRMED and not ev` in add_claims.  
  _claims: C-385 · evidence: reversa/agents/base.py:114_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `TYPE_CHECKING:  # pragma: no cover`.  
  _claims: C-470 · evidence: reversa/llm/base.py:8_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `start == -1 or end == -1` in strip_json.  
  _claims: C-471 · evidence: reversa/llm/base.py:26_
- 🟡 **REQ-6** The reimplementation should (to be confirmed) preserve: When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply".  
  _claims: C-472 · evidence: reversa/llm/base.py:26-27_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `name == "heuristic"` in get_backend.  
  _claims: C-473 · evidence: reversa/llm/base.py:32_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `name == "anthropic"` in get_backend.  
  _claims: C-474 · evidence: reversa/llm/base.py:35_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `name == "auto"` in get_backend.  
  _claims: C-475 · evidence: reversa/llm/base.py:38_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `os.environ.get("ANTHROPIC_API_KEY"` in get_backend.  
  _claims: C-476 · evidence: reversa/llm/base.py:40_
- ✅ **REQ-11** The reimplementation shall preserve: BASE can emit the message "unknown backend: {name}".  
  _claims: C-477 · evidence: reversa/llm/base.py:45_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

# Requirements — ANTHROPIC_BACKEND

ANTHROPIC_BACKEND — purpose reconstructed from 13 claims (13 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `not self.api_key` in __init__.  
  _claims: C-466 · evidence: reversa/llm/anthropic_backend.py:33_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `b.get("type") == "text"` in _call.  
  _claims: C-467 · evidence: reversa/llm/anthropic_backend.py:54_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `e.code in (429, 500, 502, 503, 529` in _call.  
  _claims: C-468 · evidence: reversa/llm/anthropic_backend.py:57_
- ✅ **REQ-4** The reimplementation shall preserve: ANTHROPIC_BACKEND can emit the message "Anthropic API failed after retries: {last}".  
  _claims: C-469 · evidence: reversa/llm/anthropic_backend.py:64_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

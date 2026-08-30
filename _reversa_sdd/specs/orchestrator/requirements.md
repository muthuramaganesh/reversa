# Requirements — ORCHESTRATOR

ORCHESTRATOR — purpose reconstructed from 19 claims (19 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `path.exists(` in load.  
  _claims: C-356 · evidence: reversa/orchestrator.py:38_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `only` in run.  
  _claims: C-357 · evidence: reversa/orchestrator.py:66_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `not resume and team in ("discovery", "all") and not only` in run.  
  _claims: C-358 · evidence: reversa/orchestrator.py:68_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `not self.state.started` in run.  
  _claims: C-359 · evidence: reversa/orchestrator.py:71_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `resume and not only and st.get("status") == "done"` in run.  
  _claims: C-360 · evidence: reversa/orchestrator.py:79_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

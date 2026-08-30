# Requirements — __MAIN__

__MAIN__ — purpose reconstructed from 3 claims (2 confirmed, 1 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `__name__ == "__main__"`.  
  _claims: C-266 · evidence: reversa/__main__.py:3_
- 🟡 **REQ-2** The reimplementation should (to be confirmed) preserve: When `__name__ == "__main__"` holds, the operation is rejected with message "SystemExit(main())".  
  _claims: C-267 · evidence: reversa/__main__.py:3-4_

## Open gaps affecting this unit

- ⛔ **GAP-002** (moderate) No recognisable structure extracted from reversa/__main__.py; manual reading required.

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

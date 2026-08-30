# Requirements — EXTRATO

EXTRATO — purpose reconstructed from 11 claims (10 confirmed, 1 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `WS-QTD = 0` in MAIN.  
  _claims: C-251 · evidence: examples/legacy_atm/EXTRATO.cbl:34_
- 🟡 **REQ-2** The reimplementation should (to be confirmed) preserve: When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS".  
  _claims: C-252 · evidence: examples/legacy_atm/EXTRATO.cbl:34-35_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `MOV-CONTA = LK-CONTA` in MOSTRA.  
  _claims: C-253 · evidence: examples/legacy_atm/EXTRATO.cbl:40_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

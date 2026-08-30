# Requirements — CONTA

CONTA — purpose reconstructed from 28 claims (22 confirmed, 6 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE.  
  _claims: C-042 · evidence: CONTA.cbl:64_
- 🟡 **REQ-2** The reimplementation should (to be confirmed) preserve: When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO".  
  _claims: C-043 · evidence: CONTA.cbl:64-65_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `WS-VALOR > LK-SALDO` in SAQUE.  
  _claims: C-044 · evidence: CONTA.cbl:68_
- 🟡 **REQ-4** The reimplementation should (to be confirmed) preserve: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE".  
  _claims: C-045 · evidence: CONTA.cbl:68-69_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `FUNCTION MOD(WS-VALOR, 10) NOT = 0` in SAQUE.  
  _claims: C-046 · evidence: CONTA.cbl:72_
- 🟡 **REQ-6** The reimplementation should (to be confirmed) preserve: When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10".  
  _claims: C-047 · evidence: CONTA.cbl:72-73_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `WS-VALOR = 0` in DEPOSITO.  
  _claims: C-048 · evidence: CONTA.cbl:82_
- 🟡 **REQ-8** The reimplementation should (to be confirmed) preserve: When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO".  
  _claims: C-049 · evidence: CONTA.cbl:82-83_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `WS-VALOR > LK-SALDO` in TRANSFERENCIA.  
  _claims: C-050 · evidence: CONTA.cbl:95_
- 🟡 **REQ-10** The reimplementation should (to be confirmed) preserve: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE".  
  _claims: C-051 · evidence: CONTA.cbl:95-96_
- ✅ **REQ-11** The reimplementation shall preserve: Branch guarded by `CLI-STATUS = 'B'` in TRANSFERENCIA.  
  _claims: C-052 · evidence: CONTA.cbl:105_
- 🟡 **REQ-12** The reimplementation should (to be confirmed) preserve: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA".  
  _claims: C-053 · evidence: CONTA.cbl:105-106_
- ✅ **REQ-13** The reimplementation shall preserve: CONTA dispatches on `LK-OP` with cases: 'S', 'Q', 'D', 'T'.  
  _claims: C-054 · evidence: CONTA.cbl:46-53_
- ✅ **REQ-14** The reimplementation shall preserve: CONTA can emit the message "CONTA DESTINO INEXISTENTE".  
  _claims: C-055 · evidence: CONTA.cbl:102_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

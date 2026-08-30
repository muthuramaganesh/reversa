# Requirements — MENU

MENU — purpose reconstructed from 20 claims (17 confirmed, 3 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `WS-TENTATIVAS >= 3` in MAIN.  
  _claims: C-254 · evidence: examples/legacy_atm/MENU.cbl:31_
- 🟡 **REQ-2** The reimplementation should (to be confirmed) preserve: When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO".  
  _claims: C-255 · evidence: examples/legacy_atm/MENU.cbl:31-32_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `CLI-STATUS = 'B'` in LOGIN.  
  _claims: C-256 · evidence: examples/legacy_atm/MENU.cbl:50_
- 🟡 **REQ-4** The reimplementation should (to be confirmed) preserve: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA".  
  _claims: C-257 · evidence: examples/legacy_atm/MENU.cbl:50-51_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `WS-SENHA NOT = CLI-SENHA` in LOGIN.  
  _claims: C-258 · evidence: examples/legacy_atm/MENU.cbl:57_
- 🟡 **REQ-6** The reimplementation should (to be confirmed) preserve: When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA".  
  _claims: C-259 · evidence: examples/legacy_atm/MENU.cbl:57-59_
- ✅ **REQ-7** The reimplementation shall preserve: MENU dispatches on `WS-OPCAO` with cases: '1', '2', '3', '4', '5', '9', OTHER.  
  _claims: C-260 · evidence: examples/legacy_atm/MENU.cbl:65-78_
- ✅ **REQ-8** The reimplementation shall preserve: MENU can emit the message "CONTA INVALIDA".  
  _claims: C-261 · evidence: examples/legacy_atm/MENU.cbl:47_
- ✅ **REQ-9** The reimplementation shall preserve: MENU can emit the message "OPCAO INVALIDA".  
  _claims: C-262 · evidence: examples/legacy_atm/MENU.cbl:79_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

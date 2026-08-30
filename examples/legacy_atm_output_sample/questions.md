# Questions for the system owner

15 questions. Answers feed back into the specification: answering a question
lets the reviewer confirm or drop the related inferred claims.

### Q-001 (CONTA)

**Q:** In CONTA, the constant 10 appears in `FUNCTION MOD(WS-VALOR, 10) NOT = 0` (CONTA.cbl:72). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-047

**A:** _(pending)_

### Q-002 (MENU)

**Q:** In MENU, the constant 3 appears in `WS-TENTATIVAS >= 3` (MENU.cbl:31). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-060

**A:** _(pending)_

### Q-003 (KBDREAD)

**Q:** In KBDREAD, the constant 9 appears in `c < '0' || c > '9') { i--; continue; }` (kbdread.c:14). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-070

**A:** _(pending)_

### Q-004 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-043

**A:** _(pending)_

### Q-005 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-045, C-051

**A:** _(pending)_

### Q-006 (CONTA)

**Q:** Please confirm or correct: When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-047

**A:** _(pending)_

### Q-007 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-049

**A:** _(pending)_

### Q-008 (CONTA)

**Q:** Please confirm or correct: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-053

**A:** _(pending)_

### Q-009 (EXTRATO)

**Q:** Please confirm or correct: When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-057

**A:** _(pending)_

### Q-010 (MENU)

**Q:** Please confirm or correct: When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-060

**A:** _(pending)_

### Q-011 (MENU)

**Q:** Please confirm or correct: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-062

**A:** _(pending)_

### Q-012 (MENU)

**Q:** Please confirm or correct: When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-064

**A:** _(pending)_

### Q-013 (project)

**Q:** Please confirm or correct: UTIL is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-071

**A:** _(pending)_

### Q-014 (project)

**Q:** Please confirm or correct: Data store 'CLIENTES' is shared by CONTA, MENU; they are coupled through the file layout, not through calls.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-072

**A:** _(pending)_

### Q-015 (project)

**Q:** Please confirm or correct: Data store 'MOVTOS' is shared by CONTA, EXTRATO; they are coupled through the file layout, not through calls.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-073

**A:** _(pending)_

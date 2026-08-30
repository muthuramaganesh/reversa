# Questions for the system owner

50 questions. Answers feed back into the specification: answering a question
lets the reviewer confirm or drop the related inferred claims.

### Q-001 (CONTA)

**Q:** In CONTA, the constant 10 appears in `FUNCTION MOD(WS-VALOR, 10) NOT = 0` (examples/legacy_atm/CONTA.cbl:72). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-242

**A:** _(pending)_

### Q-002 (MENU)

**Q:** In MENU, the constant 3 appears in `WS-TENTATIVAS >= 3` (examples/legacy_atm/MENU.cbl:31). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-255

**A:** _(pending)_

### Q-003 (KBDREAD)

**Q:** In KBDREAD, the constant 9 appears in `c < '0' || c > '9') { i--; continue; }` (examples/legacy_atm/kbdread.c:14). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-265

**A:** _(pending)_

### Q-004 (ANALYSIS)

**Q:** In ANALYSIS, the constant 3 appears in `m and m.group(3` (reversa/analysis.py:129). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-279

**A:** _(pending)_

### Q-005 (ANALYSIS)

**Q:** In ANALYSIS, the constant 01 appears in `lvl == "01"` (reversa/analysis.py:131). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-280

**A:** _(pending)_

### Q-006 (ANALYSIS)

**Q:** In ANALYSIS, the constant 9 appears in `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` (reversa/analysis.py:257). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-304

**A:** _(pending)_

### Q-007 (ANALYSIS)

**Q:** In ANALYSIS, the constant 0123456789 appears in `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` (reversa/analysis.py:257). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-304

**A:** _(pending)_

### Q-008 (ARCHITECT)

**Q:** In ARCHITECT, the constant 2 appears in `n >= 2` (reversa/agents/architect.py:54). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-375

**A:** _(pending)_

### Q-009 (DETECTIVE)

**Q:** In DETECTIVE, the constant 4 appears in `not any(0 < m.line - c.line <= 4 for c in ff.of("condition")` (reversa/agents/detective.py:84). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-389

**A:** _(pending)_

### Q-010 (PROCESS)

**Q:** In PROCESS, the constant 4 appears in `words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"` (reversa/agents/process.py:27). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-399

**A:** _(pending)_

### Q-011 (PROCESS)

**Q:** In PROCESS, the constant 6 appears in `depth > 6 or (path, para) in seen` (reversa/agents/process.py:273). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-418

**A:** _(pending)_

### Q-012 (PROCESS)

**Q:** In PROCESS, the constant 60 appears in `len(out_t) > 60` (reversa/agents/process.py:539). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-444

**A:** _(pending)_

### Q-013 (ANTHROPIC_BACKEND)

**Q:** In ANTHROPIC_BACKEND, the constant 429 appears in `e.code in (429, 500, 502, 503, 529` (reversa/llm/anthropic_backend.py:57). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-468

**A:** _(pending)_

### Q-014 (ANTHROPIC_BACKEND)

**Q:** In ANTHROPIC_BACKEND, the constant 500 appears in `e.code in (429, 500, 502, 503, 529` (reversa/llm/anthropic_backend.py:57). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-468

**A:** _(pending)_

### Q-015 (ANTHROPIC_BACKEND)

**Q:** In ANTHROPIC_BACKEND, the constant 502 appears in `e.code in (429, 500, 502, 503, 529` (reversa/llm/anthropic_backend.py:57). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-468

**A:** _(pending)_

### Q-016 (ANTHROPIC_BACKEND)

**Q:** In ANTHROPIC_BACKEND, the constant 503 appears in `e.code in (429, 500, 502, 503, 529` (reversa/llm/anthropic_backend.py:57). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-468

**A:** _(pending)_

### Q-017 (ANTHROPIC_BACKEND)

**Q:** In ANTHROPIC_BACKEND, the constant 529 appears in `e.code in (429, 500, 502, 503, 529` (reversa/llm/anthropic_backend.py:57). Is it a business limit, a technical constant, or configurable?

_Why it matters:_ Limits must be preserved (or consciously changed) in any reimplementation.  
_Related claims:_ C-468

**A:** _(pending)_

### Q-018 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-238

**A:** _(pending)_

### Q-019 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-240, C-246

**A:** _(pending)_

### Q-020 (CONTA)

**Q:** Please confirm or correct: When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-242

**A:** _(pending)_

### Q-021 (CONTA)

**Q:** Please confirm or correct: When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-244

**A:** _(pending)_

### Q-022 (CONTA)

**Q:** Please confirm or correct: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-248

**A:** _(pending)_

### Q-023 (EXTRATO)

**Q:** Please confirm or correct: When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-252

**A:** _(pending)_

### Q-024 (MENU)

**Q:** Please confirm or correct: When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-255

**A:** _(pending)_

### Q-025 (MENU)

**Q:** Please confirm or correct: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-257

**A:** _(pending)_

### Q-026 (MENU)

**Q:** Please confirm or correct: When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-259

**A:** _(pending)_

### Q-027 (__MAIN__)

**Q:** Please confirm or correct: When `__name__ == "__main__"` holds, the operation is rejected with message "SystemExit(main())".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-267

**A:** _(pending)_

### Q-028 (BASE)

**Q:** Please confirm or correct: When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply".

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-472

**A:** _(pending)_

### Q-029 (project)

**Q:** Please confirm or correct: DATACLASSES is a shared utility: 7 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-479

**A:** _(pending)_

### Q-030 (project)

**Q:** Please confirm or correct: RE is a shared utility: 7 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-480

**A:** _(pending)_

### Q-031 (project)

**Q:** Please confirm or correct: __FUTURE__ is a shared utility: 20 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-481

**A:** _(pending)_

### Q-032 (project)

**Q:** Please confirm or correct: .BASE is a shared utility: 11 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-482

**A:** _(pending)_

### Q-033 (project)

**Q:** Please confirm or correct: JSON is a shared utility: 9 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-483

**A:** _(pending)_

### Q-034 (project)

**Q:** Please confirm or correct: OS is a shared utility: 3 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-484

**A:** _(pending)_

### Q-035 (project)

**Q:** Please confirm or correct: TIME is a shared utility: 3 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-485

**A:** _(pending)_

### Q-036 (project)

**Q:** Please confirm or correct: TYPING is a shared utility: 14 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-486

**A:** _(pending)_

### Q-037 (project)

**Q:** Please confirm or correct: . is a shared utility: 11 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-487

**A:** _(pending)_

### Q-038 (project)

**Q:** Please confirm or correct: COLLECTIONS is a shared utility: 4 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-488

**A:** _(pending)_

### Q-039 (project)

**Q:** Please confirm or correct: PATHLIB is a shared utility: 13 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-489

**A:** _(pending)_

### Q-040 (project)

**Q:** Please confirm or correct: .CONFIDENCE is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-490

**A:** _(pending)_

### Q-041 (project)

**Q:** Please confirm or correct: .LLM is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-491

**A:** _(pending)_

### Q-042 (project)

**Q:** Please confirm or correct: .MODELS is a shared utility: 4 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-492

**A:** _(pending)_

### Q-043 (project)

**Q:** Please confirm or correct: .ORCHESTRATOR is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-493

**A:** _(pending)_

### Q-044 (project)

**Q:** Please confirm or correct: PYTEST is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-494

**A:** _(pending)_

### Q-045 (project)

**Q:** Please confirm or correct: SHUTIL is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-495

**A:** _(pending)_

### Q-046 (project)

**Q:** Please confirm or correct: UTIL is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-496

**A:** _(pending)_

### Q-047 (project)

**Q:** Please confirm or correct: .AGENTS is a shared utility: 2 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-497

**A:** _(pending)_

### Q-048 (project)

**Q:** Please confirm or correct: REVERSA is a shared utility: 5 units depend on it, so changes to it have system-wide impact.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-498

**A:** _(pending)_

### Q-049 (project)

**Q:** Please confirm or correct: Data store 'CLIENTES' is shared by CONTA, MENU; they are coupled through the file layout, not through calls.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-499

**A:** _(pending)_

### Q-050 (project)

**Q:** Please confirm or correct: Data store 'MOVTOS' is shared by CONTA, EXTRATO; they are coupled through the file layout, not through calls.

_Why it matters:_ This claim is inferred from patterns, not directly evidenced.  
_Related claims:_ C-500

**A:** _(pending)_

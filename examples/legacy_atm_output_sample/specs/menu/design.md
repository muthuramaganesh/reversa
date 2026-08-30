# Design — MENU

## Structure
Unit MENU is a COBOL program declared in MENU.cbl. MENU is organised into 3 paragraphs: MAIN, LOGIN, LOOP-MENU. MENU reads interactive input into: WS-CONTA, WS-OPCAO.

## Data
MENU declares file CLIENTES assigned to 'CLIENTES' (INDEXED). MENU defines file record description CLIENTES. MENU working storage has 6 top-level records: WS-CONTA, WS-SENHA, WS-TENTATIVAS, WS-OPCAO, WS-FIM, WS-FS. MENU performs CLOSE, OPEN I-O, READ on CLIENTES. MENU performs REWRITE on CLI-REG.

## Dependencies
MENU depends on KBDREAD (call). MENU depends on CONTA (call). MENU depends on EXTRATO (call).

_Derived from claims: C-003, C-007, C-008, C-009, C-031, C-032, C-033, C-034, C-035, C-036, C-037_

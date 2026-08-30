# Design — MENU

## Structure
Unit MENU is a COBOL program declared in examples/legacy_atm/MENU.cbl. MENU is organised into 3 paragraphs: MAIN, LOGIN, LOOP-MENU. MENU reads interactive input into: WS-CONTA, WS-OPCAO.

## Data
MENU declares file CLIENTES assigned to 'CLIENTES' (INDEXED). MENU defines file record description CLIENTES. MENU working storage has 6 top-level records: WS-CONTA, WS-SENHA, WS-TENTATIVAS, WS-OPCAO, WS-FIM, WS-FS. MENU performs CLOSE, OPEN I-O, READ on CLIENTES. MENU performs REWRITE on CLI-REG.

## Dependencies
MENU depends on KBDREAD (call). MENU depends on CONTA (call). MENU depends on EXTRATO (call).

_Derived from claims: C-003, C-007, C-008, C-009, C-197, C-198, C-199, C-200, C-201, C-202, C-203_

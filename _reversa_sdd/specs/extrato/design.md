# Design — EXTRATO

## Structure
Unit EXTRATO is a COBOL program declared in examples/legacy_atm/EXTRATO.cbl. EXTRATO is organised into 2 paragraphs: MAIN, MOSTRA. EXTRATO receives parameters through LINKAGE: LK-CONTA.

## Data
EXTRATO declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). EXTRATO defines file record description MOVTOS. EXTRATO working storage has 4 top-level records: WS-EOF, WS-QTD, WS-VALOR-FMT, WS-MAX-LINHAS. EXTRATO performs CLOSE, OPEN INPUT, READ on MOVTOS.

## Dependencies
EXTRATO depends on UTIL (call).

_Derived from claims: C-002, C-006, C-191, C-192, C-193, C-194, C-195, C-196_

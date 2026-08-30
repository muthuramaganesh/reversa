# Design — CONTA

## Structure
Unit CONTA is a COBOL program declared in CONTA.cbl. CONTA is organised into 6 paragraphs: MAIN, SALDO, SAQUE, DEPOSITO, TRANSFERENCIA, GRAVA. CONTA receives parameters through LINKAGE: LK-OP, LK-CLI. CONTA reads interactive input into: WS-DESTINO, WS-VALOR.

## Data
CONTA declares file CLIENTES assigned to 'CLIENTES' (INDEXED). CONTA declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). CONTA defines file record description CLIENTES. CONTA defines file record description MOVTOS. CONTA working storage has 5 top-level records: WS-VALOR, WS-DESTINO, WS-SALDO-FMT, WS-LIMITE-SAQUE, WS-TARIFA-TRANSF. CONTA performs CLOSE, OPEN I-O, READ on CLIENTES. CONTA performs CLOSE, OPEN EXTEND on MOVTOS. CONTA performs REWRITE on CLI-REG. CONTA performs WRITE on MOV-REG.

## Dependencies
CONTA depends on UTIL (call).

_Derived from claims: C-001, C-005, C-013, C-014, C-015, C-016, C-017, C-018, C-019, C-020, C-021, C-022, C-023, C-024_

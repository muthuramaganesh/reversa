# Technical analysis — EXTRATO

EXTRATO has 2 structural and 4 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-025 | structure | confirmed | EXTRATO is organised into 2 paragraphs: MAIN, MOSTRA. | EXTRATO.cbl:25-39 |
| C-026 | data | confirmed | EXTRATO declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). | EXTRATO.cbl:7 |
| C-027 | data | confirmed | EXTRATO defines file record description MOVTOS. | EXTRATO.cbl:11 |
| C-028 | structure | confirmed | EXTRATO receives parameters through LINKAGE: LK-CONTA. | EXTRATO.cbl:23 |
| C-029 | data | confirmed | EXTRATO working storage has 4 top-level records: WS-EOF, WS-QTD, WS-VALOR-FMT, WS-MAX-LINHAS. | EXTRATO.cbl:18-21 |
| C-030 | data | confirmed | EXTRATO performs CLOSE, OPEN INPUT, READ on MOVTOS. | EXTRATO.cbl:26 |

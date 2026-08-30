# Technical analysis — EXTRATO

EXTRATO has 2 structural and 4 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-191 | structure | confirmed | EXTRATO is organised into 2 paragraphs: MAIN, MOSTRA. | examples/legacy_atm/EXTRATO.cbl:25-39 |
| C-192 | data | confirmed | EXTRATO declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). | examples/legacy_atm/EXTRATO.cbl:7 |
| C-193 | data | confirmed | EXTRATO defines file record description MOVTOS. | examples/legacy_atm/EXTRATO.cbl:11 |
| C-194 | structure | confirmed | EXTRATO receives parameters through LINKAGE: LK-CONTA. | examples/legacy_atm/EXTRATO.cbl:23 |
| C-195 | data | confirmed | EXTRATO working storage has 4 top-level records: WS-EOF, WS-QTD, WS-VALOR-FMT, WS-MAX-LINHAS. | examples/legacy_atm/EXTRATO.cbl:18-21 |
| C-196 | data | confirmed | EXTRATO performs CLOSE, OPEN INPUT, READ on MOVTOS. | examples/legacy_atm/EXTRATO.cbl:26 |

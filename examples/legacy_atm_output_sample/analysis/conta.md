# Technical analysis — CONTA

CONTA has 3 structural and 9 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-013 | structure | confirmed | CONTA is organised into 6 paragraphs: MAIN, SALDO, SAQUE, DEPOSITO, TRANSFERENCIA, GRAVA. | CONTA.cbl:43-115 |
| C-014 | data | confirmed | CONTA declares file CLIENTES assigned to 'CLIENTES' (INDEXED). | CONTA.cbl:7 |
| C-015 | data | confirmed | CONTA declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). | CONTA.cbl:11 |
| C-016 | data | confirmed | CONTA defines file record description CLIENTES. | CONTA.cbl:15 |
| C-017 | data | confirmed | CONTA defines file record description MOVTOS. | CONTA.cbl:22 |
| C-018 | structure | confirmed | CONTA receives parameters through LINKAGE: LK-OP, LK-CLI. | CONTA.cbl:35-36 |
| C-019 | data | confirmed | CONTA working storage has 5 top-level records: WS-VALOR, WS-DESTINO, WS-SALDO-FMT, WS-LIMITE-SAQUE, WS-TARIFA-TRANSF. | CONTA.cbl:29-33 |
| C-020 | data | confirmed | CONTA performs CLOSE, OPEN I-O, READ on CLIENTES. | CONTA.cbl:44 |
| C-021 | data | confirmed | CONTA performs CLOSE, OPEN EXTEND on MOVTOS. | CONTA.cbl:45 |
| C-022 | data | confirmed | CONTA performs REWRITE on CLI-REG. | CONTA.cbl:111 |
| C-023 | data | confirmed | CONTA performs WRITE on MOV-REG. | CONTA.cbl:121 |
| C-024 | structure | confirmed | CONTA reads interactive input into: WS-DESTINO, WS-VALOR. | CONTA.cbl:63 |

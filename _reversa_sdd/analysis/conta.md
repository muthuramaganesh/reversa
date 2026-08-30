# Technical analysis — CONTA

CONTA has 3 structural and 9 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-179 | structure | confirmed | CONTA is organised into 6 paragraphs: MAIN, SALDO, SAQUE, DEPOSITO, TRANSFERENCIA, GRAVA. | examples/legacy_atm/CONTA.cbl:43-115 |
| C-180 | data | confirmed | CONTA declares file CLIENTES assigned to 'CLIENTES' (INDEXED). | examples/legacy_atm/CONTA.cbl:7 |
| C-181 | data | confirmed | CONTA declares file MOVTOS assigned to 'MOVTOS' (SEQUENTIAL). | examples/legacy_atm/CONTA.cbl:11 |
| C-182 | data | confirmed | CONTA defines file record description CLIENTES. | examples/legacy_atm/CONTA.cbl:15 |
| C-183 | data | confirmed | CONTA defines file record description MOVTOS. | examples/legacy_atm/CONTA.cbl:22 |
| C-184 | structure | confirmed | CONTA receives parameters through LINKAGE: LK-OP, LK-CLI. | examples/legacy_atm/CONTA.cbl:35-36 |
| C-185 | data | confirmed | CONTA working storage has 5 top-level records: WS-VALOR, WS-DESTINO, WS-SALDO-FMT, WS-LIMITE-SAQUE, WS-TARIFA-TRANSF. | examples/legacy_atm/CONTA.cbl:29-33 |
| C-186 | data | confirmed | CONTA performs CLOSE, OPEN I-O, READ on CLIENTES. | examples/legacy_atm/CONTA.cbl:44 |
| C-187 | data | confirmed | CONTA performs CLOSE, OPEN EXTEND on MOVTOS. | examples/legacy_atm/CONTA.cbl:45 |
| C-188 | data | confirmed | CONTA performs REWRITE on CLI-REG. | examples/legacy_atm/CONTA.cbl:111 |
| C-189 | data | confirmed | CONTA performs WRITE on MOV-REG. | examples/legacy_atm/CONTA.cbl:121 |
| C-190 | structure | confirmed | CONTA reads interactive input into: WS-DESTINO, WS-VALOR. | examples/legacy_atm/CONTA.cbl:63 |

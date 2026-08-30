# Technical analysis — MENU

MENU has 2 structural and 5 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-197 | structure | confirmed | MENU is organised into 3 paragraphs: MAIN, LOGIN, LOOP-MENU. | examples/legacy_atm/MENU.cbl:28-62 |
| C-198 | data | confirmed | MENU declares file CLIENTES assigned to 'CLIENTES' (INDEXED). | examples/legacy_atm/MENU.cbl:7 |
| C-199 | data | confirmed | MENU defines file record description CLIENTES. | examples/legacy_atm/MENU.cbl:13 |
| C-200 | data | confirmed | MENU working storage has 6 top-level records: WS-CONTA, WS-SENHA, WS-TENTATIVAS, WS-OPCAO, WS-FIM, WS-FS. | examples/legacy_atm/MENU.cbl:21-26 |
| C-201 | data | confirmed | MENU performs CLOSE, OPEN I-O, READ on CLIENTES. | examples/legacy_atm/MENU.cbl:29 |
| C-202 | data | confirmed | MENU performs REWRITE on CLI-REG. | examples/legacy_atm/MENU.cbl:34 |
| C-203 | structure | confirmed | MENU reads interactive input into: WS-CONTA, WS-OPCAO. | examples/legacy_atm/MENU.cbl:43 |

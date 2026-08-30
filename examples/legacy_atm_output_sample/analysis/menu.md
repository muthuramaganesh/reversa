# Technical analysis — MENU

MENU has 2 structural and 5 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-031 | structure | confirmed | MENU is organised into 3 paragraphs: MAIN, LOGIN, LOOP-MENU. | MENU.cbl:28-62 |
| C-032 | data | confirmed | MENU declares file CLIENTES assigned to 'CLIENTES' (INDEXED). | MENU.cbl:7 |
| C-033 | data | confirmed | MENU defines file record description CLIENTES. | MENU.cbl:13 |
| C-034 | data | confirmed | MENU working storage has 6 top-level records: WS-CONTA, WS-SENHA, WS-TENTATIVAS, WS-OPCAO, WS-FIM, WS-FS. | MENU.cbl:21-26 |
| C-035 | data | confirmed | MENU performs CLOSE, OPEN I-O, READ on CLIENTES. | MENU.cbl:29 |
| C-036 | data | confirmed | MENU performs REWRITE on CLI-REG. | MENU.cbl:34 |
| C-037 | structure | confirmed | MENU reads interactive input into: WS-CONTA, WS-OPCAO. | MENU.cbl:43 |

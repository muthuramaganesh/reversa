# Technical analysis — UTIL

UTIL has 2 structural and 1 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-204 | structure | confirmed | UTIL is organised into 3 paragraphs: MAIN, FORMATA, MASCARA. | examples/legacy_atm/UTIL.cbl:12-25 |
| C-205 | structure | confirmed | UTIL receives parameters through LINKAGE: LK-FUNC, LK-VALOR, LK-SAIDA. | examples/legacy_atm/UTIL.cbl:8-10 |
| C-206 | data | confirmed | UTIL working storage has 1 top-level records: WS-EDIT. | examples/legacy_atm/UTIL.cbl:6 |

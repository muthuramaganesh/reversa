# Technical analysis — ANALYSIS

ANALYSIS has 1 structural and 1 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-208 | structure | confirmed | ANALYSIS is organised into 13 classs: Fact, FileFacts, of, first, _is_comment, analyze_cobol, analyze_generic, analyze, pic_english, count, _cnt, aborts_in_branch …. | reversa/analysis.py:19-299 |
| C-209 | data | confirmed | ANALYSIS performs analyze_cobol on sqlite3. | reversa/analysis.py:196 |

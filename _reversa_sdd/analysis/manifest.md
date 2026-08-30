# Technical analysis — MANIFEST

MANIFEST has 1 structural and 1 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-214 | structure | confirmed | MANIFEST is organised into 10 functions: sha256_of, FileStatus, Manifest, __init__, load, save, record, record_many, classify, status_of. | reversa/manifest.py:22-80 |
| C-215 | data | confirmed | MANIFEST performs sha256_of on open. | reversa/manifest.py:24 |

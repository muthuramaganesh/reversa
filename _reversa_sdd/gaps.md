# Gaps

13 gaps registered: 0 critical, 13 moderate,
0 cosmetic, 0 out of scope. Blocking gaps must be
resolved by a documented human decision before migration cutover.

To resolve a gap, edit its **Status** and **Resolution** columns (or answer via `reversa answer`).

| Gap | Unit | Severity | Blocking | Status | Description | Resolution |
|---|---|---|---|---|---|---|
| GAP-009 | CONFTEST | moderate |  | open | No decision logic detected in tests/conftest.py; business rules for CONFTEST may live elsewhere (data, configuration, copybooks). |  |
| GAP-008 | HEURISTIC | moderate |  | open | No decision logic detected in reversa/llm/heuristic.py; business rules for HEURISTIC may live elsewhere (data, configuration, copybooks). |  |
| GAP-010 | TEST_ANALYSIS | moderate |  | open | No decision logic detected in tests/test_analysis.py; business rules for TEST_ANALYSIS may live elsewhere (data, configuration, copybooks). |  |
| GAP-011 | TEST_BACKEND | moderate |  | open | No decision logic detected in tests/test_backend.py; business rules for TEST_BACKEND may live elsewhere (data, configuration, copybooks). |  |
| GAP-012 | TEST_CONFIDENCE | moderate |  | open | No decision logic detected in tests/test_confidence.py; business rules for TEST_CONFIDENCE may live elsewhere (data, configuration, copybooks). |  |
| GAP-013 | TEST_MANIFEST | moderate |  | open | No decision logic detected in tests/test_manifest.py; business rules for TEST_MANIFEST may live elsewhere (data, configuration, copybooks). |  |
| GAP-001 | __INIT__ | moderate |  | open | No recognisable structure extracted from reversa/__init__.py; manual reading required. |  |
| GAP-003 | __INIT__ | moderate |  | open | No recognisable structure extracted from reversa/agents/__init__.py; manual reading required. |  |
| GAP-004 | __INIT__ | moderate |  | open | No recognisable structure extracted from reversa/llm/__init__.py; manual reading required. |  |
| GAP-005 | __INIT__ | moderate |  | open | No decision logic detected in reversa/__init__.py; business rules for __INIT__ may live elsewhere (data, configuration, copybooks). |  |
| GAP-006 | __INIT__ | moderate |  | open | No decision logic detected in reversa/agents/__init__.py; business rules for __INIT__ may live elsewhere (data, configuration, copybooks). |  |
| GAP-007 | __INIT__ | moderate |  | open | No decision logic detected in reversa/llm/__init__.py; business rules for __INIT__ may live elsewhere (data, configuration, copybooks). |  |
| GAP-002 | __MAIN__ | moderate |  | open | No recognisable structure extracted from reversa/__main__.py; manual reading required. |  |

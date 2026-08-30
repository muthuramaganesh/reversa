# Inventory

Project: `reversa`  
Stack: markdown, python, cobol, text, toml, c  
Files: 79 · Units: 36

## Units

| Unit | Kind | Entry | Files | Description |
|---|---|---|---|---|
| **CONTA** | program |  | `examples/legacy_atm/CONTA.cbl` |  |
| **EXTRATO** | program |  | `examples/legacy_atm/EXTRATO.cbl` |  |
| **MENU** | program | yes | `examples/legacy_atm/MENU.cbl` |  |
| **UTIL** | program |  | `examples/legacy_atm/UTIL.cbl` |  |
| **KBDREAD** | module |  | `examples/legacy_atm/kbdread.c` |  |
| **__INIT__** | module |  | `reversa/__init__.py` |  |
| **__MAIN__** | module | yes | `reversa/__main__.py` |  |
| **ANALYSIS** | module |  | `reversa/analysis.py` |  |
| **CLI** | module |  | `reversa/cli.py` |  |
| **CONFIDENCE** | module |  | `reversa/confidence.py` |  |
| **ENGINES** | module |  | `reversa/engines.py` |  |
| **INSTALLER** | module |  | `reversa/installer.py` |  |
| **MANIFEST** | module |  | `reversa/manifest.py` |  |
| **MODELS** | module |  | `reversa/models.py` |  |
| **ORCHESTRATOR** | module |  | `reversa/orchestrator.py` |  |
| **PROJECT** | module |  | `reversa/project.py` |  |
| **__INIT__** | module |  | `reversa/agents/__init__.py` |  |
| **ARCHAEOLOGIST** | module |  | `reversa/agents/archaeologist.py` |  |
| **ARCHITECT** | module |  | `reversa/agents/architect.py` |  |
| **BASE** | module |  | `reversa/agents/base.py` |  |
| **DETECTIVE** | module |  | `reversa/agents/detective.py` |  |
| **MIGRATION** | module |  | `reversa/agents/migration.py` |  |
| **PROCESS** | module |  | `reversa/agents/process.py` |  |
| **REVIEWER** | module |  | `reversa/agents/reviewer.py` |  |
| **SCOUT** | module |  | `reversa/agents/scout.py` |  |
| **WRITER** | module |  | `reversa/agents/writer.py` |  |
| **__INIT__** | module |  | `reversa/llm/__init__.py` |  |
| **ANTHROPIC_BACKEND** | module |  | `reversa/llm/anthropic_backend.py` |  |
| **BASE** | module |  | `reversa/llm/base.py` |  |
| **HEURISTIC** | module |  | `reversa/llm/heuristic.py` |  |
| **CONFTEST** | module |  | `tests/conftest.py` |  |
| **TEST_ANALYSIS** | module |  | `tests/test_analysis.py` |  |
| **TEST_BACKEND** | module |  | `tests/test_backend.py` |  |
| **TEST_CONFIDENCE** | module |  | `tests/test_confidence.py` |  |
| **TEST_MANIFEST** | module |  | `tests/test_manifest.py` |  |
| **TEST_PIPELINE** | module | yes | `tests/test_pipeline.py` |  |

## Files

| Path | Language | Lines | Bytes |
|---|---|---|---|
| `CLAUDE.md` | markdown | 29 | 2632 |
| `README.md` | markdown | 176 | 10308 |
| `pyproject.toml` | toml | 20 | 543 |
| `.pytest_cache/README.md` | markdown | 8 | 302 |
| `examples/legacy_atm/CONTA.cbl` | cobol | 121 | 4011 |
| `examples/legacy_atm/EXTRATO.cbl` | cobol | 44 | 1513 |
| `examples/legacy_atm/MENU.cbl` | cobol | 80 | 2745 |
| `examples/legacy_atm/README.md` | markdown | 6 | 299 |
| `examples/legacy_atm/UTIL.cbl` | cobol | 26 | 876 |
| `examples/legacy_atm/kbdread.c` | c | 20 | 544 |
| `examples/legacy_atm_output_sample/README.md` | markdown | 31 | 1733 |
| `examples/legacy_atm_output_sample/architecture.md` | markdown | 44 | 1220 |
| `examples/legacy_atm_output_sample/business-context.md` | markdown | 78 | 5138 |
| `examples/legacy_atm_output_sample/confidence-report.md` | markdown | 31 | 986 |
| `examples/legacy_atm_output_sample/dependencies.md` | markdown | 21 | 331 |
| `examples/legacy_atm_output_sample/gaps.md` | markdown | 11 | 415 |
| `examples/legacy_atm_output_sample/inventory.md` | markdown | 26 | 660 |
| `examples/legacy_atm_output_sample/processes.md` | markdown | 233 | 13151 |
| `examples/legacy_atm_output_sample/questions.md` | markdown | 139 | 4478 |
| `examples/legacy_atm_output_sample/rules.md` | markdown | 107 | 4062 |
| `examples/legacy_atm_output_sample/analysis/conta.md` | markdown | 18 | 1462 |
| `examples/legacy_atm_output_sample/analysis/extrato.md` | markdown | 12 | 852 |
| `examples/legacy_atm_output_sample/analysis/kbdread.md` | markdown | 7 | 291 |
| `examples/legacy_atm_output_sample/analysis/menu.md` | markdown | 13 | 920 |
| `examples/legacy_atm_output_sample/analysis/util.md` | markdown | 9 | 512 |
| `examples/legacy_atm_output_sample/migration/risk-register.md` | markdown | 5 | 293 |
| `examples/legacy_atm_output_sample/migration/strategy.md` | markdown | 15 | 1139 |
| `examples/legacy_atm_output_sample/specs/conta/design.md` | markdown | 12 | 969 |
| `examples/legacy_atm_output_sample/specs/conta/requirements.md` | markdown | 40 | 2839 |
| `examples/legacy_atm_output_sample/specs/conta/tasks.md` | markdown | 17 | 1093 |
| `examples/legacy_atm_output_sample/specs/extrato/design.md` | markdown | 12 | 596 |
| `examples/legacy_atm_output_sample/specs/extrato/requirements.md` | markdown | 18 | 760 |
| `examples/legacy_atm_output_sample/specs/extrato/tasks.md` | markdown | 14 | 720 |
| `examples/legacy_atm_output_sample/specs/kbdread/design.md` | markdown | 12 | 313 |
| `examples/legacy_atm_output_sample/specs/kbdread/requirements.md` | markdown | 14 | 428 |
| `examples/legacy_atm_output_sample/specs/kbdread/tasks.md` | markdown | 11 | 536 |
| `examples/legacy_atm_output_sample/specs/menu/design.md` | markdown | 12 | 717 |
| `examples/legacy_atm_output_sample/specs/menu/requirements.md` | markdown | 30 | 1802 |
| `examples/legacy_atm_output_sample/specs/menu/tasks.md` | markdown | 17 | 966 |
| `examples/legacy_atm_output_sample/specs/util/design.md` | markdown | 12 | 374 |
| `examples/legacy_atm_output_sample/specs/util/requirements.md` | markdown | 16 | 559 |
| `examples/legacy_atm_output_sample/specs/util/tasks.md` | markdown | 14 | 685 |
| `examples/legacy_atm_output_sample/traceability/code-spec-matrix.md` | markdown | 35 | 1475 |
| `examples/legacy_atm_output_sample/traceability/spec-impact-matrix.md` | markdown | 11 | 407 |
| `reversa/__init__.py` | python | 18 | 950 |
| `reversa/__main__.py` | python | 4 | 79 |
| `reversa/analysis.py` | python | 301 | 13213 |
| `reversa/cli.py` | python | 210 | 9331 |
| `reversa/confidence.py` | python | 92 | 3145 |
| `reversa/engines.py` | python | 71 | 3226 |
| `reversa/installer.py` | python | 243 | 9496 |
| `reversa/manifest.py` | python | 84 | 2623 |
| `reversa/models.py` | python | 245 | 8178 |
| `reversa/orchestrator.py` | python | 170 | 7744 |
| `reversa/project.py` | python | 88 | 3589 |
| `reversa/agents/__init__.py` | python | 20 | 758 |
| `reversa/agents/archaeologist.py` | python | 124 | 7621 |
| `reversa/agents/architect.py` | python | 181 | 8347 |
| `reversa/agents/base.py` | python | 125 | 5281 |
| `reversa/agents/detective.py` | python | 157 | 10082 |
| `reversa/agents/migration.py` | python | 152 | 8885 |
| `reversa/agents/process.py` | python | 547 | 36616 |
| `reversa/agents/reviewer.py` | python | 182 | 10184 |
| `reversa/agents/scout.py` | python | 158 | 7883 |
| `reversa/agents/writer.py` | python | 172 | 9144 |
| `reversa/llm/__init__.py` | python | 11 | 508 |
| `reversa/llm/anthropic_backend.py` | python | 78 | 3166 |
| `reversa/llm/base.py` | python | 45 | 1433 |
| `reversa/llm/heuristic.py` | python | 13 | 337 |
| `reversa.egg-info/SOURCES.txt` | text | 37 | 886 |
| `reversa.egg-info/dependency_links.txt` | text | 1 | 1 |
| `reversa.egg-info/entry_points.txt` | text | 2 | 45 |
| `reversa.egg-info/top_level.txt` | text | 1 | 8 |
| `tests/conftest.py` | python | 13 | 256 |
| `tests/test_analysis.py` | python | 28 | 1293 |
| `tests/test_backend.py` | python | 51 | 2182 |
| `tests/test_confidence.py` | python | 30 | 1221 |
| `tests/test_manifest.py` | python | 56 | 2038 |
| `tests/test_pipeline.py` | python | 141 | 7447 |

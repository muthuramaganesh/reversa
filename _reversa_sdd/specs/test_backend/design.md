# Design — TEST_BACKEND

## Structure
TEST_BACKEND is organised into 4 functions: test_strip_json_tolerates_fences, test_anthropic_backend_parses_and_falls_back, fake_call, test_registry_dedupes_questions_and_gaps.

## Data
No persistent data recovered.

## Dependencies
TEST_BACKEND depends on JSON (import). TEST_BACKEND depends on REVERSA.AGENTS (import). TEST_BACKEND depends on REVERSA.LLM.ANTHROPIC_BACKEND (import). TEST_BACKEND depends on REVERSA.LLM.BASE (import). TEST_BACKEND depends on REVERSA.MODELS (import). TEST_BACKEND depends on REVERSA.ANALYSIS (import). TEST_BACKEND depends on REVERSA.PROJECT (import).

_Derived from claims: C-159, C-160, C-161, C-162, C-163, C-164, C-165, C-233_

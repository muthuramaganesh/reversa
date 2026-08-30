# Design — TEST_PIPELINE

## Structure
TEST_PIPELINE is organised into 7 functions: _quiet, test_discovery_and_migration_offline, test_reviewer_downgrades_unverifiable_claims, test_cli_roundtrip, test_units_filter, test_processes_reconstructed, test_business_context.

## Data
No persistent data recovered.

## Dependencies
TEST_PIPELINE depends on JSON (import). TEST_PIPELINE depends on PATHLIB (import). TEST_PIPELINE depends on PYTEST (import). TEST_PIPELINE depends on REVERSA.CLI (import). TEST_PIPELINE depends on REVERSA.CONFIDENCE (import). TEST_PIPELINE depends on REVERSA.LLM (import). TEST_PIPELINE depends on REVERSA.MODELS (import). TEST_PIPELINE depends on REVERSA.ORCHESTRATOR (import).

_Derived from claims: C-171, C-172, C-173, C-174, C-175, C-176, C-177, C-178, C-236_

# Technical analysis — TEST_BACKEND

TEST_BACKEND has 1 structural and 0 data facts extracted by static analysis.

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
| C-233 | structure | confirmed | TEST_BACKEND is organised into 4 functions: test_strip_json_tolerates_fences, test_anthropic_backend_parses_and_falls_back, fake_call, test_registry_dedupes_questions_and_gaps. | tests/test_backend.py:9-43 |

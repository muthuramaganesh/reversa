"""LLM backends.

Agents describe *what* they need (system prompt, user prompt, output schema,
and a heuristic fallback). Backends decide *how* to produce it:

  * AnthropicBackend  - calls the Claude Messages API (ANTHROPIC_API_KEY).
  * HeuristicBackend  - offline static analysis via each agent's `heuristic()`.
                        Deterministic, no network; useful for tests, CI, and
                        environments with no model access.
"""
from .base import Backend, get_backend  # noqa: F401

"""Hybrid backend: heuristic extraction, LLM wording.

  generate()  → HeuristicBackend. Every claim, piece of evidence, gap, question, state and
                unit grouping comes from the deterministic analysers, exactly as with
                --backend heuristic. The LLM never sees an agent prompt.
  _call()     → Qwen (local) or Anthropic. The Detective calls this for the plain-English
                rewrite of rules, process steps and gaps/contradictions; specbuilder keeps
                the deterministic wording for any rewrite that drops a number, limit or
                message text from the code. The API also uses the same provider for the
                Business Context overview.

If the LLM is unreachable or replies with junk, the run still completes with heuristic
wording; a single warning is printed to stderr.

Backend names:  hybrid-qwen  (nothing leaves the machine)  ·  hybrid-anthropic
"""
from __future__ import annotations

import sys
from typing import Any

from .base import Backend
from .prose import PROVIDERS, make_caller


class HybridBackend(Backend):
    def __init__(self, llm: str = "qwen", model: str | None = None, max_tokens: int = 8000) -> None:
        if llm not in PROVIDERS:
            raise ValueError(f"hybrid backend: unknown LLM '{llm}' (expected {' or '.join(PROVIDERS)})")
        from .heuristic import HeuristicBackend
        self.llm = llm
        self.name = f"hybrid-{llm}"
        self._heuristic = HeuristicBackend()
        self._complete = make_caller(llm, model=model, max_tokens=max_tokens)
        self.llm_calls = 0
        self.llm_failures = 0

    def generate(self, agent, payload: dict[str, Any]) -> dict[str, Any]:
        return self._heuristic.generate(agent, payload)

    def _call(self, system: str, user: str) -> str:
        """Prose-only completion. Errors propagate so the caller keeps its heuristic text."""
        self.llm_calls += 1
        try:
            return self._complete(system, user)
        except Exception as e:
            self.llm_failures += 1
            if self.llm_failures == 1:
                print(f"warning: {self.name}: LLM call failed ({e}); keeping heuristic wording",
                      file=sys.stderr)
            raise

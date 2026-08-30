from __future__ import annotations

from typing import Any

from .base import Backend


class HeuristicBackend(Backend):
    """Offline backend: delegates to each agent's deterministic heuristic."""
    name = "heuristic"

    def generate(self, agent, payload: dict[str, Any]) -> dict[str, Any]:
        return agent.heuristic(payload)

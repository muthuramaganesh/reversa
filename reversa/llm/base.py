from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..agents.base import Agent


class Backend(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, agent: "Agent", payload: dict[str, Any]) -> dict[str, Any]:
        """Return a dict matching `agent.output_schema` for the given payload."""


def strip_json(text: str) -> dict[str, Any]:
    """Parse a JSON object out of a model reply, tolerating code fences."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in reply")
    return json.loads(t[start:end + 1])


def get_backend(name: str, **kw: Any) -> Backend:
    if name == "heuristic":
        from .heuristic import HeuristicBackend
        return HeuristicBackend()
    if name == "anthropic":
        from .anthropic_backend import AnthropicBackend
        return AnthropicBackend(**kw)
    if name == "auto":
        import os
        if os.environ.get("ANTHROPIC_API_KEY"):
            from .anthropic_backend import AnthropicBackend
            return AnthropicBackend(**kw)
        from .heuristic import HeuristicBackend
        return HeuristicBackend()
    raise ValueError(f"unknown backend: {name}")

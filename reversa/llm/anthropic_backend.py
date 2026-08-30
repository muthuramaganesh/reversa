from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from .base import Backend, strip_json

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = os.environ.get("REVERSA_MODEL", "claude-sonnet-4-6")


class AnthropicBackend(Backend):
    """Claude Messages API backend (stdlib only; no SDK dependency).

    Each agent call is one request: the agent's system prompt, its rendered
    user prompt (which embeds numbered source code so the model can cite
    file:line evidence), and an instruction to reply with a single JSON
    object. If the model's JSON cannot be parsed the agent's heuristic is used
    and a gap is recorded by the orchestrator, so uncertainty is never hidden.
    """
    name = "anthropic"

    def __init__(self, model: str | None = None, max_tokens: int = 8000,
                 api_key: str | None = None, retries: int = 3) -> None:
        self.model = model or DEFAULT_MODEL
        self.max_tokens = max_tokens
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.retries = retries
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

    def _call(self, system: str, user: str) -> str:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode()
        req = urllib.request.Request(API_URL, data=body, headers={
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        })
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    data = json.loads(resp.read())
                return "".join(b.get("text", "") for b in data.get("content", [])
                               if b.get("type") == "text")
            except urllib.error.HTTPError as e:
                last = e
                if e.code in (429, 500, 502, 503, 529):
                    time.sleep(2 ** attempt)
                    continue
                raise
            except urllib.error.URLError as e:
                last = e
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Anthropic API failed after retries: {last}")

    def generate(self, agent, payload: dict[str, Any]) -> dict[str, Any]:
        system = agent.system_prompt()
        user = agent.user_prompt(payload)
        user += ("\n\nReply with ONE JSON object only, no prose, no markdown fences, "
                 "matching this schema:\n" + json.dumps(agent.output_schema, indent=1))
        text = self._call(system, user)
        try:
            return strip_json(text)
        except (ValueError, json.JSONDecodeError):
            out = agent.heuristic(payload)
            out.setdefault("_warnings", []).append(
                f"{agent.name}: model reply was not valid JSON; used heuristic fallback")
            return out

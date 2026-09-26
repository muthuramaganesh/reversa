"""Local Qwen backend via any OpenAI-compatible server (Ollama, LM Studio, vLLM).

Configuration (environment variables, all optional):
  QWEN_BASE_URL  default http://localhost:11434/v1   (Ollama)
                 LM Studio: http://localhost:1234/v1 · vLLM: http://localhost:8000/v1
  QWEN_MODEL     default qwen2.5-coder:14b           (must match a model your server has)
  QWEN_API_KEY   default "local" (local servers ignore it)
  QWEN_TIMEOUT   seconds per request, default 900   (local models can be slow)

Nothing leaves your machine: requests go only to QWEN_BASE_URL.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from .base import Backend, strip_json

DEFAULT_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen2.5-coder:14b"


class QwenBackend(Backend):
    name = "qwen"

    def __init__(self, model: str | None = None, max_tokens: int = 8000,
                 base_url: str | None = None, retries: int = 2) -> None:
        self.model = model or os.environ.get("QWEN_MODEL", DEFAULT_MODEL)
        self.base_url = (base_url or os.environ.get("QWEN_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.api_key = os.environ.get("QWEN_API_KEY", "local")
        self.max_tokens = max_tokens
        self.timeout = int(os.environ.get("QWEN_TIMEOUT", "900"))
        self.retries = retries

    def _call(self, system: str, user: str) -> str:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": 0.2,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }).encode()
        req = urllib.request.Request(f"{self.base_url}/chat/completions", data=body, headers={
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        })
        last: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read())
                text = data["choices"][0]["message"].get("content") or ""
                # Qwen3 "thinking" models wrap reasoning in <think>…</think>; drop it
                return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
            except urllib.error.HTTPError as e:
                last = e
                if e.code == 404:
                    raise RuntimeError(f"Qwen server has no model '{self.model}'. Set QWEN_MODEL "
                                       f"to one your server lists (e.g. `ollama list`).") from e
                time.sleep(2 ** attempt)
            except urllib.error.URLError as e:
                last = e
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Could not reach Qwen at {self.base_url}: {last}. Is the local "
                           f"server running (e.g. `ollama serve`)?")

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
                f"{agent.name}: Qwen reply was not valid JSON; used heuristic fallback")
            return out

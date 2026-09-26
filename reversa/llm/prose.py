"""Plain-text LLM completion, `call(system, user) -> str`, for the prose-only passes.

Used by the hybrid backend (plain-English rewrite of rules, process steps and findings)
and by the API's Business Context overview. Nothing here extracts facts: callers feed it
text that was already extracted deterministically and validate what comes back.

Providers:
  qwen       any OpenAI-compatible local server; configured by QWEN_* (see qwen_backend.py).
             Requests go only to QWEN_BASE_URL.
  anthropic  the Anthropic Messages API. Needs ANTHROPIC_API_KEY.
             REVERSA_LLM_MODEL  model id (default claude-sonnet-4-6)
             ANTHROPIC_TIMEOUT  seconds per request (default 300)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Callable

PROVIDERS = ("qwen", "anthropic")
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

Caller = Callable[[str, str], str]


def make_caller(provider: str, model: str | None = None, max_tokens: int = 8000,
                timeout: int | None = None) -> Caller:
    """Return call(system, user) -> reply text for the given provider.
    Raises RuntimeError up front if the provider cannot be configured (e.g. no API key)."""
    if provider == "qwen":
        from .qwen_backend import QwenBackend
        qb = QwenBackend(model=model, max_tokens=max_tokens)
        if timeout:
            qb.timeout = timeout
        return qb._call
    if provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        mdl = model or os.environ.get("REVERSA_LLM_MODEL", DEFAULT_ANTHROPIC_MODEL)
        tmo = timeout or int(os.environ.get("ANTHROPIC_TIMEOUT", "300"))

        def call(system: str, user: str) -> str:
            return _anthropic(key, mdl, max_tokens, tmo, system, user)
        return call
    raise ValueError(f"unknown LLM provider: {provider} (expected one of {', '.join(PROVIDERS)})")


def _anthropic(key: str, model: str, max_tokens: int, timeout: int,
               system: str, user: str, retries: int = 3) -> str:
    body = json.dumps({"model": model, "max_tokens": max_tokens, "temperature": 0.2,
                       "system": system,
                       "messages": [{"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(ANTHROPIC_URL, data=body, headers={
        "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            return "".join(b.get("text", "") for b in data.get("content", [])
                           if b.get("type") == "text").strip()
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 500, 502, 503, 504, 529):   # auth/model/request errors: don't retry
                detail = e.read().decode(errors="replace")[:500]
                raise RuntimeError(f"Anthropic API error {e.code}: {detail}") from e
            time.sleep(2 ** attempt)
        except urllib.error.URLError as e:
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Could not get a reply from the Anthropic API: {last}")

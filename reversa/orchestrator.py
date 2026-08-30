"""The `reversa` orchestrator role: execution, resumption, activation of agents.

State lives under `.reversa/`:
  state.json    stage status (pending/done/failed), timestamps, backend used
  registry.json all claims, gaps, questions, units (the source of truth)
  plan.md       human-readable execution plan / progress
Artifacts are rendered into `_reversa_sdd/` (configurable).
"""
from __future__ import annotations

import json
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .agents import ALL, DISCOVERY, MIGRATION
from .agents.base import Context
from .confidence import distribution
from .llm import Backend
from .models import Registry
from .project import Project

STATE_DIR = ".reversa"
DEFAULT_OUT = "_reversa_sdd"


@dataclass
class State:
    stages: dict[str, dict[str, Any]] = field(default_factory=dict)
    backend: str = ""
    started: float = 0.0
    updated: float = 0.0

    @classmethod
    def load(cls, path: Path) -> "State":
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return cls(**d)
        return cls()

    def save(self, path: Path) -> None:
        self.updated = time.time()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")


class Orchestrator:
    def __init__(self, root: Path, backend: Backend, out_dir: str = DEFAULT_OUT,
                 log: Callable[[str], None] = print, config: dict[str, Any] | None = None) -> None:
        self.root = root.resolve()
        self.backend = backend
        self.state_dir = self.root / STATE_DIR
        self.out_dir = self.root / out_dir
        self.log = log
        self.config = config or {}
        self.state = State.load(self.state_dir / "state.json")
        self.registry = Registry.load(self.state_dir / "registry.json")

    # ---- public --------------------------------------------------------------
    def run(self, team: str = "discovery", resume: bool = False, only: list[str] | None = None,
            units: list[str] | None = None) -> Registry:
        agents = {"discovery": DISCOVERY, "migration": MIGRATION,
                  "all": DISCOVERY + MIGRATION}[team]
        if only:
            agents = [ALL[n if n.startswith("reversa-") else f"reversa-{n}"] for n in only]
        if not resume and team in ("discovery", "all") and not only:
            self.registry = Registry()          # fresh discovery
            self.state = State()
        if not self.state.started:
            self.state.started = time.time()
        self.state.backend = self.backend.name
        ctx = Context(project=Project(self.root), registry=self.registry, backend=self.backend,
                      out_dir=self.out_dir, config=self.config, log=self.log, units_filter=units)
        self.log(f"reversa · {team} · backend={self.backend.name} · project={self.root.name}")
        for cls in agents:
            st = self.state.stages.get(cls.name, {})
            if resume and not only and st.get("status") == "done":
                self.log(f"- {cls.name}: done (skipped)")
                continue
            self.log(f"- {cls.name}")
            t0 = time.time()
            try:
                cls().run(ctx)
                self.state.stages[cls.name] = {"status": "done", "seconds": round(time.time() - t0, 1),
                                               "claims": len(self.registry.claims)}
            except Exception as e:  # keep state consistent, fail loudly
                self.state.stages[cls.name] = {"status": "failed", "error": f"{type(e).__name__}: {e}",
                                               "trace": traceback.format_exc()[-2000:]}
                self._persist()
                raise
            self._persist()
        self._write_plan()
        self._write_readme()
        return self.registry

    def status(self) -> dict[str, Any]:
        d = distribution(self.registry.claims)
        return {"stages": self.state.stages, "backend": self.state.backend,
                "claims": d.total, "confirmed": d.confirmed, "inferred": d.inferred, "gap": d.gap,
                "index": round(d.index, 4), "gaps": len(self.registry.gaps),
                "questions": len(self.registry.questions), "units": [u.name for u in self.registry.units]}

    # ---- internals ---------------------------------------------------------
    def _persist(self) -> None:
        self.state.save(self.state_dir / "state.json")
        self.registry.save(self.state_dir / "registry.json")

    def _write_plan(self) -> None:
        rows = []
        for cls in DISCOVERY + MIGRATION:
            st = self.state.stages.get(cls.name, {"status": "pending"})
            mark = {"done": "[x]", "failed": "[!]"}.get(st["status"], "[ ]")
            extra = f" ({st.get('seconds')}s, {st.get('claims')} claims)" if st["status"] == "done" else \
                    f" — {st.get('error')}" if st["status"] == "failed" else ""
            rows.append(f"- {mark} {cls.name}{extra}")
        d = distribution(self.registry.claims)
        (self.state_dir / "plan.md").write_text(f"""# Reversa execution plan

Backend: {self.state.backend or '—'}

## Discovery team
{chr(10).join(rows[:len(DISCOVERY)])}

## Migration team
{chr(10).join(rows[len(DISCOVERY):])}

## Snapshot
- Claims: {d.total} ({d.confirmed} confirmed / {d.inferred} inferred / {d.gap} gap) · index {d.index:.1%}
- Gaps: {len(self.registry.gaps)} · Questions: {len(self.registry.questions)}
- Resume with `reversa run --resume`; re-run a single stage with `reversa run --only reviewer`.
""", encoding="utf-8")

    def _write_readme(self) -> None:
        d = distribution(self.registry.claims)
        units = ", ".join(u.name for u in self.registry.units) or "—"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        (self.out_dir / "README.md").write_text(f"""# Reversa operational specification

Generated by Reversa for `{self.root.name}` (backend: {self.state.backend}).

**Read this first:** every claim in these documents is marked **confirmed**, **inferred** or **gap**.
Confirmed claims cite code. Inferred claims are hypotheses. Gaps are things nobody knows yet.
Internal confidence index: {d.index:.1%} over {d.total} claims — this is a classification
summary, not a measure of factual accuracy.

Units: {units}

| Artifact | Purpose |
|---|---|
| `inventory.md` | project surface, stack, units, files |
| `analysis/<unit>.md` | technical facts per unit |
| `rules.md` | business rules, states, permissions, exceptions |
| `architecture.md`, `dependencies.md` | components, graph, shared data |
| `business-context.md` | plain-English orientation: what it is, who uses it, what it manages, rules, parameters |
| `processes.md` | end-to-end operational processes, step by step, traced to code |
| `specs/<unit>/requirements.md` | behaviours to preserve, each traced to claims → code |
| `specs/<unit>/design.md`, `tasks.md` | structure/data/deps and reimplementation tasks |
| `traceability/code-spec-matrix.md` | code → claim → requirement |
| `traceability/spec-impact-matrix.md` | which units a spec change impacts |
| `confidence-report.md` | confidence distribution and review actions |
| `gaps.md`, `questions.md` | what humans must decide / answer |
| `migration/` | strategy, risk register, Gherkin parity scenarios |

For a business reader: start from `business-context.md`, then `processes.md`.

For a coding agent: start from `specs/<unit>/requirements.md`, treat 🟡 items as needing
validation, never implement against a ⛔ gap without a documented decision in `gaps.md`.
""", encoding="utf-8")

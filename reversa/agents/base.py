"""Base class for Reversa agents (paper §3.4, Table 2).

An agent is a role with explicit inputs and outputs. It declares:

  * `system_prompt()`  - role instructions, including the confidence rules;
  * `user_prompt(p)`   - the task, with numbered source so evidence can be cited;
  * `output_schema`    - the JSON shape the backend must return;
  * `heuristic(p)`     - an offline, deterministic approximation of the same
                         output (static analysis) so the pipeline runs without
                         a model and so a bad model reply has a safe fallback;
  * `apply(ctx, out)`  - turns the output into claims/gaps/questions/artifacts.

Separating roles this way is what makes the pipeline auditable: an incorrect
claim can be traced to the stage that introduced it (paper §6).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..llm.base import Backend
from ..models import Claim, ClaimKind, Confidence, Evidence, Registry
from ..project import Project

CONFIDENCE_RULES = """
CONFIDENCE RULES (mandatory):
- "confirmed": the statement is directly supported by cited code or a verifiable
  artifact. You MUST cite file and line range with a short excerpt.
- "inferred": supported by recurring patterns, names, flows or structure, but not
  certain. Write it as a hypothesis, cite what you based it on.
- "gap": you could not determine this safely. Record it as a gap, do not guess.
Never present an inference as a fact. Never fabricate evidence: if you cannot
point at lines, the claim is at best "inferred". Prefer fewer, well-evidenced
claims over many fluent ones.
"""


@dataclass
class Context:
    project: Project
    registry: Registry
    backend: Backend
    out_dir: Path                     # _reversa_sdd/
    config: dict[str, Any] = field(default_factory=dict)
    log: Callable[[str], None] = print
    units_filter: list[str] | None = None

    def write(self, rel: str, content: str) -> Path:
        p = self.out_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content.rstrip() + "\n", encoding="utf-8")
        return p

    def selected_units(self):
        units = self.registry.units
        if self.units_filter:
            wanted = {u.lower() for u in self.units_filter}
            units = [u for u in units if u.name.lower() in wanted]
        return units


class Agent(ABC):
    name: str = "reversa-agent"
    role: str = ""
    output_schema: dict[str, Any] = {}

    # ---- contract ---------------------------------------------------------
    def system_prompt(self) -> str:
        return (f"You are {self.name}, part of Reversa, a reverse documentation "
                f"engineering pipeline. Role: {self.role}\n" + CONFIDENCE_RULES)

    @abstractmethod
    def user_prompt(self, payload: dict[str, Any]) -> str: ...

    @abstractmethod
    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def run(self, ctx: Context) -> None: ...

    # ---- helpers shared by agents ---------------------------------------
    @staticmethod
    def _evidence_list(items: list[dict[str, Any]] | None) -> list[Evidence]:
        out: list[Evidence] = []
        for e in items or []:
            try:
                out.append(Evidence(file=str(e["file"]), line_start=int(e["line_start"]),
                                    line_end=int(e.get("line_end", e["line_start"])),
                                    excerpt=str(e.get("excerpt", ""))[:200]))
            except (KeyError, TypeError, ValueError):
                continue
        return out

    def add_claims(self, ctx: Context, unit: str, raw: list[dict[str, Any]]) -> list[Claim]:
        """Ingest raw claim dicts, enforcing the evidence rule from §3.5:
        a confirmed claim without evidence is downgraded to inferred."""
        made: list[Claim] = []
        for r in raw or []:
            stmt = str(r.get("statement", "")).strip()
            if not stmt:
                continue
            try:
                kind = ClaimKind(str(r.get("kind", "behavior")).lower())
            except ValueError:
                kind = ClaimKind.BEHAVIOR
            try:
                conf = Confidence(str(r.get("confidence", "inferred")).lower())
            except ValueError:
                conf = Confidence.INFERRED
            ev = self._evidence_list(r.get("evidence"))
            notes = str(r.get("notes", ""))
            if conf == Confidence.CONFIRMED and not ev:
                conf = Confidence.INFERRED
                notes = (notes + " " if notes else "") + "[auto: confirmed without evidence -> inferred]"
            made.append(ctx.registry.add_claim(unit=unit, kind=kind, statement=stmt,
                                               confidence=conf, evidence=ev,
                                               produced_by=self.name, notes=notes))
        return made

    def record_warnings(self, ctx: Context, out: dict[str, Any], unit: str = "project") -> None:
        for w in out.get("_warnings", []) or []:
            ctx.log(f"  ! {w}")
            ctx.registry.add_gap(unit=unit, description=w, blocking=False)

"""Data model for Reversa artifacts.

Everything the pipeline produces is a *claim* about the legacy system. A claim
carries a confidence level and a list of evidence references so that it can be
traced back to code (paper §3.5). Gaps and questions are the explicit record of
what could *not* be determined safely and needs human validation.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


class Confidence(str, Enum):
    CONFIRMED = "confirmed"  # direct evidence in code or verifiable artifact
    INFERRED = "inferred"    # supported by patterns/names/structure, not certain
    GAP = "gap"              # could not be determined; needs human validation

    @property
    def weight(self) -> float:
        # Operational rule from the paper's case study (§5.3):
        # confirmed = 1.0, inferred = 0.5, gap = 0.
        return {"confirmed": 1.0, "inferred": 0.5, "gap": 0.0}[self.value]


class ClaimKind(str, Enum):
    STRUCTURE = "structure"      # modules, paragraphs, functions, files
    BEHAVIOR = "behavior"        # what the system does in a flow
    RULE = "rule"                # business rule / validation / limit
    STATE = "state"              # state machine / status transitions
    DATA = "data"                # persistence, schema, record layouts
    DEPENDENCY = "dependency"    # calls, imports, external systems
    PERMISSION = "permission"    # who may do what
    EXCEPTION = "exception"      # error handling / operational exceptions
    ARCHITECTURE = "architecture"


class Severity(str, Enum):
    CRITICAL = "critical"
    MODERATE = "moderate"
    COSMETIC = "cosmetic"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass
class Evidence:
    file: str
    line_start: int
    line_end: int
    excerpt: str = ""

    def ref(self) -> str:
        if self.line_start == self.line_end:
            return f"{self.file}:{self.line_start}"
        return f"{self.file}:{self.line_start}-{self.line_end}"


@dataclass
class Claim:
    id: str
    unit: str
    kind: ClaimKind
    statement: str
    confidence: Confidence
    evidence: list[Evidence] = field(default_factory=list)
    produced_by: str = ""
    notes: str = ""
    review: str = ""  # reviewer annotation (e.g. "downgraded: excerpt not found")

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = self.kind.value
        d["confidence"] = self.confidence.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Claim":
        return cls(
            id=d["id"],
            unit=d["unit"],
            kind=ClaimKind(d.get("kind", "behavior")),
            statement=d["statement"],
            confidence=Confidence(d.get("confidence", "inferred")),
            evidence=[Evidence(**e) for e in d.get("evidence", [])],
            produced_by=d.get("produced_by", ""),
            notes=d.get("notes", ""),
            review=d.get("review", ""),
        )


@dataclass
class Gap:
    id: str
    unit: str
    description: str
    severity: Severity = Severity.MODERATE
    blocking: bool = False
    status: str = "open"          # open | resolved | residual | out_of_scope
    resolution: str = ""
    related_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Gap":
        d = dict(d)
        d["severity"] = Severity(d.get("severity", "moderate"))
        return cls(**d)


@dataclass
class Question:
    id: str
    unit: str
    question: str
    why_it_matters: str = ""
    related_claims: list[str] = field(default_factory=list)
    answer: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Question":
        return cls(**d)


@dataclass
class SourceFile:
    path: str            # relative to project root
    language: str
    lines: int
    size: int


@dataclass
class Unit:
    """A unit of analysis (module, program, endpoint, screen, entity...)."""
    name: str
    files: list[str]
    kind: str = "module"
    entry_point: bool = False
    description: str = ""


class Registry:
    """In-memory store for claims, gaps, questions and units; JSON-persisted."""

    def __init__(self) -> None:
        self.claims: list[Claim] = []
        self.gaps: list[Gap] = []
        self.questions: list[Question] = []
        self.units: list[Unit] = []
        self.inventory: list[SourceFile] = []
        self.meta: dict[str, Any] = {}

    # ---- id helpers -------------------------------------------------------
    def next_id(self, prefix: str, items: Iterable[Any]) -> str:
        n = 0
        pat = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
        for it in items:
            m = pat.match(it.id)
            if m:
                n = max(n, int(m.group(1)))
        return f"{prefix}-{n + 1:03d}"

    def add_claim(self, **kw: Any) -> Claim:
        if not isinstance(kw.get("kind"), ClaimKind):
            try:
                kw["kind"] = ClaimKind(str(kw.get("kind", "behavior")).lower())
            except ValueError:
                kw["kind"] = ClaimKind.BEHAVIOR
        if not isinstance(kw.get("confidence"), Confidence):
            try:
                kw["confidence"] = Confidence(str(kw.get("confidence", "inferred")).lower())
            except ValueError:
                kw["confidence"] = Confidence.INFERRED
        c = Claim(id=self.next_id("C", self.claims), **kw)
        self.claims.append(c)
        return c

    def add_gap(self, **kw: Any) -> Gap:
        for g in self.gaps:  # idempotent on re-runs
            if g.unit == kw.get("unit") and g.description == kw.get("description"):
                return g
        sev = kw.get("severity", Severity.MODERATE)
        if not isinstance(sev, Severity):
            try:
                sev = Severity(str(sev).lower())
            except ValueError:
                sev = Severity.MODERATE
        kw["severity"] = sev
        g = Gap(id=self.next_id("GAP", self.gaps), **kw)
        self.gaps.append(g)
        return g

    def add_question(self, **kw: Any) -> Question:
        for q in self.questions:  # idempotent on re-runs; keeps existing answers
            if q.unit == kw.get("unit") and q.question == kw.get("question"):
                for c in kw.get("related_claims", []) or []:
                    if c not in q.related_claims:
                        q.related_claims.append(c)
                return q
        q = Question(id=self.next_id("Q", self.questions), **kw)
        self.questions.append(q)
        return q

    def claims_for(self, unit: str) -> list[Claim]:
        return [c for c in self.claims if c.unit == unit]

    # ---- persistence ------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "meta": self.meta,
            "inventory": [asdict(f) for f in self.inventory],
            "units": [asdict(u) for u in self.units],
            "claims": [c.to_dict() for c in self.claims],
            "gaps": [g.to_dict() for g in self.gaps],
            "questions": [q.to_dict() for q in self.questions],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Registry":
        r = cls()
        if not path.exists():
            return r
        d = json.loads(path.read_text(encoding="utf-8"))
        r.meta = d.get("meta", {})
        r.inventory = [SourceFile(**f) for f in d.get("inventory", [])]
        r.units = [Unit(**u) for u in d.get("units", [])]
        r.claims = [Claim.from_dict(c) for c in d.get("claims", [])]
        r.gaps = [Gap.from_dict(g) for g in d.get("gaps", [])]
        r.questions = [Question.from_dict(q) for q in d.get("questions", [])]
        return r

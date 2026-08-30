"""Confidence model: distribution, internal confidence index, evidence checks.

The index is the operational rule used in the paper's ATM study (§5.3):
    index = (confirmed * 1.0 + inferred * 0.5) / (confirmed + inferred + gap)
It summarises the classification produced by the pipeline; it is *not* a
measure of factual accuracy (paper §7, internal validity).
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .models import Claim, Confidence, Evidence


@dataclass
class Distribution:
    confirmed: int = 0
    inferred: int = 0
    gap: int = 0

    @property
    def total(self) -> int:
        return self.confirmed + self.inferred + self.gap

    @property
    def index(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.confirmed * 1.0 + self.inferred * 0.5) / self.total

    def add(self, c: Confidence) -> None:
        setattr(self, c.value, getattr(self, c.value) + 1)


def distribution(claims: list[Claim]) -> Distribution:
    d = Distribution()
    for c in claims:
        d.add(c.confidence)
    return d


def distribution_by_unit(claims: list[Claim]) -> dict[str, Distribution]:
    out: dict[str, Distribution] = defaultdict(Distribution)
    for c in claims:
        out[c.unit].add(c.confidence)
    return dict(sorted(out.items()))


def traceability_density(claims: list[Claim]) -> float:
    """Average number of evidence references per claim (paper Table 3)."""
    if not claims:
        return 0.0
    return sum(len(c.evidence) for c in claims) / len(claims)


# ---- evidence verification --------------------------------------------------

def _norm(s: str) -> str:
    return " ".join(s.split()).lower()


def verify_evidence(root: Path, ev: Evidence, window: int = 3) -> tuple[bool, str]:
    """Check that an evidence reference points at real code.

    Returns (ok, reason). Verification is deliberately conservative: the
    excerpt must appear within `window` lines of the cited range. This is the
    mechanical part of the Reviewer's job of "returning to the original code
    to check fragile claims" (paper §3.5).
    """
    p = root / ev.file
    if not p.exists():
        return False, f"file not found: {ev.file}"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:  # pragma: no cover
        return False, f"unreadable: {e}"
    if ev.line_start < 1 or ev.line_start > len(lines):
        return False, f"line {ev.line_start} out of range (file has {len(lines)} lines)"
    if not ev.excerpt.strip():
        return True, "range exists (no excerpt to verify)"
    lo = max(1, ev.line_start - window)
    hi = min(len(lines), ev.line_end + window)
    region = _norm("\n".join(lines[lo - 1:hi]))
    if _norm(ev.excerpt) in region:
        return True, "excerpt found"
    # tolerate partial matches on the first meaningful token sequence
    head = _norm(ev.excerpt)[:40]
    if head and head in region:
        return True, "excerpt prefix found"
    return False, "excerpt not found near cited lines"

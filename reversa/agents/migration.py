"""Migration team: plan reconstruction from the specifications (paper §3.6).

Consumes the discovery artifacts and produces:
  migration/strategy.md        strategy, paradigm/topology decisions, target architecture
  migration/risk-register.md   risks derived from gaps and inferred claims
  migration/parity/<unit>.feature   Gherkin parity scenarios (executable bridge
                                    between reverse documentation and reconstruction)
Only confirmed claims become parity scenarios; inferred ones become scenarios
tagged @needs-validation so they are visible but not trusted.
"""
from __future__ import annotations

import re
from typing import Any

from ..models import ClaimKind, Confidence
from .base import Agent, Context

_SCEN_KINDS = (ClaimKind.BEHAVIOR, ClaimKind.RULE, ClaimKind.EXCEPTION, ClaimKind.STATE, ClaimKind.PERMISSION)


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


class Migration(Agent):
    name = "reversa-migration"
    role = ("Plan the migration of a legacy system from its operational specification: "
            "choose a strategy, design the target architecture, map risks from gaps, and "
            "write Gherkin parity scenarios that both the legacy and the target must pass. "
            "Each scenario must cite the claim ids it verifies.")
    output_schema = {
        "strategy": "<paragraphs: strategy, paradigm/topology decisions, cutover approach>",
        "target_architecture": "<paragraphs>",
        "risks": [{"id": "R-1", "description": "...", "severity": "high|medium|low", "mitigation": "...",
                   "related": ["GAP-001", "C-002"]}],
        "features": [{"unit": "...", "scenarios": [{"title": "...", "tags": ["@parity"], "claims": ["C-001"],
                                                    "given": ["..."], "when": ["..."], "then": ["..."]}]}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        cl = "\n".join(f"- [{c['id']}] ({c['unit']}, {c['kind']}, {c['confidence']}) {c['statement']}"
                       for c in payload["claims"])
        gaps = "\n".join(f"- [{g['id']}] ({g['severity']}) {g['description']}" for g in payload["gaps"]) or "- (none)"
        return (f"Target: {payload['target']}\n\nClaims:\n{cl}\n\nGaps:\n{gaps}\n\n"
                "Write the migration strategy, target architecture, risk register and one "
                "Gherkin scenario per behaviour/rule/exception claim. Tag scenarios for "
                "inferred claims with @needs-validation.")

    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        target = payload["target"]
        feats: dict[str, list] = {}
        for c in payload["claims"]:
            if c["kind"] not in {k.value for k in _SCEN_KINDS} or c["confidence"] == "gap":
                continue
            tags = ["@parity"] + (["@needs-validation"] if c["confidence"] == "inferred" else [])
            stmt = c["statement"].rstrip(".")
            if c["kind"] == "exception":
                sc = {"given": [f"the {c['unit']} unit is running in both legacy and {target}"],
                      "when": ["the triggering condition occurs"],
                      "then": [f"both implementations behave as: {stmt}",
                               "the message or error is identical in both"]}
            elif c["kind"] == "rule":
                sc = {"given": [f"an input that exercises: {stmt}"],
                      "when": ["the operation is executed on legacy and on " + target],
                      "then": ["both accept or reject the input identically",
                               "any resulting balances or outputs are identical"]}
            else:
                sc = {"given": [f"the {c['unit']} unit in both implementations"],
                      "when": ["the same user actions are replayed"],
                      "then": [f"both preserve: {stmt}"]}
            title = stmt if len(stmt) <= 120 else stmt[:117].rsplit(" ", 1)[0] + "..."
            sc.update({"title": title, "tags": tags, "claims": [c["id"]]})
            feats.setdefault(c["unit"], []).append(sc)
        risks = []
        for i, g in enumerate([g for g in payload["gaps"] if g["status"] == "open"], start=1):
            sev = {"critical": "high", "moderate": "medium"}.get(g["severity"], "low")
            risks.append({"id": f"R-{i}", "description": g["description"], "severity": sev,
                          "mitigation": "Resolve by documented owner decision before cutover; "
                                        "until then keep the behaviour behind a parity test marked pending.",
                          "related": [g["id"]]})
        n_inf = sum(1 for c in payload["claims"] if c["confidence"] == "inferred")
        if n_inf:
            risks.append({"id": f"R-{len(risks) + 1}", "severity": "medium",
                          "description": f"{n_inf} inferred claims may encode wrong assumptions about legacy behaviour.",
                          "mitigation": "Run @needs-validation scenarios against the legacy system first; "
                                        "promote to confirmed only on green.", "related": []})
        strategy = (f"Strategy: reimplement in {target} unit by unit, preserving the unit boundaries "
                    "recovered by discovery, with a parallel-run period in which legacy and target execute "
                    "the same parity scenarios. Paradigm: keep the procedural flow per unit initially "
                    "(one module per legacy unit) and refactor only after parity is green. Topology: single "
                    "process, same data stores migrated to a relational schema derived from the record layouts. "
                    "Cutover only when all @parity scenarios pass and no blocking gap remains open.")
        ta = (f"Target architecture: one {target} package per legacy unit; entry-point unit becomes the CLI/menu; "
              "shared utilities become a common library; each legacy file becomes a table whose columns mirror "
              "the 01-level record layout; parity tests live beside the code and run against both systems.")
        return {"strategy": strategy, "target_architecture": ta, "risks": risks,
                "features": [{"unit": u, "scenarios": s} for u, s in feats.items()]}

    def run(self, ctx: Context) -> None:
        reg = ctx.registry
        target = ctx.config.get("target", "the target language")
        units = {u.name for u in ctx.selected_units()}
        payload = {"target": target,
                   "claims": [c.to_dict() for c in reg.claims if c.unit in units or c.unit == "project"],
                   "gaps": [g.to_dict() for g in reg.gaps if g.unit in units or g.unit == "project"]}
        out = ctx.backend.generate(self, payload)
        self.record_warnings(ctx, out)
        n = 0
        for f in out.get("features", []):
            unit = str(f.get("unit", "project")).upper()
            lines = [f"@unit-{_slug(unit)}", f"Feature: {unit} parity",
                     f"  Legacy and {target} implementations must behave identically for {unit}.", ""]
            for s in f.get("scenarios", []):
                n += 1
                tags = " ".join(s.get("tags", ["@parity"]))
                claims = " ".join(f"@{c}" for c in s.get("claims", []))
                lines.append(f"  {tags} {claims}".rstrip())
                lines.append(f"  Scenario: {s.get('title', 'untitled')}")
                for kw in ("given", "when", "then"):
                    steps = s.get(kw, [])
                    for j, st in enumerate(steps):
                        word = kw.title() if j == 0 else "And"
                        lines.append(f"    {word} {st}")
                lines.append("")
            ctx.write(f"migration/parity/{unit.lower()}.feature", "\n".join(lines))
        risks = "\n".join(f"| {r['id']} | {r['severity']} | {r['description']} | {r.get('mitigation', '')} | "
                          f"{', '.join(r.get('related', []))} |" for r in out.get("risks", [])) or "| — | — | — | — | — |"
        ctx.write("migration/risk-register.md", f"""# Risk register

| Risk | Severity | Description | Mitigation | Related |
|---|---|---|---|---|
{risks}
""")
        ctx.write("migration/strategy.md", f"""# Migration strategy

## Strategy and decisions

{out.get('strategy', '')}

## Target architecture

{out.get('target_architecture', '')}

## Parity

{n} Gherkin scenarios generated under `migration/parity/`. Scenarios tagged `@needs-validation`
derive from inferred claims and must be run against the legacy system and reviewed before they
are trusted. Cutover requires all `@parity` scenarios green and no open blocking gap.
""")
        reg.meta["parity_scenarios"] = n
        ctx.log(f"  migration: {n} parity scenarios, {len(out.get('risks', []))} risks")

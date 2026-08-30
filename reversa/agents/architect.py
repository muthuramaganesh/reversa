"""reversa-architect: synthesise architecture, dependencies, data and impact."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from ..models import ClaimKind
from .base import Agent, Context

_DEP = re.compile(r"^(\S+) (?:depends on|calls external program) (\S+?)[ ,.(]", re.I)
_FILE = re.compile(r"assigned to '([^']+)'", re.I)


class Architect(Agent):
    name = "reversa-architect"
    role = ("Synthesise the architecture of the whole system from the unit-level "
            "claims: components and layers, the dependency graph, shared data stores, "
            "main flows, and an impact matrix (which units are affected if a unit or a "
            "data store changes). Only assert what the claims support.")
    output_schema = {
        "overview": "<architecture narrative, 1-3 paragraphs>",
        "layers": [{"name": "...", "units": ["..."]}],
        "flows": [{"name": "...", "steps": ["<unit or paragraph>", "..."]}],
        "claims": [{"kind": "architecture", "statement": "...", "confidence": "confirmed|inferred|gap",
                    "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}],
        "gaps": [{"description": "...", "severity": "critical|moderate|cosmetic|out_of_scope"}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        cl = "\n".join(f"- [{c['id']}] ({c['unit']}, {c['kind']}, {c['confidence']}) {c['statement']}"
                       for c in payload["claims"])
        return (f"Units: {', '.join(payload['units'])}\n\nEstablished claims:\n{cl}\n\n"
                "Describe the architecture, layers, main flows and cross-unit impacts. "
                "Reuse evidence from the claims above; do not invent new evidence.")

    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        units = payload["units"]
        entry = payload["entry_points"]
        deps = payload["edges"]
        layers = []
        if entry:
            layers.append({"name": "Entry / UI", "units": entry})
        shared = [u for u in units if u not in entry and payload["fan_in"].get(u, 0) >= 2]
        if shared:
            layers.append({"name": "Shared services", "units": shared})
        rest = [u for u in units if u not in entry and u not in shared]
        if rest:
            layers.append({"name": "Domain modules", "units": rest})
        flows = [{"name": f"Fan-out from {e} (call targets, not a sequence)",
                  "steps": [t for s, t in deps if s == e]} for e in entry]
        claims = []
        for u, n in payload["fan_in"].items():
            if n >= 2:
                claims.append({"kind": "architecture", "confidence": "inferred",
                               "statement": f"{u} is a shared utility: {n} units depend on it, so changes to it have system-wide impact.",
                               "evidence": []})
        for store, users in payload["stores"].items():
            if len(users) >= 2:
                claims.append({"kind": "architecture", "confidence": "inferred",
                               "statement": f"Data store '{store}' is shared by {', '.join(sorted(users))}; "
                                            f"they are coupled through the file layout, not through calls.",
                               "evidence": []})
        overview = (f"The system has {len(units)} units; entry point(s): {', '.join(entry) or 'undetermined'}. "
                    f"{len(deps)} call/import edges and {len(payload['stores'])} data stores were recovered. "
                    "Layering below is inferred from fan-in and entry points.")
        gaps = []
        if not entry:
            gaps.append({"description": "No entry point could be identified; startup flow is unknown.",
                         "severity": "critical"})
        return {"overview": overview, "layers": layers, "flows": flows, "claims": claims, "gaps": gaps}

    def run(self, ctx: Context) -> None:
        reg = ctx.registry
        units = [u.name for u in reg.units]
        edges: list[tuple[str, str]] = []
        stores: dict[str, set[str]] = defaultdict(set)
        for c in reg.claims:
            if c.kind == ClaimKind.DEPENDENCY:
                m = _DEP.match(c.statement)
                if m:
                    edges.append((m.group(1).upper(), m.group(2).upper()))
            if c.kind == ClaimKind.DATA:
                m = _FILE.search(c.statement)
                if m:
                    stores[m.group(1)].add(c.unit)
        edges = sorted(set(edges))
        fan_in: dict[str, int] = defaultdict(int)
        for _, t in edges:
            fan_in[t] += 1
        payload = {"units": units, "entry_points": [u.name for u in reg.units if u.entry_point],
                   "edges": edges, "fan_in": dict(fan_in), "stores": {k: set(v) for k, v in stores.items()},
                   "claims": [c.to_dict() for c in reg.claims]}
        out = ctx.backend.generate(self, payload)
        self.record_warnings(ctx, out)
        made = self.add_claims(ctx, "project", out.get("claims", []))
        for g in out.get("gaps", []):
            reg.add_gap(unit="project", description=g["description"], severity=g.get("severity", "moderate"),
                        blocking=g.get("severity") == "critical")
        reg.meta["architecture"] = {"layers": out.get("layers", []), "flows": out.get("flows", []),
                                    "edges": edges, "stores": {k: sorted(v) for k, v in stores.items()}}
        self._write(ctx, out, edges, stores, made)
        ctx.log(f"  architect: {len(edges)} edges, {len(stores)} data stores, {len(made)} claims")

    def _write(self, ctx: Context, out: dict[str, Any], edges, stores, claims) -> None:
        reg = ctx.registry
        units = [u.name for u in reg.units]
        mer = ["```mermaid", "graph TD"]
        for u in reg.units:
            shape = f"{u.name}([{u.name}])" if u.entry_point else f"{u.name}[{u.name}]"
            mer.append(f"  {shape}")
        for s, t in edges:
            mer.append(f"  {s} --> {t}")
        for store, users in stores.items():
            sid = "DS_" + re.sub(r"[^A-Za-z0-9]", "_", store)
            mer.append(f"  {sid}[({store})]")
            for u in sorted(users):
                mer.append(f"  {u} -.-> {sid}")
        mer.append("```")
        layers = "\n".join(f"- **{l['name']}**: {', '.join(l.get('units', []))}" for l in out.get("layers", []))
        flows = "\n".join(f"- **{f['name']}**: {' → '.join(f.get('steps', []))}" for f in out.get("flows", []))
        cl = "\n".join(f"- {'✅' if c.confidence.value=='confirmed' else '🟡' if c.confidence.value=='inferred' else '⛔'} "
                       f"**{c.id}** {c.statement}" for c in claims)
        ctx.write("architecture.md", f"""# Architecture

{out.get('overview', '')}

## Component and data-store graph

{chr(10).join(mer)}

## Layers (inferred)

{layers or '- (none)'}

## Main flows

{flows or '- (none)'}

## Architecture claims

{cl or '- (none)'}
""")
        # impact matrix: unit x unit (direct dependency or shared store)
        impact: dict[str, set[str]] = defaultdict(set)
        for s, t in edges:
            impact[t].add(s)          # changing t impacts s
        for store, users in stores.items():
            for a in users:
                for b in users:
                    if a != b:
                        impact[a].add(b)
        header = "| Change in ↓ / impacts → | " + " | ".join(units) + " |"
        sep = "|---|" + "---|" * len(units)
        rows = []
        for u in units:
            rows.append(f"| **{u}** | " + " | ".join("●" if v in impact[u] else "" for v in units) + " |")
        deps_rows = "\n".join(f"| {s} | {t} |" for s, t in edges) or "| — | — |"
        store_rows = "\n".join(f"| `{k}` | {', '.join(sorted(v))} |" for k, v in stores.items()) or "| — | — |"
        ctx.write("dependencies.md", f"""# Dependencies

## Call / import edges

| From | To |
|---|---|
{deps_rows}

## Shared data stores

| Store | Used by |
|---|---|
{store_rows}
""")
        ctx.write("traceability/spec-impact-matrix.md", f"""# Spec impact matrix

A ● in row U, column V means: a change to U's specification impacts V (V calls U, or they share a data store).

{header}
{sep}
{chr(10).join(rows)}
""")

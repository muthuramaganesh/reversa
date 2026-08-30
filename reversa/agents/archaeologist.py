"""reversa-archaeologist: deepen technical analysis of modules and structures."""
from __future__ import annotations

from typing import Any

from ..analysis import analyze, excerpt
from ..models import Confidence
from .base import Agent, Context


class Archaeologist(Agent):
    name = "reversa-archaeologist"
    role = ("Analyse one unit in depth: its internal structure (sections, paragraphs, "
            "functions), data structures and record layouts, files/tables it reads or "
            "writes, inputs and outputs, and control flow between its parts. Classify "
            "technical facts. Do not interpret business meaning; that is the detective's job.")
    output_schema = {
        "summary": "<3-6 sentences on what this unit is technically>",
        "claims": [{"kind": "structure|data|dependency", "statement": "...",
                    "confidence": "confirmed|inferred|gap",
                    "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}],
        "gaps": [{"description": "...", "severity": "critical|moderate|cosmetic|out_of_scope"}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        src = "\n\n".join(f"=== {p} ===\n{txt}" for p, txt in payload["sources"].items())
        return (f"Unit: {payload['unit']}\n\nSource (numbered lines):\n{src}\n\n"
                "Produce technical claims about structure, data and I/O with exact "
                "line evidence. Register a gap for anything you cannot determine "
                "(e.g. copybooks or tables referenced but not present).")

    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        claims, gaps = [], []
        unit = payload["unit"]
        for path, ff in payload["facts"].items():
            L = payload["lines"][path]
            ev = lambda ln: [{"file": path, "line_start": ln, "line_end": ln, "excerpt": excerpt(L, ln)}]
            paras = ff.of("paragraph", "section", "function", "class")
            if paras:
                names = ", ".join(p.name for p in paras[:12]) + (" …" if len(paras) > 12 else "")
                claims.append({"kind": "structure", "confidence": "confirmed",
                               "statement": f"{unit} is organised into {len(paras)} {paras[0].kind}s: {names}.",
                               "evidence": [{"file": path, "line_start": paras[0].line,
                                             "line_end": paras[-1].line, "excerpt": excerpt(L, paras[0].line)}]})
            for s in ff.of("select"):
                org = s.extra.get("organization") or "unspecified organization"
                claims.append({"kind": "data", "confidence": "confirmed",
                               "statement": f"{unit} declares file {s.name} assigned to '{s.detail}' ({org}).",
                               "evidence": ev(s.line)})
            for fd in ff.of("fd"):
                claims.append({"kind": "data", "confidence": "confirmed",
                               "statement": f"{unit} defines file record description {fd.name}.",
                               "evidence": ev(fd.line)})
            ws = [r for r in ff.of("record") if r.detail == "working-storage"]
            lk = [r for r in ff.of("record") if r.detail == "linkage"]
            if lk:
                claims.append({"kind": "structure", "confidence": "confirmed",
                               "statement": f"{unit} receives parameters through LINKAGE: "
                                            + ", ".join(r.name for r in lk) + ".",
                               "evidence": [{"file": path, "line_start": lk[0].line, "line_end": lk[-1].line,
                                             "excerpt": excerpt(L, lk[0].line)}]})
            if ws:
                claims.append({"kind": "data", "confidence": "confirmed",
                               "statement": f"{unit} working storage has {len(ws)} top-level records: "
                                            + ", ".join(r.name for r in ws[:10]) + (" …" if len(ws) > 10 else "") + ".",
                               "evidence": [{"file": path, "line_start": ws[0].line, "line_end": ws[-1].line,
                                             "excerpt": excerpt(L, ws[0].line)}]})
            ops: dict[str, set[str]] = {}
            for io in ff.of("io"):
                ops.setdefault(io.name, set()).add(io.detail)
            for fname, verbs in ops.items():
                first = next(i for i in ff.of("io") if i.name == fname)
                claims.append({"kind": "data", "confidence": "confirmed",
                               "statement": f"{unit} performs {', '.join(sorted(verbs))} on {fname}.",
                               "evidence": ev(first.line)})
            acc = ff.of("accept")
            if acc:
                claims.append({"kind": "structure", "confidence": "confirmed",
                               "statement": f"{unit} reads interactive input into: "
                                            + ", ".join(sorted({a.name for a in acc})) + ".",
                               "evidence": ev(acc[0].line)})
            for p in ff.of("perform"):
                if not any(x.name == p.name for x in paras):
                    gaps.append({"description": f"{unit} PERFORMs '{p.name}' at {path}:{p.line} but no such "
                                                f"paragraph was found in the unit; possibly in a copybook or a parse miss.",
                                 "severity": "moderate"})
            if not paras and not ff.of("select") and not ws:
                gaps.append({"description": f"No recognisable structure extracted from {path}; manual reading required.",
                             "severity": "moderate"})
        summary = (f"{unit} has {len([c for c in claims if c['kind']=='structure'])} structural and "
                   f"{len([c for c in claims if c['kind']=='data'])} data facts extracted by static analysis.")
        return {"summary": summary, "claims": claims, "gaps": gaps}

    def run(self, ctx: Context) -> None:
        proj, reg = ctx.project, ctx.registry
        for u in ctx.selected_units():
            facts = {p: analyze(p, next(i.language for i in reg.inventory if i.path == p), proj.lines(p))
                     for p in u.files}
            payload = {"unit": u.name, "sources": {p: proj.numbered(p) for p in u.files},
                       "facts": facts, "lines": {p: proj.lines(p) for p in u.files}}
            out = ctx.backend.generate(self, payload)
            self.record_warnings(ctx, out, u.name)
            made = self.add_claims(ctx, u.name, out.get("claims", []))
            for g in out.get("gaps", []):
                reg.add_gap(unit=u.name, description=g["description"],
                            severity=g.get("severity", "moderate"),
                            blocking=g.get("severity") == "critical")
            if out.get("summary") and not u.description:
                u.description = str(out["summary"]).split(". ")[0][:140]
            self._write(ctx, u.name, out.get("summary", ""), made)
            ctx.log(f"  archaeologist: {u.name}: {len(made)} claims")

    def _write(self, ctx: Context, unit: str, summary: str, claims) -> None:
        rows = "\n".join(
            f"| {c.id} | {c.kind.value} | {c.confidence.value} | {c.statement} | "
            f"{'; '.join(e.ref() for e in c.evidence) or '—'} |" for c in claims)
        ctx.write(f"analysis/{unit.lower()}.md", f"""# Technical analysis — {unit}

{summary}

| Claim | Kind | Confidence | Statement | Evidence |
|---|---|---|---|---|
{rows}
""")

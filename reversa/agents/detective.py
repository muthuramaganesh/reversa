"""reversa-detective: extract business rules, states, permissions, exceptions."""
from __future__ import annotations

import re
from typing import Any

from ..analysis import analyze, excerpt, ERROR_WORDS
from .base import Agent, Context

_NUM = re.compile(r"(?<![\w-])(\d+(?:[.,]\d+)?)(?![\w-])")
_CMP = re.compile(r"(>=|<=|=|>|<|\bNOT\s*=|\bGREATER\b|\bLESS\b|\bEQUAL\b|\bMOD\b)", re.I)


class Detective(Agent):
    name = "reversa-detective"
    role = ("Recover the *business* knowledge hidden in one unit: rules (validations, "
            "limits, calculations), states and transitions, permissions, and the "
            "operational exceptions the code handles. Separate what the code literally "
            "does (confirmed) from what it probably means (inferred). Record every "
            "unexplained constant, undocumented branch or silent failure as a gap or a "
            "question for the human owner.")
    output_schema = {
        "claims": [{"kind": "rule|state|permission|exception|behavior", "statement": "...",
                    "confidence": "confirmed|inferred|gap",
                    "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}],
                    "notes": "<why it is confirmed/inferred>"}],
        "states": [{"name": "...", "transitions": ["<from> -> <to> on <event>"]}],
        "gaps": [{"description": "...", "severity": "critical|moderate|cosmetic|out_of_scope", "blocking": False}],
        "questions": [{"question": "...", "why_it_matters": "..."}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        src = "\n\n".join(f"=== {p} ===\n{txt}" for p, txt in payload["sources"].items())
        known = "\n".join(f"- {c}" for c in payload["technical_claims"]) or "- (none)"
        return (f"Unit: {payload['unit']}\n\nTechnical facts already established:\n{known}\n\n"
                f"Source (numbered lines):\n{src}\n\n"
                "Extract business rules, states, permissions and exceptions. For each "
                "rule cite the exact lines. When the meaning of a constant or message is "
                "not evident from code, mark the claim inferred and add a question.")

    # ---- offline -----------------------------------------------------------
    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        unit = payload["unit"]
        claims, gaps, questions, states = [], [], [], []
        seen_consts: set[str] = set()
        for path, ff in payload["facts"].items():
            L = payload["lines"][path]
            ev = lambda a, b=None: [{"file": path, "line_start": a, "line_end": b or a, "excerpt": excerpt(L, a)}]
            messages = ff.of("message")
            for cond in ff.of("condition"):
                text = cond.name.strip()
                where = f" in {cond.detail}" if cond.detail else ""
                # literal restatement of the code => confirmed
                claims.append({"kind": "rule", "confidence": "confirmed",
                               "statement": f"Branch guarded by `{text}`{where}.",
                               "evidence": ev(cond.line), "notes": "literal condition in code"})
                # interpretation using the nearest error message => inferred
                near = [m for m in messages if 0 < m.line - cond.line <= 4]
                if near and _CMP.search(text):
                    claims.append({"kind": "exception", "confidence": "inferred",
                                   "statement": f"When `{text}` holds, the operation is rejected with message "
                                                f"\"{near[0].name}\".",
                                   "evidence": ev(cond.line, near[0].line),
                                   "notes": "message follows the condition; rejection semantics inferred"})
                for n in _NUM.findall(text):
                    if n in ("0", "1") or n in seen_consts:
                        continue
                    seen_consts.add(n)
                    questions.append({"related_claim_index": len(claims) - 1,
                                      "question": f"In {unit}, the constant {n} appears in `{text}` "
                                                  f"({path}:{cond.line}). Is it a business limit, a technical "
                                                  f"constant, or configurable?",
                                      "why_it_matters": "Limits must be preserved (or consciously changed) in any reimplementation."})
            for d in ff.of("dispatch"):
                cases = [c for c in ff.of("case") if c.line > d.line and c.detail == d.detail]
                opts = ", ".join(c.name for c in cases[:8])
                claims.append({"kind": "behavior", "confidence": "confirmed",
                               "statement": f"{unit} dispatches on `{d.name}` with cases: {opts}.",
                               "evidence": ev(d.line, cases[-1].line if cases else d.line),
                               "notes": "EVALUATE/switch structure"})
                if cases:
                    states.append({"name": d.name, "transitions": [f"{d.name} -> case {c.name}" for c in cases[:8]]})
            for m in messages:
                if not any(0 < m.line - c.line <= 4 for c in ff.of("condition")):
                    claims.append({"kind": "exception", "confidence": "confirmed",
                                   "statement": f"{unit} can emit the message \"{m.name}\".",
                                   "evidence": ev(m.line), "notes": "literal DISPLAY/raise"})
            # permissions: any PIN/password/senha/auth handling
            for a in ff.of("accept"):
                if re.search(r"(senha|pin|pass|auth|login|usuario|user)", a.name, re.I):
                    claims.append({"kind": "permission", "confidence": "inferred",
                                   "statement": f"{unit} appears to authenticate the user via input {a.name}.",
                                   "evidence": ev(a.line), "notes": "name-based inference"})
                    questions.append({"related_claim_index": len(claims) - 1,
                                      "question": f"How is {a.name} validated in {unit}, and what happens after "
                                                  f"repeated failures (lockout, retry limit)?",
                                      "why_it_matters": "Authentication behaviour is security-relevant and must be paritied exactly."})
            if not ff.of("condition") and not ff.of("dispatch"):
                gaps.append({"description": f"No decision logic detected in {path}; business rules for {unit} "
                                            f"may live elsewhere (data, configuration, copybooks).",
                             "severity": "moderate", "blocking": False})
        # dedupe questions on constants across files
        return {"claims": claims, "states": states, "gaps": gaps, "questions": questions}

    # ---- run -----------------------------------------------------------------
    def run(self, ctx: Context) -> None:
        proj, reg = ctx.project, ctx.registry
        all_states: dict[str, list] = {}
        for u in ctx.selected_units():
            facts = {p: analyze(p, next(i.language for i in reg.inventory if i.path == p), proj.lines(p))
                     for p in u.files}
            payload = {"unit": u.name, "sources": {p: proj.numbered(p) for p in u.files},
                       "facts": facts, "lines": {p: proj.lines(p) for p in u.files},
                       "technical_claims": [c.statement for c in reg.claims_for(u.name)]}
            out = ctx.backend.generate(self, payload)
            self.record_warnings(ctx, out, u.name)
            made = self.add_claims(ctx, u.name, out.get("claims", []))
            for g in out.get("gaps", []):
                reg.add_gap(unit=u.name, description=g["description"],
                            severity=g.get("severity", "moderate"), blocking=bool(g.get("blocking")))
            for q in out.get("questions", []):
                related = [c for c in q.get("related_claims", []) if any(m.id == c for m in made)]
                idx = q.get("related_claim_index")
                if isinstance(idx, int) and 0 <= idx < len(made):
                    related.append(made[idx].id)
                reg.add_question(unit=u.name, question=q["question"],
                                 why_it_matters=q.get("why_it_matters", ""), related_claims=related)
            all_states[u.name] = out.get("states", [])
            ctx.log(f"  detective: {u.name}: {len(made)} claims, {len(out.get('questions', []))} questions")
        self._write(ctx, all_states)

    def _write(self, ctx: Context, states: dict[str, list]) -> None:
        reg = ctx.registry
        parts = ["# Domain rules, states and exceptions\n"]
        for u in ctx.selected_units():
            cs = [c for c in reg.claims_for(u.name) if c.produced_by == self.name]
            if not cs:
                continue
            parts.append(f"\n## {u.name}\n")
            for kind in ("rule", "behavior", "state", "permission", "exception"):
                sub = [c for c in cs if c.kind.value == kind]
                if not sub:
                    continue
                parts.append(f"\n### {kind.title()}s\n")
                for c in sub:
                    tag = {"confirmed": "✅", "inferred": "🟡", "gap": "⛔"}[c.confidence.value]
                    refs = "; ".join(e.ref() for e in c.evidence) or "—"
                    parts.append(f"- {tag} **{c.id}** {c.statement} _({c.confidence.value}; {refs})_")
            st = states.get(u.name) or []
            if st:
                parts.append("\n### State machines\n")
                for s in st:
                    parts.append(f"- **{s.get('name')}**")
                    for t in s.get("transitions", []):
                        parts.append(f"  - {t}")
        parts.append("\nLegend: ✅ confirmed · 🟡 inferred · ⛔ gap\n")
        ctx.write("rules.md", "\n".join(parts))

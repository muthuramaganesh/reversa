"""reversa-reviewer: review claims, confidence and gaps for human validation.

Two passes (paper §3.5):
  1. Mechanical: every evidence reference is re-checked against the source.
     A confirmed claim whose excerpt cannot be found is downgraded to inferred;
     a claim with no evidence at all is downgraded to gap. This is independent
     of the backend and always runs.
  2. Semantic (backend): inferred claims are challenged against the code; the
     backend may confirm, keep, or downgrade them and add questions.
Outputs: confidence-report.md, gaps.md, questions.md.
"""
from __future__ import annotations

from typing import Any

from ..confidence import distribution, distribution_by_unit, traceability_density, verify_evidence
from ..models import Confidence
from .base import Agent, Context


class Reviewer(Agent):
    name = "reversa-reviewer"
    role = ("Challenge the claims produced by the other agents. For each inferred "
            "claim, go back to the cited code and decide: confirm (only with exact "
            "evidence), keep as inferred, or downgrade to gap. Never upgrade without "
            "evidence. Then write the questions a human owner must answer before the "
            "specification can be trusted for migration.")
    output_schema = {
        "reclassify": [{"id": "C-001", "confidence": "confirmed|inferred|gap", "reason": "..."}],
        "questions": [{"unit": "...", "question": "...", "why_it_matters": "...", "related_claims": ["C-001"]}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        cl = "\n".join(f"- [{c['id']}] ({c['unit']}) {c['statement']} | evidence: "
                       + ("; ".join(f"{e['file']}:{e['line_start']}-{e['line_end']} «{e['excerpt']}»" for e in c["evidence"]) or "none")
                       for c in payload["inferred"])
        src = "\n\n".join(f"=== {p} ===\n{txt}" for p, txt in payload["sources"].items())
        ans = "\n".join(f"- [{a['id']}] ({a['unit']}; claims {', '.join(a['related_claims']) or '—'}) "
                        f"Q: {a['question']} A: {a['answer']}" for a in payload.get("answers", [])) or "- (none yet)"
        return (f"Inferred claims to challenge:\n{cl}\n\nAnswers already given by the system owner "
                f"(you may confirm a claim on the strength of an answer, citing the answer id in reason):\n{ans}\n\n"
                f"Source (numbered lines):\n{src}\n\n"
                "Reclassify only where the code or an owner answer justifies it, and list the "
                "questions a human must still answer. Do not repeat questions that already have answers.")

    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        # Offline the semantic pass adds nothing beyond the mechanical pass;
        # it just turns every remaining inferred claim into a validation question.
        qs = []
        answered = {cid for a in payload.get("answers", []) for cid in a.get("related_claims", [])}
        for c in payload["inferred"]:
            if c["id"] in answered:
                continue
            qs.append({"unit": c["unit"], "related_claims": [c["id"]],
                       "question": f"Please confirm or correct: {c['statement']}",
                       "why_it_matters": "This claim is inferred from patterns, not directly evidenced."})
        return {"reclassify": [], "questions": qs}

    def run(self, ctx: Context) -> None:
        proj, reg = ctx.project, ctx.registry
        # ---- pass 1: mechanical evidence verification ------------------------
        down_inf = down_gap = 0
        for c in reg.claims:
            if c.confidence == Confidence.GAP:
                continue
            if not c.evidence:
                if c.confidence == Confidence.CONFIRMED:
                    c.confidence = Confidence.INFERRED
                    c.review = "downgraded: no evidence"
                    down_inf += 1
                continue
            results = [verify_evidence(proj.root, e) for e in c.evidence]
            if not any(ok for ok, _ in results):
                if c.confidence == Confidence.CONFIRMED:
                    c.confidence = Confidence.INFERRED
                    c.review = "downgraded: " + "; ".join(r for _, r in results)
                    down_inf += 1
                else:
                    c.confidence = Confidence.GAP
                    c.review = "downgraded to gap: evidence unverifiable (" + "; ".join(r for _, r in results) + ")"
                    reg.add_gap(unit=c.unit, description=f"{c.id}: {c.statement} — evidence could not be verified.",
                                severity="moderate", related_claims=[c.id])
                    down_gap += 1
            else:
                c.review = c.review or "evidence verified"
        # ---- pass 2: semantic challenge of inferred claims ------------------
        inferred = [c for c in reg.claims if c.confidence == Confidence.INFERRED]
        files = sorted({e.file for c in inferred for e in c.evidence})
        payload = {"inferred": [c.to_dict() for c in inferred],
                   "sources": {p: proj.numbered(p) for p in files},
                   "answers": [q.to_dict() for q in reg.questions if q.answer]}
        out = ctx.backend.generate(self, payload) if inferred else {"reclassify": [], "questions": []}
        self.record_warnings(ctx, out)
        by_id = {c.id: c for c in reg.claims}
        for r in out.get("reclassify", []):
            c = by_id.get(r.get("id"))
            if not c:
                continue
            try:
                new = Confidence(r["confidence"])
            except (KeyError, ValueError):
                continue
            if new == Confidence.CONFIRMED and not (c.evidence and any(
                    verify_evidence(proj.root, e)[0] for e in c.evidence)):
                continue  # refuse upgrade without verified evidence (an owner answer alone is not code)
            if new != c.confidence:
                c.review = f"reviewer: {c.confidence.value} -> {new.value}: {r.get('reason', '')}"
                c.confidence = new
                if new == Confidence.GAP:
                    reg.add_gap(unit=c.unit, description=f"{c.id}: {c.statement} — {r.get('reason', '')}",
                                severity="moderate", related_claims=[c.id])
        for q in out.get("questions", []):
            reg.add_question(unit=q.get("unit", "project"), question=q["question"],
                             why_it_matters=q.get("why_it_matters", ""),
                             related_claims=[x for x in q.get("related_claims", []) if x in by_id])
        self._write(ctx, down_inf, down_gap)
        d = distribution(reg.claims)
        ctx.log(f"  reviewer: {d.total} claims → {d.confirmed} confirmed / {d.inferred} inferred / "
                f"{d.gap} gap · index {d.index:.1%} · {len(reg.gaps)} gaps · {len(reg.questions)} questions")

    def _write(self, ctx: Context, down_inf: int, down_gap: int) -> None:
        reg = ctx.registry
        total = distribution(reg.claims)
        rows = "\n".join(f"| {u} | {d.confirmed} | {d.inferred} | {d.gap} | {d.index:.1%} |"
                         for u, d in distribution_by_unit(reg.claims).items())
        blocking = [g for g in reg.gaps if g.blocking and g.status == "open"]
        reviewed = [c for c in reg.claims if c.review and not c.review.startswith("evidence verified")]
        rev_rows = "\n".join(f"| {c.id} | {c.unit} | {c.confidence.value} | {c.review} |" for c in reviewed) or "| — | — | — | — |"
        ctx.write("confidence-report.md", f"""# Confidence report

Internal confidence index: **{total.index:.1%}** over {total.total} claims
({total.confirmed} confirmed, {total.inferred} inferred, {total.gap} gaps).
Traceability density: {traceability_density(reg.claims):.2f} evidence refs per claim.

> The index summarises the classification assigned by the pipeline (confirmed = 1.0,
> inferred = 0.5, gap = 0). It is **not** factual accuracy: no external audit of the
> claims has been performed. Treat inferred claims as hypotheses.

## By unit

| Unit | Confirmed | Inferred | Gap | Index |
|---|---|---|---|---|
{rows}
| **Total** | **{total.confirmed}** | **{total.inferred}** | **{total.gap}** | **{total.index:.1%}** |

## Review actions

- Confirmed claims downgraded to inferred (evidence not found / missing): {down_inf}
- Inferred claims downgraded to gap (evidence unverifiable): {down_gap}
- Blocking gaps open: {len(blocking)}

| Claim | Unit | Now | Review note |
|---|---|---|---|
{rev_rows}
""")
        sev_order = {"critical": 0, "moderate": 1, "cosmetic": 2, "out_of_scope": 3}
        gaps = sorted(reg.gaps, key=lambda g: (sev_order[g.severity.value], g.unit, g.id))
        g_rows = "\n".join(f"| {g.id} | {g.unit} | {g.severity.value} | {'yes' if g.blocking else ''} | "
                           f"{g.status} | {g.description} | {g.resolution} |" for g in gaps) or "| — | — | — | — | — | — | — |"
        counts = {s: sum(1 for g in reg.gaps if g.severity.value == s) for s in sev_order}
        ctx.write("gaps.md", f"""# Gaps

{len(reg.gaps)} gaps registered: {counts['critical']} critical, {counts['moderate']} moderate,
{counts['cosmetic']} cosmetic, {counts['out_of_scope']} out of scope. Blocking gaps must be
resolved by a documented human decision before migration cutover.

To resolve a gap, edit its **Status** and **Resolution** columns (or answer via `reversa answer`).

| Gap | Unit | Severity | Blocking | Status | Description | Resolution |
|---|---|---|---|---|---|---|
{g_rows}
""")
        q_rows = "\n".join(f"### {q.id} ({q.unit})\n\n**Q:** {q.question}\n\n_Why it matters:_ {q.why_it_matters}  \n"
                           f"_Related claims:_ {', '.join(q.related_claims) or '—'}\n\n**A:** {q.answer or '_(pending)_'}\n"
                           for q in reg.questions) or "_(no questions)_"
        ctx.write("questions.md", f"""# Questions for the system owner

{len(reg.questions)} questions. Answers feed back into the specification: answering a question
lets the reviewer confirm or drop the related inferred claims.

{q_rows}
""")

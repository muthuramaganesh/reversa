"""reversa-detective: extract business rules, states, permissions, exceptions."""
from __future__ import annotations

import re
from typing import Any

from ..analysis import (analyze, excerpt, ERROR_WORDS, condition_english,
                         case_value_english, field_english, value_english,
                         branch_outcome)
from .base import Agent, Context
from .. import specbuilder

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
            if ff.language == "cobol":
                sp = specbuilder.build(path, L)
                claims += specbuilder.to_claims(sp)
                gaps += specbuilder.to_gaps(sp)
                questions += specbuilder.to_questions(sp)
                for t in sp.tables:
                    states.append({"name": f"{t.id} {t.subject} ({t.kind})",
                                   "transitions": [f"{lab} -> {res}" for lab, res, _ in t.rows]})
                continue
            ev = lambda a, b=None: [{"file": path, "line_start": a, "line_end": b or a, "excerpt": excerpt(L, a)}]
            messages = ff.of("message")
            consumed_message_lines: set[int] = set()
            for cond in ff.of("condition"):
                text = cond.name.strip()
                plain = condition_english(text)
                technical = f"Branch guarded by `{text}`" + (f" in {cond.detail}" if cond.detail else "") + "."
                outcome = branch_outcome(L, cond.line)
                if outcome and outcome[0] == "move":
                    _, field, value, mline = outcome
                    stmt = (f"If {plain}, then the {field_english(field)} is set to "
                            f"{value_english(value)}.")
                    claims.append({"kind": "rule", "confidence": "confirmed",
                                   "statement": stmt, "evidence": ev(cond.line, mline),
                                   "notes": technical})
                elif outcome and outcome[0] == "continue":
                    stmt = f"If {plain}, no further action is taken."
                    claims.append({"kind": "rule", "confidence": "confirmed",
                                   "statement": stmt, "evidence": ev(cond.line, outcome[3]),
                                   "notes": technical})
                elif outcome and outcome[0] == "message":
                    # the message is INSIDE this branch structurally (depth-tracked),
                    # not merely nearby -- this replaces the old proximity guess,
                    # which could pair a condition with a message from a sibling branch.
                    msg_text, _, mline = outcome[1], outcome[2], outcome[3]
                    consumed_message_lines.add(mline)
                    stmt = (f"If {plain}, the operation is rejected with the message "
                            f"\"{msg_text}\".")
                    claims.append({"kind": "rule", "confidence": "inferred",
                                   "statement": stmt, "evidence": ev(cond.line, mline),
                                   "notes": technical + " rejection semantics inferred from "
                                                        "the DISPLAY inside this branch, not literal."})
                else:
                    # no MOVE, no CONTINUE, no message within the branch: the condition
                    # itself is confirmed, but what happens as a result is not.
                    claims.append({"kind": "rule", "confidence": "confirmed",
                                   "statement": f"The process checks whether {plain}.",
                                   "evidence": ev(cond.line), "notes": technical})
                    gaps.append({"description": f"In {unit} ({path}:{cond.line}), the condition "
                                                f"`{text}` is confirmed, but its outcome (what "
                                                f"happens when it holds) could not be determined "
                                                f"from the code within the branch -- inspect "
                                                f"manually.",
                                 "severity": "moderate", "blocking": False})
                for n in _NUM.findall(text):
                    if n in ("0", "1") or n in seen_consts:
                        continue
                    seen_consts.add(n)
                    questions.append({"related_claim_index": len(claims) - 1,
                                      "question": f"In {unit}, the constant {n} appears in `{text}` "
                                                  f"({path}:{cond.line}). Is it a business limit, a technical "
                                                  f"constant, or configurable?",
                                      "why_it_matters": "Limits must be preserved (or consciously changed) in any reimplementation."})
            dispatches = sorted(ff.of("dispatch"), key=lambda x: x.line)
            for idx, d in enumerate(dispatches):
                # bound the case list by the NEXT dispatch in the same paragraph, so two
                # EVALUATE blocks sharing a paragraph don't get merged into one rule.
                next_dispatch_line = next((nd.line for nd in dispatches[idx + 1:]
                                           if nd.detail == d.detail), float("inf"))
                cases = [c for c in ff.of("case")
                         if d.line < c.line < next_dispatch_line and c.detail == d.detail]
                # subject: for EVALUATE <FIELD>, the field itself. For EVALUATE TRUE
                # (COBOL's common "switch over independent flags" idiom), derive the
                # subject from a prefix shared by the case names, e.g. CH-CARD /
                # CH-WALLET / CH-BANK share "CH-" -> subject is "channel", values
                # are "card" / "wallet" / "bank".
                shared_prefix = ""
                if d.name.upper() == "TRUE" and len(cases) > 1:
                    names = [c.name.strip("'\"") for c in cases
                             if re.match(r"^[A-Z0-9][A-Z0-9-]*$", c.name, re.I)]
                    if len(names) == len(cases):
                        parts_lists = [n.upper().split("-") for n in names]
                        i = 0
                        while all(len(p) > i + 1 for p in parts_lists) and \
                              len({p[i] for p in parts_lists}) == 1:
                            i += 1
                        if i > 0:
                            shared_prefix = "-".join(parts_lists[0][:i]) + "-"
                subject = (field_english(shared_prefix.rstrip("-")) if shared_prefix
                          else (field_english(d.name) if re.match(r"^[A-Z0-9-]+$", d.name, re.I) else None))
                lines_out, transitions = [], []
                for cidx, c in enumerate(cases[:8]):
                    case_end = cases[cidx + 1].line if cidx + 1 < len(cases) else next_dispatch_line
                    if case_end == float("inf"):
                        # last case of the last dispatch in this paragraph: bound by
                        # the nearest END-EVALUATE after this WHEN, else a small window.
                        m = None
                        for ln in range(c.line, min(len(L), c.line + 20)):
                            if _END_EVAL.match(L[ln] if ln < len(L) else ""):
                                m = ln + 1
                                break
                        case_end = m or (c.line + 15)
                    outcome = case_outcome(L, c.line, case_end)
                    value_label = (c.name.strip("'\"")[len(shared_prefix):]
                                  if shared_prefix and c.name.upper().startswith(shared_prefix)
                                  else None)
                    cond_txt = (value_label.lower() if value_label else case_value_english(c.name))
                    lead = f"the {subject} is " if subject else ""
                    if outcome:
                        field, value, _ = outcome
                        lines_out.append(f"when {lead}{cond_txt}, the {field_english(field)} "
                                         f"is set to {value_english(value)}")
                        transitions.append(f"{d.name} = {c.name} -> {field} = {value}")
                    else:
                        lines_out.append(f"when {lead}{cond_txt}, the outcome could not be determined")
                        transitions.append(f"{d.name} = {c.name} -> ?")
                subj_phrase = f"the {subject}" if subject else f"`{d.name}`"
                stmt = f"A decision table in {unit} keys off {subj_phrase}: " + "; ".join(lines_out) + "."
                claims.append({"kind": "behavior", "confidence": "confirmed",
                               "statement": stmt,
                               "evidence": ev(d.line, cases[-1].line if cases else d.line),
                               "notes": f"EVALUATE `{d.name}` at {path}:{d.line}"})
                if cases:
                    states.append({"name": d.name, "transitions": transitions})
            # messages already paired with a branch (via branch_outcome, above) are
            # excluded here by exact line, not proximity, so a message can't be
            # reported twice or attributed to the wrong condition.
            for m in messages:
                if m.line in consumed_message_lines:
                    continue
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
        self._specs: dict[str, list] = {}
        for u in ctx.selected_units():
            facts = {p: analyze(p, next(i.language for i in reg.inventory if i.path == p), proj.lines(p))
                     for p in u.files}
            # deterministic structural spec for COBOL, independent of the backend
            self._specs[u.name] = [specbuilder.build(p, proj.lines(p)) for p in u.files
                                   if facts[p].language == "cobol"]
            call = getattr(ctx.backend, "_call", None)
            if callable(call):   # AI backend configured: apply the plain-English rewriting prompt
                for sp in self._specs[u.name]:
                    n = specbuilder.rewrite_rules(sp, call)
                    ctx.log(f"  detective: {u.name}: {n}/{len(sp.rules)} rules rewritten in plain English")
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
        specs = [sp for u in ctx.selected_units() for sp in getattr(self, "_specs", {}).get(u.name, [])]
        if specs:
            ctx.write("ops_spec.md", specbuilder.render_ops_spec(specs))
            ctx.write("gaps_contradictions.md", specbuilder.render_gaps(specs))
<<<<<<< HEAD
=======
            ctx.write("process_flow.md", specbuilder.render_process(specs))
            import json as _json, os as _os
            rules_json = specbuilder.to_json(specs)
            ctx.write("rules.json", _json.dumps(rules_json, indent=2, default=str))
            std_path = _os.environ.get("REVERSA_STANDARDS")
            if std_path and _os.path.exists(std_path):
                from .. import standards as _std
                try:
                    cmp = _std.compare(rules_json, _std.load_standard(std_path))
                    ctx.write("comparison.json", _json.dumps(cmp, indent=2, default=str))
                    ctx.write("comparison.md", _std.render_md(cmp))
                    _std.write_xlsx(cmp, ctx.out_dir / "comparison.xlsx")
                    ctx.log(f"  detective: standards comparison: {cmp['summary']}")
                except Exception as e:      # never fail the run because of the standards file
                    ctx.log(f"  detective: standards comparison skipped: {e}")
>>>>>>> 5f57dba (Reversa: hybrid backend, formatted Word export, analysis-mode docs)
        parts = [specbuilder.render_rules(specs)] if specs else ["# Domain rules, states and exceptions\n"]
        spec_units = {u for u, sps in getattr(self, "_specs", {}).items() if sps}
        for u in ctx.selected_units():
            if u.name in spec_units:
                continue          # already rendered as BA tables above
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
                    if c.notes:
                        parts.append(f"  <details><summary>Technical detail</summary>{c.notes}</details>")
            st = states.get(u.name) or []
            if st:
                parts.append("\n### Decision tables\n")
                parts.append("_A decision table looks up an outcome by a field's value "
                             "(e.g. a fee percentage by payment channel). It is not a state "
                             "machine: nothing here transitions between statuses over time._\n")
                for s in st:
                    parts.append(f"- **{s.get('name')}**")
                    for t in s.get("transitions", []):
                        parts.append(f"  - {t}")
        if not specs:
            parts.append("\nLegend: ✅ confirmed · 🟡 inferred · ⛔ gap\n")
        ctx.write("rules.md", "\n".join(parts))

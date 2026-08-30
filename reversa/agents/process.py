"""reversa-process: reconstruct end-to-end operational/business processes.

Sits between Architect and Writer. Where the Detective recovers rules *inside*
a unit and the Architect recovers the graph *between* units, this agent walks
the two together: from each entry-point dispatch (menu option, command, route)
through PERFORM/CALL chains, collecting the decisions, messages and data
effects along the way. Output: `processes.md`, one process per user-visible
operation, every step traced to code, plus process-level claims so the Writer
and Migration teams can reference them.
"""
from __future__ import annotations

import re
from typing import Any

from ..analysis import analyze, excerpt, pic_english, aborts_in_branch, FileFacts, Fact
from .base import Agent, Context

_CALL_ARG = re.compile(r"CALL\s+['\"]([A-Z0-9-]+)['\"]\s+USING\s+['\"]([A-Z0-9])['\"]", re.I)
_MOVE = re.compile(r"^\s*MOVE\s+(.+?)\s+TO\s+([A-Z0-9-]+)", re.I)


def _plain(name: str) -> str:
    """Turn a COBOL-ish identifier into readable words, keeping the identifier in brackets."""
    words = name.replace("WS-", "").replace("LK-", "").replace("CLI-", "").replace("MOV-", "")
    words = words.replace("-", " ").lower()
    if words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"):
        return name
    return f"{words} ({name})"


def _cond_english(cond: str) -> str:
    c = cond.strip()
    c = re.sub(r"\bNOT\s*=", "is not", c, flags=re.I)
    c = re.sub(r"\s>=\s", " is at least ", c)
    c = re.sub(r"\s<=\s", " is at most ", c)
    c = re.sub(r"\s>\s", " is greater than ", c)
    c = re.sub(r"\s<\s", " is less than ", c)
    c = re.sub(r"\s=\s", " equals ", c)
    c = re.sub(r"FUNCTION MOD\((\S+),\s*(\d+)\)", r"the remainder of \1 divided by \2", c, flags=re.I)
    for ident in sorted(set(re.findall(r"[A-Z]{2,}(?:-[A-Z0-9]+)+", c)), key=len, reverse=True):
        c = c.replace(ident, _plain(ident))
    return c


def narrate(proc: dict) -> str:
    """Plain-English paragraph built mechanically from the steps (heuristic backend)."""
    out = [f"This process starts when {proc.get('trigger', 'it is triggered')}."]
    steps = proc.get("steps", [])
    i = 0
    while i < len(steps):
        st = steps[i]
        k, a = st.get("kind"), st.get("action", "")
        if k == "call":
            if a.startswith("Call "):
                m = re.match(r"Call (\S+)(?: with operation '(\S)')?", a)
                unit, op = m.group(1), m.group(2)
                nxt = steps[i + 1] if i + 1 < len(steps) else None
                if nxt and nxt.get("action", "").startswith(f"{unit} dispatches"):
                    para = nxt["action"].split()[-1]
                    out.append(f"{st['unit']} hands over to {unit}" + (f" with operation code '{op}'" if op else "")
                               + f", which runs its {para} routine.")
                    i += 2
                    continue
                out.append(f"{st['unit']} calls {unit}" + (f" with operation code '{op}'" if op else "") + ".")
            elif a.startswith("Perform "):
                out.append(f"It then runs the {a.split()[1]} routine.")
            elif "dispatches" in a:
                out.append(f"{a}.")
        elif k == "input":
            m = re.match(r"Take input (\S+)(?: \(prompt \"(.+)\"\))?", a)
            var, prompt = m.group(1), m.group(2)
            out.append((f"The system prompts \"{prompt}\" and reads " if prompt else "The system reads ") + f"{_plain(var)}.")
        elif k == "decision":
            cond = _cond_english(a.replace("Check ", "").strip("`"))
            t = st.get("outcome_if_true", "")
            if t.startswith("show"):
                msg = re.search(r'"(.+?)"', t)
                out.append(f"If {cond}, the system shows the message \"{msg.group(1) if msg else t}\""
                           + (" and the operation stops." if "abort" in t else "."))
            else:
                out.append(f"If {cond}, it {t}; otherwise it continues.")
        elif k == "message":
            out.append(f"It may show the message {a.replace('Show ', '')}.")
        elif k == "data":
            verb, fname = a.split(" ", 1)
            what = {"REWRITE": f"updates the existing {_plain(fname)} record",
                    "WRITE": f"writes a new {_plain(fname)} record",
                    "READ": f"reads a {_plain(fname)} record",
                    "DELETE": f"deletes a {_plain(fname)} record"}.get(verb, f"{verb.lower()}s {fname}")
            out.append(f"It {what}.")
        elif k == "output":
            if a.startswith("Set "):
                out.append(f"It {a[0].lower() + a[1:]}.")
            else:
                out.append(f"It displays {a.replace('Display ', '')}.")
        i += 1
    n_dec = sum(1 for s in steps if s.get("kind") == "decision")
    n_data = sum(1 for s in steps if s.get("kind") == "data" and not s.get("action", "").startswith("READ"))
    if steps:
        out.append(f"In total the process applies {n_dec} check(s) and makes {n_data} change(s) to stored data.")
    return " ".join(out)


def business_context(facts: dict, lines: dict, unit_of: dict, processes: list[dict], entry_points: list[str]) -> dict:
    """Assemble a plain-English business context from record layouts, constants and rules."""
    # entities: one per file-section record (FD), fields with PIC
    entities, seen_rec = [], set()
    stores = {}
    for path, ff in facts.items():
        for sel in ff.of("select"):
            stores[sel.name] = sel.detail
        for rec in ff.of("record"):
            if rec.detail != "file" or rec.name in seen_rec:
                continue
            seen_rec.add(rec.name)
            fd = next((f.name for f in reversed(ff.of("fd")) if f.line < rec.line), "")
            fields = [{"name": f.name, "meaning": _plain(f.name).split(" (")[0],
                       "type": pic_english(f.extra.get("pic", ""))}
                      for f in ff.of("field") if f.detail == rec.name]
            entities.append({"entity": (fd.lower() + " record") if fd else _plain(rec.name).split(" (")[0], "record": rec.name,
                             "store": stores.get(fd, fd), "fields": fields,
                             "evidence": [{"file": path, "line_start": rec.line, "line_end": rec.line,
                                           "excerpt": excerpt(lines[path], rec.line)}]})
    # parameters: working-storage constants with a VALUE
    params = []
    for path, ff in facts.items():
        for c in ff.of("constant"):
            if c.extra.get("section") != "working-storage":
                continue
            val = c.detail.strip("'\"")
            if not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", val) or float(val.replace(",", ".")) == 0:
                continue  # zero-initialised counters are not business parameters
            plist = ff.of("paragraph")
            paras = set()
            for k, pg in enumerate(plist):
                end = plist[k + 1].line - 1 if k + 1 < len(plist) else len(lines[path])
                if any(c.name in lines[path][j] for j in range(pg.line, end)):
                    paras.add(pg.name)
            paras = sorted(paras)
            params.append({"name": c.name, "value": val, "meaning": _plain(c.name).split(" (")[0],
                           "where_used": f"{unit_of[path]}" + (f" ({', '.join(paras)})" if paras else ""),
                           "evidence": [{"file": path, "line_start": c.line, "line_end": c.line,
                                         "excerpt": excerpt(lines[path], c.line)}]})
    # rules: every decision step across processes, in English
    rules, seen_rules = [], set()
    for pr in processes:
        for st in pr.get("steps", []):
            if st.get("kind") != "decision":
                continue
            cond = _cond_english(st["action"].replace("Check ", "").strip("`"))
            t = st.get("outcome_if_true", "")
            msg = re.search(r'"(.+?)"', t)
            text = (f"If {cond}, the system rejects the operation with \"{msg.group(1)}\"." if msg and "abort" in t
                    else f"If {cond}, the system shows \"{msg.group(1)}\"." if msg
                    else f"If {cond}, the system {t.replace('take the', 'takes the')}; otherwise it continues.")
            key = (text, pr["name"])
            if key in seen_rules:
                continue
            seen_rules.add(key)
            rules.append({"rule": text, "applies_to": pr["name"], "confidence": "confirmed",
                          "evidence": st.get("evidence", [])})
    # actors
    actors = [{"actor": "user (interactive)", "how": f"operates {', '.join(entry_points) or 'the entry point'} through prompts and a menu"}]
    if any(f.kind == "call" and f.name == "KBDREAD" for ff in facts.values() for f in ff.facts):
        actors.append({"actor": "user (secret entry)", "how": "enters a secret via a masked keyboard routine (KBDREAD)"})
    what = (f"This is an interactive, single-user system operated from {', '.join(entry_points) or 'one entry point'}. "
            f"It keeps {len(entities)} kind(s) of record ({', '.join(e['record'] for e in entities) or 'none found'}) "
            f"in {len(stores)} data store(s) ({', '.join(f'{k} → {v}' for k, v in stores.items()) or 'none found'}), "
            f"offers {len([p for p in processes if 'start-up' not in p['name']])} user operation(s), "
            f"enforces {len(rules)} rule(s) and carries {len(params)} numeric parameter(s) fixed in the code. "
            "The wording here describes the code's structure; what the records and operations mean to the "
            "business (e.g. that SAQUE is a cash withdrawal) is a reading of names and messages, not something "
            "the code states, and should be confirmed by the system owner.")
    not_in_code = []
    if not any("LOG" in n or "AUDIT" in n for n in seen_rec):
        not_in_code.append("No audit/log record beyond the movement file was found.")
    if not any(f.kind == "condition" and re.search(r"DATA|DATE|HORA|TIME", f.name, re.I) for ff in facts.values() for f in ff.facts):
        not_in_code.append("No date/time-based rule (cut-off, business day, daily limit reset) was found; limits appear to be per operation, not per day.")
    if not any(f.kind in ("io",) and f.detail.startswith("OPEN") and "LOCK" in f.name for ff in facts.values() for f in ff.facts):
        not_in_code.append("No locking or concurrency handling was found; the code assumes a single user at a time.")
    return {"what_it_is": what, "who_uses_it": actors, "what_it_manages": entities,
            "business_rules": rules, "parameters": params, "not_in_code": not_in_code}


def overview_text(processes: list[dict], entry_points: list[str]) -> str:
    if not processes:
        return "No user-triggerable processes could be reconstructed from the code."
    names = [p["name"] for p in processes]
    ep = ", ".join(entry_points) or "the entry point"
    lines = [f"The system is operated from {ep}. A user can perform {len(names)} operation(s): "
             + "; ".join(names) + "."]
    checks = sum(1 for p in processes for s in p.get("steps", []) if s.get("kind") == "decision")
    writes = sum(1 for p in processes for s in p.get("steps", []) if s.get("kind") == "data"
                 and not s.get("action", "").startswith("READ"))
    stores = sorted({s["action"].split(" ", 1)[1] for p in processes for s in p.get("steps", []) if s.get("kind") == "data"})
    lines.append(f"Across these operations the code applies {checks} validation check(s) and makes {writes} write(s) "
                 f"to stored data" + (f" in: {', '.join(stores)}." if stores else "."))
    lines.append("Process names below are taken from the code's own labels; their business meaning "
                 "(what a routine called SAQUE is *for*) is a reading of the code, not something the code states. "
                 "Each step in the tables cites the line it comes from.")
    return " ".join(lines)


class ProcessAgent(Agent):
    name = "reversa-process"
    role = ("Reconstruct the end-to-end operational processes a user or operator experiences: "
            "start from each entry point and follow the control flow across units, recording "
            "at each step the actor, the inputs taken, the decisions made (with their outcomes), "
            "the messages shown, and the data written. Name each process by its business "
            "meaning only when the code makes it evident; otherwise keep the technical name and "
            "mark the meaning inferred.")
    output_schema = {
        "business_context": {
            "what_it_is": "<2-4 sentences: what kind of system this is and what it is for, for a reader with no code knowledge>",
            "who_uses_it": [{"actor": "...", "how": "..."}],
            "what_it_manages": [{"entity": "<business name>", "record": "<code name>", "store": "<file/table>",
                                 "fields": [{"name": "...", "meaning": "...", "type": "..."}]}],
            "business_rules": [{"rule": "<plain English>", "applies_to": "<process>", "confidence": "confirmed|inferred",
                                "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}],
            "parameters": [{"name": "...", "value": "...", "meaning": "...", "where_used": "..."}],
            "not_in_code": ["<things a business reader would expect that the code does not show>"]},
        "overview": "<plain-English description of what the system does for its users, 1-2 paragraphs, "
                    "readable by a business owner with no programming knowledge>",
        "processes": [{"name": "<business name>", "technical_name": "<dispatch case / paragraph>",
                       "trigger": "<how it starts>", "actor": "<who>", "outcome": "<end state>",
                       "description": "<plain-English narrative of the process, one paragraph: what the user does, "
                                      "what the system checks, what it rejects and why, what it records>",
                       "confidence": "confirmed|inferred",
                       "steps": [{"n": 1, "unit": "...", "action": "<what happens>",
                                  "kind": "input|decision|message|data|call|output",
                                  "outcome_if_true": "<for decisions>", "outcome_if_false": "<for decisions>",
                                  "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}]}],
        "claims": [{"kind": "behavior", "statement": "...", "confidence": "confirmed|inferred",
                    "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}],
        "gaps": [{"description": "...", "severity": "critical|moderate|cosmetic|out_of_scope"}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        src = "\n\n".join(f"=== {p} ===\n{txt}" for p, txt in payload["sources"].items())
        cl = "\n".join(f"- [{c['id']}] ({c['unit']}, {c['kind']}) {c['statement']}" for c in payload["claims"])
        return (f"Entry points: {', '.join(payload['entry_points'])}\n\nKnown claims:\n{cl}\n\n"
                f"Source (numbered lines):\n{src}\n\n"
                "Reconstruct every end-to-end process a user can trigger. Follow CALL/PERFORM "
                "across units. Each step needs evidence. Decisions must state both outcomes. "
                "Also write an overview and a per-process description in plain English for a "
                "business reader: name things by what they mean to the user (e.g. 'withdrawal', "
                "'PIN', 'daily limit'), not by variable names; put the variable name in brackets "
                "the first time only. Where the meaning of a name is a guess, say 'appears to'.")

    # ---- offline -----------------------------------------------------------
    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        facts: dict[str, FileFacts] = payload["facts"]          # path -> facts
        lines: dict[str, list[str]] = payload["lines"]
        unit_of: dict[str, str] = payload["unit_of_file"]       # path -> unit
        file_of: dict[str, str] = {u: p for p, u in unit_of.items()}
        processes, claims, gaps = [], [], []

        def ev(path: str, a: int, b: int | None = None):
            return [{"file": path, "line_start": a, "line_end": b or a, "excerpt": excerpt(lines[path], a)}]

        def para_facts(path: str, para: str) -> list[Fact]:
            ff = facts[path]
            names = [f for f in ff.facts if f.kind == "paragraph"]
            start = next((f.line for f in names if f.name == para), None)
            if start is None:
                return []
            after = [f.line for f in names if f.line > start]
            end = min(after) if after else 10 ** 9
            return [f for f in ff.facts if start < f.line < end and f.kind != "paragraph"]

        def walk(path: str, para: str, steps: list, depth: int, seen: set) -> None:
            if depth > 6 or (path, para) in seen:
                return
            seen.add((path, para))
            unit = unit_of[path]
            pf = para_facts(path, para)
            i = 0
            while i < len(pf):
                f = pf[i]
                if f.kind == "accept":
                    prompt = next((d.name for d in pf[max(0, i - 2):i] if d.kind == "display"), "")
                    steps.append({"unit": unit, "kind": "input", "evidence": ev(path, f.line),
                                  "action": f"Take input {f.name}" + (f' (prompt "{prompt}")' if prompt else "")})
                elif f.kind == "condition":
                    msg = next((m for m in pf[i + 1:i + 4] if m.kind == "message"), None)
                    stop = aborts_in_branch(lines[path], f.line - 1)
                    steps.append({"unit": unit, "kind": "decision", "action": f"Check `{f.name}`",
                                  "outcome_if_true": (f'show "{msg.name}"' if msg else "take the guarded branch")
                                  + (" and abort the operation" if stop else ""),
                                  "outcome_if_false": "continue",
                                  "evidence": ev(path, f.line, msg.line if msg else f.line)})
                elif f.kind == "message" and not any(c.kind == "condition" and 0 < f.line - c.line <= 4 for c in pf):
                    steps.append({"unit": unit, "kind": "message", "action": f'Show "{f.name}"', "evidence": ev(path, f.line)})
                elif f.kind == "io" and f.detail in ("WRITE", "REWRITE", "DELETE"):
                    steps.append({"unit": unit, "kind": "data", "action": f"{f.detail} {f.name}", "evidence": ev(path, f.line)})
                elif f.kind == "io" and f.detail == "READ":
                    steps.append({"unit": unit, "kind": "data", "action": f"READ {f.name}", "evidence": ev(path, f.line)})
                elif f.kind == "perform":
                    steps.append({"unit": unit, "kind": "call", "action": f"Perform {f.name}", "evidence": ev(path, f.line)})
                    walk(path, f.name, steps, depth + 1, seen)
                elif f.kind == "call":
                    tgt = file_of.get(f.name)
                    m = _CALL_ARG.search(lines[path][f.line - 1])
                    arg = m.group(2).upper() if m else None
                    steps.append({"unit": unit, "kind": "call", "evidence": ev(path, f.line),
                                  "action": f"Call {f.name}" + (f" with operation '{arg}'" if arg else "")})
                    if tgt:
                        # jump into the callee: follow the dispatch case matching the literal argument
                        tf = facts[tgt]
                        entry = next((p.name for p in tf.of("paragraph")), None)
                        if arg:
                            case = next((c for c in tf.of("case") if c.name.strip("'\"").upper() == arg), None)
                            nxt = next((p for p in tf.of("perform") if case and p.line == case.line + 1), None)
                            if nxt:
                                steps.append({"unit": unit_of[tgt], "kind": "call", "evidence": ev(tgt, case.line, nxt.line),
                                              "action": f"{f.name} dispatches '{arg}' to {nxt.name}"})
                                walk(tgt, nxt.name, steps, depth + 1, seen)
                                i += 1
                                continue
                        if entry:
                            walk(tgt, entry, steps, depth + 1, seen)
                    else:
                        gaps.append({"description": f"Process step calls {f.name} ({path}:{f.line}) but its source is not "
                                                    f"in the inventory; the process cannot be followed past this point.",
                                     "severity": "critical"})
                elif f.kind == "display" and f.detail and not f.name.endswith(":"):
                    steps.append({"unit": unit, "kind": "output", "action": f'Display "{f.name}"', "evidence": ev(path, f.line)})
                i += 1

        for ep in payload["entry_points"]:
            path = file_of.get(ep)
            if not path:
                continue
            ff = facts[path]
            # 1. pre-dispatch process: everything performed from the first paragraph before the loop
            first = next((p.name for p in ff.of("paragraph")), None)
            dispatches = ff.of("dispatch")
            if first:
                pre_steps: list = []
                pf = para_facts(path, first)
                for f in pf:
                    if f.kind == "perform" and not any(d.detail == f.name for d in dispatches):
                        walk(path, f.name, pre_steps, 1, set())
                    elif f.kind == "condition":
                        msg = next((m for m in ff.facts if m.kind == "message" and 0 < m.line - f.line <= 4), None)
                        pre_steps.append({"unit": ep, "kind": "decision", "action": f"Check `{f.name}`",
                                          "outcome_if_true": (f'show "{msg.name}"' if msg else "take the guarded branch")
                                          + (" and abort the operation" if aborts_in_branch(lines[path], f.line - 1) else ""),
                                          "outcome_if_false": "continue", "evidence": ev(path, f.line)})
                if pre_steps:
                    processes.append({"name": f"{ep} start-up (login / session setup)", "technical_name": first,
                                      "trigger": f"{ep} is executed", "actor": "user", "confidence": "inferred",
                                      "outcome": "session established or aborted", "steps": pre_steps})
            # 2. one process per dispatch case
            for d in dispatches:
                cases = [c for c in ff.of("case") if c.line > d.line and c.detail == d.detail]
                for c in cases:
                    if c.name.upper() == "OTHER":
                        continue
                    steps: list = []
                    nxt = [x for x in ff.facts if c.line < x.line <= c.line + 2 and x.kind in ("perform", "call", "message", "display")]
                    for ln in range(c.line + 1, min(c.line + 3, len(lines[path]) + 1)):
                        mv = _MOVE.match(lines[path][ln - 1])
                        if mv:
                            steps.append({"unit": ep, "kind": "output", "evidence": ev(path, ln),
                                          "action": f"Set {mv.group(2).upper()} to {mv.group(1)}"})
                    for x in nxt:
                        if x.kind == "perform":
                            steps.append({"unit": ep, "kind": "call", "action": f"Perform {x.name}", "evidence": ev(path, x.line)})
                            walk(path, x.name, steps, 1, set())
                        elif x.kind == "call":
                            # reuse walk logic by walking a synthetic single-fact paragraph
                            tmp: list = []
                            saved = para_facts
                            m = _CALL_ARG.search(lines[path][x.line - 1])
                            arg = m.group(2).upper() if m else None
                            tgt = file_of.get(x.name)
                            steps.append({"unit": ep, "kind": "call", "evidence": ev(path, x.line),
                                          "action": f"Call {x.name}" + (f" with operation '{arg}'" if arg else "")})
                            if tgt:
                                tf = facts[tgt]
                                case = next((cc for cc in tf.of("case") if arg and cc.name.strip("'\"").upper() == arg), None)
                                nx = next((p for p in tf.of("perform") if case and p.line == case.line + 1), None)
                                if nx:
                                    steps.append({"unit": unit_of[tgt], "kind": "call", "evidence": ev(tgt, case.line, nx.line),
                                                  "action": f"{x.name} dispatches '{arg}' to {nx.name}"})
                                    walk(tgt, nx.name, steps, 1, set())
                                else:
                                    entry = next((p.name for p in tf.of("paragraph")), None)
                                    if entry:
                                        walk(tgt, entry, steps, 1, set())
                            else:
                                gaps.append({"description": f"Menu option {c.name} calls {x.name} but its source is missing.",
                                             "severity": "critical"})
                        else:
                            steps.append({"unit": ep, "kind": "message" if x.kind == "message" else "output",
                                          "action": f'Show "{x.name}"', "evidence": ev(path, x.line)})
                    label = c.name
                    first = next((k for k, s in enumerate(steps) if s["kind"] == "call"), None)
                    if first is not None:
                        words = steps[first]["action"].split()
                        label = words[1]
                        if first + 1 < len(steps) and steps[first + 1]["action"].startswith(f"{label} dispatches"):
                            label = steps[first + 1]["action"].split()[-1]
                    elif steps and steps[0]["kind"] == "output":
                        label = steps[0]["action"]
                    n_dec = sum(1 for s in steps if s["kind"] == "decision")
                    n_data = sum(1 for s in steps if s["kind"] == "data")
                    processes.append({"name": f"Option {c.name}: {label}", "technical_name": f"{d.name} WHEN {c.name} → {label}",
                                      "trigger": f"user selects {c.name} at the {ep} menu", "actor": "user",
                                      "confidence": "confirmed",
                                      "outcome": f"{n_dec} validations; {n_data} data effects" if steps else "unknown",
                                      "steps": steps})
                    if steps:
                        claims.append({"kind": "behavior", "confidence": "confirmed",
                                       "statement": f"Selecting {c.name} at {ep} runs {label} with {n_dec} validation(s) "
                                                    f"and {n_data} data write(s)/read(s).",
                                       "evidence": ev(path, c.line)})
        if not processes:
            gaps.append({"description": "No entry-point dispatch found; processes could not be reconstructed.",
                         "severity": "critical"})
        for pr in processes:
            pr["description"] = narrate(pr)
        return {"business_context": business_context(facts, lines, unit_of, processes, payload["entry_points"]),
                "overview": overview_text(processes, payload["entry_points"]),
                "processes": processes, "claims": claims, "gaps": gaps}

    # ---- run -----------------------------------------------------------------
    def run(self, ctx: Context) -> None:
        proj, reg = ctx.project, ctx.registry
        unit_of = {p: u.name for u in reg.units for p in u.files}
        lang = {f.path: f.language for f in reg.inventory}
        facts = {p: analyze(p, lang[p], proj.lines(p)) for p in unit_of}
        payload = {"entry_points": [u.name for u in reg.units if u.entry_point],
                   "facts": facts, "lines": {p: proj.lines(p) for p in unit_of}, "unit_of_file": unit_of,
                   "sources": {p: proj.numbered(p) for p in unit_of},
                   "claims": [c.to_dict() for c in reg.claims if c.kind.value in ("behavior", "rule", "exception", "dependency")]}
        out = ctx.backend.generate(self, payload)
        self.record_warnings(ctx, out)
        made = self.add_claims(ctx, "project", out.get("claims", []))
        for g in out.get("gaps", []):
            reg.add_gap(unit="project", description=g["description"], severity=g.get("severity", "moderate"),
                        blocking=g.get("severity") == "critical")
        reg.meta["processes"] = out.get("processes", [])
        reg.meta["process_overview"] = out.get("overview", "")
        reg.meta["business_context"] = out.get("business_context", {})
        self._write(ctx, out.get("processes", []), out.get("overview", ""))
        self._write_context(ctx, out.get("business_context", {}) or {}, out.get("processes", []))
        ctx.log(f"  process: {len(out.get('processes', []))} processes, {len(made)} claims")

    def _write_context(self, ctx: Context, bc: dict[str, Any], processes: list[dict[str, Any]]) -> None:
        def refs(evs):
            return "; ".join(f"`{e['file']}:{e['line_start']}`" for e in (evs or [])) or "—"
        parts = ["# Business context\n",
                 "_A plain-English orientation for people who will never read the code. "
                 "Read this before `processes.md`. Where a statement interprets the code rather than "
                 "restates it, it says so; open questions for the owner are in `questions.md`._\n",
                 "## What this system is\n", bc.get("what_it_is", "_(not determined)_"), "",
                 "## Who uses it\n"]
        for a in bc.get("who_uses_it", []) or []:
            parts.append(f"- **{a.get('actor')}** — {a.get('how')}")
        parts.append("\n## What it manages\n")
        for e in bc.get("what_it_manages", []) or []:
            parts.append(f"### {e.get('entity')} (`{e.get('record')}`" + (f", stored in `{e.get('store')}`" if e.get("store") else "") + ")\n")
            if e.get("fields"):
                parts.append("| Field | Meaning | Type |\n|---|---|---|")
                for f in e["fields"]:
                    parts.append(f"| `{f.get('name')}` | {f.get('meaning')} | {f.get('type')} |")
            if e.get("evidence"):
                parts.append(f"\n_Evidence: {refs(e['evidence'])}_")
            parts.append("")
        parts.append("## What a user can do\n")
        for p in processes:
            if "start-up" in p.get("name", ""):
                continue
            parts.append(f"- **{p.get('name')}** — {p.get('trigger', '')}. "
                         f"{sum(1 for s in p.get('steps', []) if s.get('kind') == 'decision')} check(s), "
                         f"{sum(1 for s in p.get('steps', []) if s.get('kind') == 'data' and not s.get('action', '').startswith('READ'))} data change(s).")
        parts.append("\n## Business rules the code enforces\n")
        parts.append("| # | Rule | Applies to | Confidence | Evidence |\n|---|---|---|---|---|")
        for i, r in enumerate(bc.get("business_rules", []) or [], start=1):
            parts.append(f"| {i} | {r.get('rule')} | {r.get('applies_to')} | {r.get('confidence', '')} | {refs(r.get('evidence'))} |")
        parts.append("\n## Business parameters fixed in the code\n")
        parts.append("These are numbers hard-coded in the program. Each one is a decision someone made; "
                     "in a reimplementation each should be confirmed, and probably made configurable.\n")
        parts.append("| Parameter | Value | Meaning (from name) | Where used | Evidence |\n|---|---|---|---|---|")
        for pm in bc.get("parameters", []) or []:
            parts.append(f"| `{pm.get('name')}` | {pm.get('value')} | {pm.get('meaning')} | {pm.get('where_used')} | {refs(pm.get('evidence'))} |")
        nic = bc.get("not_in_code", []) or []
        if nic:
            parts.append("\n## What a business reader might expect but the code does not show\n")
            for n in nic:
                parts.append(f"- {n}")
        ctx.write("business-context.md", "\n".join(parts))

    def _write(self, ctx: Context, processes: list[dict[str, Any]], overview: str = "") -> None:
        parts = ["# Operational processes\n",
                 "_For the business orientation (what the system is, who uses it, what it manages, its rules "
                 "and parameters) read `business-context.md` first._\n",
                 "## Overview\n", overview or "_(no overview)_", "",
                 "## Process summary\n",
                 "| Process | Trigger | Checks | Data changes | Confidence |", "|---|---|---|---|---|"]
        for p in processes:
            n_dec = sum(1 for s in p.get("steps", []) if s.get("kind") == "decision")
            n_w = sum(1 for s in p.get("steps", []) if s.get("kind") == "data" and not s.get("action", "").startswith("READ"))
            parts.append(f"| {p.get('name')} | {p.get('trigger', '')} | {n_dec} | {n_w} | {p.get('confidence', '')} |")
        parts.append("\n## Processes in detail\n"
                     "Each process has a plain-English description followed by the exact steps. "
                     "Each step cites the line it comes from; decisions show both outcomes. "
                     "The *steps* are confirmed; the *names and descriptions* interpret them.\n")
        icon = {"input": "⌨️", "decision": "❓", "message": "⚠️", "data": "💾", "call": "→", "output": "🖥️"}
        for p in processes:
            tag = "✅" if p.get("confidence") == "confirmed" else "🟡"
            parts.append(f"\n## {tag} {p.get('name')}\n")
            parts.append(f"- Technical: `{p.get('technical_name', '')}`  \n- Trigger: {p.get('trigger', '')}  \n"
                         f"- Actor: {p.get('actor', '')}  \n- Outcome: {p.get('outcome', '')}\n")
            if p.get("description"):
                parts.append(f"**Description.** {p['description']}\n")
            parts.append("**Steps.**\n")
            parts.append("| # | Unit | Step | If true | If false | Evidence |\n|---|---|---|---|---|---|")
            for i, s in enumerate(p.get("steps", []), start=1):
                refs = "; ".join(f"`{e['file']}:{e['line_start']}" + (f"-{e['line_end']}" if e.get('line_end', e['line_start']) != e['line_start'] else "") + "`"
                                 for e in s.get("evidence", []))
                parts.append(f"| {i} | {s.get('unit', '')} | {icon.get(s.get('kind'), '')} {s.get('action', '')} | "
                             f"{s.get('outcome_if_true', '')} | {s.get('outcome_if_false', '')} | {refs} |")
            # mermaid flow of decisions
            dec = [s for s in p.get("steps", []) if s.get("kind") == "decision"]
            if dec:
                parts.append("\n```mermaid\nflowchart TD")
                parts.append(f'  S(["{p.get("trigger", "start")}"])')
                prev = "S"
                for j, s in enumerate(dec):
                    nid = f"D{j}"
                    cond = s["action"].replace("Check ", "").replace("`", "").replace('"', "'")
                    parts.append(f'  {nid}{{"{cond}"}}')
                    parts.append(f"  {prev} --> {nid}")
                    out_t = str(s.get("outcome_if_true", "")).replace('"', "'")
                    if len(out_t) > 60:
                        out_t = out_t[:57].rsplit(" ", 1)[0] + "..."
                    parts.append(f'  {nid} -- yes --> E{j}["{out_t}"]')
                    prev = nid
                parts.append(f'  {prev} -- no --> OK(["{p.get("outcome", "done")}"])')
                parts.append("```")
        if not processes:
            parts.append("\n_(no processes reconstructed — see gaps.md)_")
        ctx.write("processes.md", "\n".join(parts))

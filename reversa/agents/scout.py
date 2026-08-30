"""reversa-scout: map project surface, stack, dependencies and entry points."""
from __future__ import annotations

from collections import Counter
from typing import Any

from ..analysis import analyze, excerpt
from ..models import Unit
from .base import Agent, Context


class Scout(Agent):
    name = "reversa-scout"
    role = ("Map the surface of a legacy project: languages and stack, how files "
            "group into units (programs, modules, services, screens), entry points, "
            "and which units call which. Produce an evidence-backed initial inventory. "
            "Do not analyse internals yet; that is the archaeologist's job.")
    output_schema = {
        "stack": ["<language or technology>"],
        "units": [{"name": "<unit>", "files": ["<rel path>"], "kind": "program|module|service|screen|library|data",
                   "entry_point": True, "description": "<one line>"}],
        "claims": [{"kind": "structure|dependency", "statement": "...", "confidence": "confirmed|inferred|gap",
                    "evidence": [{"file": "...", "line_start": 1, "line_end": 1, "excerpt": "..."}]}],
        "gaps": [{"description": "...", "severity": "critical|moderate|cosmetic|out_of_scope"}],
    }

    def user_prompt(self, payload: dict[str, Any]) -> str:
        listing = "\n".join(f"- {f['path']} ({f['language']}, {f['lines']} lines)"
                            for f in payload["inventory"])
        heads = "\n\n".join(f"=== {p} ===\n{txt}" for p, txt in payload["heads"].items())
        return (f"Project: {payload['project_name']}\n\nFile inventory:\n{listing}\n\n"
                f"First lines of each code file (numbered):\n{heads}\n\n"
                "Group the files into units, identify entry points, and list "
                "cross-unit dependencies (CALL, import, include, HTTP, shared files).")

    # ---- offline -----------------------------------------------------------
    def heuristic(self, payload: dict[str, Any]) -> dict[str, Any]:
        inv = payload["inventory"]
        facts_by = payload["facts"]
        lines_by = payload["lines"]
        stack = [l for l, _ in Counter(f["language"] for f in inv).most_common()]
        units, claims, gaps = [], [], []
        known_units: set[str] = set()
        for f in inv:
            if f["path"] not in facts_by:
                continue
            ff = facts_by[f["path"]]
            prog = ff.first("program")
            name = (prog.name if prog else f["path"].rsplit("/", 1)[-1].rsplit(".", 1)[0]).upper()
            known_units.add(name)
            is_entry = bool(ff.of("stop")) and not any(
                o["path"] != f["path"] and any(c.name == name for c in facts_by[o["path"]].of("call"))
                for o in inv if o["path"] in facts_by)
            kind = "program" if prog else ("library" if f["language"] in ("cobol-copybook",) else "module")
            units.append({"name": name, "files": [f["path"]], "kind": kind,
                          "entry_point": is_entry, "description": ""})
            if prog:
                claims.append({"kind": "structure", "confidence": "confirmed",
                               "statement": f"Unit {name} is a COBOL program declared in {f['path']}.",
                               "evidence": [{"file": f["path"], "line_start": prog.line,
                                             "line_end": prog.line,
                                             "excerpt": excerpt(lines_by[f["path"]], prog.line)}]})
        # dependencies
        for f in inv:
            if f["path"] not in facts_by:
                continue
            ff = facts_by[f["path"]]
            src = next(u["name"] for u in units if f["path"] in u["files"])
            seen = set()
            for c in ff.of("call", "import"):
                tgt = c.name.upper()
                if tgt in seen:
                    continue
                seen.add(tgt)
                ev = [{"file": f["path"], "line_start": c.line, "line_end": c.line,
                       "excerpt": excerpt(lines_by[f["path"]], c.line)}]
                if c.kind == "call" and tgt not in known_units:
                    claims.append({"kind": "dependency", "confidence": "inferred",
                                   "statement": f"{src} calls external program {tgt}, which is not in the inventory.",
                                   "evidence": ev})
                    gaps.append({"description": f"{src} calls '{tgt}' but no source for {tgt} was found; "
                                                f"its behaviour cannot be specified from this repository.",
                                 "severity": "critical", "unit": src})
                else:
                    claims.append({"kind": "dependency", "confidence": "confirmed",
                                   "statement": f"{src} depends on {tgt} ({c.kind}).", "evidence": ev})
        return {"stack": stack, "units": units, "claims": claims, "gaps": gaps}

    # ---- run -----------------------------------------------------------------
    def run(self, ctx: Context) -> None:
        proj, reg = ctx.project, ctx.registry
        reg.inventory = proj.inventory()
        code = proj.code_files(reg.inventory)
        facts = {f.path: analyze(f.path, f.language, proj.lines(f.path)) for f in code}
        payload = {
            "project_name": proj.root.name,
            "inventory": [f.__dict__ for f in reg.inventory],
            "heads": {f.path: proj.numbered(f.path, 40) for f in code},
            "facts": facts,
            "lines": {f.path: proj.lines(f.path) for f in code},
        }
        out = ctx.backend.generate(self, payload)
        self.record_warnings(ctx, out)
        reg.meta["stack"] = out.get("stack", [])
        reg.units = []
        for u in out.get("units", []):
            files = [p for p in u.get("files", []) if any(i.path == p for i in reg.inventory)]
            if not files:
                continue
            reg.units.append(Unit(name=str(u["name"]).upper(), files=files,
                                  kind=u.get("kind", "module"),
                                  entry_point=bool(u.get("entry_point")),
                                  description=u.get("description", "")))
        # unit attribution for claims: by the file of the first evidence
        for r in out.get("claims", []):
            unit = self._unit_for(reg, r)
            self.add_claims(ctx, unit, [r])
        for g in out.get("gaps", []):
            reg.add_gap(unit=g.get("unit", "project"), description=g["description"],
                        severity=g.get("severity", "moderate"),
                        blocking=g.get("severity") == "critical")
        self._write_inventory(ctx)
        ctx.log(f"  scout: {len(reg.inventory)} files, {len(reg.units)} units, "
                f"{len(reg.claims)} claims")

    def _unit_for(self, reg, r: dict[str, Any]) -> str:
        ev = r.get("evidence") or []
        if ev:
            f = ev[0].get("file")
            for u in reg.units:
                if f in u.files:
                    return u.name
        return "project"

    def _write_inventory(self, ctx: Context) -> None:
        reg = ctx.registry
        rows = "\n".join(f"| `{f.path}` | {f.language} | {f.lines} | {f.size} |" for f in reg.inventory)
        units = "\n".join(
            f"| **{u.name}** | {u.kind} | {'yes' if u.entry_point else ''} | "
            f"{', '.join(f'`{p}`' for p in u.files)} | {u.description} |" for u in reg.units)
        ctx.write("inventory.md", f"""# Inventory

Project: `{ctx.project.root.name}`  
Stack: {', '.join(reg.meta.get('stack', [])) or 'unknown'}  
Files: {len(reg.inventory)} · Units: {len(reg.units)}

## Units

| Unit | Kind | Entry | Files | Description |
|---|---|---|---|---|
{units}

## Files

| Path | Language | Lines | Bytes |
|---|---|---|---|
{rows}
""")

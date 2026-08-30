"""install / update / status / uninstall / add-engine (paper §3.2–3.3).

Installation must not take over the legacy project: everything Reversa writes
is registered in the manifest; `update` overwrites only intact or missing
files; `uninstall` deletes only intact files and leaves modified ones behind.
"""
from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from . import __version__
from .agents import DISCOVERY, MIGRATION
from .engines import Engine, resolve_engines
from .manifest import Manifest, FileStatus
from .orchestrator import STATE_DIR, DEFAULT_OUT

_ENTRY = """# Reversa — reverse documentation engineering

This project has Reversa installed. Reversa converts this legacy codebase into
traceable operational specifications under `{out}/`.

## How to run the pipeline as an agent

Work through the Discovery team **in order**, one skill at a time, writing the
artifacts each skill describes. Never skip the reviewer.

{skills}

## Confidence rules (apply to every statement you write)

- **confirmed**: cite file and line range; the code says exactly this.
- **inferred**: a hypothesis from names, patterns or structure. Say so.
- **gap**: unknown. Record it in `{out}/gaps.md` and ask in `questions.md`.

Never present an inference as a fact. Never fabricate evidence.

State: `.reversa/state.json`, `.reversa/registry.json`, `.reversa/plan.md`.
CLI equivalent: `reversa run` (discovery), `reversa migrate --target <lang>`.
"""

_SKILL = """---
name: {name}
description: {role_short}
---

# {name}

## Role
{role}

## Inputs
{inputs}

## Outputs
{outputs}

## Output contract
Reply with one JSON object matching:
```json
{schema}
```

## Rules
- Every confirmed claim cites `file:line_start-line_end` with a short excerpt.
- Inferred claims are written as hypotheses.
- Anything you cannot determine becomes a gap, never a guess.
"""

_INPUTS = {
    "reversa-scout": "The file inventory and the first lines of each code file.",
    "reversa-archaeologist": "The full numbered source of one unit.",
    "reversa-detective": "The numbered source of one unit plus the technical claims already established.",
    "reversa-architect": "All unit-level claims (structure, data, dependencies).",
    "reversa-process": "Entry points, all sources, and the behaviour/rule/dependency claims.",
    "reversa-writer": "All claims and open gaps of one unit.",
    "reversa-reviewer": "All inferred claims with their evidence and the cited source.",
    "reversa-migration": "All claims and gaps, plus the target language/platform.",
}
_OUTPUTS = {
    "reversa-scout": "`inventory.md`; structure/dependency claims; units with entry points.",
    "reversa-archaeologist": "`analysis/<unit>.md`; structure/data claims.",
    "reversa-detective": "`rules.md`; rule/state/permission/exception claims; questions; gaps.",
    "reversa-architect": "`architecture.md`, `dependencies.md`, `traceability/spec-impact-matrix.md`.",
    "reversa-process": "`business-context.md` (plain-English orientation) and `processes.md` (end-to-end processes, each step traced to code).",
    "reversa-writer": "`specs/<unit>/{requirements,design,tasks}.md`, `traceability/code-spec-matrix.md`.",
    "reversa-reviewer": "`confidence-report.md`, `gaps.md`, `questions.md`; reclassified claims.",
    "reversa-migration": "`migration/strategy.md`, `migration/risk-register.md`, `migration/parity/*.feature`.",
}


def _skill_text(cls) -> str:
    a = cls()
    return _SKILL.format(name=a.name, role=a.role, role_short=a.role.split(". ")[0][:140],
                         inputs=_INPUTS.get(a.name, ""), outputs=_OUTPUTS.get(a.name, ""),
                         schema=json.dumps(a.output_schema, indent=1))


def _entry_text(out: str) -> str:
    skills = "\n".join(f"{i}. **{c.name}** — {c().role.split('. ')[0]}."
                       for i, c in enumerate(DISCOVERY + MIGRATION, start=1))
    return _ENTRY.format(out=out, skills=skills)


def _write(root: Path, rel: str, text: str, man: Manifest, force: bool) -> str:
    """Write a managed file unless the user modified it. Returns action."""
    p = root / rel
    status = man.status_of(rel) if rel in man.entries else "new"
    if status == "modified" and not force:
        return "preserved"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    man.record(rel)
    return "written" if status in ("new", "missing") else "updated"


def install(root: Path, engines: list[str] | None, out_dir: str = DEFAULT_OUT,
            teams: list[str] | None = None, project_name: str | None = None,
            force: bool = False, log=print) -> dict[str, list[str]]:
    root = root.resolve()
    man = Manifest(root).load()
    eng = resolve_engines(engines, root)
    teams = teams or ["discovery", "migration"]
    actions: dict[str, list[str]] = {"written": [], "updated": [], "preserved": []}
    now = time.strftime("%Y-%m-%dT%H:%M:%S")

    def w(rel: str, text: str) -> None:
        actions[_write(root, rel, text, man, force)].append(rel)

    # state layer
    w(f"{STATE_DIR}/version", __version__ + "\n")
    w(f"{STATE_DIR}/config.toml", f"""# Reversa configuration (managed; edit config.user.toml for overrides)
[project]
name = "{project_name or root.name}"
installed = "{now}"
version = "{__version__}"

[output]
dir = "{out_dir}"

[teams]
enabled = {json.dumps(teams)}

[engines]
enabled = {json.dumps([e.key for e in eng])}
""")
    if not (root / STATE_DIR / "config.user.toml").exists():
        w(f"{STATE_DIR}/config.user.toml", "# Your overrides. This file is never overwritten by update.\n"
                                            "[migration]\n# target = \"go\"\n")
    w(f"{STATE_DIR}/plan.md", "# Reversa execution plan\n\nNot run yet. Use `reversa run`.\n")
    # templates
    w(f"{STATE_DIR}/templates/requirements.md", "# Requirements — <UNIT>\n\n<purpose>\n\n## Behaviours to preserve\n\n- ✅/🟡 **REQ-n** <text> _claims: … · evidence: file:lines_\n")
    w(f"{STATE_DIR}/templates/gaps.md", "| Gap | Unit | Severity | Blocking | Status | Description | Resolution |\n|---|---|---|---|---|---|---|\n")
    # engine layer
    agent_classes = ([*DISCOVERY] if "discovery" in teams else []) + ([*MIGRATION] if "migration" in teams else [])
    for e in eng:
        w(e.entry_file, _entry_text(out_dir))
        for cls in agent_classes:
            w(f"{e.skills_dir}/{cls.name}/SKILL.md", _skill_text(cls))
    man.save(__version__)
    log(f"reversa {__version__} installed for engines: {', '.join(e.name for e in eng)}")
    for k, v in actions.items():
        if v:
            log(f"  {k}: {len(v)}")
    return actions


def status(root: Path) -> list[FileStatus]:
    return Manifest(root.resolve()).load().classify()


def update(root: Path, force: bool = False, log=print) -> dict[str, list[str]]:
    root = root.resolve()
    cfg = root / STATE_DIR / "config.toml"
    engines = None
    out_dir = DEFAULT_OUT
    if cfg.exists():
        for line in cfg.read_text(encoding="utf-8").splitlines():
            if line.startswith("enabled = ") and "engines" in _section_before(cfg, line):
                engines = json.loads(line.split("=", 1)[1].strip())
            if line.startswith("dir = "):
                out_dir = line.split("=", 1)[1].strip().strip('"')
    return install(root, engines, out_dir=out_dir, force=force, log=log)


def _section_before(cfg: Path, target: str) -> str:
    sec = ""
    for line in cfg.read_text(encoding="utf-8").splitlines():
        if line.startswith("["):
            sec = line
        if line == target:
            return sec
    return sec


def uninstall(root: Path, purge: bool = False, log=print) -> dict[str, list[str]]:
    root = root.resolve()
    man = Manifest(root).load()
    out: dict[str, list[str]] = {"deleted": [], "preserved": [], "missing": []}
    for fs in man.classify():
        p = root / fs.path
        if fs.status == "intact" or (fs.status == "modified" and purge):
            p.unlink()
            out["deleted"].append(fs.path)
        elif fs.status == "modified":
            out["preserved"].append(fs.path)
        else:
            out["missing"].append(fs.path)
    # remove now-empty managed dirs, walking up to (but not including) root
    for f in man.entries:
        d = (root / f).parent
        while d != root and root in d.parents:
            try:
                if d.exists() and not any(d.iterdir()):
                    d.rmdir()
                else:
                    break
            except OSError:
                break
            d = d.parent
    if not out["preserved"] and (root / STATE_DIR).exists():
        shutil.rmtree(root / STATE_DIR, ignore_errors=True)
    elif man.path.exists():
        man.path.unlink()
    log(f"uninstalled: {len(out['deleted'])} deleted, {len(out['preserved'])} preserved (user-modified)")
    return out


def add_engine(root: Path, key: str, log=print) -> None:
    root = root.resolve()
    cfg = root / STATE_DIR / "config.toml"
    if not cfg.exists():
        raise RuntimeError("Reversa is not installed here; run `reversa install` first")
    txt = cfg.read_text(encoding="utf-8")
    cur: list[str] = []
    for line in txt.splitlines():
        if line.startswith("enabled = ") and "engines" in _section_before(cfg, line):
            cur = json.loads(line.split("=", 1)[1].strip())
    if key not in cur:
        cur.append(key)
    install(root, cur, log=log)

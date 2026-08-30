"""Command line interface.

    reversa install   [--engines claude,codex] [--out _reversa_sdd]
    reversa update    [--force]
    reversa status
    reversa uninstall [--purge]
    reversa add-engine <key>
    reversa run       [--backend auto|anthropic|heuristic] [--resume] [--only scout,reviewer] [--units A,B]
    reversa migrate   --target go [--backend ...]
    reversa answer    <Q-001|GAP-002> "<text>"     # feed human decisions back
    reversa export-diagrams                          # architecture graph as .mmd
    reversa report                                   # print confidence snapshot
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, installer
from .confidence import distribution
from .llm import get_backend
from .models import Registry
from .orchestrator import DEFAULT_OUT, STATE_DIR, Orchestrator


def _root(args) -> Path:
    return Path(args.path).resolve()


def _backend(args):
    try:
        return get_backend(args.backend, model=getattr(args, "model", None))
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        print("hint: set ANTHROPIC_API_KEY, or use --backend heuristic", file=sys.stderr)
        sys.exit(2)


def cmd_install(args):
    installer.install(_root(args), args.engines.split(",") if args.engines else None,
                      out_dir=args.out, teams=args.teams.split(",") if args.teams else None,
                      project_name=args.name, force=args.force)


def cmd_update(args):
    installer.update(_root(args), force=args.force)


def cmd_status(args):
    root = _root(args)
    files = installer.status(root)
    if not files:
        print("Reversa is not installed here (no manifest).")
    else:
        counts = {"intact": 0, "modified": 0, "missing": 0}
        for f in files:
            counts[f.status] += 1
            if args.verbose or f.status != "intact":
                print(f"  {f.status:8s} {f.path}")
        print(f"files: {counts['intact']} intact, {counts['modified']} modified, {counts['missing']} missing")
    st = (root / STATE_DIR / "state.json")
    if st.exists():
        o = Orchestrator(root, backend=None, log=lambda *_: None)  # type: ignore[arg-type]
        s = o.status()
        print(f"pipeline: " + ", ".join(f"{k.split('-', 1)[1]}={v['status']}" for k, v in s["stages"].items()))
        print(f"claims: {s['claims']} ({s['confirmed']} confirmed / {s['inferred']} inferred / {s['gap']} gap) "
              f"index {s['index']:.1%} · gaps {s['gaps']} · questions {s['questions']}")


def cmd_uninstall(args):
    installer.uninstall(_root(args), purge=args.purge)


def cmd_add_engine(args):
    installer.add_engine(_root(args), args.engine)


def cmd_run(args):
    o = Orchestrator(_root(args), _backend(args), out_dir=args.out,
                     config={"target": args.target} if getattr(args, "target", None) else {})
    team = "all" if getattr(args, "target", None) else "discovery"
    o.run(team=team, resume=args.resume,
          only=args.only.split(",") if args.only else None,
          units=args.units.split(",") if args.units else None)
    d = distribution(o.registry.claims)
    print(f"\nartifacts: {o.out_dir}")
    print(f"claims {d.total}: {d.confirmed} confirmed / {d.inferred} inferred / {d.gap} gap · "
          f"index {d.index:.1%} · gaps {len(o.registry.gaps)} · questions {len(o.registry.questions)}")


def cmd_migrate(args):
    o = Orchestrator(_root(args), _backend(args), out_dir=args.out, config={"target": args.target})
    if not o.registry.claims:
        print("error: run discovery first (`reversa run`)", file=sys.stderr)
        sys.exit(1)
    o.run(team="migration", resume=True, units=args.units.split(",") if args.units else None)
    print(f"parity scenarios: {o.registry.meta.get('parity_scenarios', 0)} → {o.out_dir / 'migration'}")


def cmd_answer(args):
    root = _root(args)
    reg = Registry.load(root / STATE_DIR / "registry.json")
    hit = False
    for q in reg.questions:
        if q.id == args.id:
            q.answer = args.text
            hit = True
    for g in reg.gaps:
        if g.id == args.id:
            g.resolution = args.text
            g.status = args.status or "resolved"
            hit = True
    if not hit:
        print(f"error: no question or gap with id {args.id}", file=sys.stderr)
        sys.exit(1)
    reg.save(root / STATE_DIR / "registry.json")
    print(f"recorded on {args.id}. Re-render with: reversa run --resume --only reviewer --backend heuristic")


def cmd_export(args):
    root = _root(args)
    reg = Registry.load(root / STATE_DIR / "registry.json")
    arch = reg.meta.get("architecture", {})
    lines = ["graph TD"]
    for u in reg.units:
        lines.append(f"  {u.name}([{u.name}])" if u.entry_point else f"  {u.name}[{u.name}]")
    for s, t in arch.get("edges", []):
        lines.append(f"  {s} --> {t}")
    for store, users in arch.get("stores", {}).items():
        sid = "DS_" + "".join(ch if ch.isalnum() else "_" for ch in store)
        lines.append(f"  {sid}[({store})]")
        for u in users:
            lines.append(f"  {u} -.-> {sid}")
    out = root / args.out / "diagrams"
    out.mkdir(parents=True, exist_ok=True)
    (out / "architecture.mmd").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out / 'architecture.mmd'}")


def cmd_report(args):
    root = _root(args)
    reg = Registry.load(root / STATE_DIR / "registry.json")
    d = distribution(reg.claims)
    print(json.dumps({"claims": d.total, "confirmed": d.confirmed, "inferred": d.inferred, "gap": d.gap,
                      "index": round(d.index, 4), "gaps": len(reg.gaps),
                      "blocking_gaps": sum(1 for g in reg.gaps if g.blocking and g.status == "open"),
                      "questions": len(reg.questions), "answered": sum(1 for q in reg.questions if q.answer)},
                     indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="reversa", description="Reverse documentation engineering for legacy systems")
    p.add_argument("--version", action="version", version=f"reversa {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--path", default=".", help="legacy project root (default: .)")
        sp.add_argument("--out", default=DEFAULT_OUT, help="artifact directory (default: _reversa_sdd)")

    def backend(sp):
        sp.add_argument("--backend", default="auto", choices=["auto", "anthropic", "heuristic"])
        sp.add_argument("--model", default=None, help="model id for the anthropic backend")

    s = sub.add_parser("install", help="install Reversa into a legacy project"); common(s)
    s.add_argument("--engines", help="comma list: claude,codex,cursor,gemini,... (default: detect)")
    s.add_argument("--teams", help="comma list: discovery,migration")
    s.add_argument("--name"); s.add_argument("--force", action="store_true", help="overwrite modified files")
    s.set_defaults(fn=cmd_install)

    s = sub.add_parser("update", help="update managed files, preserving user edits"); common(s)
    s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_update)

    s = sub.add_parser("status", help="manifest and pipeline status"); common(s)
    s.add_argument("-v", "--verbose", action="store_true"); s.set_defaults(fn=cmd_status)

    s = sub.add_parser("uninstall", help="remove managed files (keeps modified ones)"); common(s)
    s.add_argument("--purge", action="store_true", help="also delete user-modified files"); s.set_defaults(fn=cmd_uninstall)

    s = sub.add_parser("add-engine", help="install entry file + skills for another engine"); common(s)
    s.add_argument("engine"); s.set_defaults(fn=cmd_add_engine)

    s = sub.add_parser("run", help="run the Discovery team (add --target to run migration too)"); common(s); backend(s)
    s.add_argument("--resume", action="store_true", help="skip stages already done")
    s.add_argument("--only", help="comma list of stages, e.g. writer,reviewer")
    s.add_argument("--units", help="comma list of units to restrict to")
    s.add_argument("--target", help="target language/platform; also runs the Migration team")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("migrate", help="run the Migration team on existing discovery"); common(s); backend(s)
    s.add_argument("--target", required=True); s.add_argument("--units"); s.set_defaults(fn=cmd_migrate)

    s = sub.add_parser("answer", help="record a human answer/decision on a question or gap"); common(s)
    s.add_argument("id"); s.add_argument("text")
    s.add_argument("--status", choices=["resolved", "residual", "out_of_scope"]); s.set_defaults(fn=cmd_answer)

    s = sub.add_parser("export-diagrams", help="export architecture graph as Mermaid"); common(s); s.set_defaults(fn=cmd_export)
    s = sub.add_parser("report", help="print confidence snapshot as JSON"); common(s); s.set_defaults(fn=cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except (RuntimeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0

import json
from pathlib import Path

import pytest

from reversa.cli import main
from reversa.confidence import distribution, verify_evidence
from reversa.llm import get_backend
from reversa.models import Confidence, Registry
from reversa.orchestrator import Orchestrator


def _quiet(*_a, **_k):
    pass


def test_discovery_and_migration_offline(atm: Path):
    o = Orchestrator(atm, get_backend("heuristic"), log=_quiet, config={"target": "go"})
    reg = o.run(team="all")
    sdd = atm / "_reversa_sdd"
    for rel in ["inventory.md", "rules.md", "architecture.md", "dependencies.md",
                "confidence-report.md", "gaps.md", "questions.md",
                "traceability/code-spec-matrix.md", "traceability/spec-impact-matrix.md",
                "specs/conta/requirements.md", "specs/conta/design.md", "specs/conta/tasks.md",
                "migration/strategy.md", "migration/risk-register.md", "migration/parity/conta.feature"]:
        assert (sdd / rel).exists(), rel
    names = {u.name for u in reg.units}
    assert names == {"MENU", "CONTA", "EXTRATO", "UTIL", "KBDREAD"}
    assert next(u for u in reg.units if u.name == "MENU").entry_point
    d = distribution(reg.claims)
    assert d.total > 40 and 0 < d.index <= 1
    # the paper's core invariant: every confirmed claim has verifiable evidence
    for c in reg.claims:
        if c.confidence == Confidence.CONFIRMED:
            assert c.evidence, c.id
            assert any(verify_evidence(atm, e)[0] for e in c.evidence), c.id
    # interpretation stays inferred
    assert any(c.confidence == Confidence.INFERRED and "rejected with message" in c.statement
               for c in reg.claims)
    # requirements cite claims that exist
    ids = {c.id for c in reg.claims}
    for unit, spec in reg.meta["specs"].items():
        for r in spec["requirements"]:
            assert set(r["claims"]) <= ids
    # parity: inferred claims are tagged
    feat = (sdd / "migration/parity/conta.feature").read_text()
    assert "@needs-validation" in feat and "@parity @C-" in feat
    # state persisted and resumable
    st = json.loads((atm / ".reversa/state.json").read_text())
    assert all(v["status"] == "done" for v in st["stages"].values())
    assert (atm / ".reversa/plan.md").exists()


def test_reviewer_downgrades_unverifiable_claims(atm: Path):
    o = Orchestrator(atm, get_backend("heuristic"), log=_quiet)
    o.run(team="discovery")
    reg = Registry.load(atm / ".reversa/registry.json")
    bad = reg.add_claim(unit="CONTA", kind="rule", statement="Fake rule with bogus evidence",
                        confidence=Confidence.CONFIRMED,
                        evidence=[__import__("reversa.models", fromlist=["Evidence"]).Evidence(
                            "CONTA.cbl", 64, 64, "THIS EXCERPT DOES NOT EXIST")])
    noev = reg.add_claim(unit="CONTA", kind="rule", statement="Confirmed without evidence",
                         confidence=Confidence.CONFIRMED)
    inf_bad = reg.add_claim(unit="CONTA", kind="rule", statement="Inferred with bad evidence",
                            confidence=Confidence.INFERRED,
                            evidence=[__import__("reversa.models", fromlist=["Evidence"]).Evidence(
                                "MISSING.cbl", 1, 1, "x")])
    reg.save(atm / ".reversa/registry.json")
    o2 = Orchestrator(atm, get_backend("heuristic"), log=_quiet)
    o2.run(team="discovery", resume=True, only=["reviewer"])
    by = {c.id: c for c in o2.registry.claims}
    assert by[bad.id].confidence == Confidence.INFERRED and "downgraded" in by[bad.id].review
    assert by[noev.id].confidence == Confidence.INFERRED
    assert by[inf_bad.id].confidence == Confidence.GAP
    assert any(inf_bad.id in g.related_claims for g in o2.registry.gaps)


def test_cli_roundtrip(atm: Path, capsys):
    assert main(["install", "--path", str(atm), "--engines", "claude"]) == 0
    assert main(["run", "--path", str(atm), "--backend", "heuristic"]) == 0
    assert main(["migrate", "--path", str(atm), "--backend", "heuristic", "--target", "go"]) == 0
    assert main(["report", "--path", str(atm)]) == 0
    out = capsys.readouterr().out
    rep = json.loads(out[out.rindex("{"):])
    assert rep["claims"] > 0 and rep["questions"] > 0
    assert main(["status", "--path", str(atm)]) == 0
    assert main(["export-diagrams", "--path", str(atm)]) == 0
    assert (atm / "_reversa_sdd/diagrams/architecture.mmd").exists()
    # answer a question and a gap-less id
    reg = Registry.load(atm / ".reversa/registry.json")
    qid = reg.questions[0].id
    assert main(["answer", "--path", str(atm), qid, "It is a business limit."]) == 0
    reg = Registry.load(atm / ".reversa/registry.json")
    assert reg.questions[0].answer == "It is a business limit."
    with pytest.raises(SystemExit):
        main(["answer", "--path", str(atm), "Q-999", "x"])


def test_units_filter(atm: Path):
    o = Orchestrator(atm, get_backend("heuristic"), log=_quiet)
    o.run(team="discovery", units=["CONTA"])
    assert (atm / "_reversa_sdd/specs/conta/requirements.md").exists()
    assert not (atm / "_reversa_sdd/specs/menu").exists()


def test_processes_reconstructed(atm: Path):
    o = Orchestrator(atm, get_backend("heuristic"), log=_quiet)
    reg = o.run(team="discovery")
    procs = {p["name"]: p for p in reg.meta["processes"]}
    saque = next(p for n, p in procs.items() if "SAQUE" in n)
    kinds = [s["kind"] for s in saque["steps"]]
    assert kinds.count("decision") == 3 and "data" in kinds and kinds[0] == "call"
    assert any("LIMITE DE SAQUE EXCEDIDO" in s.get("outcome_if_true", "") for s in saque["steps"])
    assert all(s["evidence"] for s in saque["steps"])
    assert any("EXTRATO" in n for n in procs)          # option 5 labelled by the unit it calls
    assert any("'9'" in n for n in procs) and procs[[n for n in procs if "'9'" in n][0]]["steps"]
    md = (atm / "_reversa_sdd/processes.md").read_text()
    assert "flowchart TD" in md and 'D0{"' in md
    assert "## Overview" in md and reg.meta["process_overview"]
    assert saque["description"].startswith("This process starts when")
    assert "LIMITE DE SAQUE EXCEDIDO" in saque["description"] and "the operation stops" in saque["description"]
    assert "**Description.**" in md


def test_business_context(atm: Path):
    o = Orchestrator(atm, get_backend("heuristic"), log=_quiet)
    reg = o.run(team="discovery")
    bc = reg.meta["business_context"]
    recs = {e["record"]: e for e in bc["what_it_manages"]}
    assert {"CLI-REG", "MOV-REG"} <= set(recs)
    assert any(f["name"] == "CLI-SALDO" and "decimal" in f["type"] for f in recs["CLI-REG"]["fields"])
    params = {p["name"]: p for p in bc["parameters"]}
    assert params["WS-LIMITE-SAQUE"]["value"] == "1000"
    assert params["WS-TARIFA-TRANSF"]["value"] == "2.50" and "TRANSFERENCIA" in params["WS-TARIFA-TRANSF"]["where_used"]
    assert "WS-TENTATIVAS" not in params           # zero-initialised counter is not a parameter
    rules = [r["rule"] for r in bc["business_rules"]]
    assert any("CARTAO BLOQUEADO" in r and "rejects" in r for r in rules)   # abort detected via END-IF scan
    assert any("SEM MOVIMENTOS" in r and "shows" in r for r in rules)       # no abort there
    assert all(r["evidence"] for r in bc["business_rules"])
    md = (atm / "_reversa_sdd/business-context.md").read_text()
    assert "## What this system is" in md and "## Business parameters" in md

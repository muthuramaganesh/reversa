"""Hybrid backend: heuristic extraction, LLM only for the plain-English rewrite.

The LLM is replaced by a fake so these run offline.
"""
import json
import re
import shutil
from pathlib import Path

import pytest

from reversa.llm import get_backend
from reversa.llm.hybrid_backend import HybridBackend
from reversa.orchestrator import Orchestrator
from reversa.specbuilder import REWRITE_SYSTEM


def _quiet(*_a, **_k):
    pass


def _fake_llm(calls):
    """Rewrites every rule/step/finding as 'PLAIN: <draft>' — keeps every literal, so it passes validation."""
    def complete(system, user):
        calls.append(system)
        data = json.loads(user)
        return json.dumps({
            "processes": [{"id": p["id"], "step": "PLAIN: " + p["draft"]} for p in data["processes"]],
            "rules": [{"id": r["id"], "rule": "PLAIN: " + r["draft"] + " " + r["code"],
                       "example": r.get("draft_example") or ""} for r in data["rules"]],
            "findings": [{"id": f["id"], "finding": "PLAIN: " + f["draft"], "question": f["question"]}
                         for f in data["findings"]],
        })
    return complete


def _claims(reg):
    return sorted((str(c.kind), c.statement, str(c.confidence)) for c in reg.claims)


def test_get_backend_names(monkeypatch):
    b = get_backend("hybrid-qwen")
    assert isinstance(b, HybridBackend) and b.name == "hybrid-qwen" and callable(b._call)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        get_backend("hybrid-anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    assert get_backend("hybrid-anthropic").name == "hybrid-anthropic"


def test_hybrid_extraction_is_heuristic_and_llm_only_rewrites(atm: Path, tmp_path: Path):
    a, b = tmp_path / "heur", tmp_path / "hyb"
    shutil.copytree(atm, a)
    shutil.copytree(atm, b)
    heur = Orchestrator(a, get_backend("heuristic"), log=_quiet).run(team="discovery")

    hb = get_backend("hybrid-qwen")
    calls = []
    hb._complete = _fake_llm(calls)
    hyb = Orchestrator(b, hb, log=_quiet).run(team="discovery")

    # same claims, evidence-backed confidence and gaps as the pure heuristic run
    assert _claims(hyb) == _claims(heur)
    assert len(hyb.gaps) == len(heur.gaps) and len(hyb.questions) == len(heur.questions)
    # the LLM was used, and only with the rewrite prompt
    assert calls and all(s == REWRITE_SYSTEM for s in calls)
    # the rewritten wording reached the rendered rules
    rules = json.loads((b / "_reversa_sdd/rules.json").read_text())
    assert "PLAIN:" in json.dumps(rules)
    assert "PLAIN:" not in (a / "_reversa_sdd/rules.json").read_text()


def test_hybrid_survives_llm_failure(atm: Path, tmp_path: Path, capsys):
    a, b = tmp_path / "heur", tmp_path / "hyb"
    shutil.copytree(atm, a)
    shutil.copytree(atm, b)
    Orchestrator(a, get_backend("heuristic"), log=_quiet).run(team="discovery")

    hb = get_backend("hybrid-qwen")

    def down(system, user):
        raise RuntimeError("Could not reach Qwen")
    hb._complete = down
    Orchestrator(b, hb, log=_quiet).run(team="discovery")

    assert hb.llm_calls and hb.llm_failures == hb.llm_calls
    assert (b / "_reversa_sdd/rules.json").read_text() == (a / "_reversa_sdd/rules.json").read_text()
    assert len(re.findall("LLM call failed", capsys.readouterr().err)) == 1   # warned once, not per call


def test_rewrite_that_drops_a_literal_is_rejected(atm: Path, tmp_path: Path):
    b = tmp_path / "hyb"
    shutil.copytree(atm, b)
    hb = get_backend("hybrid-qwen")

    def lossy(system, user):
        data = json.loads(user)
        return json.dumps({"processes": [], "findings": [],
                           "rules": [{"id": r["id"], "rule": "There is a limit.", "example": ""}
                                     for r in data["rules"]]})
    hb._complete = lossy
    Orchestrator(b, hb, log=_quiet).run(team="discovery")
    rules = [r for p in json.loads((b / "_reversa_sdd/rules.json").read_text())["programs"]
             for r in p["rules"]]
    # rules whose code carries a number or quoted value keep their deterministic wording
    with_literals = [r for r in rules if re.search(r"'[^']+'|(?<![\w.])[2-9]\d*(?:\.\d+)?", r["code"])]
    assert with_literals and all(r["rule"] != "There is a limit." for r in with_literals)

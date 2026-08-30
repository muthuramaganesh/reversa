import json

from reversa.agents import Scout, Reviewer
from reversa.llm.anthropic_backend import AnthropicBackend
from reversa.llm.base import strip_json
from reversa.models import Registry


def test_strip_json_tolerates_fences():
    assert strip_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert strip_json('Sure! {"a": [1,2]} done') == {"a": [1, 2]}


def test_anthropic_backend_parses_and_falls_back(monkeypatch, atm):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    b = AnthropicBackend()
    calls = []

    def fake_call(system, user):
        calls.append((system, user))
        return '```json\n{"reclassify": [], "questions": [{"unit": "CONTA", "question": "q?"}]}\n```'

    monkeypatch.setattr(b, "_call", fake_call)
    out = b.generate(Reviewer(), {"inferred": [], "sources": {}, "answers": []})
    assert out["questions"][0]["question"] == "q?"
    assert "CONFIDENCE RULES" in calls[0][0]           # system prompt carries the model
    assert "Reply with ONE JSON object" in calls[0][1]  # schema appended

    monkeypatch.setattr(b, "_call", lambda s, u: "I cannot help with that.")
    from reversa.analysis import analyze
    from reversa.project import Project
    proj = Project(atm)
    inv = proj.inventory()
    code = proj.code_files(inv)
    payload = {"project_name": "atm", "inventory": [f.__dict__ for f in inv],
               "heads": {f.path: "" for f in code},
               "facts": {f.path: analyze(f.path, f.language, proj.lines(f.path)) for f in code},
               "lines": {f.path: proj.lines(f.path) for f in code}}
    out = b.generate(Scout(), payload)
    assert out["units"] and any("heuristic fallback" in w for w in out["_warnings"])


def test_registry_dedupes_questions_and_gaps():
    r = Registry()
    q1 = r.add_question(unit="A", question="x?", related_claims=["C-001"])
    q1.answer = "yes"
    q2 = r.add_question(unit="A", question="x?", related_claims=["C-002"])
    assert q1 is q2 and q2.answer == "yes" and q2.related_claims == ["C-001", "C-002"]
    g1 = r.add_gap(unit="A", description="d")
    g2 = r.add_gap(unit="A", description="d", severity="critical")
    assert g1 is g2 and len(r.gaps) == 1

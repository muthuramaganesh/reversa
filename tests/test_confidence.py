from reversa.confidence import Distribution, verify_evidence
from reversa.models import Evidence


def test_index_matches_paper_case_study():
    # Paper §5.3: 490 confirmed, 24 inferred, 3 gaps -> 97.1%
    d = Distribution(confirmed=490, inferred=24, gap=3)
    assert d.total == 517
    assert round(d.index * 100, 1) == 97.1


def test_index_per_module_matches_paper_table5():
    assert round(Distribution(32, 1, 0).index * 100, 1) == 98.5    # menu
    assert round(Distribution(124, 9, 1).index * 100, 1) == 95.9   # extrato
    assert round(Distribution(115, 4, 2).index * 100, 1) == 96.7   # util


def test_empty_distribution_is_zero():
    assert Distribution().index == 0.0


def test_verify_evidence(atm):
    ok, _ = verify_evidence(atm, Evidence("CONTA.cbl", 64, 64, "IF WS-VALOR > WS-LIMITE-SAQUE"))
    assert ok
    ok, reason = verify_evidence(atm, Evidence("CONTA.cbl", 64, 64, "this text is not in the file"))
    assert not ok and "not found" in reason
    ok, reason = verify_evidence(atm, Evidence("NOPE.cbl", 1, 1, "x"))
    assert not ok and "file not found" in reason
    ok, reason = verify_evidence(atm, Evidence("CONTA.cbl", 9999, 9999, "x"))
    assert not ok and "out of range" in reason

from pathlib import Path

from reversa.analysis import analyze


def test_cobol_facts(atm):
    ff = analyze("CONTA.cbl", "cobol", (atm / "CONTA.cbl").read_text().splitlines())
    assert ff.first("program").name == "CONTA"
    assert {p.name for p in ff.of("paragraph")} >= {"MAIN", "SALDO", "SAQUE", "DEPOSITO", "TRANSFERENCIA", "GRAVA"}
    assert {s.name for s in ff.of("select")} == {"CLIENTES", "MOVTOS"}
    assert any(c.name.startswith("WS-VALOR > WS-LIMITE-SAQUE") for c in ff.of("condition"))
    assert any(m.name == "LIMITE DE SAQUE EXCEDIDO" for m in ff.of("message"))
    assert {c.name for c in ff.of("call")} == {"UTIL"}
    opens = [i for i in ff.of("io") if i.detail.startswith("OPEN")]
    assert {i.name for i in opens} == {"CLIENTES", "MOVTOS"}
    assert any(r.detail == "linkage" for r in ff.of("record"))


def test_procedure_division_using_is_recognised(atm):
    # PROCEDURE DIVISION USING ... must still switch division (regression)
    ff = analyze("UTIL.cbl", "cobol", (atm / "UTIL.cbl").read_text().splitlines())
    assert ff.of("dispatch") and ff.of("paragraph")


def test_generic_c(atm):
    ff = analyze("kbdread.c", "c", (atm / "kbdread.c").read_text().splitlines())
    assert any(f.name == "KBDREAD" for f in ff.of("function"))
    assert ff.of("import")

@unit-process
Feature: PROCESS parity
  Legacy and go implementations must behave identically for PROCESS.

  @parity @C-399
  Scenario: Branch guarded by `words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"` in...
    Given an input that exercises: Branch guarded by `words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"` in _plain
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-400
  Scenario: Branch guarded by `k == "call"` in narrate
    Given an input that exercises: Branch guarded by `k == "call"` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-401
  Scenario: Branch guarded by `a.startswith("Call "` in narrate
    Given an input that exercises: Branch guarded by `a.startswith("Call "` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-402
  Scenario: Branch guarded by `nxt and nxt.get("action", "").startswith(f"{unit} dispatches"` in narrate
    Given an input that exercises: Branch guarded by `nxt and nxt.get("action", "").startswith(f"{unit} dispatches"` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-403
  Scenario: Branch guarded by `t.startswith("show"` in narrate
    Given an input that exercises: Branch guarded by `t.startswith("show"` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-404
  Scenario: Branch guarded by `a.startswith("Set "` in narrate
    Given an input that exercises: Branch guarded by `a.startswith("Set "` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-405
  Scenario: Branch guarded by `steps` in narrate
    Given an input that exercises: Branch guarded by `steps` in narrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-406
  Scenario: Branch guarded by `rec.detail != "file" or rec.name in seen_rec` in business_context
    Given an input that exercises: Branch guarded by `rec.detail != "file" or rec.name in seen_rec` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-407
  Scenario: Branch guarded by `c.extra.get("section") != "working-storage"` in business_context
    Given an input that exercises: Branch guarded by `c.extra.get("section") != "working-storage"` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-408
  Scenario: Branch guarded by `not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", val) or float(val.replace(",", ".")) == 0` in...
    Given an input that exercises: Branch guarded by `not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", val) or float(val.replace(",", ".")) == 0` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-409
  Scenario: Branch guarded by `any(c.name in lines[path][j] for j in range(pg.line, end)` in business_context
    Given an input that exercises: Branch guarded by `any(c.name in lines[path][j] for j in range(pg.line, end)` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-410
  Scenario: Branch guarded by `st.get("kind") != "decision"` in business_context
    Given an input that exercises: Branch guarded by `st.get("kind") != "decision"` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-411
  Scenario: Branch guarded by `key in seen_rules` in business_context
    Given an input that exercises: Branch guarded by `key in seen_rules` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-412
  Scenario: Branch guarded by `any(f.kind == "call" and f.name == "KBDREAD" for ff in facts.values() for f in ff.facts` in...
    Given an input that exercises: Branch guarded by `any(f.kind == "call" and f.name == "KBDREAD" for ff in facts.values() for f in ff.facts` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-413
  Scenario: Branch guarded by `not any("LOG" in n or "AUDIT" in n for n in seen_rec` in business_context
    Given an input that exercises: Branch guarded by `not any("LOG" in n or "AUDIT" in n for n in seen_rec` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-414
  Scenario: Branch guarded by `not any(f.kind == "condition" and re.search(r"DATA|DATE|HORA|TIME", f.name, re.I) for ff in...
    Given an input that exercises: Branch guarded by `not any(f.kind == "condition" and re.search(r"DATA|DATE|HORA|TIME", f.name, re.I) for ff in facts.values() for f in ff.facts` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-415
  Scenario: Branch guarded by `not any(f.kind in ("io",) and f.detail.startswith("OPEN") and "LOCK" in f.name for ff in...
    Given an input that exercises: Branch guarded by `not any(f.kind in ("io",) and f.detail.startswith("OPEN") and "LOCK" in f.name for ff in facts.values() for f in ff.facts` in business_context
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-416
  Scenario: Branch guarded by `not processes` in overview_text
    Given an input that exercises: Branch guarded by `not processes` in overview_text
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-417
  Scenario: Branch guarded by `start is None` in para_facts
    Given an input that exercises: Branch guarded by `start is None` in para_facts
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-418
  Scenario: Branch guarded by `depth > 6 or (path, para) in seen` in walk
    Given an input that exercises: Branch guarded by `depth > 6 or (path, para) in seen` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-419
  Scenario: Branch guarded by `f.kind == "accept"` in walk
    Given an input that exercises: Branch guarded by `f.kind == "accept"` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-420
  Scenario: Branch guarded by `tgt` in walk
    Given an input that exercises: Branch guarded by `tgt` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-421
  Scenario: Branch guarded by `arg` in walk
    Given an input that exercises: Branch guarded by `arg` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-422
  Scenario: Branch guarded by `nxt` in walk
    Given an input that exercises: Branch guarded by `nxt` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-423
  Scenario: Branch guarded by `entry` in walk
    Given an input that exercises: Branch guarded by `entry` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-424
  Scenario: Branch guarded by `not path` in walk
    Given an input that exercises: Branch guarded by `not path` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-425
  Scenario: Branch guarded by `first` in walk
    Given an input that exercises: Branch guarded by `first` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-426
  Scenario: Branch guarded by `f.kind == "perform" and not any(d.detail == f.name for d in dispatches` in walk
    Given an input that exercises: Branch guarded by `f.kind == "perform" and not any(d.detail == f.name for d in dispatches` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-427
  Scenario: Branch guarded by `pre_steps` in walk
    Given an input that exercises: Branch guarded by `pre_steps` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-428
  Scenario: Branch guarded by `c.name.upper() == "OTHER"` in walk
    Given an input that exercises: Branch guarded by `c.name.upper() == "OTHER"` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-429
  Scenario: Branch guarded by `mv` in walk
    Given an input that exercises: Branch guarded by `mv` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-430
  Scenario: Branch guarded by `x.kind == "perform"` in walk
    Given an input that exercises: Branch guarded by `x.kind == "perform"` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-431
  Scenario: Branch guarded by `tgt` in walk
    Given an input that exercises: Branch guarded by `tgt` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-432
  Scenario: Branch guarded by `nx` in walk
    Given an input that exercises: Branch guarded by `nx` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-433
  Scenario: Branch guarded by `entry` in walk
    Given an input that exercises: Branch guarded by `entry` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-434
  Scenario: Branch guarded by `first is not None` in walk
    Given an input that exercises: Branch guarded by `first is not None` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-435
  Scenario: Branch guarded by `first + 1 < len(steps) and steps[first + 1]["action"].startswith(f"{label} dispatches"` in walk
    Given an input that exercises: Branch guarded by `first + 1 < len(steps) and steps[first + 1]["action"].startswith(f"{label} dispatches"` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-436
  Scenario: Branch guarded by `steps` in walk
    Given an input that exercises: Branch guarded by `steps` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-437
  Scenario: Branch guarded by `not processes` in walk
    Given an input that exercises: Branch guarded by `not processes` in walk
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-438
  Scenario: Branch guarded by `e.get("fields"` in refs
    Given an input that exercises: Branch guarded by `e.get("fields"` in refs
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-439
  Scenario: Branch guarded by `e.get("evidence"` in refs
    Given an input that exercises: Branch guarded by `e.get("evidence"` in refs
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-440
  Scenario: Branch guarded by `"start-up" in p.get("name", ""` in refs
    Given an input that exercises: Branch guarded by `"start-up" in p.get("name", ""` in refs
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-441
  Scenario: Branch guarded by `nic` in refs
    Given an input that exercises: Branch guarded by `nic` in refs
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-442
  Scenario: Branch guarded by `p.get("description"` in _write
    Given an input that exercises: Branch guarded by `p.get("description"` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-443
  Scenario: Branch guarded by `dec` in _write
    Given an input that exercises: Branch guarded by `dec` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-444
  Scenario: Branch guarded by `len(out_t) > 60` in _write
    Given an input that exercises: Branch guarded by `len(out_t) > 60` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-445
  Scenario: Branch guarded by `not processes` in _write
    Given an input that exercises: Branch guarded by `not processes` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

@unit-detective
Feature: DETECTIVE parity
  Legacy and go implementations must behave identically for DETECTIVE.

  @parity @C-386
  Scenario: Branch guarded by `near and _CMP.search(text` in heuristic
    Given an input that exercises: Branch guarded by `near and _CMP.search(text` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-387
  Scenario: Branch guarded by `n in ("0", "1") or n in seen_consts` in heuristic
    Given an input that exercises: Branch guarded by `n in ("0", "1") or n in seen_consts` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-388
  Scenario: Branch guarded by `cases` in heuristic
    Given an input that exercises: Branch guarded by `cases` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-389
  Scenario: Branch guarded by `not any(0 < m.line - c.line <= 4 for c in ff.of("condition")` in heuristic
    Given an input that exercises: Branch guarded by `not any(0 < m.line - c.line <= 4 for c in ff.of("condition")` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-390
  Scenario: Branch guarded by `re.search(r"(senha|pin|pass|auth|login|usuario|user)", a.name, re.I` in heuristic
    Given an input that exercises: Branch guarded by `re.search(r"(senha|pin|pass|auth|login|usuario|user)", a.name, re.I` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-391
  Scenario: Branch guarded by `not ff.of("condition") and not ff.of("dispatch"` in heuristic
    Given an input that exercises: Branch guarded by `not ff.of("condition") and not ff.of("dispatch"` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-392
  Scenario: Branch guarded by `isinstance(idx, int) and 0 <= idx < len(made` in run
    Given an input that exercises: Branch guarded by `isinstance(idx, int) and 0 <= idx < len(made` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-393
  Scenario: Branch guarded by `not cs` in _write
    Given an input that exercises: Branch guarded by `not cs` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-394
  Scenario: Branch guarded by `not sub` in _write
    Given an input that exercises: Branch guarded by `not sub` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-395
  Scenario: Branch guarded by `st` in _write
    Given an input that exercises: Branch guarded by `st` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

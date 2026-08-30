@unit-scout
Feature: SCOUT parity
  Legacy and go implementations must behave identically for SCOUT.

  @parity @C-456
  Scenario: Branch guarded by `f["path"] not in facts_by` in heuristic
    Given an input that exercises: Branch guarded by `f["path"] not in facts_by` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-457
  Scenario: Branch guarded by `prog` in heuristic
    Given an input that exercises: Branch guarded by `prog` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-458
  Scenario: Branch guarded by `f["path"] not in facts_by` in heuristic
    Given an input that exercises: Branch guarded by `f["path"] not in facts_by` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-459
  Scenario: Branch guarded by `tgt in seen` in heuristic
    Given an input that exercises: Branch guarded by `tgt in seen` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-460
  Scenario: Branch guarded by `c.kind == "call" and tgt not in known_units` in heuristic
    Given an input that exercises: Branch guarded by `c.kind == "call" and tgt not in known_units` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-461
  Scenario: Branch guarded by `not files` in run
    Given an input that exercises: Branch guarded by `not files` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-462
  Scenario: Branch guarded by `ev` in _unit_for
    Given an input that exercises: Branch guarded by `ev` in _unit_for
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-463
  Scenario: Branch guarded by `f in u.files` in _unit_for
    Given an input that exercises: Branch guarded by `f in u.files` in _unit_for
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

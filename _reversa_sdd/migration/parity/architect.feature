@unit-architect
Feature: ARCHITECT parity
  Legacy and go implementations must behave identically for ARCHITECT.

  @parity @C-372
  Scenario: Branch guarded by `entry` in heuristic
    Given an input that exercises: Branch guarded by `entry` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-373
  Scenario: Branch guarded by `shared` in heuristic
    Given an input that exercises: Branch guarded by `shared` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-374
  Scenario: Branch guarded by `rest` in heuristic
    Given an input that exercises: Branch guarded by `rest` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-375
  Scenario: Branch guarded by `n >= 2` in heuristic
    Given an input that exercises: Branch guarded by `n >= 2` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-376
  Scenario: Branch guarded by `len(users) >= 2` in heuristic
    Given an input that exercises: Branch guarded by `len(users) >= 2` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-377
  Scenario: Branch guarded by `not entry` in heuristic
    Given an input that exercises: Branch guarded by `not entry` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-378
  Scenario: Branch guarded by `c.kind == ClaimKind.DEPENDENCY` in run
    Given an input that exercises: Branch guarded by `c.kind == ClaimKind.DEPENDENCY` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-379
  Scenario: Branch guarded by `m` in run
    Given an input that exercises: Branch guarded by `m` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-380
  Scenario: Branch guarded by `c.kind == ClaimKind.DATA` in run
    Given an input that exercises: Branch guarded by `c.kind == ClaimKind.DATA` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-381
  Scenario: Branch guarded by `m` in run
    Given an input that exercises: Branch guarded by `m` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-382
  Scenario: Branch guarded by `a != b` in _write
    Given an input that exercises: Branch guarded by `a != b` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

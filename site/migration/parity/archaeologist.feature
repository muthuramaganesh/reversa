@unit-archaeologist
Feature: ARCHAEOLOGIST parity
  Legacy and go implementations must behave identically for ARCHAEOLOGIST.

  @parity @C-365
  Scenario: Branch guarded by `paras` in heuristic
    Given an input that exercises: Branch guarded by `paras` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-366
  Scenario: Branch guarded by `lk` in heuristic
    Given an input that exercises: Branch guarded by `lk` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-367
  Scenario: Branch guarded by `ws` in heuristic
    Given an input that exercises: Branch guarded by `ws` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-368
  Scenario: Branch guarded by `acc` in heuristic
    Given an input that exercises: Branch guarded by `acc` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-369
  Scenario: Branch guarded by `not any(x.name == p.name for x in paras` in heuristic
    Given an input that exercises: Branch guarded by `not any(x.name == p.name for x in paras` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-370
  Scenario: Branch guarded by `not paras and not ff.of("select") and not ws` in heuristic
    Given an input that exercises: Branch guarded by `not paras and not ff.of("select") and not ws` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-371
  Scenario: Branch guarded by `out.get("summary") and not u.description` in run
    Given an input that exercises: Branch guarded by `out.get("summary") and not u.description` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

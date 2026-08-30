@unit-migration
Feature: MIGRATION parity
  Legacy and go implementations must behave identically for MIGRATION.

  @parity @C-396
  Scenario: Branch guarded by `c["kind"] not in {k.value for k in _SCEN_KINDS} or c["confidence"] == "gap"` in heuristic
    Given an input that exercises: Branch guarded by `c["kind"] not in {k.value for k in _SCEN_KINDS} or c["confidence"] == "gap"` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-397
  Scenario: Branch guarded by `c["kind"] == "exception"` in heuristic
    Given an input that exercises: Branch guarded by `c["kind"] == "exception"` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-398
  Scenario: Branch guarded by `n_inf` in heuristic
    Given an input that exercises: Branch guarded by `n_inf` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

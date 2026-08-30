@unit-writer
Feature: WRITER parity
  Legacy and go implementations must behave identically for WRITER.

  @parity @C-464
  Scenario: Branch guarded by `c["kind"] in {k.value for k in _REQ_KINDS}` in heuristic
    Given an input that exercises: Branch guarded by `c["kind"] in {k.value for k in _REQ_KINDS}` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-465
  Scenario: Branch guarded by `not cids` in run
    Given an input that exercises: Branch guarded by `not cids` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

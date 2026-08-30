@unit-manifest
Feature: MANIFEST parity
  Legacy and go implementations must behave identically for MANIFEST.

  @parity @C-344
  Scenario: Branch guarded by `self.path.exists(` in load
    Given an input that exercises: Branch guarded by `self.path.exists(` in load
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-345
  Scenario: Branch guarded by `not p.exists(` in classify
    Given an input that exercises: Branch guarded by `not p.exists(` in classify
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-346
  Scenario: Branch guarded by `fs.path == rel` in status_of
    Given an input that exercises: Branch guarded by `fs.path == rel` in status_of
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

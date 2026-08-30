@unit-engines
Feature: ENGINES parity
  Legacy and go implementations must behave identically for ENGINES.

  @parity @C-327
  Scenario: Branch guarded by `any((root / m).exists() for m in e.markers` in detect_engines
    Given an input that exercises: Branch guarded by `any((root / m).exists() for m in e.markers` in detect_engines
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-328
  Scenario: Branch guarded by `keys` in resolve_engines
    Given an input that exercises: Branch guarded by `keys` in resolve_engines
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-329
  Scenario: Branch guarded by `unknown` in resolve_engines
    Given an input that exercises: Branch guarded by `unknown` in resolve_engines
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

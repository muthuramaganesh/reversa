@unit-reviewer
Feature: REVIEWER parity
  Legacy and go implementations must behave identically for REVIEWER.

  @parity @C-446
  Scenario: Branch guarded by `c["id"] in answered` in heuristic
    Given an input that exercises: Branch guarded by `c["id"] in answered` in heuristic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-447
  Scenario: Branch guarded by `c.confidence == Confidence.GAP` in run
    Given an input that exercises: Branch guarded by `c.confidence == Confidence.GAP` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-448
  Scenario: Branch guarded by `not c.evidence` in run
    Given an input that exercises: Branch guarded by `not c.evidence` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-449
  Scenario: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run
    Given an input that exercises: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-450
  Scenario: Branch guarded by `not any(ok for ok, _ in results` in run
    Given an input that exercises: Branch guarded by `not any(ok for ok, _ in results` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-451
  Scenario: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run
    Given an input that exercises: Branch guarded by `c.confidence == Confidence.CONFIRMED` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-452
  Scenario: Branch guarded by `not c` in run
    Given an input that exercises: Branch guarded by `not c` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-453
  Scenario: Branch guarded by `new == Confidence.CONFIRMED and not (c.evidence and any(` in run
    Given an input that exercises: Branch guarded by `new == Confidence.CONFIRMED and not (c.evidence and any(` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-454
  Scenario: Branch guarded by `new != c.confidence` in run
    Given an input that exercises: Branch guarded by `new != c.confidence` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-455
  Scenario: Branch guarded by `new == Confidence.GAP` in run
    Given an input that exercises: Branch guarded by `new == Confidence.GAP` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

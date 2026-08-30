@unit-models
Feature: MODELS parity
  Legacy and go implementations must behave identically for MODELS.

  @parity @C-347
  Scenario: Branch guarded by `self.line_start == self.line_end` in ref
    Given an input that exercises: Branch guarded by `self.line_start == self.line_end` in ref
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-348
  Scenario: Branch guarded by `m` in next_id
    Given an input that exercises: Branch guarded by `m` in next_id
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-349
  Scenario: Branch guarded by `not isinstance(kw.get("kind"), ClaimKind` in add_claim
    Given an input that exercises: Branch guarded by `not isinstance(kw.get("kind"), ClaimKind` in add_claim
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-350
  Scenario: Branch guarded by `not isinstance(kw.get("confidence"), Confidence` in add_claim
    Given an input that exercises: Branch guarded by `not isinstance(kw.get("confidence"), Confidence` in add_claim
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-351
  Scenario: Branch guarded by `g.unit == kw.get("unit") and g.description == kw.get("description"` in add_gap
    Given an input that exercises: Branch guarded by `g.unit == kw.get("unit") and g.description == kw.get("description"` in add_gap
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-352
  Scenario: Branch guarded by `not isinstance(sev, Severity` in add_gap
    Given an input that exercises: Branch guarded by `not isinstance(sev, Severity` in add_gap
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-353
  Scenario: Branch guarded by `q.unit == kw.get("unit") and q.question == kw.get("question"` in add_question
    Given an input that exercises: Branch guarded by `q.unit == kw.get("unit") and q.question == kw.get("question"` in add_question
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-354
  Scenario: Branch guarded by `c not in q.related_claims` in add_question
    Given an input that exercises: Branch guarded by `c not in q.related_claims` in add_question
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-355
  Scenario: Branch guarded by `not path.exists(` in load
    Given an input that exercises: Branch guarded by `not path.exists(` in load
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

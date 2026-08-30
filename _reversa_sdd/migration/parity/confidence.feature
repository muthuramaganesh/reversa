@unit-confidence
Feature: CONFIDENCE parity
  Legacy and go implementations must behave identically for CONFIDENCE.

  @parity @C-320
  Scenario: Branch guarded by `self.total == 0` in index
    Given an input that exercises: Branch guarded by `self.total == 0` in index
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-321
  Scenario: Branch guarded by `not claims` in traceability_density
    Given an input that exercises: Branch guarded by `not claims` in traceability_density
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-322
  Scenario: Branch guarded by `not p.exists(` in verify_evidence
    Given an input that exercises: Branch guarded by `not p.exists(` in verify_evidence
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-323
  Scenario: Branch guarded by `ev.line_start < 1 or ev.line_start > len(lines` in verify_evidence
    Given an input that exercises: Branch guarded by `ev.line_start < 1 or ev.line_start > len(lines` in verify_evidence
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-324
  Scenario: Branch guarded by `not ev.excerpt.strip(` in verify_evidence
    Given an input that exercises: Branch guarded by `not ev.excerpt.strip(` in verify_evidence
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-325
  Scenario: Branch guarded by `_norm(ev.excerpt) in region` in verify_evidence
    Given an input that exercises: Branch guarded by `_norm(ev.excerpt) in region` in verify_evidence
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-326
  Scenario: Branch guarded by `head and head in region` in verify_evidence
    Given an input that exercises: Branch guarded by `head and head in region` in verify_evidence
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

@unit-anthropic-backend
Feature: ANTHROPIC_BACKEND parity
  Legacy and go implementations must behave identically for ANTHROPIC_BACKEND.

  @parity @C-466
  Scenario: Branch guarded by `not self.api_key` in __init__
    Given an input that exercises: Branch guarded by `not self.api_key` in __init__
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-467
  Scenario: Branch guarded by `b.get("type") == "text"` in _call
    Given an input that exercises: Branch guarded by `b.get("type") == "text"` in _call
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-468
  Scenario: Branch guarded by `e.code in (429, 500, 502, 503, 529` in _call
    Given an input that exercises: Branch guarded by `e.code in (429, 500, 502, 503, 529` in _call
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-469
  Scenario: ANTHROPIC_BACKEND can emit the message "Anthropic API failed after retries: {last}"
    Given the ANTHROPIC_BACKEND unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: ANTHROPIC_BACKEND can emit the message "Anthropic API failed after retries: {last}"
    And the message or error is identical in both

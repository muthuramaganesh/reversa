@unit-base
Feature: BASE parity
  Legacy and go implementations must behave identically for BASE.

  @parity @C-383
  Scenario: Branch guarded by `self.units_filter` in selected_units
    Given an input that exercises: Branch guarded by `self.units_filter` in selected_units
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-384
  Scenario: Branch guarded by `not stmt` in add_claims
    Given an input that exercises: Branch guarded by `not stmt` in add_claims
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-385
  Scenario: Branch guarded by `conf == Confidence.CONFIRMED and not ev` in add_claims
    Given an input that exercises: Branch guarded by `conf == Confidence.CONFIRMED and not ev` in add_claims
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-470
  Scenario: Branch guarded by `TYPE_CHECKING:  # pragma: no cover`
    Given an input that exercises: Branch guarded by `TYPE_CHECKING:  # pragma: no cover`
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-471
  Scenario: Branch guarded by `start == -1 or end == -1` in strip_json
    Given an input that exercises: Branch guarded by `start == -1 or end == -1` in strip_json
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-472
  Scenario: When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply"
    Given the BASE unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply"
    And the message or error is identical in both

  @parity @C-473
  Scenario: Branch guarded by `name == "heuristic"` in get_backend
    Given an input that exercises: Branch guarded by `name == "heuristic"` in get_backend
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-474
  Scenario: Branch guarded by `name == "anthropic"` in get_backend
    Given an input that exercises: Branch guarded by `name == "anthropic"` in get_backend
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-475
  Scenario: Branch guarded by `name == "auto"` in get_backend
    Given an input that exercises: Branch guarded by `name == "auto"` in get_backend
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-476
  Scenario: Branch guarded by `os.environ.get("ANTHROPIC_API_KEY"` in get_backend
    Given an input that exercises: Branch guarded by `os.environ.get("ANTHROPIC_API_KEY"` in get_backend
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-477
  Scenario: BASE can emit the message "unknown backend: {name}"
    Given the BASE unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: BASE can emit the message "unknown backend: {name}"
    And the message or error is identical in both

@unit-util
Feature: UTIL parity
  Legacy and go implementations must behave identically for UTIL.

  @parity @C-068
  Scenario: UTIL dispatches on `LK-FUNC` with cases: 'F', 'M', OTHER
    Given the UTIL unit in both implementations
    When the same user actions are replayed
    Then both preserve: UTIL dispatches on `LK-FUNC` with cases: 'F', 'M', OTHER

  @parity @C-069
  Scenario: UTIL can emit the message "FUNCAO UTIL INVALIDA"
    Given the UTIL unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: UTIL can emit the message "FUNCAO UTIL INVALIDA"
    And the message or error is identical in both

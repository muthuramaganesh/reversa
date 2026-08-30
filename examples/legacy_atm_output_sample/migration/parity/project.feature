@unit-project
Feature: PROJECT parity
  Legacy and go implementations must behave identically for PROJECT.

  @parity @C-074
  Scenario: Selecting '1' at MENU runs SALDO with 0 validation(s) and 0 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '1' at MENU runs SALDO with 0 validation(s) and 0 data write(s)/read(s)

  @parity @C-075
  Scenario: Selecting '2' at MENU runs SAQUE with 3 validation(s) and 2 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '2' at MENU runs SAQUE with 3 validation(s) and 2 data write(s)/read(s)

  @parity @C-076
  Scenario: Selecting '3' at MENU runs DEPOSITO with 1 validation(s) and 2 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '3' at MENU runs DEPOSITO with 1 validation(s) and 2 data write(s)/read(s)

  @parity @C-077
  Scenario: Selecting '4' at MENU runs TRANSFERENCIA with 2 validation(s) and 4 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '4' at MENU runs TRANSFERENCIA with 2 validation(s) and 4 data write(s)/read(s)

  @parity @C-078
  Scenario: Selecting '5' at MENU runs EXTRATO with 2 validation(s) and 1 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '5' at MENU runs EXTRATO with 2 validation(s) and 1 data write(s)/read(s)

  @parity @C-079
  Scenario: Selecting '9' at MENU runs Set WS-FIM to 'S' with 0 validation(s) and 0 data write(s)/read(s)
    Given the project unit in both implementations
    When the same user actions are replayed
    Then both preserve: Selecting '9' at MENU runs Set WS-FIM to 'S' with 0 validation(s) and 0 data write(s)/read(s)

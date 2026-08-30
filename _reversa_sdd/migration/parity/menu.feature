@unit-menu
Feature: MENU parity
  Legacy and go implementations must behave identically for MENU.

  @parity @C-254
  Scenario: Branch guarded by `WS-TENTATIVAS >= 3` in MAIN
    Given an input that exercises: Branch guarded by `WS-TENTATIVAS >= 3` in MAIN
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-255
  Scenario: When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO"
    Given the MENU unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO"
    And the message or error is identical in both

  @parity @C-256
  Scenario: Branch guarded by `CLI-STATUS = 'B'` in LOGIN
    Given an input that exercises: Branch guarded by `CLI-STATUS = 'B'` in LOGIN
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-257
  Scenario: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA"
    Given the MENU unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA"
    And the message or error is identical in both

  @parity @C-258
  Scenario: Branch guarded by `WS-SENHA NOT = CLI-SENHA` in LOGIN
    Given an input that exercises: Branch guarded by `WS-SENHA NOT = CLI-SENHA` in LOGIN
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-259
  Scenario: When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA"
    Given the MENU unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA"
    And the message or error is identical in both

  @parity @C-260
  Scenario: MENU dispatches on `WS-OPCAO` with cases: '1', '2', '3', '4', '5', '9', OTHER
    Given the MENU unit in both implementations
    When the same user actions are replayed
    Then both preserve: MENU dispatches on `WS-OPCAO` with cases: '1', '2', '3', '4', '5', '9', OTHER

  @parity @C-261
  Scenario: MENU can emit the message "CONTA INVALIDA"
    Given the MENU unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: MENU can emit the message "CONTA INVALIDA"
    And the message or error is identical in both

  @parity @C-262
  Scenario: MENU can emit the message "OPCAO INVALIDA"
    Given the MENU unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: MENU can emit the message "OPCAO INVALIDA"
    And the message or error is identical in both

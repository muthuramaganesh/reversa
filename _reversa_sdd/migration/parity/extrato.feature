@unit-extrato
Feature: EXTRATO parity
  Legacy and go implementations must behave identically for EXTRATO.

  @parity @C-251
  Scenario: Branch guarded by `WS-QTD = 0` in MAIN
    Given an input that exercises: Branch guarded by `WS-QTD = 0` in MAIN
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-252
  Scenario: When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS"
    Given the EXTRATO unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS"
    And the message or error is identical in both

  @parity @C-253
  Scenario: Branch guarded by `MOV-CONTA = LK-CONTA` in MOSTRA
    Given an input that exercises: Branch guarded by `MOV-CONTA = LK-CONTA` in MOSTRA
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

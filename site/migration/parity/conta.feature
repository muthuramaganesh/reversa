@unit-conta
Feature: CONTA parity
  Legacy and go implementations must behave identically for CONTA.

  @parity @C-237
  Scenario: Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE
    Given an input that exercises: Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-238
  Scenario: When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO"
    And the message or error is identical in both

  @parity @C-239
  Scenario: Branch guarded by `WS-VALOR > LK-SALDO` in SAQUE
    Given an input that exercises: Branch guarded by `WS-VALOR > LK-SALDO` in SAQUE
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-240
  Scenario: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE"
    And the message or error is identical in both

  @parity @C-241
  Scenario: Branch guarded by `FUNCTION MOD(WS-VALOR, 10) NOT = 0` in SAQUE
    Given an input that exercises: Branch guarded by `FUNCTION MOD(WS-VALOR, 10) NOT = 0` in SAQUE
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-242
  Scenario: When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10"
    And the message or error is identical in both

  @parity @C-243
  Scenario: Branch guarded by `WS-VALOR = 0` in DEPOSITO
    Given an input that exercises: Branch guarded by `WS-VALOR = 0` in DEPOSITO
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-244
  Scenario: When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO"
    And the message or error is identical in both

  @parity @C-245
  Scenario: Branch guarded by `WS-VALOR > LK-SALDO` in TRANSFERENCIA
    Given an input that exercises: Branch guarded by `WS-VALOR > LK-SALDO` in TRANSFERENCIA
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-246
  Scenario: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE"
    And the message or error is identical in both

  @parity @C-247
  Scenario: Branch guarded by `CLI-STATUS = 'B'` in TRANSFERENCIA
    Given an input that exercises: Branch guarded by `CLI-STATUS = 'B'` in TRANSFERENCIA
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-248
  Scenario: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA"
    And the message or error is identical in both

  @parity @C-249
  Scenario: CONTA dispatches on `LK-OP` with cases: 'S', 'Q', 'D', 'T'
    Given the CONTA unit in both implementations
    When the same user actions are replayed
    Then both preserve: CONTA dispatches on `LK-OP` with cases: 'S', 'Q', 'D', 'T'

  @parity @C-250
  Scenario: CONTA can emit the message "CONTA DESTINO INEXISTENTE"
    Given the CONTA unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: CONTA can emit the message "CONTA DESTINO INEXISTENTE"
    And the message or error is identical in both

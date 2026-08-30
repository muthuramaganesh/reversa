@unit-main
Feature: __MAIN__ parity
  Legacy and go implementations must behave identically for __MAIN__.

  @parity @C-266
  Scenario: Branch guarded by `__name__ == "__main__"`
    Given an input that exercises: Branch guarded by `__name__ == "__main__"`
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @needs-validation @C-267
  Scenario: When `__name__ == "__main__"` holds, the operation is rejected with message "SystemExit(main())"
    Given the __MAIN__ unit is running in both legacy and go
    When the triggering condition occurs
    Then both implementations behave as: When `__name__ == "__main__"` holds, the operation is rejected with message "SystemExit(main())"
    And the message or error is identical in both

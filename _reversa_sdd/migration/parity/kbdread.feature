@unit-kbdread
Feature: KBDREAD parity
  Legacy and go implementations must behave identically for KBDREAD.

  @parity @C-265
  Scenario: Branch guarded by `c < '0' || c > '9') { i--; continue; }` in KBDREAD
    Given an input that exercises: Branch guarded by `c < '0' || c > '9') { i--; continue; }` in KBDREAD
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

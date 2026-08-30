@unit-test-pipeline
Feature: TEST_PIPELINE parity
  Legacy and go implementations must behave identically for TEST_PIPELINE.

  @parity @C-478
  Scenario: Branch guarded by `c.confidence == Confidence.CONFIRMED` in test_discovery_and_migration_offline
    Given an input that exercises: Branch guarded by `c.confidence == Confidence.CONFIRMED` in test_discovery_and_migration_offline
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

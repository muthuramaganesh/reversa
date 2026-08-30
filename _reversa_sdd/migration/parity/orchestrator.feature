@unit-orchestrator
Feature: ORCHESTRATOR parity
  Legacy and go implementations must behave identically for ORCHESTRATOR.

  @parity @C-356
  Scenario: Branch guarded by `path.exists(` in load
    Given an input that exercises: Branch guarded by `path.exists(` in load
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-357
  Scenario: Branch guarded by `only` in run
    Given an input that exercises: Branch guarded by `only` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-358
  Scenario: Branch guarded by `not resume and team in ("discovery", "all") and not only` in run
    Given an input that exercises: Branch guarded by `not resume and team in ("discovery", "all") and not only` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-359
  Scenario: Branch guarded by `not self.state.started` in run
    Given an input that exercises: Branch guarded by `not self.state.started` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-360
  Scenario: Branch guarded by `resume and not only and st.get("status") == "done"` in run
    Given an input that exercises: Branch guarded by `resume and not only and st.get("status") == "done"` in run
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

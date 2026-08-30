@unit-cli
Feature: CLI parity
  Legacy and go implementations must behave identically for CLI.

  @parity @C-313
  Scenario: Branch guarded by `not files` in cmd_status
    Given an input that exercises: Branch guarded by `not files` in cmd_status
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-314
  Scenario: Branch guarded by `args.verbose or f.status != "intact"` in cmd_status
    Given an input that exercises: Branch guarded by `args.verbose or f.status != "intact"` in cmd_status
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-315
  Scenario: Branch guarded by `st.exists(` in cmd_status
    Given an input that exercises: Branch guarded by `st.exists(` in cmd_status
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-316
  Scenario: Branch guarded by `not o.registry.claims` in cmd_migrate
    Given an input that exercises: Branch guarded by `not o.registry.claims` in cmd_migrate
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-317
  Scenario: Branch guarded by `q.id == args.id` in cmd_answer
    Given an input that exercises: Branch guarded by `q.id == args.id` in cmd_answer
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-318
  Scenario: Branch guarded by `g.id == args.id` in cmd_answer
    Given an input that exercises: Branch guarded by `g.id == args.id` in cmd_answer
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-319
  Scenario: Branch guarded by `not hit` in cmd_answer
    Given an input that exercises: Branch guarded by `not hit` in cmd_answer
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

@unit-installer
Feature: INSTALLER parity
  Legacy and go implementations must behave identically for INSTALLER.

  @parity @C-330
  Scenario: Branch guarded by `status == "modified" and not force` in _write
    Given an input that exercises: Branch guarded by `status == "modified" and not force` in _write
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-331
  Scenario: Branch guarded by `not (root / STATE_DIR / "config.user.toml").exists(` in w
    Given an input that exercises: Branch guarded by `not (root / STATE_DIR / "config.user.toml").exists(` in w
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-332
  Scenario: Branch guarded by `v` in w
    Given an input that exercises: Branch guarded by `v` in w
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-333
  Scenario: Branch guarded by `cfg.exists(` in update
    Given an input that exercises: Branch guarded by `cfg.exists(` in update
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-334
  Scenario: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in update
    Given an input that exercises: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in update
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-335
  Scenario: Branch guarded by `line.startswith("dir = "` in update
    Given an input that exercises: Branch guarded by `line.startswith("dir = "` in update
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-336
  Scenario: Branch guarded by `line.startswith("["` in _section_before
    Given an input that exercises: Branch guarded by `line.startswith("["` in _section_before
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-337
  Scenario: Branch guarded by `line == target` in _section_before
    Given an input that exercises: Branch guarded by `line == target` in _section_before
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-338
  Scenario: Branch guarded by `fs.status == "intact" or (fs.status == "modified" and purge` in uninstall
    Given an input that exercises: Branch guarded by `fs.status == "intact" or (fs.status == "modified" and purge` in uninstall
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-339
  Scenario: Branch guarded by `d.exists() and not any(d.iterdir()` in uninstall
    Given an input that exercises: Branch guarded by `d.exists() and not any(d.iterdir()` in uninstall
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-340
  Scenario: Branch guarded by `not out["preserved"] and (root / STATE_DIR).exists(` in uninstall
    Given an input that exercises: Branch guarded by `not out["preserved"] and (root / STATE_DIR).exists(` in uninstall
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-341
  Scenario: Branch guarded by `not cfg.exists(` in add_engine
    Given an input that exercises: Branch guarded by `not cfg.exists(` in add_engine
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-342
  Scenario: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in add_engine
    Given an input that exercises: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in add_engine
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-343
  Scenario: Branch guarded by `key not in cur` in add_engine
    Given an input that exercises: Branch guarded by `key not in cur` in add_engine
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

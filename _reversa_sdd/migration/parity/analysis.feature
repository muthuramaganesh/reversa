@unit-analysis
Feature: ANALYSIS parity
  Legacy and go implementations must behave identically for ANALYSIS.

  @parity @C-268
  Scenario: Branch guarded by `_is_comment(raw` in analyze_cobol
    Given an input that exercises: Branch guarded by `_is_comment(raw` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-269
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-270
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-271
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-272
  Scenario: Branch guarded by `division == "DATA"` in analyze_cobol
    Given an input that exercises: Branch guarded by `division == "DATA"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-273
  Scenario: Branch guarded by `division == "PROCEDURE"` in analyze_cobol
    Given an input that exercises: Branch guarded by `division == "PROCEDURE"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-274
  Scenario: Branch guarded by `division == "ENVIRONMENT"` in analyze_cobol
    Given an input that exercises: Branch guarded by `division == "ENVIRONMENT"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-275
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-276
  Scenario: Branch guarded by `division == "DATA"` in analyze_cobol
    Given an input that exercises: Branch guarded by `division == "DATA"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-277
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-278
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-279
  Scenario: Branch guarded by `m and m.group(3` in analyze_cobol
    Given an input that exercises: Branch guarded by `m and m.group(3` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-280
  Scenario: Branch guarded by `lvl == "01"` in analyze_cobol
    Given an input that exercises: Branch guarded by `lvl == "01"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-281
  Scenario: Branch guarded by `val` in analyze_cobol
    Given an input that exercises: Branch guarded by `val` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-282
  Scenario: Branch guarded by `division == "PROCEDURE"` in analyze_cobol
    Given an input that exercises: Branch guarded by `division == "PROCEDURE"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-283
  Scenario: Branch guarded by `m and m.group(1).upper() not in _KEYWORDS` in analyze_cobol
    Given an input that exercises: Branch guarded by `m and m.group(1).upper() not in _KEYWORDS` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-284
  Scenario: Branch guarded by `tgt not in _KEYWORDS and tgt not in ("UNTIL", "VARYING", "WITH"` in analyze_cobol
    Given an input that exercises: Branch guarded by `tgt not in _KEYWORDS and tgt not in ("UNTIL", "VARYING", "WITH"` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-285
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-286
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-287
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-288
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-289
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-290
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-291
  Scenario: Branch guarded by `m` in analyze_cobol
    Given an input that exercises: Branch guarded by `m` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-292
  Scenario: Branch guarded by `tok in _OPEN_MODES` in analyze_cobol
    Given an input that exercises: Branch guarded by `tok in _OPEN_MODES` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-293
  Scenario: Branch guarded by `_STOP.search(line` in analyze_cobol
    Given an input that exercises: Branch guarded by `_STOP.search(line` in analyze_cobol
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-294
  Scenario: Branch guarded by `not s or (s.startswith("#") and not s.startswith("#include")) or s.startswith(("//", "/*", "*")`...
    Given an input that exercises: Branch guarded by `not s or (s.startswith("#") and not s.startswith("#include")) or s.startswith(("//", "/*", "*")` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-295
  Scenario: Branch guarded by `m` in analyze_generic
    Given an input that exercises: Branch guarded by `m` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-296
  Scenario: Branch guarded by `m and m.group(1) not in ("if", "for", "while", "switch", "return"` in analyze_generic
    Given an input that exercises: Branch guarded by `m and m.group(1) not in ("if", "for", "while", "switch", "return"` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-297
  Scenario: Branch guarded by `m` in analyze_generic
    Given an input that exercises: Branch guarded by `m` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-298
  Scenario: Branch guarded by `_G_MAIN.search(line` in analyze_generic
    Given an input that exercises: Branch guarded by `_G_MAIN.search(line` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-299
  Scenario: Branch guarded by `m` in analyze_generic
    Given an input that exercises: Branch guarded by `m` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-300
  Scenario: Branch guarded by `m` in analyze_generic
    Given an input that exercises: Branch guarded by `m` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-301
  Scenario: Branch guarded by `m` in analyze_generic
    Given an input that exercises: Branch guarded by `m` in analyze_generic
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-302
  Scenario: Branch guarded by `language.startswith("cobol"` in analyze
    Given an input that exercises: Branch guarded by `language.startswith("cobol"` in analyze
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-303
  Scenario: Branch guarded by `"V" in p` in count
    Given an input that exercises: Branch guarded by `"V" in p` in count
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-304
  Scenario: Branch guarded by `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` in count
    Given an input that exercises: Branch guarded by `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` in count
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-305
  Scenario: Branch guarded by `"X" in p` in count
    Given an input that exercises: Branch guarded by `"X" in p` in count
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-306
  Scenario: Branch guarded by `"Z" in p or "-" in p or "," in p` in count
    Given an input that exercises: Branch guarded by `"Z" in p or "-" in p or "," in p` in count
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-307
  Scenario: Branch guarded by `_IF_OPEN.match(txt` in aborts_in_branch
    Given an input that exercises: Branch guarded by `_IF_OPEN.match(txt` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-308
  Scenario: Branch guarded by `depth == 1 and re.match(r"^\s*ELSE\b", txt, re.I` in aborts_in_branch
    Given an input that exercises: Branch guarded by `depth == 1 and re.match(r"^\s*ELSE\b", txt, re.I` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-309
  Scenario: Branch guarded by `_EXIT.search(txt) and depth >= 1` in aborts_in_branch
    Given an input that exercises: Branch guarded by `_EXIT.search(txt) and depth >= 1` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-310
  Scenario: Branch guarded by `_IF_CLOSE.match(txt` in aborts_in_branch
    Given an input that exercises: Branch guarded by `_IF_CLOSE.match(txt` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-311
  Scenario: Branch guarded by `depth <= 0` in aborts_in_branch
    Given an input that exercises: Branch guarded by `depth <= 0` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

  @parity @C-312
  Scenario: Branch guarded by `depth >= 1 and txt.rstrip().endswith(".") and not _IF_OPEN.match(txt` in aborts_in_branch
    Given an input that exercises: Branch guarded by `depth >= 1 and txt.rstrip().endswith(".") and not _IF_OPEN.match(txt` in aborts_in_branch
    When the operation is executed on legacy and on go
    Then both accept or reject the input identically
    And any resulting balances or outputs are identical

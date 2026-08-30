# Requirements — ANALYSIS

ANALYSIS — purpose reconstructed from 50 claims (50 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `_is_comment(raw` in analyze_cobol.  
  _claims: C-268 · evidence: reversa/analysis.py:88_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-269 · evidence: reversa/analysis.py:92_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-270 · evidence: reversa/analysis.py:97_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-271 · evidence: reversa/analysis.py:101_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `division == "DATA"` in analyze_cobol.  
  _claims: C-272 · evidence: reversa/analysis.py:103_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `division == "PROCEDURE"` in analyze_cobol.  
  _claims: C-273 · evidence: reversa/analysis.py:106_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `division == "ENVIRONMENT"` in analyze_cobol.  
  _claims: C-274 · evidence: reversa/analysis.py:109_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-275 · evidence: reversa/analysis.py:111_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `division == "DATA"` in analyze_cobol.  
  _claims: C-276 · evidence: reversa/analysis.py:118_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-277 · evidence: reversa/analysis.py:120_
- ✅ **REQ-11** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-278 · evidence: reversa/analysis.py:124_
- ✅ **REQ-12** The reimplementation shall preserve: Branch guarded by `m and m.group(3` in analyze_cobol.  
  _claims: C-279 · evidence: reversa/analysis.py:129_
- ✅ **REQ-13** The reimplementation shall preserve: Branch guarded by `lvl == "01"` in analyze_cobol.  
  _claims: C-280 · evidence: reversa/analysis.py:131_
- ✅ **REQ-14** The reimplementation shall preserve: Branch guarded by `val` in analyze_cobol.  
  _claims: C-281 · evidence: reversa/analysis.py:132_
- ✅ **REQ-15** The reimplementation shall preserve: Branch guarded by `division == "PROCEDURE"` in analyze_cobol.  
  _claims: C-282 · evidence: reversa/analysis.py:138_
- ✅ **REQ-16** The reimplementation shall preserve: Branch guarded by `m and m.group(1).upper() not in _KEYWORDS` in analyze_cobol.  
  _claims: C-283 · evidence: reversa/analysis.py:140_
- ✅ **REQ-17** The reimplementation shall preserve: Branch guarded by `tgt not in _KEYWORDS and tgt not in ("UNTIL", "VARYING", "WITH"` in analyze_cobol.  
  _claims: C-284 · evidence: reversa/analysis.py:148_
- ✅ **REQ-18** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-285 · evidence: reversa/analysis.py:151_
- ✅ **REQ-19** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-286 · evidence: reversa/analysis.py:154_
- ✅ **REQ-20** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-287 · evidence: reversa/analysis.py:157_
- ✅ **REQ-21** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-288 · evidence: reversa/analysis.py:160_
- ✅ **REQ-22** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-289 · evidence: reversa/analysis.py:166_
- ✅ **REQ-23** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-290 · evidence: reversa/analysis.py:169_
- ✅ **REQ-24** The reimplementation shall preserve: Branch guarded by `m` in analyze_cobol.  
  _claims: C-291 · evidence: reversa/analysis.py:173_
- ✅ **REQ-25** The reimplementation shall preserve: Branch guarded by `tok in _OPEN_MODES` in analyze_cobol.  
  _claims: C-292 · evidence: reversa/analysis.py:177_
- ✅ **REQ-26** The reimplementation shall preserve: Branch guarded by `_STOP.search(line` in analyze_cobol.  
  _claims: C-293 · evidence: reversa/analysis.py:182_
- ✅ **REQ-27** The reimplementation shall preserve: Branch guarded by `not s or (s.startswith("#") and not s.startswith("#include")) or s.startswith(("//", "/*", "*")` in analyze_generic.  
  _claims: C-294 · evidence: reversa/analysis.py:207_
- ✅ **REQ-28** The reimplementation shall preserve: Branch guarded by `m` in analyze_generic.  
  _claims: C-295 · evidence: reversa/analysis.py:210_
- ✅ **REQ-29** The reimplementation shall preserve: Branch guarded by `m and m.group(1) not in ("if", "for", "while", "switch", "return"` in analyze_generic.  
  _claims: C-296 · evidence: reversa/analysis.py:214_
- ✅ **REQ-30** The reimplementation shall preserve: Branch guarded by `m` in analyze_generic.  
  _claims: C-297 · evidence: reversa/analysis.py:219_
- ✅ **REQ-31** The reimplementation shall preserve: Branch guarded by `_G_MAIN.search(line` in analyze_generic.  
  _claims: C-298 · evidence: reversa/analysis.py:222_
- ✅ **REQ-32** The reimplementation shall preserve: Branch guarded by `m` in analyze_generic.  
  _claims: C-299 · evidence: reversa/analysis.py:225_
- ✅ **REQ-33** The reimplementation shall preserve: Branch guarded by `m` in analyze_generic.  
  _claims: C-300 · evidence: reversa/analysis.py:228_
- ✅ **REQ-34** The reimplementation shall preserve: Branch guarded by `m` in analyze_generic.  
  _claims: C-301 · evidence: reversa/analysis.py:232_
- ✅ **REQ-35** The reimplementation shall preserve: Branch guarded by `language.startswith("cobol"` in analyze.  
  _claims: C-302 · evidence: reversa/analysis.py:238_
- ✅ **REQ-36** The reimplementation shall preserve: Branch guarded by `"V" in p` in count.  
  _claims: C-303 · evidence: reversa/analysis.py:253_
- ✅ **REQ-37** The reimplementation shall preserve: Branch guarded by `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` in count.  
  _claims: C-304 · evidence: reversa/analysis.py:257_
- ✅ **REQ-38** The reimplementation shall preserve: Branch guarded by `"X" in p` in count.  
  _claims: C-305 · evidence: reversa/analysis.py:259_
- ✅ **REQ-39** The reimplementation shall preserve: Branch guarded by `"Z" in p or "-" in p or "," in p` in count.  
  _claims: C-306 · evidence: reversa/analysis.py:261_
- ✅ **REQ-40** The reimplementation shall preserve: Branch guarded by `_IF_OPEN.match(txt` in aborts_in_branch.  
  _claims: C-307 · evidence: reversa/analysis.py:283_
- ✅ **REQ-41** The reimplementation shall preserve: Branch guarded by `depth == 1 and re.match(r"^\s*ELSE\b", txt, re.I` in aborts_in_branch.  
  _claims: C-308 · evidence: reversa/analysis.py:285_
- ✅ **REQ-42** The reimplementation shall preserve: Branch guarded by `_EXIT.search(txt) and depth >= 1` in aborts_in_branch.  
  _claims: C-309 · evidence: reversa/analysis.py:287_
- ✅ **REQ-43** The reimplementation shall preserve: Branch guarded by `_IF_CLOSE.match(txt` in aborts_in_branch.  
  _claims: C-310 · evidence: reversa/analysis.py:289_
- ✅ **REQ-44** The reimplementation shall preserve: Branch guarded by `depth <= 0` in aborts_in_branch.  
  _claims: C-311 · evidence: reversa/analysis.py:291_
- ✅ **REQ-45** The reimplementation shall preserve: Branch guarded by `depth >= 1 and txt.rstrip().endswith(".") and not _IF_OPEN.match(txt` in aborts_in_branch.  
  _claims: C-312 · evidence: reversa/analysis.py:294_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

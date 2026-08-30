# Requirements — INSTALLER

INSTALLER — purpose reconstructed from 25 claims (25 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `status == "modified" and not force` in _write.  
  _claims: C-330 · evidence: reversa/installer.py:111_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `not (root / STATE_DIR / "config.user.toml").exists(` in w.  
  _claims: C-331 · evidence: reversa/installer.py:149_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `v` in w.  
  _claims: C-332 · evidence: reversa/installer.py:165_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `cfg.exists(` in update.  
  _claims: C-333 · evidence: reversa/installer.py:179_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in update.  
  _claims: C-334 · evidence: reversa/installer.py:181_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `line.startswith("dir = "` in update.  
  _claims: C-335 · evidence: reversa/installer.py:183_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `line.startswith("["` in _section_before.  
  _claims: C-336 · evidence: reversa/installer.py:191_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `line == target` in _section_before.  
  _claims: C-337 · evidence: reversa/installer.py:193_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `fs.status == "intact" or (fs.status == "modified" and purge` in uninstall.  
  _claims: C-338 · evidence: reversa/installer.py:204_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `d.exists() and not any(d.iterdir()` in uninstall.  
  _claims: C-339 · evidence: reversa/installer.py:216_
- ✅ **REQ-11** The reimplementation shall preserve: Branch guarded by `not out["preserved"] and (root / STATE_DIR).exists(` in uninstall.  
  _claims: C-340 · evidence: reversa/installer.py:223_
- ✅ **REQ-12** The reimplementation shall preserve: Branch guarded by `not cfg.exists(` in add_engine.  
  _claims: C-341 · evidence: reversa/installer.py:234_
- ✅ **REQ-13** The reimplementation shall preserve: Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in add_engine.  
  _claims: C-342 · evidence: reversa/installer.py:239_
- ✅ **REQ-14** The reimplementation shall preserve: Branch guarded by `key not in cur` in add_engine.  
  _claims: C-343 · evidence: reversa/installer.py:241_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

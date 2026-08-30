# Requirements — PROCESS

PROCESS — purpose reconstructed from 53 claims (53 confirmed, 0 inferred).

## Behaviours to preserve

- ✅ **REQ-1** The reimplementation shall preserve: Branch guarded by `words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"` in _plain.  
  _claims: C-399 · evidence: reversa/agents/process.py:27_
- ✅ **REQ-2** The reimplementation shall preserve: Branch guarded by `k == "call"` in narrate.  
  _claims: C-400 · evidence: reversa/agents/process.py:54_
- ✅ **REQ-3** The reimplementation shall preserve: Branch guarded by `a.startswith("Call "` in narrate.  
  _claims: C-401 · evidence: reversa/agents/process.py:55_
- ✅ **REQ-4** The reimplementation shall preserve: Branch guarded by `nxt and nxt.get("action", "").startswith(f"{unit} dispatches"` in narrate.  
  _claims: C-402 · evidence: reversa/agents/process.py:59_
- ✅ **REQ-5** The reimplementation shall preserve: Branch guarded by `t.startswith("show"` in narrate.  
  _claims: C-403 · evidence: reversa/agents/process.py:77_
- ✅ **REQ-6** The reimplementation shall preserve: Branch guarded by `a.startswith("Set "` in narrate.  
  _claims: C-404 · evidence: reversa/agents/process.py:93_
- ✅ **REQ-7** The reimplementation shall preserve: Branch guarded by `steps` in narrate.  
  _claims: C-405 · evidence: reversa/agents/process.py:100_
- ✅ **REQ-8** The reimplementation shall preserve: Branch guarded by `rec.detail != "file" or rec.name in seen_rec` in business_context.  
  _claims: C-406 · evidence: reversa/agents/process.py:114_
- ✅ **REQ-9** The reimplementation shall preserve: Branch guarded by `c.extra.get("section") != "working-storage"` in business_context.  
  _claims: C-407 · evidence: reversa/agents/process.py:129_
- ✅ **REQ-10** The reimplementation shall preserve: Branch guarded by `not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", val) or float(val.replace(",", ".")) == 0` in business_context.  
  _claims: C-408 · evidence: reversa/agents/process.py:132_
- ✅ **REQ-11** The reimplementation shall preserve: Branch guarded by `any(c.name in lines[path][j] for j in range(pg.line, end)` in business_context.  
  _claims: C-409 · evidence: reversa/agents/process.py:138_
- ✅ **REQ-12** The reimplementation shall preserve: Branch guarded by `st.get("kind") != "decision"` in business_context.  
  _claims: C-410 · evidence: reversa/agents/process.py:149_
- ✅ **REQ-13** The reimplementation shall preserve: Branch guarded by `key in seen_rules` in business_context.  
  _claims: C-411 · evidence: reversa/agents/process.py:158_
- ✅ **REQ-14** The reimplementation shall preserve: Branch guarded by `any(f.kind == "call" and f.name == "KBDREAD" for ff in facts.values() for f in ff.facts` in business_context.  
  _claims: C-412 · evidence: reversa/agents/process.py:165_
- ✅ **REQ-15** The reimplementation shall preserve: Branch guarded by `not any("LOG" in n or "AUDIT" in n for n in seen_rec` in business_context.  
  _claims: C-413 · evidence: reversa/agents/process.py:176_
- ✅ **REQ-16** The reimplementation shall preserve: Branch guarded by `not any(f.kind == "condition" and re.search(r"DATA|DATE|HORA|TIME", f.name, re.I) for ff in facts.values() for f in ff.facts` in business_context.  
  _claims: C-414 · evidence: reversa/agents/process.py:178_
- ✅ **REQ-17** The reimplementation shall preserve: Branch guarded by `not any(f.kind in ("io",) and f.detail.startswith("OPEN") and "LOCK" in f.name for ff in facts.values() for f in ff.facts` in business_context.  
  _claims: C-415 · evidence: reversa/agents/process.py:180_
- ✅ **REQ-18** The reimplementation shall preserve: Branch guarded by `not processes` in overview_text.  
  _claims: C-416 · evidence: reversa/agents/process.py:187_
- ✅ **REQ-19** The reimplementation shall preserve: Branch guarded by `start is None` in para_facts.  
  _claims: C-417 · evidence: reversa/agents/process.py:266_
- ✅ **REQ-20** The reimplementation shall preserve: Branch guarded by `depth > 6 or (path, para) in seen` in walk.  
  _claims: C-418 · evidence: reversa/agents/process.py:273_
- ✅ **REQ-21** The reimplementation shall preserve: Branch guarded by `f.kind == "accept"` in walk.  
  _claims: C-419 · evidence: reversa/agents/process.py:281_
- ✅ **REQ-22** The reimplementation shall preserve: Branch guarded by `tgt` in walk.  
  _claims: C-420 · evidence: reversa/agents/process.py:308_
- ✅ **REQ-23** The reimplementation shall preserve: Branch guarded by `arg` in walk.  
  _claims: C-421 · evidence: reversa/agents/process.py:312_
- ✅ **REQ-24** The reimplementation shall preserve: Branch guarded by `nxt` in walk.  
  _claims: C-422 · evidence: reversa/agents/process.py:315_
- ✅ **REQ-25** The reimplementation shall preserve: Branch guarded by `entry` in walk.  
  _claims: C-423 · evidence: reversa/agents/process.py:321_
- ✅ **REQ-26** The reimplementation shall preserve: Branch guarded by `not path` in walk.  
  _claims: C-424 · evidence: reversa/agents/process.py:333_
- ✅ **REQ-27** The reimplementation shall preserve: Branch guarded by `first` in walk.  
  _claims: C-425 · evidence: reversa/agents/process.py:339_
- ✅ **REQ-28** The reimplementation shall preserve: Branch guarded by `f.kind == "perform" and not any(d.detail == f.name for d in dispatches` in walk.  
  _claims: C-426 · evidence: reversa/agents/process.py:343_
- ✅ **REQ-29** The reimplementation shall preserve: Branch guarded by `pre_steps` in walk.  
  _claims: C-427 · evidence: reversa/agents/process.py:351_
- ✅ **REQ-30** The reimplementation shall preserve: Branch guarded by `c.name.upper() == "OTHER"` in walk.  
  _claims: C-428 · evidence: reversa/agents/process.py:359_
- ✅ **REQ-31** The reimplementation shall preserve: Branch guarded by `mv` in walk.  
  _claims: C-429 · evidence: reversa/agents/process.py:365_
- ✅ **REQ-32** The reimplementation shall preserve: Branch guarded by `x.kind == "perform"` in walk.  
  _claims: C-430 · evidence: reversa/agents/process.py:369_
- ✅ **REQ-33** The reimplementation shall preserve: Branch guarded by `tgt` in walk.  
  _claims: C-431 · evidence: reversa/agents/process.py:381_
- ✅ **REQ-34** The reimplementation shall preserve: Branch guarded by `nx` in walk.  
  _claims: C-432 · evidence: reversa/agents/process.py:385_
- ✅ **REQ-35** The reimplementation shall preserve: Branch guarded by `entry` in walk.  
  _claims: C-433 · evidence: reversa/agents/process.py:391_
- ✅ **REQ-36** The reimplementation shall preserve: Branch guarded by `first is not None` in walk.  
  _claims: C-434 · evidence: reversa/agents/process.py:401_
- ✅ **REQ-37** The reimplementation shall preserve: Branch guarded by `first + 1 < len(steps) and steps[first + 1]["action"].startswith(f"{label} dispatches"` in walk.  
  _claims: C-435 · evidence: reversa/agents/process.py:404_
- ✅ **REQ-38** The reimplementation shall preserve: Branch guarded by `steps` in walk.  
  _claims: C-436 · evidence: reversa/agents/process.py:415_
- ✅ **REQ-39** The reimplementation shall preserve: Branch guarded by `not processes` in walk.  
  _claims: C-437 · evidence: reversa/agents/process.py:420_
- ✅ **REQ-40** The reimplementation shall preserve: Branch guarded by `e.get("fields"` in refs.  
  _claims: C-438 · evidence: reversa/agents/process.py:466_
- ✅ **REQ-41** The reimplementation shall preserve: Branch guarded by `e.get("evidence"` in refs.  
  _claims: C-439 · evidence: reversa/agents/process.py:470_
- ✅ **REQ-42** The reimplementation shall preserve: Branch guarded by `"start-up" in p.get("name", ""` in refs.  
  _claims: C-440 · evidence: reversa/agents/process.py:475_
- ✅ **REQ-43** The reimplementation shall preserve: Branch guarded by `nic` in refs.  
  _claims: C-441 · evidence: reversa/agents/process.py:491_
- ✅ **REQ-44** The reimplementation shall preserve: Branch guarded by `p.get("description"` in _write.  
  _claims: C-442 · evidence: reversa/agents/process.py:518_
- ✅ **REQ-45** The reimplementation shall preserve: Branch guarded by `dec` in _write.  
  _claims: C-443 · evidence: reversa/agents/process.py:529_
- ✅ **REQ-46** The reimplementation shall preserve: Branch guarded by `len(out_t) > 60` in _write.  
  _claims: C-444 · evidence: reversa/agents/process.py:539_
- ✅ **REQ-47** The reimplementation shall preserve: Branch guarded by `not processes` in _write.  
  _claims: C-445 · evidence: reversa/agents/process.py:545_

## Open gaps affecting this unit

- (none)

Legend: ✅ confirmed · 🟡 inferred (validate before relying on it) · ⛔ gap

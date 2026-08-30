# Domain rules, states and exceptions


## CONTA


### Rules

- ✅ **C-237** Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE. _(confirmed; examples/legacy_atm/CONTA.cbl:64)_
- ✅ **C-239** Branch guarded by `WS-VALOR > LK-SALDO` in SAQUE. _(confirmed; examples/legacy_atm/CONTA.cbl:68)_
- ✅ **C-241** Branch guarded by `FUNCTION MOD(WS-VALOR, 10) NOT = 0` in SAQUE. _(confirmed; examples/legacy_atm/CONTA.cbl:72)_
- ✅ **C-243** Branch guarded by `WS-VALOR = 0` in DEPOSITO. _(confirmed; examples/legacy_atm/CONTA.cbl:82)_
- ✅ **C-245** Branch guarded by `WS-VALOR > LK-SALDO` in TRANSFERENCIA. _(confirmed; examples/legacy_atm/CONTA.cbl:95)_
- ✅ **C-247** Branch guarded by `CLI-STATUS = 'B'` in TRANSFERENCIA. _(confirmed; examples/legacy_atm/CONTA.cbl:105)_

### Behaviors

- ✅ **C-249** CONTA dispatches on `LK-OP` with cases: 'S', 'Q', 'D', 'T'. _(confirmed; examples/legacy_atm/CONTA.cbl:46-53)_

### Exceptions

- 🟡 **C-238** When `WS-VALOR > WS-LIMITE-SAQUE` holds, the operation is rejected with message "LIMITE DE SAQUE EXCEDIDO". _(inferred; examples/legacy_atm/CONTA.cbl:64-65)_
- 🟡 **C-240** When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE". _(inferred; examples/legacy_atm/CONTA.cbl:68-69)_
- 🟡 **C-242** When `FUNCTION MOD(WS-VALOR, 10) NOT = 0` holds, the operation is rejected with message "VALOR DEVE SER MULTIPLO DE 10". _(inferred; examples/legacy_atm/CONTA.cbl:72-73)_
- 🟡 **C-244** When `WS-VALOR = 0` holds, the operation is rejected with message "VALOR INVALIDO". _(inferred; examples/legacy_atm/CONTA.cbl:82-83)_
- 🟡 **C-246** When `WS-VALOR > LK-SALDO` holds, the operation is rejected with message "SALDO INSUFICIENTE". _(inferred; examples/legacy_atm/CONTA.cbl:95-96)_
- 🟡 **C-248** When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA DESTINO BLOQUEADA". _(inferred; examples/legacy_atm/CONTA.cbl:105-106)_
- ✅ **C-250** CONTA can emit the message "CONTA DESTINO INEXISTENTE". _(confirmed; examples/legacy_atm/CONTA.cbl:102)_

### State machines

- **LK-OP**
  - LK-OP -> case 'S'
  - LK-OP -> case 'Q'
  - LK-OP -> case 'D'
  - LK-OP -> case 'T'

## EXTRATO


### Rules

- ✅ **C-251** Branch guarded by `WS-QTD = 0` in MAIN. _(confirmed; examples/legacy_atm/EXTRATO.cbl:34)_
- ✅ **C-253** Branch guarded by `MOV-CONTA = LK-CONTA` in MOSTRA. _(confirmed; examples/legacy_atm/EXTRATO.cbl:40)_

### Exceptions

- 🟡 **C-252** When `WS-QTD = 0` holds, the operation is rejected with message "SEM MOVIMENTOS". _(inferred; examples/legacy_atm/EXTRATO.cbl:34-35)_

## MENU


### Rules

- ✅ **C-254** Branch guarded by `WS-TENTATIVAS >= 3` in MAIN. _(confirmed; examples/legacy_atm/MENU.cbl:31)_
- ✅ **C-256** Branch guarded by `CLI-STATUS = 'B'` in LOGIN. _(confirmed; examples/legacy_atm/MENU.cbl:50)_
- ✅ **C-258** Branch guarded by `WS-SENHA NOT = CLI-SENHA` in LOGIN. _(confirmed; examples/legacy_atm/MENU.cbl:57)_

### Behaviors

- ✅ **C-260** MENU dispatches on `WS-OPCAO` with cases: '1', '2', '3', '4', '5', '9', OTHER. _(confirmed; examples/legacy_atm/MENU.cbl:65-78)_

### Exceptions

- 🟡 **C-255** When `WS-TENTATIVAS >= 3` holds, the operation is rejected with message "CARTAO BLOQUEADO". _(inferred; examples/legacy_atm/MENU.cbl:31-32)_
- 🟡 **C-257** When `CLI-STATUS = 'B'` holds, the operation is rejected with message "CONTA BLOQUEADA". _(inferred; examples/legacy_atm/MENU.cbl:50-51)_
- 🟡 **C-259** When `WS-SENHA NOT = CLI-SENHA` holds, the operation is rejected with message "SENHA INVALIDA". _(inferred; examples/legacy_atm/MENU.cbl:57-59)_
- ✅ **C-261** MENU can emit the message "CONTA INVALIDA". _(confirmed; examples/legacy_atm/MENU.cbl:47)_
- ✅ **C-262** MENU can emit the message "OPCAO INVALIDA". _(confirmed; examples/legacy_atm/MENU.cbl:79)_

### State machines

- **WS-OPCAO**
  - WS-OPCAO -> case '1'
  - WS-OPCAO -> case '2'
  - WS-OPCAO -> case '3'
  - WS-OPCAO -> case '4'
  - WS-OPCAO -> case '5'
  - WS-OPCAO -> case '9'
  - WS-OPCAO -> case OTHER

## UTIL


### Behaviors

- ✅ **C-263** UTIL dispatches on `LK-FUNC` with cases: 'F', 'M', OTHER. _(confirmed; examples/legacy_atm/UTIL.cbl:13-18)_

### Exceptions

- ✅ **C-264** UTIL can emit the message "FUNCAO UTIL INVALIDA". _(confirmed; examples/legacy_atm/UTIL.cbl:19)_

### State machines

- **LK-FUNC**
  - LK-FUNC -> case 'F'
  - LK-FUNC -> case 'M'
  - LK-FUNC -> case OTHER

## KBDREAD


### Rules

- ✅ **C-265** Branch guarded by `c < '0' || c > '9') { i--; continue; }` in KBDREAD. _(confirmed; examples/legacy_atm/kbdread.c:14)_

## __MAIN__


### Rules

- ✅ **C-266** Branch guarded by `__name__ == "__main__"`. _(confirmed; reversa/__main__.py:3)_

### Exceptions

- 🟡 **C-267** When `__name__ == "__main__"` holds, the operation is rejected with message "SystemExit(main())". _(inferred; reversa/__main__.py:3-4)_

## ANALYSIS


### Rules

- ✅ **C-268** Branch guarded by `_is_comment(raw` in analyze_cobol. _(confirmed; reversa/analysis.py:88)_
- ✅ **C-269** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:92)_
- ✅ **C-270** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:97)_
- ✅ **C-271** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:101)_
- ✅ **C-272** Branch guarded by `division == "DATA"` in analyze_cobol. _(confirmed; reversa/analysis.py:103)_
- ✅ **C-273** Branch guarded by `division == "PROCEDURE"` in analyze_cobol. _(confirmed; reversa/analysis.py:106)_
- ✅ **C-274** Branch guarded by `division == "ENVIRONMENT"` in analyze_cobol. _(confirmed; reversa/analysis.py:109)_
- ✅ **C-275** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:111)_
- ✅ **C-276** Branch guarded by `division == "DATA"` in analyze_cobol. _(confirmed; reversa/analysis.py:118)_
- ✅ **C-277** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:120)_
- ✅ **C-278** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:124)_
- ✅ **C-279** Branch guarded by `m and m.group(3` in analyze_cobol. _(confirmed; reversa/analysis.py:129)_
- ✅ **C-280** Branch guarded by `lvl == "01"` in analyze_cobol. _(confirmed; reversa/analysis.py:131)_
- ✅ **C-281** Branch guarded by `val` in analyze_cobol. _(confirmed; reversa/analysis.py:132)_
- ✅ **C-282** Branch guarded by `division == "PROCEDURE"` in analyze_cobol. _(confirmed; reversa/analysis.py:138)_
- ✅ **C-283** Branch guarded by `m and m.group(1).upper() not in _KEYWORDS` in analyze_cobol. _(confirmed; reversa/analysis.py:140)_
- ✅ **C-284** Branch guarded by `tgt not in _KEYWORDS and tgt not in ("UNTIL", "VARYING", "WITH"` in analyze_cobol. _(confirmed; reversa/analysis.py:148)_
- ✅ **C-285** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:151)_
- ✅ **C-286** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:154)_
- ✅ **C-287** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:157)_
- ✅ **C-288** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:160)_
- ✅ **C-289** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:166)_
- ✅ **C-290** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:169)_
- ✅ **C-291** Branch guarded by `m` in analyze_cobol. _(confirmed; reversa/analysis.py:173)_
- ✅ **C-292** Branch guarded by `tok in _OPEN_MODES` in analyze_cobol. _(confirmed; reversa/analysis.py:177)_
- ✅ **C-293** Branch guarded by `_STOP.search(line` in analyze_cobol. _(confirmed; reversa/analysis.py:182)_
- ✅ **C-294** Branch guarded by `not s or (s.startswith("#") and not s.startswith("#include")) or s.startswith(("//", "/*", "*")` in analyze_generic. _(confirmed; reversa/analysis.py:207)_
- ✅ **C-295** Branch guarded by `m` in analyze_generic. _(confirmed; reversa/analysis.py:210)_
- ✅ **C-296** Branch guarded by `m and m.group(1) not in ("if", "for", "while", "switch", "return"` in analyze_generic. _(confirmed; reversa/analysis.py:214)_
- ✅ **C-297** Branch guarded by `m` in analyze_generic. _(confirmed; reversa/analysis.py:219)_
- ✅ **C-298** Branch guarded by `_G_MAIN.search(line` in analyze_generic. _(confirmed; reversa/analysis.py:222)_
- ✅ **C-299** Branch guarded by `m` in analyze_generic. _(confirmed; reversa/analysis.py:225)_
- ✅ **C-300** Branch guarded by `m` in analyze_generic. _(confirmed; reversa/analysis.py:228)_
- ✅ **C-301** Branch guarded by `m` in analyze_generic. _(confirmed; reversa/analysis.py:232)_
- ✅ **C-302** Branch guarded by `language.startswith("cobol"` in analyze. _(confirmed; reversa/analysis.py:238)_
- ✅ **C-303** Branch guarded by `"V" in p` in count. _(confirmed; reversa/analysis.py:253)_
- ✅ **C-304** Branch guarded by `set(p.replace("(", "").replace(")", "")) <= set("9 0123456789"` in count. _(confirmed; reversa/analysis.py:257)_
- ✅ **C-305** Branch guarded by `"X" in p` in count. _(confirmed; reversa/analysis.py:259)_
- ✅ **C-306** Branch guarded by `"Z" in p or "-" in p or "," in p` in count. _(confirmed; reversa/analysis.py:261)_
- ✅ **C-307** Branch guarded by `_IF_OPEN.match(txt` in aborts_in_branch. _(confirmed; reversa/analysis.py:283)_
- ✅ **C-308** Branch guarded by `depth == 1 and re.match(r"^\s*ELSE\b", txt, re.I` in aborts_in_branch. _(confirmed; reversa/analysis.py:285)_
- ✅ **C-309** Branch guarded by `_EXIT.search(txt) and depth >= 1` in aborts_in_branch. _(confirmed; reversa/analysis.py:287)_
- ✅ **C-310** Branch guarded by `_IF_CLOSE.match(txt` in aborts_in_branch. _(confirmed; reversa/analysis.py:289)_
- ✅ **C-311** Branch guarded by `depth <= 0` in aborts_in_branch. _(confirmed; reversa/analysis.py:291)_
- ✅ **C-312** Branch guarded by `depth >= 1 and txt.rstrip().endswith(".") and not _IF_OPEN.match(txt` in aborts_in_branch. _(confirmed; reversa/analysis.py:294)_

## CLI


### Rules

- ✅ **C-313** Branch guarded by `not files` in cmd_status. _(confirmed; reversa/cli.py:54)_
- ✅ **C-314** Branch guarded by `args.verbose or f.status != "intact"` in cmd_status. _(confirmed; reversa/cli.py:60)_
- ✅ **C-315** Branch guarded by `st.exists(` in cmd_status. _(confirmed; reversa/cli.py:64)_
- ✅ **C-316** Branch guarded by `not o.registry.claims` in cmd_migrate. _(confirmed; reversa/cli.py:95)_
- ✅ **C-317** Branch guarded by `q.id == args.id` in cmd_answer. _(confirmed; reversa/cli.py:107)_
- ✅ **C-318** Branch guarded by `g.id == args.id` in cmd_answer. _(confirmed; reversa/cli.py:111)_
- ✅ **C-319** Branch guarded by `not hit` in cmd_answer. _(confirmed; reversa/cli.py:115)_

## CONFIDENCE


### Rules

- ✅ **C-320** Branch guarded by `self.total == 0` in index. _(confirmed; reversa/confidence.py:29)_
- ✅ **C-321** Branch guarded by `not claims` in traceability_density. _(confirmed; reversa/confidence.py:53)_
- ✅ **C-322** Branch guarded by `not p.exists(` in verify_evidence. _(confirmed; reversa/confidence.py:73)_
- ✅ **C-323** Branch guarded by `ev.line_start < 1 or ev.line_start > len(lines` in verify_evidence. _(confirmed; reversa/confidence.py:79)_
- ✅ **C-324** Branch guarded by `not ev.excerpt.strip(` in verify_evidence. _(confirmed; reversa/confidence.py:81)_
- ✅ **C-325** Branch guarded by `_norm(ev.excerpt) in region` in verify_evidence. _(confirmed; reversa/confidence.py:86)_
- ✅ **C-326** Branch guarded by `head and head in region` in verify_evidence. _(confirmed; reversa/confidence.py:90)_

## ENGINES


### Rules

- ✅ **C-327** Branch guarded by `any((root / m).exists() for m in e.markers` in detect_engines. _(confirmed; reversa/engines.py:57)_
- ✅ **C-328** Branch guarded by `keys` in resolve_engines. _(confirmed; reversa/engines.py:64)_
- ✅ **C-329** Branch guarded by `unknown` in resolve_engines. _(confirmed; reversa/engines.py:66)_

## INSTALLER


### Rules

- ✅ **C-330** Branch guarded by `status == "modified" and not force` in _write. _(confirmed; reversa/installer.py:111)_
- ✅ **C-331** Branch guarded by `not (root / STATE_DIR / "config.user.toml").exists(` in w. _(confirmed; reversa/installer.py:149)_
- ✅ **C-332** Branch guarded by `v` in w. _(confirmed; reversa/installer.py:165)_
- ✅ **C-333** Branch guarded by `cfg.exists(` in update. _(confirmed; reversa/installer.py:179)_
- ✅ **C-334** Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in update. _(confirmed; reversa/installer.py:181)_
- ✅ **C-335** Branch guarded by `line.startswith("dir = "` in update. _(confirmed; reversa/installer.py:183)_
- ✅ **C-336** Branch guarded by `line.startswith("["` in _section_before. _(confirmed; reversa/installer.py:191)_
- ✅ **C-337** Branch guarded by `line == target` in _section_before. _(confirmed; reversa/installer.py:193)_
- ✅ **C-338** Branch guarded by `fs.status == "intact" or (fs.status == "modified" and purge` in uninstall. _(confirmed; reversa/installer.py:204)_
- ✅ **C-339** Branch guarded by `d.exists() and not any(d.iterdir()` in uninstall. _(confirmed; reversa/installer.py:216)_
- ✅ **C-340** Branch guarded by `not out["preserved"] and (root / STATE_DIR).exists(` in uninstall. _(confirmed; reversa/installer.py:223)_
- ✅ **C-341** Branch guarded by `not cfg.exists(` in add_engine. _(confirmed; reversa/installer.py:234)_
- ✅ **C-342** Branch guarded by `line.startswith("enabled = ") and "engines" in _section_before(cfg, line` in add_engine. _(confirmed; reversa/installer.py:239)_
- ✅ **C-343** Branch guarded by `key not in cur` in add_engine. _(confirmed; reversa/installer.py:241)_

## MANIFEST


### Rules

- ✅ **C-344** Branch guarded by `self.path.exists(` in load. _(confirmed; reversa/manifest.py:46)_
- ✅ **C-345** Branch guarded by `not p.exists(` in classify. _(confirmed; reversa/manifest.py:72)_
- ✅ **C-346** Branch guarded by `fs.path == rel` in status_of. _(confirmed; reversa/manifest.py:82)_

## MODELS


### Rules

- ✅ **C-347** Branch guarded by `self.line_start == self.line_end` in ref. _(confirmed; reversa/models.py:57)_
- ✅ **C-348** Branch guarded by `m` in next_id. _(confirmed; reversa/models.py:170)_
- ✅ **C-349** Branch guarded by `not isinstance(kw.get("kind"), ClaimKind` in add_claim. _(confirmed; reversa/models.py:175)_
- ✅ **C-350** Branch guarded by `not isinstance(kw.get("confidence"), Confidence` in add_claim. _(confirmed; reversa/models.py:180)_
- ✅ **C-351** Branch guarded by `g.unit == kw.get("unit") and g.description == kw.get("description"` in add_gap. _(confirmed; reversa/models.py:191)_
- ✅ **C-352** Branch guarded by `not isinstance(sev, Severity` in add_gap. _(confirmed; reversa/models.py:194)_
- ✅ **C-353** Branch guarded by `q.unit == kw.get("unit") and q.question == kw.get("question"` in add_question. _(confirmed; reversa/models.py:206)_
- ✅ **C-354** Branch guarded by `c not in q.related_claims` in add_question. _(confirmed; reversa/models.py:208)_
- ✅ **C-355** Branch guarded by `not path.exists(` in load. _(confirmed; reversa/models.py:236)_

## ORCHESTRATOR


### Rules

- ✅ **C-356** Branch guarded by `path.exists(` in load. _(confirmed; reversa/orchestrator.py:38)_
- ✅ **C-357** Branch guarded by `only` in run. _(confirmed; reversa/orchestrator.py:66)_
- ✅ **C-358** Branch guarded by `not resume and team in ("discovery", "all") and not only` in run. _(confirmed; reversa/orchestrator.py:68)_
- ✅ **C-359** Branch guarded by `not self.state.started` in run. _(confirmed; reversa/orchestrator.py:71)_
- ✅ **C-360** Branch guarded by `resume and not only and st.get("status") == "done"` in run. _(confirmed; reversa/orchestrator.py:79)_

## PROJECT


### Rules

- ✅ **C-361** Branch guarded by `lang is None` in inventory. _(confirmed; reversa/project.py:56)_
- ✅ **C-362** Branch guarded by `size > MAX_FILE_BYTES` in inventory. _(confirmed; reversa/project.py:62)_
- ✅ **C-363** Branch guarded by `rel not in self._cache` in lines. _(confirmed; reversa/project.py:69)_
- ✅ **C-364** Branch guarded by `max_lines` in numbered. _(confirmed; reversa/project.py:83)_

## ARCHAEOLOGIST


### Rules

- ✅ **C-365** Branch guarded by `paras` in heuristic. _(confirmed; reversa/agents/archaeologist.py:39)_
- ✅ **C-366** Branch guarded by `lk` in heuristic. _(confirmed; reversa/agents/archaeologist.py:56)_
- ✅ **C-367** Branch guarded by `ws` in heuristic. _(confirmed; reversa/agents/archaeologist.py:62)_
- ✅ **C-368** Branch guarded by `acc` in heuristic. _(confirmed; reversa/agents/archaeologist.py:77)_
- ✅ **C-369** Branch guarded by `not any(x.name == p.name for x in paras` in heuristic. _(confirmed; reversa/agents/archaeologist.py:83)_
- ✅ **C-370** Branch guarded by `not paras and not ff.of("select") and not ws` in heuristic. _(confirmed; reversa/agents/archaeologist.py:87)_
- ✅ **C-371** Branch guarded by `out.get("summary") and not u.description` in run. _(confirmed; reversa/agents/archaeologist.py:108)_

## ARCHITECT


### Rules

- ✅ **C-372** Branch guarded by `entry` in heuristic. _(confirmed; reversa/agents/architect.py:42)_
- ✅ **C-373** Branch guarded by `shared` in heuristic. _(confirmed; reversa/agents/architect.py:45)_
- ✅ **C-374** Branch guarded by `rest` in heuristic. _(confirmed; reversa/agents/architect.py:48)_
- ✅ **C-375** Branch guarded by `n >= 2` in heuristic. _(confirmed; reversa/agents/architect.py:54)_
- ✅ **C-376** Branch guarded by `len(users) >= 2` in heuristic. _(confirmed; reversa/agents/architect.py:59)_
- ✅ **C-377** Branch guarded by `not entry` in heuristic. _(confirmed; reversa/agents/architect.py:68)_
- ✅ **C-378** Branch guarded by `c.kind == ClaimKind.DEPENDENCY` in run. _(confirmed; reversa/agents/architect.py:79)_
- ✅ **C-379** Branch guarded by `m` in run. _(confirmed; reversa/agents/architect.py:81)_
- ✅ **C-380** Branch guarded by `c.kind == ClaimKind.DATA` in run. _(confirmed; reversa/agents/architect.py:83)_
- ✅ **C-381** Branch guarded by `m` in run. _(confirmed; reversa/agents/architect.py:85)_
- ✅ **C-382** Branch guarded by `a != b` in _write. _(confirmed; reversa/agents/architect.py:151)_

## BASE


### Rules

- ✅ **C-383** Branch guarded by `self.units_filter` in selected_units. _(confirmed; reversa/agents/base.py:58)_
- ✅ **C-384** Branch guarded by `not stmt` in add_claims. _(confirmed; reversa/agents/base.py:102)_
- ✅ **C-385** Branch guarded by `conf == Confidence.CONFIRMED and not ev` in add_claims. _(confirmed; reversa/agents/base.py:114)_
- ✅ **C-470** Branch guarded by `TYPE_CHECKING:  # pragma: no cover`. _(confirmed; reversa/llm/base.py:8)_
- ✅ **C-471** Branch guarded by `start == -1 or end == -1` in strip_json. _(confirmed; reversa/llm/base.py:26)_
- ✅ **C-473** Branch guarded by `name == "heuristic"` in get_backend. _(confirmed; reversa/llm/base.py:32)_
- ✅ **C-474** Branch guarded by `name == "anthropic"` in get_backend. _(confirmed; reversa/llm/base.py:35)_
- ✅ **C-475** Branch guarded by `name == "auto"` in get_backend. _(confirmed; reversa/llm/base.py:38)_
- ✅ **C-476** Branch guarded by `os.environ.get("ANTHROPIC_API_KEY"` in get_backend. _(confirmed; reversa/llm/base.py:40)_

### Exceptions

- 🟡 **C-472** When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply". _(inferred; reversa/llm/base.py:26-27)_
- ✅ **C-477** BASE can emit the message "unknown backend: {name}". _(confirmed; reversa/llm/base.py:45)_

## DETECTIVE


### Rules

- ✅ **C-386** Branch guarded by `near and _CMP.search(text` in heuristic. _(confirmed; reversa/agents/detective.py:59)_
- ✅ **C-387** Branch guarded by `n in ("0", "1") or n in seen_consts` in heuristic. _(confirmed; reversa/agents/detective.py:66)_
- ✅ **C-388** Branch guarded by `cases` in heuristic. _(confirmed; reversa/agents/detective.py:81)_
- ✅ **C-389** Branch guarded by `not any(0 < m.line - c.line <= 4 for c in ff.of("condition")` in heuristic. _(confirmed; reversa/agents/detective.py:84)_
- ✅ **C-390** Branch guarded by `re.search(r"(senha|pin|pass|auth|login|usuario|user)", a.name, re.I` in heuristic. _(confirmed; reversa/agents/detective.py:90)_
- ✅ **C-391** Branch guarded by `not ff.of("condition") and not ff.of("dispatch"` in heuristic. _(confirmed; reversa/agents/detective.py:98)_
- ✅ **C-392** Branch guarded by `isinstance(idx, int) and 0 <= idx < len(made` in run. _(confirmed; reversa/agents/detective.py:124)_
- ✅ **C-393** Branch guarded by `not cs` in _write. _(confirmed; reversa/agents/detective.py:137)_
- ✅ **C-394** Branch guarded by `not sub` in _write. _(confirmed; reversa/agents/detective.py:142)_
- ✅ **C-395** Branch guarded by `st` in _write. _(confirmed; reversa/agents/detective.py:150)_

## MIGRATION


### Rules

- ✅ **C-396** Branch guarded by `c["kind"] not in {k.value for k in _SCEN_KINDS} or c["confidence"] == "gap"` in heuristic. _(confirmed; reversa/agents/migration.py:54)_
- ✅ **C-397** Branch guarded by `c["kind"] == "exception"` in heuristic. _(confirmed; reversa/agents/migration.py:58)_
- ✅ **C-398** Branch guarded by `n_inf` in heuristic. _(confirmed; reversa/agents/migration.py:83)_

## PROCESS


### Rules

- ✅ **C-399** Branch guarded by `words.upper() == name or len(words) < 4 or words in ("reg", "rec", "fs", "eof", "qtd", "fim"` in _plain. _(confirmed; reversa/agents/process.py:27)_
- ✅ **C-400** Branch guarded by `k == "call"` in narrate. _(confirmed; reversa/agents/process.py:54)_
- ✅ **C-401** Branch guarded by `a.startswith("Call "` in narrate. _(confirmed; reversa/agents/process.py:55)_
- ✅ **C-402** Branch guarded by `nxt and nxt.get("action", "").startswith(f"{unit} dispatches"` in narrate. _(confirmed; reversa/agents/process.py:59)_
- ✅ **C-403** Branch guarded by `t.startswith("show"` in narrate. _(confirmed; reversa/agents/process.py:77)_
- ✅ **C-404** Branch guarded by `a.startswith("Set "` in narrate. _(confirmed; reversa/agents/process.py:93)_
- ✅ **C-405** Branch guarded by `steps` in narrate. _(confirmed; reversa/agents/process.py:100)_
- ✅ **C-406** Branch guarded by `rec.detail != "file" or rec.name in seen_rec` in business_context. _(confirmed; reversa/agents/process.py:114)_
- ✅ **C-407** Branch guarded by `c.extra.get("section") != "working-storage"` in business_context. _(confirmed; reversa/agents/process.py:129)_
- ✅ **C-408** Branch guarded by `not re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?", val) or float(val.replace(",", ".")) == 0` in business_context. _(confirmed; reversa/agents/process.py:132)_
- ✅ **C-409** Branch guarded by `any(c.name in lines[path][j] for j in range(pg.line, end)` in business_context. _(confirmed; reversa/agents/process.py:138)_
- ✅ **C-410** Branch guarded by `st.get("kind") != "decision"` in business_context. _(confirmed; reversa/agents/process.py:149)_
- ✅ **C-411** Branch guarded by `key in seen_rules` in business_context. _(confirmed; reversa/agents/process.py:158)_
- ✅ **C-412** Branch guarded by `any(f.kind == "call" and f.name == "KBDREAD" for ff in facts.values() for f in ff.facts` in business_context. _(confirmed; reversa/agents/process.py:165)_
- ✅ **C-413** Branch guarded by `not any("LOG" in n or "AUDIT" in n for n in seen_rec` in business_context. _(confirmed; reversa/agents/process.py:176)_
- ✅ **C-414** Branch guarded by `not any(f.kind == "condition" and re.search(r"DATA|DATE|HORA|TIME", f.name, re.I) for ff in facts.values() for f in ff.facts` in business_context. _(confirmed; reversa/agents/process.py:178)_
- ✅ **C-415** Branch guarded by `not any(f.kind in ("io",) and f.detail.startswith("OPEN") and "LOCK" in f.name for ff in facts.values() for f in ff.facts` in business_context. _(confirmed; reversa/agents/process.py:180)_
- ✅ **C-416** Branch guarded by `not processes` in overview_text. _(confirmed; reversa/agents/process.py:187)_
- ✅ **C-417** Branch guarded by `start is None` in para_facts. _(confirmed; reversa/agents/process.py:266)_
- ✅ **C-418** Branch guarded by `depth > 6 or (path, para) in seen` in walk. _(confirmed; reversa/agents/process.py:273)_
- ✅ **C-419** Branch guarded by `f.kind == "accept"` in walk. _(confirmed; reversa/agents/process.py:281)_
- ✅ **C-420** Branch guarded by `tgt` in walk. _(confirmed; reversa/agents/process.py:308)_
- ✅ **C-421** Branch guarded by `arg` in walk. _(confirmed; reversa/agents/process.py:312)_
- ✅ **C-422** Branch guarded by `nxt` in walk. _(confirmed; reversa/agents/process.py:315)_
- ✅ **C-423** Branch guarded by `entry` in walk. _(confirmed; reversa/agents/process.py:321)_
- ✅ **C-424** Branch guarded by `not path` in walk. _(confirmed; reversa/agents/process.py:333)_
- ✅ **C-425** Branch guarded by `first` in walk. _(confirmed; reversa/agents/process.py:339)_
- ✅ **C-426** Branch guarded by `f.kind == "perform" and not any(d.detail == f.name for d in dispatches` in walk. _(confirmed; reversa/agents/process.py:343)_
- ✅ **C-427** Branch guarded by `pre_steps` in walk. _(confirmed; reversa/agents/process.py:351)_
- ✅ **C-428** Branch guarded by `c.name.upper() == "OTHER"` in walk. _(confirmed; reversa/agents/process.py:359)_
- ✅ **C-429** Branch guarded by `mv` in walk. _(confirmed; reversa/agents/process.py:365)_
- ✅ **C-430** Branch guarded by `x.kind == "perform"` in walk. _(confirmed; reversa/agents/process.py:369)_
- ✅ **C-431** Branch guarded by `tgt` in walk. _(confirmed; reversa/agents/process.py:381)_
- ✅ **C-432** Branch guarded by `nx` in walk. _(confirmed; reversa/agents/process.py:385)_
- ✅ **C-433** Branch guarded by `entry` in walk. _(confirmed; reversa/agents/process.py:391)_
- ✅ **C-434** Branch guarded by `first is not None` in walk. _(confirmed; reversa/agents/process.py:401)_
- ✅ **C-435** Branch guarded by `first + 1 < len(steps) and steps[first + 1]["action"].startswith(f"{label} dispatches"` in walk. _(confirmed; reversa/agents/process.py:404)_
- ✅ **C-436** Branch guarded by `steps` in walk. _(confirmed; reversa/agents/process.py:415)_
- ✅ **C-437** Branch guarded by `not processes` in walk. _(confirmed; reversa/agents/process.py:420)_
- ✅ **C-438** Branch guarded by `e.get("fields"` in refs. _(confirmed; reversa/agents/process.py:466)_
- ✅ **C-439** Branch guarded by `e.get("evidence"` in refs. _(confirmed; reversa/agents/process.py:470)_
- ✅ **C-440** Branch guarded by `"start-up" in p.get("name", ""` in refs. _(confirmed; reversa/agents/process.py:475)_
- ✅ **C-441** Branch guarded by `nic` in refs. _(confirmed; reversa/agents/process.py:491)_
- ✅ **C-442** Branch guarded by `p.get("description"` in _write. _(confirmed; reversa/agents/process.py:518)_
- ✅ **C-443** Branch guarded by `dec` in _write. _(confirmed; reversa/agents/process.py:529)_
- ✅ **C-444** Branch guarded by `len(out_t) > 60` in _write. _(confirmed; reversa/agents/process.py:539)_
- ✅ **C-445** Branch guarded by `not processes` in _write. _(confirmed; reversa/agents/process.py:545)_

## REVIEWER


### Rules

- ✅ **C-446** Branch guarded by `c["id"] in answered` in heuristic. _(confirmed; reversa/agents/reviewer.py:52)_
- ✅ **C-447** Branch guarded by `c.confidence == Confidence.GAP` in run. _(confirmed; reversa/agents/reviewer.py:64)_
- ✅ **C-448** Branch guarded by `not c.evidence` in run. _(confirmed; reversa/agents/reviewer.py:66)_
- ✅ **C-449** Branch guarded by `c.confidence == Confidence.CONFIRMED` in run. _(confirmed; reversa/agents/reviewer.py:67)_
- ✅ **C-450** Branch guarded by `not any(ok for ok, _ in results` in run. _(confirmed; reversa/agents/reviewer.py:73)_
- ✅ **C-451** Branch guarded by `c.confidence == Confidence.CONFIRMED` in run. _(confirmed; reversa/agents/reviewer.py:74)_
- ✅ **C-452** Branch guarded by `not c` in run. _(confirmed; reversa/agents/reviewer.py:97)_
- ✅ **C-453** Branch guarded by `new == Confidence.CONFIRMED and not (c.evidence and any(` in run. _(confirmed; reversa/agents/reviewer.py:103)_
- ✅ **C-454** Branch guarded by `new != c.confidence` in run. _(confirmed; reversa/agents/reviewer.py:106)_
- ✅ **C-455** Branch guarded by `new == Confidence.GAP` in run. _(confirmed; reversa/agents/reviewer.py:109)_

## SCOUT


### Rules

- ✅ **C-456** Branch guarded by `f["path"] not in facts_by` in heuristic. _(confirmed; reversa/agents/scout.py:45)_
- ✅ **C-457** Branch guarded by `prog` in heuristic. _(confirmed; reversa/agents/scout.py:57)_
- ✅ **C-458** Branch guarded by `f["path"] not in facts_by` in heuristic. _(confirmed; reversa/agents/scout.py:65)_
- ✅ **C-459** Branch guarded by `tgt in seen` in heuristic. _(confirmed; reversa/agents/scout.py:72)_
- ✅ **C-460** Branch guarded by `c.kind == "call" and tgt not in known_units` in heuristic. _(confirmed; reversa/agents/scout.py:77)_
- ✅ **C-461** Branch guarded by `not files` in run. _(confirmed; reversa/agents/scout.py:108)_
- ✅ **C-462** Branch guarded by `ev` in _unit_for. _(confirmed; reversa/agents/scout.py:128)_
- ✅ **C-463** Branch guarded by `f in u.files` in _unit_for. _(confirmed; reversa/agents/scout.py:131)_

## WRITER


### Rules

- ✅ **C-464** Branch guarded by `c["kind"] in {k.value for k in _REQ_KINDS}` in heuristic. _(confirmed; reversa/agents/writer.py:51)_
- ✅ **C-465** Branch guarded by `not cids` in run. _(confirmed; reversa/agents/writer.py:102)_

## ANTHROPIC_BACKEND


### Rules

- ✅ **C-466** Branch guarded by `not self.api_key` in __init__. _(confirmed; reversa/llm/anthropic_backend.py:33)_
- ✅ **C-467** Branch guarded by `b.get("type") == "text"` in _call. _(confirmed; reversa/llm/anthropic_backend.py:54)_
- ✅ **C-468** Branch guarded by `e.code in (429, 500, 502, 503, 529` in _call. _(confirmed; reversa/llm/anthropic_backend.py:57)_

### Exceptions

- ✅ **C-469** ANTHROPIC_BACKEND can emit the message "Anthropic API failed after retries: {last}". _(confirmed; reversa/llm/anthropic_backend.py:64)_

## BASE


### Rules

- ✅ **C-383** Branch guarded by `self.units_filter` in selected_units. _(confirmed; reversa/agents/base.py:58)_
- ✅ **C-384** Branch guarded by `not stmt` in add_claims. _(confirmed; reversa/agents/base.py:102)_
- ✅ **C-385** Branch guarded by `conf == Confidence.CONFIRMED and not ev` in add_claims. _(confirmed; reversa/agents/base.py:114)_
- ✅ **C-470** Branch guarded by `TYPE_CHECKING:  # pragma: no cover`. _(confirmed; reversa/llm/base.py:8)_
- ✅ **C-471** Branch guarded by `start == -1 or end == -1` in strip_json. _(confirmed; reversa/llm/base.py:26)_
- ✅ **C-473** Branch guarded by `name == "heuristic"` in get_backend. _(confirmed; reversa/llm/base.py:32)_
- ✅ **C-474** Branch guarded by `name == "anthropic"` in get_backend. _(confirmed; reversa/llm/base.py:35)_
- ✅ **C-475** Branch guarded by `name == "auto"` in get_backend. _(confirmed; reversa/llm/base.py:38)_
- ✅ **C-476** Branch guarded by `os.environ.get("ANTHROPIC_API_KEY"` in get_backend. _(confirmed; reversa/llm/base.py:40)_

### Exceptions

- 🟡 **C-472** When `start == -1 or end == -1` holds, the operation is rejected with message "no JSON object in reply". _(inferred; reversa/llm/base.py:26-27)_
- ✅ **C-477** BASE can emit the message "unknown backend: {name}". _(confirmed; reversa/llm/base.py:45)_

## TEST_PIPELINE


### Rules

- ✅ **C-478** Branch guarded by `c.confidence == Confidence.CONFIRMED` in test_discovery_and_migration_offline. _(confirmed; tests/test_pipeline.py:34)_

Legend: ✅ confirmed · 🟡 inferred · ⛔ gap

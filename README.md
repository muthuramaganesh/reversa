# Reversa (Python implementation)

Reverse documentation engineering: convert a legacy codebase into **traceable operational
specifications for AI coding agents**, with every claim marked *confirmed*, *inferred* or *gap*.

An implementation of the framework in Macedo & Costa, *Reversa: A Reverse Documentation
Engineering Framework for Converting Legacy Software into Operational Specifications for AI
Agents*, arXiv:2605.18684 (May 2026). The authors' reference tool is a Node.js CLI; this is an
independent Python implementation of the same architecture, written from the paper.

```
pip install -e .
cd /path/to/legacy-project
reversa install                      # writes .reversa/, CLAUDE.md / AGENTS.md, agent skills
reversa run --target go              # discovery team + migration team
open _reversa_sdd/README.md
```

No API key? Add `--backend heuristic` to run fully offline with static analysis.

## What it does

```
legacy code ──► Scout ──► Archaeologist ──► Detective ──► Architect ──► Process ──► Writer ──► Reviewer ──► _reversa_sdd/
                                                                                     │
                                                              Migration team ◄───────┘
                                                              (strategy, risks, Gherkin parity)
```

Each agent has one job and explicit inputs/outputs, so a wrong claim can be traced to the stage
that introduced it. Each produces **claims**; each claim carries a confidence level and evidence
references (`file:line-line` + excerpt). The Reviewer re-opens the source, verifies every
excerpt, and downgrades anything that does not hold. Gaps and questions are first-class outputs.

| Role (paper Table 2) | Class | Produces |
|---|---|---|
| `reversa` orchestrator | `orchestrator.Orchestrator` | `.reversa/state.json`, `registry.json`, `plan.md`; resumption |
| `reversa-scout` | `agents.Scout` | `inventory.md`; units, entry points, dependency claims |
| `reversa-archaeologist` | `agents.Archaeologist` | `analysis/<unit>.md`; structure and data claims |
| `reversa-detective` | `agents.Detective` | `rules.md`; rules, states, permissions, exceptions, questions |
| `reversa-architect` | `agents.Architect` | `architecture.md` (Mermaid), `dependencies.md`, `traceability/spec-impact-matrix.md` |
| `reversa-process` (addition) | `agents.ProcessAgent` | `business-context.md`: plain-English orientation (what it is, who uses it, what it manages, rules, hard-coded parameters, what's missing); `processes.md`: end-to-end operational processes with narrative + traced steps + flowchart |
| `reversa-writer` | `agents.Writer` | `specs/<unit>/{requirements,design,tasks}.md`, `traceability/code-spec-matrix.md` |
| `reversa-reviewer` | `agents.Reviewer` | `confidence-report.md`, `gaps.md`, `questions.md`; reclassified claims |
| Migration | `agents.Migration` | `migration/strategy.md`, `risk-register.md`, `parity/<unit>.feature` |

## The confidence model (paper §3.5)

- **confirmed** — direct evidence in code. Must cite lines. A confirmed claim without evidence is
  downgraded automatically; a confirmed claim whose excerpt cannot be found in the file is
  downgraded by the Reviewer.
- **inferred** — supported by names, patterns or structure. Written as a hypothesis. Becomes an
  `@needs-validation` parity scenario and a question for the owner.
- **gap** — could not be determined. Never guessed; recorded in `gaps.md` with severity
  (critical / moderate / cosmetic / out of scope) and a blocking flag.

Internal confidence index = (confirmed × 1.0 + inferred × 0.5) / total (paper §5.3). It is a
classification summary, **not** factual accuracy — the report says so on every run.

In the sample below the heuristic detective produces, for one `IF`:

```
✅ C-039 Branch guarded by `WS-VALOR > WS-LIMITE-SAQUE` in SAQUE.              (confirmed; CONTA.cbl:64)
🟡 C-040 When that holds, the operation is rejected with "LIMITE DE SAQUE EXCEDIDO". (inferred; CONTA.cbl:64-65)
Q-002    Is the constant a business limit, a technical constant, or configurable?
```

The literal fact is confirmed; the interpretation is inferred; the unknown becomes a question.

## Reading the business process

Two files are written for non-programmers. `business-context.md` answers "what is this system?":
the records it keeps (each field with its type in plain words), who uses it, what operations exist,
every rule it enforces in one sentence each with the line that proves it, every number hard-coded
in the program (limits, fees, page sizes) with where it is used, and a short list of things a
business reader would expect that the code does not contain (e.g. no daily limit, no locking).

`processes.md` is the artifact to start from if the question is "what does this system actually
do for a user?". It opens with a plain-English overview and a summary table, then gives each
process a narrative description followed by the exact steps. For the sample ATM, option 2 reads:

> This process starts when user selects '2' at the MENU menu. MENU hands over to CONTA with
> operation code 'Q', which runs its SAQUE routine. The system prompts "VALOR DO SAQUE:" and reads
> valor (WS-VALOR). If valor is greater than limite saque (WS-LIMITE-SAQUE), the system shows the
> message "LIMITE DE SAQUE EXCEDIDO" and the operation stops. … It updates the existing CLI-REG
> record. It writes a new MOV-REG record.

and the step table underneath is:

```
1 MENU   → Call CONTA with operation 'Q'                                   MENU.cbl:69
2 CONTA  → CONTA dispatches 'Q' to SAQUE                                   CONTA.cbl:49-50
3 CONTA  ⌨️ Take input WS-VALOR (prompt "VALOR DO SAQUE:")                 CONTA.cbl:63
4 CONTA  ❓ WS-VALOR > WS-LIMITE-SAQUE  → show "LIMITE DE SAQUE EXCEDIDO", abort   CONTA.cbl:64-65
5 CONTA  ❓ WS-VALOR > LK-SALDO         → show "SALDO INSUFICIENTE", abort         CONTA.cbl:68-69
6 CONTA  ❓ MOD(WS-VALOR,10) NOT = 0    → show "VALOR DEVE SER MULTIPLO DE 10", abort
7 CONTA  → Perform GRAVA
8 CONTA  💾 REWRITE CLI-REG                                                CONTA.cbl:117
9 CONTA  💾 WRITE MOV-REG                                                  CONTA.cbl:121
```

The *steps* are confirmed (each is a line of code). The *process name* is inferred from the
dispatch label. The process agent is an addition to the paper's role set; its output is what the
paper's "domain model, state machines, flows" bullet in §5.2 refers to, made explicit.

## Backends

| `--backend` | How claims are produced |
|---|---|
| `anthropic` | Each agent sends its system prompt, the numbered source, and a JSON schema to the Claude Messages API (`ANTHROPIC_API_KEY`, model via `REVERSA_MODEL` or `--model`). Malformed replies fall back to the heuristic and are logged as a gap. |
| `heuristic` | Deterministic static analysis (`reversa/analysis.py`): COBOL divisions, paragraphs, SELECT/FD, IF/EVALUATE, DISPLAY messages, CALL/PERFORM; generic def/import/if/raise for other languages. No network. |
| `auto` (default) | `anthropic` if the key is set, else `heuristic`. |

The mechanical part of the Reviewer (evidence verification) runs identically under both backends.
Agents are the contract; backends only fulfil it — see `agents/base.py`.

## Installation layer (paper §3.3)

`reversa install` detects engines (Claude Code, Codex, Cursor, Gemini CLI, Windsurf, Kiro,
Opencode, Cline, Roo, Copilot, Aider, Amazon Q, Antigravity) and writes, per engine, an entry
file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, …) and one `SKILL.md` per agent, so a coding agent
can run the pipeline itself by following the skills in order. Every managed file is hashed into
`.reversa/_config/files-manifest.json`:

```
reversa status            # intact / modified / missing per file
reversa update            # rewrites intact + missing, PRESERVES modified
reversa uninstall         # deletes intact only; --purge to remove modified too
reversa add-engine gemini
```

## Human feedback loop (paper §3.6)

```
reversa answer Q-001 "It is a business rule: notes are dispensed in multiples of 10."
reversa answer GAP-002 "Out of scope for parity" --status out_of_scope
reversa run --resume --only reviewer
```

Answers are stored in the registry, shown in `questions.md`, and passed to the Reviewer, which
may confirm an inferred claim on the strength of an answer — but only if the claim's code
evidence also verifies. An answer alone never manufactures a confirmed claim.

## Layout

```
reversa/
  models.py        Claim / Evidence / Gap / Question / Unit, Registry (JSON persistence)
  confidence.py    distribution, index, evidence verification
  analysis.py      static analysis (COBOL + generic) with line numbers
  project.py       inventory, file access, language detection
  manifest.py      SHA-256 manifest, intact/modified/missing
  engines.py       engine table + detection
  installer.py     install / update / uninstall / add-engine
  orchestrator.py  state, plan, resumption
  cli.py           command line
  llm/             Backend protocol, AnthropicBackend, HeuristicBackend
  agents/          Scout, Archaeologist, Detective, Architect, ProcessAgent, Writer, Reviewer, Migration
examples/legacy_atm/   COBOL ATM (MENU, CONTA, EXTRATO, UTIL) + C keyboard helper
tests/                 19 tests, all offline
```

## Evaluation hooks (paper §4, Table 3)

`confidence-report.md` exposes confidence distribution, blocking gaps and traceability density.
`reversa report` prints the same as JSON for scripting (coverage per unit, answered questions).
Expert precision and agent utility are deliberately not computed: they need independent review and
controlled downstream tasks, which the paper lists as future work.

## Limitations

- The heuristic backend is a floor, not a substitute for a model: it restates code literally and
  interprets little. Its value is reproducibility and a safe fallback.
- Language support beyond COBOL is generic. Rules hidden in databases, configuration or runtime
  behaviour are not visible to either backend (paper §6).
- The confidence index is self-reported by the pipeline. Treat it as a review-prioritisation aid.

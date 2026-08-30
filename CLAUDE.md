# Reversa — reverse documentation engineering

This project has Reversa installed. Reversa converts this legacy codebase into
traceable operational specifications under `_reversa_sdd/`.

## How to run the pipeline as an agent

Work through the Discovery team **in order**, one skill at a time, writing the
artifacts each skill describes. Never skip the reviewer.

1. **reversa-scout** — Map the surface of a legacy project: languages and stack, how files group into units (programs, modules, services, screens), entry points, and which units call which.
2. **reversa-archaeologist** — Analyse one unit in depth: its internal structure (sections, paragraphs, functions), data structures and record layouts, files/tables it reads or writes, inputs and outputs, and control flow between its parts.
3. **reversa-detective** — Recover the *business* knowledge hidden in one unit: rules (validations, limits, calculations), states and transitions, permissions, and the operational exceptions the code handles.
4. **reversa-architect** — Synthesise the architecture of the whole system from the unit-level claims: components and layers, the dependency graph, shared data stores, main flows, and an impact matrix (which units are affected if a unit or a data store changes).
5. **reversa-process** — Reconstruct the end-to-end operational processes a user or operator experiences: start from each entry point and follow the control flow across units, recording at each step the actor, the inputs taken, the decisions made (with their outcomes), the messages shown, and the data written.
6. **reversa-writer** — Write the operational specification of one unit for a coding agent: requirements (behaviours to preserve), design (structure, data, dependencies) and reimplementation tasks.
7. **reversa-reviewer** — Challenge the claims produced by the other agents.
8. **reversa-migration** — Plan the migration of a legacy system from its operational specification: choose a strategy, design the target architecture, map risks from gaps, and write Gherkin parity scenarios that both the legacy and the target must pass.

## Confidence rules (apply to every statement you write)

- **confirmed**: cite file and line range; the code says exactly this.
- **inferred**: a hypothesis from names, patterns or structure. Say so.
- **gap**: unknown. Record it in `_reversa_sdd/gaps.md` and ask in `questions.md`.

Never present an inference as a fact. Never fabricate evidence.

State: `.reversa/state.json`, `.reversa/registry.json`, `.reversa/plan.md`.
CLI equivalent: `reversa run` (discovery), `reversa migrate --target <lang>`.

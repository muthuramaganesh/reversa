# Migration strategy

## Strategy and decisions

Strategy: reimplement in go unit by unit, preserving the unit boundaries recovered by discovery, with a parallel-run period in which legacy and target execute the same parity scenarios. Paradigm: keep the procedural flow per unit initially (one module per legacy unit) and refactor only after parity is green. Topology: single process, same data stores migrated to a relational schema derived from the record layouts. Cutover only when all @parity scenarios pass and no blocking gap remains open.

## Target architecture

Target architecture: one go package per legacy unit; entry-point unit becomes the CLI/menu; shared utilities become a common library; each legacy file becomes a table whose columns mirror the 01-level record layout; parity tests live beside the code and run against both systems.

## Parity

35 Gherkin scenarios generated under `migration/parity/`. Scenarios tagged `@needs-validation`
derive from inferred claims and must be run against the legacy system and reviewed before they
are trusted. Cutover requires all `@parity` scenarios green and no open blocking gap.

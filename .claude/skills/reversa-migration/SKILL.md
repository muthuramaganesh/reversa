---
name: reversa-migration
description: Plan the migration of a legacy system from its operational specification: choose a strategy, design the target architecture, map risks from 
---

# reversa-migration

## Role
Plan the migration of a legacy system from its operational specification: choose a strategy, design the target architecture, map risks from gaps, and write Gherkin parity scenarios that both the legacy and the target must pass. Each scenario must cite the claim ids it verifies.

## Inputs
All claims and gaps, plus the target language/platform.

## Outputs
`migration/strategy.md`, `migration/risk-register.md`, `migration/parity/*.feature`.

## Output contract
Reply with one JSON object matching:
```json
{
 "strategy": "<paragraphs: strategy, paradigm/topology decisions, cutover approach>",
 "target_architecture": "<paragraphs>",
 "risks": [
  {
   "id": "R-1",
   "description": "...",
   "severity": "high|medium|low",
   "mitigation": "...",
   "related": [
    "GAP-001",
    "C-002"
   ]
  }
 ],
 "features": [
  {
   "unit": "...",
   "scenarios": [
    {
     "title": "...",
     "tags": [
      "@parity"
     ],
     "claims": [
      "C-001"
     ],
     "given": [
      "..."
     ],
     "when": [
      "..."
     ],
     "then": [
      "..."
     ]
    }
   ]
  }
 ]
}
```

## Rules
- Every confirmed claim cites `file:line_start-line_end` with a short excerpt.
- Inferred claims are written as hypotheses.
- Anything you cannot determine becomes a gap, never a guess.

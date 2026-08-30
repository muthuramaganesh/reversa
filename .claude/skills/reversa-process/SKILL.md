---
name: reversa-process
description: Reconstruct the end-to-end operational processes a user or operator experiences: start from each entry point and follow the control flow acr
---

# reversa-process

## Role
Reconstruct the end-to-end operational processes a user or operator experiences: start from each entry point and follow the control flow across units, recording at each step the actor, the inputs taken, the decisions made (with their outcomes), the messages shown, and the data written. Name each process by its business meaning only when the code makes it evident; otherwise keep the technical name and mark the meaning inferred.

## Inputs
Entry points, all sources, and the behaviour/rule/dependency claims.

## Outputs
`business-context.md` (plain-English orientation) and `processes.md` (end-to-end processes, each step traced to code).

## Output contract
Reply with one JSON object matching:
```json
{
 "business_context": {
  "what_it_is": "<2-4 sentences: what kind of system this is and what it is for, for a reader with no code knowledge>",
  "who_uses_it": [
   {
    "actor": "...",
    "how": "..."
   }
  ],
  "what_it_manages": [
   {
    "entity": "<business name>",
    "record": "<code name>",
    "store": "<file/table>",
    "fields": [
     {
      "name": "...",
      "meaning": "...",
      "type": "..."
     }
    ]
   }
  ],
  "business_rules": [
   {
    "rule": "<plain English>",
    "applies_to": "<process>",
    "confidence": "confirmed|inferred",
    "evidence": [
     {
      "file": "...",
      "line_start": 1,
      "line_end": 1,
      "excerpt": "..."
     }
    ]
   }
  ],
  "parameters": [
   {
    "name": "...",
    "value": "...",
    "meaning": "...",
    "where_used": "..."
   }
  ],
  "not_in_code": [
   "<things a business reader would expect that the code does not show>"
  ]
 },
 "overview": "<plain-English description of what the system does for its users, 1-2 paragraphs, readable by a business owner with no programming knowledge>",
 "processes": [
  {
   "name": "<business name>",
   "technical_name": "<dispatch case / paragraph>",
   "trigger": "<how it starts>",
   "actor": "<who>",
   "outcome": "<end state>",
   "description": "<plain-English narrative of the process, one paragraph: what the user does, what the system checks, what it rejects and why, what it records>",
   "confidence": "confirmed|inferred",
   "steps": [
    {
     "n": 1,
     "unit": "...",
     "action": "<what happens>",
     "kind": "input|decision|message|data|call|output",
     "outcome_if_true": "<for decisions>",
     "outcome_if_false": "<for decisions>",
     "evidence": [
      {
       "file": "...",
       "line_start": 1,
       "line_end": 1,
       "excerpt": "..."
      }
     ]
    }
   ]
  }
 ],
 "claims": [
  {
   "kind": "behavior",
   "statement": "...",
   "confidence": "confirmed|inferred",
   "evidence": [
    {
     "file": "...",
     "line_start": 1,
     "line_end": 1,
     "excerpt": "..."
    }
   ]
  }
 ],
 "gaps": [
  {
   "description": "...",
   "severity": "critical|moderate|cosmetic|out_of_scope"
  }
 ]
}
```

## Rules
- Every confirmed claim cites `file:line_start-line_end` with a short excerpt.
- Inferred claims are written as hypotheses.
- Anything you cannot determine becomes a gap, never a guess.

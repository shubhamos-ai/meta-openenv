---
status: planned
description: Phase 3 Context identifying deterministic Task bounds and the Grader logic engine.
---

# Phase 3 Context: Tasks & Graders

## Domain Context
The hackathon evaluation criteria demands completely reproducible evaluation scores. The tasks must consist of fixed-length episodes with specifically generated content seeds.

## Decisions Made
- **D-30 [Task Difficulty Tiers]**: 
  - `easy`: 8 emails, Seed 42, simpler parsing
  - `medium`: 20 emails, Seed 123, requires strict prioritization
  - `hard`: 50 emails, Seed 999, requires efficiency optimization to stay within max steps
  (Implemented in `tasks/`)
- **D-31 [Deterministic Base Grader]**: 
  - Grades must be computed on a 0.0-1.0 deterministic scale at the end of every episode.
  - Calculation incorporates Priority sorting accuracy, Classification clustering mapping, and Resolution ratios.
  (Implemented in `graders/base_grader.py`)

## Canonical References
- `.planning/REQUIREMENTS.md`

## Code Context
- `tasks/easy.py`, `tasks/medium.py`, `tasks/hard.py`
- `graders/base_grader.py` 

## Specifics & Edge Cases
- Grader must gracefully handle the agent calling `finish` prematurely.
- Seeds must lock the email IDs and texts precisely so that graders always compute against the same ground truths.

## Deferred Ideas
None.

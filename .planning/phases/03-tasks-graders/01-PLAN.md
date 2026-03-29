---
wave: 1
depends_on: []
files_modified: []
autonomous: true
requirements_addressed: [EMAIL-03, EMAIL-04]
must_haves:
  - Verify deterministic mapping in Grader formula
  - Verify difficulty tasks exist in the directory
---

# Plan 01: Verify Tasks and Graders logic

## Objective
The Tasks and Graders modules were implemented concurrently with the engine environment setup in Phase 1 to satisfy tests. This plan merely verifies their presence and compliance.

## Tasks

### Task 1: Verify pre-implemented directory
<task>
<read_first>
- tasks/
- graders/
</read_first>
<action>
Verify that the files `easy.py`, `medium.py`, and `hard.py` exist in `tasks/` and strictly use seeds 42, 123, and 999. Verify that `base_grader.py` exists in `graders/` and implements deterministic scoring. Commit the completion of Phase 3 Planning.
</action>
<acceptance_criteria>
- [ ] Tasks use fixed seeds and exact counts.
- [ ] Grader engine executes a deterministic weighting function.
</acceptance_criteria>
</task>

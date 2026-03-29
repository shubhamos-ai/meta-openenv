---
wave: 2
depends_on: [01-PLAN.md]
files_modified: [environment.py]
autonomous: true
requirements_addressed: [OENV-01, OENV-02, OENV-03, OENV-06, EMAIL-05, EMAIL-06, EMAIL-07]
must_haves:
  - environment.py implements EmailTriageEnv class
  - reset(task_config) returns valid Observation
  - step(action) returns (Observation, float, bool, dict)
  - state() returns full State with gt_category and gt_priority
  - Episode terminates when all emails processed OR max_steps reached
  - Same seed always yields identical reset() output
---

# Plan 02: environment.py — EmailTriageEnv Class

## Objective
Implement `EmailTriageEnv` — the core OpenEnv engine managing episode lifecycle, email state, and correct observation construction.

## Tasks

### Task 1: Create environment.py with EmailTriageEnv
<task>
<read_first>
- models.py — to import all typed models
- .planning/phases/01-core-environment-models/01-CONTEXT.md — D-11 through D-19
- .planning/REQUIREMENTS.md — OENV-01 through OENV-06, EMAIL-05, EMAIL-06, EMAIL-07
</read_first>
<action>
Create `environment.py` implementing the full EmailTriageEnv class with reset/step/state + episode management.
</action>
<acceptance_criteria>
- [ ] `grep -n "class EmailTriageEnv" environment.py` returns a match
- [ ] `grep -n "def reset" environment.py` returns a match
- [ ] `grep -n "def step" environment.py` returns a match
- [ ] `grep -n "def state" environment.py` returns a match
- [ ] `grep -n "_build_observation" environment.py` returns a match
- [ ] `grep -n "body_preview" environment.py` returns a match (200-char truncation)
- [ ] `python3 -c "from environment import EmailTriageEnv"` exits 0
- [ ] Two sequential reset() calls with same seed return identical email IDs
</acceptance_criteria>
</task>

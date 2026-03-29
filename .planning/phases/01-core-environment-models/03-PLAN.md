---
wave: 1
depends_on: []
files_modified: [openenv.yaml]
autonomous: true
requirements_addressed: [OENV-05]
must_haves:
  - openenv.yaml is valid YAML
  - Contains name, version, description, author, task_count
  - Contains action_space, observation_space, reward_range
  - Contains all 3 tasks (easy/medium/hard) with seeds matching REQUIREMENTS.md
---

# Plan 03: openenv.yaml — Metadata File

## Objective
Produce the `openenv.yaml` metadata file required by the OpenEnv spec and `openenv validate`.

## Tasks

### Task 1: Create openenv.yaml
<task>
<read_first>
- .planning/REQUIREMENTS.md — task seeds (TASK-01: seed=42, TASK-02: seed=123, TASK-03: seed=999)
- .planning/phases/01-core-environment-models/01-CONTEXT.md — D-16, D-17
</read_first>
<action>
Create `openenv.yaml` in the project root with this exact YAML content defining all metadata per OpenEnv spec.
</action>
<acceptance_criteria>
- [ ] `openenv.yaml` exists in project root
- [ ] `python3 -c "import yaml; yaml.safe_load(open('openenv.yaml'))"` exits 0
- [ ] File contains `name: SHUBHAMOS`
- [ ] File contains seed: 42, seed: 123, seed: 999
- [ ] File contains all 6 action types
- [ ] `reward_range` field is present
</acceptance_criteria>
</task>

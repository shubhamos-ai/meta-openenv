---
wave: 1
depends_on: []
files_modified: []
autonomous: true
requirements_addressed: [EMAIL-05, EMAIL-06, OENV-02]
must_haves:
  - Verify models.py and environment.py actually conform to Action schema.
  - Verify reward.py assigns correct dense signals.
---

# Plan 01: Verify Action Space and Reward Engine

## Objective
The Action Space and Reward Engine code was implemented early during Phase 1 to satisfy cross-class dependency resolution. This plan just formally verifies that the implementation adheres to Phase 2 requirements so we can proceed to Graders.

## Tasks

### Task 1: Verify pre-implemented code
<task>
<read_first>
- models.py
- reward.py
</read_first>
<action>
Verify that the `Action` schema in `models.py` has all required fields and `reward.py` contains the exact reward constants and step cost calculation. Submit the git commit marking the completion of the phase planning.
</action>
<acceptance_criteria>
- [ ] Action space defined and serializable.
- [ ] RewardEngine attached to EmailTriageEnv.
- [ ] Dense rewards assign positive and negative markers reliably.
</acceptance_criteria>
</task>

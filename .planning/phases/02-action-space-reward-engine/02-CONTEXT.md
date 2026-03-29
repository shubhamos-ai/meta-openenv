---
status: planned
description: Phase 2 Context and Decisions for Action Space and Reward Engine
---

# Phase 2 Context: Action Space & Reward Engine

## Domain Context
The action space must be strictly dispatchable to update the state of an email instance. The reward engine must be dense, providing feedback on sub-tasks rather than just end-of-episode resolution.

## Decisions Made
- **D-20 [Action Structure]**: OpenEnv action should define an `action_type` string, target `email_id`, and optional payloads `category`, `level`, and `text`. (Implemented in Phase 1 `models.py`)
- **D-21 [Dense Component Rewards]**: 
  - Classification: +0.3 Correct, -0.2 Incorrect
  - Priority: +0.3 Correct, -0.2 Incorrect
  - Resolution: +0.5 Non-spam resolved, +0.4 Bonus for Urgent
  - Penalties: -0.3 for resolving Spam, -0.5 for ignoring Urgent
  - Cost: -0.01 per step to force efficiency.
  (Implemented in Phase 1 `reward.py`)
- **D-22 [Reward Engine Attachment]**: Due to dependency constraints, we injected the `RewardEngine` into the `EmailTriageEnv` instead of hardcoding the reward calculation directly inside `environment.py`.

## Canonical References
- `.planning/REQUIREMENTS.md` (Specifically task and grading requirements)

## Code Context
- `models.py`
- `reward.py`
- `environment.py`

## Specifics & Edge Cases
- Agents drafting a reply for an urgent or billing email before resolving gets an extra +0.1 `REPLY_BONUS`.
- `ignore_email` gives +0.2 if the target was `spam` (as avoiding the step cost + active skipping).

## Deferred Ideas
None.

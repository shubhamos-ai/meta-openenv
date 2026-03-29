---
wave: 1
depends_on: []
files_modified: []
autonomous: true
requirements_addressed: [INF-01, INF-02, INF-03, INF-05]
must_haves:
  - Verify standalone inference.py execution constraints using HF OpenRouter integration.
---

# Plan 01: Verify Inference Agent Loop

## Objective
The Agent inference integration script was already completed to check the model capabilities with OpenEnv API schema requirements in the previous phase sprint. Verify existing integration.

## Tasks

### Task 1: Verify pre-implemented directory
<task>
<read_first>
- inference.py
</read_first>
<action>
Verify that `inference.py` integrates `EmailTriageEnv` mapped via an OpenAI LLM class passing environment variables `HF_TOKEN` and `MODEL_NAME`. Validate that prompt construction strictly requires json mode rendering. Commit Phase 4 formal verification.
</action>
<acceptance_criteria>
- [ ] Agent evaluates using OpenAI library over HF Router mapping.
- [ ] Code iterates through initialized difficulty tasks sequentially.
</acceptance_criteria>
</task>

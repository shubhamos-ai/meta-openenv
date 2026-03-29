---
status: planned
description: Phase 4 Context focusing on LLM Integration script.
---

# Phase 4 Context: Inference Script

## Domain Context
An automated script needs to run LLM inferences via Hugging Face OpenRouter using OpenAI libraries to navigate the newly-created `EmailTriageEnv`.

## Decisions Made
- **D-40 [Client Configuration]**: The OpenAI Python client handles all routing. Standard environmental constants `HF_TOKEN`, `API_BASE_URL` (default `router.huggingface.co/v1`), and `MODEL_NAME` (default `Qwen/Qwen2.5-72B-Instruct`) must be parameterized.
- **D-41 [JSON Parsing Safety]**: `inference.py` wraps model outputs in safety try-catch loops when interpreting JSON to handle non-compliant API responses.
- **D-42 [Episode Management]**: Script iterates sequentially through `easy.py`, `medium.py`, and `hard.py`, producing a graded score for each one.

## Canonical References
- `.planning/REQUIREMENTS.md`

## Code Context
- `inference.py`

## Specifics & Edge Cases
- Script should execute gracefully under 20 minutes with limits.

## Deferred Ideas
None.

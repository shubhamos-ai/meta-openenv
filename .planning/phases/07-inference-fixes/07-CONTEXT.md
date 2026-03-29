---
status: planned
description: Phase 7 integrates robust fault-tolerance, LLM output handling, API retries, and hardened execution loops inside inference.py.
---

# Phase 7 Context: Inference Robustness

## Domain Context
Because SHUBHAMOS is evaluating AI agents on real-world constraints via Hackathon automated grading, runtime crashes strictly evaluate to 0 points. Open-source LLMs can output conversational text alongside JSON, and Hugging Face Router experiences rate-limit spikes. The `inference.py` loop must become 100% resilient to these realities.

## Decisions Made
- **D-70 [Fallback Actions]**: If parsing fails after stripping markdown blocks, the agent will gracefully inject a fallback action (e.g., `ignore_email`) or `classify_email: "general"` to preserve loop integrity.
- **D-71 [API Backoff]**: Hugging Face API invokes will wrap inside a 3-retry block with an exponential 1s -> 2s -> 4s backoff.
- **D-72 [No Unhandled Runtime Exceptions]**: Every `env.step()` application and API response will be wrapped in try/catches.
- **D-73 [Clean Terminations]**: Ensure `env.close()` exists via `finally` blocks, and that stdout accurately formats `FINAL SCORE (<task>): X.XX` for judges reading terminal dumps.

## Canonical References
- `.planning/REQUIREMENTS.md` (REQ-700 to 703, 801)

## Code Context
- `inference.py`

## Specifics & Edge Cases
- Markdown blocks might appear as ```json\n{...}\n``` or inline text. The parser must aggressively extract the first `{ ... }` block matching JSON schemas.
- Empty responses from the API should trigger the retry loop, not an immediate fallback. Only a total exhaustion of retries triggers a fallback action.

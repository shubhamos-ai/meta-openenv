---
wave: 1
depends_on: []
files_modified: ["inference.py"]
autonomous: true
requirements_addressed: [REQ-700, REQ-701, REQ-702, REQ-703, REQ-801]
must_haves:
  - inference.py handles markdown and chatty LLM responses cleanly using regex or block truncation.
  - LLM timeouts trigger a 3-max-retry exponential backoff instead of crashing.
  - Final task output clearly states 'FINAL SCORE (task): X.XX' mapped perfectly.
---

# Plan 01: Agent Fault-Tolerance

## Objective
Harden `inference.py` LLM agent loop preventing grading disqualifications due to crashes, bad format serialization, or Hugging Face endpoint latency spikes.

## Tasks

### Task 1: API Resiliency Wrapper
<task>
<read_first>
- inference.py
</read_first>
<action>
Implement an `api_call_with_retry` function wrapping `call_llm`. Use a `for attempt in range(3)` construct capturing `Exception` (especially networking/timeout errors). Implement `time.sleep(2 ** attempt)` for exponential backoff (1s, 2s, 4s). If all retries fail, return a dummy string `"{}"` allowing the parser step to invoke the fallback action rather than crashing.
</action>
<acceptance_criteria>
- [ ] 3 retries max executed internally.
- [ ] Fallback `{}` string passed downstream upon total failure.
</acceptance_criteria>
</task>

### Task 2: Robust LLM Parser & Fallback Generator
<task>
<action>
Update `parse_action` in `inference.py` to strip arbitrary markdown and conversational prefix/suffix text securely. (Extract the substring between the first `{` and the last `}`). 
Add a strict validation fallback. If validation/JSON extraction totally fails or doesn't match an active valid `email_id` from the observation, construct and return a safe fallback action `Action(action_type="ignore_email", email_id=obs.emails[0].id)` manually. Ensure `parse_action` never returns `None`.
</action>
<acceptance_criteria>
- [ ] Parser strips all wrapping texts outside `{ ... }`.
- [ ] Returns a valid fallback `Action` instead of `None` on unrecoverable data.
</acceptance_criteria>
</task>

### Task 3: Hardened Step Loop & Output Metrics
<task>
<action>
Wrap `env.step(action)` in `try/except Exception as e:` inside `run_agent`. If `step` fails, log the exception and invoke the fallback action mechanism manually to prevent runtime halt. Add explicit logging metrics detailing `[Fallback: YES/NO]`.
Wrap the entire agent loop logic inside a `try/finally` block that calls `env.close()` ensuring graceful state clearing.
Alter the final output prints natively at the end of `run_agent` to clearly emit `FINAL SCORE (task): X.XX` for evaluator grading scripts.
</action>
<acceptance_criteria>
- [ ] Step executions wrapped securely in try/catches.
- [ ] Finally block invokes `env.close()`.
- [ ] Stdout contains exact final evaluation signature.
</acceptance_criteria>
</task>

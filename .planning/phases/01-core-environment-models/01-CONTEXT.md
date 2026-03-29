# Phase 1: Core Environment & Models - Context

**Gathered:** 2026-03-29 (auto mode)
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the foundational OpenEnv engine: typed Pydantic models for Email/Action/Observation/State, and the `EmailTriageEnv` class implementing `reset()`, `step()`, `state()`. Also produce `openenv.yaml`. This phase establishes data contracts and episode lifecycle — no action dispatch or reward logic yet.

</domain>

<decisions>
## Implementation Decisions

### Pydantic Models
- **D-01:** All models use Pydantic v2 (`from pydantic import BaseModel, Field`). Use strict typing with `Literal` for enums (category, priority, sentiment).
- **D-02:** `EmailCategory`: `Literal["spam", "general_inquiry", "billing_issue", "urgent_complaint"]`
- **D-03:** `Priority`: `Literal["low", "medium", "high", "unknown"]` — `unknown` is the default agent-facing value
- **D-04:** `Sentiment`: `Literal["positive", "neutral", "negative"]`
- **D-05:** `Email` model fields: `id` (str), `subject` (str), `body` (str), `sender` (str), `timestamp` (datetime), `category` (EmailCategory | None), `priority` (Priority = "unknown"`, `sentiment` (Sentiment), `resolved` (bool = False), `escalated` (bool = False), `ignored` (bool = False), `reply_drafted` (bool = False)
- **D-06:** `Action` model fields: `action_type` (str), `email_id` (str), `params` (dict — flexible for category/level/text payloads)
- **D-07:** `Observation` model fields: `emails` (list of ObservationEmail — truncated view), `total_emails` (int), `pending_count` (int), `resolved_count` (int), `step_count` (int), `max_steps` (int), `elapsed_time` (float)
- **D-08:** `ObservationEmail` (agent-facing subset): `id`, `subject`, `body_preview` (≤200 chars), `category` (what agent has assigned so far, else None), `priority` (agent-assigned, defaults "unknown"), `sentiment`, `resolved`, `escalated`
- **D-09:** `State` (internal, full): all emails with complete body + ground truth `gt_category` + `gt_priority`, action history list, step count, episode start time, total cumulative reward
- **D-10:** `Info` dict returned from step(): `{"action_type": str, "email_id": str, "valid": bool, "error": str|None, "step_reward": float}`

### Environment Class
- **D-11:** Class name: `EmailTriageEnv`. Single file: `environment.py`. No framework dependency — pure Python class.
- **D-12:** `reset(task_config)` accepts a task config dict with: `emails` (list of raw email dicts), `seed` (int), `max_steps` (int). Returns `Observation`.
- **D-13:** Episode terminates (`done=True`) when: all emails resolved/ignored/escalated OR `step_count >= max_steps`.
- **D-14:** `state()` returns full internal `State` including ground truth labels hidden from `Observation`.
- **D-15:** Episode state is stored on `self` — no external DB or file I/O during episode.

### openenv.yaml
- **D-16:** Fields: `name`, `version`, `description`, `author`, `task_count`, `action_space`, `observation_space`, `reward_range`, `tasks` (list with name/difficulty/seed).
- **D-17:** `reward_range: [-inf, +inf]` (unbounded dense rewards)

### Reproducibility
- **D-18:** `reset()` uses `random.seed(seed)` before any stochastic operations. Same seed → identical starting state guaranteed.
- **D-19:** Email ordering in Observation is deterministic (insertion order, not shuffled).

### Agent's Discretion
- Internal logging format (use print statements or Python logging — planner decides)
- Whether `step()` validates action type as enum or free string with dispatch fallback
- Exact timestamp format in openenv.yaml

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### OpenEnv Spec
- `.planning/REQUIREMENTS.md` §OpenEnv Spec — OENV-01 through OENV-06: full spec requirements
- `.planning/ROADMAP.md` §Phase 1 — success criteria and plan breakdown

### Project Context
- `.planning/PROJECT.md` — Core value, constraints, key decisions (LLM API, naming, deployment target)

No external OpenEnv spec file exists in repo — requirements are fully captured in .planning/REQUIREMENTS.md and decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — greenfield project, no existing code

### Established Patterns
- Python + Pydantic v2 (from requirements)
- No framework for env class — pure Python OOP
- OpenAI SDK used in inference.py (Phase 4) — models must be JSON-serializable

### Integration Points
- `environment.py` is the central import for all other phases
- `models.py` types are imported by tasks/, graders/, and inference.py
- `openenv.yaml` must align exactly with models defined in models.py

</code_context>

<specifics>
## Specific Ideas

- Environment should feel like a real enterprise tool — not a toy. Email bodies should be realistic (professional tone, plausible scenarios).
- The `ObservationEmail.body_preview` is the only body text the agent sees — full body stays in State for grading purposes.
- Project name across all files: **SHUBHAMOS: AI Email Operations & Triage Environment**

</specifics>

<deferred>
## Deferred Ideas

- Action dispatch logic (validate_action, _dispatch_action) — Phase 2
- Reward calculation — Phase 2
- Email dataset generation (seeded) — Phase 3
- Dashboard serving — Phase 6

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-core-environment-models*
*Context gathered: 2026-03-29*

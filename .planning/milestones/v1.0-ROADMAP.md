# Roadmap: SHUBHAMOS — AI Email Operations & Triage Environment

**Milestone:** v1.0 — Hackathon Submission
**Granularity:** Standard
**Total phases:** 6
**Requirements mapped:** 47 / 47 ✓

---

## Phases Overview

| # | Phase | Goal | Requirements | Steps |
|---|-------|------|--------------|-------|
| 1 | Core Environment & Models | Build the OpenEnv engine and typed models | OENV-01–06, EMAIL-01–07 | ~3 |
| 2 | Action Space & Reward Engine | Wire actions and dense reward function | ACT-01–07, REW-01–09 | ~3 |
| 3 | Tasks & Graders | Build 3 difficulty tiers with deterministic scoring | TASK-01–05, GRAD-01–05 | ~3 |
| 4 | Inference Script | LLM agent loop via OpenAI client → HF Router | INF-01–07 | ~2 |
| 5 | Dockerfile & README | Containerize and document for HF Spaces submission | DEPLOY-01–04, DOC-01–02 | ~2 |
| 6 | Dashboard | Lightweight inbox view and stats UI | UI-01–04 | ~2 |

---

## Phase 1: Core Environment & Models

**Goal:** Implement the foundational OpenEnv spec — `reset()`, `step()`, `state()` — backed by typed Pydantic models for Email, Action, Observation, and State. The environment engine must manage episode lifecycle and email dataset loading.

**Requirements:** OENV-01, OENV-02, OENV-03, OENV-04, OENV-05, OENV-06, EMAIL-01, EMAIL-02, EMAIL-03, EMAIL-04, EMAIL-05, EMAIL-06, EMAIL-07

**Plans:**
1. `models.py` — Define all Pydantic models: `Email`, `Action`, `Observation`, `State`, `EmailCategory`, `Priority`, `Sentiment`
2. `environment.py` — Implement `EmailTriageEnv` class with `reset()`, `step()`, `state()` and episode lifecycle
3. `openenv.yaml` — Write metadata file; validate structure passes spec

**Success criteria:**
1. `env.reset()` returns a valid `Observation` with a non-empty email list
2. `env.step(action)` returns `(Observation, float, bool, dict)` without raising exceptions
3. `env.state()` returns full internal `State` including ground truth labels
4. All Pydantic models validate their fields (type errors on invalid data)
5. `openenv.yaml` is well-formed with correct environment metadata
6. `env.reset()` twice produces identical starting states (seed reproducibility)

**UI hint:** no

---

## Phase 2: Action Space & Reward Engine

**Goal:** Implement the full action dispatch system and the dense reward function. Every valid action must produce a realistic state transition. Every action outcome must generate a meaningful reward signal grounded in ground truth.

**Requirements:** ACT-01, ACT-02, ACT-03, ACT-04, ACT-05, ACT-06, ACT-07, REW-01, REW-02, REW-03, REW-04, REW-05, REW-06, REW-07, REW-08, REW-09

**Plans:**
1. `environment.py` (action dispatch) — Implement `_dispatch_action()` routing all 6 action types with validation
2. `reward.py` — Implement `RewardEngine` computing per-action rewards against ground truth
3. Integration test — Run a short episode manually verifying reward accumulation per action type

**Success criteria:**
1. `classify_email` with correct category yields +0.3 reward; incorrect yields -0.2
2. `set_priority` with correct level yields +0.3; incorrect yields -0.2
3. `mark_resolved` yields +0.5 (and +0.4 urgent bonus if within first 30% of max_steps)
4. `ignore_email` on urgent email yields -0.5
5. Each step always incurs -0.01 delay penalty regardless of action
6. Invalid action (bad email_id) returns error in `info` dict, reward=0.0, episode continues

**UI hint:** no

---

## Phase 3: Tasks & Graders

**Goal:** Create three seeded, deterministic email datasets (easy/medium/hard) as loadable task configs, and matching graders that score a completed episode 0.0–1.0 based on the grading formula.

**Requirements:** TASK-01, TASK-02, TASK-03, TASK-04, TASK-05, GRAD-01, GRAD-02, GRAD-03, GRAD-04, GRAD-05

**Plans:**
1. `tasks/easy.py`, `tasks/medium.py`, `tasks/hard.py` — Define seeded email datasets with ground truth
2. `graders/easy_grader.py`, `graders/medium_grader.py`, `graders/hard_grader.py` — Implement post-episode scoring
3. Task validation — Verify each task produces identical dataset on repeated seed calls; graders output stable scores

**Success criteria:**
1. Easy task always loads exactly the same 5–8 emails when called with seed=42
2. Medium task loads 15–25 emails with seed=123; at least 3 different categories present
3. Hard task loads 40–60 emails with seed=999; includes spam, urgent, billing
4. Each grader outputs a float in [0.0, 1.0] for any completed episode state
5. Same episode state passed to grader twice returns identical score (deterministic)
6. Hard grader score is lower than easy grader score for the same random agent (difficulty scaling verified)

**UI hint:** no

---

## Phase 4: Inference Script

**Goal:** Build `inference.py` — a complete LLM agent loop that reads environment observations, decides actions via Qwen/HF Router through the OpenAI-compatible client, and runs all three tasks to produce reproducible scores.

**Requirements:** INF-01, INF-02, INF-03, INF-04, INF-05, INF-06, INF-07

**Plans:**
1. `inference.py` — LLM agent loop: prompt construction from Observation, action parsing, `step()` integration
2. Agent prompt design — System prompt + observation serialization + action parsing with fallback handling
3. Score reporting — Per-task and aggregate output with timing guard (< 20 min)

**Success criteria:**
1. Script starts with `python inference.py` and requires no manual input
2. `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN` read from environment variables only (no hardcoding)
3. OpenAI client instantiated as `OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)`
4. All three tasks run sequentially; each produces a grader score output
5. Script completes in under 20 minutes on 2 vCPU / 8GB RAM
6. Output format: task name, steps taken, final score (float), reproducible across runs

**UI hint:** no

---

## Phase 5: Dockerfile & README

**Goal:** Containerize the environment for HF Spaces deployment and write the complete README with all hackathon-required documentation sections.

**Requirements:** DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DOC-01, DOC-02

**Plans:**
1. `Dockerfile` — Multi-stage build: Python base, install deps, expose API server port, start command
2. API server layer — Thin FastAPI/Flask wrapper exposing `/reset`, `/step`, `/state` HTTP endpoints
3. `README.md` — All required sections: problem, action/obs spaces, tasks, reward, setup, baseline results

**Success criteria:**
1. `docker build -t shubhamos-openenv .` completes without errors
2. `docker run -p 8000:8000 shubhamos-openenv` starts server and responds to `GET /health`
3. `POST /reset` returns valid Observation JSON
4. `POST /step` with valid action JSON returns `(observation, reward, done, info)` JSON
5. README contains all required sections per hackathon spec
6. All Python files have module-level docstrings

**UI hint:** no

---

## Phase 6: Dashboard

**Goal:** Add a minimal read-only web dashboard served from the same container. Displays email inbox state, resolution status, and live stats — useful for demonstrating the environment to judges.

**Requirements:** UI-01, UI-02, UI-03, UI-04

**Plans:**
1. `dashboard/` — Static HTML + vanilla JS dashboard served by the existing API server
2. Inbox view — Table of emails: subject, category, priority, status (pending/resolved/escalated)
3. Stats panel — Counters: total, pending, resolved; current episode score

**Success criteria:**
1. Dashboard loads at `http://localhost:8000/dashboard` in a browser
2. Inbox view shows all emails with correct status indicators
3. Stats update to reflect current environment state
4. Dashboard degrades gracefully (no JS errors) when no episode is active

**UI hint:** yes

---

## Requirement Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OENV-01 | Phase 1 | Pending |
| OENV-02 | Phase 1 | Pending |
| OENV-03 | Phase 1 | Pending |
| OENV-04 | Phase 1 | Pending |
| OENV-05 | Phase 1 | Pending |
| OENV-06 | Phase 1 | Pending |
| EMAIL-01 | Phase 1 | Pending |
| EMAIL-02 | Phase 1 | Pending |
| EMAIL-03 | Phase 1 | Pending |
| EMAIL-04 | Phase 1 | Pending |
| EMAIL-05 | Phase 1 | Pending |
| EMAIL-06 | Phase 1 | Pending |
| EMAIL-07 | Phase 1 | Pending |
| ACT-01 | Phase 2 | Pending |
| ACT-02 | Phase 2 | Pending |
| ACT-03 | Phase 2 | Pending |
| ACT-04 | Phase 2 | Pending |
| ACT-05 | Phase 2 | Pending |
| ACT-06 | Phase 2 | Pending |
| ACT-07 | Phase 2 | Pending |
| REW-01 | Phase 2 | Pending |
| REW-02 | Phase 2 | Pending |
| REW-03 | Phase 2 | Pending |
| REW-04 | Phase 2 | Pending |
| REW-05 | Phase 2 | Pending |
| REW-06 | Phase 2 | Pending |
| REW-07 | Phase 2 | Pending |
| REW-08 | Phase 2 | Pending |
| REW-09 | Phase 2 | Pending |
| TASK-01 | Phase 3 | Pending |
| TASK-02 | Phase 3 | Pending |
| TASK-03 | Phase 3 | Pending |
| TASK-04 | Phase 3 | Pending |
| TASK-05 | Phase 3 | Pending |
| GRAD-01 | Phase 3 | Pending |
| GRAD-02 | Phase 3 | Pending |
| GRAD-03 | Phase 3 | Pending |
| GRAD-04 | Phase 3 | Pending |
| GRAD-05 | Phase 3 | Pending |
| INF-01 | Phase 4 | Pending |
| INF-02 | Phase 4 | Pending |
| INF-03 | Phase 4 | Pending |
| INF-04 | Phase 4 | Pending |
| INF-05 | Phase 4 | Pending |
| INF-06 | Phase 4 | Pending |
| INF-07 | Phase 4 | Pending |
| DEPLOY-01 | Phase 5 | Pending |
| DEPLOY-02 | Phase 5 | Pending |
| DEPLOY-03 | Phase 5 | Pending |
| DEPLOY-04 | Phase 5 | Pending |
| DOC-01 | Phase 5 | Pending |
| DOC-02 | Phase 5 | Pending |
| UI-01 | Phase 6 | Pending |
| UI-02 | Phase 6 | Pending |
| UI-03 | Phase 6 | Pending |
| UI-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 57 total
- Mapped to phases: 57
- Unmapped: 0 ✓

---
*Roadmap created: 2026-03-29*
*Last updated: 2026-03-29 after initial creation*

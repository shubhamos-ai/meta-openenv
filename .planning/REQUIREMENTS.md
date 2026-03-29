# Requirements: SHUBHAMOS — AI Email Operations & Triage Environment

**Defined:** 2026-03-29
**Core Value:** AI agents can be meaningfully evaluated on real-world email operations via dense reward signals, deterministic grading, and reproducible scores across easy/medium/hard difficulty tiers.

---

## v1 Requirements

### OpenEnv Spec

- [ ] **OENV-01**: Environment implements `reset()` that returns a clean typed `Observation`
- [ ] **OENV-02**: Environment implements `step(action)` that returns `(Observation, reward, done, info)`
- [ ] **OENV-03**: Environment implements `state()` that returns full internal `State`
- [ ] **OENV-04**: `Action`, `Observation`, `State` are Pydantic typed models with full field validation
- [ ] **OENV-05**: `openenv.yaml` metadata file present and passes `openenv validate`
- [ ] **OENV-06**: Episode terminates when all emails processed OR max steps reached

### Email Simulation

- [ ] **EMAIL-01**: Environment generates realistic emails with: id, subject, body, sender, timestamp, category, priority, sentiment, resolved status
- [ ] **EMAIL-02**: Emails support four categories: spam, general_inquiry, billing_issue, urgent_complaint
- [ ] **EMAIL-03**: Emails have priority levels: low, medium, high (unknown to agent initially)
- [ ] **EMAIL-04**: Emails have sentiment: positive, neutral, negative (derived from body)
- [ ] **EMAIL-05**: Ground truth labels (category + priority) stored in internal State, hidden from agent
- [ ] **EMAIL-06**: Email datasets are seeded and deterministic per task (reproducible)
- [ ] **EMAIL-07**: Each email has a body preview (≤200 chars) exposed to agent in Observation

### Action Space

- [ ] **ACT-01**: Agent can call `classify_email(email_id, category)` to assign a category
- [ ] **ACT-02**: Agent can call `set_priority(email_id, level)` with levels: low, medium, high
- [ ] **ACT-03**: Agent can call `draft_reply(email_id, text)` to draft a response (required for resolution)
- [ ] **ACT-04**: Agent can call `mark_resolved(email_id)` to close an email
- [ ] **ACT-05**: Agent can call `escalate_email(email_id)` to flag for human handling
- [ ] **ACT-06**: Agent can call `ignore_email(email_id)` to skip an email (penalized for urgent)
- [ ] **ACT-07**: All actions are validated; invalid actions return error in `info` without crashing

### Reward Function

- [ ] **REW-01**: Correct classification awards +0.3 (vs ground truth)
- [ ] **REW-02**: Correct priority assignment awards +0.3 (vs ground truth)
- [ ] **REW-03**: Successfully resolving an email awards +0.5
- [ ] **REW-04**: Resolving an urgent email within first 30% of max steps awards +0.4 bonus
- [ ] **REW-05**: Incorrect classification penalizes -0.2
- [ ] **REW-06**: Wrong priority penalizes -0.2
- [ ] **REW-07**: Ignoring an urgent email penalizes -0.5
- [ ] **REW-08**: Each step incurs a delay penalty of -0.01 (encourages efficiency)
- [ ] **REW-09**: Reward is continuous and dense across entire episode (no sparse-only endpoints)

### Tasks

- [ ] **TASK-01**: Easy task "Basic Inbox" — 5–8 emails, clear unambiguous categories, minimal noise, seed=42
- [ ] **TASK-02**: Medium task "Support Queue" — 15–25 emails, mixed priorities, requires sequencing, seed=123
- [ ] **TASK-03**: Hard task "Enterprise Inbox" — 40–60 emails, high ambiguity, spam + urgent + billing under pressure, seed=999
- [ ] **TASK-04**: Each task is deterministic: same seed always produces same email set
- [ ] **TASK-05**: Each task defines max_steps appropriate to email volume

### Graders

- [ ] **GRAD-01**: Easy grader outputs a float 0.0–1.0 using: classification_accuracy×0.3 + priority_accuracy×0.3 + resolution_rate×0.3 + urgent_handling×0.1
- [ ] **GRAD-02**: Medium grader uses same formula with stricter urgency thresholds
- [ ] **GRAD-03**: Hard grader uses same formula with additional penalty for excessive steps
- [ ] **GRAD-04**: All graders are deterministic and idempotent (same state → same score always)
- [ ] **GRAD-05**: Graders do NOT expose ground truth during episode — only evaluated post-episode

### Inference Script

- [ ] **INF-01**: `inference.py` exists in project root
- [ ] **INF-02**: Script uses `openai.OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)` client
- [ ] **INF-03**: Script reads `API_BASE_URL`, `MODEL_NAME`, `HF_TOKEN` from environment variables
- [ ] **INF-04**: Script runs all three tasks (easy, medium, hard) sequentially
- [ ] **INF-05**: For each task, agent reads Observation, decides Action, calls `step()` in a loop
- [ ] **INF-06**: Script outputs reproducible score per task and overall score
- [ ] **INF-07**: Total runtime under 20 minutes on 2 vCPU / 8GB RAM

### Deployment

- [ ] **DEPLOY-01**: `Dockerfile` builds an image that starts the OpenEnv API server
- [ ] **DEPLOY-02**: Container exposes endpoints compatible with OpenEnv spec (reset, step, state)
- [ ] **DEPLOY-03**: Dockerfile is compatible with Hugging Face Spaces (Docker runtime)
- [ ] **DEPLOY-04**: `docker build` and `docker run` both succeed without manual intervention

### Documentation

- [ ] **DOC-01**: `README.md` covers: problem description, action/observation spaces, task descriptions, reward explanation, setup & run instructions, baseline results
- [ ] **DOC-02**: All Python files include module-level docstrings and inline comments explaining key logic

### Dashboard (Minimal)

- [ ] **UI-01**: Lightweight web dashboard served from the same container
- [ ] **UI-02**: Inbox view listing all emails with subject, category, priority, and status
- [ ] **UI-03**: Stats panel showing: total emails, resolved count, pending count, current score
- [ ] **UI-04**: Dashboard is read-only (display only, not primary interface for agent)

---

## v2 Requirements

### Advanced Simulation

- **SIM-01**: Dynamic email arrival mid-episode (new emails arrive as steps progress)
- **SIM-02**: Multi-thread email conversations (replies creating sub-threads)
- **SIM-03**: Escalation to simulated human with reply-back mechanics

### Advanced Grading

- **ADVG-01**: Response quality grading (NLP-based evaluation of draft_reply content)
- **ADVG-02**: Efficiency scoring penalizing unnecessary action sequences

### Integration

- **INT-01**: Real email API connectors (Gmail, Outlook read-only)
- **INT-02**: Multi-agent collaboration framework

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| NVIDIA SDK direct calls | Hackathon requires OpenAI-compatible client |
| Gradio / Streamlit UI | Docker-only deployment per requirements |
| Real email integration | Simulation-only for reproducibility and grading |
| Complex React/Next.js frontend | Lightweight HTML/JS dashboard sufficient |
| Voice/email hybrid system | Out of domain for email triage evaluation |
| Multi-agent collaboration | Complexity beyond v1 scope |
| OAuth / authentication for dashboard | Not needed for hackathon evaluation |

---

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OENV-01–06 | Phase 1 | Pending |
| EMAIL-01–07 | Phase 1 | Pending |
| ACT-01–07 | Phase 2 | Pending |
| REW-01–09 | Phase 2 | Pending |
| TASK-01–05 | Phase 3 | Pending |
| GRAD-01–05 | Phase 3 | Pending |
| INF-01–07 | Phase 4 | Pending |
| DEPLOY-01–04 | Phase 5 | Pending |
| DOC-01–02 | Phase 5 | Pending |
| UI-01–04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 47 total
- Mapped to phases: 47
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-29*
*Last updated: 2026-03-29 after initial definition*

# SHUBHAMOS: AI Email Operations & Triage Environment

## What This Is

A production-grade OpenEnv-compatible environment that simulates real-world email inbox management workflows. AI agents interact via `step()`, `reset()`, and `state()` APIs to classify, prioritize, respond to, and resolve emails efficiently. Built for a competitive hackathon, this environment evaluates agent performance on operational tasks like customer support triage, enterprise email handling, and workflow automation.

## Core Value

**AI agents can be meaningfully evaluated on real-world email operations** — the environment must produce dense reward signals, deterministic grading, and reproducible scores across easy/medium/hard difficulty tiers.

## Requirements

### Validated

- ✓ OpenEnv spec compliance (step/reset/state with typed Pydantic models) — v1.0
- ✓ Email simulation engine with realistic content and categories (spam, general inquiry, billing issue, urgent complaint) — v1.0
- ✓ Action system: classify_email, set_priority, draft_reply, mark_resolved, escalate_email, ignore_email — v1.0
- ✓ Observation system: email list with metadata, global stats, time progression — v1.0
- ✓ Dense reward function with partial progress signals and penalties — v1.0
- ✓ Three difficulty-tiered tasks (easy: 5–8 emails, medium: 15–25, hard: 40–60) — v1.0
- ✓ Deterministic graders per task scoring 0.0–1.0 — v1.0
- ✓ Episode management with max steps and clean reset — v1.0
- ✓ Baseline inference script using OpenAI client via HF Router — v1.0
- ✓ Working Dockerfile for HF Spaces deployment — v1.0
- ✓ openenv.yaml metadata file — v1.0
- ✓ Comprehensive README with full documentation — v1.0
- ✓ Minimal web dashboard (inbox view, status indicators, basic stats) — v1.0

### Active

<!-- Current scope. Building toward these. -->
(Pending v1.1 requirements from `/gsd-new-milestone`)

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Multi-agent collaboration — complexity beyond hackathon scope, defer to future
- Real email API integration (Gmail, Outlook) — simulation-only for reproducibility
- Voice/email hybrid — not relevant to core email triage evaluation
- Complex frontend framework (React, Next.js) — lightweight HTML/JS dashboard only
- Gradio/Streamlit UI — Docker-based deployment per hackathon requirements
- NVIDIA SDK direct usage — must use OpenAI-compatible client per rules

## Context

**Hackathon context:** This is for a competitive hackathon with specific evaluation criteria:
- Real-world utility: 30%
- Task & grader quality: 25%
- Environment design: 20%
- Code quality & spec compliance: 15%
- Creativity & novelty: 10%

**Pre-submission checklist (must pass):**
1. HF Space deploys and responds to reset()
2. OpenEnv spec validates (openenv.yaml, typed models, step/reset/state)
3. Dockerfile builds successfully
4. Baseline inference script completes without error
5. 3+ tasks with graders producing scores in 0.0–1.0

**LLM configuration:**
- API_BASE_URL = "https://router.huggingface.co/v1"
- MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
- HF_TOKEN = (from environment)
- Client: OpenAI Python SDK with base_url override

**Infra constraints:**
- 2 vCPU, 8GB RAM
- Inference runtime < 20 minutes

**Email simulation design:**
- Categories: spam, general_inquiry, billing_issue, urgent_complaint
- Email attributes: subject, body, sender, timestamp, priority (unknown initially), sentiment (positive/neutral/negative), resolved status
- Dynamic behavior: new emails may arrive, delays increase backlog pressure, some require escalation
- Ground truth labels for each email (hidden from agent, used by graders)

**Reward design (dense):**
- Correct classification: +0.3
- Correct priority: +0.3
- Resolved email: +0.5
- Quick urgent handling bonus: +0.4
- Incorrect classification: -0.2
- Wrong priority: -0.2
- Ignoring urgent: -0.5
- Step delay penalty: -0.01

**Grading formula:**
```
score = (classification_accuracy * 0.3 + priority_accuracy * 0.3 + resolution_rate * 0.3 + urgent_handling_score * 0.1)
```

## Constraints

- **Tech stack**: Python, Pydantic, OpenAI SDK — per OpenEnv spec and hackathon rules
- **Deployment**: Docker on Hugging Face Spaces — per hackathon requirements
- **Performance**: 2 vCPU, 8GB RAM, < 20 min inference — hard infra limits
- **Reproducibility**: Fixed seeds, deterministic graders — required for evaluation
- **API**: OpenAI-compatible client via HF Router — no direct NVIDIA SDK

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use HF Router instead of NVIDIA SDK | Hackathon requires OpenAI client; HF Router is OpenAI-compatible and free | ✓ Good |
| Include minimal dashboard in v1 | Bonus points for UI, but environment logic is priority | ✓ Good |
| Docker deployment (not Gradio/Streamlit) | Cleaner for OpenEnv API endpoints, more control | ✓ Good |
| Dense reward over sparse | Hackathon scores on "useful varying signal" — dense rewards score higher | ✓ Good |
| Fixed email datasets per task | Reproducibility is critical for evaluation and grading | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-29 after v1.0 milestone*

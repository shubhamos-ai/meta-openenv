# STATE.md — SHUBHAMOS Project

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-29)

**Core value:** AI agents can be meaningfully evaluated on real-world email operations via dense reward signals, deterministic grading, and reproducible scores across easy/medium/hard difficulty tiers.
**Current focus:** Phase 1 — Core Environment & Models

---

## Current Status

**Milestone:** v1.0 — Hackathon Submission
**Phase:** 1 of 6
**Phase status:** Not started

---

## Phase Progress

| Phase | Name | Status | Plans Done |
|-------|------|--------|-----------|
| 1 | Core Environment & Models | ○ Pending | 0/3 |
| 2 | Action Space & Reward Engine | ○ Pending | 0/3 |
| 3 | Tasks & Graders | ○ Pending | 0/3 |
| 4 | Inference Script | ○ Pending | 0/3 |
| 5 | Dockerfile & README | ○ Pending | 0/3 |
| 6 | Dashboard | ○ Pending | 0/3 |

---

## Context for Next Agent

Project is freshly initialized. No code exists yet.

**Priority order:**
1. OpenEnv environment (step/reset/state)
2. Typed Pydantic models
3. Reward function
4. Tasks (easy/medium/hard)
5. Graders
6. inference.py
7. Dockerfile
8. README
9. Lightweight dashboard

**Key constraints:**
- Use OpenAI SDK with `base_url=API_BASE_URL` pointing to HF Router
- MODEL_NAME = Qwen/Qwen2.5-72B-Instruct
- Fixed seeds for reproducibility
- Runs on 2 vCPU / 8GB RAM
- Inference < 20 minutes

---
*Initialized: 2026-03-29*

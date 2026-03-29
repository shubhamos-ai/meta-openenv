# SHUBHAMOS: AI Email Operations & Triage Environment

[![OpenEnv](https://img.shields.io/badge/OpenEnv-1.0-blue)](openenv.yaml)
[![Python](https://img.shields.io/badge/Python-3.11-green)](requirements.txt)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A production-grade **OpenEnv**-compatible environment that simulates real-world email inbox management. AI agents interact via `reset()`, `step()`, and `state()` APIs to classify, prioritize, respond to, and resolve emails efficiently.

## Features

- **OpenEnv-compliant** — standard `reset / step / state` API
- **Dense reward signals** — positive/negative rewards per action type
- **3 difficulty tiers** — Easy (8 emails), Medium (20), Hard (50)
- **Deterministic grading** — same seed always yields same score
- **Realistic email simulation** — real-world billing, urgent, spam scenarios
- **FastAPI server** — HTTP API for remote agent interaction
- **Minimal dashboard** — read-only inbox monitoring UI
- **Docker-ready** — one command deploy to Hugging Face Spaces

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API server

```bash
python server.py
# → http://localhost:7860
```

### 3. Run the LLM agent

```bash
export HF_TOKEN=hf_your_token_here
python inference.py --task easy
python inference.py --task medium
python inference.py --task hard
python inference.py --task all
```

---

## API Reference

All endpoints served at `http://localhost:7860`.

### `POST /reset`

Start a new episode.

```json
{
  "task_id": "easy"
}
```

Returns: `Observation` object with inbox state.

### `POST /step`

Apply one action.

```json
{
  "action_type": "classify_email",
  "email_id": "email_001",
  "category": "billing_issue"
}
```

Returns: `{ observation, reward, done, info }`

### `GET /state`

Full internal state (ground truth labels). For graders only.

### `GET /grade`

Grade the current episode. Returns structured score report.

### `GET /health`

Liveness probe.

---

## Action Space

| `action_type`   | Required fields      | Effect |
|-----------------|---------------------|--------|
| `classify_email`| `email_id`, `category` | Assign category |
| `set_priority`  | `email_id`, `level`    | Assign priority |
| `draft_reply`   | `email_id`, `text`     | Save reply text |
| `mark_resolved` | `email_id`             | Mark done ✓ |
| `escalate_email`| `email_id`             | Escalate to human |
| `ignore_email`  | `email_id`             | Skip (for spam) |

**Categories:** `spam` · `general_inquiry` · `billing_issue` · `urgent_complaint`

**Priorities:** `low` · `medium` · `high`

---

## Reward Function

| Action | Condition | Reward |
|--------|-----------|--------|
| `classify_email` | Correct | +0.30 |
| `classify_email` | Wrong | -0.20 |
| `set_priority` | Correct | +0.30 |
| `set_priority` | Wrong | -0.20 |
| `mark_resolved` | Non-spam | +0.50 |
| `mark_resolved` | Urgent complaint | +0.90 (+0.40 bonus) |
| `mark_resolved` | Spam | -0.30 |
| `ignore_email` | Spam | +0.20 |
| `ignore_email` | Urgent complaint | -0.50 |
| Each step | Always | -0.01 |

---

## Grading Formula

```
score = classification_accuracy × 0.30
      + priority_accuracy        × 0.30
      + resolution_rate          × 0.30
      + urgent_handling_score    × 0.10
```

All metrics are computed deterministically from `state()` ground truth.

### Pass thresholds

| Tier | Pass | Good | Excellent |
|------|------|------|-----------|
| Easy | 0.60 | 0.75 | 0.90 |
| Medium | 0.55 | 0.70 | 0.85 |
| Hard | 0.50 | 0.65 | 0.80 |

---

## Tasks

| ID | Emails | Max Steps | Seed | Description |
|----|--------|-----------|------|-------------|
| `easy` | 8 | 50 | 42 | Basic inbox — clear categories |
| `medium` | 20 | 120 | 123 | Support queue — mixed priorities |
| `hard` | 50 | 300 | 999 | Enterprise inbox — high pressure |

---

## Project Structure

```
shubhamos/
├── models.py          # Pydantic v2 data models
├── environment.py     # EmailTriageEnv (reset/step/state)
├── reward.py          # Dense reward engine
├── server.py          # FastAPI HTTP server
├── inference.py       # LLM agent loop (HF Router)
├── openenv.yaml       # OpenEnv metadata spec
├── requirements.txt
├── Dockerfile
├── tasks/
│   ├── easy.py        # seed=42, 8 emails
│   ├── medium.py      # seed=123, 20 emails
│   └── hard.py        # seed=999, 50 emails
├── graders/
│   ├── base_grader.py # Deterministic scoring logic
│   ├── easy_grader.py
│   ├── medium_grader.py
│   └── hard_grader.py
└── dashboard/
    └── index.html     # Minimal monitoring UI
```

---

## Docker / HF Spaces Deployment

```bash
# Build
docker build -t shubhamos .

# Run locally
docker run -p 7860:7860 -e HF_TOKEN=hf_xxx shubhamos

# HF Spaces: push repo, set HF_TOKEN as secret
```

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_TOKEN` | *(required)* | Hugging Face API token |
| `API_BASE_URL` | `https://router.huggingface.co/v1` | LLM API endpoint |
| `MODEL_NAME` | `Qwen/Qwen2.5-72B-Instruct` | Model to use |
| `PORT` | `7860` | Server port |

---

## License

MIT

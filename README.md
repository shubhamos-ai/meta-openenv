---
title: SHUBHAMOS - AI Email Triage Environment
emoji: 📈
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
license: mit
short_description: OpenEnv AI email triage environment for agent learning
---

# SHUBHAMOS: AI Email Operations & Triage Environment

[![OpenEnv Compliant](https://img.shields.io/badge/OpenEnv-1.0.0-blue.svg)](https://github.com/openenv/spec)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SHUBHAMOS** is a production-grade [OpenEnv](https://github.com/openenv/spec)-compliant environment (developed by **Meta Research**) designed for the **Meta PyTorch Hackathon**. It evaluates and trains AI agents on real-world email triage tasks, providing high-density reward signals and deterministic grading for operational AI agents.

---

## 🖼️ Architecture Overview

```mermaid
graph TD
    A[Gradio Dashboard] -->|User Trigger| B[Inference Engine]
    B -->|Action| C[EmailTriageEnv]
    C -->|Observation| B
    B -->|Step Logic| D{AI Router}
    D -->|Tier 1| E[Qwen-72B Primary]
    D -->|Tier 2| F[NVIDIA Fallback]
    D -->|Tier 3| G[Smart Heuristics]
    C -->|State| H[Deterministic Grader]
    H -->|Final Score| A
```

---

## 🛠️ Key Systems

> [!IMPORTANT]
> **SHUBHAMOS** implements a rigid three-tier inference safety loop to ensure zero-downtime benchmarking even during API outages.

| Feature | Description |
| :--- | :--- |
| **OpenEnv Core** | Full compliance with the OpenEnv v1.0 specification. |
| **Dense Rewards** | Shaped reward signals optimized for RL training and tuning. |
| **Gradio GUI** | Instant interactive benchmarking without writing code. |
| **Multi-AI Switch** | Automatic failover between primary cloud and secret internal AI. |

---

## 🧠 Environment Description

SHUBHAMOS simulates a dynamic email inbox environment. The environment lifecycle follows the standard RL pattern:

1.  **Reset:** The environment initializes with a task-specific seed, creating a predictable set of emails with varying categories and priorities.
2.  **Step:** The agent receives an **Observation** (inbox state) and submits an **Action**. The environment returns a **Reward**, updated state, and a **Done** flag.
3.  **Episode:** The agent continues taking steps until all emails are resolved, escalated, or ignored, or until the `max_steps` limit is reached.

---

## 🚀 Evaluation Center (For Judges)

The agent can be verified through three distinct layers of observability:

### 🎮 Interactive Verification (UI)
1.  Navigate to your **Hugging Face Space**.
2.  Paste your **Hugging Face Token** in the dashboard.
3.  Choose a **Simulation Task** (Easy / Medium / Hard).
4.  Click **Run Agent Benchmark 🚀**.
5.  Watch the agent process the inbox in real-time and view the final **Grade Report**.

### 📝 Automated Startup Audit (Logs)
Every container boot runs a **Pre-flight Health Check**. Inspect the **Hugging Face Container Logs** for:
- [x] **Secret Loading**: `HF_TOKEN loaded successfully ✅`
- [x] **Inference Test**: `Health Check: AI Provider is HEALTHY ✅`
- [x] **E2E Validation**: Detailed benchmark metrics for `easy` and `medium` tasks.

### 🔌 Programmatic API (OpenEnv)
The environment exposes standard OpenEnv endpoints via FastAPI. Access the **interactive documentation** at `/docs`.

---

## ⚙️ OpenEnv Specification

### 📥 Observation Model
The agent perceives the inbox through a structured `Observation` object:
*   **`emails`**: A list of `ObservationEmail` objects (ID, Subject, Sender, Sentiment, Body Preview).
*   **`pending_count`**: Number of emails requiring action.
*   **`resolved_count`**: Number of emails successfully closed.
*   **`elapsed_ratio`**: A float (0.0 to 1.0) indicating progress toward the step limit.

### 📤 Action Model
The agent interacts using structured discrete actions:
*   **`classify_email(email_id, category)`**: Assigns a label (e.g., `billing_issue`).
*   **`set_priority(email_id, level)`**: Assigns priority (`low`, `medium`, `high`).
*   **`mark_resolved(email_id)`**: Attempts to close the email.
*   **`escalate_email(email_id)`**: Hands off to a human operator.
*   **`ignore_email(email_id)`**: Skips the email (penalized for urgent items).

---

## 🎯 Tasks

| Task | ID | Emails | Steps | Difficulty |
| :--- | :--- | :--- | :--- | :--- |
| **Basic Inbox** | `easy` | 8 | 50 | Low complexity, clear categories. |
| **Support Queue** | `medium` | 20 | 120 | Mixed priorities, requires sequencing. |
| **Enterprise Inbox** | `hard` | 50 | 300 | High ambiguity, spam noise, scale pressure. |

---

## 🧪 Grading System (0.0 – 1.0)

SHUBHAMOS uses a **Deterministic Grader** to ensure reproducible scores across different agent architectures. The final score is calculated based on:
1.  **Classification Accuracy (30%):** Matching agent-assigned categories to ground truth.
2.  **Priority Accuracy (30%):** Correctly identifying urgency levels.
3.  **Resolution Rate (30%):** Successfully closing actionable emails.
4.  **Urgent Handling (10%):** Specific bonus for resolving high-priority items early.

---

## 🏆 Reward Function

The environment provides **dense, shaped rewards** to facilitate reinforcement learning:
*   **+0.3**: Correct classification of an email.
*   **+0.3**: Correct priority assignment.
*   **+0.5**: Successful resolution of an email.
*   **+0.4**: Bonus for resolving urgent emails before the halfway point of `max_steps`.
*   **-0.2**: Penalty for incorrect labels.
*   **-0.5**: Heavy penalty for ignoring or incorrectly handling urgent complaints.

---

## 🤖 Baseline Agent (`inference.py`)

A reference implementation is provided in `inference.py`. It features:
*   **Multi-Provider Fallback:** Uses a Primary AI (Hugging Face) with a secret Internal Secondary AI fallback for high reliability.
*   **Stateful Memory:** Tracks which emails have already been handled to avoid redundant actions.
*   **Smart Fallback:** A keyword-based heuristic engine triggers if the LLM fails repeatedly or hits rate limits.
*   **Deterministic Logic:** Uses `temperature=0.05` and strict JSON outputs.

---

## 🛠️ Setup Instructions

### 1. Clone & Install
```bash
git clone https://github.com/shubhamos-ai/meta-openenv
cd meta-openenv
pip install -r requirements.txt
```

### 2. Configure Secrets
Create a `.env` file in the root directory:
```bash
HF_TOKEN=hf_...
INTERNAL_AI_KEY=nvapi-...
```
> [!TIP]
> On Hugging Face, add these as **Secrets** in the Space settings to ensure high-performance inference fallback is active.

---

## ▶️ Running the Environment

### Run Baseline Agent
```bash
# Run Easy task (default)
python3 inference.py --task easy

# Run Medium task
python3 inference.py --task medium --verbose

# Run All tasks and save results
python3 inference.py --task all --output results.json
```

### Run E2E Validation
SHUBHAMOS includes a validation suite to verify environment health and agent performance:
```bash
chmod +x tests/e2e_runner.sh
./tests/e2e_runner.sh
```

---

## 🐳 Docker & Deployment

### Local Docker Run
```bash
docker build -t shubhamos .
docker run -p 7860:7860 --env-file .env shubhamos
```

### Hugging Face Spaces
1.  Create a new **Docker** Space on Hugging Face.
2.  Select the **Empty** template or push this repository directly.
3.  Add `HF_TOKEN` and `INTERNAL_AI_KEY` under **Settings > Variables and Secrets**.
4.  Deployment will automatically start using the included `Dockerfile`.

---

## 📁 Project Structure

```text
├── environment.py      # Core OpenEnv logic
├── models.py           # Pydantic state/action models
├── reward.py           # Reward signal engine
├── tasks/              # Task configurations (Easy/Medium/Hard)
├── graders/            # Deterministic scoring logic
├── inference.py        # Baseline LLM Agent
├── openenv.yaml        # OpenEnv Spec Manifest
├── .env                # Private secrets (git-ignored)
└── tests/              # E2E validation scripts
```

---

## 💡 Design Decisions
*   **Determinism:** Fixed seeds and explicit graders ensure that agent improvements are real, not noise.
*   **JSON-First:** Agent communication is forced into pure JSON to minimize parsing variability.
*   **Observability:** Every step is logged with associated rewards and state transitions for easy debugging.

---

## 🚀 Training Purpose
SHUBHAMOS is designed for **Reward-Driven Optimization**. The dense rewards allow for:
*   **Proximal Policy Optimization (PPO)** for triage strategy.
*   **Few-Shot Tuning** of LLM system prompts.
*   **Fine-Tuning** of small models (e.g., Llama-3-8B) on the generated triage trajectories.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

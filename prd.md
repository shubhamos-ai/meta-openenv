# 📄 Product Requirements Document (PRD)

## 🏷️ Product Name

**AI Email Operations & Triage Environment (OpenEnv)**

---

## 🎯 Objective

Build a production-grade OpenEnv-compatible environment that simulates real-world email inbox management workflows. This environment will allow AI agents to interact via `step()`, `reset()`, and `state()` APIs to classify, prioritize, respond to, and resolve emails efficiently.

The system is designed to evaluate agent performance on real-world operational tasks such as customer support triage, enterprise email handling, and workflow automation.

---

## 🌍 Problem Statement

Modern organizations receive large volumes of emails that require manual processing:

* Categorization (spam, billing, support, urgent)
* Prioritization
* Response drafting
* Escalation handling

This process is time-consuming and error-prone. There is a need for a standardized environment to train and evaluate AI agents on these workflows.

---

## 💡 Solution Overview

We will simulate an email operations system where:

* Emails arrive dynamically
* Each email has attributes (content, sentiment, urgency)
* An AI agent performs actions to manage the inbox

The environment provides:

* Structured observations
* Action-based interactions
* Reward feedback
* Task-based evaluation

---

## 👤 Target Users

* AI/ML researchers
* RL engineers
* LLM agent developers
* Hackathon participants
* Organizations evaluating automation systems

---

## 🧩 Core Features

### 1. Email Simulation Engine

* Generates realistic email data
* Includes multiple categories:

  * Spam
  * General inquiry
  * Billing issue
  * Urgent complaint

---

### 2. OpenEnv Interface

Implements:

* `reset()` → Initialize environment
* `step(action)` → Execute action and return results
* `state()` → Return full internal state

---

### 3. Action System

Supported actions:

* classify_email(email_id, category)
* set_priority(email_id, level)
* draft_reply(email_id, text)
* mark_resolved(email_id)
* escalate_email(email_id)
* ignore_email(email_id)

---

### 4. Observation System

Provides:

* List of emails with metadata
* Current system stats
* Pending and resolved counts
* Time progression

---

### 5. Reward Engine

Dense reward system:

* Positive rewards for:

  * Correct classification
  * Proper prioritization
  * Efficient resolution
* Negative rewards for:

  * Errors
  * Delays
  * Ignoring urgent emails

---

### 6. Task System

Three difficulty levels:

#### 🟢 Easy — Basic Inbox

* Small dataset
* Clear categories

#### 🟡 Medium — Support Queue

* Moderate volume
* Mixed priorities

#### 🔴 Hard — Enterprise Inbox

* High volume
* Ambiguous cases
* Requires strategic decision-making

---

### 7. Grading System

Each task includes a deterministic grader:

* Outputs score from 0.0 to 1.0
* Based on:

  * Accuracy
  * Efficiency
  * Resolution rate

---

### 8. Baseline Agent

* Uses OpenAI-compatible API
* Executes actions step-by-step
* Produces reproducible scores

---

## 🧠 Functional Requirements

* Must comply with OpenEnv specification
* Must use typed Pydantic models
* Must support reproducible tasks via seeding
* Must provide meaningful reward signals
* Must include at least 3 tasks with graders

---

## ⚙️ Non-Functional Requirements

* Runs within:

  * 2 vCPU
  * 8GB RAM
* Execution time < 20 minutes
* Dockerized environment
* Deployable on Hugging Face Spaces

---

## 📦 System Architecture

```
Agent (LLM)
   ↓
OpenEnv API (step/reset/state)
   ↓
Environment Engine
   ↓
State + Reward + Tasks
   ↓
Grader Evaluation
```

---

## 📁 Project Structure

```
email-openenv/
├── openenv.yaml
├── models.py
├── environment.py
├── reward.py
├── tasks/
├── graders/
├── inference.py
├── Dockerfile
└── README.md
```

---

## 📊 Success Metrics

* Accurate classification rate
* Priority assignment accuracy
* Email resolution rate
* Time efficiency
* Final grader score (0.0–1.0)

---

## 🚀 Future Enhancements

* Multi-agent collaboration
* Voice/email hybrid system
* Real-time dashboard visualization
* Integration with real email APIs

---

## ⚠️ Risks & Mitigations

| Risk                      | Mitigation                  |
| ------------------------- | --------------------------- |
| Over-simplified emails    | Use varied templates        |
| Reward exploitation       | Add penalties + constraints |
| Non-deterministic grading | Use fixed seeds             |

---

## 🏁 Conclusion

This project delivers a realistic, scalable, and evaluation-ready environment for training AI agents in email operations. It aligns with real-world workflows and provides meaningful benchmarking for agent performance.

---

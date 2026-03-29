---
wave: 1
depends_on: []
files_modified: [models.py]
autonomous: true
requirements_addressed: [OENV-04, EMAIL-01, EMAIL-02, EMAIL-03, EMAIL-04, EMAIL-05, EMAIL-06, EMAIL-07]
must_haves:
  - models.py exists with all typed Pydantic v2 models
  - EmailCategory, Priority, Sentiment literals defined
  - Email, ObservationEmail, Action, Observation, State, Info models defined
  - All models are JSON-serializable
  - gt_category and gt_priority in Email (ground truth, hidden from agent)
---

# Plan 01: models.py — Typed Pydantic Models

## Objective
Define all Pydantic v2 typed data models that form the data contract for the entire SHUBHAMOS environment. Every other module imports from here.

## Tasks

### Task 1: Create models.py with all typed models
<task>
<read_first>
- .planning/phases/01-core-environment-models/01-CONTEXT.md — decisions D-01 through D-10
- .planning/REQUIREMENTS.md — OENV-04, EMAIL-01 to EMAIL-07
</read_first>
<action>
Create `models.py` in the project root with this exact content:

```python
"""
SHUBHAMOS: AI Email Operations & Triage Environment
models.py — All typed Pydantic v2 data models

These models define the data contract between environment, agents, and graders.
- Email: full internal representation with ground truth labels
- ObservationEmail: agent-facing truncated view (no ground truth)
- Action: structured agent action with type dispatch
- Observation: what the agent receives each step
- State: full internal state (includes ground truth, used by graders)
- Info: per-step metadata dict
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ── Type Aliases ──────────────────────────────────────────────────────────────

EmailCategory = Literal["spam", "general_inquiry", "billing_issue", "urgent_complaint"]
Priority = Literal["low", "medium", "high", "unknown"]
Sentiment = Literal["positive", "neutral", "negative"]
ActionType = Literal[
    "classify_email",
    "set_priority",
    "draft_reply",
    "mark_resolved",
    "escalate_email",
    "ignore_email",
]

# ── Internal Email Model (full, with ground truth) ─────────────────────────────

class Email(BaseModel):
    """Full internal email representation. Ground truth labels are stored here
    and never exposed to the agent via Observation."""

    id: str = Field(..., description="Unique email identifier")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Full email body text")
    sender: str = Field(..., description="Sender email address")
    timestamp: datetime = Field(..., description="Arrival timestamp")

    # Ground truth labels (hidden from agent)
    gt_category: EmailCategory = Field(..., description="True category for grading")
    gt_priority: Priority = Field(..., description="True priority for grading")
    sentiment: Sentiment = Field(..., description="Body sentiment")

    # Agent-assigned labels (start as None/unknown)
    category: Optional[EmailCategory] = Field(None, description="Agent-assigned category")
    priority: Priority = Field("unknown", description="Agent-assigned priority")

    # Status flags
    resolved: bool = Field(False, description="Marked resolved by agent")
    escalated: bool = Field(False, description="Escalated by agent")
    ignored: bool = Field(False, description="Ignored by agent")
    reply_drafted: bool = Field(False, description="Has a drafted reply")
    reply_text: Optional[str] = Field(None, description="Drafted reply text")

    def is_processed(self) -> bool:
        """True if email has been acted on terminally (resolved/escalated/ignored)."""
        return self.resolved or self.escalated or self.ignored

# ── Agent-Facing Email View (no ground truth) ─────────────────────────────────

class ObservationEmail(BaseModel):
    """Truncated email view exposed to the agent. No ground truth labels."""

    id: str
    subject: str
    sender: str
    timestamp: datetime
    sentiment: Sentiment
    body_preview: str = Field(..., description="First 200 chars of body")
    category: Optional[EmailCategory] = Field(None, description="Agent-assigned category so far")
    priority: Priority = Field("unknown", description="Agent-assigned priority so far")
    resolved: bool = False
    escalated: bool = False
    ignored: bool = False
    reply_drafted: bool = False

# ── Action Model ──────────────────────────────────────────────────────────────

class Action(BaseModel):
    """Structured agent action. action_type determines which fields are used."""

    action_type: ActionType = Field(..., description="Type of action to perform")
    email_id: str = Field(..., description="Target email ID")
    # Optional payload fields (used depending on action_type)
    category: Optional[EmailCategory] = Field(None, description="For classify_email")
    level: Optional[Priority] = Field(None, description="For set_priority")
    text: Optional[str] = Field(None, description="For draft_reply")

# ── Observation Model (returned by step/reset) ────────────────────────────────

class Observation(BaseModel):
    """What the agent receives after each step or on reset."""

    emails: List[ObservationEmail] = Field(..., description="Current inbox state")
    total_emails: int = Field(..., description="Total emails in this episode")
    pending_count: int = Field(..., description="Emails not yet processed")
    resolved_count: int = Field(..., description="Emails marked resolved")
    escalated_count: int = Field(..., description="Emails escalated")
    step_count: int = Field(..., description="Current step number")
    max_steps: int = Field(..., description="Maximum steps allowed")
    elapsed_ratio: float = Field(..., description="step_count / max_steps, 0.0–1.0")

# ── Internal State (full, used by graders) ────────────────────────────────────

class State(BaseModel):
    """Complete internal environment state including ground truth. Used by graders."""

    emails: List[Email] = Field(..., description="All emails with ground truth labels")
    action_history: List[Dict[str, Any]] = Field(default_factory=list)
    step_count: int = 0
    max_steps: int = 0
    done: bool = False
    total_reward: float = 0.0
    seed: int = 0
    task_id: str = ""

# ── Step Info Dict ─────────────────────────────────────────────────────────────

class StepInfo(BaseModel):
    """Metadata returned in the info dict from step()."""

    action_type: str
    email_id: str
    valid: bool
    error: Optional[str] = None
    step_reward: float = 0.0
```
</action>
<acceptance_criteria>
- [ ] `models.py` exists in project root
- [ ] `grep -n "class Email" models.py` returns a match
- [ ] `grep -n "gt_category" models.py` returns a match (ground truth field exists)
- [ ] `grep -n "class ObservationEmail" models.py` returns a match with no gt_ fields
- [ ] `grep -n "class Action" models.py` returns a match with action_type field
- [ ] `grep -n "class Observation" models.py` returns a match with emails list
- [ ] `grep -n "class State" models.py` returns a match with action_history
- [ ] `python3 -c "from models import Email, Action, Observation, State, ObservationEmail"` exits 0
- [ ] `python3 -c "from models import EmailCategory, Priority, Sentiment"` exits 0
</acceptance_criteria>
</task>

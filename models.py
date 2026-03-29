"""
SHUBHAMOS: AI Email Operations & Triage Environment
models.py — All typed Pydantic v2 data models

These models define the data contract between environment, agents, and graders.
- Email: full internal representation with ground truth labels
- ObservationEmail: agent-facing truncated view (no ground truth)
- Action: structured agent action with type dispatch
- Observation: what the agent receives each step
- State: full internal state (includes ground truth, used by graders)
- StepInfo: per-step metadata
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ── Type Aliases ───────────────────────────────────────────────────────────────

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

    id: str = Field(..., description="Unique email identifier e.g. 'email_001'")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Full email body text")
    sender: str = Field(..., description="Sender email address")
    timestamp: datetime = Field(..., description="Arrival timestamp")

    # Ground truth labels — hidden from agent, used by graders
    gt_category: EmailCategory = Field(..., description="True category for grading")
    gt_priority: Priority = Field(..., description="True priority for grading (no 'unknown')")
    sentiment: Sentiment = Field(..., description="Body sentiment")

    # Agent-assigned labels (start as None / unknown)
    category: Optional[EmailCategory] = Field(None, description="Agent-assigned category")
    priority: Priority = Field("unknown", description="Agent-assigned priority")

    # Status flags (mutually exclusive terminal states: resolved/escalated/ignored)
    resolved: bool = Field(False, description="Marked resolved by agent")
    escalated: bool = Field(False, description="Escalated by agent")
    ignored: bool = Field(False, description="Ignored by agent")
    reply_drafted: bool = Field(False, description="Reply has been drafted")
    reply_text: Optional[str] = Field(None, description="Drafted reply text")

    def is_processed(self) -> bool:
        """True if email has been terminally acted on (resolved/escalated/ignored)."""
        return self.resolved or self.escalated or self.ignored


# ── Agent-Facing Email View (no ground truth) ─────────────────────────────────

class ObservationEmail(BaseModel):
    """Truncated email view exposed to the agent. Contains no ground truth labels."""

    id: str
    subject: str
    sender: str
    timestamp: datetime
    sentiment: Sentiment
    body_preview: str = Field(..., description="First 200 chars of body only")
    category: Optional[EmailCategory] = Field(None, description="Agent-assigned category so far")
    priority: Priority = Field("unknown", description="Agent-assigned priority so far")
    resolved: bool = False
    escalated: bool = False
    ignored: bool = False
    reply_drafted: bool = False


# ── Action Model ───────────────────────────────────────────────────────────────

class Action(BaseModel):
    """Structured agent action. action_type determines which payload fields apply.

    Action types and their required fields:
    - classify_email: email_id, category (required)
    - set_priority:   email_id, level (required)
    - draft_reply:    email_id, text (required)
    - mark_resolved:  email_id only
    - escalate_email: email_id only
    - ignore_email:   email_id only
    """

    action_type: ActionType = Field(..., description="Which action to perform")
    email_id: str = Field(..., description="Target email ID")
    category: Optional[EmailCategory] = Field(None, description="Used by classify_email")
    level: Optional[Priority] = Field(None, description="Used by set_priority")
    text: Optional[str] = Field(None, description="Used by draft_reply")


# ── Observation Model (returned by step/reset) ────────────────────────────────

class Observation(BaseModel):
    """What the agent sees after each step or on reset. No ground truth."""

    emails: List[ObservationEmail] = Field(..., description="Current inbox state")
    total_emails: int = Field(..., description="Total emails in this episode")
    pending_count: int = Field(..., description="Emails not yet terminally processed")
    resolved_count: int = Field(..., description="Emails successfully resolved")
    escalated_count: int = Field(..., description="Emails escalated")
    ignored_count: int = Field(..., description="Emails ignored")
    step_count: int = Field(..., description="Steps taken so far (0-indexed at reset)")
    max_steps: int = Field(..., description="Maximum steps before forced termination")
    elapsed_ratio: float = Field(..., description="step_count / max_steps, 0.0 to 1.0")


# ── Internal State (complete, used by graders) ────────────────────────────────

class State(BaseModel):
    """Complete internal environment state including ground truth. Graders use this."""

    emails: List[Email] = Field(..., description="All emails with ground truth labels")
    action_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Ordered list of all actions taken this episode"
    )
    step_count: int = Field(0, description="Steps taken in current episode")
    max_steps: int = Field(0, description="Max steps for current task")
    done: bool = Field(False, description="Whether episode has terminated")
    total_reward: float = Field(0.0, description="Cumulative reward this episode")
    seed: int = Field(0, description="Random seed used for this episode")
    task_id: str = Field("", description="Task identifier: easy / medium / hard")


# ── Per-Step Info ─────────────────────────────────────────────────────────────

class StepInfo(BaseModel):
    """Structured info returned in the info dict from step()."""

    action_type: str = Field(..., description="Action that was applied")
    email_id: str = Field(..., description="Email that was targeted")
    valid: bool = Field(..., description="Whether the action was valid")
    error: Optional[str] = Field(None, description="Error message if invalid")
    step_reward: float = Field(0.0, description="Reward earned this step")
    done: bool = Field(False, description="Whether episode ended after this step")

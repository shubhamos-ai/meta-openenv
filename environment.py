"""
SHUBHAMOS: AI Email Operations & Triage Environment
environment.py — EmailTriageEnv OpenEnv-compliant environment class

Implements:
  reset(task_config) → Observation
  step(action)       → (Observation, float, bool, dict)
  state()            → State
"""

from __future__ import annotations
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from models import (
    Action,
    ActionType,
    Email,
    EmailCategory,
    Observation,
    ObservationEmail,
    Priority,
    Sentiment,
    State,
    StepInfo,
)

# ── Seed data for realistic email generation ────────────────────────────────────

_SENDERS = [
    "alice.johnson@acmecorp.com",
    "bob.smith@enterprise.io",
    "support@bigclient.net",
    "billing@financeops.com",
    "ceo@urgentco.org",
    "info@spamblaster.biz",
    "noreply@marketing.cloud",
    "james.t@retailpartner.com",
    "helpdesk@internal.corp",
    "carol.w@medicalgroup.org",
]

_SUBJECTS_BY_CATEGORY: Dict[EmailCategory, List[str]] = {
    "spam": [
        "You've won a $500 gift card!",
        "URGENT: Claim your prize now",
        "Free iPhone — limited offer",
        "Make money from home — guaranteed",
        "Your account has been selected!",
    ],
    "general_inquiry": [
        "Question about your services",
        "Request for product information",
        "Partnership inquiry",
        "Media inquiry regarding your company",
        "How do I get started?",
        "Can you help me understand your pricing?",
    ],
    "billing_issue": [
        "Invoice discrepancy — please review",
        "Double charged on my account",
        "Refund request for order #44821",
        "Payment failed — what do I do?",
        "Billing error on last statement",
        "I was overcharged this month",
    ],
    "urgent_complaint": [
        "URGENT: Service outage affecting my business",
        "Complete system failure — need immediate help",
        "Critical bug causing data loss",
        "Unacceptable service — legal action pending",
        "Production down — customers impacted",
    ],
}

_BODIES_BY_CATEGORY: Dict[EmailCategory, List[str]] = {
    "spam": [
        "Congratulations! You have been selected to receive a $500 gift card. Click here to claim your reward before it expires in 24 hours. No purchase necessary. Act now!",
        "We have a special offer just for you! Make $5000/week from the comfort of your home. No experience needed. Join thousands of successful members. Click to get started today!",
        "LIMITED TIME OFFER: You have been pre-approved for a FREE iPhone 15 Pro. Simply complete a short survey and the device will be shipped to your door. Claim now!",
        "Your email was randomly selected for our VIP program. As a VIP member you get access to exclusive deals, cash prizes, and luxury vacations. Join for free today!",
    ],
    "general_inquiry": [
        "Hello, I came across your company online and I'm interested in learning more about your product offerings. Could you please send me a product catalog and pricing information? I'm particularly interested in your enterprise solutions. Thank you for your time.",
        "Hi there, I'm evaluating potential vendors for our upcoming project and your company came highly recommended. I'd love to schedule a 30-minute call to discuss how you might be able to help us. What's your availability this week?",
        "I'm a journalist writing an article about innovation in your industry. I would love to get a quote from your team about recent developments. Could you connect me with your PR contact? Deadline is Friday.",
        "We are a small business looking to expand our operations and are interested in your services. Before we proceed, I have a few questions about your support model and SLA commitments. Can someone from your sales team reach out?",
        "Hello, I recently attended your webinar on digital transformation and had a few follow-up questions. Could you share the recording and slide deck? Also, I'd love to speak with a product specialist about implementation timelines.",
    ],
    "billing_issue": [
        "I received my invoice for last month and I believe there is an error. I was charged $1,200 but my contract clearly states the monthly fee is $950. Can you please review and send a corrected invoice as soon as possible? Invoice #INV-2024-0892.",
        "I was double charged on March 15th. My bank statement shows two transactions of $299 from your company. Please refund one of these charges immediately. I can provide bank statement screenshots if needed. This needs to be resolved urgently.",
        "I would like to request a refund for my recent purchase (Order #44821). I was charged for a premium plan but I never actually used the service. Per your refund policy, I should be eligible for a full refund within 30 days. Please process this ASAP.",
        "My credit card payment failed but I was still charged. I now see a pending charge of $450 on my card but I never received a confirmation. Can you check your system and either confirm the payment was received or release the hold?",
        "There is a discrepancy on my account statement. I was on the $99/month plan but was charged $149 this cycle. I did not authorize any plan upgrade. Please revert this change and refund the difference of $50.",
    ],
    "urgent_complaint": [
        "Our production environment has been down for the past 2 hours and your support team has been completely unresponsive. This is causing significant financial losses for our company — approximately $10,000 per hour. We have 500+ customers impacted and I need an immediate response. If this isn't resolved in the next hour we will be forced to seek an emergency injunction.",
        "I am writing to formally complain about the catastrophic failure of your service last night. Our entire database was corrupted due to what appears to be a bug in your latest update. We lost 3 days worth of data that cannot be recovered. Our legal team is reviewing our options. I expect a formal response within 24 hours.",
        "CRITICAL: Your system has been sending duplicate notifications to all our users for the last 4 hours. Our customers are furious and several have already cancelled their subscriptions. I have escalated this internally to our CEO. Your on-call team needs to fix this immediately. I am requesting a full incident report within 48 hours.",
        "I have been waiting 3 weeks for my issue to be resolved and I am at the end of my patience. Every time I contact support I get a different answer. This is completely unacceptable for an enterprise customer paying $50,000/year. I am now involving our procurement department to review the contract renewal.",
    ],
}

_SENTIMENT_BY_CATEGORY: Dict[EmailCategory, Sentiment] = {
    "spam": "neutral",
    "general_inquiry": "positive",
    "billing_issue": "negative",
    "urgent_complaint": "negative",
}

_PRIORITY_BY_CATEGORY: Dict[EmailCategory, Priority] = {
    "spam": "low",
    "general_inquiry": "medium",
    "billing_issue": "medium",
    "urgent_complaint": "high",
}

# Occasional overrides for variety
_PRIORITY_OVERRIDES = {
    "billing_issue": {"high": 0.3, "medium": 0.7},  # 30% chance of high priority billing
    "general_inquiry": {"low": 0.2, "medium": 0.8},
}


def _generate_emails(count: int, seed: int) -> List[Email]:
    """Generate a deterministic list of realistic emails using the given seed."""
    rng = random.Random(seed)

    # Category distribution
    categories: List[EmailCategory] = ["spam", "general_inquiry", "billing_issue", "urgent_complaint"]
    weights = [0.2, 0.35, 0.3, 0.15]

    emails: List[Email] = []
    base_ts = datetime(2024, 3, 1, 9, 0, 0, tzinfo=timezone.utc)

    for i in range(count):
        category: EmailCategory = rng.choices(categories, weights=weights, k=1)[0]

        # Pick subject and body
        subject = rng.choice(_SUBJECTS_BY_CATEGORY[category])
        body = rng.choice(_BODIES_BY_CATEGORY[category])
        sender = rng.choice(_SENDERS)

        # Timestamp spread over 5 business days
        offset_minutes = rng.randint(0, 5 * 8 * 60)
        ts = base_ts.replace(
            minute=base_ts.minute + offset_minutes % 60,
            hour=base_ts.hour + (offset_minutes // 60) % 8,
        )

        # Priority (with occasional overrides for realism)
        if category in _PRIORITY_OVERRIDES:
            opts = _PRIORITY_OVERRIDES[category]
            priority_labels = list(opts.keys())
            priority_weights = list(opts.values())
            gt_priority: Priority = rng.choices(priority_labels, weights=priority_weights, k=1)[0]
        else:
            gt_priority = _PRIORITY_BY_CATEGORY[category]

        sentiment: Sentiment = _SENTIMENT_BY_CATEGORY[category]

        emails.append(Email(
            id=f"email_{i+1:03d}",
            subject=subject,
            body=body,
            sender=sender,
            timestamp=ts,
            gt_category=category,
            gt_priority=gt_priority,
            sentiment=sentiment,
        ))

    return emails


class EmailTriageEnv:
    """
    SHUBHAMOS OpenEnv-compliant environment for email triage.

    Usage:
        env = EmailTriageEnv()
        obs = env.reset(task_config)
        for _ in range(max_steps):
            action = agent.act(obs)
            obs, reward, done, info = env.step(action)
            if done:
                break
        final_state = env.state()
    """

    def __init__(self) -> None:
        self._emails: List[Email] = []
        self._step_count: int = 0
        self._max_steps: int = 0
        self._done: bool = False
        self._total_reward: float = 0.0
        self._action_history: List[Dict[str, Any]] = []
        self._seed: int = 0
        self._task_id: str = ""
        self._initialized: bool = False

        # Import reward engine lazily to allow Phase 2 to plug in
        self._reward_engine = None

    # ── Public OpenEnv API ────────────────────────────────────────────────────

    def reset(self, task_config: Dict[str, Any]) -> Observation:
        """
        Reset the environment for a new episode.

        Args:
            task_config: Dict with keys:
                - seed (int): random seed for reproducibility
                - email_count (int): number of emails to generate
                - max_steps (int): episode step limit
                - task_id (str, optional): "easy"/"medium"/"hard"

        Returns:
            Observation: initial state visible to agent
        """
        self._seed = int(task_config.get("seed", 42))
        email_count = int(task_config.get("email_count", 8))
        self._max_steps = int(task_config.get("max_steps", 50))
        self._task_id = str(task_config.get("task_id", "easy"))

        # Seed Python stdlib RNG for any stochastic resets
        random.seed(self._seed)

        # Generate deterministic email set
        self._emails = _generate_emails(email_count, self._seed)
        self._step_count = 0
        self._done = False
        self._total_reward = 0.0
        self._action_history = []
        self._initialized = True

        return self._build_observation()

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """
        Apply an action to the environment.

        Args:
            action: Action object with action_type and email_id (+ optional payload)

        Returns:
            (observation, reward, done, info)
        """
        if not self._initialized:
            raise RuntimeError("Call reset() before step()")
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        # Validate action
        valid, error_msg = self._validate_action(action)

        step_reward = 0.0
        if valid:
            # Dispatch action to update email state
            self._dispatch_action(action)

            # Calculate reward (reward engine plugged in by Phase 2)
            if self._reward_engine is not None:
                step_reward = self._reward_engine.score_action(action, self._emails)
            else:
                # Stub reward: small negative to incentivize efficiency
                step_reward = -0.01

        # Increment step
        self._step_count += 1
        self._total_reward += step_reward

        # Record action history
        self._action_history.append({
            "step": self._step_count,
            "action_type": action.action_type,
            "email_id": action.email_id,
            "valid": valid,
            "error": error_msg,
            "reward": step_reward,
        })

        # Check termination (D-13)
        all_processed = all(e.is_processed() for e in self._emails)
        step_limit_reached = self._step_count >= self._max_steps
        self._done = all_processed or step_limit_reached

        obs = self._build_observation()
        info = StepInfo(
            action_type=action.action_type,
            email_id=action.email_id,
            valid=valid,
            error=error_msg,
            step_reward=step_reward,
            done=self._done,
        ).model_dump()

        return obs, step_reward, self._done, info

    def state(self) -> State:
        """
        Return the complete internal state including ground truth labels.
        Used by graders — never expose this to the agent during evaluation.
        """
        return State(
            emails=list(self._emails),
            action_history=list(self._action_history),
            step_count=self._step_count,
            max_steps=self._max_steps,
            done=self._done,
            total_reward=self._total_reward,
            seed=self._seed,
            task_id=self._task_id,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _validate_action(self, action: Action) -> Tuple[bool, Optional[str]]:
        """Validate action target and required payload fields."""
        # Check email exists
        email = self._find_email(action.email_id)
        if email is None:
            return False, f"Email '{action.email_id}' not found in inbox"

        # Check email is not already terminally processed
        if email.is_processed():
            return False, f"Email '{action.email_id}' is already processed (resolved/escalated/ignored)"

        # Payload validation
        if action.action_type == "classify_email" and action.category is None:
            return False, "classify_email requires 'category' field"
        if action.action_type == "set_priority" and action.level is None:
            return False, "set_priority requires 'level' field"
        if action.action_type == "draft_reply" and (action.text is None or not action.text.strip()):
            return False, "draft_reply requires non-empty 'text' field"

        return True, None

    def _dispatch_action(self, action: Action) -> None:
        """Mutate email state based on action type."""
        email = self._find_email(action.email_id)
        if email is None:
            return

        if action.action_type == "classify_email":
            email.category = action.category

        elif action.action_type == "set_priority":
            email.priority = action.level

        elif action.action_type == "draft_reply":
            email.reply_drafted = True
            email.reply_text = action.text

        elif action.action_type == "mark_resolved":
            email.resolved = True

        elif action.action_type == "escalate_email":
            email.escalated = True

        elif action.action_type == "ignore_email":
            email.ignored = True

    def _find_email(self, email_id: str) -> Optional[Email]:
        """Find an email by ID or return None."""
        for e in self._emails:
            if e.id == email_id:
                return e
        return None

    def _build_observation(self) -> Observation:
        """Build the agent-facing Observation from current internal state."""
        obs_emails = []
        for e in self._emails:
            obs_emails.append(ObservationEmail(
                id=e.id,
                subject=e.subject,
                sender=e.sender,
                timestamp=e.timestamp,
                sentiment=e.sentiment,
                body_preview=e.body[:200],  # D-08: 200-char limit
                category=e.category,
                priority=e.priority,
                resolved=e.resolved,
                escalated=e.escalated,
                ignored=e.ignored,
                reply_drafted=e.reply_drafted,
            ))

        resolved_count = sum(1 for e in self._emails if e.resolved)
        escalated_count = sum(1 for e in self._emails if e.escalated)
        ignored_count = sum(1 for e in self._emails if e.ignored)
        pending_count = len(self._emails) - resolved_count - escalated_count - ignored_count

        elapsed_ratio = (
            self._step_count / self._max_steps if self._max_steps > 0 else 0.0
        )

        return Observation(
            emails=obs_emails,
            total_emails=len(self._emails),
            pending_count=pending_count,
            resolved_count=resolved_count,
            escalated_count=escalated_count,
            ignored_count=ignored_count,
            step_count=self._step_count,
            max_steps=self._max_steps,
            elapsed_ratio=elapsed_ratio,
        )

    def attach_reward_engine(self, engine: Any) -> None:
        """Attach a reward engine (called by Phase 2). engine must implement score_action()."""
        self._reward_engine = engine

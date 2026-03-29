"""
SHUBHAMOS: AI Email Operations & Triage Environment
reward.py — Dense reward engine (Phase 2)

Computes step-level rewards based on agent actions vs. ground truth labels.
Attached to EmailTriageEnv via env.attach_reward_engine(RewardEngine()).

Reward design:
  Positive signals (agent did something correct):
    +0.3  — correct category classification
    +0.3  — correct priority assignment
    +0.5  — email resolved successfully
    +0.4  — urgent complaint resolved (bonus)
    +0.1  — relevant reply drafted for billing/urgent

  Negative signals (agent did something wrong):
    -0.2  — wrong category
    -0.2  — wrong priority
    -0.5  — urgent complaint ignored
    -0.3  — spam resolved (wasted effort — should be ignored)
    -0.01 — per-step cost (encourages efficiency)
"""

from __future__ import annotations
from typing import List, Optional

from models import Action, Email


class RewardEngine:
    """
    Stateless step-level reward calculator.

    Usage:
        engine = RewardEngine()
        env.attach_reward_engine(engine)
    """

    # ── Reward constants ──────────────────────────────────────────────────────

    CORRECT_CATEGORY = +0.30
    WRONG_CATEGORY = -0.20

    CORRECT_PRIORITY = +0.30
    WRONG_PRIORITY = -0.20

    RESOLVE_BONUS = +0.50
    URGENT_RESOLVE_BONUS = +0.40  # extra bonus on top of RESOLVE_BONUS

    IGNORE_URGENT_PENALTY = -0.50
    RESOLVE_SPAM_PENALTY = -0.30  # spam should be ignored, not resolved

    REPLY_BONUS = +0.10  # drafted reply before resolve (billing/urgent)

    STEP_COST = -0.01   # encourages faster resolution

    def score_action(self, action: Action, emails: List[Email]) -> float:
        """
        Calculate the reward for a single action.

        Args:
            action: the action just dispatched
            emails: the full email list (with ground truth)

        Returns:
            float reward value (may be positive, negative, or zero)
        """
        reward = self.STEP_COST  # always pay step cost

        target = self._find(emails, action.email_id)
        if target is None:
            return reward  # invalid action (no email found) — already penalised by step cost

        if action.action_type == "classify_email":
            reward += self._score_classify(action, target)

        elif action.action_type == "set_priority":
            reward += self._score_priority(action, target)

        elif action.action_type == "mark_resolved":
            reward += self._score_resolve(target)

        elif action.action_type == "ignore_email":
            reward += self._score_ignore(target)

        elif action.action_type == "draft_reply":
            reward += self._score_reply(target)

        # escalate_email: neutral reward — no bonus/penalty by default
        # (graders score it based on whether escalation was warranted)

        return round(reward, 4)

    # ── Action scorers ────────────────────────────────────────────────────────

    def _score_classify(self, action: Action, email: Email) -> float:
        if action.category == email.gt_category:
            return self.CORRECT_CATEGORY
        return self.WRONG_CATEGORY

    def _score_priority(self, action: Action, email: Email) -> float:
        if action.level == email.gt_priority:
            return self.CORRECT_PRIORITY
        return self.WRONG_PRIORITY

    def _score_resolve(self, email: Email) -> float:
        r = self.RESOLVE_BONUS

        # Penalise resolving spam (should be ignored instead)
        if email.gt_category == "spam":
            return self.RESOLVE_SPAM_PENALTY

        # Extra bonus for resolving urgent complaints
        if email.gt_category == "urgent_complaint":
            r += self.URGENT_RESOLVE_BONUS

        # Bonus if a reply was drafted before resolving (billing + urgent)
        if email.gt_category in ("billing_issue", "urgent_complaint") and email.reply_drafted:
            r += self.REPLY_BONUS

        return r

    def _score_ignore(self, email: Email) -> float:
        if email.gt_category == "urgent_complaint":
            return self.IGNORE_URGENT_PENALTY
        # Ignoring spam is correct — small positive (avoids step cost effectively)
        if email.gt_category == "spam":
            return +0.20
        return 0.0  # neutral for other categories

    def _score_reply(self, email: Email) -> float:
        # Reward for drafting a reply on billing/urgent (proactive)
        if email.gt_category in ("billing_issue", "urgent_complaint"):
            return self.REPLY_BONUS
        return 0.0

    # ── Utility ───────────────────────────────────────────────────────────────

    @staticmethod
    def _find(emails: List[Email], email_id: str) -> Optional[Email]:
        for e in emails:
            if e.id == email_id:
                return e
        return None

"""
SHUBHAMOS: AI Email Operations & Triage Environment
graders/base_grader.py — Abstract base grader

All graders share the same deterministic scoring formula:
  score = classification_accuracy * 0.30
        + priority_accuracy        * 0.30
        + resolution_rate          * 0.30
        + urgent_handling          * 0.10

Graders inspect final State (ground truth visible) against agent actions.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..models import Email, State


class GradeReport:
    """Structured grading output."""

    def __init__(
        self,
        task_id: str,
        seed: int,
        total_emails: int,
        steps_used: int,
        max_steps: int,
        classification_accuracy: float,
        priority_accuracy: float,
        resolution_rate: float,
        urgent_handling: float,
        final_score: float,
        breakdown: Dict[str, Any],
        passed: bool,
    ) -> None:
        self.task_id = task_id
        self.seed = seed
        self.total_emails = total_emails
        self.steps_used = steps_used
        self.max_steps = max_steps
        self.classification_accuracy = classification_accuracy
        self.priority_accuracy = priority_accuracy
        self.resolution_rate = resolution_rate
        self.urgent_handling = urgent_handling
        self.final_score = final_score
        self.breakdown = breakdown
        self.passed = passed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "seed": self.seed,
            "total_emails": self.total_emails,
            "steps_used": self.steps_used,
            "max_steps": self.max_steps,
            "efficiency_ratio": round(1.0 - self.steps_used / max(self.max_steps, 1), 3),
            "scores": {
                "classification_accuracy": round(self.classification_accuracy, 4),
                "priority_accuracy": round(self.priority_accuracy, 4),
                "resolution_rate": round(self.resolution_rate, 4),
                "urgent_handling": round(self.urgent_handling, 4),
                "final_score": round(self.final_score, 4),
            },
            "passed": self.passed,
            "breakdown": self.breakdown,
        }

    def __repr__(self) -> str:
        status = "PASS ✓" if self.passed else "FAIL ✗"
        return (
            f"GradeReport({self.task_id} | {status} | "
            f"score={self.final_score:.3f} | {self.steps_used}/{self.max_steps} steps)"
        )


class BaseGrader(ABC):
    """
    Abstract grader. Subclasses may override component weights or thresholds.

    Usage:
        grader = EasyGrader()
        report = grader.grade(env.state())
        print(report.to_dict())
    """

    # Component weights — must sum to 1.0
    W_CLASSIFICATION = 0.30
    W_PRIORITY = 0.30
    W_RESOLUTION = 0.30
    W_URGENT = 0.10

    # Minimum score to pass (overridden by subclasses)
    PASS_THRESHOLD = 0.60

    def grade(self, state: State) -> GradeReport:
        """
        Grade a completed (or terminated) episode.

        Args:
            state: Final State from env.state() — includes ground truth labels

        Returns:
            GradeReport with per-component and final scores
        """
        emails = state.emails
        n = len(emails)

        if n == 0:
            return self._empty_report(state)

        # ── Component scores ─────────────────────────────────────────────────

        classification_acc = self._classification_accuracy(emails)
        priority_acc = self._priority_accuracy(emails)
        resolution_rate = self._resolution_rate(emails)
        urgent_score = self._urgent_handling_score(emails)

        # ── Weighted final score ─────────────────────────────────────────────

        final = (
            classification_acc * self.W_CLASSIFICATION
            + priority_acc * self.W_PRIORITY
            + resolution_rate * self.W_RESOLUTION
            + urgent_score * self.W_URGENT
        )
        final = min(1.0, max(0.0, final))

        # ── Breakdown (per-email detail) ──────────────────────────────────────

        breakdown = self._build_breakdown(emails, state)

        passed = final >= self.PASS_THRESHOLD

        return GradeReport(
            task_id=state.task_id,
            seed=state.seed,
            total_emails=n,
            steps_used=state.step_count,
            max_steps=state.max_steps,
            classification_accuracy=classification_acc,
            priority_accuracy=priority_acc,
            resolution_rate=resolution_rate,
            urgent_handling=urgent_score,
            final_score=final,
            breakdown=breakdown,
            passed=passed,
        )

    # ── Component scorers (deterministic) ────────────────────────────────────

    @staticmethod
    def _classification_accuracy(emails: List[Email]) -> float:
        """Fraction of emails correctly classified vs. ground truth."""
        classified = [e for e in emails if e.category is not None]
        if not classified:
            return 0.0
        correct = sum(1 for e in classified if e.category == e.gt_category)
        return correct / len(emails)  # denominator = ALL emails (not just classified)

    @staticmethod
    def _priority_accuracy(emails: List[Email]) -> float:
        """Fraction of emails with correct priority vs. ground truth."""
        prioritized = [e for e in emails if e.priority != "unknown"]
        if not prioritized:
            return 0.0
        correct = sum(1 for e in prioritized if e.priority == e.gt_priority)
        return correct / len(emails)

    @staticmethod
    def _resolution_rate(emails: List[Email]) -> float:
        """Fraction of non-spam emails that were resolved or appropriately escalated."""
        non_spam = [e for e in emails if e.gt_category != "spam"]
        if not non_spam:
            return 1.0

        handled = sum(
            1 for e in non_spam
            if e.resolved or (e.escalated and e.gt_category == "urgent_complaint")
        )
        # Partial credit: spam correctly ignored doesn't count against resolution rate
        return handled / len(non_spam)

    @staticmethod
    def _urgent_handling_score(emails: List[Email]) -> float:
        """
        Score for urgent complaint handling.
        Full credit: resolved or escalated.
        Zero credit: ignored or untouched.
        """
        urgent = [e for e in emails if e.gt_category == "urgent_complaint"]
        if not urgent:
            return 1.0  # no urgent emails → full marks by default

        handled = sum(1 for e in urgent if e.resolved or e.escalated)
        return handled / len(urgent)

    def _build_breakdown(self, emails: List[Email], state: State) -> Dict[str, Any]:
        """Build per-email breakdown for the grade report."""
        per_email = []
        for e in emails:
            per_email.append({
                "id": e.id,
                "subject": e.subject[:60],
                "gt_category": e.gt_category,
                "agent_category": e.category,
                "category_correct": e.category == e.gt_category,
                "gt_priority": e.gt_priority,
                "agent_priority": e.priority,
                "priority_correct": e.priority == e.gt_priority,
                "resolved": e.resolved,
                "escalated": e.escalated,
                "ignored": e.ignored,
                "reply_drafted": e.reply_drafted,
                "processed": e.is_processed(),
            })

        spam_emails = [e for e in emails if e.gt_category == "spam"]
        spam_ignored = sum(1 for e in spam_emails if e.ignored)

        return {
            "per_email": per_email,
            "total_steps": state.step_count,
            "total_reward": round(state.total_reward, 4),
            "spam_accuracy": f"{spam_ignored}/{len(spam_emails)} spam correctly ignored",
            "action_count": len(state.action_history),
        }

    def _empty_report(self, state: State) -> GradeReport:
        return GradeReport(
            task_id=state.task_id,
            seed=state.seed,
            total_emails=0,
            steps_used=state.step_count,
            max_steps=state.max_steps,
            classification_accuracy=0.0,
            priority_accuracy=0.0,
            resolution_rate=0.0,
            urgent_handling=0.0,
            final_score=0.0,
            breakdown={},
            passed=False,
        )

    @abstractmethod
    def task_name(self) -> str:
        ...

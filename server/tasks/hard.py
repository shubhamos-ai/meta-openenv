"""
SHUBHAMOS: AI Email Operations & Triage Environment
tasks/hard.py — Hard Task (seed=999, 50 emails, 300 steps)

Scenario: Enterprise inbox under fire.
High volume, high-urgency emails, spam noise, SLA pressure.
Tests agent resilience under pressure with tight efficiency requirements.
"""

from __future__ import annotations
from typing import Any, Dict


class HardTask:
    """
    Hard difficulty task.

    - 50 emails: high volume with significant noise
    - ~15% spam to filter efficiently
    - Multiple urgent_complaint threads requiring immediate resolution
    - Several billing disputes needing drafted replies
    - 300 max steps — must be efficient to cover all emails
    - Seed 999 — fixed for evaluation
    """

    task_id = "hard"
    seed = 999
    email_count = 50
    max_steps = 300
    difficulty = "hard"

    grading_thresholds = {
        "pass": 0.50,
        "good": 0.65,
        "excellent": 0.80,
    }

    @classmethod
    def config(cls) -> Dict[str, Any]:
        return {
            "task_id": cls.task_id,
            "seed": cls.seed,
            "email_count": cls.email_count,
            "max_steps": cls.max_steps,
            "difficulty": cls.difficulty,
        }

    @classmethod
    def description(cls) -> str:
        return (
            "Enterprise Inbox (Hard): 50 emails under high-pressure conditions. "
            "Tests resilience, prioritization, and efficiency. "
            f"Seed={cls.seed}, max_steps={cls.max_steps}."
        )

    @classmethod
    def grader_class(cls):
        from ..graders.hard_grader import HardGrader
        return HardGrader

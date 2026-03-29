"""
SHUBHAMOS: AI Email Operations & Triage Environment
tasks/medium.py — Medium Task (seed=123, 20 emails, 120 steps)

Scenario: A growing startup's support queue.
Mix of billing disputes, feature requests, and a few urgent complaints.
Agent must prioritize effectively to score well.
"""

from __future__ import annotations
from typing import Any, Dict


class MediumTask:
    """
    Medium difficulty task.

    - 20 emails: realistic mix with overlapping themes
    - 3-4 urgent complaints requiring immediate attention
    - 5-6 billing issues needing reply before resolution
    - Some spam to filter out
    - 120 max steps — tighter budget
    - Seed 123 — fixed for evaluation
    """

    task_id = "medium"
    seed = 123
    email_count = 20
    max_steps = 120
    difficulty = "medium"

    grading_thresholds = {
        "pass": 0.55,
        "good": 0.70,
        "excellent": 0.85,
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
            "Support Queue (Medium): 20 emails with mixed priorities. "
            "Agent must sequence actions strategically. "
            f"Seed={cls.seed}, max_steps={cls.max_steps}."
        )

    @classmethod
    def grader_class(cls):
        from graders.medium_grader import MediumGrader
        return MediumGrader

"""
SHUBHAMOS: AI Email Operations & Triage Environment
tasks/peaceful.py — Peaceful Task (seed=1, 3 emails, 20 steps)

Scenario: A quiet morning. Very few emails, all very clear.
The lowest possible entry point for any agent.
"""

from __future__ import annotations
from typing import Any, Dict


class PeacefulTask:
    """
    Peaceful difficulty task.
    - 3 emails: 1 inquiry, 1 billing, 1 resolved already (baseline test)
    - 20 max steps
    - Seed 1
    """

    task_id = "peaceful"
    seed = 1
    email_count = 3
    max_steps = 20
    difficulty = "peaceful"

    grading_thresholds = {
        "pass": 0.50,
        "good": 0.80,
        "excellent": 1.0,
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
            "Peaceful Inbox: 3 emails, very low noise. Baseline verification. "
            f"Seed={cls.seed}, max_steps={cls.max_steps}."
        )

    @classmethod
    def grader_class(cls):
        from ..graders.peaceful_grader import PeacefulGrader
        return PeacefulGrader

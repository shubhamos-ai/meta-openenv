"""
SHUBHAMOS: AI Email Operations & Triage Environment
tasks/extreme.py — Extreme Task (seed=666, 100 emails, 500 steps)

Scenario: Total chaos. Midnight after a major security breach.
Hundreds of angry emails, massive spam, strictly limited steps per email.
"""

from __future__ import annotations
from typing import Any, Dict


class ExtremeTask:
    """
    Extreme difficulty task.
    - 100 emails: vast volume
    - High ratio of urgent and complex billing issues
    - 500 max steps — extremely tight (avg 5 steps per email)
    - Seed 666
    """

    task_id = "extreme"
    seed = 666
    email_count = 100
    max_steps = 500
    difficulty = "extreme"

    grading_thresholds = {
        "pass": 0.40,
        "good": 0.55,
        "excellent": 0.75,
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
            "Extreme Chaos: 100 emails under crisis conditions. "
            "Tests absolute max throughput and prioritization. "
            f"Seed={cls.seed}, max_steps={cls.max_steps}."
        )

    @classmethod
    def grader_class(cls):
        from ..graders.extreme_grader import ExtremeGrader
        return ExtremeGrader

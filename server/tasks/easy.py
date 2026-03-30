"""
SHUBHAMOS: AI Email Operations & Triage Environment
tasks/easy.py — Easy Task (seed=42, 8 emails, 50 steps)

Scenario: A small business inbox with clear, unambiguous emails.
Ideal for agent calibration — each email belongs to an obvious category.
"""

from __future__ import annotations
from typing import Any, Dict


class EasyTask:
    """
    Easy difficulty task.

    - 8 emails: mix of spam, general inquiries, 1-2 billing issues
    - Clear subject lines, no ambiguity
    - 50 max steps — plenty of room
    - Seed 42 — deterministic, fixed for evaluation
    """

    task_id = "easy"
    seed = 42
    email_count = 8
    max_steps = 50
    difficulty = "easy"

    # Grading thresholds for this tier
    grading_thresholds = {
        "pass": 0.60,       # minimum score to "pass"
        "good": 0.75,
        "excellent": 0.90,
    }

    @classmethod
    def config(cls) -> Dict[str, Any]:
        """Return task_config dict for env.reset()."""
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
            "Basic Inbox (Easy): 8 emails with clear categories. "
            "Ideal starting point for agent calibration. "
            f"Seed={cls.seed}, max_steps={cls.max_steps}."
        )

    @classmethod
    def grader_class(cls):
        from ..graders.easy_grader import EasyGrader
        return EasyGrader

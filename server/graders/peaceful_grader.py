"""graders/peaceful_grader.py — Peaceful task grader"""
from .base_grader import BaseGrader


class PeacefulGrader(BaseGrader):
    PASS_THRESHOLD = 0.50

    def task_name(self) -> str:
        return "peaceful"


def grade(state) -> dict:
    """OpenEnv entrypoint for grading."""
    report = PeacefulGrader().grade(state)
    return report.to_dict()

"""graders/extreme_grader.py — Extreme task grader"""
from .base_grader import BaseGrader


class ExtremeGrader(BaseGrader):
    PASS_THRESHOLD = 0.40

    def task_name(self) -> str:
        return "extreme"


def grade(state) -> dict:
    """OpenEnv entrypoint for grading."""
    report = ExtremeGrader().grade(state)
    return report.to_dict()

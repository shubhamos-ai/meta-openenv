"""graders/medium_grader.py — Medium task grader (seed=123, pass threshold=0.55)"""
from .base_grader import BaseGrader


class MediumGrader(BaseGrader):
    PASS_THRESHOLD = 0.55

    def task_name(self) -> str:
        return "medium"

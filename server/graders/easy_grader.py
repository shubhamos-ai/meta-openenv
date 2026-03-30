"""graders/easy_grader.py — Easy task grader (seed=42, pass threshold=0.60)"""
from .base_grader import BaseGrader


class EasyGrader(BaseGrader):
    PASS_THRESHOLD = 0.60

    def task_name(self) -> str:
        return "easy"

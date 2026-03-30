"""graders/hard_grader.py — Hard task grader (seed=999, pass threshold=0.50)"""
from graders.base_grader import BaseGrader


class HardGrader(BaseGrader):
    PASS_THRESHOLD = 0.50

    def task_name(self) -> str:
        return "hard"

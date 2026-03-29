"""
SHUBHAMOS Task Definitions — Phase 3
tasks/__init__.py

Each task is a callable that returns a task_config dict suitable for env.reset().
Tasks are deterministic via fixed seeds defined in openenv.yaml.
"""

from tasks.easy import EasyTask
from tasks.medium import MediumTask
from tasks.hard import HardTask

TASKS = {
    "easy": EasyTask,
    "medium": MediumTask,
    "hard": HardTask,
}

__all__ = ["TASKS", "EasyTask", "MediumTask", "HardTask"]

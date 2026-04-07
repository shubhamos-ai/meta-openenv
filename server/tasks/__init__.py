"""
SHUBHAMOS Task Definitions — Phase 3
tasks/__init__.py

Each task is a callable that returns a task_config dict suitable for env.reset().
Tasks are deterministic via fixed seeds defined in openenv.yaml.
"""

from .easy import EasyTask
from .medium import MediumTask
from .hard import HardTask
from .peaceful import PeacefulTask
from .extreme import ExtremeTask

TASKS = {
    "peaceful": PeacefulTask,
    "easy": EasyTask,
    "medium": MediumTask,
    "hard": HardTask,
    "extreme": ExtremeTask,
}

__all__ = ["TASKS", "EasyTask", "MediumTask", "HardTask", "PeacefulTask", "ExtremeTask"]

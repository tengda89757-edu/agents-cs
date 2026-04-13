"""
Orchestration Module
====================
Modular, reproducible multi-agent orchestration for the tutoring system.
"""

from .config import COURSE_NAME, ROUNDS, DEFAULT_MODEL
from .student_profile import StudentProfile
from .profile_updater import update_student_profile
from .profile_summary import get_student_profile_summary
from .transfers import (
    make_transfer_to_coordinator,
    make_transfer_to_tester,
    make_transfer_to_tutor,
    make_transfer_to_grader,
    make_transfer_to_exit,
)
from .agents import build_agents
from .runner import run_demo_loop, run_batch_simulation

__all__ = [
    "COURSE_NAME",
    "ROUNDS",
    "DEFAULT_MODEL",
    "StudentProfile",
    "update_student_profile",
    "get_student_profile_summary",
    "make_transfer_to_coordinator",
    "make_transfer_to_tester",
    "make_transfer_to_tutor",
    "make_transfer_to_grader",
    "make_transfer_to_exit",
    "build_agents",
    "run_demo_loop",
    "run_batch_simulation",
]

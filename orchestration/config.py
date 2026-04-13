"""
Global configuration constants.
"""

import os

COURSE_NAME = "数据结构与算法"
ROUNDS = 1
DEFAULT_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")

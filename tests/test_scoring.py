"""
Tests for scoring module.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scoring.tests import (
    TestComprehensiveMasteryScore,
    TestComprehensiveLearningBehaviorsScore,
    TestAdaptiveDifficultyAdjustment,
    TestComputeAllScores,
)

if __name__ == "__main__":
    import unittest
    unittest.main()

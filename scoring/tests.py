"""
Unit tests for the scoring engine.
Run with: python -m unittest scoring.tests
"""

import math
import unittest
from .engine import (
    comprehensive_mastery_score,
    comprehensive_learning_behaviors_score,
    adaptive_difficulty_adjustment,
    compute_all_scores,
)


class TestComprehensiveMasteryScore(unittest.TestCase):
    def test_default_weights(self):
        cms = comprehensive_mastery_score(1.0, 1.0, 1.0, 1.0)
        self.assertAlmostEqual(cms, 1.0)

    def test_nan_input(self):
        cms = comprehensive_mastery_score(float("nan"), 0.5, 0.5, 0.5)
        # NaN accuracy_rate -> 0.0, others 0.5, weights default
        self.assertGreaterEqual(cms, 0.0)
        self.assertLessEqual(cms, 1.0)
        self.assertFalse(math.isnan(cms))

    def test_zero_weights(self):
        cms = comprehensive_mastery_score(1.0, 1.0, 1.0, 1.0, weights={k: 0.0 for k in [
            "accuracy_rate", "concept_understanding", "problem_solving", "code_implementation"
        ]})
        self.assertEqual(cms, 0.0)

    def test_out_of_range_inputs(self):
        cms = comprehensive_mastery_score(1.5, -0.2, 0.5, 0.5)
        # 1.5 -> 1.0, -0.2 -> 0.0
        self.assertGreaterEqual(cms, 0.0)
        self.assertLessEqual(cms, 1.0)

    def test_negative_weights(self):
        cms = comprehensive_mastery_score(1.0, 1.0, 1.0, 1.0, weights={
            "accuracy_rate": -0.5,
            "concept_understanding": 0.5,
            "problem_solving": 0.5,
            "code_implementation": 0.5,
        })
        self.assertGreaterEqual(cms, 0.0)
        self.assertLessEqual(cms, 1.0)


class TestComprehensiveLearningBehaviorsScore(unittest.TestCase):
    def test_zero_target_study_time(self):
        clbs = comprehensive_learning_behaviors_score(
            0.5, 0.5, 0.5, 0.5, daily_study_time=2.5, problem_attempts=3.5,
            target_study_time=0.0, target_attempts=3.5
        )
        self.assertGreaterEqual(clbs, 0.0)
        self.assertLessEqual(clbs, 1.0)
        self.assertFalse(math.isnan(clbs))

    def test_negative_target_attempts(self):
        clbs = comprehensive_learning_behaviors_score(
            0.5, 0.5, 0.5, 0.5, daily_study_time=2.5, problem_attempts=3.5,
            target_study_time=2.5, target_attempts=-1.0
        )
        self.assertGreaterEqual(clbs, 0.0)
        self.assertLessEqual(clbs, 1.0)

    def test_nan_inputs(self):
        clbs = comprehensive_learning_behaviors_score(
            float("nan"), float("nan"), float("nan"), float("nan"),
            daily_study_time=float("nan"), problem_attempts=float("nan")
        )
        self.assertEqual(clbs, 0.0)

    def test_large_values_clip_to_one(self):
        clbs = comprehensive_learning_behaviors_score(
            0.0, 0.0, 1.0, 1.0, daily_study_time=1e9, problem_attempts=1e9
        )
        self.assertEqual(clbs, 1.0)


class TestAdaptiveDifficultyAdjustment(unittest.TestCase):
    def test_attempts_below_one(self):
        ada = adaptive_difficulty_adjustment(0.9, 0.9, 0.0, attempt_threshold_high=4.0)
        # attempts floored to 1.0, s=0.9, 1.0 < 4.0 -> medium
        self.assertEqual(ada, "medium")

    def test_out_of_range_mastery(self):
        ada = adaptive_difficulty_adjustment(1.5, -0.3, 3.0)
        # mastery->1.0, avg->0.0, s=0.5 -> medium
        self.assertEqual(ada, "medium")

    def test_threshold_below_one(self):
        ada = adaptive_difficulty_adjustment(0.9, 0.9, 5.0, attempt_threshold_high=0.5)
        # threshold floored to 1.0, 5.0 >= 1.0 -> hard
        self.assertEqual(ada, "hard")

    def test_boundary_strict_gt(self):
        ada = adaptive_difficulty_adjustment(0.8, 0.8, 5.0)
        # s = 0.8 exactly, condition is > 0.8 -> medium
        self.assertEqual(ada, "medium")

    def test_easy_branch(self):
        ada = adaptive_difficulty_adjustment(0.1, 0.2, 1.0)
        self.assertEqual(ada, "easy")

    def test_medium_branch(self):
        ada = adaptive_difficulty_adjustment(0.6, 0.6, 3.0)
        self.assertEqual(ada, "medium")

    def test_hard_branch(self):
        ada = adaptive_difficulty_adjustment(0.9, 0.9, 5.0)
        self.assertEqual(ada, "hard")


class TestComputeAllScores(unittest.TestCase):
    def test_full_record(self):
        record = {
            "Accuracy_Rate": 0.8,
            "Independent_Solutions_Rate": 0.7,
            "Active_Learning_Score": 0.6,
            "Learning_Persistence": 0.5,
            "Daily_Study_Time": 2.0,
            "Problem_Attempts": 4.0,
            "current_difficulty": "medium",
            "assessment_dimensions": {
                "concept_understanding": 0.7,
                "problem_solving": 0.6,
                "code_implementation": 0.5,
                "learning_attitude": 0.8,
            },
        }
        result = compute_all_scores(record)
        self.assertIn("comprehensive_mastery_score", result)
        self.assertIn("comprehensive_learning_behaviors_score", result)
        self.assertIn("adaptive_difficulty", result)
        self.assertIn("average_dimension_score", result)
        self.assertTrue(result["adaptive_difficulty"] in {"easy", "medium", "hard"})


if __name__ == "__main__":
    unittest.main()

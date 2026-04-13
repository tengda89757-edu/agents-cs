"""
Tests for guardrails module.
"""

import math
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from guardrails import (
    validate_performance_data,
    safe_divide,
    clip,
    fallback_score_out_of_range,
    fallback_dimension_out_of_range,
    fallback_empty_knowledge_points,
    fallback_negative_time_spent,
    fallback_unknown_difficulty,
    fallback_total_questions_zero,
    fallback_mastery_nan,
)


class TestMathUtils(unittest.TestCase):
    def test_safe_divide_by_zero(self):
        self.assertEqual(safe_divide(5, 0), 0.0)

    def test_safe_divide_nan_denominator(self):
        self.assertEqual(safe_divide(5, float("nan")), 0.0)

    def test_safe_divide_inf_denominator(self):
        self.assertEqual(safe_divide(5, float("inf")), 0.0)

    def test_safe_divide_negative_denominator(self):
        self.assertEqual(safe_divide(5, -2), -2.5)

    def test_clip_nan(self):
        self.assertEqual(clip(float("nan"), 0, 1), 0.0)

    def test_clip_reversed_bounds(self):
        self.assertEqual(clip(5, 10, 0), 5.0)


class TestFallbackRules(unittest.TestCase):
    def test_score_out_of_range(self):
        val, log = fallback_score_out_of_range(15.0)
        self.assertEqual(val, 10.0)
        self.assertTrue(log["triggered"])

    def test_dimension_out_of_range(self):
        val, log = fallback_dimension_out_of_range(-0.5, "concept")
        self.assertEqual(val, 0.0)
        self.assertTrue(log["triggered"])

    def test_empty_knowledge_points(self):
        val, log = fallback_empty_knowledge_points([])
        self.assertEqual(val, ["未分类知识点"])
        self.assertTrue(log["triggered"])

    def test_negative_time_spent(self):
        val, log = fallback_negative_time_spent(-10)
        self.assertEqual(val, 0.0)
        self.assertTrue(log["triggered"])

    def test_unknown_difficulty(self):
        val, log = fallback_unknown_difficulty("INSANE")
        self.assertEqual(val, "medium")
        self.assertTrue(log["triggered"])

    def test_total_questions_zero(self):
        val, log = fallback_total_questions_zero(0)
        self.assertEqual(val, 1)
        self.assertTrue(log["triggered"])

    def test_mastery_nan(self):
        val, log = fallback_mastery_nan(float("nan"))
        self.assertEqual(val, 0.0)
        self.assertTrue(log["triggered"])


class TestValidatePerformanceData(unittest.TestCase):
    def _valid_payload(self):
        return {
            "correct": True,
            "topic": "链表",
            "score": 8.0,
            "question_details": {
                "question_type": "概念题",
                "difficulty_level": "medium",
                "knowledge_points": ["链表"],
                "time_spent": 300
            },
            "answer_process": {
                "attempts": 1,
                "error_types": [],
                "code_quality": {
                    "time_complexity": "O(n)",
                    "space_complexity": "O(1)",
                    "code_style": "good"
                }
            },
            "learning_behavior": {
                "used_hints": False,
                "reference_materials": [],
                "solution_approach": "独立思考"
            },
            "assessment_dimensions": {
                "concept_understanding": 0.8,
                "problem_solving": 0.7,
                "code_implementation": 0.6,
                "learning_attitude": 0.9
            }
        }

    def test_valid(self):
        result = validate_performance_data(self._valid_payload())
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)

    def test_missing_key(self):
        payload = self._valid_payload()
        del payload["topic"]
        result = validate_performance_data(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("topic" in e for e in result["errors"]))

    def test_score_clipped(self):
        payload = self._valid_payload()
        payload["score"] = 15.0
        result = validate_performance_data(payload)
        # Auto-fixable fallbacks still generate validation warnings; sanitized value is correct
        self.assertEqual(result["sanitized"]["score"], 10.0)
        self.assertTrue(any("clipped" in e for e in result["errors"]))

    def test_dimension_clipped(self):
        payload = self._valid_payload()
        payload["assessment_dimensions"]["concept_understanding"] = 1.5
        result = validate_performance_data(payload)
        self.assertEqual(result["sanitized"]["assessment_dimensions"]["concept_understanding"], 1.0)
        self.assertTrue(any("clipped" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()

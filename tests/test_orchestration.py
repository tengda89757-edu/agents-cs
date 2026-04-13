"""
Tests for orchestration module.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from orchestration import StudentProfile, update_student_profile, get_student_profile_summary
from orchestration.transfers import REPRODUCIBLE_HOOKS


class TestStudentProfile(unittest.TestCase):
    def test_mastery_zero_questions(self):
        sp = StudentProfile()
        self.assertEqual(sp.calculate_mastery(), 0.0)

    def test_update_knowledge_points(self):
        sp = StudentProfile()
        sp.update_knowledge_points_mastery(["链表"], 8.0)
        self.assertEqual(sp.knowledge_points_mastery["链表"]["attempts"], 1)


class TestProfileUpdater(unittest.TestCase):
    def _payload(self, correct=True, score=8.0):
        return {
            "correct": correct,
            "topic": "链表",
            "score": score,
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

    def test_successful_update(self):
        sp = StudentProfile()
        result = update_student_profile(sp, self._payload())
        self.assertEqual(result["status"], "updated")
        self.assertEqual(sp.total_questions, 1)
        self.assertEqual(sp.correct_answers, 1)

    def test_validation_error(self):
        sp = StudentProfile()
        payload = self._payload()
        del payload["topic"]
        result = update_student_profile(sp, payload)
        self.assertEqual(result["status"], "error")

    def test_difficulty_adjustment_hard(self):
        sp = StudentProfile()
        # Feed 10 perfect answers with all dimension scores > 0.8
        payload = self._payload(correct=True, score=10.0)
        payload["assessment_dimensions"] = {
            "concept_understanding": 0.9,
            "problem_solving": 0.9,
            "code_implementation": 0.9,
            "learning_attitude": 0.9,
        }
        for _ in range(10):
            update_student_profile(sp, payload)
        self.assertEqual(sp.current_difficulty, "hard")


class TestProfileSummary(unittest.TestCase):
    def test_summary_format(self):
        sp = StudentProfile()
        summary = get_student_profile_summary(sp)
        self.assertIn("总答题数", summary)
        self.assertIn("正确率", summary)


class TestTransfers(unittest.TestCase):
    def test_reproducible_hooks(self):
        hooks = REPRODUCIBLE_HOOKS
        # Should not raise or print
        hooks["print"]("test")
        hooks["sleep"](1)


if __name__ == "__main__":
    unittest.main()

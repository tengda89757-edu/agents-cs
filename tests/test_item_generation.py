"""
Tests for item generation pipeline.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from item_generation import select_template, fill_template, generate_item


class TestItemGeneration(unittest.TestCase):
    def test_select_template_deterministic_with_seed(self):
        profile = {"current_difficulty": "medium", "weak_points": ["链表"]}
        t1 = select_template(profile["current_difficulty"], profile["weak_points"], rng_seed=42)
        t2 = select_template(profile["current_difficulty"], profile["weak_points"], rng_seed=42)
        self.assertEqual(t1["template_id"], t2["template_id"])

    def test_fill_template_replaces_placeholders(self):
        template = {
            "template_id": "TEST-01",
            "question_type": "概念题",
            "skeleton": "解释 {{knowledge_point}} 的 {{aspect}}。",
            "placeholders": {"aspect": ["定义"]},
        }
        item = fill_template(template, "easy", ["链表"], rng_seed=42)
        self.assertIn("链表", item["student_prompt"])
        self.assertNotIn("{{knowledge_point}}", item["student_prompt"])

    def test_generate_item_structure(self):
        profile = {"current_difficulty": "hard", "weak_points": ["二叉树遍历"]}
        item = generate_item(profile, rng_seed=42)
        self.assertIn("template_id", item)
        self.assertIn("difficulty", item)
        self.assertIn("student_prompt", item)


if __name__ == "__main__":
    unittest.main()

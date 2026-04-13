"""
JSON Schema for performance data (update_student_profile payload).
"""

VERSION = "1.0.0"

PERFORMANCE_DATA_SCHEMA = {
    "type": "object",
    "required": [
        "correct", "topic", "score", "question_details",
        "answer_process", "learning_behavior", "assessment_dimensions"
    ],
    "properties": {
        "correct": {"type": "bool"},
        "topic": {"type": "string", "min_length": 1},
        "score": {"type": "number", "minimum": 0.0, "maximum": 10.0},
        "question_details": {
            "type": "object",
            "required": ["question_type", "difficulty_level", "knowledge_points", "time_spent"],
            "properties": {
                "question_type": {"type": "string", "enum": [
                    "概念题", "选择题", "填空题", "简答题",
                    "程序纠错题", "判断题", "coding"
                ]},
                "difficulty_level": {"type": "string", "enum": ["easy", "medium", "hard"]},
                "knowledge_points": {"type": "array", "items": {"type": "string"}, "min_items": 1},
                "time_spent": {"type": "number", "minimum": 0}
            }
        },
        "answer_process": {
            "type": "object",
            "required": ["attempts", "error_types", "code_quality"],
            "properties": {
                "attempts": {"type": "number", "minimum": 1},
                "error_types": {"type": "array", "items": {"type": "string"}},
                "code_quality": {
                    "type": "object",
                    "required": ["time_complexity", "space_complexity", "code_style"],
                    "properties": {
                        "time_complexity": {"type": "string"},
                        "space_complexity": {"type": "string"},
                        "code_style": {"type": "string"}
                    }
                }
            }
        },
        "learning_behavior": {
            "type": "object",
            "required": ["used_hints", "reference_materials", "solution_approach"],
            "properties": {
                "used_hints": {"type": "bool"},
                "reference_materials": {"type": "array", "items": {"type": "string"}},
                "solution_approach": {"type": "string"}
            }
        },
        "assessment_dimensions": {
            "type": "object",
            "required": ["concept_understanding", "problem_solving",
                         "code_implementation", "learning_attitude"],
            "properties": {
                "concept_understanding": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "problem_solving": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "code_implementation": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "learning_attitude": {"type": "number", "minimum": 0.0, "maximum": 1.0}
            }
        }
    }
}

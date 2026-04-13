"""
StudentProfile — pure data container with no side effects on construction.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Set


@dataclass
class StudentProfile:
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    weak_points: Set[str] = field(default_factory=set)
    strong_points: Set[str] = field(default_factory=set)
    current_difficulty: str = "medium"
    total_questions: int = 0
    correct_answers: int = 0
    topic_scores: Dict[str, float] = field(default_factory=dict)
    learning_path: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_points_mastery: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    question_type_performance: Dict[str, Any] = field(default_factory=dict)
    time_statistics: Dict[str, Any] = field(default_factory=lambda: {
        "total_time": 0,
        "average_time": 0,
        "time_by_difficulty": {"easy": 0, "medium": 0, "hard": 0}
    })
    learning_behavior_stats: Dict[str, int] = field(default_factory=lambda: {
        "hint_usage": 0,
        "reference_usage": 0,
        "independent_solutions": 0
    })
    dimension_scores: Dict[str, List[float]] = field(default_factory=lambda: {
        "concept_understanding": [],
        "problem_solving": [],
        "code_implementation": [],
        "learning_attitude": []
    })
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    decision_explanations: List[Dict[str, Any]] = field(default_factory=list)

    def calculate_mastery(self) -> float:
        """Calculate mastery with denominator guard."""
        denominator = max(1, self.total_questions)
        return self.correct_answers / denominator

    def update_knowledge_points_mastery(self, knowledge_points: List[str], score: float) -> None:
        for point in knowledge_points:
            if point not in self.knowledge_points_mastery:
                self.knowledge_points_mastery[point] = {"total_score": 0.0, "attempts": 0}
            self.knowledge_points_mastery[point]["total_score"] += score
            self.knowledge_points_mastery[point]["attempts"] += 1

    def update_time_statistics(self, time_spent: float, difficulty: str) -> None:
        self.time_statistics["total_time"] += time_spent
        self.time_statistics["average_time"] = self.time_statistics["total_time"] / max(1, self.total_questions)
        self.time_statistics["time_by_difficulty"][difficulty] = self.time_statistics["time_by_difficulty"].get(difficulty, 0) + time_spent

    def update_learning_behavior(self, behavior_data: Dict[str, Any]) -> None:
        if not behavior_data.get("used_hints", True):
            self.learning_behavior_stats["independent_solutions"] += 1
        if behavior_data.get("used_hints", False):
            self.learning_behavior_stats["hint_usage"] += 1
        if behavior_data.get("reference_materials", []):
            self.learning_behavior_stats["reference_usage"] += 1

    def update_dimension_scores(self, assessment_dimensions: Dict[str, float]) -> None:
        for dimension, score in assessment_dimensions.items():
            if dimension in self.dimension_scores:
                self.dimension_scores[dimension].append(score)

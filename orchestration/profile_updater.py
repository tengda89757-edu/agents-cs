"""
update_student_profile — explicit guardrails integration.
"""

from typing import Dict, Any
from .student_profile import StudentProfile
from guardrails import validate_performance_data


def update_student_profile(student_profile: StudentProfile, performance_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the student profile after validating and sanitizing the payload.
    Returns a detailed result dict including explanation of any fallbacks applied.
    """
    # 1. Explicit validation via guardrails
    validation = validate_performance_data(performance_data)
    if not validation["valid"]:
        return {
            "status": "error",
            "message": "Validation failed",
            "errors": validation["errors"],
            "logs": validation.get("logs", []),
        }

    sanitized = validation["sanitized"]

    # 2. Record pre-update state
    old_state = {
        "difficulty": student_profile.current_difficulty,
        "topic_score": student_profile.topic_scores.get(sanitized["topic"], 0.0),
        "total_questions": student_profile.total_questions,
        "correct_answers": student_profile.correct_answers,
    }

    # 3. Update basic data
    student_profile.performance_history.append(sanitized)
    student_profile.total_questions += 1
    topic = sanitized["topic"]

    # 4. Update detailed tracking
    student_profile.update_knowledge_points_mastery(
        sanitized["question_details"]["knowledge_points"],
        sanitized["score"]
    )
    student_profile.update_time_statistics(
        sanitized["question_details"]["time_spent"],
        sanitized["question_details"]["difficulty_level"]
    )
    student_profile.update_learning_behavior(sanitized["learning_behavior"])
    student_profile.update_dimension_scores(sanitized["assessment_dimensions"])

    # 5. Update correctness and topic score
    if sanitized["correct"]:
        student_profile.correct_answers += 1
    current_score = student_profile.topic_scores.get(topic, 0.0)
    student_profile.topic_scores[topic] = current_score + sanitized["score"]

    # 6. Difficulty adjustment (Eq. 9 logic, inline for clarity)
    mastery = student_profile.calculate_mastery()
    old_difficulty = student_profile.current_difficulty
    dims = sanitized["assessment_dimensions"]
    avg_dimension_score = sum(dims.values()) / max(1, len(dims))

    if mastery > 0.8 and avg_dimension_score > 0.8:
        new_difficulty = "hard"
    elif mastery < 0.4 or avg_dimension_score < 0.4:
        new_difficulty = "easy"
    else:
        new_difficulty = "medium"

    if old_difficulty != new_difficulty:
        student_profile.current_difficulty = new_difficulty

    return {
        "status": "updated",
        "current_difficulty": student_profile.current_difficulty,
        "explanation": {
            "mastery": mastery,
            "difficulty_change": {
                "old": old_difficulty,
                "new": student_profile.current_difficulty,
                "reason": "基于综合表现的调整"
            },
            "topic_progress": {
                "topic": topic,
                "old_score": current_score,
                "new_score": student_profile.topic_scores[topic]
            },
            "learning_behavior": student_profile.learning_behavior_stats,
            "time_statistics": student_profile.time_statistics,
            "dimension_scores": student_profile.dimension_scores,
        },
        "validation_logs": validation.get("logs", []),
    }

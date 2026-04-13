"""
Runtime validators that compose fallback rules into a single validation pipeline.
"""

import math
from typing import Dict, Any, List
from .schema import PERFORMANCE_DATA_SCHEMA
from .fallback_rules import (
    fallback_score_out_of_range,
    fallback_dimension_out_of_range,
    fallback_missing_required_key,
    fallback_empty_knowledge_points,
    fallback_negative_time_spent,
    fallback_unknown_difficulty,
)


def validate_performance_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize a performance-data payload.
    Returns {"valid": bool, "errors": List[str], "sanitized": Dict, "logs": List[Dict]}.
    """
    errors: List[str] = []
    logs: List[Dict[str, Any]] = []
    schema = PERFORMANCE_DATA_SCHEMA
    sanitized = {}

    # 1. Required keys (using executable fallback)
    is_valid, missing, log = fallback_missing_required_key(data, schema["required"])
    logs.append(log)
    if not is_valid:
        for key in missing:
            errors.append(f"Missing required key: {key}")
        return {"valid": False, "errors": errors, "sanitized": {}, "logs": logs}

    # 2. Top-level fields
    correct = data.get("correct")
    if not isinstance(correct, bool):
        errors.append("'correct' must be boolean")

    score_raw = float(data.get("score", 0.0))
    score, log = fallback_score_out_of_range(score_raw)
    logs.append(log)
    if log["triggered"]:
        errors.append(f"'score' {score_raw} out of range [0, 10]; clipped")

    topic = str(data.get("topic", "")).strip()
    if not topic:
        errors.append("'topic' must be non-empty string")

    sanitized.update({"correct": correct, "score": score, "topic": topic})

    # 3. Question details
    qd = data.get("question_details", {})
    qd_required = schema["properties"]["question_details"]["required"]
    for k in qd_required:
        if k not in qd:
            errors.append(f"Missing question_details key: {k}")

    difficulty, log = fallback_unknown_difficulty(qd.get("difficulty_level", "medium"))
    logs.append(log)
    if log["triggered"]:
        errors.append(f"Unknown difficulty '{qd.get('difficulty_level')}'; fallback to 'medium'")

    kp_list = list(qd.get("knowledge_points", []))
    knowledge_points, log = fallback_empty_knowledge_points(kp_list)
    logs.append(log)
    if log["triggered"]:
        errors.append("Empty knowledge_points; fallback to ['未分类知识点']")

    time_raw = float(qd.get("time_spent", 0.0))
    time_spent, log = fallback_negative_time_spent(time_raw)
    logs.append(log)
    if log["triggered"]:
        errors.append(f"Negative time_spent {time_raw}; set to 0.0")

    sanitized["question_details"] = {
        "question_type": str(qd.get("question_type", "概念题")),
        "difficulty_level": difficulty,
        "knowledge_points": knowledge_points,
        "time_spent": time_spent,
    }

    # 4. Answer process & learning behavior (light validation, preserve structure)
    sanitized["answer_process"] = dict(data.get("answer_process", {}))
    sanitized["learning_behavior"] = dict(data.get("learning_behavior", {}))

    # 5. Assessment dimensions – clip to [0, 1]
    dims = data.get("assessment_dimensions", {})
    dim_required = schema["properties"]["assessment_dimensions"]["required"]
    sanitized_dims = {}
    for k in dim_required:
        raw = float(dims.get(k, 0.0))
        if math.isnan(raw):
            errors.append(f"Dimension '{k}' is NaN; fallback to 0.0")
            raw = 0.0
        val, log = fallback_dimension_out_of_range(raw, name=k)
        logs.append(log)
        if log["triggered"]:
            errors.append(f"Dimension '{k}' {raw} out of [0,1]; clipped")
        sanitized_dims[k] = val
    sanitized["assessment_dimensions"] = sanitized_dims

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "sanitized": sanitized,
        "logs": logs,
    }

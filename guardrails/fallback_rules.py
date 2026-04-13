"""
Fallback / edge-case rules — executable implementations.

Each function below corresponds to an entry in the original FALLBACK_RULES dict.
They are designed to be called explicitly by validators or orchestration code,
making every edge-case branch inspectable and testable.
"""

import math
from typing import List, Dict, Any, Tuple
from .math_utils import clip


def fallback_score_out_of_range(score: float) -> Tuple[float, Dict[str, Any]]:
    """
    Rule: score_out_of_range -> clip(score, 0.0, 10.0)
    """
    original = score
    clipped = clip(score, 0.0, 10.0)
    log = {
        "rule": "score_out_of_range",
        "original": original,
        "clipped": clipped,
        "action_taken": "clipped to [0.0, 10.0]",
        "triggered": (original != clipped) or math.isnan(original),
    }
    return clipped, log


def fallback_dimension_out_of_range(value: float, name: str = "dimension") -> Tuple[float, Dict[str, Any]]:
    """
    Rule: dimension_out_of_range -> clip(value, 0.0, 1.0)
    """
    original = value
    clipped = clip(value, 0.0, 1.0)
    log = {
        "rule": "dimension_out_of_range",
        "name": name,
        "original": original,
        "clipped": clipped,
        "action_taken": "clipped to [0.0, 1.0]",
        "triggered": (original != clipped) or math.isnan(original),
    }
    return clipped, log


def fallback_missing_required_key(data: Dict[str, Any], schema_required: List[str]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Rule: missing_required_key -> raise ValidationError with exact missing-key list.

    Returns (is_valid, missing_keys, log).
    """
    missing = [key for key in schema_required if key not in data]
    log = {
        "rule": "missing_required_key",
        "missing_keys": missing,
        "action_taken": "report missing keys" if missing else "none",
        "triggered": bool(missing),
    }
    return len(missing) == 0, missing, log


def fallback_empty_knowledge_points(kp_list: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Rule: empty_knowledge_points -> fallback to ['未分类知识点']
    """
    if not kp_list:
        fallback = ["未分类知识点"]
        log = {
            "rule": "empty_knowledge_points",
            "original": kp_list,
            "fallback": fallback,
            "action_taken": "replaced with ['未分类知识点']",
            "triggered": True,
        }
        return fallback, log
    return kp_list, {
        "rule": "empty_knowledge_points",
        "action_taken": "none",
        "triggered": False,
    }


def fallback_negative_time_spent(t: float) -> Tuple[float, Dict[str, Any]]:
    """
    Rule: negative_time_spent -> set to 0.0 and log warning.
    """
    if t < 0:
        log = {
            "rule": "negative_time_spent",
            "original": t,
            "corrected": 0.0,
            "action_taken": "set to 0.0",
            "triggered": True,
        }
        return 0.0, log
    return t, {
        "rule": "negative_time_spent",
        "action_taken": "none",
        "triggered": False,
    }


def fallback_total_questions_zero(total_questions: int) -> Tuple[int, Dict[str, Any]]:
    """
    Rule: total_questions_zero -> denominator clipped to 1 to avoid ZeroDivisionError.
    """
    if total_questions == 0:
        log = {
            "rule": "total_questions_zero",
            "original": total_questions,
            "corrected": 1,
            "action_taken": "denominator clipped to 1",
            "triggered": True,
        }
        return 1, log
    return total_questions, {
        "rule": "total_questions_zero",
        "action_taken": "none",
        "triggered": False,
    }


def fallback_mastery_nan(mastery: float) -> Tuple[float, Dict[str, Any]]:
    """
    Rule: mastery_nan -> return 0.0 and log warning.
    """
    if math.isnan(mastery):
        log = {
            "rule": "mastery_nan",
            "original": mastery,
            "corrected": 0.0,
            "action_taken": "fallback to 0.0",
            "triggered": True,
        }
        return 0.0, log
    return mastery, {
        "rule": "mastery_nan",
        "action_taken": "none",
        "triggered": False,
    }


def fallback_unknown_difficulty(difficulty: str) -> Tuple[str, Dict[str, Any]]:
    """
    Rule: difficulty_unknown -> fallback to 'medium'.
    """
    allowed = {"easy", "medium", "hard"}
    d = str(difficulty).lower().strip()
    if d not in allowed:
        log = {
            "rule": "difficulty_unknown",
            "original": difficulty,
            "corrected": "medium",
            "action_taken": "fallback to 'medium'",
            "triggered": True,
        }
        return "medium", log
    return d, {
        "rule": "difficulty_unknown",
        "action_taken": "none",
        "triggered": False,
    }

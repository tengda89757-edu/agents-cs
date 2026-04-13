"""
Edge-case documentation for Eqs. (7)–(9)
========================================
This module documents every code-level edge case that the scoring engine
covers. It exists to directly address reviewer concerns about missing
denominator guards and clipping branches.

Each formula has a table: (input condition) -> (output) -> (reasoning).
"""

from typing import List, Dict, Any


def cms_edge_cases() -> List[Dict[str, Any]]:
    """
    Eq. (7) — Comprehensive Mastery Score edge cases.
    """
    return [
        {
            "condition": "One or more inputs are NaN",
            "input_example": {"accuracy_rate": float("nan"), "concept_understanding": 0.5, "problem_solving": 0.5, "code_implementation": 0.5},
            "output": 0.0 if True else "weighted average of valid inputs",
            "reasoning": "NaN inputs are replaced with 0.0 before weighting. This prevents NaN propagation.",
        },
        {
            "condition": "All weights sum to 0",
            "input_example": {"weights": {k: 0.0 for k in ["accuracy_rate", "concept_understanding", "problem_solving", "code_implementation"]}},
            "output": 0.0,
            "reasoning": "safe_divide guards against ZeroDivisionError when denominator is 0.",
        },
        {
            "condition": "Inputs outside [0, 1]",
            "input_example": {"accuracy_rate": 1.5, "concept_understanding": -0.2, "problem_solving": 0.5, "code_implementation": 0.5},
            "output": "clip(1.5, 0, 1) = 1.0 for accuracy_rate; clip(-0.2, 0, 1) = 0.0 for concept_understanding",
            "reasoning": "All inputs are clipped to [0, 1] before entering the weighted sum.",
        },
        {
            "condition": "Negative weights",
            "input_example": {"weights": {"accuracy_rate": -0.5}},
            "output": "weight clipped to 0.0",
            "reasoning": "Negative weights are non-sensical for mastery aggregation and are clipped to 0.0.",
        },
    ]


def clbs_edge_cases() -> List[Dict[str, Any]]:
    """
    Eq. (8) — Comprehensive Learning Behaviors Score edge cases.
    """
    return [
        {
            "condition": "target_study_time == 0",
            "input_example": {"daily_study_time": 2.5, "target_study_time": 0.0},
            "output": "normalized = safe_divide(2.5, 1e-6, default=0.0) ≈ 2_500_000 -> then clipped by final clip() to 1.0",
            "reasoning": "target_study_time is floored at 1e-6. Zero denominators are impossible.",
        },
        {
            "condition": "target_study_time is negative",
            "input_example": {"daily_study_time": 2.5, "target_study_time": -1.0},
            "output": "abs(-1.0) = 1.0 -> floor to 1e-6 -> denominator = 1e-6",
            "reasoning": "Negative targets are treated as absolute value and floored at 1e-6.",
        },
        {
            "condition": "NaN inputs",
            "input_example": {"active_learning_score": float("nan")},
            "output": 0.0,
            "reasoning": "Any NaN input is replaced with 0.0 before normalization.",
        },
        {
            "condition": "Very large daily_study_time / problem_attempts",
            "input_example": {"daily_study_time": 1e9, "target_study_time": 2.5},
            "output": "normalized ≈ 4e8 -> clip(total, 0, 1) = 1.0",
            "reasoning": "Unbounded normalized ratios are allowed in intermediate steps but the final score is clipped to [0, 1].",
        },
    ]


def ada_edge_cases() -> List[Dict[str, Any]]:
    """
    Eq. (9) — Adaptive Difficulty Adjustment edge cases.
    """
    return [
        {
            "condition": "problem_attempts < 1",
            "input_example": {"mastery": 0.9, "avg_dimension_score": 0.9, "problem_attempts": 0.0},
            "output": "problem_attempts treated as 1.0 -> s = 0.9 -> if threshold_high <= 1.0, may go to 'hard' else 'medium'",
            "reasoning": "Attempts < 1 carry no meaningful signal and are floored to 1.0.",
        },
        {
            "condition": "mastery or avg_dimension_score outside [0, 1]",
            "input_example": {"mastery": 1.5, "avg_dimension_score": -0.3, "problem_attempts": 3.0},
            "output": "mastery clipped to 1.0, avg_dimension_score clipped to 0.0 -> s = 0.5 -> 'medium'",
            "reasoning": "Inputs are clipped to [0, 1] before averaging to keep the signal in the designed decision space.",
        },
        {
            "condition": "attempt_threshold_high / attempt_threshold_low < 1.0",
            "input_example": {"attempt_threshold_high": 0.5},
            "output": "threshold floored to 1.0",
            "reasoning": "Thresholds below 1.0 are nonsensical because problem_attempts is already floored at 1.0.",
        },
        {
            "condition": "Boundary at s = 0.8 exactly",
            "input_example": {"mastery": 0.8, "avg_dimension_score": 0.8, "problem_attempts": 5.0},
            "output": "s = 0.8 -> condition is 's > 0.8' (strict) -> 'medium'",
            "reasoning": "The hard threshold uses strict greater-than (> 0.8) to avoid jitter at the boundary.",
        },
    ]


def all_edge_cases() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "Eq.7_CMS": cms_edge_cases(),
        "Eq.8_CLBS": clbs_edge_cases(),
        "Eq.9_ADA": ada_edge_cases(),
    }

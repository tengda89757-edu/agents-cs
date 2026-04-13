"""
Guardrails & Validation Module
==============================
Explicit input-validation, output-sanitization, and fallback rules for the
multi-agent tutoring system. All schemas and clipping boundaries are
version-locked to ensure reproducibility.
"""

from .schema import PERFORMANCE_DATA_SCHEMA, VERSION
from .math_utils import safe_divide, clip
from .fallback_rules import (
    fallback_score_out_of_range,
    fallback_dimension_out_of_range,
    fallback_missing_required_key,
    fallback_empty_knowledge_points,
    fallback_negative_time_spent,
    fallback_total_questions_zero,
    fallback_mastery_nan,
    fallback_unknown_difficulty,
)
from .validators import validate_performance_data

__all__ = [
    "PERFORMANCE_DATA_SCHEMA",
    "VERSION",
    "safe_divide",
    "clip",
    "fallback_score_out_of_range",
    "fallback_dimension_out_of_range",
    "fallback_missing_required_key",
    "fallback_empty_knowledge_points",
    "fallback_negative_time_spent",
    "fallback_total_questions_zero",
    "fallback_mastery_nan",
    "fallback_unknown_difficulty",
    "validate_performance_data",
]

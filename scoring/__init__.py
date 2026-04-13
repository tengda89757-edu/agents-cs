"""
Scoring Engine — Reference Implementation
==========================================
Reconstructed reference implementation for the three composite scoring
formulas used in the tutoring system (Eqs. 7–9 in the manuscript).
"""

from .engine import (
    comprehensive_mastery_score,
    comprehensive_learning_behaviors_score,
    adaptive_difficulty_adjustment,
    compute_all_scores,
    VERSION,
)

__all__ = [
    "comprehensive_mastery_score",
    "comprehensive_learning_behaviors_score",
    "adaptive_difficulty_adjustment",
    "compute_all_scores",
    "VERSION",
]

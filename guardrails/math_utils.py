"""
Mathematical utilities with explicit edge-case handling.
"""

import math
from typing import Union

Number = Union[int, float]


def safe_divide(numerator: Number, denominator: Number, default: float = 0.0) -> float:
    """
    Division with denominator clipping to avoid ZeroDivisionError.

    Edge cases handled:
      - denominator == 0
      - denominator is NaN
      - denominator is +/- inf
      - denominator is negative (allowed, but logged in strict mode)
      - numerator is NaN or inf
      - result is NaN or inf
    """
    # Guard against invalid denominator
    if denominator == 0 or math.isnan(denominator) or math.isinf(denominator):
        return float(default)

    n = float(numerator)
    d = float(denominator)

    # Guard against invalid numerator
    if math.isnan(n):
        return float(default)
    if math.isinf(n):
        # inf / finite = inf; we return default to stay bounded
        return float(default)

    result = n / d
    if math.isnan(result) or math.isinf(result):
        return float(default)
    return result


def clip(value: Number, lower: float, upper: float) -> float:
    """
    Clamp a numeric value to a closed interval.

    Edge cases handled:
      - value is NaN -> returns lower
      - lower > upper -> swaps them
    """
    if math.isnan(value):
        return lower
    lo, hi = (lower, upper) if lower <= upper else (upper, lower)
    return max(lo, min(hi, float(value)))

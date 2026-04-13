"""
Item Generation Pipeline
========================
A reproducible, template-based pipeline for generating assessment items.
"""

from .pipeline import (
    select_template,
    fill_template,
    generate_item,
    VERSION,
)

__all__ = [
    "select_template",
    "fill_template",
    "generate_item",
    "VERSION",
]

"""
Item Generation Pipeline
========================
A reproducible, template-based pipeline for generating assessment items.
Instead of allowing the LLM to freely invent questions, the pipeline:
1. Selects a template based on (difficulty, question_type, weak_points)
2. Fills placeholders deterministically where possible
3. Calls the LLM only for the creative sub-parts (code snippets, distractors)
"""

import json
import random
from typing import Dict, Any, List, Optional

VERSION = "1.0.0"

import os

_TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "question_templates.json")
with open(_TEMPLATES_PATH, "r", encoding="utf-8") as f:
    TEMPLATES_DB = json.load(f)


def _load_templates() -> List[Dict[str, Any]]:
    return TEMPLATES_DB["templates"]


def _difficulty_meta(difficulty: str) -> Dict[str, Any]:
    return TEMPLATES_DB["meta_rules"]["difficulty_mapping"].get(
        difficulty.lower(),
        {"cognitive_level": ["Apply"], "time_limit_seconds": 300, "code_length_lines": "5–15", "hint_count": 1},
    )


def select_template(
    difficulty: str,
    weak_points: List[str],
    excluded_types: Optional[List[str]] = None,
    rng_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Select an appropriate template given student state.

    Rules:
      - If weak_points contains "链表", "树", "图" → prefer concept or code-fix.
      - If difficulty == "hard" and weak_points include algorithm design → prefer coding.
      - Excluded types (already mastered formats) are filtered out.
    """
    if excluded_types is None:
        excluded_types = []
    templates = [t for t in _load_templates() if t["question_type"] not in excluded_types]

    if not templates:
        templates = _load_templates()

    if rng_seed is not None:
        random.seed(rng_seed)

    # Simple heuristic: hard → coding; easy → concept; otherwise uniform
    if difficulty == "hard":
        candidates = [t for t in templates if t["question_type"] == "coding"]
    elif difficulty == "easy":
        candidates = [t for t in templates if t["question_type"] == "概念题"]
    else:
        candidates = [t for t in templates if t["question_type"] in ("程序纠错题", "coding")]

    if not candidates:
        candidates = templates

    return random.choice(candidates)


def fill_template(
    template: Dict[str, Any],
    difficulty: str,
    weak_points: List[str],
    topic_syllabus: Optional[List[str]] = None,
    rng_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fill a template skeleton with deterministic values.
    Returns a dict containing the prompt for the LLM and the resolved metadata.
    """
    if rng_seed is not None:
        random.seed(rng_seed)

    if weak_points:
        kp = random.choice(weak_points)
    elif topic_syllabus:
        kp = random.choice(topic_syllabus)
    else:
        kp = "未指定知识点"

    meta = _difficulty_meta(difficulty)
    skeleton = template["skeleton"]
    placeholders = template.get("placeholders", {})

    # Deterministic fillers
    filled = skeleton.replace("{{knowledge_point}}", kp)

    if "{{aspect}}" in filled:
        aspects = placeholders.get("aspect", ["基本概念"])
        filled = filled.replace("{{aspect}}", random.choice(aspects))

    if "{{n}}" in filled:
        n_map = {"easy": 1, "medium": 2, "hard": 3}
        filled = filled.replace("{{n}}", str(n_map.get(difficulty, 2)))

    if "{{operation}}" in filled:
        operations = placeholders.get("operation", ["查找"])
        filled = filled.replace("{{operation}}", random.choice(operations))

    if "{{time_complexity}}" in filled:
        tc_map = {"easy": "O(n)", "medium": "O(log n)", "hard": "O(1) 平均"}
        filled = filled.replace("{{time_complexity}}", tc_map.get(difficulty, "O(n)"))

    if "{{space_complexity}}" in filled:
        sc_map = {"easy": "O(n)", "medium": "O(log n)", "hard": "O(1)"}
        filled = filled.replace("{{space_complexity}}", sc_map.get(difficulty, "O(n)"))

    if "{{forbidden_api}}" in filled:
        forbidden = "N/A" if difficulty == "easy" else "collections.OrderedDict, functools.lru_cache"
        filled = filled.replace("{{forbidden_api}}", forbidden)

    # function_signature is deterministic for known topics
    sig_map = {
        "链表": "def insert(head, val): -> ListNode",
        "二叉树遍历": "def inorder(root): -> List[int]",
        "LRU 缓存": "class LRUCache: def __init__(self, capacity: int): ...",
    }
    if "{{function_signature}}" in filled:
        filled = filled.replace("{{function_signature}}", sig_map.get(kp, "def solve():"))

    # code_snippet placeholder is intentionally left for the LLM;
    # we wrap it in a structured prompt.
    llm_sub_prompt = ""
    if "{{code_snippet}}" in filled:
        llm_sub_prompt = (
            f"Generate a {difficulty}-difficulty Python code snippet about '{kp}' "
            f"containing exactly one logical error suitable for a debugging exercise. "
            f"Length: {meta['code_length_lines']} lines."
        )
        filled = filled.replace("{{code_snippet}}", "[LLM_GENERATED_CODE_SNIPPET]")

    return {
        "template_id": template["template_id"],
        "question_type": template["question_type"],
        "difficulty": difficulty,
        "knowledge_point": kp,
        "cognitive_level": meta["cognitive_level"],
        "time_limit_seconds": meta["time_limit_seconds"],
        "hint_count": meta["hint_count"],
        "student_prompt": filled,
        "llm_sub_prompt": llm_sub_prompt,
        "version": VERSION,
    }


def generate_item(
    student_profile: Dict[str, Any],
    topic_syllabus: Optional[List[str]] = None,
    excluded_types: Optional[List[str]] = None,
    rng_seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    End-to-end item generation given a student profile.
    """
    difficulty = student_profile.get("current_difficulty", "medium")
    weak_points = list(student_profile.get("weak_points", []))

    template = select_template(difficulty, weak_points, excluded_types, rng_seed)
    item = fill_template(template, difficulty, weak_points, topic_syllabus, rng_seed)
    return item


# ---------------------------------------------------------------------------
# Example usage (reproducible)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    example_profile = {
        "current_difficulty": "medium",
        "weak_points": ["链表", "二叉树遍历"],
    }
    item = generate_item(example_profile, rng_seed=42)
    print(json.dumps(item, ensure_ascii=False, indent=2))

"""
Agent factory that loads version-locked prompts from prompts/*.json.
"""

import json
import os
from typing import Dict, Any, List, Callable


def _load_prompt(agent_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Load a prompt JSON and format placeholders with config."""
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", f"{agent_name}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Format any placeholders in instructions
    data["instructions"] = data["instructions"].format(**config)
    # Format guardrails if they contain placeholders
    data["guardrails"] = [
        g.format(**config) if "{" in g else g for g in data.get("guardrails", [])
    ]
    return data


def build_agents(
    student_profile,
    get_student_profile_summary_fn: Callable,
    update_student_profile_fn: Callable,
    transfer_fns: Dict[str, Callable],
    model: str = None,
    course_name: str = "数据结构与算法",
    rounds: int = 1,
):
    """
    Build the four Swarm agents using dynamically loaded prompts.

    Args:
        student_profile: The StudentProfile instance (used by transfer functions).
        get_student_profile_summary_fn: Bound get_student_profile_summary callable.
        update_student_profile_fn: Bound update_student_profile callable.
        transfer_fns: Dict of transfer functions from transfers.py.
        model: LLM model name.
        course_name: Course name for prompt formatting.
        rounds: Number of rounds for prompt formatting.
    """
    try:
        from swarm import Agent
    except ImportError as e:
        raise ImportError(
            "The 'swarm' package is required. Install it from: "
            "pip install git+https://github.com/openai/swarm.git"
        ) from e

    config = {
        "course_name": course_name,
        "rounds": rounds,
    }

    # Performance data template used in course_tutor prompt
    PERFORMANCE_DATA_TEMPLATE = json.dumps({
        "correct": False,
        "topic": "知识点名称",
        "score": 0,
        "question_details": {
            "question_type": "题目类型",
            "difficulty_level": "当前难度级别",
            "knowledge_points": ["知识点1", "知识点2"],
            "time_spent": 300
        },
        "answer_process": {
            "attempts": 1,
            "error_types": ["错误类型"],
            "code_quality": {
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "code_style": "N/A"
            }
        },
        "learning_behavior": {
            "used_hints": False,
            "reference_materials": [],
            "solution_approach": "解题方式"
        },
        "assessment_dimensions": {
            "concept_understanding": 0.6,
            "problem_solving": 0.5,
            "code_implementation": 0.0,
            "learning_attitude": 0.8
        }
    }, ensure_ascii=False, indent=2)

    EXAMPLE_CALL = """
update_student_profile({
    "correct": False,
    "topic": "链表",
    "score": 0,
    "question_details": {
        "question_type": "概念题",
        "difficulty_level": "medium",
        "knowledge_points": ["链表", "时间复杂度"],
        "time_spent": 300
    },
    "answer_process": {
        "attempts": 1,
        "error_types": ["概念理解错误"],
        "code_quality": {
            "time_complexity": "N/A",
            "space_complexity": "N/A",
            "code_style": "N/A"
        }
    },
    "learning_behavior": {
        "used_hints": False,
        "reference_materials": [],
        "solution_approach": "独立思考"
    },
    "assessment_dimensions": {
        "concept_understanding": 0.4,
        "problem_solving": 0.5,
        "code_implementation": 0.0,
        "learning_attitude": 0.8
    }
})
"""

    coordinator_data = _load_prompt("coordinator", config)
    tester_data = _load_prompt("course_tester", config)
    tutor_data = _load_prompt("course_tutor", config)
    grader_data = _load_prompt("final_grader", config)

    # Append template/example to tutor instructions
    tutor_instructions = tutor_data["instructions"]
    tutor_instructions = tutor_instructions.replace(
        "数据格式示例：",
        f"数据格式示例：\n{PERFORMANCE_DATA_TEMPLATE}\n"
    )
    tutor_instructions = tutor_instructions.replace(
        "调用示例：",
        f"调用示例：\n{EXAMPLE_CALL}\n"
    )

    coordinator = Agent(
        name=coordinator_data.get("agent_name", "Coordinator"),
        model=model or coordinator_data.get("model", "gpt-4o-mini"),
        instructions=coordinator_data["instructions"],
        functions=[transfer_fns["transfer_to_tester"], transfer_fns["transfer_to_grader"]]
    )

    course_tester = Agent(
        name=tester_data.get("agent_name", "CourseTester"),
        model=model or tester_data.get("model", "gpt-4o-mini"),
        instructions=tester_data["instructions"],
        functions=[
            get_student_profile_summary_fn,
            update_student_profile_fn,
            transfer_fns["transfer_to_tutor"]
        ]
    )

    course_tutor = Agent(
        name=tutor_data.get("agent_name", "CourseTutor"),
        model=model or tutor_data.get("model", "gpt-4o-mini"),
        instructions=tutor_instructions,
        functions=[
            get_student_profile_summary_fn,
            update_student_profile_fn,
            transfer_fns["transfer_to_coordinator"]
        ]
    )

    final_grader = Agent(
        name=grader_data.get("agent_name", "FinalGrader"),
        model=model or grader_data.get("model", "gpt-4o-mini"),
        instructions=grader_data["instructions"],
        functions=[get_student_profile_summary_fn, transfer_fns["transfer_to_exit"]]
    )

    return {
        "coordinator": coordinator,
        "course_tester": course_tester,
        "course_tutor": course_tutor,
        "final_grader": final_grader,
    }

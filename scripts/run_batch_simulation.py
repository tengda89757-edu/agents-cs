#!/usr/bin/env python3
"""
Batch simulation for reproducibility testing.
Uses reproducible (no-op) hooks so the run is deterministic aside from LLM calls.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from openai import OpenAI

try:
    from swarm import Swarm
except ImportError as e:
    print("Error: 'swarm' package is required. Install with:")
    print("  pip install git+https://github.com/openai/swarm.git")
    sys.exit(1)

from orchestration import (
    StudentProfile,
    update_student_profile,
    get_student_profile_summary,
    make_transfer_to_coordinator,
    make_transfer_to_tester,
    make_transfer_to_tutor,
    make_transfer_to_grader,
    make_transfer_to_exit,
    build_agents,
    run_batch_simulation,
    REPRODUCIBLE_HOOKS,
    COURSE_NAME,
    ROUNDS,
)


def main():
    load_dotenv()
    base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("OPENAI_API_KEY", "ollama")
    model = os.getenv("MODEL_NAME", "gpt-4o-mini")

    client = Swarm(OpenAI(base_url=base_url, api_key=api_key))
    student_profile = StudentProfile()

    def bound_update_student_profile(performance_data):
        return update_student_profile(student_profile, performance_data)

    def bound_get_student_profile_summary():
        return get_student_profile_summary(student_profile)

    transfer_fns = {
        "transfer_to_coordinator": make_transfer_to_coordinator(
            student_profile, "CourseTutor", "Coordinator", hooks=REPRODUCIBLE_HOOKS
        ),
        "transfer_to_tester": make_transfer_to_tester(
            student_profile, "Coordinator", "CourseTester", hooks=REPRODUCIBLE_HOOKS
        ),
        "transfer_to_tutor": make_transfer_to_tutor(
            student_profile, "CourseTester", "CourseTutor", hooks=REPRODUCIBLE_HOOKS
        ),
        "transfer_to_grader": make_transfer_to_grader(
            student_profile, "Coordinator", "FinalGrader", ROUNDS, hooks=REPRODUCIBLE_HOOKS
        ),
        "transfer_to_exit": make_transfer_to_exit(
            student_profile, "FinalGrader", hooks=REPRODUCIBLE_HOOKS
        ),
    }

    agents = build_agents(
        student_profile=student_profile,
        get_student_profile_summary_fn=bound_get_student_profile_summary,
        update_student_profile_fn=bound_update_student_profile,
        transfer_fns=transfer_fns,
        model=model,
        course_name=COURSE_NAME,
        rounds=ROUNDS,
    )

    # A minimal canned conversation for batch testing
    conversation_turns = [
        "我准备好了",
        "选 A",
        "明白了",
        "没有问题",
    ]

    result = run_batch_simulation(
        client=client,
        agents=agents,
        student_profile=student_profile,
        conversation_turns=conversation_turns,
    )

    print("Batch simulation complete.")
    print(f"Final agent: {result['final_agent']}")
    print(f"Total questions: {result['total_questions']}")
    print(f"Current difficulty: {result['current_difficulty']}")


if __name__ == "__main__":
    main()

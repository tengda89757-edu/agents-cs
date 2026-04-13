#!/usr/bin/env python3
"""
Interactive demo entry point.
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
    run_demo_loop,
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

    # Bind profile to profile functions
    def bound_update_student_profile(performance_data):
        return update_student_profile(student_profile, performance_data)

    def bound_get_student_profile_summary():
        return get_student_profile_summary(student_profile)

    transfer_fns = {
        "transfer_to_coordinator": make_transfer_to_coordinator(
            student_profile, "CourseTutor", "Coordinator"
        ),
        "transfer_to_tester": make_transfer_to_tester(
            student_profile, "Coordinator", "CourseTester"
        ),
        "transfer_to_tutor": make_transfer_to_tutor(
            student_profile, "CourseTester", "CourseTutor"
        ),
        "transfer_to_grader": make_transfer_to_grader(
            student_profile, "Coordinator", "FinalGrader", ROUNDS
        ),
        "transfer_to_exit": make_transfer_to_exit(
            student_profile, "FinalGrader"
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

    run_demo_loop(agents["coordinator"], client, stream=False, debug=False)


if __name__ == "__main__":
    main()

"""
Transfer functions between agents.

All side effects (sleep, print) are injected via hooks so that the core
logic remains pure and reproducible in test / batch mode.
"""

from typing import Dict, Any, Callable
from .student_profile import StudentProfile


import builtins

# Default production hooks (with delays and prints)
PRODUCTION_HOOKS: Dict[str, Callable[..., Any]] = {
    "sleep": __import__("time").sleep,
    "print": builtins.print,
}

# Reproducible hooks (no-ops) for testing and batch simulation
REPRODUCIBLE_HOOKS: Dict[str, Callable[..., Any]] = {
    "sleep": lambda *a, **k: None,
    "print": lambda *a, **k: None,
}


def _log_interaction(student_profile: StudentProfile, from_agent: str, to_agent: str, reason: str, context: Dict[str, Any]) -> None:
    from datetime import datetime
    student_profile.interaction_history.append({
        "timestamp": datetime.now(),
        "from_agent": from_agent,
        "to_agent": to_agent,
        "reason": reason,
        "context": context,
    })


def _record_decision(student_profile: StudentProfile, agent_name: str, decision: str, rationale: str, impact: str) -> None:
    from datetime import datetime
    student_profile.learning_path.append({
        "timestamp": datetime.now(),
        "agent": agent_name,
        "decision": decision,
        "rationale": rationale,
        "impact": impact,
    })


def make_transfer_to_coordinator(student_profile: StudentProfile, course_tutor_name: str, coordinator_name: str, hooks: Dict[str, Callable] = None):
    """Return the transfer_to_coordinator function bound to the given profile."""
    hooks = hooks or PRODUCTION_HOOKS

    def transfer_to_coordinator():
        hooks["sleep"](1)
        _log_interaction(
            student_profile,
            from_agent=course_tutor_name,
            to_agent=coordinator_name,
            reason="完成当前轮次辅导，返回协调员进行下一步安排",
            context={
                "current_difficulty": student_profile.current_difficulty,
                "current_mastery": student_profile.calculate_mastery()
            }
        )
        _record_decision(
            student_profile,
            agent_name=course_tutor_name,
            decision="转换到协调员",
            rationale="当前轮次辅导完成",
            impact="协调员将决定是继续下一轮还是结束测试"
        )
        # The actual agent object must be resolved by the caller
        return {"target_agent": coordinator_name}

    return transfer_to_coordinator


def make_transfer_to_tester(student_profile: StudentProfile, coordinator_name: str, course_tester_name: str, hooks: Dict[str, Callable] = None):
    hooks = hooks or PRODUCTION_HOOKS

    def transfer_to_tester():
        hooks["sleep"](1)
        _log_interaction(
            student_profile,
            from_agent=coordinator_name,
            to_agent=course_tester_name,
            reason="开始新一轮测试",
            context={
                "current_difficulty": student_profile.current_difficulty,
                "strong_points": list(student_profile.strong_points),
                "weak_points": list(student_profile.weak_points)
            }
        )
        _record_decision(
            student_profile,
            agent_name=coordinator_name,
            decision="转换到测试官",
            rationale="需要进行新一轮的知识测试",
            impact="测试官将根据当前难度和知识点情况出题"
        )
        hooks["print"]("接下来，我出题考核。")
        hooks["sleep"](1.5)
        return {"target_agent": course_tester_name}

    return transfer_to_tester


def make_transfer_to_tutor(student_profile: StudentProfile, course_tester_name: str, course_tutor_name: str, hooks: Dict[str, Callable] = None):
    hooks = hooks or PRODUCTION_HOOKS

    def transfer_to_tutor():
        hooks["sleep"](1)
        _log_interaction(
            student_profile,
            from_agent=course_tester_name,
            to_agent=course_tutor_name,
            reason="完成测试，需要辅导",
            context={
                "last_performance": student_profile.performance_history[-1] if student_profile.performance_history else None,
                "current_difficulty": student_profile.current_difficulty
            }
        )
        _record_decision(
            student_profile,
            agent_name=course_tester_name,
            decision="转换到辅导员",
            rationale="学生完成测试，需要针对性辅导",
            impact="辅导员将根据测试表现提供相应的指导"
        )
        hooks["print"]("接下来，我将把你转给课程辅导员进行进一步的辅导。")
        hooks["sleep"](1.5)
        return {"target_agent": course_tutor_name}

    return transfer_to_tutor


def make_transfer_to_grader(student_profile: StudentProfile, coordinator_name: str, final_grader_name: str, rounds: int, hooks: Dict[str, Callable] = None):
    hooks = hooks or PRODUCTION_HOOKS

    def transfer_to_grader():
        hooks["sleep"](1)
        _log_interaction(
            student_profile,
            from_agent=coordinator_name,
            to_agent=final_grader_name,
            reason="完成所有测试轮次，进行最终评估",
            context={
                "total_rounds": rounds,
                "final_difficulty": student_profile.current_difficulty,
                "mastery": student_profile.calculate_mastery(),
                "topic_scores": student_profile.topic_scores
            }
        )
        _record_decision(
            student_profile,
            agent_name=coordinator_name,
            decision="转换到最终评分官",
            rationale=f"已完成{rounds}轮测试，需要进行综合评估",
            impact="最终评分官将对整体学习表现进行多维度评估"
        )
        hooks["print"]("正在转到最终评分官...")
        hooks["sleep"](1.5)
        return {"target_agent": final_grader_name}

    return transfer_to_grader


def make_transfer_to_exit(student_profile: StudentProfile, final_grader_name: str, hooks: Dict[str, Callable] = None):
    hooks = hooks or PRODUCTION_HOOKS

    def transfer_to_exit():
        _log_interaction(
            student_profile,
            from_agent=final_grader_name,
            to_agent="System",
            reason="完成所有评估，结束测试",
            context={
                "final_state": {
                    "total_questions": student_profile.total_questions,
                    "mastery": student_profile.calculate_mastery(),
                    "final_difficulty": student_profile.current_difficulty,
                    "strong_points": list(student_profile.strong_points),
                    "weak_points": list(student_profile.weak_points)
                }
            }
        )
        _record_decision(
            student_profile,
            agent_name=final_grader_name,
            decision="结束测试",
            rationale="已完成所有测试和评估环节",
            impact="生成最终评估报告并结束测试流程"
        )
        hooks["print"]("测试结束，退出")
        raise SystemExit(0)

    return transfer_to_exit

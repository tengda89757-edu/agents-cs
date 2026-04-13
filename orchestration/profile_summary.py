"""
get_student_profile_summary — pure logic, no side effects.
"""

import json
from typing import Dict, Any
from .student_profile import StudentProfile


def get_student_profile_summary(student_profile: StudentProfile) -> str:
    """Return a formatted summary of the student profile."""
    mastery = student_profile.calculate_mastery()
    learning_path = student_profile.learning_path
    interactions = student_profile.interaction_history
    decisions = student_profile.decision_explanations

    def fmt_item(item: Dict[str, Any]) -> Dict[str, Any]:
        # safely format any timestamp if present
        out = dict(item)
        if "timestamp" in out:
            ts = out["timestamp"]
            try:
                out["timestamp"] = ts.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
        return out

    summary = {
        "基本信息": {
            "总答题数": student_profile.total_questions,
            "正确率": f"{mastery:.2%}",
            "当前难度": student_profile.current_difficulty,
        },
        "知识掌握": {
            "知识点得分": student_profile.topic_scores,
            "强项": list(student_profile.strong_points),
            "弱项": list(student_profile.weak_points)
        },
        "学习轨迹": {
            "难度调整历史": [fmt_item(item) for item in learning_path],
            "智能体交互": [fmt_item(item) for item in interactions[-5:]],
            "决策解释": [fmt_item(item) for item in decisions[-5:]],
        }
    }

    return f"""根据学生档案分析：

基本信息：
- 总答题数：{summary['基本信息']['总答题数']}
- 正确率：{summary['基本信息']['正确率']}
- 当前难度：{summary['基本信息']['当前难度']}

知识掌握情况：
- 知识点得分：{summary['知识掌握']['知识点得分']}
- 强项：{summary['知识掌握']['强项']}
- 弱项：{summary['知识掌握']['弱项']}

最近的学习轨迹：
1. 难度调整历史：
{json.dumps(summary['学习轨迹']['难度调整历史'], indent=2, ensure_ascii=False)}

2. 最近的智能体交互：
{json.dumps(summary['学习轨迹']['智能体交互'], indent=2, ensure_ascii=False)}

3. 最近的决策解释：
{json.dumps(summary['学习轨迹']['决策解释'], indent=2, ensure_ascii=False)}
"""

"""
Runnable entry points for the tutoring system.
"""

import json
import os
from typing import Dict, Any, Optional


def _process_and_print_streaming_response(response):
    content = ""
    last_sender = ""
    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]
        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]
        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")
        if "delim" in chunk and chunk.get("delim") == "end" and content:
            print()
            content = ""
        if "response" in chunk:
            return chunk["response"]


def _pretty_print_messages(messages) -> None:
    for message in messages:
        if message.get("role") != "assistant":
            continue
        print(f"\033[94m{message.get('sender', 'Agent')}\033[0m:", end=" ")
        if message.get("content"):
            print(message["content"])
        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")


def run_demo_loop(starting_agent, client, context_variables=None, stream=False, debug=False) -> None:
    """
    Interactive demo loop.

    Args:
        starting_agent: A swarm Agent instance.
        client: A swarm.Swarm client instance.
        context_variables: Optional context dict.
        stream: Whether to stream responses.
        debug: Whether to enable debug mode.
    """
    from swarm import Swarm
    print("Starting Swarm CLI 🐝...")

    messages = [{"role": "user", "content": "你好，我是学生，请开始测试"}]
    agent = starting_agent

    while True:
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        if stream:
            response = _process_and_print_streaming_response(response)
        else:
            _pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent
        user_input = input("\033[90m学生\033[0m: ")
        messages.append({"role": "user", "content": user_input})


def run_batch_simulation(
    client,
    agents: Dict[str, Any],
    student_profile,
    conversation_turns: list,
    context_variables=None,
    stream=False,
    debug=False,
) -> Dict[str, Any]:
    """
    Non-interactive batch simulation for reproducibility testing.

    Args:
        client: swarm.Swarm client instance.
        agents: Dict of agent objects.
        student_profile: StudentProfile instance.
        conversation_turns: List of user message strings.
        context_variables: Optional context dict.

    Returns:
        Dict with final messages, final agent name, and student profile state.
    """
    messages = [{"role": "user", "content": "你好，我是学生，请开始测试"}]
    for turn in conversation_turns:
        messages.append({"role": "user", "content": turn})

    agent = agents["coordinator"]
    for _ in range(len(conversation_turns)):
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )
        messages.extend(response.messages)
        agent = response.agent

    return {
        "messages": messages,
        "final_agent": agent.name if hasattr(agent, "name") else str(agent),
        "total_questions": student_profile.total_questions,
        "current_difficulty": student_profile.current_difficulty,
    }

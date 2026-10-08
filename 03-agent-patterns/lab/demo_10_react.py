"""
Demo 12 · ReAct：Thought → Action → Observation
================================================

配套：第 12 节《ReAct：Thought-Action-Observation 循环》

ReAct 是 2022 年 Yao 等人提出的范式，**早于 OpenAI Function Calling**。
它的核心：让模型在每一步**先输出一段思考（Thought），再输出一个行动（Action）**，
我们用正则把它解出来执行，把结果以 Observation 拼回 prompt，循环往复。

本 demo 故意**走"老 paradigm"**：
  - 不用 OpenAI tool_calls
  - 全靠 prompt 约定输出格式
  - 用正则解析 Thought / Action

跑完之后你会感觉到——为什么 2023 年 OpenAI Function Calling 出来后，
所有人都迫不及待地切过去（demo_13 / demo_14 也都用 tool_calls 写）。

跑法：
    python demo_12_react.py
"""

from __future__ import annotations

import re

from _env import chat as llm_chat
from toy_agent_base import TASKS, make_llm, registry

client, MODEL = make_llm()


REACT_PROMPT_TEMPLATE = """你是一个会思考的助手，严格按以下格式回应。每一轮你只输出一对 Thought 和 Action，不要多输出。

# 可用工具
{tools}

# 输出格式（严格遵守）
Thought: 你这一步的思考
Action: 以下两种之一
  - tool_name(arg1="value1", arg2="value2")  调用工具
  - Finish[最终答案]                          给出最终答案

# 当前任务
{question}

# 历史记录（已经发生的步骤）
{history}

请输出下一步的 Thought 和 Action："""


def parse_react_output(text: str):
    """从 LLM 输出里抠出 (Thought, Action)。

    这是 ReAct 老 paradigm 最脆的一环：
      - 模型多说一句话就崩
      - 模型把 Action 换行了就崩
      - 模型在 Action 后面又写了一段就崩
    工程版本一般要做大量的 fallback。这里我们做一些简单容错。
    """
    # Thought
    t_match = re.search(r"Thought:\s*(.*?)(?=Action:|$)", text, re.DOTALL)
    thought = t_match.group(1).strip() if t_match else ""

    # Action（取第一行 Action: ... 之后到下一个 Thought/Action 之前）
    a_match = re.search(
        r"Action:\s*(.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)",
        text,
        re.DOTALL,
    )
    action = a_match.group(1).strip() if a_match else ""
    return thought, action


def parse_action(action: str):
    """解析 Action 字符串。

    支持两种：
      - Finish[xxx]
      - tool_name(arg="value", arg2="value2")
    """
    # Finish
    finish = re.match(r"Finish\[(.*)\]", action, re.DOTALL)
    if finish:
        return ("finish", finish.group(1), None)

    # tool 调用
    name_match = re.match(r"(\w+)\(", action)
    args_match = re.search(r"\((.*)\)", action)
    if not name_match or not args_match:
        return ("error", f"无法解析: {action}", None)
    name = name_match.group(1)
    # 形如 city="北京", weather="晴"
    kwargs = dict(re.findall(r'(\w+)\s*=\s*"([^"]*)"', args_match.group(1)))
    return ("tool", name, kwargs)


def run_react(question: str, max_steps: int = 6, verbose: bool = True) -> str:
    history_lines: list[str] = []

    for step in range(1, max_steps + 1):
        prompt = REACT_PROMPT_TEMPLATE.format(
            tools=registry.get_tools_description(),
            question=question,
            history="\n".join(history_lines) if history_lines else "（无）",
        )
        msg = llm_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            client=client,
            model=MODEL,
        )
        raw = msg.content or ""
        thought, action = parse_react_output(raw)

        if verbose:
            print(f"\n[Step {step}]")
            print(f"  💭 Thought:     {thought}")
            print(f"  ⚡ Action:      {action}")

        kind, val, args = parse_action(action)

        if kind == "finish":
            if verbose:
                print(f"  🎯 Finish:      {val}")
            return val

        if kind == "error":
            obs = f"❌ 解析失败: {val}"
        else:
            obs = registry.invoke(val, args or {})

        if verbose:
            print(f"  👁 Observation: {obs[:120]}{'...' if len(obs) > 120 else ''}")

        history_lines.append(f"Thought: {thought}")
        history_lines.append(f"Action: {action}")
        history_lines.append(f"Observation: {obs}")

    return "⚠️ 达到最大步数仍未 Finish"


if __name__ == "__main__":
    for i, q in enumerate(TASKS, 1):
        print("\n" + "=" * 60)
        print(f"任务 {i}: {q}")
        print("=" * 60)
        ans = run_react(q)
        print(f"\n🎯 答案: {ans}")

    print("\n\n" + "=" * 60)
    print("🎯 ReAct 的特点：")
    print("  - 优点：随机应变，每步看了 Observation 再决定下一步")
    print("  - 缺点 1：纯靠 prompt + 正则解析，模型一不规矩就崩")
    print("  - 缺点 2：步多 → token 多 → 成本高")
    print("  - 缺点 3：没有'整体计划'感，遇到长任务容易在中间走偏")
    print()
    print("  下一节我们看 Plan-and-Solve：先规划再执行，看看是不是更稳。")
    print("=" * 60)

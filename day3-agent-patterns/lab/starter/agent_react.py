"""
Day 3 Lab Part 1 · ReAct 范式骨架 —— 学生填空

主循环和工具集都已写好；你只需要补上：
  - REACT_PROMPT_TEMPLATE 的具体内容
  - parse_react_output / parse_action 的解析逻辑

参考：第 12 节 + demos/demo_12_react.py（实在卡住时再看）
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from toy_agent_base import TASKS, make_llm, registry


# ----------------------------------------------------------------
# TODO ① 完成 ReAct 的 prompt 模板
# 要求：让模型每次只输出一对 Thought + Action；Action 支持工具调用 + Finish
# ----------------------------------------------------------------
REACT_PROMPT_TEMPLATE = """你是一个会思考的助手...

# 可用工具
{tools}

# 当前任务
{question}

# 历史
{history}

请输出下一步:"""   # ← 你的代码（重写整段）


def parse_react_output(text: str):
    """解析 LLM 输出里的 (Thought, Action)。"""
    # ----------------------------------------------------------------
    # TODO ② 用正则把 Thought 和 Action 抠出来
    # 提示：注意模型可能多说一句、可能把 Action 换行、可能末尾还跟一段
    # ----------------------------------------------------------------
    thought = ""    # ← 你的代码
    action = ""     # ← 你的代码
    return thought, action


def parse_action(action: str):
    """把 Action 字符串解析成 (kind, name_or_answer, args_dict)。

    kind ∈ {"finish", "tool", "error"}
    """
    # ----------------------------------------------------------------
    # TODO ③ 解析两种格式：
    #   - Finish[最终答案]      → ("finish", "最终答案", None)
    #   - tool_name(arg="value", ...)  → ("tool", "tool_name", {arg: value, ...})
    # 解析失败 → ("error", 报错原因, None)
    # ----------------------------------------------------------------
    return ("error", "TODO 未实现", None)


def run_react(question: str, max_steps: int = 6) -> str:
    client, MODEL = make_llm()
    history_lines: list[str] = []

    for step in range(1, max_steps + 1):
        prompt = REACT_PROMPT_TEMPLATE.format(
            tools=registry.get_tools_description(),
            question=question,
            history="\n".join(history_lines) if history_lines else "（无）",
        )
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = resp.choices[0].message.content or ""
        thought, action = parse_react_output(raw)
        print(f"\n[Step {step}]\n  💭 {thought}\n  ⚡ {action}")

        kind, val, args = parse_action(action)

        if kind == "finish":
            return val
        if kind == "error":
            obs = f"❌ 解析失败: {val}"
        else:
            obs = registry.invoke(val, args or {})
        print(f"  👁 {obs[:120]}")

        history_lines += [f"Thought: {thought}", f"Action: {action}", f"Observation: {obs}"]

    return "⚠️ 达到最大步数仍未 Finish"


if __name__ == "__main__":
    for q in TASKS[:3]:
        print("\n" + "=" * 60)
        print(f"任务: {q}")
        print("=" * 60)
        print(f"\n🎯 答案: {run_react(q)}")

"""
Day 3 Lab Part 2 · Plan-and-Solve 骨架 —— 填空

要补的三件事：
  ① Planner 的 prompt（让模型输出 JSON 数组的步骤列表）
  ② Executor 复用 Day2 的最小 Agent Loop
  ③ Aggregator 把所有步骤结果汇总

参考：第 13 节 + demos/demo_13_plan_and_solve.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from toy_agent_base import TASKS, make_llm, registry


# ----------------------------------------------------------------
# TODO ① 写 Planner prompt
# 要求：让模型把用户问题拆成 2-5 个子任务，**严格输出 JSON 数组**
# ----------------------------------------------------------------
PLANNER_PROMPT = """你是规划器...   # ← 你的代码

可用工具：
{tools}

用户问题：{question}

输出（严格 JSON）：
"""


def make_plan(question: str) -> list[str]:
    client, MODEL = make_llm()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": PLANNER_PROMPT.format(
                tools=registry.get_tools_description(), question=question,
            ),
        }],
        temperature=0,
    )
    raw = (resp.choices[0].message.content or "").strip()
    # ----------------------------------------------------------------
    # TODO ②（小）从 raw 里抠出 JSON 数组并 json.loads
    # 提示：模型可能把 JSON 包在 ```json ... ``` 里，记得剥掉
    # 失败时返回 [question]（让一次执行兜底）
    # ----------------------------------------------------------------
    return [question]   # ← 你的代码


def execute_step(step_desc: str, prior_results: list[str]) -> str:
    """执行一个子任务。复用 Day2 的最小 Agent Loop。"""
    # ----------------------------------------------------------------
    # TODO ③ 复用 Day2 你写的最小 Agent Loop（带 tool_calls 的那版）
    # 提示：messages 里 system 说"你在执行某大任务的子步骤"，
    #       user 说"前面步骤的结果是 X，本步任务是 Y"
    # 关键：仍然要走 tools=registry.to_schemas() / tool_choice="auto"
    # ----------------------------------------------------------------
    return "TODO 未实现"


def aggregate(question: str, plan: list[str], results: list[str]) -> str:
    """让 LLM 把所有子结果汇总成最终答案。"""
    # ----------------------------------------------------------------
    # TODO ④ 写汇总 prompt + 调一次 LLM
    # ----------------------------------------------------------------
    return "TODO 未实现"


def run_plan_and_solve(question: str) -> str:
    print("📋 Planner...")
    plan = make_plan(question)
    for i, s in enumerate(plan, 1):
        print(f"  {i}. {s}")

    results = []
    for i, step in enumerate(plan, 1):
        print(f"\n⚙️ Step {i}: {step}")
        r = execute_step(step, results)
        print(f"  → {r[:150]}")
        results.append(r)

    print("\n📝 Aggregator...")
    return aggregate(question, plan, results)


if __name__ == "__main__":
    for q in TASKS[:3]:
        print("\n" + "=" * 60)
        print(f"任务: {q}")
        print("=" * 60)
        print(f"\n🎯 答案: {run_plan_and_solve(q)}")

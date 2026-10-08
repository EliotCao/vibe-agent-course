"""
Demo 13 · Plan-and-Solve：先规划再执行
======================================

配套：第 11 节《Plan-and-Solve：先规划再执行》

跟 ReAct 反过来：
  - ReAct：走一步看一步（信息收集型）
  - Plan-and-Solve：先在脑里把整盘棋画出来，再逐步执行（流程明确型）

实现：
  ① Planner：用 LLM 把任务拆成 N 步具体子任务，输出一个步骤列表
  ② Executor：逐个执行每一步，每步可以调工具（用 Function Calling）
  ③ Aggregator：拿到所有步骤的结果，由 LLM 汇总成最终答案

跟 第2章 的最小 Agent Loop 比，多了一个"规划阶段"。
跟 demo_10 的 ReAct 比，少了"边走边看"的自由度。

跑法：
    python demo_11_plan_and_solve.py
"""

from __future__ import annotations

import json

from _env import chat as llm_chat
from toy_agent_base import TASKS, make_llm, registry

client, MODEL = make_llm()


# ============================================================
# Planner：把用户问题拆成步骤列表
# ============================================================
PLANNER_PROMPT = """你是一个任务规划器。把用户的问题拆成一个**有序的子任务列表**。

可用工具：
{tools}

# 规则
- 每一步必须是"可以独立执行 + 拿到中间结果"的子任务
- 步骤数控制在 2-5 个
- 如果用户的问题不需要工具，直接返回一个步骤就行（"基于已知信息回答"）
- 严格输出 JSON 数组，每项一个字符串描述子任务

# 用户问题
{question}

# 输出（严格 JSON 数组，不要任何其他文字）
"""


def make_plan(question: str) -> list[str]:
    msg = llm_chat(
        messages=[
            {
                "role": "user",
                "content": PLANNER_PROMPT.format(
                    tools=registry.get_tools_description(),
                    question=question,
                ),
            }
        ],
        temperature=0,
        client=client,
        model=MODEL,
    )
    raw = msg.content or "[]"
    # 容错：模型可能用 ```json ``` 包裹
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].strip()
    start = raw.find("[")
    end = raw.rfind("]")
    if start == -1 or end == -1:
        return [question]
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return [question]


# ============================================================
# Executor：执行单个子任务（用 Function Calling 把活干好）
# ============================================================
def execute_step(step_desc: str, prior_results: list[str], max_iters: int = 4) -> str:
    """执行一个子任务，返回字符串结果。复用 第2章 的最小 Agent Loop。"""
    context = (
        "前面步骤的结果（供你参考）：\n" + "\n".join(f"- {r}" for r in prior_results)
        if prior_results
        else "（这是第一步，没有前序结果）"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "你正在执行一个大任务里的子步骤。需要时可以调用工具。"
                "拿到结果后用一句话总结。"
            ),
        },
        {"role": "user", "content": f"{context}\n\n本步骤任务: {step_desc}"},
    ]

    for _ in range(max_iters):
        msg = llm_chat(
            messages=messages,
            tools=registry.to_schemas(),
            tool_choice="auto",
            temperature=0,
            client=client,
            model=MODEL,
        )

        if not msg.tool_calls:
            return msg.content or ""

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = registry.invoke(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})

    return "（达到子任务最大步数）"


# ============================================================
# Aggregator：汇总所有步骤结果
# ============================================================
AGG_PROMPT = """以下是某个用户问题的多步骤执行结果，请基于这些结果给用户一个简洁的最终答案。

用户问题：{question}

执行步骤与结果：
{steps_summary}

最终答案："""


def aggregate(question: str, plan: list[str], results: list[str]) -> str:
    summary = "\n".join(f"步骤 {i+1}: {p}\n  结果: {r}" for i, (p, r) in enumerate(zip(plan, results)))
    msg = llm_chat(
        messages=[{"role": "user", "content": AGG_PROMPT.format(question=question, steps_summary=summary)}],
        temperature=0,
        client=client,
        model=MODEL,
    )
    return msg.content or ""


# ============================================================
# 把三段拼起来
# ============================================================
def run_plan_and_solve(question: str, verbose: bool = True) -> str:
    if verbose:
        print(f"📋 [Planner] 正在规划...")
    plan = make_plan(question)
    if verbose:
        for i, step in enumerate(plan, 1):
            print(f"   {i}. {step}")

    results = []
    for i, step in enumerate(plan, 1):
        if verbose:
            print(f"\n⚙️ [Executor 步骤 {i}] {step}")
        r = execute_step(step, results)
        if verbose:
            print(f"   结果: {r[:200]}{'...' if len(r) > 200 else ''}")
        results.append(r)

    if verbose:
        print(f"\n📝 [Aggregator] 正在汇总...")
    return aggregate(question, plan, results)


if __name__ == "__main__":
    for i, q in enumerate(TASKS, 1):
        print("\n" + "=" * 60)
        print(f"任务 {i}: {q}")
        print("=" * 60)
        ans = run_plan_and_solve(q)
        print(f"\n🎯 最终答案: {ans}")

    print("\n\n" + "=" * 60)
    print("🎯 Plan-and-Solve 的特点：")
    print("  - 优点 1：步骤清晰，token 比 ReAct 省（一次规划 + 多步执行）")
    print("  - 优点 2：适合多步硬任务（比如'查 N 个城市再汇总'）")
    print("  - 缺点 1：规划阶段本身就可能错——模型对'要拆成几步'判断不准")
    print("  - 缺点 2：执行中如果中途某步失败，整个 plan 可能就废了")
    print("           （工业版通常加 Replan：发现失败就回头重新规划）")
    print()
    print("  下一节我们看 Reflection：让 Agent 自己回头检查答案。")
    print("=" * 60)

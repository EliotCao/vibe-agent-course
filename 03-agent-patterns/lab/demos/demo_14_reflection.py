"""
Demo 14 · Reflection：让 Agent 自己回头看一眼
=============================================

配套：第 14 节《Reflection：让 Agent 自我反思与修正》

Reflection 是一个**包装层**：它不改变底层 Agent 怎么工作，
只是在底层 Agent 给出答案后**多走一步**：
  ① 让同一个模型扮演"评审员"，挑出答案里可能有的问题
  ② 如果有问题 → 让原 Agent 拿着批注重新作答
  ③ 重复 N 次或直到评审员说"没问题"

本 demo 把 Reflection 包在 demo_13 (Plan-and-Solve) 的外面。
你可以替换成 demo_12 (ReAct) 或者 Day2 的最小 Agent，逻辑一样。

跑法：
    python demo_14_reflection.py
"""

from __future__ import annotations

import re

from toy_agent_base import TASKS, make_llm
from demo_13_plan_and_solve import run_plan_and_solve


# ============================================================
# Reviewer：让 LLM 扮演评审员
# ============================================================
REVIEW_PROMPT = """你现在是一个严格的评审员。请检查下面这个答案是否符合用户问题的要求。

用户问题：{question}

待评审答案：
{answer}

# 检查清单
1. 答案是否直接回答了用户的核心诉求？
2. 数字、计算结果是否准确？
3. 是否漏掉了用户问题里的某个子问题？
4. 是否编造了未经证实的信息？

# 输出格式（严格遵守）
VERDICT: PASS 或 NEEDS_REVISION
ISSUES:
- 如果 PASS，写"无"
- 如果 NEEDS_REVISION，列出每个问题，每行一条
"""


def review(question: str, answer: str) -> tuple[bool, str]:
    """返回 (是否通过, 评审意见字符串)。"""
    client, MODEL = make_llm()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": REVIEW_PROMPT.format(question=question, answer=answer)}],
        temperature=0,
    )
    raw = resp.choices[0].message.content or ""
    verdict_match = re.search(r"VERDICT:\s*(\w+)", raw)
    issues_match = re.search(r"ISSUES:\s*(.*)", raw, re.DOTALL)
    verdict = verdict_match.group(1).upper() if verdict_match else "PASS"
    issues = issues_match.group(1).strip() if issues_match else ""
    passed = verdict == "PASS" or "无" in issues[:5]
    return passed, raw


# ============================================================
# Refiner：拿着评审意见再写一次
# ============================================================
def refine(question: str, prev_answer: str, review_feedback: str) -> str:
    client, MODEL = make_llm()
    prompt = f"""你之前回答了一个用户问题，但评审员指出了问题。请基于评审意见**重写一份更好的答案**。

用户问题：{question}

你之前的答案：
{prev_answer}

评审意见：
{review_feedback}

# 重写后的答案
"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content or ""


# ============================================================
# Reflection 包装：底层用 Plan-and-Solve，外面套 review/refine
# ============================================================
def run_with_reflection(question: str, max_rounds: int = 2, verbose: bool = True) -> str:
    if verbose:
        print(f"\n=== ✏️ 第 1 轮 · 起草 ===")
    answer = run_plan_and_solve(question, verbose=verbose)

    for round_no in range(1, max_rounds + 1):
        if verbose:
            print(f"\n=== 🔍 第 {round_no} 轮 · 自我评审 ===")
        passed, feedback = review(question, answer)

        if verbose:
            print(feedback)

        if passed:
            if verbose:
                print("\n✅ 评审通过，提交答案。")
            return answer

        if verbose:
            print(f"\n=== 🛠 第 {round_no} 轮 · 修订 ===")
        answer = refine(question, answer, feedback)
        if verbose:
            print(f"修订后答案：\n{answer}")

    if verbose:
        print(f"\n⚠️ 达到最大反思轮数（{max_rounds}），返回当前答案。")
    return answer


if __name__ == "__main__":
    # 故意只跑 3 个任务，避免把课堂时间烧光（Reflection 一道题 token 是其他范式的 2-3 倍）
    SHORT_TASKS = TASKS[:3]
    for i, q in enumerate(SHORT_TASKS, 1):
        print("\n" + "=" * 60)
        print(f"任务 {i}: {q}")
        print("=" * 60)
        ans = run_with_reflection(q)
        print(f"\n🎯 最终答案: {ans}")

    print("\n\n" + "=" * 60)
    print("🎯 Reflection 的特点：")
    print("  - 优点：质量明显提升，特别是写作 / 代码 / 推理类任务")
    print("  - 缺点 1：token 直接翻倍（review + refine 各一次 LLM 调用）")
    print("  - 缺点 2：评审员是同一个模型 → 'LLM 自己检查自己' 有盲区")
    print("           （工业版常用更强的模型当评审，或者引入外部检查工具）")
    print("  - 适用场景：质量优先 > 速度优先（写代码、写报告、做推理）")
    print()
    print("  注意：Reflection 是个'包装层'，可以套在任何 Agent 外面。")
    print("        你也可以把它套在 demo_12 (ReAct) 上，或者 Day2 的最小 Agent 上。")
    print("=" * 60)

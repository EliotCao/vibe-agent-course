"""
Day 3 Lab Part 3 · Reflection 包装层骨架 —— 学生填空

Reflection 是一个**包装层**，不改底层 Agent，只在外面套：
  起草 → 评审 → （有问题）修订 → 评审 → ... → 通过 / 达到上限

要补的：
  ① REVIEW_PROMPT：评审员 prompt
  ② review() 的 verdict 解析
  ③ refine() 的 refiner prompt

参考：第 14 节 + demos/demo_14_reflection.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "demos"))
from toy_agent_base import TASKS, make_llm

# 复用你 Part2 写好的 Plan-and-Solve 作为底层 Agent
# （也可以换成 Part1 的 ReAct 版本）
sys.path.insert(0, str(Path(__file__).parent))
from agent_plan_solve import run_plan_and_solve


# ----------------------------------------------------------------
# TODO ① REVIEW_PROMPT
# 要求：让模型扮演严格评审员，输出 VERDICT + ISSUES
# ----------------------------------------------------------------
REVIEW_PROMPT = """你是评审员...

用户问题：{question}
答案：
{answer}

输出格式：
VERDICT: PASS 或 NEEDS_REVISION
ISSUES:
...
"""


def review(question: str, answer: str) -> tuple[bool, str]:
    """返回 (是否通过, 评审原文)。"""
    client, MODEL = make_llm()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": REVIEW_PROMPT.format(question=question, answer=answer)}],
        temperature=0,
    )
    raw = resp.choices[0].message.content or ""

    # ----------------------------------------------------------------
    # TODO ② 从 raw 里解析 VERDICT 字段
    # 提示：用正则取 'VERDICT:\s*(\w+)' 后面的词
    # ----------------------------------------------------------------
    passed = False    # ← 你的代码
    return passed, raw


def refine(question: str, prev_answer: str, feedback: str) -> str:
    """拿着评审意见再写一份。"""
    # ----------------------------------------------------------------
    # TODO ③ 写 refiner prompt + 调一次 LLM
    # ----------------------------------------------------------------
    return "TODO 未实现"


def run_with_reflection(question: str, max_rounds: int = 2) -> str:
    print("\n=== ✏️ 起草 ===")
    answer = run_plan_and_solve(question)

    for r in range(1, max_rounds + 1):
        print(f"\n=== 🔍 第 {r} 轮 评审 ===")
        passed, fb = review(question, answer)
        print(fb)

        if passed:
            print("\n✅ 通过，提交。")
            return answer

        print(f"\n=== 🛠 第 {r} 轮 修订 ===")
        answer = refine(question, answer, fb)
        print(answer)

    print(f"\n⚠️ 达到 {max_rounds} 轮反思上限")
    return answer


if __name__ == "__main__":
    for q in TASKS[:2]:
        print("\n" + "=" * 60)
        print(f"任务: {q}")
        print("=" * 60)
        print(f"\n🎯 最终答案: {run_with_reflection(q)}")

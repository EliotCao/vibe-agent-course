"""
Demo 02 · 三种 system prompt，三种"人格"
========================================

配套：第 2 节《提示词与角色：System / User / Assistant》

效果：同一个 user 问题，挂三种不同 system prompt，输出风格天差地别。
让学生体感"system prompt 是改变 AI 行为最便宜的方式"。

跑法：
    python demo_02_roles.py
"""

from __future__ import annotations

import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["BASE_URL"],
    api_key=os.environ["API_KEY"],
)
MODEL = os.environ["MODEL_ID"]


def chat(system: str, user: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=200,
    )
    return resp.choices[0].message.content or ""


SYSTEM_PROMPTS = {
    "严谨学者": "你是一位严谨的计算机科学教授，回答必须准确、术语规范，配一个例子。",
    "5 岁小朋友的语言": "你说话像 5 岁小朋友，用最简单的词，多用比喻，每句不超过 15 个字。",
    "只能用 emoji": "你只能用 emoji 回答问题，不允许出现任何文字。最多 10 个 emoji。",
}

QUESTION = "什么是递归？"


if __name__ == "__main__":
    print("=" * 60)
    print(f"User 问题（固定）: {QUESTION}")
    print("=" * 60)

    for name, sys_prompt in SYSTEM_PROMPTS.items():
        print(f"\n【人格：{name}】")
        print(f"system: {sys_prompt}")
        print("-" * 40)
        answer = chat(sys_prompt, QUESTION)
        print(answer)
        print()

    print("=" * 60)
    print("👀 观察：")
    print("  - 同样的问题，模型的行为完全由 system prompt 决定")
    print("  - 这就是后面所有 Agent 的基础：")
    print("    Agent = 一个特殊的 system prompt + 工具")
    print("=" * 60)

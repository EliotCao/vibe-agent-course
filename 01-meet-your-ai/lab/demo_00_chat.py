"""
Demo 00 · 最简单的 LLM 对话
============================

配套：第1章 课前热身

效果：一个最小的交互式对话循环——你输入什么，大模型回答什么。
第一次"跑通"与大模型对话的完整链路。

跑法：
    python demo_00_chat.py

输入 quit / exit / q 退出。
"""

from __future__ import annotations

import readline  # noqa: F401 — 启用终端行编辑，修复中文退格问题

from _env import get_model_id, make_client

client = make_client()
MODEL = get_model_id()


def chat(user_input: str) -> str:
    """单轮对话：发送用户输入，流式逐字打印模型回复。"""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": user_input}],
        temperature=0.9,
        stream=True,
    )
    parts = []
    first = True
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            if first:
                # 清除 thinking 标识，开始打印回复
                print("\r\033[K" + "AI: ", end="", flush=True)
                first = False
            text = chunk.choices[0].delta.content
            print(text, end="", flush=True)
            parts.append(text)
    print()  # 换行
    return "".join(parts)


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Hello! 我是你的 AI 助手，有什么想聊的？")
    print("   输入 quit / exit / q 退出")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break

        print("\nAI: 💭 thinking...", end="", flush=True)
        chat(user_input)

    print("\n👋 再见！")
